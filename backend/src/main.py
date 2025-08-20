#!/usr/bin/env python
#!-*- coding:utf-8 -*-

'''
main.py

@since: 2023-07-21
@version: 2023-08-29
@updated: Akitoshi Abe
'''

import time
import os
import datetime

import sateraito_logger as logging  # GAEGEN2対応:独自ロガー
import sateraito_inc
from sateraito_inc import developer_mode

import os
import json
from flask import jsonify

from flask import Flask, Response, render_template, request, session	# GAEGEN2対応:WebフレームワークとしてFlaskを使用
from google.appengine.api import wrap_wsgi_app												# GAEGEN2対応:AppEngine API SDKを使用する際に必要（yamlの　app_engine_apis: true　指定も必要）
from werkzeug.routing import BaseConverter														# GAEGEN2対応:routingで正規表現を使うために使う
from ucf.utils import jinjacustomfilters
from utilities.gaesession import GaeNdbSessionInterface								# GAEGEN2対応：セッション管理 セッション管理：DB版（SameSite対応などカスタマイズするのでソースコード直接参照）

_TIME_START = time.time()
app = Flask(__name__)

if developer_mode:
    from google.cloud import ndb
    client = ndb.Client()
    def ndb_wsgi_middleware(wsgi_app):
        def middleware(environ, start_response):
            with client.context():
                return wsgi_app(environ, start_response)
        return middleware
		
    app.wsgi_app = ndb_wsgi_middleware(app.wsgi_app)
else:
    app.wsgi_app = wrap_wsgi_app(app.wsgi_app)

# セッション管理:セッションインタフェースを上書き
# 参考）https://flask.palletsprojects.com/en/2.2.x/api/#sessions
# permanent=True…ブラウザを閉じてもセッションが残るオプション
# セッション有効期限：permanent=Falseでも使用する
app.session_interface = GaeNdbSessionInterface(app, permanent=True)  # DataStore版
app.secret_key = sateraito_inc.MD5_SUFFIX_KEY_DICT['sateraito-web-search-ai']
app.permanent_session_lifetime = datetime.timedelta(hours=24*31)  # ワークフローは31日セッションが継続
app.config.update(
SESSION_COOKIE_NAME='SATEID2',  # g2版はSATEIDからSATEID2に変更
SESSION_COOKIE_SECURE=True,
SESSION_COOKIE_HTTPONLY=True,
SESSION_COOKIE_SAMESITE='None',
SESSION_USE_SIGNER=True,
SESSION_REFRESH_EACH_REQUEST=True)

# GAEGEN2対応：URLマッピングを正規表現で行うためのクラス
class RegexConverter(BaseConverter):
	def __init__(self, url_map, *items):
		super(RegexConverter, self).__init__(url_map)
		self.regex = items[0]
app.url_map.converters['regex'] = RegexConverter

# from health import add_url_rules as health_add_url_rules
# health_add_url_rules(app)

from  introducing import add_url_rules as introducing_add_url_rules
introducing_add_url_rules(app)

from user import add_url_rules as user_add_url_rules
user_add_url_rules(app)

# from checkuser import add_url_rules as checkuser_add_url_rules
# checkuser_add_url_rules(app)

# from contract import add_url_rules as contract_add_url_rules
# contract_add_url_rules(app)

from oidccallback import add_url_rules as oidccallback_add_url_rules
oidccallback_add_url_rules(app)

# from oidccallback4sso import add_url_rules as oidccallback4sso_add_url_rules
# oidccallback4sso_add_url_rules(app)

# from oidccallback4ssite import add_url_rules as oidccallback4ssite_add_url_rules
# oidccallback4ssite_add_url_rules(app)

@app.route('/health')
def health():
    """Health check với thông tin chi tiết"""
    cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    cred_info = "Not set"
    
    if cred_path and os.path.exists(cred_path):
        try:
            with open(cred_path, 'r') as f:
                sa_info = json.load(f)
            cred_info = f"Service Account: {sa_info.get('client_email')}"
        except:
            cred_info = f"File exists but can't read: {cred_path}"
    
    return jsonify({
        'status': 'ok',
        'app_name': 'Sateraito Web Search AI',
        'credentials_info': cred_info,
    })

# GAEGEN2対応：View関数方式でページを定義（本来はflask.views.MethodViewクラス方式を採用だが簡単な処理はView関数でもOK）
@app.route('/_ah/warmup', methods=['GET', 'POST'])
def warmup():
	logging.info('warmup instance.')
	return Response(__name__, status=200)

@app.route('/_ah/start', methods=['GET'])
def start():
	return Response(__name__, status=200)

@app.route('/_ah/stop', methods=['GET'])
def stop():
	return Response(__name__, status=200)

# GAEGEN2対応：エラーハンドリング処理（各ページで処理できなかったエラーを大本のここでハンドリング可能）
@app.errorhandler(400)
def handle_bad_request(e):
	logging.exception(e)
	return 'Bad Request', 400

@app.errorhandler(502)
def handle_bad_gateway(e):
	logging.exception(e)
	return 'Bad Gateway', 502

@app.errorhandler(404)
def handle_notfound(e):
	logging.warning(e)
	return 'Not Found', 404

@app.errorhandler(500)
def handle_internalservererror(e):
	logging.exception(e)
	return 'Internal Server Error', 500

@app.template_filter()
def jsescape(value):
	return jinjacustomfilters.escapeJavaScriptString(value)

@app.template_filter()
def escapejs(value):
	return jinjacustomfilters.escapejs(value)

if hasattr(logging, 'register_app'):
	if logging.GROUP_LOGS_BY_REQUEST:
		logging.register_app(app)

if __name__ == '__main__':
    threaded = True

    if os.environ.get('SATERAITO_SET_SINGLETHREAD_MODE', '') == 'True':
        # defalutサービスをF1かつシングルスレッドで動作させる
        threaded = False

    if developer_mode:
        # 開発モードでは、ホストとポートを指定
        app.run(host=sateraito_inc.HOST, port=sateraito_inc.PORT, debug=sateraito_inc.debug_mode, threaded=threaded)
    else:
        # 本番モードでは、デフォルトのホストとポートを使用
        app.run(debug=sateraito_inc.debug_mode, threaded=threaded)

_TIME_END = time.time()
_TIME_INIT = _TIME_START - _TIME_END
logging.info('INIT main.py took: ~%.3fs' % _TIME_INIT)
