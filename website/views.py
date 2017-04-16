# coding: utf8

__author__ = 'neodooth'

from website import app
from config import UNSUBMITTED_DIR, PWD_PREFIX

from flask import render_template, redirect, session, url_for, flash, request

from os import path
import json, logging, datetime, time

import forms
from utils import data_util, statistics
from utils.net_util import send_mail

logger = logging.getLogger(__name__)

last_time_sendmail = {}

def sendmail_per_min(key, sub, text, min=300):
    global last_time_sendmail
    if key not in last_time_sendmail:
        last_time_sendmail[key] = 0
    if time.time() - last_time_sendmail[key] > min:
        send_mail(sub, text)
        last_time_sendmail[key] = time.time()


@app.route('/', methods=['GET', 'POST'])
def signin():
    special_accounts = []

    form = forms.SigninForm()
    if form.validate_on_submit():
        username = form.username.data
        if path.exists(path.join(UNSUBMITTED_DIR, username)):
            if username in special_accounts:
                if form.password.data == 'hello' + username:
                    logger.info('%s signed in' % username)
                    session['username'] = username.encode('utf8')
                    return redirect(url_for('index'))
            else:
                ok = False
                if form.password.data == PWD_PREFIX + username:
                    ok = True

                if ok:
                    logger.info('%s signed in' % username)
                    session['username'] = username.encode('utf8')
                    return redirect(url_for('index'))
            logger.warning('%s failed to sign in: wrong password' % username)
            flash(u'密码错误')
        else:
            logger.warning('%s failed to sign in: doesn\'t exist' % username)
            flash(u'用户 ' + username + u' 不存在')

    duties = [
        [],
        [u'熊'],
        [],
        [],
        [],
        [],
        []
    ]

    workload = statistics.annotated_last_n_days(7)

    return render_template(
        'signin.html',
        form=form,
        on_duty=duties[datetime.datetime.now().weekday()],
        show_statistics=(datetime.datetime.now().weekday() == 4 and datetime.datetime.now().hour >= 11),
        workload=[{
            'username': w['username'],
            'each': ['%d/%d' % (e[0], e[1]) for e in zip(w['each_day_people'], w['each_day_pictures'])],
            'total': '%d/%d' % (w['total_people'], w['total_pictures'])
        } for w in workload],
        overall_people=sum([w['total_people'] for w in workload]),
        overall_pictures=sum([w['total_pictures'] for w in workload])
    )


@app.route('/signout')
def signout():
    if session.get('username') is not None:
        logger.info('%s signed out' % session.get('username'))
        session.pop('username', None)
    return redirect('/')


@app.route('/index')
def index():
    if session.get('username') is None:
        return redirect('/')
    return render_template('index.html', username=session['username'])


@app.route('/work')
def work():
    if session.get('username') is None:
        return redirect('/')

    return render_template('work.html', username=session['username'])


@app.route('/get_list')
def get_list():
    username = session.get('username')
    get_type = request.args.get('type', None)  # 'undownloaded', 'unannotated', 'annotated'
    _from = request.args.get('from', 0)
    _to = request.args.get('to', 100)

    logger.info('get_list, username: %s, type: %s, from: %s, to: %s' % (username, get_type, _from, _to))

    try:
        _from = int(_from)
    except:
        _from = 0
    try:
        _to = int(_to)
    except:
        _to = 100

    if username is None or get_type is None or get_type not in ['undownloaded', 'unannotated', 'annotated']:
        return ''

    try:
        get_type = get_type.encode('utf8')
        if get_type == 'undownloaded':
            li = data_util.get_undownloaded_list(username)
        elif get_type == 'unannotated':
            li = data_util.get_unannotated_list(username)
        elif get_type == 'annotated':
            li = data_util.get_annotated_list(username)
        else:
            li = data_util.get_13000_list()

        # li是列表, [{name: "人名(文件夹名)", thumbnail: "相对于TODO_DIR/FINISHED_DIR的人的第一张图片的路径"}]
        if get_type != '13000':
            for l in li:
                if l['thumbnail'] != '':
                    l['thumbnail'] = url_for('data.static', filename='%s/%s/%s/%s' % (get_type, username, l['id'], l['thumbnail']))
        return json.dumps({'length': len(li), 'data': li[_from: _to]})

    except Exception as e:
        logger.error('get_list exception, raw: %s' % e, exc_info=True)
        send_mail('get_list exception', str(e))
        return json.dumps({'msg': str(e)})


@app.route('/get_images_of_one')
def get_images_of_one():
    username = session.get('username')
    get_type = request.args.get('type', None)  # 'unannotated', 'annotated'
    id = request.args.get('id', None)
    _from = request.args.get('from', 0)
    _to = request.args.get('to', 100)

    logger.info('get_images_of_one, username: %s, type: %s, id: %s, from: %s, to: %s' % (username, get_type, id, _from, _to))

    try:
        _from = int(_from)
    except:
        _from = 0
    try:
        _to = int(_to)
    except:
        _to = 100

    if username is None or get_type is None or id is None or get_type not in ['unannotated', 'annotated']:
        return ''

    get_type = get_type.encode('utf8')
    id = id.encode('utf8')

    try:
        if get_type == 'unannotated':
            result, li = data_util.get_unannotated_images_of_one(username, id)
        elif get_type == 'annotated':
            result, li = data_util.get_annotated_images_of_one(username, id)

        if result == -1:
            return json.dumps({'msg': u'查看的id(%s)不存在' % id})

        li = sorted(li, key=lambda x: int(x.split('_')[1]))
        ret = [
            {
                'id': img,
                'url': url_for('data.static', filename='%s/%s/%s/%s' % (get_type, username, id, img))
            } for img in li[_from:_to]]
        return json.dumps({'length': len(li), 'data': ret})

    except Exception as e:
        logger.error('get_images_of_one exception, raw: %s' % e, exc_info=True)
        sendmail_per_min('get_images_of_one', 'get_images_of_one exception', str(e))
        return json.dumps({'msg': str(e)})


@app.route('/save_annotation', methods=['POST'])
def save_annotation():
    username = session.get('username')
    if username is None:
        return ''

    id = request.form['id'].encode('utf8')
    image_ids = json.loads(request.form['image_ids'])

    logger.info('save_annotation, username: %s, id: %s, image_ids: %s' % (username, id, ','.join(image_ids)))

    try:
        result = data_util.save_annotation_result(username, id, image_ids)
        if result == 0:
            return json.dumps('success')
        if result == -1:
            return json.dumps({'msg': u'要保存的id(%s)不存在' % id})

    except Exception as e:
        logger.error('save_annotation exception, raw: %s' % e, exc_info=True)
        sendmail_per_min('save_annotation', 'save_annotation exception', str(e))
        return json.dumps({'msg': str(e)})


@app.route('/delete_one', methods=['POST'])
def delete_one():
    username = session.get('username').encode('utf8')
    id = request.form['id'].encode('utf8')
    delete_type = request.form['type'].encode('utf8')
    if username is None or delete_type not in ['unannotated', 'annotated']:
        logger.warning('%s tried to delete one, type: %s, id %s' % (username, delete_type, id))
        return ''

    logger.info('delete_one, username: %s, type: %s, id %s' % (username, delete_type, id))

    try:
        if delete_type == 'unannotated':
            result = data_util.delete_unannotated_one(username, id)
        elif delete_type == 'annotated':
            result = data_util.delete_annotated_one(username, id)
        else:
            return json.dumps('illegal type')

        if result == -1:
            return json.dumps(u'要删除的id(%s)不存在' % id)
        return json.dumps('success')

    except Exception as e:
        logger.error('delete_one exception, raw: %s' % e, exc_info=True)
        sendmail_per_min('delete_one', 'delete_one exception', str(e))
        return json.dumps({'msg': str(e)})


@app.route('/delete_some_of_one', methods=['POST'])
def delete_some_of_one():
    username = session.get('username')
    delete_type = request.form['type'].encode('utf8')
    id = request.form['id'].encode('utf8')
    image_ids = json.loads(request.form['image_ids'])
    if username is None or delete_type not in ['unannotated', 'annotated', '13000']:
        logger.warning('%s tried to delete some of one, type: %s, id %s' % (username, delete_type, id))
        return ''

    logger.info('delete_some_of_one, username: %s, type: %s, id %s, image_ids: %s'
                % (username, delete_type, id, ','.join(image_ids)))

    try:
        result = data_util.delete_images_of_one(username, delete_type, id, image_ids)
        if result == -1:
            return json.dumps(u'要删除的id(%s)不存在' % id)
        return json.dumps('success')

    except Exception as e:
        logger.error('delete_some_of_one exception, raw: %s' % e, exc_info=True)
        sendmail_per_min('delete_some_of_one', 'delete_some_of_one exception', str(e))
        return json.dumps({'msg': str(e)})


@app.route('/submit_namelist', methods=['POST'])
def submit_namelist():
    username = session.get('username')
    if username is None:
        return redirect('/')

    data = [{
                'id': x['id'],
                'chinese_name': x['chinese_name'].encode('utf8').strip(),
                'english_name': x['english_name'].encode('utf8').strip(),
                'keyword': x['keyword'].encode('utf8').strip(),
                'intro': x['intro'].encode('utf8').strip(),
                'weibo': x['weibo'].encode('utf8'),
                'dont_detect_face': x['dont_detect_face']
            } for x in json.loads(request.form['data'])]
    force_submit = request.form['force_submit'] == 'true'
    has_duplicate = False
    dup = []

    t1 = time.time()
    try:
        if not force_submit:
            has_duplicate, dup = data_util.check_duplicate(data)

    except Exception as e:
        logger.error('failed to check duplicate names. %s' % e, exc_info=True)
        sendmail_per_min('submit_namelist.check_duplicate', 'check duplicate names exception', str(e))
        return json.dumps({'msg': str(e)})

    logger.info('submit_namelist, username: %s, force: %s, data: %s, has_duplicate: %s, dup: %s'
                % (username, force_submit, json.dumps(data, ensure_ascii=False), has_duplicate, dup))

    if force_submit or has_duplicate == False:
        try:
            data_util.save_todo_names(username, data)
        except Exception as e:
            logger.error('failed to save todo names. %s' % e, exc_info=True)
            sendmail_per_min('submit_namelist.save_todo', 'save todo names exception', str(e))
            return json.dumps({'msg': str(e)})
    t2 = time.time()
    return json.dumps({'has_duplicate': has_duplicate, 'duplicates': dup, 'time': t2-t1})


@app.route('/send_images', methods=['POST'])
def send_images():
    username = request.form['username']
    id = request.form['id'].encode('utf8')
    images = request.files.iteritems()

    try:
        directory = data_util.get_save_image_prefix(username, id)
        logger.info('received images from downloader, username: %s, id: %s. save to %s' % (username, id, directory))
        for k, i in images:
            i.save(path.join(directory, i.filename))
        data_util.finish_receive(username, id)
        return 'success'

    except Exception as e:
        logger.error('failed to receive images. exception: %s' % e, exc_info=True)
        msg = '%s\n%s %s' % (str(e), username, id)
        sendmail_per_min('send_images', 'send_images exception', msg, 900)
        return 'failed'


@app.route('/check_duplicate', methods=['POST'])
def check_duplicate():
    username = session.get('username')
    if username is None:
        return redirect('/')

    data = {
        'id': request.form['id'],
        'chinese_name': request.form['chinese_name'].encode('utf8').strip(),
        'english_name': request.form['english_name'].encode('utf8').strip()
    }

    try:
        t1 = time.time()
        has_duplicate, dup = data_util.check_duplicate([data])
        t2 = time.time()
        return json.dumps({'has_duplicate': has_duplicate, 'duplicates': dup, 'time': t2-t1})
    except Exception as e:
        logger.error('check_duplicate exception, raw: %s' % e, exc_info=True)
        sendmail_per_min('check_duplicate', 'check_duplicate exception', str(e))
        return json.dumps({'msg': str(e)})


@app.route('/get_info')
def get_info():
    username = session.get('username')
    if username is None:
        return redirect('/')

    type = request.args['type'].encode('utf8')
    id = request.args['id'].encode('utf8')

    logger.info('get_info, username: %s, type: %s, id: %s' % (username, type, id))

    try:
        info = data_util.get_info(username, type, id)
        return json.dumps({
            'chinese_name': info['ch_name'],
            'english_name': info['en_name'],
            'weibo': info.get('weibo', ''),
            'introduction': info.get('intro', '')
        })

    except Exception as e:
        logger.error('get_info exception, raw: %s' % e, exc_info=True)
        sendmail_per_min('get_info', 'get_info exception', str(e))
        return json.dumps({'msg': str(e)})


@app.route('/modify_info', methods=['POST'])
def modify_info():
    username = session.get('username')
    if username is None:
        return redirect('/')

    type = request.form['type'].encode('utf8')
    id = request.form['id'].encode('utf8')
    data = {
        'chinese_name': request.form['chinese_name'].encode('utf8'),
        'english_name': request.form['english_name'].encode('utf8'),
        'intro': request.form['intro'].encode('utf8'),
        'weibo': request.form['weibo'].encode('utf8')
    }

    logger.info('modify_info, username: %s, type: %s, id: %s, data: %s'
                % (username, type, id, json.dumps(data, ensure_ascii=False)))

    try:
        if data_util.update_info(username, type, id, data) == 0:
            return 'success'
        return 'failed'

    except Exception as e:
        logger.error('modify_info exception, raw: %s' % e, exc_info=True)
        sendmail_per_min('modify_info', 'modify_info exception', str(e))
        return json.dumps({'msg': str(e)})
