# coding: utf8

__author__ = 'neodooth'

from requests_toolbelt import MultipartEncoder
import requests

import logging, smtplib
from os import path
from email.mime.text import MIMEText

from config import WEBSITE_HOST

logger = logging.getLogger(__name__)


def send_images(username, id, image_paths):
    url = path.join(WEBSITE_HOST, 'send_images')
    payload = {
        'username': username,
        'id': id
    }

    fps = []
    for i in image_paths:
        imgname = i.split('/')[-1]
        fp = open(i, 'rb')
        fps.append(fp)
        payload[imgname] = (imgname, fp, 'application/octet-stream')
    m = MultipartEncoder(fields=payload)

    try:
        # resp = requests.post(url, data=payload, files=files)
        resp = requests.post(url, data=m, headers={'Content-Type': m.content_type})
        if resp.content != 'success':
            raise Exception({'msg': 'website returned this: %s' % resp.content})
    except requests.exceptions.RequestException as e:
        raise Exception({'msg': 'error connecting website %s, username: %s, id: %s' % (WEBSITE_HOST, username, id), 'raw': e})
    finally:
        for f in fps:
            f.close()


def send_mail(sub, text):
    _user = ""
    _pwd = ""
    _to = ""

    msg = MIMEText(text)
    msg["Subject"] = "annotate downloader - %s" % sub
    msg["From"] = _user
    msg["To"] = _to

    try:
        s = smtplib.SMTP("smtp.qq.com", 587, timeout=10)#连接smtp邮件服务器,端口默认是25
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(_user, _pwd)#登陆服务器
        s.sendmail(_user, _to, msg.as_string())#发送邮件
        logger.info('sending mail %s' % sub)
        s.close()
    except Exception as e:
        logger.error('send mail exception, raw: %s' % e, exc_info=True)
