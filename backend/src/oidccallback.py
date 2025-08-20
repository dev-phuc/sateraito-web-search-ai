#!/usr/bin/python
# coding: utf-8

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'

import flask
from flask import Flask, Response, render_template, request, make_response, session, redirect, after_this_request
from flask.views import View, MethodView
import requests
import google.oauth2.credentials	# GAEGEN2対応
import dateutil
import itsdangerous

# # set default encodeing to utf-8
# import sys
# stdin = sys.stdin
# stdout = sys.stdout
# reload(sys)
# sys.setdefaultencoding('utf-8')
# sys.stdin = stdin
# sys.stdout = stdout

import os
import jinja2
# import webapp2

# GAEGEN2対応:独自ロガー
# import logging
import sateraito_logger as logging

import json
import urllib
import base64
import datetime
import time
import random
import httplib2

from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api import urlfetch

import sateraito_inc
import sateraito_func
import sateraito_page

from google.appengine.runtime import DeadlineExceededError
# from oauth2client.client import OAuth2WebServerFlow  # g2対応
from oauthlib.oauth2 import WebApplicationClient

from ucf.utils.ucfutil import UcfUtil

# 標準高速化対応：ログインステータスチェック対応：template内で「escapejs」を使いたかったので追加 2016.12.20
cwd = os.path.dirname(__file__)
path = os.path.join(cwd, 'templates')
bcc = jinja2.MemcachedBytecodeCache(client=memcache.Client(), prefix='jinja2/bytecode/', timeout=None)
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path), auto_reload=False, bytecode_cache=bcc)
from ucf.utils import jinjacustomfilters
jinjacustomfilters.registCustomFilters(jinja_environment)

import Crypto.PublicKey.RSA as RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256


'''
oidccallback.py

@since: 2014-05-29
@version: 2017-06-14
@author: Akitoshi Abe
'''

""" 準備：
  ・Google Developer Consoleにて、[APIと認証]-[認証情報]画面で新しいクライアントID（ウェブアプリケーション）を作成する必要あり。その際の「承認済みリダイレクトURI」は、「http://...../startsession」のような値にする
  ・[APIと認証]-[同意画面]にて、ちゃんと同意画面を設定する必要あり
  ・作成したクライアントIDとクライアントシークレットを用いる

参考：

・Using OAuth2.0 for Login(OpenID Connect)
https://developers.google.com/accounts/docs/OAuth2Login

・Googleアカウントの認証をOpenIDからOpenID Connectに移行する方法
http://webos-goodies.jp/archives/how_to_migrate_from_openid_to_openid_connect.html

・（目標）ワンクリックSSO（プロンプト表示なしがOpenID Connectでも実現できる？）
https://developers.google.com/apps-marketplace/practices#5_use_one-click_single_sign-on

"""

TOKEN_EXCHANGE_API_TIMEOUT_SECONDS = 10

# get credentials with server-side retry
def getCredentials(state, code, with_admin_consent=False, num_retry=0):
	try:
		# トークン取得用の情報を生成
		client = WebApplicationClient(sateraito_inc.WEBAPP_CLIENT_ID)
		token_url, headers, body = client.prepare_token_request(
			'https://oauth2.googleapis.com/token',
			authorization_response=request.url,
			redirect_url=request.base_url,
			code=code,
		)

		# リクエスト(id_tokenの取得)
		token_response = requests.post(
			token_url,
			headers=headers,
			data=body,
			auth=(sateraito_inc.WEBAPP_CLIENT_ID, sateraito_inc.WEBAPP_CLIENT_SECRET),
			timeout=sateraito_inc.URLFETCH_TIMEOUT_SECOND
		)
		# logging.debug('===========token_response===========')
		# logging.debug(token_response.status_code)
		# logging.debug(token_response.content)
		dictTokenResponse = token_response.json()
		client.parse_request_body_response(json.dumps(dictTokenResponse))

		id_token = dictTokenResponse.get('id_token')
		expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=client.expires_in)
		# logging.debug(id_token)

		credentials = google.oauth2.credentials.Credentials(
			token_uri='https://oauth2.googleapis.com/token',
			client_id=sateraito_inc.WEBAPP_CLIENT_ID,
			client_secret=sateraito_inc.WEBAPP_CLIENT_SECRET,
			token=client.access_token,
			expiry=expiry,
			scopes=dictTokenResponse.get('scope', '').split(' '),
			id_token=id_token
		)
		return credentials

	# GAE Gen2対応
	# except DeadlineExceededError as e:
	except requests.exceptions.Timeout as e:
		logging.error('getCredentials: class name:' + e.__class__.__name__ + ' message=' +str(e) + ' num_retry=' + str(num_retry))
		if num_retry > 10:
			raise e
		else:
			return getCredentials(state, code, with_admin_consent,(num_retry + 1))
	except Exception as ex:
		logging.error('getCredentials: class name:' + ex.__class__.__name__ + ' message=' + str(ex) + ' num_retry=' + str(num_retry))
		if num_retry > 10:
			raise ex
		else:
			return getCredentials(state, code, with_admin_consent, (num_retry + 1))


class OIDCCallback(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	# def get(self):
	def doAction(self):
		logging.debug('**** requests *********************')
		logging.debug(self.request)

		# get param from callback url query parameter
		code = self.request.get('code')
		logging.info('code=' + str(code))
		state = self.request.get('state')
		logging.info('state=' + str(state))
		session_state = self.request.get('session_state')
		logging.info('session_state=' + str(session_state))
		error = self.request.get('error')
		logging.info('error=' + str(error))
		error_subtype = self.request.get('error_subtype')
		logging.info('error_subtype=' + str(error_subtype))
		# state = self.session.get('state')
		# logging.info('state=' + str(state))

		# state解析
		with_error_page = False
		# G Suite 版申込ページ対応…管理者チェックフラグと認証後にUserEntryを作成するオプション 2017.06.05
		with_admin_consent = False
		with_regist_user_entry = False

		hl = None
		tenant_or_domain = None  # iOS13サードパーティーCookieブロック対策 2019.09.26

		states = state.split('-')
		if len(states) >= 3 and states[1] != '':
			# GAEGEN2対応
			# info = UcfUtil.base64Decode(states[1])
			# info = UcfUtil.base64Decode(states[1]).decode('utf-8') --> やっぱりこれはしなくて良い？
			info = UcfUtil.base64Decode(states[1])
			logging.info('info=' + info)
			infos = info.split('&')
			for item in infos:
				ary = item.split('=')
				k = ary[0]
				v = ary[1] if len(ary) >= 2 else ''
				if k == 'wep' and v == '1':
					with_error_page = True
				# G Suite 版申込ページ対応 2017.06.05
				# 管理者かどうかのチェックフラグ
				if k == 'wac' and v == '1':
					with_admin_consent = True
				# 認証後にUserEntryを作成するフラグ
				if k == 'wrue' and v == '1':
					with_regist_user_entry = True
				if k == 'hl':
					hl = v
				# iOS13サードパーティーCookieブロック対策 2019.09.26
				if k == 't':
					tenant_or_domain = v

		# G Suite 版申込ページ対応…エラーページ対応 2017.06.05
		error_page_url = ''
		if with_error_page:
			# GAEGEN2対応	urllib.quote => urllib.parse.quote
			# error_page_url = self.request.cookies.get(urllib.quote(state + '-ep'))  # g2対応
			error_page_url = self.request.cookies.get(urllib.parse.quote(state + '-ep'))
			if error_page_url is None:
				error_page_url = ''
		logging.info('error_page_url=' + error_page_url)

		# check state
		state_from_session = self.session.get('state')
		if state_from_session is None or state_from_session == '':
			state_from_session = self.request.cookies.get('oidc_state')
		if str(state) != str(state_from_session):
			# state error

			# check 'multiple iframe gadget in a page' login case
			# GAEGEN2対応	urllib.unquote => urllib.parse.unquote, urllib.quote => urllib.parse.quote
			# url_to_go_from_cookie = self.request.cookies.get(urllib.quote(state))  # g2対応
			url_to_go_from_cookie = self.request.cookies.get(urllib.parse.quote(state))
			logging.info('url_to_go_from_cookie=' + str(url_to_go_from_cookie))
			if url_to_go_from_cookie is not None and str(url_to_go_from_cookie).strip() != '':
				if str(url_to_go_from_cookie).startswith(sateraito_inc.my_site_url):
					# this is 'multiple iframe gadget in a page' login case, session id is over-written, jump to url_to_go_from_cookie after wait
					logging.info('** jumping to:' + str(url_to_go_from_cookie))
					# 					self.response.out.write('<html><head>')
					# #					self.response.out.write('<meta http-equiv="refresh" content="1;URL=' + str(url_to_go_from_cookie) + '">')
					# 					# ここではoidcクエリー不要では？？ 2016.12.20
					# 					#url_to_go_from_cookie = UcfUtil.appendQueryString(url_to_go_from_cookie, 'oidc', 'cb')
					# 					self.response.out.write('<meta http-equiv="refresh" content="' + str(1 + random.randint(1, 5)) + ';URL=' + str(url_to_go_from_cookie) + '">')
					# 					self.response.out.write('</head><body></body></html>')
					# 					return
					return '<html><head>' \
						+ '<meta http-equiv="refresh" content="' + str(1 + random.randint(1, 5)) + ';URL=' + str(
							url_to_go_from_cookie) + '">' \
						+ '</head><body></body></html>'

			if with_error_page:
				logging.warning('state value not matched: state_from_session=' + str(state_from_session))
				my_lang = sateraito_func.MyLang(hl)
				# G Suite 版申込ページ対応…エラーページ対応 2017.06.05
				error_msg = my_lang.getMsg('INVALID_AUTH_OPENID_CONNECT')
				if error_page_url != '':
					self.session['error_msg'] = error_msg
					self.redirect(str(error_page_url))
					return

				# iOS13サードパーティーCookieブロック対策 2019.09.26
				if tenant_or_domain is not None and tenant_or_domain != '':
					google_apps_domain_from_gadget_url = tenant_or_domain
					token = UcfUtil.guid()
					# app_id = ''
					user_language = hl
					# popup = sateraito_func.getMySiteURL(tenant_or_domain, self.request.url) + '/' + google_apps_domain_from_gadget_url + '/openid/' + token + '/' + google_apps_domain_from_gadget_url + '/before_popup.html?hl=' + UcfUtil.urlEncode(hl)
					popup = sateraito_func.getMySiteURL(tenant_or_domain, self.request.url) + '/' + tenant_or_domain + '/popup3.html?hl=' + UcfUtil.urlEncode(hl)
					values = {
						'hl': hl,
						'user_lang': user_language,
						'extjs_locale_file': sateraito_func.getExtJsLocaleFileName(user_language),
						'google_apps_domain': tenant_or_domain,
						# 'app_id': app_id,
						'my_site_url': sateraito_func.getMySiteURL(tenant_or_domain, self.request.url),
						'my_site_url_for_static': sateraito_func.getMySiteURLForStaticContents(tenant_or_domain, self.request.url),
						# 静的コンテンツキャッシュ障害対応
						'version': sateraito_func.getScriptVersionQuery(),
						'vscripturl': sateraito_func.getScriptVirtualUrl(),
						'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
						'is_free_edition': sateraito_inc.IS_FREE_EDITION,
						'debug_mode': sateraito_inc.debug_mode,
						# 'hide_ad': hide_ad,
						# 'is_oauth2_domain':not sateraito_func.isNeedExchangeOauth2Mode(tenant_or_domain),
						'mode': '',
						'popup': popup,
					}

					template = jinja_environment.get_template('authentication.html')
					# start http body
					# self.response.out.write(template.render(values))
					# return
					return template.render(values)

				# self.response.out.write('<html><head>')
				# self.response.out.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
				# self.response.out.write('</head><body>')
				# self.response.out.write(error_msg)
				# self.response.out.write('</body></html>')
				return '<html><head>' \
					+ '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />' \
					+ '</head><body>' \
					+ error_msg \
					+ '</body></html>'
			else:
				logging.error('state value not matched: state_from_session=' + str(state_from_session))
				self.response.set_status(403)
			return

		# interaction_required を追加 2020.08.11
		# if error == 'immediate_failed' and error_subtype == 'access_denied':
		if error in ['immediate_failed', 'interaction_required'] and error_subtype == 'access_denied':
			logging.warning('error=%s&error_sub_type=%s' % (error, error_subtype))
			self.session['viewer_email'] = ''
			self.session['loggedin_timestamp'] = None  # G Suiteのマルチログイン時にiframe内でOIDC認証ができなくなったので強制で少しだけ高速化オプションする対応＆SameSite対応 2019.10.28
			self.session['is_oidc_loggedin'] = False
			self.session['is_oidc_need_show_signin_link'] = True
			# redirect to destination page
			redirect_url = self.session.get('url_to_go_after_oidc_login')
			if redirect_url is None or redirect_url == '':
				# GAEGEN2対応	urllib.quote => urllib.parse.quote
				# redirect_url = self.request.cookies.get(urllib.quote(state))  # g2対応
				redirect_url = self.request.cookies.get(urllib.parse.quote(state))
			if redirect_url is None or redirect_url == '':
				if with_error_page:
					my_lang = sateraito_func.MyLang(hl)
					# G Suite 版申込ページ対応…エラーページ対応 2017.06.05
					error_msg = my_lang.getMsg('FAILED_AUTH_OPENID_CONNECT_MULTIACCOUNT')
					if error_page_url != '':
						self.session['error_msg'] = error_msg
						self.redirect(str(error_page_url))
						return
					# self.response.out.write('<html><head>')
					# self.response.out.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
					# self.response.out.write('</head><body>')
					# self.response.out.write(error_msg)
					# self.response.out.write('</body></html>')
					return '<html><head>' \
						+ '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />' \
						+ '</head><body>' \
						+ error_msg \
						+ '</body></html>'
				else:
					self.response.set_status(403)
			else:

				# iOS13サードパーティーCookieブロック対策 2019.09.26
				if tenant_or_domain is not None and tenant_or_domain != '':
					google_apps_domain_from_gadget_url = tenant_or_domain
					token = UcfUtil.guid()
					# app_id = ''
					user_language = hl
					popup = sateraito_func.getMySiteURL(tenant_or_domain, self.request.url) + '/' + google_apps_domain_from_gadget_url + '/openid/' + token + '/' + google_apps_domain_from_gadget_url + '/before_popup.html?hl=' + UcfUtil.urlEncode(
						hl)
					values = {
						'hl': hl,
						'user_lang': user_language,
						'extjs_locale_file': sateraito_func.getExtJsLocaleFileName(user_language),
						'google_apps_domain': tenant_or_domain,
						# 'app_id': app_id,
						'my_site_url': sateraito_func.getMySiteURL(tenant_or_domain, self.request.url),
						'my_site_url_for_static': sateraito_func.getMySiteURLForStaticContents(tenant_or_domain, self.request.url),
						# 静的コンテンツキャッシュ障害対応
						'version': sateraito_func.getScriptVersionQuery(),
						'vscripturl': sateraito_func.getScriptVirtualUrl(),
						'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
						'is_free_edition': sateraito_inc.IS_FREE_EDITION,
						'debug_mode': sateraito_inc.debug_mode,
						# 'hide_ad': hide_ad,
						# 'is_oauth2_domain':not sateraito_func.isNeedExchangeOauth2Mode(tenant_or_domain),
						'mode': '',
						'popup': popup,
						'url_to_go_after_oidc_login': redirect_url,  # SameSite対応…標準高速化対応のついでに自動リロード対応を追加 2019.12.30
					}

					template = jinja_environment.get_template('authentication.html')
					# start http body
					# self.response.out.write(template.render(values))
					# return
					return template.render(values)

				# ページ内リンクを考慮するためUcfUtilを使用
				# if '?' in redirect_url:
				#	redirect_url += '&oidc=cb'
				# else:
				#	redirect_url += '?oidc=cb'
				redirect_url = UcfUtil.appendQueryString(redirect_url, 'oidc', 'cb')
				logging.info('redirect_url=' + redirect_url)
				# self.redirect(redirect_url)
				self.redirect(str(redirect_url))
			return

		# check error
		if error == 'access_denied':
			# user denied to access his info:
			if with_error_page:
				my_lang = sateraito_func.MyLang(hl)
				# G Suite 版申込ページ対応…エラーページ対応 2017.06.05
				error_msg = my_lang.getMsg('FAILED_AUTH_OPENID_CONNECT_ACCESS_DENIED')
				if error_page_url != '':
					self.session['error_msg'] = error_msg
					self.redirect(str(error_page_url))
					return
				# self.response.out.write('<html><head>')
				# self.response.out.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
				# self.response.out.write('</head><body>')
				# self.response.out.write(error_msg)
				# self.response.out.write('</body></html>')
				return '<html><head>' \
					+ '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />' \
					+ '</head><body>' \
					+ error_msg \
					+ '</body></html>'
			else:
				self.response.set_status(403)
			return

		# TODO id_tokenのverify…oauth2clientを使わないほうがやりやすそう 2016.12.20
		credentials = getCredentials(state, code)

		# get user email from id_token
		id_token = credentials.id_token
		logging.debug('id_token=' + str(id_token))

		# GAEGEN2対応	id_token は辞書形式に変換されていないので変換する
		lstItems = id_token.split('.')
		if (len(lstItems) == 3):
			id_token = json.loads(itsdangerous.encoding.base64_decode(lstItems[1]))

		viewer_email = str(id_token['email'])
		opensocial_viewer_id = id_token.get('sub', '')
		logging.info('viewer_email=' + str(viewer_email))
		logging.info('opensocial_viewer_id=' + str(opensocial_viewer_id))

		# G Suite 版申込ページ対応…管理者判定＆UserEntry作成 2017.06.05
		# 管理者判定
		if with_admin_consent:
			google_apps_domain = id_token.get('hd', '')
			logging.info('google_apps_domain=' + google_apps_domain)
			is_admin = False
			try:
				is_admin = sateraito_func.check_user_is_admin(google_apps_domain, viewer_email, do_not_use_impersonate_mail=True, credentials=credentials)
			except sateraito_func.ImpersonateMailException as e:
				logging.warning('class name:' + e.__class__.__name__ + ' message=' + str(e))
			if not is_admin:
				if with_error_page:
					my_lang = sateraito_func.MyLang(hl)
					# G Suite 版申込ページ対応…エラーページ対応 2017.06.05
					error_msg = my_lang.getMsg('FAILED_AUTH_BY_PRIVILEGE_ADMIN')
					if error_page_url != '':
						self.session['error_msg'] = error_msg
						self.redirect(str(error_page_url))
						return
					# self.response.out.write('<html><head>')
					# self.response.out.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
					# self.response.out.write('</head><body>')
					# self.response.out.write(error_msg)
					# self.response.out.write('</body></html>')
					return '<html><head>' \
						+ '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />' \
						+ '</head><body>' \
						+ error_msg \
						+ '</body></html>'
				else:
					self.response.set_status(403)
				return
			self.session['is_admin'] = is_admin

			# ユーザー情報登録（管理者判定ありき？）
			if with_regist_user_entry:
				sateraito_func.setNamespace(google_apps_domain, '')
				checker = sateraito_func.RequestChecker()
				row_u = checker.putNewUserEntry(
					viewer_email,
					google_apps_domain,
					sateraito_func.getDomainPart(viewer_email),
					opensocial_viewer_id,
					sateraito_func.OPENSOCIAL_CONTAINER_GOOGLE_SITE,
					'', is_admin)
				sateraito_func.setNamespace('', '')

		# turn on login flag in session
		# self.session['viewer_email'] = str(viewer_email).lower()
		self.session['viewer_email'] = str(viewer_email)
		# GAEGEN2対応
		# self.session['loggedin_timestamp'] = datetime.datetime.now()				# G Suiteのマルチログイン時にiframe内でOIDC認証ができなくなったので強制で少しだけ高速化オプションする対応＆SameSite対応 2019.10.28
		self.session['loggedin_timestamp'] = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')  # G Suiteのマルチログイン時にiframe内でOIDC認証ができなくなったので強制で少しだけ高速化オプションする対応＆SameSite対応 2019.10.28
		self.session['opensocial_viewer_id'] = str(opensocial_viewer_id)
		self.session['is_oidc_loggedin'] = True
		self.session['is_oidc_need_show_signin_link'] = False
		# redirect to destination page
		redirect_url = self.session.get('url_to_go_after_oidc_login')
		if redirect_url is None or redirect_url == '':
			# GAEGEN2対応	urllib.quote => urllib.parse.quote
			# redirect_url = self.request.cookies.get(urllib.quote(state))  # g2対応
			redirect_url = self.request.cookies.get(urllib.parse.quote(state))
		if redirect_url is None or redirect_url == '':
			pass
		# elif str(redirect_url).strip() == '':
		#	pass
		else:
			# ※OIDC認証時の高速化オプション廃止（デフォルトで高速化状態）後はこのパラメータ不要 2016.12.20
			if redirect_url.find('oidc=cb') < 0:  # 簡易的にクエリーがすでにあるかをチェック 2019.11.22
				redirect_url = UcfUtil.appendQueryString(redirect_url, 'oidc', 'cb')
			logging.info('redirect_url=' + redirect_url)
			# self.redirect(redirect_url)
			self.redirect(str(redirect_url))


class LoginMobile(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):

	def doAction(self, tenant_or_domain):
		logging.debug('google_apps_domain=' + str(tenant_or_domain))

		redirect_url = self.request.get('redirect')
		if redirect_url is None:
			# self.response.out.write('wrong request')
			self.response.set_status(403)
			# return
			return 'wrong request'
		else:
			self.session['redirect_uri_mobile'] = str(redirect_url)
		# check login
		# スマホ版はエラーを画面に出してもOKなので変更（TODO hlパラメータを渡したい） 2016.12.19
		# if not self.oidAutoLogin(tenant_or_domain):

		# モバイル版でログアウト直後のログイン時にG Suite側のアカウント選択画面を出すことで自動再ログインを防ぐ 2020.02.21
		# if not self.oidAutoLogin(tenant_or_domain, with_error_page=True, hl=self.request.get('hl')):
		with_select_account_prompt = self.getCookie('aoilout') == '1'
		logging.info('with_select_account_prompt=%s' % (with_select_account_prompt))
		is_ok, body_for_not_ok = self.oidAutoLogin(tenant_or_domain, with_error_page=True, with_select_account_prompt=with_select_account_prompt, hl=self.request.get('hl'))
		if not is_ok:
			return body_for_not_ok

		# queryのURLを優先 2017.03.06
		if redirect_url != '':
			logging.info('redirect to:%s' % (redirect_url))
			self.redirect(str(redirect_url))
		elif self.session['redirect_uri_mobile'] and str(self.session['redirect_uri_mobile']) != '':
			logging.info('redirect to:%s' % (self.session['redirect_uri_mobile']))
			self.redirect(self.session['redirect_uri_mobile'])
		else:
			logging.warning('session redirect_uri_mobile is empty.')
			logging.warning(self.session['redirect_uri_mobile'])

# 標準高速化対応：ガジェットが開いた後に現在のログインユーザーが正しいどうかをチェックするためのページ（iframeからコール） 2019.12.19
# ※Reports APIを使った自前実装方式で復活（ログイン、ログアウトはほかの端末、ブラウザのログインかもしれないがやむを得ないものとする）
class OidcCheckCurrentUser(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	# Reports APIで最後のログイン、ログアウト情報を取得
	def checkLastLogoutOfGSuite(self, tenant_or_domain, viewer_email):
		last_login_time_utc = None
		last_logout_time_utc = None
		try:
			admin_report_service = sateraito_func.get_admin_report_service(viewer_email, tenant_or_domain)
			# ログアウト情報
			report_entry = admin_report_service.activities().list(userKey=viewer_email, applicationName='login', eventName='logout', filters='login_type==google_password', maxResults=1).execute()
			logging.info(report_entry)
			if report_entry is not None and report_entry.get('items', None) is not None and len(report_entry.get('items', None)) > 0:
				last_logout_time_str = report_entry['items'][0].get('id', {}).get('time', '')
				if last_logout_time_str != '':
					last_logout_time_utc = datetime.datetime.strptime(last_logout_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
			# ログイン情報
			report_entry = admin_report_service.activities().list(userKey=viewer_email, applicationName='login', eventName='login_success', maxResults=1).execute()
			logging.info(report_entry)
			if report_entry is not None and report_entry.get('items', None) is not None and len(report_entry.get('items', None)) > 0:
				last_login_time_str = report_entry['items'][0].get('id', {}).get('time', '')
				if last_login_time_str != '':
					last_login_time_utc = datetime.datetime.strptime(last_login_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
		except BaseException as e:
			logging.exception(e)
		return last_login_time_utc, last_logout_time_utc

	# Reports APIを使用した自前実装版
	# OIDCじゃないのでここで直接Report APIをコールしてログアウトを判定
	def doAction(self, tenant_or_domain):

		is_need_logout = False
		popup = ''

		hl = self.request.get('hl')
		logging.info('hl=' + hl)

		# ※ワークフローではCookieのセッションID自体が破棄されないのでセッションからとってOK
		viewer_email = self.session.get('viewer_email', '')
		logging.info('viewer_email:%s' % (viewer_email))

		if viewer_email is not None and viewer_email != '':

			loggedin_timestamp = self.session.get('loggedin_timestamp')
			# GAEGEN2対応
			if isinstance(loggedin_timestamp, str):
				loggedin_timestamp = dateutil.parser.parse(loggedin_timestamp)

			logging.info('loggedin_timestamp=%s' % (loggedin_timestamp))

			# loggedin_timestamp = None
			# if loggedin_timestamp_str is not None and loggedin_timestamp_str != '':
			#	loggedin_timestamp = datetime.datetime.strptime(loggedin_timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ')

			last_login_datetime = None
			last_logout_datetime = None
			if loggedin_timestamp is not None:		# loggedin_timestamp がNoneの場合は取得しても仕方ないので（単に少しでもAPIコールを減らす目的）
				last_login_datetime, last_logout_datetime = self.checkLastLogoutOfGSuite(tenant_or_domain, viewer_email)
				logging.info('last_login_datetime=%s' % (last_login_datetime))
				logging.info('last_logout_datetime=%s' % (last_logout_datetime))

			# 最終アクセス日時より後にG Suite からログアウトされていたらアドオン側もログアウト
			# → G Suiteの最後のログインより古いログアウトは無視
			#if loggedin_timestamp is not None and last_logout_datetime is not None and loggedin_timestamp < last_logout_datetime:
			if loggedin_timestamp is not None and last_logout_datetime is not None and loggedin_timestamp < last_logout_datetime and (last_login_datetime is None or last_login_datetime < last_logout_datetime):
			#if True:

				# /logoutにリダイレクトしたくないのでここでセッション破棄
				self.session['viewer_email'] = ''
				self.session['opensocial_viewer_id'] = ''
				self.session['is_oidc_loggedin'] = False
				self.session['is_oidc_need_show_signin_link'] = False
				# clear openid connect session
				self.removeCookie(sateraito_page.OPENID_COOKIE_NAME)

				token = UcfUtil.guid()
				popup = sateraito_func.getMySiteURL(tenant_or_domain, self.request.url) + '/' + tenant_or_domain + '/openid/' + token + '/' + tenant_or_domain + '/before_popup.html?hl=' + UcfUtil.urlEncode(hl)

				is_need_logout = True
			## ログイン日時をセット（アクセスのたびに上書きするのではなくセッションに値がない場合（初回）のみセット）
			# elif loggedin_timestamp_str is None or loggedin_timestamp_str == '':
			#	new_loggedin_timestamp = UcfUtil.getNow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
			#	self.session['loggedin_timestamp'] = new_loggedin_timestamp
			#	logging.info('set loggedin_timestamp=%s' % (new_loggedin_timestamp))
			logging.info('is_need_logout=%s' % (is_need_logout))

		lang = hl
		lang_file = sateraito_func.getLangFileName(lang)

		values = {
			'lang': lang,
			'lang_file': lang_file,
			'extjs_locale_file': sateraito_func.getExtJsLocaleFileName(lang),
			'tenant_or_domain': tenant_or_domain,
			'my_site_url': sateraito_func.getMySiteURL(tenant_or_domain, self.request.url),
			'my_site_url_for_static': sateraito_func.getMySiteURLForStaticContents(tenant_or_domain, self.request.url),
			# 静的コンテンツキャッシュ障害対応
			'version': sateraito_func.getScriptVersionQuery(),
			'vscripturl': sateraito_func.getScriptVirtualUrl(),
			'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
			'is_check_ok': '1' if not is_need_logout else '0',
			'popup': popup,
		}
		template_filename = 'oidc_page_check_current_user.html'
		template = jinja_environment.get_template(template_filename)
		# self.response.out.write(template.render(values))
		return template.render(values)


def add_url_rules(app):
	app.add_url_rule('/oidccallback',
									 view_func=OIDCCallback.as_view('OIDCCallback'))

	app.add_url_rule('/<string:tenant_or_domain>/oidccheckcurrentuser',
									 view_func=OidcCheckCurrentUser.as_view('OidcCheckCurrentUser'))

