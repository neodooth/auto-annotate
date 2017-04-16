# coding: utf8

__author__ = 'neodooth'

from utils import data_util
from utils.net_util import send_mail
from config import TMP_DIR, DETECT_SERVER_HOST, DETECT_SERVER_PORT, TOO_MANY_FACES_THRESHOLD

import threading, time, os, socket, json, logging
from os import path

logger = logging.getLogger(__name__)


def start_detector():
    print 'starting detector'
    worker_thread = threading.Thread(target=_detector)
    worker_thread.setDaemon(True)
    worker_thread.start()


def _detector():
    last_time_sendmail = 0
    while True:
        try:
            namelists = data_util.get_undetected(10)
            for nl in namelists:
                username = nl['username']
                id = nl['id']
                directory = nl['dir']

                with open(path.join(directory, '_options')) as f:
                    options = json.load(f)
                    skip = options['dont_detect_face']

                with open(path.join(directory, '_name')) as f:
                    ch_name = f.readline().strip()
                    en_name = f.readline().strip()

                try:
                    rects_path = path.join(directory,'_rects')
                    if skip is True:
                        logger.info('skip detect %s/%s/%s for %s' % (id, ch_name, en_name, username))
                        for f in [_ for _ in os.listdir(directory) if _.endswith('.jpg')]:
                            os.system('mv {}/{} {}/other_{}_0.jpg'.format(directory, f, directory, f[:-4]))
                        if not os.path.exists(rects_path):
                            with open(rects_path,'w+') as f1:
                                pass
                    else:
                        logger.info('detect %s/%s/%s for %s' % (id, ch_name, en_name, username))
                        pic_num = 0
                        # 找到上次检测到达的id
                            
                        for f in os.listdir(directory):
                            if f.startswith('face'):
                                this_num = int(f.split('_')[1])
                                if this_num >= pic_num:
                                    pic_num = this_num + 1

                        for f in os.listdir(directory):
                            if f.startswith('face'):  # 跳过之前完成的检测
                                continue
                            img_path = path.join(directory, f)

                            if f.endswith('.jpg'):
                                result = do_detect(img_path)
                                #result = {"rects":[{"x":1,"y":2,"w":3,"h":4},{"x":4,"y":4,"w":3,"h":4},{"x":8,"y":10,"w":6,"h":6}]}
               
                                if len(result['rects']) > TOO_MANY_FACES_THRESHOLD:
                                    logger.info('too many faces, remove. %s, %d faces' % (f, len(result['rects'])))
                                else:
                                    face_num = 0
                                    detected_rects = {}
                                    for rect in result['rects']:
                                        dest_file = os.path.join(directory, 'face_%s_%d.jpg' % (f[:-4], face_num))
                                        file_name = os.path.join('face_%s_%d.jpg' % (f[:-4], face_num))
                                        extended_rect = _extend_rect(rect['x'], rect['y'], rect['w'], rect['h'])
                                        detected_rects[file_name]= [extended_rect['x'],extended_rect['y'],extended_rect['w'],extended_rect['h']]
                                        cmd = 'convert "%s" -crop %dx%d+%d+%d "%s"' \
                                                  % (img_path, extended_rect['w'], extended_rect['h'], extended_rect['x'], extended_rect['y'], dest_file)
                                        os.system(cmd)
                                        # 太大的没必要
                                        if extended_rect['w'] > 600 or extended_rect['h'] > 600:
                                            os.system('convert -resize %dx%d "%s" "%s"'
                                                      % (600, 600, dest_file, dest_file))
                                        face_num += 1
                                    pic_num += 1
                                    
                                    if not os.path.exists(rects_path):
                                        with open(rects_path,'w+') as f1:
                                            json.dump(detected_rects,f1)
                                    else:
                                        with open(rects_path,'r+') as f1:
                                            rects = json.load(f1)
                                            merge_rects = dict(rects,**detected_rects)
                                        with open(rects_path,'w+') as f2:
                                            json.dump(merge_rects,f2)           
                            if not f.startswith('_'):
                                os.remove(img_path)

                        logger.info('finished detect %s/%s/%s for %s. %d pictures' % (id, ch_name, en_name, username, pic_num))
                    data_util.finish_detect(username, id)

                except Exception as e:
                    raise Exception({'msg': 'error detecting %s/%s/%s for %s' % (id, ch_name, en_name, username), 'raw': e})

        except Exception as e:
            if time.time() - last_time_sendmail > 600:
                send_mail('detector exception', str(e))
                last_time_sendmail = time.time()
            logger.error('detector exception, raw: %s' % e, exc_info=True)
        time.sleep(2)


def do_detect(img):
    cwd = os.getcwd()
    input_file = path.join(cwd, TMP_DIR, 'detect.input.json')
    output_file = path.join(cwd, TMP_DIR, 'detect.output.json')
    sock_cmd = '#'.join([input_file, output_file, 'detect'])

    with open(input_file, 'w') as f:
        print >> f, json.dumps([{'path': path.join(cwd, img), 'id': 0}]),

    address = (DETECT_SERVER_HOST, DETECT_SERVER_PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(address)
    s.send(sock_cmd)
    resp = s.recv(1024)
    s.close()

    if resp == 'finished':
        with open(output_file) as f:
            results = json.load(f)
            return results[0]
    else:
        raise Exception({'msg': 'detector returned %s' % resp})


def _extend_rect(x, y, w, h):
    scale = 3
    x -= w * (scale-1) / 2
    y -= h * (scale-1) / 2
    w *= scale
    h *= scale
    if x < 0:
        w += x
        x = 0
    if y < 0:
        h += y
        y = 0
    return {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)}