# coding: utf8

__author__ = 'neodooth'

from utils import data_util
from config import SEARCH_BASE_URL, USER_AGENT, DOWNLOAD_NUMBER
from utils.net_util import send_mail

import requests, grequests
from gevent import Timeout
from pyquery import PyQuery as pq

import threading, time, logging, json
from os import path

logger = logging.getLogger(__name__)


def start_worker():
    logger.info('start worker')
    worker_thread = threading.Thread(target=_woker)
    worker_thread.setDaemon(True)
    worker_thread.start()


def _woker():
    last_time_sendmail = 0
    while True:
        try:
            namelists = data_util.get_undownloaded()

            if len(namelists) > 0:
                s = '\n'.join(['%s' % json.dumps(n, ensure_ascii=False) for n in namelists])
                logger.info('download list:\n%s' % s)

            for nl in namelists:
                username = nl['username']
                id = nl['id']
                name = nl['name']
                kw = nl['keyword']
                logger.info('begin download %s(%s) for %s' % (name, kw, username))
                save_to = data_util.prepare_download(username, id)
                download(name, kw, save_to)
                logger.info('finished download %s(%s) for %s' % (name, kw, username))
                data_util.finish_download(username, id)
        except Exception as e:
            logger.error('downloader exception, raw: %s' % e, exc_info=True)
            if time.time() - last_time_sendmail > 600:
                send_mail('worker exception', str(e))
                last_time_sendmail = time.time()
        time.sleep(2)


def download(name, keyword, save_to):
    search_url = SEARCH_BASE_URL % ((name+' '+keyword).replace(' ', '+'))
    downloaded_number = 0

    next_paged = False

    while downloaded_number < DOWNLOAD_NUMBER:
        # 搜索结果页，user-agent是config里那个可以获得不需要js加载搜索结果的静态网页
        resp = requests.get(search_url, headers={'User-Agent': USER_AGENT})
        search_result = pq(resp.content)
        # 每个结果的class是image，href是这个结果的详情页
        detail_pages = [d.attrib['href'] for d in search_result('.image')]

        # 对每个结果获取详情页
        detail_requests = (grequests.get(u, headers={'User-Agent': USER_AGENT}) for u in detail_pages)
        detail_resps = grequests.map(detail_requests)
        # 详情页里下标是3的a标签的链接是原图链接

        images_urls = []
        for r in detail_resps:
            try:
                images_urls.append(pq(r.content)('a')[4].attrib['href'])
            except Exception as e:
                logger.error('download get image url exception, url: %s, raw: %s' % (search_url, e))

        download_requests = (grequests.get('http://images.google.com/' + u, stream=True, timeout=3) for u in images_urls)

        images = grequests.map(download_requests)

        # 保存图片
        for i in range(len(images_urls)):
            img = images[i]
            if img is not None:
                success = False
                with Timeout(2, False):
                    with open(path.join(save_to, '%d.jpg' % downloaded_number), 'wb') as f:
                        # requests库文档推荐写法，但是grequests不知道该不该也这么写
                        for chunk in img.iter_content(4096):
                            f.write(chunk)
                    downloaded_number += 1
                    success = True
                if success is False:
                    logger.info('download timed out, image: %s' % images_urls[i])

        # 下一页搜索结果
        prev_next_buttons = search_result('#navbar').children()
        if len(prev_next_buttons) == 0 or len(prev_next_buttons) == 1 and next_paged:
            logger.info('%s reched end of search result. break' % name)
            break

        search_url = 'http://www.google.com' + prev_next_buttons[-1].attrib['href']
        logger.info('downloaded %s %d/%d' % (name, downloaded_number, DOWNLOAD_NUMBER))

        next_paged = True