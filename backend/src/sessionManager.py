# coding: utf-8

import sateraito_logger as logging

# from gdata.service import CaptchaRequired

from google.appengine.api import memcache, urlfetch
from google.appengine.ext import ndb

# import gdata
import sateraito_func
import time
import datetime
import hashlib
import random
import json
import urllib
import smtplib

from ucf.utils.ucfutil import UcfUtil

import sateraito_inc

'''
sessionManager.py

@since 2013-12-13
@version 2013-12-03
'''

from json import JSONDecoder


def sha256(value):
	m = hashlib.sha256()
	m.update(value.encode())
	return m.hexdigest()


def createSessionId(email):
	return sha256(
		str(time.time()) + email + str(random.randint(10000000, 99999999)) + str(random.randint(10000000, 99999999)) + str(
			random.randint(10000000, 99999999)) + str(random.randint(10000000, 99999999)))


class TenantSession(ndb.Model):
	""" セッション情報
			key_name は session_id
	"""
	# created_date			 = ndb.DateTimeProperty(auto_now_add=True, indexed=False)
	updated_date = ndb.DateTimeProperty(auto_now=True)
	user_email = ndb.StringProperty()
	google_apps_domain = ndb.StringProperty()
	epoc = ndb.FloatProperty()
	auto_login = ndb.BooleanProperty()

	@classmethod
	def getBySid(cls, strSid):
		# logging.info('strSid=' + strSid)
		key = ndb.Key('TenantSession', strSid)
		row = key.get()
		# row = cls.get_by_id(strSid)
		# logging.info(row)
		return row

	def getSid(self):
		return self.key.string_id()

	def getAsJson(self):
		strSid = self.getSid()
		dictTmp = {
			'sid': strSid,
			'user_email': self.user_email,
			'epoc': self.epoc,
			'auto_login': self.auto_login
		}
		return sateraito_func.jsonEncodeToUtf8str(dictTmp)


def _smtpLoginApi(email, password):
	# SMTP 認証の場合

	SMTP_LOGIN_MD5_SUFFIX_KEY = 'ea65427e4c2142848cf3052517311b6b'
	SMTP_LOGIN_ENCRYPTION_KEY = '7d89b1f7'

	logging.info('SMTP Login')
	google_apps_domain = sateraito_func.getDomainPart(email)
	# create check key
	now = UcfUtil.getNow()  # 標準時
	ck = UcfUtil.md5(email + now.strftime('%Y%m%d%H%M') + SMTP_LOGIN_MD5_SUFFIX_KEY)
	logging.info('ck=' + str(ck))
	# create encrypted password
	password_bytes = None
	if isinstance(password, str):
		password_bytes = password.encode('utf-8')
	else:
		password_bytes = password

	# logging.info('password_bytes=' + str(password_bytes))
	encrypted_password = UcfUtil.enCrypto(password_bytes, SMTP_LOGIN_ENCRYPTION_KEY)
	logging.info('encrypted_password=' + str(encrypted_password))

	auth_request_url = 'https://api.sateraito.jp/api/google_auth.aspx'
	logging.info('auth_request_url=' + str(auth_request_url))
	# check user by sateraito sso server
	form_fields = {
		'uid': email,
		'pwd': encrypted_password,
		'ck': ck,
		'encrypto_mode': 'CBC',
	}
	form_data = urllib.parse.urlencode(form_fields)
	result = urlfetch.fetch(url=auth_request_url, method='post', payload=form_data, follow_redirects=True)

	if result.status_code != 200:
		logging.error('result.status_code=' + str(result.status_code))
		return False, None

	response_body = result.content
	logging.info('SMTP Login response_body=' + str(response_body))

	response = json.JSONDecoder().decode(response_body)
	if response['code'] == '0' and response['auth_result'] == 'SUCCESS':
		# ログインに成功した場合は、セッション情報の返却する。
		strSessionId = createSessionId(email)
		return True, strSessionId

	return False, None


def _smtpLoginDirect(email, auth_pwd):
	logging.info('SMTP Login Direct.')
	logging.info(email)

	boolResult = False
	strSessionId = None
	return True, createSessionId(email)

	try:
		s = smtplib.SMTP('smtp.gmail.com', 587)
		s.ehlo()
		s.starttls()
		s.ehlo()
		s.login(email, auth_pwd)
		s.close()

		boolResult = True

		# 認証成功
		strSessionId = createSessionId(email)

	except smtplib.SMTPAuthenticationError as e:
		# ID、パスワードが間違っている場合
		if e.smtp_code == 535:
			logging.warn('BAD_AUTHENTICATION:' + str(e))
			pass;

		elif e.smtp_code == 534:
			# GmailサービスがOFFの場合
			logging.warn('Gmail service may be off. :' + str(e))
			pass;

		else:
			logging.error('Unknown Error :' + str(e))

			logging.error(e)
			api_return_code = '0'  # 処理自体は成功
			api_return_message = e.smtp_error
			data = {
				'auth_result': 'FAILED',  # 認証は失敗
				'auth_error_code': 'FAILED_FAITAL_ERROR',
			}

	except BaseException as e:
		logging.error(type(e))
		logging.error(str(e))

	logging.info(str(boolResult) + ' / ' + str(strSessionId))

	return boolResult, strSessionId


def smtpLogin(email, password):
	if (True):
		return _smtpLoginDirect(email, password)
	else:
		return _smtpLoginApi(email, password)


# def clientLogin(email, password, captchaToken=None, capcthaResponse=None):
# 	'''
# 			Google　APIを使用するために必要な認証を行います。
#
# 			引数
# 					email:	ログイン用アカウント
# 					password: パスワード
# 					captchaTokn: キャプチャトークン
# 					capcthaResponse: キャプチャレスポンス
# 			戻り値
# 					セッション情報
# 	'''
# 	client = gdata.contacts.service.ContactsService()
# 	client.email = email
# 	client.password = password
# 	client.source = 'sateraito-apps-workflow'
# 	client.ProgrammaticLogin()
# 	try:
# 		client.ProgrammaticLogin(captchaToken, capcthaResponse)
# 	except CaptchaRequired:
# 		return False, client.captcha_token, client.captcha_url
#
# 	# ログインに成功した場合は、セッション情報の返却する。
# 	strSessionId = createSessionId(email)
#
# 	return True, strSessionId


SSO_LOGIN_MD5_SUFFIX_KEY = '0f6fc40dcecc462d9df170e7687b6e5b'
SSO_LOGIN_ENCRYPTION_KEY = 'a9507dca'


def ssoLogin(email, password, client_ip, client_user_agent, google_apps_domain, sso_endpoint=None):
	'''
			Google　APIを使用するために必要な認証を行います。

			引数
					email:	ログイン用アカウント
					password: パスワード
					client_ip: クライアントのIP
					client_user_agent: クライアントのUser-Agent
			戻り値
					セッション情報
	'''
	logging.info('ssoLogin')
	# google_apps_domain = sateraito_func.getDomainPart(email)
	# create check key
	now = UcfUtil.getNow()  # 標準時
	ck = UcfUtil.md5(email + now.strftime('%Y%m%d%H%M') + SSO_LOGIN_MD5_SUFFIX_KEY)
	logging.info('ck=' + str(ck))
	# create encrypted password
	password_bytes = None
	if isinstance(password, str):
		password_bytes = password.encode('utf-8')
	else:
		password_bytes = password
	# logging.info('password_bytes=' + str(password_bytes))
	encrypted_password = UcfUtil.enCrypto(password_bytes, SSO_LOGIN_ENCRYPTION_KEY)
	logging.info('encrypted_password=' + str(encrypted_password))
	# create request url
	# カスタム連携設定
	if sso_endpoint is not None and sso_endpoint in ['sateraito-apps-sso.appspot.com', 'sateraito-apps-sso3.appspot.com',
	                                                 'kddi-sso.appspot.com', 'sateraito-dev2.appspot.com']:
		auth_server = sso_endpoint
	# GAEアプリ単位で指定がある場合
	elif hasattr(sateraito_inc, 'SSO_SERVER'):
		auth_server = sateraito_inc.SSO_SERVER
	# 有償版
	elif sateraito_inc.appspot_domain == 'sateraito-apps-workflow':
		auth_server = 'sateraito-apps-sso.appspot.com'
	# 無償版
	elif sateraito_inc.appspot_domain == 'sateraito-apps-workflow2':
		auth_server = 'sateraito-apps-sso3.appspot.com'
	# KDDI版
	elif sateraito_inc.appspot_domain == 'kddi-workflow':
		auth_server = 'kddi-sso.appspot.com'
	# その他は一応有償版に
	else:
		auth_server = 'sateraito-apps-sso.appspot.com'

	auth_request_url = 'https://' + auth_server + '/a/' + google_apps_domain + '/api/checkauth2'
	logging.info('auth_request_url=' + str(auth_request_url))
	# check user by sateraito sso server
	form_fields = {
		'uid': email,
		'pwd': encrypted_password,
		'ck': ck,
		'encrypto_mode': 'CBC',
		'client_ip': client_ip,
	}
	form_data = urllib.parse.urlencode(form_fields)
	result = urlfetch.fetch(url=auth_request_url, method='post', payload=form_data, follow_redirects=True)
	if result.status_code != 200:
		logging.error('result.status_code=' + str(result.status_code))
		return False, None
	response_body = result.content
	logging.info('ssoLogin response_body=' + str(response_body))
	response = json.JSONDecoder().decode(response_body)
	if response['code'] == '0' and response['auth_result'] == 'SUCCESS':
		# ログインに成功した場合は、セッション情報の返却する。
		strSessionId = createSessionId(email)
		return True, strSessionId, response['user_id']
	return False, None, None


class SessionManager:
	@classmethod
	def removeSession(cls, strSid):
		memcache.delete(strSid)
		key = ndb.Key('TenantSession', strSid)
		try:
			key.delete()
		# cls.get_by_id(strSid).key().delete()
		except:
			logging.error('delete session failed: ' + str(strSid))

		logging.info('remove session: %s' % (strSid))

	@classmethod
	def setSession(cls, session):
		# セッション情報の保存
		sid = session.getSid()

		session.epoc = time.mktime(datetime.datetime.now().timetuple());

		session.put()
		logging.info('save session: %s' % (sid))

		strJson = session.getAsJson()
		memcache.set(sid, strJson)
		logging.info('cache session: %s' % (sid))

	@classmethod
	def checkAndGetSessionAsDict(cls, strSid, domainSetting, extendSession=False):
		if (not strSid):
			return None

		session = None
		dictSession = None
		boolExtendEpoc = False

		strJson = memcache.get(strSid)
		if (strJson):
			dictSession = JSONDecoder().decode(strJson)

			if (dictSession["auto_login"]):
				# timeOutSeconds = domainSetting["mobile_autologin_hours"] * 60 * 60
				timeOutSeconds = 24 * 60 * 60 * 365 * 50
			else:
				timeOutSeconds = domainSetting["mobile_session_minutes"] * 60

			epocNow = time.mktime(datetime.datetime.now().timetuple())

			logging.info('MemCache⇒ passing seconds = ' + str(epocNow - dictSession["epoc"]))

			if (epocNow - dictSession["epoc"] > timeOutSeconds):
				logging.error('Session Expired. ' + str(epocNow - dictSession["epoc"]) + '/' + str(timeOutSeconds));
				return None
			elif (epocNow - dictSession["epoc"] > 5 * 60):
				boolExtendEpoc = True

		else:
			session = TenantSession.getBySid(strSid)
			if (session):
				if (session.auto_login):
					# timeOutSeconds = domainSetting["mobile_autologin_hours"] * 60 * 60
					timeOutSeconds = 24 * 60 * 60 * 365 * 50
				else:
					timeOutSeconds = domainSetting["mobile_session_minutes"] * 60

				epocNow = time.mktime(datetime.datetime.now().timetuple())

				logging.info('DateSet ⇒ passing seconds = ' + str(epocNow - session.epoc))
				if (epocNow - session.epoc > timeOutSeconds):
					logging.error('Session Expired. ' + str(epocNow - session.epoc) + '/' + str(timeOutSeconds))
					session.key.delete()
					return None

				elif (epocNow - session.epoc >= 5 * 60):
					boolExtendEpoc = True

				dictSession = {
					'sid': session.key.string_id(),
					'user_email': session.user_email,
					'epoc': session.epoc,
					'auto_login': session.auto_login,
				}

		if (extendSession) and (boolExtendEpoc):
			logging.info('need update Session')
			memcache.delete(strSid)
			if (session is None):
				session = TenantSession.getBySid(strSid)

			if (session):
				logging.info('update Session')
				session.epoc = epocNow
				session.put()

				strJson = session.getAsJson()
				memcache.set(strSid, strJson)

		return dictSession
