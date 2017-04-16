# coding: utf8

__author__ = 'neodooth'

from config import UNSUBMITTED_DIR, UNRECEIVED_DIR, UNANNOTATED_DIR, ANNOTATED_DIR, THIRTEENTHOUSAND_DIR
# from . import net_util

import os, logging, json
from datetime import datetime
from os import path

logger = logging.getLogger(__name__)

person_info = {}


def get_undownloaded_list(username):
    li = _list_existing_folder(path.join(UNSUBMITTED_DIR, username))
    li += _list_existing_folder(path.join(UNRECEIVED_DIR, username))
    return li


def get_unannotated_list(username):
    return _list_existing_folder(path.join(UNANNOTATED_DIR, username))


def get_annotated_list(username):
    return _list_existing_folder(path.join(ANNOTATED_DIR, username))


def get_13000_list():
    with open(path.join(THIRTEENTHOUSAND_DIR, '_name')) as f:
        names = f.readlines()

    ret = []
    for n in names:
        n = n.split('#')
        ret.append({
            'id': n[0],
            'chinese_name': n[0].replace('_', ' '),
            'english_name': '',
            'thumbnail': path.join(THIRTEENTHOUSAND_DIR, n[1])
        })
    return sorted(ret, key=lambda x: x['id'])


# def get_13000_images_of_one(name):
#     return net_util.get_13000_images_of_one(name)


def get_unannotated_images_of_one(username, id):
    target = path.join(UNANNOTATED_DIR, username, id)
    if not path.exists(target):
        return -1, None
    return 0, [x for x in os.listdir(target) if x.endswith('.jpg')]


def get_annotated_images_of_one(username, id):
    target = path.join(ANNOTATED_DIR, username, id)
    if not path.exists(target):
        return -1, None
    return 0, [x for x in os.listdir(target) if x.endswith('.jpg')]


def check_duplicate(data):
    '''
    检查data里的名字是不是和其他用户拥有的人名重复
    :param data: {'id': id, 'chinese_name': 中文名, 'english_name': 英文名}
    :return: (has_duplicate, dup)：（True/False是否有重复的，重复的项{'id':有重复的id, ['username':拥有已有的重复项的那个的用户, 'chinese_name': 已有的中文名, 'english_name': 已有的英文名, 'thumbnail': 缩略图路径, 'dir': 这个人路径]}
    '''
    dirs = [UNSUBMITTED_DIR, UNRECEIVED_DIR, UNANNOTATED_DIR, ANNOTATED_DIR]  # 要检查重复的地方
    has_duplicate = False  # 是否有重复
    dup = []  # 重复的记录

    # 用字典，在后面检查重复可能比较快，只需要somename in dict
    ch_dict = {}  # 已有中文名和其拥有者用户名、英文名的对应dict，具体是ch_dict['那谁']=[{username: 'un', chinese_name: '', english_name: '', thumbnail: ''}, {}, ...]
    en_dict = {}  # 已有英文名和其拥有者用户名、中文名的对应dict，具体是eh_dict['小写英文名']=[{username: 'un', chinese_name: '', english_name: '', thumbnail: ''}, {}, ...]
    for d in dirs:
        for user in os.listdir(d):
            user_dir = path.join(d, user)
            for id in os.listdir(user_dir):
                try:
                    this_dir = path.join(user_dir, id)
                    info = _get_info_of_one(this_dir)
                    ch_name = info['ch_name']
                    en_name = info['en_name']
                    this_record = {
                        'username': user,
                        'dir': this_dir,
                        'chinese_name': ch_name,
                        'english_name': en_name,
                    }
                    if len(ch_name) > 0:
                        ch_record = ch_dict.get(ch_name, None)  # 先检查是不是有别的用户也有这个名字
                        if ch_record is not None:
                            ch_dict[ch_name].append(this_record)  # 如果有的话就把这个用户的记录加进去
                        else:
                            ch_dict[ch_name] = [this_record]
                    if len(en_name) > 0:
                        norm_en_name = en_name.lower()
                        en_record = en_dict.get(norm_en_name, None)
                        if en_record is not None:
                            en_dict[norm_en_name].append(this_record)
                        else:
                            en_dict[norm_en_name] = [this_record]

                except Exception as e:
                    logger.error('check duplicate exception, path: %s, raw: %s' % (path.join(user_dir, id), e), exc_info=True)

    with open(path.join(THIRTEENTHOUSAND_DIR, '_name')) as f:
        name_urls = f.readlines()
    user = '13000名人'
    for n_l in name_urls:
        n_l = n_l.split('#')
        name = n_l[0].replace('_', ' ')
        thumbnail = n_l[1]
        if name[0].isalpha() or name[-1].isalpha():
            norm_name = name.lower()
            en_record = en_dict.get(norm_name, None)
            this_record = {
                'username': user,
                'chinese_name': '',
                'english_name': name,
                'thumbnail': path.join(THIRTEENTHOUSAND_DIR, thumbnail)
            }
            if en_record is not None:
                en_dict[norm_name].append(this_record)
            else:
                en_dict[norm_name] = [this_record]
        else:
            ch_record = ch_dict.get(name, None)
            this_record = {
                'username': user,
                'chinese_name': name,
                'english_name': '',
                'thumbnail': path.join(THIRTEENTHOUSAND_DIR, thumbnail)
            }
            if ch_record is not None:
                ch_dict[name].append(this_record)  # 如果有的话就把这个用户的记录加进去
            else:
                ch_dict[name] = [this_record]

    for datum in data:
        ch_name = datum['chinese_name']
        en_name = datum['english_name'].lower()
        ch_record = ch_dict.get(ch_name, None)  # 检查中文名是否重复
        en_record = en_dict.get(en_name, None)  # 检查英文名是否重复
        if ch_record is not None or en_record is not None:
            has_duplicate = True
            dup.append({
                'id': datum['id'],
                'existing': ch_record if en_record is None else en_record
            })
    for d in dup:
        for e in d['existing']:
            if e.get('thumbnail', None) is None:
                e['thumbnail'] = path.join(e['dir'], _get_thumbnail_of_one(e['dir']))
    return has_duplicate, dup


def save_annotation_result(username, id, to_save_images):
    '''
    保存标注结果
    :param username:用户名
    :param id: 标注的人id
    :param to_save_images:要保存的图片
    :return:None
    '''
    unfinished_user_folder = path.join(UNANNOTATED_DIR, username)
    unfinished_one_folder = path.join(unfinished_user_folder, id)
    if not path.exists(unfinished_one_folder):
        return -1

    finished_user_folder = path.join(ANNOTATED_DIR, username)
    finished_one_folder = path.join(finished_user_folder, _get_new_id(username, 'annotated'))

    if not path.exists(finished_user_folder):
        os.mkdir(finished_user_folder)
    # if not path.exists(finished_one_folder):
    #     os.mkdir(finished_one_folder)

    existing = [x for x in os.listdir(unfinished_one_folder) if not x.startswith('_')]
    to_delete = list(set(existing) - set(to_save_images))
    delete_images_of_one(username, 'unannotated', id, to_delete)

    logger.info('%s save annotation result, rename %s to %s' % (username, unfinished_one_folder, finished_one_folder))
    os.rename(unfinished_one_folder, finished_one_folder)

    now = datetime.today()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    os.system('echo %s >> %s' % (timestamp, path.join(finished_one_folder, '_date')))
    return 0


def delete_images_of_one(username, one_type, id, image_ids):
    '''
    从某种类型的人的图片里删除不想要的
    :param username: 用户名
    :param one_type: 要删图片的类型
    :param id: 要删除图片的人的id
    :param image_ids: 要删除的图片名
    :return:None
    '''

    if one_type == 'unannotated':
        folder = UNANNOTATED_DIR
    elif one_type == 'annotated':
        folder = ANNOTATED_DIR
    # elif one_type == '13000':
    #     with open(THIRTEENTHOUSAND_ACTION_FILE, 'a') as f:
    #         print >> f, '%s#deleteone#%s#%s' % (username, id, json.dumps(image_ids))
    #     return
    else:
        raise Exception({'msg': 'illegal type, usename: %s, type: %s, id: %s, image_ids: %s' % (username, one_type, id, image_ids), 'raw': ''})

    one_folder = path.join(folder, username, id)
    if not path.exists(one_folder):
        return -1

    for img in image_ids:
        if '..' in img or '/' in img:
            return -1

    os.system('rm %s' % ' '.join([path.join(one_folder, img) for img in image_ids]))
    return 0


def delete_unannotated_one(username, id):
    if '.' in id or '/' in id:
        return -1

    one_folder = path.join(UNANNOTATED_DIR, username, id)
    if not path.exists(one_folder):
        return -1

    os.system('rm -rf %s' % one_folder)
    return 0


def delete_annotated_one(username, id):
    if '.' in id or '/' in id:
        return -1

    one_folder = path.join(ANNOTATED_DIR, username, id)
    if not path.exists(one_folder):
        return -1

    os.system('rm -rf %s' % one_folder)
    return 0


# def delete_13000_one(username, id):
#     with open(THIRTEENTHOUSAND_ACTION_FILE, 'a') as f:
#         print >> f, '%s#delete#%s' % (username, id)


# def save_13000_list(items):
#     with open(path.join(THIRTEENTHOUSAND_DIR, '_name'), 'w') as f:
#         for n in items:
#             print >> f, '%s#%s' % (n[0], n[1])


def save_todo_names(username, data):
    user_folder = path.join(UNSUBMITTED_DIR, username)
    for d in data:
        new_id = _get_new_id(username, 'unannotated')
        this_folder = path.join(user_folder, new_id)
        try:
            os.mkdir(this_folder)
            with open(path.join(this_folder, '_name'), 'w') as f:
                print >> f, '%s\n%s' % (d.get('chinese_name', ''), d.get('english_name', ''))
            if 'keyword' in d:
                with open(path.join(this_folder, '_keyword'), 'w') as f:
                    print >> f, d['keyword']
            if 'intro' in d:
                with open(path.join(this_folder, '_introduction'), 'w') as f:
                    print >> f, d['intro']
            if 'weibo' in d:
                with open(path.join(this_folder, '_weibo'), 'w') as f:
                    print >> f, d['weibo']
            with open(path.join(this_folder, '_options'), 'w') as f:
                if 'dont_detect_face' in d:
                    json.dump({'dont_detect_face': d['dont_detect_face']}, f, ensure_ascii=False)

        except Exception as e:
            raise Exception({
                'msg': 'save todo names exception, username: %s, data: %s, this_folder: %s' % (username, data, this_folder),
                'raw': e
            })


def _list_existing_folder(target_dir):
    '''
    列出当前文件夹下所有的人
    :param target_dir: 要列出的文件夹
    :return: [{'id': id, 'chinese_name': 中文名，可能空, 'english_name': 英文名，可能空，但两个名字至少有一个非空, 'thumbnail': 缩略图文件名}, {}, ...]
    '''

    def get_names(base, folders):
        result = []
        try:
            for fol in folders:
                info = _get_info_of_one(path.join(base, fol))
                result.append({'chinese': info['ch_name'], 'english': info['en_name']})
            return result

        except Exception as e:
            raise Exception({'msg': 'get names exception, base: %s, folders: %s' % (base, folders), 'raw': e})

    def get_thumbnails(base, folders):
        result = []
        try:
            tn = ''
            for fol in folders:
                imgs = [x for x in os.listdir(path.join(base, fol)) if x.endswith('.jpg')]
                if len(imgs) > 0:
                    imgs = sorted(imgs, key=lambda x: int(x.split('_')[1]))
                    tn = imgs[0]
                result.append(tn)
            return result

        except Exception as e:
            raise Exception({'msg': 'get thumbnails exception, base: %s, folders: %s' % (base, folders), 'raw': e})

    def get_list_result(folders, names, thumbnails):
        li = []
        try:
            for (f, n, t) in zip(folders, names, thumbnails):
                li.append({
                    'id': f,
                    'chinese_name': n['chinese'],
                    'english_name': n['english'],
                    'thumbnail': t
                })
            li = sorted(li, key=lambda x: int(x['id']))
            return li
        except Exception as e:
            raise Exception({'msg': 'get list result exception, folders: %s, names: %s, thumbnails: %s' % (folders, names, thumbnails), 'raw': e})

    if path.exists(target_dir):
        ones_folders = os.listdir(target_dir)
        names = get_names(target_dir, ones_folders)
        thumbnails = get_thumbnails(target_dir, ones_folders)
        return get_list_result(ones_folders, names, thumbnails)
    return []


def _get_new_id(username, id_type):
    if id_type == 'unannotated':
        folders = [UNSUBMITTED_DIR, UNRECEIVED_DIR, UNANNOTATED_DIR]
    else:
        folders = [ANNOTATED_DIR]

    l = []
    new_id = 0
    for f in folders:
        user_dir = path.join(f, username)
        if path.exists(user_dir):
            existing = [int(x) for x in os.listdir(user_dir)]
            l += existing

    if len(l) > 0:
        new_id = max(l) + 1
    return str(new_id)


def _get_info_of_one(target):
    global person_info
    ret = {}
    try:
        mtime = os.stat(target).st_mtime
        if target in person_info and mtime == person_info[target]['mtime']:
            return person_info[target]['info']

        with open(path.join(target, '_name')) as f:
            ret['ch_name'] = f.readline().strip()
            ret['en_name'] = f.readline().strip()
        if not path.exists(path.join(target, '_keyword')):
            with open(path.join(target, '_keyword'), 'w') as f:
                pass
        with open(path.join(target, '_keyword')) as f:
            ret['keyword'] = f.readline().strip()
        if path.exists(path.join(target, '_weibo')):
            with open(path.join(target, '_weibo')) as f:
                ret['weibo'] = f.readline().strip()
        if path.exists(path.join(target, '_introduction')):
            with open(path.join(target, '_introduction')) as f:
                ret['intro'] = f.readline().strip()
        if path.exists(path.join(target, '_options')):
            with open(path.join(target, '_options')) as f:
                ret['options'] = {}
                for k, v in json.load(f).iteritems():
                    ret['options'][k.encode('utf8')] = v
        person_info[target] = {
            'mtime': mtime,
            'info': ret
        }
        return ret

    except Exception as e:
        raise Exception({'msg': 'get info of one exception, target: %s' % target, 'raw': e})


def _set_info_of_one(target, ch_name, en_name, weibo, intro):
    try:
        with open(path.join(target, '_name'), 'w') as f:
            print >> f, '%s\n%s' % (ch_name, en_name)
        if len(weibo) > 0:
            with open(path.join(target, '_weibo'), 'w') as f:
                print >> f, '%s' % weibo
        if len(intro) > 0:
            with open(path.join(target, '_introduction'), 'w') as f:
                print >> f, '%s' % intro

    except Exception as e:
        raise Exception({'msg': 'get info of one exception, target: %s' % target, 'raw': e})


def _get_thumbnail_of_one(target):
    try:
        li = [x for x in os.listdir(target) if x.endswith('.jpg')]
        li = sorted(li, key=lambda x: int(x.split('_')[1]))
        if len(li) > 0:
            return li[0]
        return ''

    except Exception as e:
        raise Exception({'msg': 'get thumbnail of one exception, target: %s' % target, 'raw': e})


def get_unsubmitted():
    result = []
    for username in os.listdir(UNSUBMITTED_DIR):
        this_user_folder = path.join(UNSUBMITTED_DIR, username)
        this_user_namelist = []
        for folder in os.listdir(this_user_folder):
            try:
                info = _get_info_of_one(path.join(this_user_folder, folder))
                this_user_namelist.append({
                    'id': folder,
                    'chinese_name': info['ch_name'],
                    'english_name': info['en_name'],
                    'keyword': info['keyword'],
                    'options': info['options']
                })

            except Exception as e:
                logger.error('get unsubmitted exception. path: %s. raw: %s' % (path.join(this_user_folder, folder), e), exc_info=True)
        if len(this_user_namelist) > 0:
            result.append({'username': username, 'namelist': this_user_namelist})
    return result


def finish_untransmitted(username, ones):
    unsub_this_user_folder = path.join(UNSUBMITTED_DIR, username)
    unrec_this_user_folder = path.join(UNRECEIVED_DIR, username)
    if not path.exists(unrec_this_user_folder):
        os.mkdir(unrec_this_user_folder)
    for one in ones:
        src = path.join(unsub_this_user_folder, one['id'])
        dst = path.join(unrec_this_user_folder, one['id'])
        logger.info('finish untransmitted for %s rename %s to %s' % (username, src, dst))
        try:
            os.rename(src, dst)

        except Exception as e:
            raise Exception({'msg': 'finish untransmitted exception, username: %s, ones: %s, src: %s, dst: %s'
                                    % (username, json.dumps(ones, ensure_ascii=False), src, dst), 'raw': e})


def get_save_image_prefix(username, id):
    user_dir = path.join(UNRECEIVED_DIR, username)
    if not path.exists(user_dir):
        os.mkdir(user_dir)
    save_to = path.join(user_dir, id)
    if not path.exists(save_to):
        raise Exception({'msg': 'save_to dir not exists. save_to: %s' % save_to, 'raw': ''})
    return save_to


def finish_receive(username, id):
    unrec_user_dir = path.join(UNRECEIVED_DIR, username)
    unanno_user_dir = path.join(UNANNOTATED_DIR, username)
    if not path.exists(unanno_user_dir):
        os.mkdir(unanno_user_dir)
    src = path.join(unrec_user_dir, id)
    dst = path.join(unanno_user_dir, id)
    logger.info('finish receive images, username: %s, id: %s, rename from %s to %s' % (username, id, src, dst))
    os.rename(src, dst)


def get_info(username, type, id):
    base = UNANNOTATED_DIR if type == 'unannotated' else ANNOTATED_DIR
    d = path.join(base, username, id)
    if path.exists(d):
        return _get_info_of_one(d)
    return {}


def update_info(username, type, id, data):
    base = UNANNOTATED_DIR if type == 'unannotated' else ANNOTATED_DIR
    d = path.join(base, username, id)
    if path.exists(d):
        _set_info_of_one(
            d,
            data['chinese_name'],
            data['english_name'],
            data['weibo'],
            data['intro']
        )
        return 0
    else:
        return -1