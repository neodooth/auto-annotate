# coding: utf8

__author__ = 'neodooth'

from utils.data_util import get_unsubmitted, finish_untransmitted
from utils.net_util import send_names, send_mail, test_downloader

import threading, time, logging, json

logger = logging.getLogger(__name__)


def start_worker():
    logger.info('starting transmitter')
    worker_thread = threading.Thread(target=_woker)
    worker_thread.setDaemon(True)
    worker_thread.start()


def _woker():
    last_time_sendmail = 0
    while True:
        try:
            namelists = get_unsubmitted()
            for nl in namelists:
                logger.info('send downloader username: %s, names: %s' % (nl['username'], json.dumps(nl['namelist'], ensure_ascii=False)))
                send_names(nl['username'], nl['namelist'])
                finish_untransmitted(nl['username'], nl['namelist'])

            if len(namelists) == 0:
                test_downloader()

        except Exception as e:
            if time.time() - last_time_sendmail > 600:
                send_mail('transmitter exception', str(e))
                last_time_sendmail = time.time()
            logger.error(e, exc_info=True)
        time.sleep(60)
