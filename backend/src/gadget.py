#!/usr/bin/python
# coding: utf-8

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'

from flask import Flask, Response, render_template, request, make_response, session, redirect, after_this_request
from flask.views import View, MethodView

import os, re
import json
import jinja2

# GAEGEN2対応:独自ロガー
# import logging
import sateraito_logger as logging

import datetime
from dateutil import zoneinfo
from google.appengine.api import users
from google.appengine.api import namespace_manager
from google.appengine.api import memcache
from ucf.utils.ucfutil import UcfUtil
from ucf.utils import jinjacustomfilters
from apiclient.errors import HttpError
import sateraito_inc
import sateraito_db
import sateraito_func
import sateraito_mini_pr
import sateraito_page
import checkuser

cwd = os.path.dirname(__file__)
path = os.path.join(cwd, 'templates')
bcc = jinja2.MemcachedBytecodeCache(client=memcache.Client(), prefix='jinja2/bytecode/', timeout=None)
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path), auto_reload=False, bytecode_cache=bcc)
jinjacustomfilters.registCustomFilters(jinja_environment)

def needToShowUpgradeLink(google_apps_domain):
	""" check if domain is in status to show upgrade link
		Return: True if showing upgrade link is needed
	"""
	# Upgrade link is shown ONLY IN FREE edition
	if not sateraito_inc.IS_FREE_EDITION:
		return False
	# check number of users
	row_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
	if row_dict is None:
		return False
	available_users = row_dict['available_users']
	num_users = row_dict['num_users']
	logging.info('available_users=' + str(available_users) + ' num_users=' + str(num_users))
	if available_users is not None and num_users is not None:
		if available_users < num_users:
			return True
	return False

class GadgetPage(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def renderTemplate(self, template_filename, google_apps_domain, lang=sateraito_inc.DEFAULT_LANGUAGE):

		mini_pr = ''
		if sateraito_inc.IS_FREE_EDITION:
			mini_pr = sateraito_mini_pr.getMiniPr()

		file_name = sateraito_func.getLangFileName(lang)
		lang_file = file_name + '?v=' + sateraito_func.getScriptVersionQuery()

		# sateraito new ui 2020-05-07
		new_ui, new_ui_config, new_ui_afu = sateraito_func.getNewUISetting(self, google_apps_domain)
		is_preview, attached_file_viewer_type = sateraito_func.getSettingAttachViewerType(google_apps_domain)

		# for debug
		lang_enabled = False
		if google_apps_domain in sateraito_inc.LANG_ENABLED_APPS_DOMAIN:
			lang_enabled = True

		# get all domain
		# list_google_apps_domain = sateraito_func.getListAppsDomain(google_apps_domain)

		values = {
			'lang': lang,
			'lang_file': lang_file,
			'google_apps_domain': google_apps_domain,
			# 'list_google_apps_domain': list_google_apps_domain,
			'my_site_url': sateraito_func.getMySiteURL(google_apps_domain, request.url),
			'vscripturl': sateraito_func.getScriptVirtualUrl(new_ui=new_ui),
			'mini_pr': mini_pr,
			'related_sateraito_address_domain': sateraito_func.getRelatedSateraitoAddressDomain(google_apps_domain),
			'version': sateraito_func.getScriptVersionQuery(),
			'lang_enabled': lang_enabled,
			'new_ui': new_ui,
			'new_ui_config': new_ui_config,
			'new_ui_afu': new_ui_afu,
			'is_preview': is_preview,
			'attached_file_viewer_type': attached_file_viewer_type,
		}

		template_filename = sateraito_func.convertTemplateFileName(template_filename, new_ui=new_ui)
		return render_template(template_filename, **values)

	def doAction(self, google_apps_domain, gadget_name):
		# google_apps_domain param check
		if str(google_apps_domain).find('.') == -1:
			# if google_apps_domain contains no '.', it is wrong
			logging.info('wrong domain name:' + str(google_apps_domain))
			return

		# language param
		hl = self.request.get('hl', None)
		if hl is None or hl == '':
			hl = sateraito_inc.DEFAULT_LANGUAGE
		else:
			hl = sateraito_func.getActiveLanguage(hl)

		domain_disabled = sateraito_func.isDomainDisabled(google_apps_domain)
		if domain_disabled:
			my_lang = sateraito_func.MyLang(hl)
			return '<html><head>'\
				+ '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'\
				+ '</head><body>'\
				+ my_lang.getMsg('THIS_APPRICATION_IS_STOPPED_FOR_YOUR_DOMAIN')\
				+ '</body></html>'

		use_iframe_version_gadget = False
		domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
		if domain_dict is not None:
			if domain_dict.get('use_iframe_version_gadget', False):
				use_iframe_version_gadget = True

		iframe = self.request.get('iframe', '')
		# 明示的なfalse指定の場合falseで上書きするように変更 2016.04.21
		logging.info('iframe=' + str(iframe))
		if str(iframe) in ['true', 'false']:
			use_iframe_version_gadget = sateraito_func.strToBool(str(iframe))


		gadget_names = sateraito_func.GetGadgetNames()
		if gadget_name in gadget_names:
			if use_iframe_version_gadget:
				gadget_name += '_iframe'
			logging.info('gadget_name=' + str(gadget_name))
			return self.renderTemplate(gadget_name + '.xml', google_apps_domain, lang=hl)

class HtmlPage(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):
	""" OpenID version gadget screen
	"""

	def renderTemplate(self, template_filename, google_apps_domain, app_id, is_oidc_need_show_signin_link=False, lang=None):

		mini_pr = ''
		if sateraito_inc.IS_FREE_EDITION:
			mini_pr = sateraito_mini_pr.getMiniPr()

		user_info_found = False
		if self.viewer_email is not None and self.viewer_email != '':
			logging.info("self.viewer_email=" + self.viewer_email)
			old_namespace = namespace_manager.get_namespace()
			sateraito_func.setNamespace(google_apps_domain, app_id)
			user_info = sateraito_db.UserInfo.getInstance(self.viewer_email)
			user_info_found = True
			if user_info is None:
				user_info_found = False
			else:
				user_language = sateraito_db.UserInfo.getUserLanguage(self.viewer_email, hl=lang)
				if lang is None:
					lang = user_language
			namespace_manager.set_namespace(old_namespace)

		domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
		hide_ad = domain_dict.get('hide_ad', False)
		if google_apps_domain in ['satelaito.jp', 'sateraito.jp', 'line.sateraito.jp', 'sateraito-demo.facebook.com']:
			no_auto_logout = not (domain_dict.get('no_login_cache', False))
		else:
			no_auto_logout = domain_dict.get('no_auto_logout', False)

		multi_domain_setting = False
		if domain_dict is None:
			multi_domain_setting = False
		else:
			multi_domain_setting = domain_dict.get('multi_domain_setting', False)

		# get language
		lang_file = sateraito_func.getLangFileName(lang)
		my_lang = sateraito_func.MyLang(lang)
		# user_language = sateraito_db.UserInfo.getUserLanguage(self.viewer_email, hl=lang)
		sateraito_lang = my_lang.getMsgs()

		# check domain_disabled
		domain_disabled = False
		if sateraito_func.isDomainDisabled(google_apps_domain):
			domain_disabled = True

		if is_oidc_need_show_signin_link:
			popup = sateraito_inc.my_site_url + '/' + google_apps_domain + '/popup_oidc.html?hl=' + UcfUtil.urlEncode(lang)
		else:
			popup = ''

		# sateraito new ui 2020-05-07
		new_ui, new_ui_config, new_ui_afu = sateraito_func.getNewUISetting(self, google_apps_domain, domain_dict)
		is_preview, attached_file_viewer_type = sateraito_func.getSettingAttachViewerType(google_apps_domain)

		# get all domain
		list_google_apps_domain = sateraito_func.getListAppsDomain(google_apps_domain, domain_dict)

		values = {
			'default_lang': sateraito_inc.DEFAULT_LANGUAGE,
			'lang': lang,
			'sateraito_lang': sateraito_lang,
			'lang_file': lang_file,
			'google_apps_domain': google_apps_domain,
			'list_google_apps_domain': json.JSONEncoder().encode(list_google_apps_domain),
			'my_site_url': sateraito_func.getMySiteURL(google_apps_domain, request.url),
			'vscripturl': sateraito_func.getScriptVirtualUrl(new_ui=new_ui),
			'mini_pr': mini_pr,
			'related_sateraito_address_domain': sateraito_func.getRelatedSateraitoAddressDomain(google_apps_domain),
			'version': sateraito_func.getScriptVersionQuery(),
			'debug_mode': sateraito_inc.debug_mode,
			'hide_ad': hide_ad,
			'user_info_found': user_info_found,
			'viewer_email': self.viewer_email,
			'domain_disabled': domain_disabled,
			'multi_domain_setting': multi_domain_setting,
			'is_oidc_need_show_signin_link': is_oidc_need_show_signin_link,
			'popup': popup,
			'no_auto_logout': no_auto_logout,
			'new_ui': new_ui,
			'new_ui_config': new_ui_config,
			'new_ui_afu': new_ui_afu,
			'is_preview': is_preview,
			'attached_file_viewer_type': attached_file_viewer_type,
			'impersonate_email': sateraito_func.getImpersonateEmail(google_apps_domain),
			'app_id': app_id,
			'client_id': sateraito_inc.WEBAPP_CLIENT_ID,
			'scope_drive': sateraito_inc.OAUTH2_SCOPES_DRIVE,
			'api_key': sateraito_inc.API_KEY,
		}

		# ワークフローは簡単利用開始対応があるので必ず管理者かどうかはチェック
		# for admin page only:
		is_workflow_admin = False
		is_google_apps_admin = False
		if self.viewer_email is not None and self.viewer_email != '':
			is_workflow_admin = sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id)
			try:
				is_google_apps_admin = sateraito_func.check_user_is_admin(google_apps_domain, self.viewer_email)
			except sateraito_func.ImpersonateMailException as e:
				logging.warning(e)
		values['is_google_apps_admin'] = is_google_apps_admin
		values['is_workflow_admin'] = is_workflow_admin

		# check if showing upgrade link is needed
		show_upgrade_link = sateraito_func.needToShowUpgradeLink(google_apps_domain)
		values['show_upgrade_link'] = show_upgrade_link
		values['allow_display_template_id_on_admin_console'] = False

		template_filename = sateraito_func.convertTemplateFileName(template_filename, new_ui=new_ui)
		return render_template(template_filename, **values)

	def doAction(self, google_apps_domain, app_id, gadget_name):

		# language param
		# ガジェットのURL指定対応
		hl = self.request.get('hl', sateraito_inc.DEFAULT_LANGUAGE)

		# google_apps_domain param check
		if str(google_apps_domain).find('.') == -1:
			# if google_apps_domain contains no '.', it is wrong
			logging.info('wrong domain name:' + str(google_apps_domain))
			return

		domain_disabled = sateraito_func.isDomainDisabled(google_apps_domain)
		if domain_disabled:
			my_lang = sateraito_func.MyLang(hl)
			return '<html><head>'\
				+ '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'\
				+ '</head><body>'\
				+ my_lang.getMsg('THIS_APPRICATION_IS_STOPPED_FOR_YOUR_DOMAIN')\
				+ '</body></html>'

		# set namespace
		if not self.setNamespace(google_apps_domain, None):
			return
		#
		# check login: new subdomain user --> Add new GoogleAppsDomainEntry and GoogleAppsUserEntry
		#
		domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
		if domain_dict is None:
			# self.response.out.write('Domain ' + google_apps_domain + ' not register')
			return make_response('not register', 500)

		if google_apps_domain in ['satelaito.jp', 'sateraito.jp', 'line.sateraito.jp', 'sateraito-demo.facebook.com']:
			if not (domain_dict.get('no_login_cache', False)):
				is_force_auth = False
			else:
				is_force_auth = self.request.get('oidc') != 'cb'
		else:
			if domain_dict.get('no_auto_logout', False):
				is_force_auth = False
			else:
				is_force_auth = self.request.get('oidc') != 'cb'

		# ガジェットからではなく直接開く場合の対応 2019.11.22
		with_none_prompt = True
		if self.request.get('tabmode') == '1':
			with_none_prompt = False
		# g2対応
		is_ok, body_for_not_ok = self.oidAutoLogin(google_apps_domain, skip_domain_compatibility=True, with_error_page=True, with_none_prompt=with_none_prompt, is_force_auth=is_force_auth, hl=hl)
		if not is_ok:
			is_oidc_need_show_signin_link = self.session.get('is_oidc_need_show_signin_link')
			logging.info('is_oidc_need_show_signin_link=' + str(is_oidc_need_show_signin_link))
			if is_oidc_need_show_signin_link:
				if gadget_name in sateraito_func.GetGadgetNames():
					return self.renderTemplate(gadget_name + '.html', google_apps_domain, app_id, is_oidc_need_show_signin_link=is_oidc_need_show_signin_link, lang=hl)
			return body_for_not_ok

		# GoogleAppsUserEntry
		row_u = None

		# check domain: raise error for another domain user
		viewer_email_domain = sateraito_func.getDomainPart(self.viewer_email)
		if viewer_email_domain != google_apps_domain:
			# sub-domain user?
			if not sateraito_func.isCompatibleDomain(google_apps_domain, viewer_email_domain):
				logging.info('unmatched google apps domain and login user')
				# check GoogleAppsUserEntry exists
				row_u = None
				old_namespace = namespace_manager.get_namespace()
				try:
					sateraito_func.setNamespace(google_apps_domain, '')
					q = sateraito_db.GoogleAppsUserEntry.query()
					q = q.filter(sateraito_db.GoogleAppsUserEntry.user_email == self.viewer_email.lower())
					for row in q:
						if row.opensocial_viewer_id.find('_deleted') < 0:
							row_u = row
							break
				finally:
					namespace_manager.set_namespace(old_namespace)

				if row_u is None:
					# GoogleAppsUserEntry NOT exists --> Check he is sub-domain user by getting info using impersonating_user setting

					directory_service = sateraito_func.fetch_get_admin_sdk_service(google_apps_domain, self.viewer_email, viewer_email_domain)
					user_found = False
					try:
						user_entry = directory_service.users().get(userKey=self.viewer_email).execute()
					# except AppsForYourDomainException as instance:
					# 	# entry does not exists
					# 	user_found = False
					except HttpError as e:
						logging.info('class name:' + e.__class__.__name__ + ' message=' +str(e))
						user_found = False
					else:
						# user found: register new GoogleAppsUserEntry
						if user_entry is not None:
							logging.info('user successfully get by impersonate_mail: ' + str(self.viewer_email) + ' is subdomain user: user_entry=' + str(user_entry))
							user_found = True
							# register new GoogleAppsUserEntry
							checker = sateraito_func.RequestChecker()
							# is_admin = False
							# try:
							# 	is_admin = checker.checkAppsAdmin(self.viewer_email, google_apps_domain)		# ※ここでセットするドメインはnamespaceのドメイン（それによってOAuth2かどうかを判定するので）
							# 	logging.info('is_admin=' + str(is_admin))
							# except Exception, instance:
							# 	logging.error(instance)
							# add new GoogleAppsUserEntry
							logging.info('registering new GoogleAppsUserEntry')
							row_u = checker.putNewUserEntry(
								self.viewer_email,
								google_apps_domain,
								sateraito_func.getDomainPart(self.viewer_email),
								self.viewer_id if self.viewer_id is not None and self.viewer_id != '' else '__not_set',
								sateraito_func.OPENSOCIAL_CONTAINER_GOOGLE_SITE,
								self.viewer_user_id)
							# create GoogleAppsDomainEntry if not exist
							domain_dict = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain, subdomain=viewer_email_domain, auto_create=True)
						else:
							user_found = False

					if not user_found:
						# he is NOT subdomain user: raise error
						logging.error('unmatched google apps domain and login user')
						# self.response.out.write('wrong request')
						# self.response.set_status(403)
						return make_response('wrong request', 403)

		# add GoogleAppsUserEntry if not exist
		if row_u is None:
			# row_u = sateraito_db.GoogleAppsUserEntry.getInstance(google_apps_domain, self.viewer_email)
			row_u = None
			old_namespace = namespace_manager.get_namespace()
			try:
				sateraito_func.setNamespace(google_apps_domain, '')
				q = sateraito_db.GoogleAppsUserEntry.query()
				q = q.filter(sateraito_db.GoogleAppsUserEntry.user_email == self.viewer_email.lower())
				for row in q:
					if row.opensocial_viewer_id.find('_deleted') < 0:
						row_u = row
						break
			finally:
				namespace_manager.set_namespace(old_namespace)

			if row_u is None:
				# register new GoogleAppsUserEntry
				checker = sateraito_func.RequestChecker()
				logging.info('registering new GoogleAppsUserEntry')
				row_u = checker.putNewUserEntry(
					self.viewer_email,
					google_apps_domain,
					sateraito_func.getDomainPart(self.viewer_email),
					self.viewer_id if self.viewer_id is not None and self.viewer_id != '' else '__not_set',
					sateraito_func.OPENSOCIAL_CONTAINER_GOOGLE_SITE,
					self.viewer_user_id)

		# check last_login_month
		#
		# check and update GoogleAppsDomainEntry.last_login_month and number of users(once in a month)
		# it is OK to do this RARELY
		#
		tz_utc = zoneinfo.gettz('UTC')
		current_time_utc = datetime.datetime.now(tz_utc)
		current_month = current_time_utc.strftime('%Y-%m')
		logging.info('current_month=' + str(current_month))
		domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
		if not(domain_dict.get('last_login_month') == current_month):
			checkuser.updateLastLoginMonthAndNumUsers(self.viewer_email, domain_dict, google_apps_domain)

		if gadget_name in sateraito_func.GetGadgetNames():
			return self.renderTemplate(gadget_name + '.html', google_apps_domain, app_id, lang=hl)

		return make_response('', 404)


class GadgetTemplate(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	def renderTemplate(self, template_filename, google_apps_domain, lang='ja', timezone=sateraito_inc.DEFAULT_TIMEZONE):
		#		mini_pr = ''
		#		if sateraito_inc.IS_FREE_EDITION:
		#			mini_pr = sateraito_mini_pr.getMiniPr()

		file_name = sateraito_func.getLangFileName(lang)
		lang_file = file_name + '?v=' + sateraito_func.getScriptVersionQuery()

		# get all domain
		list_google_apps_domain = sateraito_func.getListAppsDomain(google_apps_domain)

		values = {
			'tz': timezone,
			'lang': lang,
			'lang_file': lang_file,
			'google_apps_domain': google_apps_domain,
			'list_google_apps_domain': json.JSONEncoder().encode(list_google_apps_domain),
			'my_site_url': sateraito_func.getMySiteURL(google_apps_domain, request.url),
			'vscripturl': sateraito_func.getScriptVirtualUrl(),
			#			'mini_pr': mini_pr,
			'is_free_edition': sateraito_inc.IS_FREE_EDITION,
			'related_sateraito_address_domain': sateraito_func.getRelatedSateraitoAddressDomain(google_apps_domain),
			'version': sateraito_func.getScriptVersionQuery(),
			'impersonate_email': sateraito_func.getImpersonateEmail(google_apps_domain),
			'extjs_locale_file': sateraito_func.getExtJsLocaleFileName(lang),
		}
		return render_template(template_filename, **values)

class SSiteGadgetPage(GadgetTemplate):

	def doAction(self, google_apps_domain, gadget_name):
		# 複数のオリジン指定がなぜかできない...
		# self.response.headers.add_header('Access-Control-Allow-Origin', 'https://sateraito-sites.appspot.com https://sites.sateraito.jp http://localhost')
		# self.response.headers.add_header('Access-Control-Allow-Origin', 'https://sateraito-sites.appspot.com')
		self.setResponseHeader('Access-Control-Allow-Origin', '*')

		# language param
		# ガジェットのURL指定対応
		hl = self.request.get('hl')
		if hl is None or hl == '':
			hl = sateraito_inc.DEFAULT_LANGUAGE
		logging.debug('hl=' + str(hl))

		# check gadget_name
		if gadget_name not in sateraito_func.GetGadgetNames():
			logging.warn('wrong gadget_name:' + str(gadget_name))
			return

		lang = hl
		my_lang = sateraito_func.MyLang(lang)

		domain_disabled = sateraito_func.isDomainDisabled(google_apps_domain)
		if domain_disabled:
			return '<html><head>'\
				+ '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'\
				+ '</head><body>'\
				+ my_lang.getMsg('THIS_APPRICATION_IS_STOPPED_FOR_YOUR_DOMAIN')\
				+ '</body></html>'
		
		# for gadget property
		lang_file = sateraito_func.getLangFileName(lang)
		sateraito_lang = my_lang.getMsgs()

		# sateraito new ui 2020-05-07
		new_ui, new_ui_config, new_ui_afu = sateraito_func.getNewUISetting(self, google_apps_domain)
		is_preview, attached_file_viewer_type = sateraito_func.getSettingAttachViewerType(google_apps_domain)

		# get all domain
		list_google_apps_domain = sateraito_func.getListAppsDomain(google_apps_domain)

		# rendering
		values = {
			'google_apps_domain': google_apps_domain,
			'list_google_apps_domain': json.JSONEncoder().encode(list_google_apps_domain),
			'lang': lang,
			'lang_file': lang_file,
			'sateraito_lang': sateraito_lang,
			# SSITE対応：カスタムドメイン対応 2016.11.28
			'my_site_url': sateraito_func.getMySiteURL(google_apps_domain, request.url),
			'version': sateraito_func.getScriptVersionQuery(),
			'vscripturl': sateraito_func.getScriptVirtualUrl(new_ui=new_ui),
			'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
			'new_ui': new_ui,
			'new_ui_config': new_ui_config,
			'new_ui_afu': new_ui_afu,
			'is_preview': is_preview,
			'attached_file_viewer_type': attached_file_viewer_type,
		}

		custompropertyinfo = {}
		values['customproperty'] = custompropertyinfo

		template_filename = gadget_name + '_for_ssite.xml'

		template_filename = sateraito_func.convertTemplateFileName(template_filename, new_ui=new_ui)
		return render_template(template_filename, **values)

class SSiteHtmlPage(sateraito_page._AuthSSiteGadget):
	def renderTemplate(self, template_filename, tenant_or_domain, app_id, is_oidc_need_show_signin_link=False,
										 lang=sateraito_inc.DEFAULT_LANGUAGE, option_params=None, domain_row=None):
		# mini_pr = ''
		# if sateraito_inc.IS_FREE_EDITION:
		#	mini_pr = sateraito_mini_pr.getMiniPr()

		user_info_found = False
		if self.viewer_email is not None and self.viewer_email != '':
			old_namespace = namespace_manager.get_namespace()
			sateraito_func.setNamespace(tenant_or_domain, app_id)
			user_info = sateraito_db.UserInfo.getInstance(self.viewer_email)
			user_info_found = True
			if user_info is None:
				user_info_found = False
			namespace_manager.set_namespace(old_namespace)

		if domain_row is None:
			domain_row = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)

		hide_ad = sateraito_func.noneToFalse(domain_row.hide_ad)

		# sateraito new ui 2020-05-07
		new_ui, new_ui_config, new_ui_afu = sateraito_func.getNewUISetting(self, tenant_or_domain)
		is_preview, attached_file_viewer_type = sateraito_func.getSettingAttachViewerType(tenant_or_domain)

		# get language
		user_language = sateraito_func.getUserLanguage(self.viewer_email, hl=lang)

		# for gadget property
		lang_file = sateraito_func.getLangFileName(lang)
		my_lang = sateraito_func.MyLang(lang)
		sateraito_lang = my_lang.getMsgs()

		# check domain_disabled
		domain_disabled = False
		if sateraito_func.isDomainDisabled(tenant_or_domain):
			domain_disabled = True

		# if is_oidc_need_show_signin_link:
		#	popup = sateraito_inc.my_site_url + '/' + tenant_or_domain + '/popup_oidc.html?hl=' + UcfUtil.urlEncode(lang)
		# else:
		#	popup = ''
		popup = ''

		# 管理者判定
		is_workflow_admin = False
		# ワークフローは簡単利用開始対応があるので必ず管理者かどうかはチェック
		## for admin page only:
		# if template_filename == 'admin_console.html':
		if True:
			if self.viewer_email is not None and self.viewer_email != '':
				is_workflow_admin = sateraito_func.isWorkflowAdminForSSite(self.viewer_email, tenant_or_domain, app_id, do_not_include_additional_admin=False)

		# 簡単利用開始対応（Apps版はgadget.py で認証しないのでここで処理） 2015.10.26
		# 同テナント＆アプリケーションID領域に初期ひな形を作成
		# if is_workflow_admin:		# 初回に一般ユーザーがアクセスすることは実質ないので考慮不要
		#     checkuser.CheckUser(self).presetContents(tenant_or_domain, app_id, self.viewer_email, hl=lang)

		# get all domain
		list_google_apps_domain = sateraito_func.getListAppsDomain(tenant_or_domain)

		values = {

			# 'default_lang': sateraito_inc.DEFAULT_LANGUAGE,
			'lang': lang,
			'user_lang': user_language,
			'sateraito_lang': sateraito_lang,
			'lang_file': lang_file,
			'extjs_locale_file': sateraito_func.getExtJsLocaleFileName(user_language),
			'google_apps_domain': tenant_or_domain,
			'list_google_apps_domain': json.JSONEncoder().encode(list_google_apps_domain),
			'app_id': app_id,
			# SSITE対応：カスタムドメイン対応 2016.11.28
			'my_site_url': sateraito_func.getMySiteURL(tenant_or_domain, request.url),
			'version': sateraito_func.getScriptVersionQuery(),
			'vscripturl': sateraito_func.getScriptVirtualUrl(new_ui=new_ui),
			'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
			# 'mini_pr': mini_pr,
			'is_free_edition': sateraito_func.noneToFalse(domain_row.is_free_mode),
			'debug_mode': sateraito_inc.debug_mode,
			'hide_ad': hide_ad,
			'is_oauth2_domain': True,
			'mode': sateraito_func.MODE_SSITE,
			'show_upgrade_link': sateraito_func.needToShowUpgradeLink(tenant_or_domain),
			'is_oidc_need_show_signin_link': is_oidc_need_show_signin_link,
			'popup': popup,
			'user_info_found': user_info_found,
			'viewer_email': self.viewer_email,
			'user_disabled': False,  # user_entryからほんとは取得するが実際使っていないので..
			'domain_disabled': domain_disabled,
			'is_workflow_admin': is_workflow_admin,
			'no_auto_logout': False,
			'new_ui': new_ui,
			'new_ui_config': new_ui_config,
			'new_ui_afu': new_ui_afu,
			'is_preview': is_preview,
			'attached_file_viewer_type': attached_file_viewer_type,
		}

		if option_params is not None:
			for k, v in iter(option_params.items()):
				values[k] = v

		template_filename = sateraito_func.convertTemplateFileName(template_filename, new_ui=new_ui)
		return render_template(template_filename, **values)

	def _process(self, tenant, app_id, gadget_name):
		hl = self.request.get('hl')
		logging.info('hl=' + str(hl))
		if hl == '':
			hl = 'en'  # サテライトサイト版はデフォルト英語

		domain_disabled = sateraito_func.isDomainDisabled(tenant)
		if domain_disabled:
			my_lang = sateraito_func.MyLang(hl)
			return '<html><head>'\
				+ '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'\
				+ '</head><body>'\
				+ my_lang.getMsg('THIS_APPRICATION_IS_STOPPED_FOR_YOUR_DOMAIN')\
				+ '</body></html>'

		# set namespace
		sateraito_func.setNamespace('', '')

		tenant = tenant.lower()  # 追加 2018.08.28

		if not sateraito_func.isValidAppId(app_id):
			app_id = sateraito_func.DEFAULT_APP_ID

		logging.debug('tenant=' + str(tenant))
		logging.debug('app_id=' + str(app_id))

		no_auto_logout = False
		# SSITE用のテナントIDかどうかをチェック
		domain_row = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant)
		if domain_row is None or domain_row.is_disable or domain_row.google_apps_domain is None or domain_row.google_apps_domain == '' or not domain_row.is_ssite_tenant:
			my_lang = sateraito_func.MyLang(hl)
			# self.response.out.write(my_lang.getMsg('UNAVAILABLE_ON_SSSITE'))
			# self.response.out.write('The tenant "' + tenant + '" is unavailable for ssite.')
			vHTML = '<html><head>'
			vHTML += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
			vHTML += '</head><body>'
			vHTML += my_lang.getMsg('UNAVAILABLE_ON_SSITE')
			vHTML += '</body></html>'
			return make_response(vHTML, 200)

		# 認証（簡易認証）…TODO 標準高速化対応ができたら、OIDC認証に切り替えたい
		if not self._authSSiteGadget(tenant, domain_row):
			return

		tenant_or_domain = domain_row.google_apps_domain
		logging.info('tenant_or_domain=' + tenant_or_domain)

		# set namespace
		self.setNamespace(tenant_or_domain, app_id)

		user_email = self.viewer_email
		sp_user_email = user_email.split('@')
		target_domain = ''
		if len(sp_user_email) >= 2:
			target_domain = sp_user_email[1].lower()
		logging.info('target_domain=' + target_domain)

		if self.viewer_user_id is not None and self.viewer_user_id != '':
			auth_token_living_days = 1
			# if no_auto_logout:
			#	auth_token_living_days = sateraito_page.MAX_AUTH_TOKEN_AGE_DAYS_FOR_NO_AUTO_LOGOUT_MODE
			rc = sateraito_func.RequestChecker()
			# user_token = rc.registOrUpdateUserEntry(tenant, app_id, user_email, target_domain, self._current_user_name_id, self._host_name, self._current_user_name_id, None, enable_oidc_login=True, user_object_id=self.user_object_id, auth_token_living_days=auth_token_living_days)
			user_token = rc.registOrUpdateUserEntry(tenant, user_email, target_domain, self.viewer_user_id, self._host_name,
																							self.viewer_user_id, self._current_user_is_admin)
		# if user_token is not None and user_token != '':
		#	self.setTokenToCookie(user_token)	# token…Cookie上書き

		is_admin = self._current_user_is_admin
		logging.info('is_admin=' + str(is_admin))

		sateraito_func.registDomainEntry(tenant_or_domain, tenant_or_domain, user_email)
		viewer_email_domain = target_domain
		if viewer_email_domain != tenant_or_domain:
			sateraito_func.registDomainEntry(tenant_or_domain, viewer_email_domain, user_email)

		option_params = {}
		if gadget_name == sateraito_func.GADGET_ADMIN_CONSOLE:
			# 申請書検索タブを非表示にする
			hast = self.request.get('hast')
			hast = sateraito_func.strToBool(hast) if hast is not None else False
			# 申請書ひな形タブを非表示にする
			hatt = self.request.get('hatt')
			hatt = sateraito_func.strToBool(hatt) if hatt is not None else False
			# ユーザー情報タブを非表示にする
			huit = self.request.get('huit')
			huit = sateraito_func.strToBool(huit) if huit is not None else False
			# 承認グループ情報タブを非表示にする
			hagit = self.request.get('hagit')
			hagit = sateraito_func.strToBool(hagit) if hagit is not None else False
			# 参照用マスターデータタブを非表示にする
			hrmdt = self.request.get('hrmdt')
			hrmdt = sateraito_func.strToBool(hrmdt) if hrmdt is not None else False
			# 連係設定タブを非表示にする
			hsst = self.request.get('hsst')
			hsst = sateraito_func.strToBool(hsst) if hsst is not None else False
			# 申請一覧項目タブを非表示にする
			hslct = self.request.get('hslct')
			hslct = sateraito_func.strToBool(hslct) if hslct is not None else False
			# スマートフォン設定タブを非表示にする
			hspst = self.request.get('hspst')
			hspst = sateraito_func.strToBool(hspst) if hspst is not None else False
			# オペレーションログタブを非表示にする
			holt = self.request.get('holt')
			holt = sateraito_func.strToBool(holt) if holt is not None else False
			# その他の設定タブを非表示にする
			host = self.request.get('host')
			host = sateraito_func.strToBool(host) if host is not None else False

			option_params = {
				'hast': str(hast).lower(),
				'hatt': str(hatt).lower(),
				'huit': str(huit).lower(),
				'hagit': str(hagit).lower(),
				'hrmdt': str(hrmdt).lower(),
				'hsst': str(hsst).lower(),
				'hslct': str(hslct).lower(),
				'hspst': str(hspst).lower(),
				'holt': str(holt).lower(),
				'host': str(host).lower(),
			}
		logging.info(option_params)

		# language param

		gadget_names = sateraito_func.GetGadgetNames()
		for defined_gadget_name in gadget_names:
			if gadget_name == defined_gadget_name:
				return self.renderTemplate(gadget_name + '_for_ssite.html', tenant_or_domain, app_id, lang=hl,
														option_params=option_params, domain_row=domain_row)

		return make_response('', 404)

	def doAction(self, tenant, app_id, gadget_name):
		return self._process(tenant, app_id, gadget_name)

class SSOGadgetHtmlPage(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):
	def renderTemplate(self, template_filename, tenant_or_domain, app_id, is_oidc_need_show_signin_link=False,
										 lang=sateraito_inc.DEFAULT_LANGUAGE, option_params=None, domain_row=None,
										 timezone=sateraito_inc.DEFAULT_TIMEZONE):
		user_info_found = False
		if self.viewer_email is not None and self.viewer_email != '':
			old_namespace = namespace_manager.get_namespace()
			sateraito_func.setNamespace(tenant_or_domain, app_id)
			user_info = sateraito_db.UserInfo.getInstance(self.viewer_email)
			user_info_found = True
			if user_info is None:
				user_info_found = False
			namespace_manager.set_namespace(old_namespace)

		if domain_row is None:
			domain_row = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)
		hide_ad = sateraito_func.noneToFalse(domain_row.hide_ad)

		# sateraito new ui 2020-05-07
		new_ui, new_ui_config, new_ui_afu = sateraito_func.getNewUISetting(self, tenant_or_domain)
		is_preview, attached_file_viewer_type = sateraito_func.getSettingAttachViewerType(tenant_or_domain)

		# get language
		user_language = sateraito_func.getUserLanguage(self.viewer_email, hl=lang)
		# for gadget property
		lang_file = sateraito_func.getLangFileName(lang)
		my_lang = sateraito_func.MyLang(lang)
		sateraito_lang = my_lang.getMsgs()
		# check domain_disabled
		domain_disabled = False
		if sateraito_func.isDomainDisabled(tenant_or_domain):
			domain_disabled = True
		no_auto_logout = domain_row.no_auto_logout if domain_row.no_auto_logout is not None else False

		# 管理者判定
		is_workflow_admin = False
		# ワークフローは簡単利用開始対応があるので必ず管理者かどうかはチェック
		if self.viewer_email is not None and self.viewer_email != '':
			is_workflow_admin = sateraito_func.isWorkflowAdminForSSOGadget(self.viewer_email, tenant_or_domain, app_id, do_not_include_additional_admin=False)
		logging.info('is_workflow_admin=' + str(is_workflow_admin))
		# 簡単利用開始対応
		# 同テナント＆アプリケーションID領域に初期ひな形を作成
		# if is_workflow_admin:		# 初回に一般ユーザーがアクセスすることは実質ないので考慮不要
		#     checkuser.CheckUser(self).presetContents(tenant_or_domain, app_id, self.viewer_email, hl=lang)

		# get all domain
		list_google_apps_domain = sateraito_func.getListAppsDomain(tenant_or_domain)

		values = {
			'lang': lang,
			'user_lang': user_language,
			'lang_file': lang_file,
			'sateraito_lang': sateraito_lang,
			'extjs_locale_file': sateraito_func.getExtJsLocaleFileName(user_language),
			'google_apps_domain': tenant_or_domain,
			'list_google_apps_domain': json.JSONEncoder().encode(list_google_apps_domain),
			'app_id': app_id,
			'my_site_url': sateraito_func.getMySiteURL(tenant_or_domain, request.url),
			'version': sateraito_func.getScriptVersionQuery(),
			'vscripturl': sateraito_func.getScriptVirtualUrl(new_ui=new_ui),
			'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
			'is_free_edition': sateraito_func.noneToFalse(domain_row.is_free_mode),
			'debug_mode': sateraito_inc.debug_mode,
			'hide_ad': hide_ad,
			'is_oauth2_domain': True,
			'mode': sateraito_func.MODE_SSOGADGET,
			'show_upgrade_link': sateraito_func.needToShowUpgradeLink(tenant_or_domain),
			'is_oidc_need_show_signin_link': is_oidc_need_show_signin_link,
			'popup': '',
			'user_info_found': user_info_found,
			'viewer_email': self.viewer_email,
			'user_disabled': False,  # user_entryからほんとは取得するが実際使っていないので..
			'domain_disabled': domain_disabled,
			'is_workflow_admin': is_workflow_admin,
			# 'no_auto_logout': True,			# SSOGadgetはSSOの画面が一瞬出ることもあり毎回ログイン認証するのも微妙？なのでひとまずTrueにしておく
			'no_auto_logout': no_auto_logout,
			'new_ui': new_ui,
			'new_ui_config': new_ui_config,
			'is_preview': is_preview,
			'attached_file_viewer_type': attached_file_viewer_type,
			'new_ui_afu': new_ui_afu,
			'related_sateraito_address_domain': sateraito_func.getRelatedSateraitoAddressDomain(tenant_or_domain),
			'tz': timezone,
			'impersonate_email': sateraito_func.getImpersonateEmail(tenant_or_domain),
		}

		if option_params is not None:
			for k, v in iter(option_params.items()):
				values[k] = v

		template_filename = sateraito_func.convertTemplateFileName(template_filename, new_ui=new_ui)
		return render_template(template_filename, **values)

	def _process(self, tenant_or_domain, app_id, gadget_name):
		logging.info('**** requests *********************')
		logging.info(self.request)

		hl = self.request.get('hl')
		logging.info('hl=' + str(hl))
		if hl == '':
			hl = 'en'  # サテライトサイトと同様にデフォルト英語とする
			
		domain_disabled = sateraito_func.isDomainDisabled(tenant_or_domain)
		if domain_disabled:
			my_lang = sateraito_func.MyLang(hl)
			return '<html><head>'\
				+ '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'\
				+ '</head><body>'\
				+ my_lang.getMsg('THIS_APPRICATION_IS_STOPPED_FOR_YOUR_DOMAIN')\
				+ '</body></html>'

		## set namespace
		# sateraito_func.setNamespace('', '')

		domain_row = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)

		logging.info(domain_row)

		# SSOGadget用のテナントIDかどうかをチェック
		if domain_row is None or domain_row.is_disable or domain_row.google_apps_domain is None or domain_row.google_apps_domain == '' or not domain_row.is_sso_tenant:
			my_lang = sateraito_func.MyLang(hl)
			vHTML = '<html><head>'
			vHTML += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
			vHTML += '</head><body>'
			vHTML += my_lang.getMsg('UNAVAILABLE_ON_SSOGADGET')
			vHTML += '</body></html>'
			return make_response(vHTML, 200)

		# 高速化オプションの設定どおりに動作 2017.03.12
		if domain_row.no_auto_logout:
			is_force_auth = False
		else:
			is_force_auth = self.request.get('oidc') != 'cb'
		# is_force_auth = False
		# if not self.checkLogin(tenant_or_domain):
		# if not self.oidAutoLogin(tenant_or_domain):
		# g2対応
		is_ok, body_for_not_ok = self.oidAutoLogin(tenant_or_domain, skip_domain_compatibility=True, with_error_page=True, with_none_prompt=True, is_force_auth=is_force_auth, hl=hl)
		if not is_ok:
			return body_for_not_ok

		if not sateraito_func.isValidAppId(app_id):
			app_id = sateraito_func.DEFAULT_APP_ID

		logging.debug('tenant_or_domain=' + str(tenant_or_domain))
		logging.debug('app_id=' + str(app_id))

		# tenant_or_domain = domain_row.google_apps_domain
		# logging.info('tenant_or_domain=' + tenant_or_domain)

		# set namespace
		self.setNamespace(tenant_or_domain, app_id)
		# 認証自体はこのページではないので変更
		# user_email = self.viewer_email
		# sp_user_email = user_email.split('@')
		# target_domain = ''
		# if len(sp_user_email) >= 2:
		#	target_domain = sp_user_email[1].lower()
		# logging.info('target_domain=' + target_domain)
		##is_admin = self._current_user_is_admin
		# is_admin = self.is_admin
		# logging.info('is_admin=' + str(is_admin))
		# host_name = domain_row.sso_entity_id
		# logging.info('host_name=' + str(host_name))
		# if self.viewer_user_id is not None and self.viewer_user_id != '':
		#	auth_token_living_days = 1
		#	rc = sateraito_func.RequestChecker()
		#	user_token = rc.registOrUpdateUserEntry(tenant_or_domain, user_email, target_domain, self.viewer_user_id, host_name, self.viewer_user_id, is_admin)
		# sateraito_func.registDomainEntry(tenant_or_domain, tenant_or_domain, user_email)
		# viewer_email_domain = target_domain
		# if viewer_email_domain != tenant_or_domain:
		#	sateraito_func.registDomainEntry(tenant_or_domain, viewer_email_domain, user_email)

		option_params = {}
		if gadget_name == sateraito_func.GADGET_ADMIN_CONSOLE:
			# 申請書検索タブを非表示にする
			hast = self.request.get('hast')
			hast = sateraito_func.strToBool(hast) if hast is not None else False
			# 申請書ひな形タブを非表示にする
			hatt = self.request.get('hatt')
			hatt = sateraito_func.strToBool(hatt) if hatt is not None else False
			# ユーザー情報タブを非表示にする
			huit = self.request.get('huit')
			huit = sateraito_func.strToBool(huit) if huit is not None else False
			# 承認グループ情報タブを非表示にする
			hagit = self.request.get('hagit')
			hagit = sateraito_func.strToBool(hagit) if hagit is not None else False
			# 参照用マスターデータタブを非表示にする
			hrmdt = self.request.get('hrmdt')
			hrmdt = sateraito_func.strToBool(hrmdt) if hrmdt is not None else False
			# 連係設定タブを非表示にする
			hsst = self.request.get('hsst')
			hsst = sateraito_func.strToBool(hsst) if hsst is not None else False
			# 申請一覧項目タブを非表示にする
			hslct = self.request.get('hslct')
			hslct = sateraito_func.strToBool(hslct) if hslct is not None else False
			# スマートフォン設定タブを非表示にする
			hspst = self.request.get('hspst')
			hspst = sateraito_func.strToBool(hspst) if hspst is not None else False
			# オペレーションログタブを非表示にする
			holt = self.request.get('holt')
			holt = sateraito_func.strToBool(holt) if holt is not None else False
			# その他の設定タブを非表示にする
			host = self.request.get('host')
			host = sateraito_func.strToBool(host) if host is not None else False

			option_params = {
				'hast': str(hast).lower(),
				'hatt': str(hatt).lower(),
				'huit': str(huit).lower(),
				'hagit': str(hagit).lower(),
				'hrmdt': str(hrmdt).lower(),
				'hsst': str(hsst).lower(),
				'hslct': str(hslct).lower(),
				'hspst': str(hspst).lower(),
				'holt': str(holt).lower(),
				'host': str(host).lower(),
			}

			logging.info(option_params)

		# language param
		gadget_names = sateraito_func.GetGadgetNames()
		for defined_gadget_name in gadget_names:
			if gadget_name == defined_gadget_name:
				return self.renderTemplate(gadget_name + '_for_ssogadget.html', tenant_or_domain, app_id, lang=hl, option_params=option_params, domain_row=domain_row)

		return make_response('', 404)

	def doAction(self, tenant_or_domain, app_id, gadget_name):
		return self._process(tenant_or_domain, app_id, gadget_name)

class LogoutPage(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):

	def doAction(self):
		# clear session value
		self.session['viewer_email'] = ''
		self.session['opensocial_viewer_id'] = ''
		self.session['is_oidc_loggedin'] = False
		self.session['is_oidc_need_show_signin_link'] = False
		# clear openid connect session
		self.removeCookie(sateraito_page.OPENID_COOKIE_NAME)
		# get msg
		my_lang = sateraito_func.MyLang(self.request.get('hl'))

		logout_message = my_lang.getMsg('LOGGED_OUT')

		template_filename = 'logout.html'
		values = {
			#'logout_message': my_lang.getMsg('LOGGED_OUT'),
			'logout_message': logout_message,
		}
		template = jinja_environment.get_template(template_filename)
		# start http body
		#self.response.out.write(template.render(values))
		return template.render(values)


class _DocDetailPopup(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):
	def process(self, google_apps_domain, app_id, workflow_doc_id):
		# language param
		is_gadget_admin = sateraito_func.strToBool(self.request.get('is_gadget_admin', 'False'))
		key_filter_doc_deleted = self.request.get('key_filter_doc_deleted', sateraito_func.KEY_FILTER_DELETED_DOC)

		screen = self.request.get('screen')
		if screen is None or screen == '':
			is_gadget_admin = False
			screen = 'user_console'
			key_filter_doc_deleted = ''

		hl = self.request.get('hl')
		if hl is None or hl == '':
			hl = sateraito_inc.DEFAULT_LANGUAGE

		not_include_delelted = True
		if is_gadget_admin and not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
			return

		is_search_all_doc = False
		is_search_doc_del = False
		is_search_doc_not_del = False
		# just admin can search doc deleted
		if is_gadget_admin:
			not_include_delelted = False

			if key_filter_doc_deleted == sateraito_func.KEY_FILTER_DOC_ALL:
				is_search_all_doc = True
			elif key_filter_doc_deleted == sateraito_func.KEY_FILTER_DELETED_DOC:
				is_search_doc_del = True
			elif key_filter_doc_deleted == sateraito_func.KEY_FILTER_NOT_DELETED_DOC:
				is_search_doc_not_del = True

		# get language
		user_language = sateraito_func.getActiveLanguage('', hl=hl)
		lang_file = sateraito_func.getLangFileName(user_language)
		my_lang = sateraito_func.MyLang(user_language)
		sateraito_lang = my_lang.getMsgs()

		logging.info('user_language=' + user_language)

		user_token = self.request.get('token', '')

		# validate need
		if workflow_doc_id is None or workflow_doc_id == '':
			return make_response('', 400)
		if screen not in ['admin_console', 'user_console']:
			return make_response('', 400)

		domain = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)

		self.setNamespace(google_apps_domain, app_id)

		is_openid_mode = True
		is_token_mode = False
		if user_token is not None:
			is_openid_mode = False
			is_token_mode = True

		user_info_found = False
		if self.viewer_email is not None and self.viewer_email != '':
			old_namespace = namespace_manager.get_namespace()
			sateraito_func.setNamespace(google_apps_domain, app_id)
			user_info = sateraito_db.UserInfo.getInstance(self.viewer_email)
			user_info_found = True
			if user_info is None:
				user_info_found = False
			namespace_manager.set_namespace(old_namespace)

		is_show_detail = False
		user_access_doc = False
		jsondata_doc = ''
		description = ''

		# Check has workflow doc with workflow_doc_id
		row_dict = sateraito_db.WorkflowDoc.getDict(workflow_doc_id)
		if row_dict is None:
			return make_response(sateraito_lang.get('MSG_NOT_FOUND_DOC'), 400)

		user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(self.viewer_email, auto_create=True)

		# Check accessible doc
		entry_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, self.viewer_email)
		if entry_dict is None:
			return
		if is_gadget_admin or sateraito_db.WorkflowDoc.isAccessibleDoc(row_dict['workflow_doc_id'], self.viewer_email, user_accessible_info_dict):
			user_access_doc = True

		dict_folder = sateraito_db.DocFolder.getDict(row_dict['folder_code'])
		folder_name = dict_folder['folder_name']
		folder_name_fullpath = dict_folder['full_path_folder']
		user_can_edit = (row_dict['author_email'] == self.viewer_email) or is_gadget_admin

		user_can_delete = True
		if not is_gadget_admin:
			user_can_delete = sateraito_func.isUserCanDeleteWorkflowDoc(google_apps_domain, app_id, self.viewer_email, workflow_doc_id, row_dict['folder_code'])

		tag_list = []
		for tag_id in row_dict['tag_list']:
			row_tag = sateraito_db.Categories.getDict(tag_id)
			if row_tag is not None:
				if row_tag is not None:
					tag_list.append({
						'id': tag_id,
						'name': row_tag['name'],
					})

		categorie_dict = sateraito_db.Categories.getDict(row_dict['categorie_id'])
		categorie = {
			'categorie_id': categorie_dict['categorie_id'],
			'name': categorie_dict['name'],
			'txt_color': categorie_dict['txt_color'],
			'bg_color': categorie_dict['bg_color'],
		}

		user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(self.viewer_email, auto_create=True)
		files = sateraito_db.FileflowDoc.getByWorkflowDoc(google_apps_domain, row_dict, dict_folder, user_accessible_info_dict,
																											auto_publish=True, not_include_delelted=not_include_delelted,
																											sort_created_date=True)
		data_currency = sateraito_func.getCurrencyMasterDef(self.viewer_email)

		is_deletable_files = True
		if not is_gadget_admin:
			is_deletable_files = sateraito_db.WorkflowDoc.isDeletableFiles(self.viewer_email, google_apps_domain, app_id,
																																		 workflow_doc_id, row_dict['folder_code'],
																																		 entry_dict['google_apps_groups'],
																																		 user_accessible_info_dict)

		description = row_dict['description'].replace('\n', 'sateraito_break_the_line')

		data_doc = {
			'id': row_dict['workflow_doc_id'],
			'workflow_doc_id': row_dict['workflow_doc_id'],
			'folder_code': row_dict['folder_code'],
			'folder_name': folder_name,
			'folder_name_fullpath': folder_name_fullpath,
			'category_id': row_dict['categorie_id'],
			'category': categorie,
			'files': files,
			'client_id': row_dict['client_id'],
			'client_name': row_dict['client_name'],
			'google_drive_folder_id': row_dict['google_drive_folder_id'],
			'notice_users': row_dict['notice_users'],
			'author_email': row_dict['author_email'],
			'author_name': row_dict['author_name'],
			'updated_author_email': row_dict['updated_author_email'],
			'updated_author_name': row_dict['updated_author_name'],
			'title': row_dict['title'],
			'tag_list': tag_list,
			'document_code': row_dict['document_code'],
			'need_preservation_doc': row_dict['need_preservation_doc'],
			'transaction_date': str(sateraito_func.getLocalDate(row_dict['transaction_date'])),
			'transaction_amount': row_dict['transaction_amount'],
			'currency': sateraito_func.getCurrencyDoc(row_dict, self.viewer_email, data_currency),
			'updated_date': sateraito_func.toShortLocalTime(row_dict['updated_date']),
			'user_can_edit': user_can_edit,
			'user_can_delete': user_can_delete,
			'doc_deleted': row_dict['del_flag'],
			'is_deletable_files': is_deletable_files,
		}
		jsondata_doc = json.JSONEncoder().encode(data_doc)

		# sateraito new ui 2020-05-07
		new_ui, new_ui_config, new_ui_afu = sateraito_func.getNewUISetting(self, google_apps_domain)
		is_preview, attached_file_viewer_type = sateraito_func.getSettingAttachViewerType(google_apps_domain)

		# get all domain
		list_google_apps_domain = sateraito_func.getListAppsDomain(google_apps_domain, domain_dict=domain)

		values = {
			'is_gadget_admin': is_gadget_admin,
			'is_gadget_mode': False,
			'is_openid_mode': is_openid_mode,
			'is_token_mode': is_token_mode,
			'user_token': user_token,
			'my_site_url': sateraito_func.getMySiteURL(google_apps_domain, request.url),
			'version': sateraito_func.getScriptVersionQuery(),
			'google_apps_domain': google_apps_domain,
			'list_google_apps_domain': json.JSONEncoder().encode(list_google_apps_domain),
			'app_id': app_id,
			'viewer_email': str(self.viewer_email),
			'user_info_found': user_info_found,
			'default_lang': sateraito_inc.DEFAULT_LANGUAGE,
			'lang': user_language,
			'sateraito_lang': sateraito_lang,
			'lang_file': lang_file,
			'hl': hl,
			'vscripturl': sateraito_func.getScriptVirtualUrl(new_ui=new_ui),
			'new_ui': new_ui,
			'new_ui_config': new_ui_config,
			'new_ui_afu': new_ui_afu,
			'is_preview': is_preview,
			'attached_file_viewer_type': attached_file_viewer_type,
			'related_sateraito_address_domain': sateraito_func.getRelatedSateraitoAddressDomain(google_apps_domain),
			'is_show_detail': True,
			'jsondata_doc': jsondata_doc,
			'description': description,
			'user_access_doc': user_access_doc,
			'screen': screen,
			'mode': self.mode,
			'is_search_all_doc': is_search_all_doc,
			'is_search_doc_del': is_search_doc_del,
			'is_search_doc_not_del': is_search_doc_not_del,
		}

		template_filename = 'docdetailpopup.html'
		template_filename = sateraito_func.convertTemplateFileName(template_filename, new_ui=new_ui)
		return render_template(template_filename, **values)

class DocDetailPopup(_DocDetailPopup):

	def doAction(self, google_apps_domain, app_id, workflow_doc_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return

		if not self._OIDCAutoLogin(google_apps_domain):
			return

		return self.process(google_apps_domain, app_id, workflow_doc_id)


def add_url_rules(app):
	app.add_url_rule('/gadget/<string:google_apps_domain>/<string:gadget_name>.xml',
									 view_func=GadgetPage.as_view('GadgetPage'))

	app.add_url_rule('/gadget/<string:google_apps_domain>/<string:app_id>/<string:gadget_name>.html',
									 view_func=HtmlPage.as_view('HtmlPage'))

	app.add_url_rule('/gadget/ssite/<string:google_apps_domain>/<string:gadget_name>.xml',
									 view_func=SSiteGadgetPage.as_view('SSiteGadgetPage'))

	app.add_url_rule('/ssite/<string:tenant>/<string:app_id>/<string:gadget_name>',
									 view_func=SSiteHtmlPage.as_view('SSiteHtmlPage'))

	app.add_url_rule('/ssogadget/<string:tenant_or_domain>/<string:app_id>/<string:gadget_name>',
									 view_func=SSOGadgetHtmlPage.as_view('SSOGadgetHtmlPage'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/docdetailpopup/<string:workflow_doc_id>',
									 view_func=DocDetailPopup.as_view('DocDetailPopup'))

	app.add_url_rule('/logout', view_func=LogoutPage.as_view('LogoutPage'))


'''
introducing.py

@created 2022-06-22
@version 1.0.0

@author: phuc@vnd.sateraito.co.jp
'''