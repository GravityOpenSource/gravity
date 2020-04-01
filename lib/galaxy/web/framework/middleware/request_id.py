# coding=utf-8
import base64
import datetime
import os
import sys
import time
import uuid

from Crypto import Hash
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from galaxy import config


class VerifyException(Exception):
    pass


class RequestIDMiddleware(object):
    """
    A WSGI middleware that creates a unique ID for the request and
    puts it in the environment
    """

    def __init__(self, app, application, global_conf=None):
        self.app = app
        self.application = application

    def __call__(self, environ, start_response):
        environ['request_id'] = uuid.uuid1().hex
        response = self.app(environ, start_response)
        try:
            trans = self.application.transaction_factory(environ)
            if not trans.get_user():
                return response
        except:
            pass
        if environ.get('REQUEST_URI') == '/admin/license_reg':
            return response
        return RsaVerify().verify(response)


class RsaVerify:
    def __init__(self):
        node = uuid.getnode()
        self.machine_code = str(uuid.UUID(int=int((str(node)*3)[:39])))
        self.expire = ''
        self.error_msg = ''
        self.license = ''
        root_path = config.find_root({})
        self.license_file_path = os.path.join(root_path, 'LICENSE.txt')
        self._init_license()

    def _init_license(self):
        if not os.path.exists(self.license_file_path):
            return
        with open(self.license_file_path, mode='r') as f:
            try:
                self.license = f.read()
                self.license_dec = base64.b64decode(self.license).decode().split('\t')
                self.pubkey = self.license_dec[1]
                self.expire = self.license_dec[2]
            except:
                pass

    def rsa_obj(self, key):
        return PKCS1_v1_5.new(RSA.import_key(key))

    def hash_code(self):
        rand_hash = Hash.SHA256.new()
        code = self.machine_code + '\t' + self.expire
        rand_hash.update(code.encode())
        return rand_hash

    def date_to_timestamp(self, date):
        if sys.version_info.major == 2:
            return int((time.mktime(date.timetuple()) + date.microsecond / 1000000.0))
        else:
            return int(date.timestamp())

    def write_reg_file(self, code):
        with open(self.license_file_path, mode='w') as f:
            return f.write(code)

    def sign_with_license(self):
        sign = self.license_dec[0]
        return base64.b64decode(sign)

    def expire_verify(self):
        now = self.date_to_timestamp(datetime.datetime.today())
        expire = self.date_to_timestamp(datetime.datetime.strptime(self.expire, '%Y-%m-%d'))
        if now > expire:
            raise VerifyException('授权文件无效：已过期')

    def verify_with_pubkey(self):
        verifier = self.rsa_obj(self.pubkey)
        sign = self.sign_with_license()
        res = verifier.verify(self.hash_code(), sign)
        if not res:
            raise VerifyException('授权文件无效')
        self.expire_verify()

    def verify(self, response):
        try:
            self.verify_with_pubkey()
        except VerifyException as e:
            self.error_msg = str(e)
        except TypeError:
            self.error_msg = '授权文件无效'
        except:
            self.error_msg = '未知错误，请联系管理员'
        if self.error_msg:
            response = self.error_template()
        return response

    def error_template(self):
        from mako.template import Template
        file_path = os.path.abspath(__file__)
        dir_path = os.path.dirname(file_path)
        t = Template(filename='%s/../templates/rsa.mako' % dir_path,
                     input_encoding='utf-8',
                     output_encoding='utf-8',
                     default_filters=['decode.utf_8'])
        return t.render(verify=self)
