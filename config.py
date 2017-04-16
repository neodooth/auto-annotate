# coding: utf8

__author__ = 'neodooth'

import os

ROLE = 'website'  # 'website' or 'downloader'

_IMAGE_ROOT = 'images'
_dirs_to_create = [_IMAGE_ROOT]

if ROLE == 'website':
    print 'running as website'

    UNSUBMITTED_DIR = os.path.join(_IMAGE_ROOT, 'unsubmitted')
    UNRECEIVED_DIR = os.path.join(_IMAGE_ROOT, 'unreceived')
    UNANNOTATED_DIR = os.path.join(_IMAGE_ROOT, 'unannotated')
    ANNOTATED_DIR = os.path.join(_IMAGE_ROOT, 'annotated')
    THIRTEENTHOUSAND_DIR = os.path.join(_IMAGE_ROOT, '13000')

    DOWNLOADER_HOST = ''
    SECRET_KEY = 'AUTO_ANNOTATE'

    PWD_PREFIX = ''

    _dirs_to_create.append(UNSUBMITTED_DIR)
    _dirs_to_create.append(UNRECEIVED_DIR)
    _dirs_to_create.append(UNANNOTATED_DIR)
    _dirs_to_create.append(ANNOTATED_DIR)

elif ROLE == 'downloader':
    print 'running as downloader'

    UNDOWNLOADED_DIR = os.path.join(_IMAGE_ROOT, 'undownloaded')
    DOWNLOADING_DIR = os.path.join(_IMAGE_ROOT, 'downloading')
    DOWNLOADED_DIR = os.path.join(_IMAGE_ROOT, 'downloaded')
    DETECTED_DIR = os.path.join(_IMAGE_ROOT, 'detected')
    TMP_DIR = 'tmp'

    _dirs_to_create.append(UNDOWNLOADED_DIR)
    _dirs_to_create.append(DOWNLOADING_DIR)
    _dirs_to_create.append(DOWNLOADED_DIR)
    _dirs_to_create.append(DETECTED_DIR)
    _dirs_to_create.append(TMP_DIR)

    WEBSITE_HOST = ''
    DOWNLOAD_NUMBER = 1000
    SEARCH_BASE_URL = 'http://www.google.com.hk/search?newwindow=1&safe=moderate&tbm=isch&q=%s'
    USER_AGENT = 'Mozilla/5.0 (MeeGo; NokiaN9) AppleWebKit/534.13 (KHTML, like Gecko) NokiaBrowser/8.5.0 Mobile Safari/534.13'

    DETECT_SERVER_HOST = '127.0.0.1'
    DETECT_SERVER_PORT = '56565'
    TOO_MANY_FACES_THRESHOLD = 5

for d in _dirs_to_create:
    if not os.path.exists(d):
        os.mkdir(d)
