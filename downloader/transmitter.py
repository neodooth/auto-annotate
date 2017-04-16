# coding: utf8

__author__ = 'neodooth'

from utils import data_util, net_util

import threading, time, os, logging, json, random
from os import path

logger = logging.getLogger(__name__)


def start_transmitter():
    logger.info('starting transmitter')
    worker_thread = threading.Thread(target=_transmitter)
    worker_thread.setDaemon(True)
    worker_thread.start()


def _transmitter():
    last_time_sendmail = 0
    while True:
        id = ''
        ch_name = ''
        en_name = ''
        username = ''
        try:
            ones = data_util.get_untransmitted(5)
            random.shuffle(ones)

            if len(ones) > 0:
                s = '\n'.join(['%s %s %s %s'
                               % (o['username'], o['id'], o['chinese_name'], o['english_name']) for o in ones])
                logger.info('transmit list:\n%s' % s)

            for one in ones:
                username = one['username']
                id = one['id']
                ch_name = one['chinese_name']
                en_name = one['english_name']
                directory = one['dir']
                logger.info('begin transmit for %s, one: %s' % (username, json.dumps(one, ensure_ascii=False)))
                transmit(username, id, directory)
                data_util.finish_transmit(username, id)
                logger.info('finished transmit for %s, one: %s' % (username, json.dumps(one, ensure_ascii=False)))
        except Exception as e:
            logger.error('transmitter exception when transmit %s/%s/%s for %s: %s'
                         % (id, ch_name, en_name, username, e), exc_info=True)
            if time.time() - last_time_sendmail > 600:
                net_util.send_mail('transmitter exception', str(e))
                last_time_sendmail = time.time()

        time.sleep(60)


def transmit(username, id, directory):
    to_send = []

    try:
        imgs = os.listdir(directory)
        for img in imgs:
            to_send.append(path.join(directory, img))
        return net_util.send_images(username, id, to_send)
    except Exception as e:
        logger.error('transmit exception: ' + str(e), exc_info=True)
        raise Exception({'msg': 'transmit exception, username: %s, id: %s, directory: %s' % (username, id, directory), 'raw': e})