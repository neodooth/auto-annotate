# coding: utf8

__author__ = 'neodooth'

from config import ANNOTATED_DIR

import os, logging, datetime
from os import path

logger = logging.getLogger(__name__)


def annotated_last_n_days(n):
    '''

    :param n:统计多少天内的
    :return:[ {
            'username': 'username',
            'total_pictures': 12, # 过去n天一共标注了多少图片,
            'total_people': 2, # 过去n天标注了多少人
            'each_day_pictures': [3,1,4,5,2] # 过去n天每天分别标注了多少图片
            'each_day_people': [0,0,1,0,1] # 过去n天每天标注多少人
        }, {}, ...
    ] # 按total降序排列
    '''

    ret = []
    try:
        for u in os.listdir(ANNOTATED_DIR):
            each_day_pictures = [0 for i in range(n+1)]
            each_day_people = [0 for i in range(n+1)]

            today = datetime.date.today()
            this_user_dir = path.join(ANNOTATED_DIR, u)
            for p in os.listdir(this_user_dir):
                with open(path.join(this_user_dir, p, '_date')) as f:
                    _date = f.readline().strip()
                dttm = _date.split(' ')
                dt = dttm[0].split('-')
                tm = dttm[1].split(':')
                file_date = datetime.date(int(dt[0]), int(dt[1]), int(dt[2]))
                diff = (today - file_date).days
                if (diff == 0 and int(tm[0]) < 12) or (0 < diff < n) or (diff == n and int(tm[0]) >= 12):
                    each_day_people[n-diff] += 1
                    each_day_pictures[n-diff] += len([x for x in os.listdir(path.join(this_user_dir, p)) if x.endswith('.jpg')])

            ret.append({
                'username': u,
                'total_pictures': sum(each_day_pictures),
                'total_people': sum(each_day_people),
                'each_day_pictures': each_day_pictures,
                'each_day_people': each_day_people
            })
        return sorted(ret, key=lambda x: x['total_pictures'], reverse=True)

    except Exception as e:
        logger.error('annotated_last_n_days exception, n: %d, raw: %s' % (n, e), exc_info=True)
        return {}
        # raise Exception({'msg': 'annotated_last_n_days exception, n: %d, raw: %s' % (n, e), 'raw': e})