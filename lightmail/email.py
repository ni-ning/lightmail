# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

import sys
import os
import logging
import socket
import smtplib
import six
import mimetypes
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import formatdate

import uuid

from lightmail import utils


class Email(object):
    CONFIG = None

    def __init__(self, config=None):
        self._config = config or {}

        if not self._config:
            self._config = self.CONFIG or {}

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

        attach_size, file_attach = 0, []
        if args.get('attach'):
            name, att_content = '', ''
            args['attach'] = [args['attach']] if isinstance(args['attach'], six.string_types) \
                else args['attach']
            for idx, att in enumerate(args['attach']):
                if isinstance(att, six.string_types):
                    att_content, name = self._get_content(att)
                    if name:
                        file_attach.append(name)
                    elif not att_content:
                        continue
                elif isinstance(att, tuple):
                    name = att[0]
                    att_content = att[1].read() if hasattr(att[1], 'read') else att[1]
                    file_attach.append((name, att_content))
                if not name:
                    name = 'attachment_%s.txt' % idx

                name = os.path.basename(name)
                subtype = mimetypes.guess_type(name)[0] or 'text/plain'
                subtype = mimetypes.guess_type(att_content, subtype)
                att_msg = MIMEApplication(att_content, subtype)
                att_msg.add_header('Content-Disposition', 'attachment', filename=Header(name, 'utf-8').encode())
                att_msg.add_header('Content-ID', '<%s>' % idx)
                att_msg.add_header('X-Attachment-Id', '%s' % idx)
                att_msgs.append(att_msg)
                attach_size += len(att_content)

        main_msg = MIMEMultipart()
        if sub_msgs:
            sub_main = MIMEMultipart('alternative')
            for msg in sub_msgs:
                sub_main.attach(msg)
            main_msg.attach(sub_main)
        if att_msgs:
            for att_msg in att_msgs:
                main_msg.attach(att_msg)

        args['title'] = args.get('title') or '无题'
        if isinstance(args['title'], list):
            args['title'] = ''.join(args['title'])

        main_msg['Subject'] = Header(utils.to_unicode(args['title']))
        main_msg['From'] = args.get('mail_from', '')
        main_msg['To'] = ', '.join(args['to']) if isinstance(args['to'], list) \
            else args['to']
        if args.get('cc'):
            main_msg['Cc'] = ", ".join(args['cc']) if isinstance(args['cc'], list) \
                else args['cc']
        if args.get('bcc'):
            main_msg['Bcc'] = ", ".join(args['bcc']) if isinstance(args['bcc'], list) \
                else args['bcc']
        main_msg['Date'] = formatdate(localtime=True)
        main_msg['Message-ID'] = '%s.%s' % (str(uuid.uuid1()), main_msg['From'])
        return main_msg

    def send_email(self, msg):
        cls = smtplib.SMTP_SSL if self._config['ssl'] else smtplib.SMTP
        client = cls(host=self._config['host'],
                     port=self._config['port'],
                     timeout=self._config.get('timeout', socket._GLOBAL_DEFAULT_TIMEOUT))
        client.login(self._config['user'], self._config['password'])

        _to = [msg[i].split(',') for i in ['to', 'cc', 'bcc'] if msg.get(i)]
        if not msg['From']:
            msg['From'] = self._config['user']
        ret = client.send_message(msg, self._config['user'], sum(_to, []))

        log_info = {'Message-From': msg['From'], 'Message-To': msg['To'],
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

    e = Email()
    msg = e.build_email(arg_dict)
    return e.send_email(msg)
