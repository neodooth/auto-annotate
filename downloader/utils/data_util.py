# coding: utf8

__author__ = 'neodooth'

import os, logging
from os import path
import json

from config import UNDOWNLOADED_DIR, DOWNLOADING_DIR, DOWNLOADED_DIR, DETECTED_DIR

logger = logging.getLogger(__name__)


def save_todo_names(username, ones):
    user_folder = path.join(UNDOWNLOADED_DIR, username)
    if not path.exists(user_folder):
        os.mkdir(user_folder)

    for one in ones:
        this_dir = path.join(user_folder, one['id'])
        try:
            os.mkdir(this_dir)
            with open(path.join(this_dir, '_name'), 'w') as f:
                print >> f, '%s\n%s' % (one['chinese_name'], one['english_name'])
            with open(path.join(this_dir, '_keyword'), 'w') as f:
                print >> f, '%s' % one['keyword']
            with open(path.join(this_dir, '_options'), 'w') as f:
                json.dump(one['options'], f, ensure_ascii=False)
        except Exception as e:
            logger.error('save todo name exception, username: %s, one: %s, this_dir: %s, raw: %s' % (username, one, this_dir, e), exc_info=True)


def get_undownloaded():
    '''
    返回未下载的名单
    :return: [ {'username': username, 'id': id, 'name': one's name to download}, {}, ...]
    '''

    # 把之前没下载完的清空并移动回未下载文件夹
    for username in os.listdir(DOWNLOADING_DIR):
        this_user_folder = path.join(DOWNLOADING_DIR, username)
        try:
            ids = os.listdir(this_user_folder)
            for id in ids:
                this_id_folder = path.join(this_user_folder, id)
                logger.info('resume downloading %s' % this_id_folder)
                for f in os.listdir(this_id_folder):
                    if not f.startswith('_'):
                        os.remove(path.join(this_id_folder, f))
                os.rename(this_id_folder, path.join(UNDOWNLOADED_DIR, username, id))
        except Exception as e:
            logger.error('get undownloaded resume downloading exception, this_user_folder: %s, ids: %s, raw: %s' % (this_user_folder, ids, e), exc_info=True)

    namelist = []
    for username in os.listdir(UNDOWNLOADED_DIR):
        this_user_folder = path.join(UNDOWNLOADED_DIR, username)
        try:
            ids = os.listdir(this_user_folder)
            for id in ids[:1]:
                info = _get_info_of_one(path.join(this_user_folder, id))
                namelist.append({
                    'username': username,
                    'id': id,
                    'name': info['ch_name'] if len(info['ch_name']) > 0 else info['en_name'],
                    'keyword': info['keyword']
                })
        except Exception as e:
            logger.error('get undownloaded exception, this_user_folder: %s, ids: %s, raw: %s' % (this_user_folder, ids, e), exc_info=True)
    return namelist


# return a path to save downloaded images
def prepare_download(username, id):
    src = path.join(UNDOWNLOADED_DIR, username, id)
    downloading_user_dir = path.join(DOWNLOADING_DIR, username)
    if not path.exists(downloading_user_dir):
        os.mkdir(downloading_user_dir)
    dst = path.join(downloading_user_dir, id)
    try:
        os.rename(src, dst)
    except Exception as e:
        raise Exception('prepare download exception, username: %s, id: %s, src: %s, dst: %s, raw: %s' % (username, id, src, dst, e), exc_info=True)
    return dst


def finish_download(username, id):
    downloading_user_dir = path.join(DOWNLOADING_DIR, username)
    finish_user_dir = path.join(DOWNLOADED_DIR, username)
    if not path.exists(finish_user_dir):
        os.mkdir(finish_user_dir)

    src = path.join(downloading_user_dir, id)
    dst = path.join(finish_user_dir, id)

    try:
        os.rename(src, dst)
    except Exception as e:
        raise Exception('finish download exception, username: %s, id: %s, src: %s, dst: %s, raw: %s' % (username, id, src, dst, e), exc_info=True)


def get_undetected(number):
    '''
    返回未检测脸的
    :param number:要返回的个数
    :return:[ {'username': username, 'id': id, 'dir': 到这个人脸文件夹的路径}, {}, ...]
    '''
    namelist = []
    for username in os.listdir(DOWNLOADED_DIR):
        if len(namelist) < number:
            this_user_folder = path.join(DOWNLOADED_DIR, username)
            try:
                ids = os.listdir(this_user_folder)
                for id in ids:
                    if len(namelist) < number:
                        namelist.append({'username': username,
                                         'id': id,
                                         'dir': path.join(this_user_folder, id)})
                    else:
                        break
            except Exception as e:
                logger.error('get undetected exception, this_user_folder: %s, ids: %s, raw: %s' % (this_user_folder, ids, e), exc_info=True)
        else:
            break
    return namelist


def finish_detect(username, id):
    src = path.join(DOWNLOADED_DIR, username, id)
    dst_user_folder = path.join(DETECTED_DIR, username)
    if not path.exists(dst_user_folder):
        os.mkdir(dst_user_folder)

    dst = path.join(dst_user_folder, id)
    try:
        os.rename(src, dst)
    except Exception as e:
        raise Exception('finish detect exception, username: %s, id: %s, src: %s, dst: %s, raw: %s' % (username, id, src, dst, e), exc_info=True)


def get_untransmitted(number):
    '''

    :param number: number of dirs to return
    :return: [{'username': username,
                'id':: id,
                'chinese_name': person's chinese name,
                'english_name': person's english name,
                'dir': dir of this person},
            {}, ...]
    '''
    namelist = []
    for username in os.listdir(DETECTED_DIR):
        if len(namelist) < number:
            this_user_folder = path.join(DETECTED_DIR, username)
            try:
                ids = os.listdir(this_user_folder)
                for id in ids:
                    if len(namelist) < number:
                        info = _get_info_of_one(path.join(this_user_folder, id))
                        namelist.append({'username': username,
                                         'chinese_name': info['ch_name'],
                                         'english_name': info['en_name'],
                                         'keyword': info['keyword'],
                                         'id': id,
                                         'dir': path.join(this_user_folder, id)})
                    else:
                        break
            except Exception as e:
                logger.error('get untransmitted exception, this_user_folder: %s, ids: %s, raw: %s' % (this_user_folder, ids, e), exc_info=True)
        else:
            break
    return namelist


def finish_transmit(username, id):
    target = path.join(DETECTED_DIR, username)
    os.system('rm -rf %s' % path.join(target, id))


def _get_info_of_one(target):
    ret = {}
    try:
        with open(path.join(target, '_name')) as f:
            ret['ch_name'] = f.readline().strip()
            ret['en_name'] = f.readline().strip()
        with open(path.join(target, '_keyword')) as f:
            ret['keyword'] = f.readline().strip()
        return ret

    except Exception as e:
        raise Exception({'msg': 'get info of one exception, target: %s' % target, 'raw': e})