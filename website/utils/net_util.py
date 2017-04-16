# coding: utf8

__author__ = 'neodooth'

from config import DOWNLOADER_HOST

import logging
from os import path
import requests, json, smtplib
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def send_names(username, namelist):
    url = path.join(DOWNLOADER_HOST, 'submit_download_names')
    payload = {'data': json.dumps(namelist), 'username': username}
    try:
        resp = requests.post(url, data=payload)
        if resp.content != '0':
            raise Exception({'msg': 'send names to downloader exception, returned this: %s' % resp.content})
    except requests.exceptions.RequestException as e:
        raise Exception({'msg': 'error connecting downloader %s' % DOWNLOADER_HOST, 'raw': e})


def send_mail(sub, text):
    _user = ""
    _pwd = ""
    _to = ""

    msg = MIMEText(text)
    msg["Subject"] = "annotate website - %s" % sub
    msg["From"] = _user
    msg["To"] = _to

    try:
        s = smtplib.SMTP("smtp.qq.com", 587, timeout=10)#连接smtp邮件服务器,端口默认是25
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(_user, _pwd)#登陆服务器
        s.sendmail(_user, _to, msg.as_string())#发送邮件
        s.close()
    except Exception as e:
        logger.error('send mail exception, raw: %s' % e, exc_info=True)


def test_downloader():
    url = path.join(DOWNLOADER_HOST, 'heartbeat')
    try:
        resp = requests.get(url)
        if resp.content != 'i got 99 problems':
            raise Exception({'msg': 'heartbeat test downloader, downloader returned this: %s' % resp.content})
    except requests.exceptions.RequestException as e:
        msg = str(e)
        if ('reset' in msg or 'Connection timed out' in msg) is False:
            raise Exception({'msg': 'error connecting downloader %s' % DOWNLOADER_HOST, 'raw': e})
