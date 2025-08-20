#!/usr/bin/python
# coding: utf-8

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'
from flask import render_template, request, make_response
import sateraito_logger as logging
from google.appengine.api import namespace_manager

import sateraito_inc
import sateraito_page
import sateraito_func
import sateraito_db

# from oauth2client.client import AccessTokenRefreshError # todo: edited start: tan@vn.sateraito.co.jp (version: 2)
# from apiclient.errors import HttpError  # todo: edited start: tan@vn.sateraito.co.jp (version: 2)


'''
introducing.py

@since: 2011-07-11
@version: 2013-06-01
@author: akitoshi_abe
'''

class MainHandler(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):

	def doAction(self, google_apps_domain):
		# set namespace
		hl = self.request.get('hl', None)
		#		if hl is None or hl == '':
		#			hl = sateraito_inc.DEFAULT_LANGUAGE
		#		else:
		#			hl = sateraito_func.getActiveLanguage(hl, hl=sateraito_inc.ENGLISH_LANGUAGE)

		namespace_manager.set_namespace(google_apps_domain)
		# check login
		# if not self.oidAutoLogin(google_apps_domain): #old
		# if not self.oidAutoLoginOAuth1(google_apps_domain):
		logging.debug('============_OIDCAutoLogin==============')
		is_ok, body_for_not_ok = self._OIDCAutoLogin(google_apps_domain)
		if not is_ok:
			return body_for_not_ok
		# loginCheck = self._OIDCAutoLogin(google_apps_domain)
		# logging.debug(loginCheck)
		# if not loginCheck.get('status'):
		# 	# not logged in: login and go to v2 MainPage
		# 	if loginCheck.get('response'):
		# 		return loginCheck.get('response')
		# 	return

			# check google_apps_domain and user_email
		user_email_splited = str(self.viewer_email).split('@')
		if user_email_splited[1] != google_apps_domain:
			logging.error('google apps domain and login user domain unmatched')
			return make_response('unmatched google apps domain and login user',200)
		my_site_url_splited = str(sateraito_inc.my_site_url).split('/')
		site_url_no_ssl = 'http://' + my_site_url_splited[2]
		is_admin = False
		is_warning_invalid_impersonate_mail = False
		logging.debug('============check_user_is_admin==============')
		try:
			is_admin = sateraito_func.check_user_is_admin(google_apps_domain, self.viewer_email)
		except sateraito_func.ImpersonateMailException as e:
			is_admin = sateraito_func.check_user_is_admin(google_apps_domain, self.viewer_email, do_not_use_impersonate_mail=True)
			is_warning_invalid_impersonate_mail = True

		# todo: edited start: tan@vn.sateraito.co.jp (version 2)
		# カレンダーAPIを使用して言語を取得
		logging.debug('============getLanguageUsing==============')
		logging.info('viewer_email="%s"' % self.viewer_email)
		logging.info('google_apps_domain="%s"' % google_apps_domain)
		user_language = sateraito_func.getLanguageUsing(hl, self.viewer_email, google_apps_domain)
		user_language = sateraito_func.getActiveLanguage(user_language, hl=sateraito_inc.DEFAULT_LANGUAGE)
		logging.info('user_language=' + user_language)

		my_lang = sateraito_func.MyLang(user_language)
		lang = my_lang.getMsgs()

		gadget_list = {}
		for hl in sateraito_func.ACTIVE_LANGUAGES:
			gadget_list[hl] = my_lang.getMsg(sateraito_func.LANGUAGES_MSGID.get(hl, ''))

		# todo: edited end

		# SSITE、SSOGadget対応：Apps版もついでに営業メンバーにメールを送信するように対応 2017.01.31
		domain_entry = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain)
		if domain_entry is None:
			# GWS版契約管理対応：有償版アドオンにもトライアル期限をセット（将来申し込みページ対応をする際には contract.pyの方も対応予定） 2022.05.30
			is_set_dates = True
			if sateraito_inc.IS_FREE_EDITION:
				# 無償版にはトライアル期限はセットしない 2022.09.28
				is_set_dates = False
			domain_entry = sateraito_func.registDomainEntry(google_apps_domain, google_apps_domain, self.viewer_email, contract_entry=None, is_set_dates=is_set_dates)

		# impersonate_emailが空なら本管理者を自動セット（自動セットフラグも立てる）
		if is_admin and (domain_entry.impersonate_email is None or domain_entry.impersonate_email == ''):
			domain_entry = sateraito_func.setImpersonateEmail(google_apps_domain, self.viewer_email, True, domain_entry=domain_entry)
		is_auto_create_impersonate_email = False
		impersonate_email = ''
		if domain_entry is not None:
			impersonate_email = domain_entry.impersonate_email if domain_entry.impersonate_email is not None else ''
			is_auto_create_impersonate_email = domain_entry.is_auto_create_impersonate_email if domain_entry.is_auto_create_impersonate_email is not None else False

		logging.info('is_admin:' + str(is_admin))
		logging.info('is_warning_invalid_impersonate_mail:' + str(is_warning_invalid_impersonate_mail))
		logging.info('is_auto_create_impersonate_email:' + str(is_auto_create_impersonate_email))
		values = {
			'user_email': self.viewer_email,
			'google_apps_domain': google_apps_domain,
			'site_url': sateraito_inc.my_site_url,
			'site_url_no_ssl': site_url_no_ssl,
			'is_admin': is_admin,
			'vscripturl': sateraito_func.getScriptVirtualUrl(),
			'impersonate_email': impersonate_email,
			'is_warning_invalid_impersonate_mail': is_warning_invalid_impersonate_mail,
			'is_auto_create_impersonate_email': is_auto_create_impersonate_email,
			'gadget_list': gadget_list,
			'locale': user_language,
			'extjs_locale_file': sateraito_func.getExtJsLocaleFileName(user_language),
			'default_lang': sateraito_inc.DEFAULT_LANGUAGE,
			'lang': lang
		}
		# start http body
		return render_template('introducing.html', **values)


def add_url_rules(app):
	app.add_url_rule('/<google_apps_domain>/introducing', view_func=MainHandler.as_view('MainHandlerPage'))
