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
from sateraito_inc import developer_mode, flask_docker

import os
import json
from flask import jsonify, send_from_directory
from flask_cors import CORS, cross_origin

from flask import Flask, Response, render_template, request, session	# GAEGEN2対応:WebフレームワークとしてFlaskを使用

from google.appengine.api import wrap_wsgi_app												# GAEGEN2対応:AppEngine API SDKを使用する際に必要（yamlの　app_engine_apis: true　指定も必要）
from werkzeug.routing import BaseConverter														# GAEGEN2対応:routingで正規表現を使うために使う
from ucf.utils import jinjacustomfilters
from utilities.gaesession import GaeNdbSessionInterface								# GAEGEN2対応：セッション管理 セッション管理：DB版（SameSite対応などカスタマイズするのでソースコード直接参照）

_TIME_START = time.time()
app = Flask(__name__)

if flask_docker:
    from google.cloud import ndb
    client = ndb.Client(namespace="vn2.sateraito.co.jp")
    def ndb_wsgi_middleware(wsgi_app):
        def middleware(environ, start_response):
            with client.context():
                return wsgi_app(environ, start_response)
        return middleware
    app.wsgi_app = ndb_wsgi_middleware(app.wsgi_app)
    
    import memcache
    
    @app.route('/images/<path:filename>')
    def custom_images(filename):
        return send_from_directory('images', filename)
    @app.route('/js/<path:filename>')
    def custom_js(filename):
        return send_from_directory('js', filename)
    @app.route('/css/<path:filename>')
    def custom_css(filename):
        return send_from_directory('css', filename)
    
    @app.route('/clear-memcache', methods=['GET'])
    def clear_memcache():
        """Clear all memcache entries."""
        memcache.clear_all_cache()  # GAEGEN2対応:起動時にキャッシュをクリア（開発モードでのみ実行）
        return jsonify({'status': 'success', 'message': 'Memcache cleared.'})
else:
    app.wsgi_app = wrap_wsgi_app(app.wsgi_app)

# CORS
from sateraito_inc import CORS_LIST
CORS(app, resources={r"/*": {"origins": CORS_LIST}}, supports_credentials=True)
CORS(app, resources={r"/static/*": {"origins": '*'}}, supports_credentials=True)

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

# Firebase initialize
import firebase

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

# 
from sateraito_utils import add_url_rules as sateraito_utils_add_url_rules
sateraito_utils_add_url_rules(app)

from operationlog import add_url_rules as operation_log_add_url_rules
operation_log_add_url_rules(app)

from client_websites import add_url_rules as client_websites_add_url_rules
client_websites_add_url_rules(app)

from box_search import add_url_rules as box_search_add_url_rules
box_search_add_url_rules(app)

from llm_configuration import add_url_rules as llm_configuration_add_url_rules
llm_configuration_add_url_rules(app)

from llm_actions import add_url_rules as llm_actions_add_url_rules
llm_actions_add_url_rules(app)

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

@app.route('/assets/<path:filename>')
def custom_assets(filename):
    return send_from_directory('static/frontend/assets', filename)
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory('static', filename)

# tenant/app_id/admin_console/(任意のパス)
# Example: http://localhost:8080/vn2.sateraito.co.jp/default/admin_console or https://vn2.sateraito.co.jp/default/admin_console/domains
@app.route('/<string:tenant>/<string:app_id>/login', methods=['GET'])
@app.route('/<string:tenant>/<string:app_id>/box_search', methods=['GET'])
@app.route('/<string:tenant>/<string:app_id>/admin_console', methods=['GET'])
@app.route('/<string:tenant>/<string:app_id>/admin_console/<path:page_name>', methods=['GET'])
def page(tenant, app_id, page_name=None):
    # ページのテンプレートをレンダリング
    try:
        return render_template(f'reactjs_frontend.html')
    except Exception as e:
        logging.exception('Error rendering page: %s', e)
        return 'Internal Server Error', 500

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
