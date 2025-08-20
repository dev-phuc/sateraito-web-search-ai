#!/usr/bin/python
# coding: utf-8

from flask import render_template, request, make_response
import json
from sateraito_logger import logging
from google.appengine.api import taskqueue, namespace_manager

# import datetime
# from dateutil import zoneinfo, tz

import sateraito_inc
import sateraito_func
import sateraito_db
import sateraito_page


class _GetOtherSetting(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

  def process(self, google_apps_domain, app_id):
    # set response header
    self.setResponseHeader('Content-Type', 'application/json')
    # check if cached data exists
    # get data
    row_dict = sateraito_db.OtherSetting.getDict(auto_create=True)
    is_preview, attached_file_viewer_type = sateraito_func.getSettingAttachViewerType(google_apps_domain)

    ret_obj = {
      'doc_sort_setting': row_dict['doc_sort_setting'],
      'use_sateraito_address_popup': row_dict['use_sateraito_address_popup'],
      'sateraito_address_popup_url_param': row_dict['sateraito_address_popup_url_param'],
      'additional_admin_user_groups': ' '.join(row_dict['additional_admin_user_groups']),
      'limit_access_to_doc_management': row_dict['limit_access_to_doc_management'],
      'access_allowd_user_groups': ' '.join(row_dict['access_allowd_user_groups']),
      'user_can_delete_doc': row_dict['user_can_delete_doc'],
      'users_groups_can_delete_doc': ' '.join(row_dict['users_groups_can_delete_doc']),
      'enable_other_app_id_reference': row_dict['enable_other_app_id_reference'],
      'reference_app_id': row_dict['reference_app_id'],
      'csv_fileencoding': sateraito_func.none2ZeroStr(row_dict['csv_fileencoding']),
      'cols_to_show': row_dict['cols_to_show'],
      'is_ok_to_delete_doc': sateraito_func.isOkToDeleteWorkflowDoc(self.viewer_email, google_apps_domain, app_id, other_setting=row_dict),
      'enable_attach_file_keyword_search_function': sateraito_func.noneToFalse(row_dict.get('enable_attach_file_keyword_search_function', False)),
      'enable_send_mail_doc_create': sateraito_func.noneToFalse(row_dict.get('enable_send_mail_doc_create', False)),
      'enable_send_mail_doc_edit': sateraito_func.noneToFalse(row_dict.get('enable_send_mail_doc_edit', False)),
      'enable_send_mail_doc_delete': sateraito_func.noneToFalse(row_dict.get('enable_send_mail_doc_delete', False)),
      'is_preview': is_preview,
      'attached_file_viewer_type': attached_file_viewer_type,
      'currency_data': sateraito_func.getCurrencyMasterDef(self.viewer_email),
    }

    # export json data
    jsondata = json.JSONEncoder().encode(ret_obj)
    if sateraito_inc.debug_mode:
      logging.info(jsondata)
    return jsondata

class GetOtherSetting(_GetOtherSetting):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkGadgetRequest(google_apps_domain):
      return
    
    return self.process(google_apps_domain, app_id)

class OidGetOtherSetting(_GetOtherSetting):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkOidRequest(google_apps_domain):
      return

    return self.process(google_apps_domain, app_id)


class _UpdateOtherSettingAdmin(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
  """ for workflow admin only
  """

  def process(self, google_apps_domain, app_id):
    # check if user workflow admin
    if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
      return

    # get params
    doc_sort_setting = self.request.get('doc_sort_setting')
    sateraito_address_popup_url_param = self.request.get('sateraito_address_popup_url_param')
    use_sateraito_address_popup_raw = self.request.get('use_sateraito_address_popup')
    logging.info('use_sateraito_address_popup_raw=' + str(use_sateraito_address_popup_raw))
    use_sateraito_address_popup = False
    if str(use_sateraito_address_popup_raw).lower() == 'true':
      logging.info('it is TRUE')
      use_sateraito_address_popup = True
    additional_admin_user_groups_raw = str(self.request.get('additional_admin_user_groups')).lower()
    additional_admin_user_groups = additional_admin_user_groups_raw.split(' ')
    limit_access_to_doc_management_raw = self.request.get('limit_access_to_doc_management')
    limit_access_to_doc_management = False
    if str(limit_access_to_doc_management_raw).lower() == 'true':
      limit_access_to_doc_management = True
    access_allowd_user_groups_raw = str(self.request.get('access_allowd_user_groups')).lower()
    access_allowd_user_groups = access_allowd_user_groups_raw.split(' ')

    user_can_delete_doc_raw = self.request.get('user_can_delete_doc', 'false')
    user_can_delete_doc = sateraito_func.strToBool(user_can_delete_doc_raw)
    users_groups_can_delete_doc_raw = str(self.request.get('users_groups_can_delete_doc', '')).lower()
    users_groups_can_delete_doc = []
    if users_groups_can_delete_doc_raw != '':
      users_groups_can_delete_doc = users_groups_can_delete_doc_raw.split(' ')

    enable_attach_file_keyword_search_function = sateraito_func.strToBool(self.request.get('enable_attach_file_keyword_search_function', 'false'))
    enable_send_mail_doc_create = sateraito_func.strToBool(self.request.get('enable_send_mail_doc_create', 'false'))
    enable_send_mail_doc_edit = sateraito_func.strToBool(self.request.get('enable_send_mail_doc_edit', 'false'))
    enable_send_mail_doc_delete = sateraito_func.strToBool(self.request.get('enable_send_mail_doc_delete', 'false'))

    csv_fileencoding = self.request.get('csv_fileencoding', 'cp932')
    cols_to_show = self.request.get('cols_to_show', '')

    # set response header
    self.setResponseHeader('Content-Type', 'application/json')
    # save setting
    row = sateraito_db.OtherSetting.getInstance(auto_create=True)
    row.doc_sort_setting = doc_sort_setting
    row.use_sateraito_address_popup = use_sateraito_address_popup
    row.sateraito_address_popup_url_param = sateraito_address_popup_url_param
    row.additional_admin_user_groups = additional_admin_user_groups
    row.limit_access_to_doc_management = limit_access_to_doc_management
    row.access_allowd_user_groups = access_allowd_user_groups
    row.user_can_delete_doc = user_can_delete_doc
    row.users_groups_can_delete_doc = users_groups_can_delete_doc
    row.csv_fileencoding = csv_fileencoding
    row.cols_to_show = cols_to_show
    row.enable_attach_file_keyword_search_function = enable_attach_file_keyword_search_function
    row.enable_send_mail_doc_create = enable_send_mail_doc_create
    row.enable_send_mail_doc_edit = enable_send_mail_doc_edit
    row.enable_send_mail_doc_delete = enable_send_mail_doc_delete
    row.put()
    
    # export json data
    jsondata = json.JSONEncoder().encode({'status': 'ok'})
    if sateraito_inc.debug_mode:
      logging.info(jsondata)
    return jsondata

class UpdateOtherSettingAdmin(_UpdateOtherSettingAdmin):
  """ for workflow admin only
  """

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkGadgetRequest(google_apps_domain):
      return
    # check if user workflow admin
    if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
      return
    
    return self.process(google_apps_domain, app_id)

class UpdateOtherSettingAdminOid(_UpdateOtherSettingAdmin):
  """ for workflow admin only
  """

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkOidRequest(google_apps_domain):
      return
    # check if user workflow admin
    if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
      return
    
    return self.process(google_apps_domain, app_id)


class UpdateAppIdReferenceAdmin(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
  """ for workflow admin only
  """

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkGadgetRequest(google_apps_domain):
      return
    # check if user workflow admin
    if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
      return
    
    # get params
    enable_other_app_id_reference_raw = self.request.get('enable_other_app_id_reference')
    enable_other_app_id_reference = sateraito_func.strToBool(enable_other_app_id_reference_raw)
    reference_app_id = self.request.get('reference_app_id')
    # set response header
    self.setResponseHeader('Content-Type', 'application/json')
    # check app_id
    if enable_other_app_id_reference:
      # set target namespace
      self.setNamespace(google_apps_domain, reference_app_id)
      q = sateraito_db.OtherSetting.query()
      key = q.get(keys_only=True)
      if key is None:
        # export json data
        jsondata = json.JSONEncoder().encode({
          'status': 'error',
          'error_code': 'wrong_app_id',
        })
        return jsondata
      q2 = sateraito_db.UserInfo.query()
      key2 = q2.get(keys_only=True)
      if key2 is None:
        # export json data
        jsondata = json.JSONEncoder().encode({
          'status': 'error',
          'error_code': 'no_user_info_found_for_reference_app_id',
        })
        return jsondata
      # set old namespace
      self.setNamespace(google_apps_domain, app_id)
    # save setting
    row = sateraito_db.OtherSetting.getInstance(auto_create=True)
    row.enable_other_app_id_reference = enable_other_app_id_reference
    row.reference_app_id = reference_app_id
    row.put()
    # schedule reset accessible info date
    queue = taskqueue.Queue('default')
    task = taskqueue.Task(
      url='/' + google_apps_domain + '/' + app_id + '/othersetting/tq/resetallaccessibleinfoupdateddate',
      target=sateraito_func.getBackEndsModuleNameDeveloper('b1process'),
      countdown=10
    )
    queue.add(task)

    # export json data
    jsondata = json.JSONEncoder().encode({'status': 'ok'})
    if sateraito_inc.debug_mode:
      logging.info(jsondata)
    return jsondata


class TqResetAllAccessibleInfoUpdateDate(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    
    # update data
    q = sateraito_db.UserAccessibleInfo.query()
    #    q = q.filter(sateraito_db.UserAccessibleInfo.updated_date > datetime.datetime(1970, 1, 30))
    for key in q.iter(keys_only=True):
      row = key.get()
      logging.info('processing ' + row.email)
      if row.need_update is None or row.need_update == False:
        row.need_update = True
        row.put()

    return make_response('', 200)


class _UpdateImpersonateEmail(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

  def process(self, google_apps_domain, viewer_email):

    if not sateraito_func.isValidImpersonateEmail(viewer_email, google_apps_domain):
      # export json data
      jsondata = json.JSONEncoder().encode({
        'status': 'ng',
        'error_code': 'user_is_not_admin_or_oauth2_not_installed',
      })
      return jsondata

    domain_entry = sateraito_func.setImpersonateEmail(google_apps_domain, viewer_email, False)
    
    # set response header
    self.setResponseHeader('Content-Type', 'application/json')

    # export json data
    jsondata = json.JSONEncoder().encode({'status': 'ok'})
    if sateraito_inc.debug_mode:
      logging.info(jsondata)
    return jsondata

class UpdateImpersonateEmail(_UpdateImpersonateEmail):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    namespace_manager.set_namespace(google_apps_domain)
    # check request
    if not self.checkGadgetRequest(google_apps_domain):
      return

    #		# check if user workflow admin
    #		if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain):
    #			return

    return self.process(google_apps_domain, self.viewer_email)

class OidUpdateImpersonateEmail(_UpdateImpersonateEmail):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    namespace_manager.set_namespace(google_apps_domain)
    # check request
    if not self.checkOidRequest(google_apps_domain):
      return

    # if sateraito_func.check_user_is_admin(google_apps_domain, self.viewer_email) is True:
    return self.process(google_apps_domain, self.viewer_email)


def add_url_rules(app):
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/othersetting/tq/resetallaccessibleinfoupdateddate',
                   view_func=TqResetAllAccessibleInfoUpdateDate.as_view('OtherSettingTqResetAllAccessibleInfoUpdateDate'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/othersetting/updateappidreferenceadmin',
                   view_func=UpdateAppIdReferenceAdmin.as_view('OtherSettingUpdateAppIdReferenceAdmin'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/othersetting/getothersetting',
                   view_func=GetOtherSetting.as_view('OtherSettingGetOtherSetting'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/othersetting/oid/getothersetting',
                   view_func=OidGetOtherSetting.as_view('OtherSettingOidGetOtherSetting'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/othersetting/updateothersettingadmin',
                   view_func=UpdateOtherSettingAdmin.as_view('OtherSettingUpdateOtherSettingAdmin'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/othersetting/oid/updateothersettingadmin',
                   view_func=UpdateOtherSettingAdminOid.as_view('OtherSettingUpdateOtherSettingAdminOid'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/othersetting/updateimpersonateemail',
                   view_func=UpdateImpersonateEmail.as_view('OtherSettingUpdateImpersonateEmail'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/othersetting/oid/updateimpersonateemail',
                   view_func=OidUpdateImpersonateEmail.as_view('OtherSettingOidUpdateImpersonateEmail'))

