#!/usr/bin/python
# coding: utf-8

__author__ = 'T.ASAO <asao@sateraito.co.jp>'

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
# GAEGEN2対応:SAML、SSO連携対応のついで
# import webapp2
from flask import Flask, Response, render_template, request, make_response, session, redirect
import random

# GAEGEN2対応:独自ロガー
# import logging
import sateraito_logger as logging

import json
import urllib
import base64
import datetime
import time
import random
from google.appengine.api import namespace_manager
from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api import urlfetch

import Crypto.PublicKey.RSA as RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.Util.asn1 import DerSequence

import sateraito_inc
import sateraito_func
import sateraito_page
import sateraito_db

from ucf.utils.ucfutil import UcfUtil

cwd = os.path.dirname(__file__)
path = os.path.join(cwd, 'templates')
bcc = jinja2.MemcachedBytecodeCache(client=memcache.Client(), prefix='jinja2/bytecode/', timeout=None)
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path), auto_reload=False, bytecode_cache=bcc)
from ucf.utils import jinjacustomfilters
jinjacustomfilters.registCustomFilters(jinja_environment)		# ログインステータスチェック対応：template内で「escapejs」を使いたかったので追加 2016.12.08


# バイト配列を整数型に変換 2016.12.07
def _unpack_bigint(b):
	# x = 0L  # g2対応
	x = 0
	for bi, bb in enumerate(b):
		x += (1 << (bi*8)) * ord(bb)
	return x

def _urlsafe_b64decode(b64string):
	# Guard against unicode strings, which base64 can't handle.
	# GAEGEN2対応:SAML、SSO連携対応
	#b64string = b64string.encode('ascii')
	padded = b64string + '=' * (4 - len(b64string) % 4)
	return base64.urlsafe_b64decode(padded)


class _OidcCallback(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	# X.509のTumbprintから公開鍵を取得（変わる可能性があるのでちゃんと取得）
	def _getSSitePublicKey(self, thumbprint):
		public_key = None
		exponent = None
		modulus = None
		if thumbprint is not None and thumbprint != '':
			memcache_key_public_key = 'oidc_public_key?thumbprint=' + thumbprint
			memcache_key_exponent = 'oidc_exponent?thumbprint=' + thumbprint
			memcache_key_modulus = 'oidc_modulus?thumbprint=' + thumbprint

			memcache_keys = [memcache_key_public_key, memcache_key_exponent, memcache_key_modulus]
			memcache_datas = memcache.get_multi(memcache_keys)
			public_key = memcache_datas.get(memcache_key_public_key)
			exponent = memcache_datas.get(memcache_key_exponent)			# AQAB（65537）
			modulus = memcache_datas.get(memcache_key_modulus)
			if public_key is not None and exponent is not None and modulus is not None:
				logging.info('retrieve public key from memcache.thumbprint=' + thumbprint)
				pass
			else:

				process_cnt = 0
				MAX_RETRY_CNT = 2
				while process_cnt <= MAX_RETRY_CNT:
					try:
						request_url = sateraito_inc.SSITE_ROOT_URL + '/common/discovery/keys'
						deadline = 5
						result = urlfetch.fetch(url=request_url, method=urlfetch.GET, follow_redirects=True, deadline=deadline)
						if result.status_code != 200:
							logging.error('result.status_code=' + str(result.status_code))
							# logging.error('result.content=' + str(result.content))  # g2対応
							logging.error('result.content=' + sateraito_func.bytesToStr(result.content))
						else:
							# keys_dict = json.JSONDecoder().decode(result.content)
							keys_dict = json.JSONDecoder().decode(sateraito_func.bytesToStr(result.content))
							keys = keys_dict.get('keys', [])
							for item in keys:
								if item.get('x5t', '') == thumbprint:
									public_key = item.get('x5c')[0]
									exponent = item.get('e')
									modulus = item.get('n')
									break
							break
					except BaseException as e:
						logging.exception(e)
						pass
					process_cnt += 1

				if public_key is not None and exponent is not None and modulus is not None:
					memcache_datas = {
						memcache_key_public_key:public_key,
						memcache_key_exponent:exponent,
						memcache_key_modulus:modulus,
					}
					if not memcache.set_multi(memcache_datas, time=3600 * 24):			# ２４時間間隔でチェックが推奨とのことなので
						logging.warning("Memcache set failed.")

		logging.info(public_key)
		logging.info(exponent)
		logging.info(modulus)
		return public_key, exponent, modulus

	# id_tokenの検証＆ペイロードJSONを取得 2016.12.08
	def analysisAndRetrieveIDToken(self, id_token):
		jwt_data = None
		# id_tokenをピリオドで分割して２個目の値をベース64デコードしてJSON型にセット
		id_token_sp = id_token.split('.')
		if not sateraito_inc.debug_mode:
			# デジタル署名を検証 2016.12.06
			'''
			～参考～
			□
			https://blogs.msdn.microsoft.com/tsmatsuz/2014/04/17/azure-ad-openid-connect/
			□
			https://blog.kazu69.net/2016/07/30/authenticate_with_json_web_token/
			□Azure AD のトークン リファレンス
			https://docs.microsoft.com/ja-jp/azure/active-directory/active-directory-token-and-claims
			□
			http://christina04.hatenablog.com/entry/2015/01/27/131259
			※Apps版で参考になりそう
			'''

			jwt_header_enc = id_token_sp[0]
			jwt_payload_enc = id_token_sp[1]
			jwt_sig_enc = id_token_sp[2]

			jwt_header_dec = _urlsafe_b64decode(jwt_header_enc)
			logging.debug('jwt_header=' + jwt_header_dec)
			jwt_header = json.loads(jwt_header_dec)
			jwt_payload_dec = _urlsafe_b64decode(jwt_payload_enc)
			logging.debug('jwt_payload_dec=' + jwt_payload_dec)
			logging.debug('jwt_signature=' + jwt_sig_enc)
			jwt_sig = _urlsafe_b64decode(jwt_sig_enc)

			# 公開鍵を取得
			thumbprint = jwt_header.get('x5t', '')
			if thumbprint is None or thumbprint == '':
				logging.error('invalid_thumbprint')
				return None
			public_key, exponent, modulus = self._getSSitePublicKey(thumbprint)
			if public_key is None or exponent is None or modulus is None:
				logging.error('failed retrieve public key. thumbprint=' + thumbprint)
				return None


			# 小塚さんに公開鍵の作成方法を調べていただいたので再度変更 2017.01.13
			# ネタ元:https://cloud.google.com/appengine/docs/python/appidentity/
			## ※ RSA.importKey(public_key) だとどう加工してもうまくいかないのでmodulusとexponentから公開鍵を作成
			## RSA.importKey(public_key)
			#modulus_dec = _unpack_bigint(_urlsafe_b64decode(modulus))
			#exponent_dec = _unpack_bigint(_urlsafe_b64decode(exponent))
			#logging.debug(modulus_dec)
			#logging.debug(exponent_dec)
			#rsa_pub_key = RSA.construct((modulus_dec, exponent_dec))
			cert_der = base64.urlsafe_b64decode(str(public_key))
			cert_seq = DerSequence()
			cert_seq.decode(cert_der)
			tbs_seq = DerSequence()
			tbs_seq.decode(cert_seq[0])
			rsa_pub_key = RSA.importKey(tbs_seq[6])

			signer = PKCS1_v1_5.new(rsa_pub_key)
			digest = SHA256.new()
			# RFC https://tools.ietf.org/html/rfc7515#appendix-A.2 によるとbase64しないのが正解のようなので変更 2017.04.28
			#digest.update(base64.b64encode(str(jwt_header_enc + '.' + jwt_payload_enc)))
			digest.update(str(jwt_header_enc + '.' + jwt_payload_enc))
			if signer.verify(digest, jwt_sig):
				logging.error('failed verify rsa digest.')
				return None
			else:
				logging.info('verifing signature succeed!')
				pass

		# id_tokenの解析＆データ取得
		# 3.1.3.7.  ID Token Validation（http://openid-foundation-japan.github.io/openid-connect-core-1_0.ja.html#IDTokenValidation）

		id_token_enc = id_token_sp[1]
		id_token_dec = _urlsafe_b64decode(id_token_enc)
		logging.debug('id_token_dec=' + str(id_token_dec))
		jwt_data = json.loads(id_token_dec)
		logging.debug("--------------   JWT payload Base64 Decode --------------")
		for jkey in jwt_data:
			logging.debug(jkey + " : " + str(jwt_data[jkey]) + "")

		return jwt_data


class OidcCallback(_OidcCallback):

	# def doAction(self):
	# 	self._process()

	# response_mode=form_postの場合postでくるので 2016.12.08
	def doAction(self):
		return self._process()

	def _process(self):

		logging.debug('**** requests *********************')
		# GAEGEN2対応:SAML、SSO連携対応のついで
		#logging.debug(self.request)
		logging.debug(request.headers)
		logging.debug(request.get_data())

		code = self.request.get('code')
		state = self.request.get('state')
		session_state = self.request.get('session_state')
		error = self.request.get('error')
		error_description = self.request.get('error_description')
		id_token = self.request.get('id_token')

		logging.info('code=' + str(code))
		logging.info('state=' + str(state))
		logging.info('session_state=' + str(session_state))
		logging.info('error=' + str(error))
		logging.info('error_description=' + str(error_description))
		logging.info('id_token=' + str(id_token))

		# ※サードパーティーCookie無効時などにメッセージを表示するための言語などを「state」に含めてセット（Apps版と同じ方式）
		# state解析
		with_error_page = False
		hl = None
		states = state.split('-')
		if len(states) >= 3 and states[1] != '':
			info = UcfUtil.base64Decode(states[1])
			logging.info('info=' + info)
			infos = info.split('&')
			for item in infos:
				ary = item.split('=')
				k = ary[0]
				v = ary[1] if len(ary) >= 2 else ''
				if k == 'wep' and v == '1':
					with_error_page = True
				if k == 'hl':
					hl = v
		logging.info('with_error_page=' + str(with_error_page))
		logging.info('hl=' + str(hl))

		# check error
		if error is not None and error != '':
			if with_error_page:
				my_lang = sateraito_func.MyLang(hl)
				ret_datas = []
				ret_datas.append('<html><head>')
				ret_datas.append('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
				ret_datas.append('</head><body>')
				if error == 'login_required':
					ret_datas.append(my_lang.getMsg('INVALID_AUTH_OPENID_CONNECT_LOGIN_REQUIRED'))
				else:
					ret_datas.append(my_lang.getMsg('INVALID_AUTH_OPENID_CONNECT') + error)
				ret_datas.append('</body></html>')
				return ''.join(ret_datas)
			else:
				self.response.set_status(403)
				return
			return

		else:
			# １ページ複数ガジェット対応
			# check state
			state_from_cookie = self.request.cookies.get('oidc_state', None)
			if state_from_cookie is None or str(state_from_cookie) != str(state):

				# url_to_go_from_cookie = self.request.cookies.get(urllib.quote(state))  # g2対応
				url_to_go_from_cookie = self.request.cookies.get(urllib.parse.quote(state))
				logging.info('url_to_go_from_cookie=' + str(url_to_go_from_cookie))
				if url_to_go_from_cookie is not None and str(url_to_go_from_cookie).strip() != '':
					if str(url_to_go_from_cookie).startswith(sateraito_inc.custom_domain_my_site_url):
						# this is 'multiple iframe gadget in a page' login case, session id is over-written, jump to url_to_go_from_cookie after wait
						logging.info('** jumping to:' + str(url_to_go_from_cookie))
						ret_datas = []
						ret_datas.append('<html><head>')
						ret_datas.append('<meta http-equiv="refresh" content="' + str(1 + random.randint(1, 5)) + ';URL=' + str(url_to_go_from_cookie) + '">')
						ret_datas.append('</head><body></body></html>')
						return ''.join(ret_datas)
				if with_error_page:
					my_lang = sateraito_func.MyLang(hl)
					ret_datas = []
					ret_datas.append('<html><head>')
					ret_datas.append('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
					ret_datas.append('</head><body>')
					ret_datas.append(my_lang.getMsg('INVALID_AUTH_OPENID_CONNECT_LOGIN_REQUIRED'))
					ret_datas.append('</body></html>')
					return ''.join(ret_datas)
				else:
					self.response.set_status(403)
					return
				return

		# id_tokenの検証＆情報取得
		jwt_data = self.analysisAndRetrieveIDToken(id_token)

		if jwt_data is None:
			logging.error('failed verify id_token.')
			self.response.set_status(403)
			return

		# client_idのチェック 2016.12.06
		aud = jwt_data.get('aud')
		if aud != sateraito_inc.SSITE_OIDC_CLIENT_ID:
			logging.error('invalid aud.')
			self.response.set_status(403)
			return

		# 有効期間の検証 2016.12.06
		nbf = jwt_data.get('nbf')
		exp = jwt_data.get('exp')
		if sateraito_func.epochTodatetime(nbf) > datetime.datetime.now():
			logging.error('invalid nbf.')
			self.response.set_status(403)
			return
		if sateraito_func.epochTodatetime(exp) < datetime.datetime.now():
			logging.error('invalid exp.')
			self.response.set_status(403)
			return

		# nonceのチェック 2016.12.08
		nonce = jwt_data.get('nonce')
		logging.info('nonce=' + str(nonce))
		session_nonce = self.session.get('nonce-' + state)
		logging.info('session_nonce=' + str(session_nonce))
		if nonce != session_nonce:
			# sessionへの反映のタイムラグで取得できないことが多いので不本意ながら当面warningにしておく...
			#logging.error('failed verify nonce.')
			#self.response.set_status(403)
			#return
			logging.warning('failed verify nonce.')
			pass
		else:
			self.session['nonce-' + state] = ''

		# id_tokenペイロードから情報を取得
		# family_name = jwt_data.get('family_name')
		# given_name = jwt_data.get('given_name')

		# user_object_id = jwt_data.get('oid')
		# user_email = jwt_data.get('unique_name')
		user_object_id = jwt_data.get('sub')
		logging.info('user_object_id=' + str(user_object_id))
		user_email = jwt_data.get('upn')
		logging.info('user_email=' + str(user_email))
		opensocial_container = jwt_data.get('iss')
		logging.info('opensocial_container=' + str(opensocial_container))
		# is_admin
		is_ssite_admin = jwt_data.get('is_admin', False)
		logging.info('is_ssite_admin=' + str(is_ssite_admin))
		# tenant_or_domain
		tenant_or_domain = jwt_data.get('client_tenant', '')
		logging.info('tenant_or_domain=' + str(tenant_or_domain))

		tenant_or_domain = tenant_or_domain.lower()

		# set namespace
		namespace_manager.set_namespace(tenant_or_domain)

		# UserEntryのレコード登録、更新、セッションにログインユーザー情報のセットなどしかるべき処理を行い、その後、リダイレクト
		sp_user_email = user_email.split('@')
		target_domain = ''
		if len(sp_user_email) >= 2:
			target_domain = sp_user_email[1].lower()
		logging.info('target_domain=' + target_domain)

		rc = sateraito_func.RequestChecker()
		user_token = rc.registOrUpdateUserEntry(tenant_or_domain, user_email, target_domain, user_object_id, opensocial_container, user_object_id, is_ssite_admin)
		#if user_token is not None and user_token != '':
		#	self.setTokenToCookie(user_token)	# token…Cookie上書き

		self.session['viewer_email'] = str(user_email)
		#self.session['user_object_id'] = str(user_object_id)
		self.session['opensocial_viewer_id'] = str(user_object_id)
		self.session['is_oidc_loggedin'] = True
		self.session['is_oidc_need_show_signin_link'] = False

		# redirect_url = self.request.cookies.get(urllib.quote(state), None)  # g2対応
		redirect_url = self.request.cookies.get(urllib.parse.quote(state), None)
		if redirect_url is not None and str(redirect_url) != '':
			logging.info('redirect_url=' + str(redirect_url))
			self.redirect(str(redirect_url))
		else:
			logging.warning('No redirect url found')


# ログインステータスチェック対応…RP側のiframe 2016.12.08
# ※現在は未実装＆未使用...
class OidcCheckSessionState(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self, tenant_or_domain):
		hl = self.request.get('hl')
		logging.info('hl=' + hl)
		#session_state = self.session.get('session_state')
		session_state = self.request.get('session_state')
		logging.info('session_state=' + str(session_state))
		user_language = hl
		lang_file = sateraito_func.getLangFileName(user_language)
		values = {
			'hl': hl,
			'user_lang': user_language,
			# 'user_lang': sateraito_func.normalizationLangCode(user_language),
			'lang_file': lang_file,
			'extjs_locale_file': sateraito_func.getExtJsLocaleFileName(user_language),
			'tenant_or_domain': tenant_or_domain,
			'my_site_url': sateraito_func.getMySiteURL(tenant_or_domain, self.request.url),
			'my_site_url_for_static': sateraito_func.getMySiteURLForStaticContents(tenant_or_domain, self.request.url),		# 静的コンテンツキャッシュ障害対応
			'version': sateraito_func.getScriptVersionQuery(),
			'vscripturl': sateraito_func.getScriptVirtualUrl(),
			'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
			'session_state':session_state,
			'client_id':sateraito_inc.SSITE_OIDC_CLIENT_ID,
		}
		template_filename = 'oidc_page_check_session_state.html'
		template = jinja_environment.get_template(template_filename)
		# self.response.out.write(template.render(values))
		return template.render(values)


# 高速化オプション有効化でガジェットが開いた後に現在のログインユーザーが正しいどうかをチェックするためのページ（iframeからコール） 2016.12.08
# ※現在は未実装＆未使用...
class OidcCheckCurrentUser(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def _createOIDCAuthorizeUrl(self, tenant_or_domain, state, url_to_go_after_oidc_login):

		query_params = {}
		query_params['state'] = state
		query_params['response_type'] = 'id_token'
		query_params['response_mode'] = 'form_post'
		nonce = UcfUtil.guid()
		self.session['nonce-' + state] = nonce
		query_params['nonce'] = nonce
		query_params['client_id'] = sateraito_inc.SSITE_OIDC_CLIENT_ID
		query_params['redirect_uri'] = sateraito_func.getMySiteURL(tenant_or_domain, self.request.url) + '/ssite/oidccallback4check'
		query_params['scope'] = 'openid'
		query_params['prompt'] = 'none'
		query_params['client_tenant'] = tenant_or_domain		# SSITE独自クレーム. クライアント（アドオン）側のドメインをセット
		tenant_id = sateraito_db.GoogleAppsDomainEntry.getSSiteTenantID(tenant_or_domain)		# SSITEのテナントID
		# url_to_go = sateraito_inc.SSITE_ROOT_URL + '/' + tenant_id + '/oauth2/authorize?' + urllib.urlencode(query_params)
		url_to_go = sateraito_inc.SSITE_ROOT_URL + '/' + tenant_id + '/oauth2/authorize?' + urllib.parse.urlencode(query_params)

		auth_uri = str(url_to_go)
		logging.info('auth_uri=' + str(auth_uri))

		return auth_uri

	def doAction(self, tenant_or_domain):

		hl = self.request.get('hl')
		logging.info('hl=' + hl)
		session_state = self.request.get('session_state')
		logging.info('session_state=' + session_state)
		is_check_ok = self.request.get('is_check_ok')
		logging.info('is_check_ok=' + is_check_ok)

		if self.request.get('oidc') == 'cb':

			user_language = hl
			lang_file = sateraito_func.getLangFileName(user_language)
			values = {
				'hl': hl,
				'user_lang': user_language,
				# 'user_lang': sateraito_func.normalizationLangCode(user_language),
				'lang_file': lang_file,
				'extjs_locale_file': sateraito_func.getExtJsLocaleFileName(user_language),
				'tenant_or_domain': tenant_or_domain,
				'my_site_url': sateraito_func.getMySiteURL(tenant_or_domain, self.request.url),
				'my_site_url_for_static': sateraito_func.getMySiteURLForStaticContents(tenant_or_domain, self.request.url),		# 静的コンテンツキャッシュ障害対応
				'version': sateraito_func.getScriptVersionQuery(),
				'vscripturl': sateraito_func.getScriptVirtualUrl(),
				'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
				'is_check_ok':is_check_ok,
				'session_state':session_state,
			}
			template_filename = 'oidc_page_check_current_user.html'
			template = jinja_environment.get_template(template_filename)
			# self.response.out.write(template.render(values))
			return template.render(values)

		state = 'state-' + sateraito_func.dateString() + sateraito_func.randomString()
		logging.info('state=' + state)
		self.session['state'] = state

		# 認証後にもどってくる用URL
		url_to_go_after_oidc_login = self.request.url

		# for 'multiple iframe gadget in a page' case login
		#self.setCookie(urllib.quote(state), str(url_to_go_after_oidc_login), living_sec=30)
		# set cookie
		expires = UcfUtil.add_hours(UcfUtil.getNow(), 1).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
		self.setCookie('oidc_state', str(state), expires=expires)
		# 30秒とかだとうまくいかないので. 2017.06.29
		#self.setCookie(urllib.quote(state), str(url_to_go_after_oidc_login), living_sec=30)
		#self.setCookie(urllib.quote(state), str(url_to_go_after_oidc_login), living_sec=60)
		#self.setCookie(urllib.quote(state), str(url_to_go_after_oidc_login), expires=expires)  # g2対応
		self.setCookie(urllib.parse.quote(state), str(url_to_go_after_oidc_login), expires=expires)

		# Oauth認証用URLを作成
		auth_uri = self._createOIDCAuthorizeUrl(state, tenant_or_domain, url_to_go_after_oidc_login)
		self.redirect(auth_uri)


# ログインユーザーチェック用のCallBack処理
# ※現在は未実装＆未使用...
class OidcCallbackForCheckCurrentUser(_OidcCallback):

	# def doAction(self):
	# 	self._process()

	# response_mode=form_postの場合postでくるので 2016.12.08
	def doAction(self):
		return self._process()

	def _process(self):

		logging.debug('**** requests *********************')
		# GAEGEN2対応：SAML、SSO連携対応のついで
		#logging.debug(self.request)
		logging.debug(request.headers)
		logging.debug(request.get_data())

		code = self.request.get('code')
		state = self.request.get('state')
		session_state = self.request.get('session_state')
		error = self.request.get('error')
		error_description = self.request.get('error_description')
		id_token = self.request.get('id_token')

		logging.info('code=' + str(code))
		logging.info('state=' + str(state))
		logging.info('session_state=' + str(session_state))
		logging.info('error=' + str(error))
		logging.info('error_description=' + str(error_description))
		logging.info('id_token=' + str(id_token))

		is_check_ok = False
		is_error = False

		if error is not None and error != '':
			is_error = True

		if not is_error:
			# １ページ複数ガジェット対応
			state_from_cookie = self.request.cookies.get('oidc_state', None)
			if state_from_cookie is None or str(state_from_cookie) != str(state):
				# url_to_go_from_cookie = self.request.cookies.get(urllib.quote(state))  # g2対応
				url_to_go_from_cookie = self.request.cookies.get(urllib.parse.quote(state))
				logging.info('url_to_go_from_cookie=' + str(url_to_go_from_cookie))
				if url_to_go_from_cookie is not None and str(url_to_go_from_cookie).strip() != '':
					if str(url_to_go_from_cookie).startswith(sateraito_inc.custom_domain_my_site_url):
						# this is 'multiple iframe gadget in a page' login case, session id is over-written, jump to url_to_go_from_cookie after wait
						logging.info('** jumping to:' + str(url_to_go_from_cookie))
						ret_datas = []
						ret_datas.append('<html><head>')
						ret_datas.append('<meta http-equiv="refresh" content="' + str(1 + random.randint(1, 5)) + ';URL=' + str(url_to_go_from_cookie) + '">')
						ret_datas.append('</head><body></body></html>')
						return ''.join(ret_datas)
				is_error = True

		# id_tokenの検証＆情報取得 2016.12.08
		jwt_data = None
		if not is_error:
			jwt_data = self.analysisAndRetrieveIDToken(id_token)
			if jwt_data is None:
				logging.error('failed verify id_token.')
				is_error = True
				return

			# client_idのチェック 2016.12.06
			aud = jwt_data.get('aud')
			if aud != sateraito_inc.SSITE_OIDC_CLIENT_ID:
				logging.error('invalid aud.')
				is_error = True
			# 有効期間の検証 2016.12.06
			nbf = jwt_data.get('nbf')
			exp = jwt_data.get('exp')
			if sateraito_func.epochTodatetime(nbf) > datetime.datetime.now():
				logging.error('invalid nbf.')
				is_error = True
			if sateraito_func.epochTodatetime(exp) < datetime.datetime.now():
				logging.error('invalid exp.')
				is_error = True
			# nonceのチェック 2016.12.08
			nonce = jwt_data.get('nonce')
			logging.info('nonce=' + str(nonce))
			session_nonce = self.session.get('nonce-' + state)
			#if session_nonce is None:
			#	# take time for ndb cache issue
			#	time.sleep(1)
			#	session_nonce = self.session.get('nonce-' + state)
			logging.info('session_nonce=' + str(session_nonce))
			if nonce != session_nonce:
				# sessionへの反映のタイムラグで取得できないことが多いので不本意ながら当面warningにしておく...
				#logging.error('failed verify nonce.')
				#is_error = True
				logging.warning('failed verify nonce.')
				pass
			else:
				self.session['nonce-' + state] = ''


		if not is_error:
			user_email = jwt_data.get('unique_name')
			logging.info('user_email=' + str(user_email))
			is_check_ok = user_email.lower() == self.session.get('viewer_email', '').lower()

		logging.info('is_error=' + str(is_error))
		logging.info('is_check_ok=' + str(is_check_ok))

		# redirect_url = self.request.cookies.get(urllib.quote(state), None)  # g2対応
		redirect_url = self.request.cookies.get(urllib.parse.quote(state), None)
		if redirect_url is not None and str(redirect_url) != '':
			redirect_url = UcfUtil.appendQueryString(redirect_url, 'oidc', 'cb')			# これは必要（is_check_okで判断してもいいけど）...
			redirect_url = UcfUtil.appendQueryString(redirect_url, 'session_state', session_state)
			redirect_url = UcfUtil.appendQueryString(redirect_url, 'is_check_ok', '1' if is_check_ok else '0')
			logging.info('redirect_url=' + str(redirect_url))
			self.redirect(str(redirect_url))
		else:
			logging.warning('No redirect url found')


# app = ndb.toplevel(webapp2.WSGIApplication([
# 	(r'/ssite/oidccallback', OidcCallback),
# 	(r'/([^/]*)/ssite/oidcchecksessionstate', OidcCheckSessionState),			# ログインステータスチェック対応
# 	(r'/([^/]*)/ssite/oidccheckcurrentuser', OidcCheckCurrentUser),			# ログインステータスチェック対応
# 	(r'/ssite/oidccallback4check', OidcCallbackForCheckCurrentUser),			# ログインステータスチェック対応
# ], debug=sateraito_inc.debug_mode, config=sateraito_page.config))

def add_url_rules(app):
	app.add_url_rule('/ssite/oidccallback', view_func=OidcCallback.as_view('OidcCallback4SSite_SsiteOidcCallback'))
	app.add_url_rule('/<tenant_or_domain>/ssite/oidcchecksessionstate', view_func=OidcCheckSessionState.as_view('OidcCallback4SSite_SsiteOidcCheckSessionState'))			# ログインステータスチェック対応
	app.add_url_rule('/<tenant_or_domain>/ssite/oidccheckcurrentuser', view_func=OidcCheckCurrentUser.as_view('OidcCallback4SSite_SsiteOidcCheckCurrentUser'))			# ログインステータスチェック対応
	app.add_url_rule('/ssite/oidccallback4check', view_func=OidcCallbackForCheckCurrentUser.as_view('OidcCallback4SSite_SsiteOidcCallbackForCheckCurrentUser'))			# ログインステータスチェック対応

