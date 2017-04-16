# coding: utf8

__author__ = 'neodooth'

import logging
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

from config import ROLE

logging.basicConfig(filename=ROLE+'.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if ROLE == 'website':
    from website import app
else:
    from downloader import app

logging.info('starting %s' % ROLE)
app.run(debug=True, use_reloader=False, threaded=True, host='0.0.0.0', port=2938)
