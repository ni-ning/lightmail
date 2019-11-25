# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

import sys
import os
import logging
import socket
import smtplib
import six
from email.mime.multipart import MIMEMultipart
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email.parser import Parser
import uuid

from lightmail import utils


class Email(object):

    def __init__(self, config=None):
        self._config = config or {}
        if not self._config:
            self._config = utils.load_config('email')

        self._config['ssl'] = True if str(self._config['port']) in ['465', '587'] else False

    def _get_content(self, content):
        name = ""
        if content and len(content) > 1024:
            pass
        elif not isinstance(content, six.string_types):
            pass
        elif content == 'STDIN':
            content = sys.stdin.read()
        elif content.startswith('@') and os.path.exists(content[1:]):
            name = content[1:]
            content = open(content[1:], 'rb').read()
        return content, name

    def build_email(self, args):
        sub_msgs, att_msgs = [], []
        if args.get('text'):
            content, _ = self._get_content(args['text'])
            sub_msg = MIMEText(content, 'plain', 'utf-8')
            sub_msgs.append(sub_msg)
        if args.get('html'):
            content, _ = self._get_content(args['html'])
            sub_msg = MIMEText(content, 'html', 'utf-8')
            sub_msgs.append(sub_msg)
        if args.get('content'):
            content, _ = self._get_content(args['content'])
            sub_msg = MIMEText(content, 'html', 'utf-8')
            sub_msgs.append(sub_msg)

    def send(self, msg):
        cls = smtplib.SMTP_SSL if self._config['ssl'] else smtplib.SMTP
        client = cls(host=self._config['host'],
                     port=self._config['port'],
                     timeout=self._config.get('timeout', socket._GLOBAL_DEFAULT_TIMEOUT))
        client.login(self._config['user'], self._config['password'])

        _to = [msg[i].split(',') for i in ['to', 'cc', 'bcc'] if msg.get(i)]
        if not msg['From']:
            msg['From'] = self._config['user']
        ret = client.send_message(msg, self._config['user'], sum(_to, []))

        log_info = {'Message-From': msg['From'], 'Message-To': msg['to'],
                    'Message-Subject': msg['Subject'], "Message-ID:": msg['Message-ID']}
        logging.info(log_info)
        client.quit()

        return ret


def send_email(to, content=None, title=None, mail_from=None,
               attach=None, cc=None, bcc=None, text=None, headers=None):
    '''

    :param to:
    :param content:
    :param title:
    :param mail_from:
    :param attach:
    :param cc:
    :param bcc:
    :param text: 邮件纯文本内容
    :param headers:
    :return:
    '''
    arg_dict = dict(to=to)

    arg_dict['to'] = to
    arg_dict['content'] = content
    arg_dict['title'] = title
    arg_dict['mail_from'] = mail_from
    arg_dict['attach'] = attach
    arg_dict['cc'] = cc
    arg_dict['bcc'] = bcc
    arg_dict['text'] = text
    arg_dict['headers'] = headers or {}
