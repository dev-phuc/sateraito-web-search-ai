#!/usr/bin/python
# coding: utf-8

__author__ = 'Tran Minh Phuc<phuc@vnd.sateraito.co.jp>'

from flask import render_template, request, make_response
from sateraito_logger import logging
from json import JSONEncoder

from google.appengine.api import namespace_manager

import sateraito_page
import sateraito_func
import sateraito_db

from ucf.utils.ucfutil import UcfUtil
from sateraito_func import toShortLocalTime

'''
externallinksetting.py

@since: 2015-06-02
@version: 2015-06-02
@author: Tran Minh Phuc
'''

class AdminPage(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	pass


class ExternalLinkSettingPage(AdminPage):

	def doAction(self, tenant_or_domain, app_id):
		#primaryDomain = sateraito_db.MultiDomainEntry.setNameSpaceAndGetPrimaryDomain(tenant_or_domain)

		# token check
		if not self.checkToken(tenant_or_domain):
			return

		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(tenant_or_domain, app_id)
		#row = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)

		user_token = self.request.get('token')
		hl = self.request.get('hl')

		# get language
		user_language = sateraito_func.getUserLanguage(self.viewer_email, hl=hl)
		my_lang = sateraito_func.MyLang(user_language)
		logging.info('user_language=' + user_language)

		# sateraito new ui 2020-05-07
		new_ui, new_ui_config, new_ui_afu = sateraito_func.getNewUISetting(self, tenant_or_domain)

		# template values
		values = {
			'tenant_or_domain': tenant_or_domain,
			'app_id': app_id,
			'my_site_url': sateraito_func.getMySiteURL(tenant_or_domain, request.url),
			'version': sateraito_func.getScriptVersionQuery(),
			'vscripturl': sateraito_func.getScriptVirtualUrl(new_ui=new_ui),
			'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
			'user_token': user_token,
			'lang': user_language,
			'extjs_locale_file': sateraito_func.getExtJsLocaleFileName(user_language),
			'sharepoint_auth_url': '',
			'mode': '',
			'new_ui': new_ui,
			'new_ui_config': new_ui_config,
			'new_ui_afu': new_ui_afu,
		}
		sateraito_func.setNamespace(old_namespace, app_id)

		template_filename = 'externallinksetting_page.html'
		template_filename = sateraito_func.convertTemplateFileName(template_filename, new_ui=new_ui)
		return render_template(template_filename, **values)


class SaveSettingBase(AdminPage):

	def updateParam(self, domain_entry):
		"""
			�q�N���X�ŃI�[�o�[���C�h����
		"""
		return False

	def doAction(self, tenant_or_domain, app_id):

		is_ok = self.checkToken(tenant_or_domain)
		if not is_ok:
			values = {
				'my_site_url': sateraito_func.getMySiteURL(tenant_or_domain, request.url),
				'version': sateraito_func.getScriptVersionQuery(),
				'vscripturl': sateraito_func.getScriptVirtualUrl(),
				'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
				'lang': self.request.get('hl'),
			}
			return render_template('not_available.html', **values)

		# CSRF�g�[�N���`�F�b�N
		if not sateraito_func.checkCsrf(request):
			logging.exception('Invalid token')
			return

		# set header
		self.setResponseHeader('Content-Type', 'application/json')
		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(tenant_or_domain, app_id)

		ret_obj = {
			'status': 'ok',
		}

		# export json data
		return JSONEncoder().encode(ret_obj)


class SaveSharePointUrl(AdminPage):

	def updateParam(self, setting_entry):
		"""
			�q�N���X�ŃI�[�o�[���C�h����
		"""
		return False

	def doAction(self, tenant_or_domain, app_id):

		is_ok = self.checkToken(tenant_or_domain)
		if not is_ok:
			values = {
				'my_site_url': sateraito_func.getMySiteURL(tenant_or_domain, request.url),
				'version': sateraito_func.getScriptVersionQuery(),
				'vscripturl': sateraito_func.getScriptVirtualUrl(),
				'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
				'lang': self.request.get('hl'),
			}
			return render_template('not_available.html', **values)

		# CSRF�g�[�N���`�F�b�N
		if not sateraito_func.checkCsrf(request):
			logging.exception('Invalid token')
			return

		# set header
		self.setResponseHeader('Content-Type', 'application/json')
		sateraito_func.setNamespace(tenant_or_domain, app_id)

		boolModified = False
		# settingEntry = sateraito_db.OtherSetting.getInstance(auto_create=True)
		# if self.updateParam(settingEntry):
		# 	boolModified = True

		strErrtype = ''

		# �e�p�����[�^��ݒ�
		# paramValue = self.request.get('sharepoint_auth_url', None)
		# if ((paramValue is not None) and (settingEntry.sharepoint_auth_url != paramValue)):
		# 	boolModified = True
		# 	settingEntry.sharepoint_auth_url = paramValue

		# if boolModified:
		# 	settingEntry.put()

		if (strErrtype == ''):
			ret_obj = {
				'status': 'ok',
			}
		else:
			ret_obj = {
				'status': 'error',
				'error_type': strErrtype
			}

		# export json data
		return JSONEncoder().encode(ret_obj)


# APIKEY����쐬����
class CreateNewAPIKey(AdminPage):

	def updateParam(self, setting_entry):
		"""
			�q�N���X�ŃI�[�o�[���C�h����
		"""
		return False

	def doAction(self, tenant_or_domain, app_id):

		is_ok = self.checkToken(tenant_or_domain)
		if not is_ok:
			values = {
				'my_site_url': sateraito_func.getMySiteURL(tenant_or_domain, request.url),
				'version': sateraito_func.getScriptVersionQuery(),
				'vscripturl': sateraito_func.getScriptVirtualUrl(),
				'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
				'lang': self.request.get('hl'),
			}
			return render_template('not_available.html', **values)

		# CSRF�g�[�N���`�F�b�N
		if not sateraito_func.checkCsrf(request):
			logging.exception('Invalid token')
			return

		# set header
		self.setResponseHeader('Content-Type', 'application/json')
		sateraito_func.setNamespace(tenant_or_domain, app_id)

		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(tenant_or_domain, '')

		api_key_row = sateraito_db.APIKey()
		api_key_row.unique_id = UcfUtil.guid()
		api_key_row.api_key = UcfUtil.guid()
		api_key_row.creator_email = self.viewer_email
		api_key_row.put()

		namespace_manager.set_namespace(old_namespace)

		# export json data
		return JSONEncoder().encode({
			'status': 'ok',
			'api_key': api_key_row.api_key,
		})


# APIKEY����폜����
class DeleteAPIKey(AdminPage):

	def updateParam(self, setting_entry):
		"""
			�q�N���X�ŃI�[�o�[���C�h����
		"""
		return False

	def doAction(self, tenant_or_domain, app_id):

		is_ok = self.checkToken(tenant_or_domain)
		if not is_ok:
			values = {
				'my_site_url': sateraito_func.getMySiteURL(tenant_or_domain, request.url),
				'version': sateraito_func.getScriptVersionQuery(),
				'vscripturl': sateraito_func.getScriptVirtualUrl(),
				'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
				'lang': self.request.get('hl'),
			}
			return render_template('not_available.html', **values)

		# CSRF�g�[�N���`�F�b�N
		if not sateraito_func.checkCsrf(request):
			logging.exception('Invalid token')
			return

		unique_id = self.request.get('unique_id')
		if unique_id == '':
			logging.exception('Invalid api_key')
			return make_response('', 400)

		# set header
		self.setResponseHeader('Content-Type', 'application/json')
		sateraito_func.setNamespace(tenant_or_domain, app_id)

		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(tenant_or_domain, '')

		q = sateraito_db.APIKey.query()
		q = q.filter(sateraito_db.APIKey.unique_id == unique_id)
		key = q.get(keys_only=True)
		key.delete()

		namespace_manager.set_namespace(old_namespace)

		# export json data
		return JSONEncoder().encode({
			'status': 'ok',
		})


# APIKEY�ꗗ���擾
class GetAPIKeyList(AdminPage):

	def doAction(self, tenant_or_domain, app_id):

		# set header
		self.setResponseHeader('Content-Type', 'application/json')

		is_ok = self.checkToken(tenant_or_domain)
		if not is_ok:
			return JSONEncoder().encode({'status': 'error', 'error_code': 'not_available'})

		# CSRF�g�[�N���`�F�b�N
		if not sateraito_func.checkCsrf(request):
			logging.exception('Invalid token')
			return

		sateraito_func.setNamespace(tenant_or_domain, app_id)

		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(tenant_or_domain, '')

		boolModified = False
		q = sateraito_db.APIKey.query()
		q = q.order(sateraito_db.APIKey.created_date)
		results = []
		for api_key_row in q.iter():
			end_index = int(len(api_key_row.api_key) / 2)
			api_key_disp = "{0:*<32}".format(api_key_row.api_key[:end_index])
			item = {
					'unique_id': api_key_row.unique_id,
					'api_key': api_key_disp,
					'creator_email': api_key_row.creator_email,
					'created_date': str(toShortLocalTime(api_key_row.created_date)),
				}
			results.append(item)

		namespace_manager.set_namespace(old_namespace)

		# export json data
		return JSONEncoder().encode({
			'status': 'ok',
			'data': results,
		})


def add_url_rules(app):
	app.add_url_rule('/<string:tenant_or_domain>/<string:app_id>/externallinksetting/page',
									 view_func=ExternalLinkSettingPage.as_view('ExternalLinkSettingExternalLinkSettingPage'))

	app.add_url_rule('/<string:tenant_or_domain>/<string:app_id>/externallinksetting/savesharepointurl',
									 view_func=SaveSharePointUrl.as_view('ExternalLinkSettingSaveSharePointUrl'))

	app.add_url_rule('/<string:tenant_or_domain>/<string:app_id>/externallinksetting/createnewapikey',
									 view_func=CreateNewAPIKey.as_view('ExternalLinkSettingCreateNewAPIKey'))

	app.add_url_rule('/<string:tenant_or_domain>/<string:app_id>/externallinksetting/deleteapikey',
									 view_func=DeleteAPIKey.as_view('ExternalLinkSettingDeleteAPIKey'))

	app.add_url_rule('/<string:tenant_or_domain>/<string:app_id>/externallinksetting/getapikeylist',
									 view_func=GetAPIKeyList.as_view('ExternalLinkSettingGetAPIKeyList'))
