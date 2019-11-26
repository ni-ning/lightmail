# -*- coding:utf-8 -*-

import six
import os
import logging
from configparser import ConfigParser

EMAIL_CFG_NAME = 'lightmail.cfg'


def load_config(section):
    user_home_cfg_path = os.path.join(os.path.expanduser('~'), EMAIL_CFG_NAME)
    config, cf = {}, ConfigParser()

    if os.path.exists(EMAIL_CFG_NAME):
        cf.read(EMAIL_CFG_NAME)
        logging.info('Loading config from %s' % EMAIL_CFG_NAME)
    elif os.path.exists(user_home_cfg_path):
        cf.read(user_home_cfg_path)
        logging.info("Loading config from user_home_cfg_path")
    elif os.path.exists('/etc/%s' % EMAIL_CFG_NAME):
        cf.read('/etc/%s' % EMAIL_CFG_NAME)
        logging.info("Loading config from /etc/%s" % EMAIL_CFG_NAME)
    else:
        cf = None
        logging.error('Not found %s' % EMAIL_CFG_NAME)

    if cf:
        for opt in cf.options(section):
            config[opt] = cf.get(section, opt)
    return config


def to_unicode(s):
    if not isinstance(s, six.text_type):
        return s.decode('utf-8', 'ignore')
    return s
