# coding: utf8

__author__ = 'neodooth'

from downloader import app

from flask import request
from flask.ext.cors import cross_origin

from utils import data_util
from utils.net_util import send_mail

import json, logging, time

logger = logging.getLogger(__name__)
last_time_sendmail = 0


@app.route('/submit_download_names', methods=['POST'])
@cross_origin()
def submit_download_names():
    global last_time_sendmail

    username = request.form['username']
    try:
        data = [
            {
                'id': x['id'].encode('utf8'),
                'chinese_name': x['chinese_name'].encode('utf8'),
                'english_name': x['english_name'].encode('utf8'),
                'keyword': x['keyword'].encode('utf8'),
                'options': x['options']
            } for x in json.loads(request.form['data'])
        ]
        logger.info('received download names, username: %s, data: %s'
                    % (username, json.dumps(data, encoding='utf8', ensure_ascii=False)))
        data_util.save_todo_names(username, data)
        return '0'

    except Exception as e:
        logger.error('submit_download_names exception, raw: %s' % e, exc_info=True)
        if time.time() - last_time_sendmail > 600:
            send_mail('submit_download_names exception', str(e))
            last_time_sendmail = time.time()
        return json.dumps(e, ensure_ascii=False, encoding='utf8')


@app.route('/heartbeat')
def heartbeat():
    return "i got 99 problems"