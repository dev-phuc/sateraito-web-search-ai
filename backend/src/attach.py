#!/usr/bin/python
# coding: utf-8

__author__ = 'Tran Minh Phuc <phuc@vnd.sateraito.co.jp>'
'''
attach.py

@since: 2022-06-22
@version: 1.0.0
@author: Tran Minh Phuc
'''

# set default encodeing to utf-8
from flask import render_template, request, make_response
import json
from sateraito_logger import logging
import httpagentparser
import urllib
import time
import datetime
import io
import cgi
import mimetypes

from google.appengine.ext import ndb, blobstore
from google.appengine.api import memcache, namespace_manager, app_identity, urlfetch

from ucf.utils.ucfutil import UcfUtil

import sateraito_inc
import sateraito_func
import sateraito_db
import sateraito_page
import mail_queue

import shared.attach_shared

MAX_ATTACH_FILE_SIZE = 1024 * 1024 * 200  # 200MB
NUM_PER_PAGE_FILE_FLOW_DOC = 50

FILE_TO_TEXT_API_STATUS_QUEUED = 'queued'  # just queued need call api again
FILE_TO_TEXT_API_STATUS_PROCESSING = 'processing'  # now processing need call api again
FILE_TO_TEXT_API_STATUS_FAILED = 'failed'  # convert failed
FILE_TO_TEXT_API_STATUS_SUCCESS = 'success'  # convert succeeded


class FileUpload(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # token check
    if not self.checkToken(google_apps_domain):
      return

    # get parameter
    user_token = self.request.get('token')
    screen = self.request.get('screen')
    workflow_doc_id = self.request.get('workflow_doc_id')
    folder_code = self.request.get('folder_code')
    mode_admin = sateraito_func.strToBool(self.request.get('admin_mode', 'false'))

    # Check if user workflow admin
    if mode_admin:
      if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
        mode_admin = False

    # check capacity
    capacity_over = False
    domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
    if domain_dict['is_capacity_over']:
      capacity_over = True

    user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(self.viewer_email, auto_create=True)
    is_can_upload = sateraito_func.get_permission_can_upload_folder(folder_code, user_accessible_info_dict, self.viewer_email, google_apps_domain, mode_admin)

    hl = self.request.get('hl')
    if hl is None or hl == '':
      hl = sateraito_db.UserInfo.getUserLanguage(self.viewer_email, hl=sateraito_inc.DEFAULT_LANGUAGE)

    # sateraito new ui 2020-05-07
    new_ui, new_ui_config, new_ui_afu = sateraito_func.getNewUISetting(self, google_apps_domain)

    # start http body
    values = {
      'google_apps_domain': google_apps_domain,
      'app_id': app_id,
      'my_site_url': sateraito_func.getMySiteURL(google_apps_domain, request.url),
      'vscripturl': sateraito_func.getScriptVirtualUrl(new_ui=new_ui),
      'user_token': user_token,
      'workflow_doc_id': workflow_doc_id,
      'folder_code': folder_code,
      'is_openid_mode': False,
      'version': sateraito_func.getScriptVersionQuery(),
      'lang': hl,
      'screen': screen,
      'new_ui': new_ui,
      'new_ui_config': new_ui_config,
      'new_ui_afu': new_ui_afu,
      'is_can_upload': is_can_upload,
      'capacity_over': capacity_over,
      'is_user_can_delete': sateraito_func.isOkToDeleteWorkflowDoc(self.viewer_email, google_apps_domain, app_id),
    }

    template_filename = sateraito_func.convertTemplateFileName('file_upload.html', new_ui=new_ui)
    return render_template(template_filename, **values)


class GetUploadUrl(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # token check
    if not self.checkToken(google_apps_domain):
      return

    # set response header
    self.setResponseHeader('Content-Type', 'application/json')

    folder_code = self.request.get('folder_code', '')
    if folder_code == '':
      return json.JSONEncoder().encode({
        'status': 'error'
      })

    namespace_name = google_apps_domain + sateraito_func.DELIMITER_NAMESPACE_DOMAIN_APP_ID + app_id
    gcs_bucket_name = app_identity.get_default_gcs_bucket_name()
    gcs_filename_sub = gcs_bucket_name + '/' + namespace_name + '/' + folder_code

    # create upload url
    upload_url = blobstore.create_upload_url(
      '/' + google_apps_domain + '/' + app_id + '/attach/attachupload',
      gs_bucket_name=gcs_filename_sub,
      max_bytes_per_blob=MAX_ATTACH_FILE_SIZE
    )
    logging.info('upload_url=' + upload_url)

    return json.JSONEncoder().encode({
      'status': 'ok',
      'upload_url': upload_url,
    })


class UploadHandler(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage, blobstore.BlobstoreUploadHandler):
  """ process after blob data is uploaded to blobstore
  """

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return

    # Blobstoreからのファイル取得. request.form、request.get_data() などの前に↓を実施する必要がある
    envDummy = request.environ.copy()
    envDummy['wsgi.input'] = io.BytesIO(request.get_data())
    upload_files = self.get_uploads(envDummy, field_name='attach_file')

    # 更にFlaskのrequest.values、request.formだと、マルチパートでのPOSTに値が空の情報があると値が正しく取れなくなるためcgiを使った方法に変更（cgiは非推奨、廃止予定だが現時点では使用可能）
    request_body_byte = request.get_data()
    fp = io.BytesIO(request_body_byte)
    fs = cgi.FieldStorage(fp=fp, environ=request.environ)

    # token check
    user_token = fs.getfirst('token')
    logging.debug('token=' + str(user_token))
    if not self.checkToken(google_apps_domain, user_token=user_token):
      return

    # upload_files = self.get_blob_uploads('attach_file')  # 'file' is file upload field in the form
    workflow_doc_id = fs.getfirst('workflow_doc_id', '')
    folder_code = fs.getfirst('folder_code', '')
    screen = fs.getfirst('screen', '')
    logging.info('screen=' + str(screen))

    lang = fs.getfirst('lang', sateraito_inc.DEFAULT_LANGUAGE)
    my_lang = sateraito_func.MyLang(lang)

    domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
    is_workflow_admin = sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id)
    user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(self.viewer_email, auto_create=True)

    # check capacity
    if domain_dict['is_capacity_over']:
      return make_response('status=capacity_over', 200)

    # permission upload
    is_can_upload = sateraito_func.get_permission_can_upload_folder(folder_code, user_accessible_info_dict, self.viewer_email, google_apps_domain, is_workflow_admin)
    if not is_can_upload:
      return make_response('status=no_permission', 200)

    blob_info = upload_files[0]

    file_size = blob_info.size
    logging.info('file size=%d' % file_size)
    if file_size > MAX_ATTACH_FILE_SIZE:
      return make_response('status=too_big', 200)

    file_id = sateraito_func.createNewFileId(sateraito_db.FileflowDoc.name_field)

    blob_key = blob_info.key()

    new_blob_info = blobstore.BlobInfo.get(blob_key)
    file_name = new_blob_info.filename

    doc_dict = sateraito_db.WorkflowDoc.getDict(workflow_doc_id)

    # step1. delete all same name FileflowDoc in folder
    q = sateraito_db.FileflowDoc.query()
    q = q.filter(sateraito_db.FileflowDoc.del_flag == False)
    q = q.filter(sateraito_db.FileflowDoc.file_name == file_name)
    q = q.filter(sateraito_db.FileflowDoc.workflow_doc_id == workflow_doc_id)
    q = q.filter(sateraito_db.FileflowDoc.folder_code == folder_code)
    is_deleted = False
    publish_flag = False
    is_overwrite = False
    for key in q.iter(keys_only=True):
      row = key.get()

      # check permission overwrite file
      if not is_workflow_admin and not sateraito_func.isOkToDeleteWorkflowDoc(self.viewer_email, google_apps_domain, app_id):
        return make_response('status=no_permission_overwrite_file', 200)

      delete_row_file_id = row.file_id
      delete_row_file_size = row.file_size
      # put del_flag
      row.del_flag = True
      row.put()

      is_deleted = True
      publish_flag = True
      is_overwrite = True

      # logging
      if doc_dict is not None:
        author_name = sateraito_func.getUserName(google_apps_domain, self.viewer_email)
        detail = my_lang.getMsg('MSG_DETAIL_DELETE_FILE').format(row.file_name, author_name, doc_dict['title'])
        sateraito_db.OperationLog.addLogForFile(self.viewer_user_id, self.viewer_email,
                                                sateraito_db.OPERATION_DELETE_FILE, screen, delete_row_file_id,
                                                workflow_doc_id, detail=detail)

      # reduce total file size
      sateraito_db.FileSizeCounterShared.decrement(delete_row_file_size)

    # step2. create new FileflowDoc
    new_row = sateraito_db.FileflowDoc(id=file_id)
    new_row.workflow_doc_id = workflow_doc_id
    new_row.folder_code = folder_code
    new_row.file_id = file_id
    new_row.file_name = file_name
    new_row.blob_key = blob_key
    new_row.mime_type = blob_info.content_type
    new_row.attached_by_user_email = self.viewer_email
    new_row.file_size = blob_info.size
    new_row.publish_flag = publish_flag
    new_row.author_email = self.viewer_email
    new_row.author_name = sateraito_func.getUserName(google_apps_domain, self.viewer_email)
    new_row.put()

    # add total file size
    sateraito_db.FileSizeCounterShared.increment(new_row.file_size)
    sateraito_func.updateFreeSpaceStatus(google_apps_domain)

    # logging
    if is_overwrite and doc_dict is not None:
      detail = my_lang.getMsg('MSG_DETAIL_UPLOAD_FILE').format(new_row.file_name, new_row.author_name, doc_dict['title'])
      sateraito_db.OperationLog.addLogForFile(self.viewer_user_id, self.viewer_email,
                                              sateraito_db.OPERATION_UPLOAD_FILE, screen, file_id, workflow_doc_id,
                                              detail=detail)

    # register blob pointer
    sateraito_db.BlobPointer.registerNew(blob_info, namespace_manager.get_namespace())

    return make_response('status=ok', 200)


class CheckIsSameFileExists(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # token check
    if not self.checkToken(google_apps_domain):
      return

    # set response header
    self.setResponseHeader('Content-Type', 'application/json')

    # get parameter
    workflow_doc_id = self.request.get('workflow_doc_id')
    file_name = self.request.get('file_name')
    folder_code = self.request.get('folder_code')

    # check db
    same_file_exists = True
    q = sateraito_db.FileflowDoc.query()
    q = q.filter(sateraito_db.FileflowDoc.workflow_doc_id == workflow_doc_id)
    q = q.filter(sateraito_db.FileflowDoc.folder_code == folder_code)
    q = q.filter(sateraito_db.FileflowDoc.file_name == file_name)
    q = q.filter(sateraito_db.FileflowDoc.del_flag == False)
    key = q.get(keys_only=True)
    if key is None:
      same_file_exists = False
    else:
      # double-check
      row = key.get()
      if row.file_name == file_name:
        same_file_exists = True
      else:
        same_file_exists = False

    # export json data
    return json.JSONEncoder().encode({
      'same_file_exists': same_file_exists,
    })


class _GetByWorkflowDocID(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
  def process(self, google_apps_domain, app_id, admin_mode=False):
    # set response header
    self.setResponseHeader('Content-Type', 'application/json')

    # get parameter
    workflow_doc_id = self.request.get('workflow_doc_id')
    is_creating_new_doc = sateraito_func.boolToStr(self.request.get('is_creating_new_doc', 'false'))

    if workflow_doc_id is None:
      return make_response('workflow_doc_id: None', 200)

    doc_dict = sateraito_db.WorkflowDoc.getDict(workflow_doc_id)
    user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(self.viewer_email, auto_create=True)

    is_downloadable = False
    if doc_dict is not None:
      is_downloadable = sateraito_db.DocFolder.isDownloadableFolder(doc_dict['folder_code'], user_accessible_info_dict, google_apps_domain)
    elif is_creating_new_doc:
      is_downloadable = True

    is_deletable_files = True
    if not admin_mode and doc_dict:
      # step1. check accessible in folder
      user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(self.viewer_email)
      is_deletable = sateraito_db.DocFolder.isDeletableFolder(doc_dict['folder_code'], user_accessible_info_dict, google_apps_domain)
      if not is_deletable:
        is_deletable_files = False

      # step2. check accessible in doc
      if is_deletable_files:
        is_accessible_doc = sateraito_db.WorkflowDoc.isAccessibleDoc(workflow_doc_id, self.viewer_email, user_accessible_info_dict)
        if not is_accessible_doc:
          is_deletable_files = False

    q = sateraito_db.FileflowDoc.query()
    q = q.filter(sateraito_db.FileflowDoc.workflow_doc_id == workflow_doc_id)
    if not admin_mode:
      q = q.filter(sateraito_db.FileflowDoc.del_flag == False)
    q = q.order(-sateraito_db.FileflowDoc.created_date)

    files = []
    for row in q:
      files.append({
        'file_id': row.file_id,
        'gg_drive_file_id': row.gg_drive_file_id,
        'file_id_in_mail': row.file_id_in_mail,
        'workflow_doc_id': row.workflow_doc_id,
        'file_name': row.file_name,
        'file_description': row.file_description,
        'attachment_type': row.attachment_type,
        'attach_link': row.attach_link,
        'file_size': row.file_size,
        'mime_type': row.mime_type,
        'icon_url': row.icon_link,
        'author_name': row.author_name,
        'author_email': row.author_email,
        'folder_code': row.folder_code,
        'folder_name': sateraito_db.DocFolder.getFolderName(row.folder_code),
        'uploaded_date': str(sateraito_func.toShortLocalTime(row.uploaded_date)),
        'is_downloadable': is_downloadable,
        'publish_flag': row.publish_flag,
        'del_flag': row.del_flag,
        'type_item': 'file',
        'is_deletable': is_deletable_files,
      })

    return json.JSONEncoder().encode({
      'status': 'ok',
      'files': files,
    })

class GetByWorkflowDocID(_GetByWorkflowDocID):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkGadgetRequest(google_apps_domain):
      return

    return self.process(google_apps_domain, app_id)

class GetByWorkflowDocIDOid(_GetByWorkflowDocID):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkOidRequest(google_apps_domain):
      return

    return self.process(google_apps_domain, app_id)

class GetByWorkflowDocIDAdmin(_GetByWorkflowDocID):

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

    return self.process(google_apps_domain, app_id, admin_mode=True)

class GetByWorkflowDocIDAdminOid(_GetByWorkflowDocID):

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

    return self.process(google_apps_domain, app_id, admin_mode=True)


class _DeleteFile(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

  def process(self, google_apps_domain, app_id, mode_admin=False):
    # set response header
    self.setResponseHeader('Content-Type', 'application/json')

    # get parameter
    file_id = self.request.get('file_id')
    screen = self.request.get('screen')
    lang = self.request.get('lang', sateraito_inc.DEFAULT_LANGUAGE)
    my_lang = sateraito_func.MyLang(lang)

    dict_file = sateraito_db.FileflowDoc.getDict(file_id)
    doc_row = sateraito_db.WorkflowDoc.getInstance(dict_file['workflow_doc_id'])

    if dict_file is None:
      result = {
        'status': 'ng',
        'error_code': 'file_to_delete_not_found'
      }
      return json.JSONEncoder().encode(result)
    elif dict_file['publish_flag'] and doc_row is None:
      result = {
        'status': 'ng',
        'error_code': 'doc_dict_not_found'
      }
      return json.JSONEncoder().encode(result)
    else:
      if dict_file['publish_flag']:
        file_name = dict_file['file_name']
        file_size = dict_file['file_size']
        # check delete permission
        folder_code = dict_file['folder_code']

        if mode_admin is False:
          # # step1. check deletable_admin_only
          # folder_dict = sateraito_db.DocFolder.getDict(folder_code)
          # if folder_dict['deletable_admin_only']:
          #   # this file can be deleted in admin mode only
          #   # this api is for NORMAL USER SCREEN, so deletion is prohibited
          #   result = {
          #     'status': 'ng',
          #     'error_code': 'have_no_permission_to_delete'
          #   }
          #   jsondata = json.JSONEncoder().encode(result)
          #   self.response.out.write(jsondata)
          #   return

          # step2.
          user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(self.viewer_email)
          is_deletable = sateraito_db.DocFolder.isDeletableFolder(folder_code, user_accessible_info_dict, google_apps_domain)
          if not is_deletable:
            result = {
              'status': 'ng isDeletableFolder',
              'error_code': 'have_no_permission_to_delete'
            }
            return json.JSONEncoder().encode(result)

          # step3. check accessible in doc
          is_accessible_doc = sateraito_db.WorkflowDoc.isAccessibleDoc(dict_file['workflow_doc_id'], self.viewer_email, user_accessible_info_dict)
          if not is_accessible_doc:
            result = {
              'status': 'ng isAccessibleDoc',
              'error_code': 'have_no_permission_to_delete'
            }
            return json.JSONEncoder().encode(result)

        # logging
        author_name = sateraito_func.getUserName(google_apps_domain, self.viewer_email)
        doc_title = dict_file['workflow_doc_id']
        if doc_row is not None:
          doc_title = doc_row.title
        detail = my_lang.getMsg('MSG_DETAIL_DELETE_FILE').format(dict_file['file_name'], author_name, doc_title)
        sateraito_db.OperationLog.addLogForFile(self.viewer_user_id, self.viewer_email, sateraito_db.OPERATION_DELETE_FILE, screen, file_id, dict_file['workflow_doc_id'], detail=detail)

        # Send mail user accessible
        base_url = sateraito_func.getMySiteURL(google_apps_domain, request.url) + '/' + google_apps_domain + '/' + app_id
        doc_url = base_url + '/docdetailpopup/' + dict_file['workflow_doc_id']

        # send notice mail
        delete_user_name = author_name
        mail_queue.sendDeletedNoticeMail(folder_code, [file_id], [file_name], dict_file['workflow_doc_id'], doc_url, self.viewer_email, delete_user_name, google_apps_domain)

    # Go logical delete
    row_file = sateraito_db.FileflowDoc.getInstance(file_id)
    if row_file.publish_flag:
      row_file.del_flag = True
      row_file.put()
    else:
      # Delete files
      if row_file.cloud_storage:
        blobstore.delete(row_file.blob_key_cloud)
      elif row_file.attachment_type == 'gae_blobstore':
        blobstore.delete(row_file.blob_key)

      # Delete file in Database
      row_file.key.delete()

    # size decrement
    sateraito_db.FileSizeCounterShared.decrement(row_file.file_size)
    sateraito_func.updateFreeSpaceStatus(google_apps_domain)

    # rebuild text search workflow doc
    if doc_row is not None:
      sateraito_func.rebuildTextSearchIndexDoc(doc_row)

    # export json data
    result = {
      'status': 'ok'
    }
    return json.JSONEncoder().encode(result)

class DeleteFile(_DeleteFile):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkGadgetRequest(google_apps_domain):
      return

    return self.process(google_apps_domain, app_id, mode_admin=False)

class DeleteFileOid(_DeleteFile):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkOidRequest(google_apps_domain):
      return

    return self.process(google_apps_domain, app_id, mode_admin=False)

class DeleteFileAdmin(_DeleteFile):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkGadgetRequest(google_apps_domain):
      return
    # check admin
    if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
      return

    return self.process(google_apps_domain, app_id, mode_admin=True)

class DeleteFileAdminOid(_DeleteFile):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkOidRequest(google_apps_domain):
      return
    # check admin
    if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
      return

    return self.process(google_apps_domain, app_id, mode_admin=True)


class _GetMyFileShared(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
  def process(self, google_apps_domain):

    # get param
    page_raw = self.request.get('page')
    page = 1
    if page_raw is None or page_raw == '':
      pass
    else:
      page = int(page_raw)

    num_per_page_raw = self.request.get('num_per_page')
    num_per_page = NUM_PER_PAGE_FILE_FLOW_DOC
    if num_per_page_raw is None or num_per_page_raw == '':
      pass
    else:
      logging.info(num_per_page_raw)
      num_per_page = int(num_per_page_raw)

    # set response header
    self.setResponseHeader('Content-Type', 'application/json')

    # get child doc folders
    q = sateraito_db.FileflowDoc.query()
    q = q.filter(sateraito_db.FileflowDoc.author_email == self.viewer_email)
    q = q.filter(sateraito_db.FileflowDoc.del_flag == False)
    q = q.order(sateraito_db.FileflowDoc.created_date)
    rows = q.fetch(limit=(num_per_page + 1), offset=((page - 1) * num_per_page))

    data = []
    index = 0
    for row in rows:
      if index == (num_per_page):
        break
      data.append({
        'file_id': row.file_id,
        'workflow_doc_id': row.workflow_doc_id,
        'file_name': row.file_name,
        'file_description': row.file_description,
        'attachment_type': row.attachment_type,
        'file_size': row.file_size,
        'mime_type': row.mime_type,
        'icon_url': row.icon_link,
        'author_name': row.author_name,
        'author_email': row.author_email,
        'folder_code': row.folder_code,
        'folder_name': sateraito_db.DocFolder.getFolderName(row.folder_code),
        'uploaded_date': row.uploaded_date,
      })
      index += 1

    have_more_rows = False
    if len(rows) > num_per_page:
      have_more_rows = True

    # return status
    ret_obj = {
      'status': 'ok',
      'fileflow_docs': data,
      'have_more_rows': have_more_rows,
    }

    return json.JSONEncoder().encode(ret_obj)

class GetMyFileShared(_GetMyFileShared):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkGadgetRequest(google_apps_domain):
      return

    return self.process(google_apps_domain)

class GetMyFileSharedOid(_GetMyFileShared):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkOidRequest(google_apps_domain):
      return

    return self.process(google_apps_domain)


class _DownloadAttachedFile(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage, blobstore.BlobstoreDownloadHandler):

  def _get_one_time_token(self, key, google_apps_domain, user_email):

    row = None
    if key is not None:
      row = sateraito_db.OneTimeUserToken.getByKey(key)
    is_need_put = False
    if row is None:
      row = sateraito_db.OneTimeUserToken()
      row.user_email = user_email
      row.google_apps_domain = google_apps_domain
      row.is_sharepoint_mode = (self.mode == sateraito_func.MODE_SHAREPOINT)
      is_need_put = True
    # トークンセットなしか期限切れなら発行
    if row.user_token is None or row.user_token == '' or row.token_expire_date is None or row.token_expire_date < datetime.datetime.now():
      logging.debug('token expired')
      row.user_token = sateraito_func.createNewUserToken()
      row.token_expire_date = datetime.datetime.now() + datetime.timedelta(minutes=1)
      is_need_put = True
    # ぎりぎりなら少し伸ばす（クリックから表示までの間に切れちゃうと表示できないので）
    elif row.token_expire_date < UcfUtil.add_seconds(datetime.datetime.now(), 10):
      logging.debug('token expire soon ...')
      row.token_expire_date = row.token_expire_date + datetime.timedelta(seconds=10)
      is_need_put = True

    if is_need_put:
      row.put()
    user_token = str(row.user_token)
    logging.debug('user_token=' + user_token + 'user_email=' + str(row.user_email) + ' token_expire_date=' + str(row.token_expire_date))
    return user_token

  def getOneTimeToken(self, google_apps_domain):
    """
    getOneTimeToken
    :param google_apps_domain: string
    :return: string
    """

    token = ''

    # old namespace
    old_namespace = namespace_manager.get_namespace()
    # set namespace --> OneTimeUserToken only exists in default namespace
    namespace_manager.set_namespace(google_apps_domain)

    query = sateraito_db.OneTimeUserToken.query()
    query = query.filter(sateraito_db.OneTimeUserToken.user_email.IN([self.viewer_email, self.viewer_email.lower()]))
    key = query.get(keys_only=True, memcache_timeout=sateraito_db.NDB_MEMCACHE_TIMEOUT)
    token = ndb.transaction(lambda: self._get_one_time_token(key, google_apps_domain, self.viewer_email))

    namespace_manager.set_namespace(old_namespace)

    return token

  def get_key_preview(self, google_apps_domain, file_id):
    key = sateraito_func.randomString()

    memcache_key = 'key_priview_v1_' + key + '&g=2'
    memcache.set(memcache_key, {
      'file_id': file_id,
    }, time=60)
    return key

  def check_key_preview(self, google_apps_domain, file_id, key):
    memcache_key = 'key_priview_v1_' + key + '&g=2'
    data = memcache.get(memcache_key)
    if data is None:
      return False

    if 'file_id' in data and data['file_id'] == file_id:
      return True

    return False

  def get_preview_url(self, google_apps_domain, app_id, file_id, screen, admin_mode):
    key = self.get_key_preview(google_apps_domain, file_id)
    ot_token = self.getOneTimeToken(google_apps_domain)

    method = 'previewattachedfile'
    if admin_mode:
      method = 'previewattachedfileadmin'

    return u"{0}/{1}/{2}/attach/{3}?file_id={4}&key={5}&screen={6}&ot_token={7}" \
      .format(sateraito_func.getMySiteURL(google_apps_domain, request.url), google_apps_domain, app_id, method, file_id, key, screen, ot_token)

  def open_previewer(self, google_apps_domain, app_id, file, screen, admin_mode, hl=sateraito_inc.DEFAULT_LANGUAGE):
    if hl is None or hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE
    if file['mime_type'] and (file['mime_type'].lower().startswith('image/') or file['mime_type'].lower() == 'application/pdf'):
      return False

    preview_option = None
    domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
    if 'attached_file_viewer_type' in domain_dict:
      preview_option = domain_dict['attached_file_viewer_type']

    if preview_option not in ['GOOGLEDRIVEVIEWER', 'OFFICEVIEWER', 'SATERAITOVIEWER']:
      preview_option = 'GOOGLEDRIVEVIEWER'

    if not sateraito_func.checkOpenAsGoogleDocViewer(google_apps_domain, file['mime_type']):
      return False

    preview_url = self.get_preview_url(google_apps_domain, app_id, file['file_id'], screen, admin_mode)
    logging.info("preview_url: " + str(preview_url))
    previewer = 'https://drive.google.com/viewer?' + urllib.parse.urlencode({'hl': hl, 'url': preview_url})
    if preview_option == 'OFFICEVIEWER':
      previewer = 'https://view.officeapps.live.com/op/view.aspx?' + urllib.parse.urlencode({'src': preview_url})

    logging.info('previewer:' + previewer)
    # template = jinja_environment.get_template('open_viewer.html')
    # self.response.out.write(template.render({
    #   'previewer': previewer,
    #   'locale': hl
    # }))

    template_filename = sateraito_func.convertTemplateFileName('open_viewer.html')
    return render_template(template_filename, **{'previewer': previewer, 'locale': hl})

  def downloadFile(self, google_apps_domain, app_id, viewer_email, viewer_user_id, file_id, inline=False, screen='', do_not_log_operation=False,
                   admin_mode=False, action='', lang=sateraito_inc.DEFAULT_LANGUAGE):
    """
    Args:
      google_apps_domain: string
      app_id: string
      viewer_email: string
      viewer_user_id: string
      file_id: string
      inline: boolean ... for PDF inline showing in browser or inline image file showing
      screen: string ... for operation log
      do_not_log_operation: boolean
      admin_mode: boolean
      action: string
      lang: string
    """

    my_lang = sateraito_func.MyLang(lang)

    # get file
    doc_dict = sateraito_db.FileflowDoc.getDict(file_id)
    if doc_dict is None:
      logging.warn('file_id ' + str(file_id) + ' not found in FileflowDoc')
      return make_response('', 404)
    if doc_dict['del_flag'] and not admin_mode:
      logging.warn('file_id ' + str(file_id) + ' deleted in FileflowDoc')
      return make_response('', 404)

    file_id = doc_dict['file_id']
    # check folder priv for download
    #
    if doc_dict is not None and doc_dict['folder_code'] is not None:
      if admin_mode:
        # no priv check if admin_mode
        pass
      else:
        # step1.
        user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(viewer_email, auto_create=True)
        is_downloadable = sateraito_db.DocFolder.isDownloadableFolder(doc_dict['folder_code'], user_accessible_info_dict, google_apps_domain)

        # step2. check accessible in doc
        is_accessible_doc = False
        if doc_dict['publish_flag']:
          is_accessible_doc = sateraito_db.WorkflowDoc.isAccessibleDoc(doc_dict['workflow_doc_id'], viewer_email, user_accessible_info_dict)
        else:
          is_accessible_doc = True

        logging.info('##### is_downloadable=' + str(is_downloadable))
        if not is_downloadable or not is_accessible_doc:
          logging.warn('have no priv to download file file_id=' + file_id + ' folder_code=' + doc_dict['folder_code'])

          if not do_not_log_operation:
            # logging
            author_name = sateraito_func.getUserName(google_apps_domain, self.viewer_email)
            workflow_doc_dict = sateraito_db.WorkflowDoc.getDict(doc_dict['workflow_doc_id'])
            folder_dict = sateraito_db.DocFolder.getDict(doc_dict['folder_code'])

            detail = my_lang.getMsg('MSG_DETAIL_DOWNLOAD_FILE_PRI_FOLDER_FAILED').format(author_name, doc_dict['file_name'], workflow_doc_dict['title'], folder_dict['full_path_folder'])
            sateraito_db.OperationLog.addLogForFile(viewer_user_id, viewer_email, sateraito_db.OPERATION_DOWNLOAD_FILE, screen, file_id, doc_dict['workflow_doc_id'], detail=detail)
          return

    attached_by_user_email = doc_dict['attached_by_user_email']

    logging.info('viewer_email=' + viewer_email)
    logging.info('attached_by_user_email=' + attached_by_user_email)

    file_name = doc_dict['file_name']
    mime_type = doc_dict['mime_type']
    logging.info('file_name:' + str(file_name))
    logging.info('mime_type:' + str(mime_type))

    if not mime_type or mime_type == '' or mime_type == 'application/octet-stream':
      mime_type_guess, encoding = mimetypes.guess_type(file_name)
      logging.info(f'mimetypes.guess_type => mime_type_guess={mime_type_guess} encoding={encoding}')
      if mime_type_guess:
        mime_type = mime_type_guess

    if action == 'view':
      open_previewer = self.open_previewer(google_apps_domain, app_id, doc_dict, screen=screen, admin_mode=admin_mode, hl=lang)
      if open_previewer is not False:
        return open_previewer

    if viewer_email == attached_by_user_email or sateraito_func.isOkToAccessDocDict(viewer_email, doc_dict, google_apps_domain, app_id):
      try:
        browser_name = httpagentparser.detect(request.user_agent)['browser']['name']
      except Exception as instance:
        logging.error('useragent=' + str(request.user_agent))
        logging.error(str(instance))
        browser_name = ''

      logging.info('browser_name=' + str(browser_name))
      if browser_name == 'Microsoft Internet Explorer':
        logging.info('for IE')
        # filename = urllib.parse.parse.quote(str(file_name).encode('utf8'))
        self.setResponseHeader('Cache-Control', 'public')
        if inline:
          self.setResponseHeader('Content-Disposition', self.createContentDisposition(file_name, type='inline'))  # 'inline; filename="' + str(filename) + '"')
        else:
          self.setResponseHeader('Content-Disposition', self.createContentDisposition(file_name, type='attachment'))  # 'attachment; filename="' + str(filename) + '"')
        self.setResponseHeader('Content-Type', str(mime_type) + '; charset=utf-8')
      else:
        # for other browser
        logging.info('for other browser')
        # filename = base64.b64encode(str(file_name).encode('utf8'))
        self.setResponseHeader('Cache-Control', 'public')
        if inline:
          self.setResponseHeader('Content-Disposition', self.createContentDispositionUtf8(file_name, type='inline'))  # 'inline; filename="=?utf-8?B?' + str(filename) + '?="')
        else:
          self.setResponseHeader('Content-Disposition', self.createContentDispositionUtf8(file_name, type='attachment'))  # 'attachment; filename="=?utf-8?B?' + str(filename) + '?="')
        self.setResponseHeader('Content-Type', str(mime_type) + '; charset=utf-8')

      if do_not_log_operation or doc_dict is None:
        # doc is None --> user is creating new doc, download operation should not be logged
        pass
      else:
        # download operation logging
        workflow_doc_dict = sateraito_db.WorkflowDoc.getDict(doc_dict['workflow_doc_id'])
        if workflow_doc_dict is not None:
          author_name = sateraito_func.getUserName(google_apps_domain, self.viewer_email)

          detail = my_lang.getMsg('MSG_DETAIL_DOWNLOAD_FILE_SUCCESS').format(author_name, doc_dict['file_name'], workflow_doc_dict['title'])
          sateraito_db.OperationLog.addLogForFile(viewer_user_id, viewer_email, sateraito_db.OPERATION_DOWNLOAD_FILE, screen, file_id, doc_dict['workflow_doc_id'], detail=detail)

      if 'cloud_storage' in doc_dict and doc_dict['cloud_storage']:
        blob_key = doc_dict['blob_key_cloud']
        logging.info("blob_key_cloud=%s" % blob_key)
      elif 'blob_key' in doc_dict and doc_dict['blob_key']:
        blob_key = doc_dict['blob_key']
        logging.info("blob_key=%s" % blob_key)
      else:
        return make_response('', 404)

      sateraito_func.loggingRuntimeStatus()
      logging.info("send_blob_file")
      return self.send_blob_file(self.send_blob, blob_key, content_type=mime_type)
    else:
      logging.warn('not ok to access file')

      if not do_not_log_operation:
        # logging
        author_name = sateraito_func.getUserName(google_apps_domain, self.viewer_email)
        workflow_doc_dict = sateraito_db.WorkflowDoc.getDict(doc_dict['workflow_doc_id'])

        detail = my_lang.getMsg('MSG_DETAIL_DOWNLOAD_FILE_PRI_DOC_FAILED').format(author_name, doc_dict['file_name'], workflow_doc_dict['title'])
        sateraito_db.OperationLog.addLogForFile(viewer_user_id, viewer_email, sateraito_db.OPERATION_DOWNLOAD_FILE, screen, file_id, doc_dict['workflow_doc_id'], detail=detail)

      return make_response('', 403)

class DownloadAttachedFile(_DownloadAttachedFile):
  """ download attached file
    Token version
  """

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check token
    if not self.checkToken(google_apps_domain):
      return
    # get parameter
    action = self.request.get('action', '')
    file_id = self.request.get('file_id')
    inline_raw = self.request.get('inline')
    screen = self.request.get('screen')
    inline = False
    if inline_raw == '1':
      inline = True

    # download file
    return self.downloadFile(google_apps_domain, app_id, self.viewer_email, self.viewer_user_id, file_id, inline=inline, screen=screen, action=action)

class OidDownloadAttachedFile(_DownloadAttachedFile, sateraito_page._OidBasePage):
  """ download attached file
    OpenID version
  """

  def doAction(self, google_apps_domain, app_id, file_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return

    # multi-domain check
    if not sateraito_func.isOauth2Domain(google_apps_domain):
      multi_domain_setting = sateraito_func.isMultiDomainSetting(google_apps_domain)
    else:
      multi_domain_setting = False

    if multi_domain_setting:
      target_tenant_or_domain = self.request.get('target_tenant_or_domain')
      if target_tenant_or_domain is None or target_tenant_or_domain == '':
        # check login
        is_ok, body_for_not_ok = self.oidAutoLogin(google_apps_domain, is_multi_domain=True)
        if not is_ok:
          return body_for_not_ok
      else:
        # check login
        is_ok, body_for_not_ok = self.oidAutoLogin(target_tenant_or_domain)
        if not is_ok:
          return body_for_not_ok
    else:
      # check login
      is_ok, body_for_not_ok = self.oidAutoLogin(google_apps_domain)
      if not is_ok:
        return body_for_not_ok

    # go download
    action = self.request.get('action', '')
    screen = self.request.get('screen')
    inline_raw = self.request.get('inline')
    screen = self.request.get('screen')
    inline = False
    if inline_raw == '1':
      inline = True

    # download file
    return self.downloadFile(google_apps_domain, app_id, self.viewer_email, self.viewer_user_id, file_id, inline=inline, screen=screen, action=action)

class DownloadAttachedFileAdmin(_DownloadAttachedFile):
  """ download attached file
    Token version
  """

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check token
    if not self.checkToken(google_apps_domain):
      return
    # check admin
    if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
      return

    # get parameter
    action = self.request.get('action', '')
    file_id = self.request.get('file_id')
    inline_raw = self.request.get('inline')
    screen = self.request.get('screen')
    inline = False
    if inline_raw == '1':
      inline = True

    # download file
    return self.downloadFile(google_apps_domain, app_id, self.viewer_email, self.viewer_user_id, file_id, inline=inline, screen=screen, admin_mode=True, action=action)

class OidDownloadAttachedFileAdmin(_DownloadAttachedFile, sateraito_page._OidBasePage):
  """ download attached file
    Token version
  """

  def doAction(self, google_apps_domain, app_id, file_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return

    # multi-domain oid check
    domain = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
    if domain['multi_domain_setting']:
      target_google_apps_domain = self.request.get('target_google_apps_domain')
      if target_google_apps_domain is None or target_google_apps_domain == '':
        # check login
        is_ok, body_for_not_ok = self._OIDCAutoLogin(google_apps_domain)
        if not is_ok:
          return body_for_not_ok
      else:
        # check login
        is_ok, body_for_not_ok = self._OIDCAutoLogin(google_apps_domain)
        if not is_ok:
          return body_for_not_ok
    else:
      # check login
      is_ok, body_for_not_ok = self._OIDCAutoLogin(google_apps_domain)
      if not is_ok:
        return body_for_not_ok

    # get parameter
    action = self.request.get('action', '')
    inline_raw = self.request.get('inline')
    inline = False
    if inline_raw == '1':
      inline = True

    # download file
    return self.downloadFile(google_apps_domain, app_id, self.viewer_email, self.viewer_user_id, file_id, inline=inline, screen=sateraito_db.SCREEN_ADMIN_CONSOLE, admin_mode=True, action=action)


# ・クラス「_PreviewAttachedFile」、「PreviewAttachedFile」の実装
class _PreviewAttachedFile(_DownloadAttachedFile):
  pass

class PreviewAttachedFile(_PreviewAttachedFile):
  """ download attached file for preview
    OneTimeToken version
  """

  def process(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # get parameter
    file_id = self.request.get('file_id')
    key = self.request.get('key')

    if not self.check_key_preview(google_apps_domain, file_id, key):
      logging.info(403)
      return

    if not self.checkOneTimeToken(google_apps_domain):
      logging.info(403)
      return

    if file_id is None or file_id == '':
      logging.warn('invalid file_id=' + str(file_id))
      return make_response('', 404)
    screen = self.request.get('screen')

    # download file
    return self.downloadFile(google_apps_domain, app_id, self.viewer_email, self.viewer_user_id, file_id, inline=True, screen=screen)

  def doAction(self, google_apps_domain, app_id):
    return self.process(google_apps_domain, app_id)

class PreviewAttachedFileAdmin(_PreviewAttachedFile):
  """ download attached file for preview
    OneTimeToken version
  """

  def process(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return

    # get parameter
    file_id = self.request.get('file_id')
    key = self.request.get('key')

    if not self.check_key_preview(google_apps_domain, file_id, key):
      logging.info(403)
      return

    if not self.checkOneTimeToken(google_apps_domain):
      logging.info(403)
      return

    # check admin
    if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
      return

    if file_id is None or file_id == '':
      logging.warn('invalid file_id=' + str(file_id))
      return make_response('', 404)

    # download file
    return self.downloadFile(google_apps_domain, app_id, self.viewer_email, self.viewer_user_id, file_id, inline=True, screen=sateraito_db.SCREEN_ADMIN_CONSOLE, admin_mode=True)

  def doAction(self, google_apps_domain, app_id):
    return self.process(google_apps_domain, app_id)


class _UpdateAttachFile(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
  def process(self, google_apps_domain, app_id):

    # get param
    ids_file_raw = self.request.get('ids_file')
    key_split_raw = self.request.get('key_split', sateraito_inc.KEY_SPLIT_RAW)
    folder_code = self.request.get('folder_code')
    workflow_doc_id = self.request.get('workflow_doc_id')

    ids_file = ids_file_raw.split(key_split_raw)
    folder_dict = sateraito_db.DocFolder.getDict(folder_code)
    if folder_dict is None:
      return json.JSONEncoder().encode({
        'status': 'error'
      })

    for file_id in ids_file:
      row = sateraito_db.FileflowDoc.getInstance(file_id)
      if row is not None:
        row.folder_code = folder_dict['folder_code']
        row.put()

    # Update logging for file
    # Get all logging of file uploaded before
    q = sateraito_db.OperationLog.query()
    q = q.filter(sateraito_db.OperationLog.workflow_doc_id == workflow_doc_id)
    for row in q.iter():
      row.folder_code = folder_dict['folder_code']
      row.folder_name = folder_dict['folder_name']
      row.put()

    # return status
    ret_obj = {
      'status': 'ok',
    }

    return json.JSONEncoder().encode(ret_obj)

class UpdateAttachFile(_UpdateAttachFile):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkGadgetRequest(google_apps_domain):
      return

    return self.process(google_apps_domain, app_id)

class UpdateAttachFileOid(_UpdateAttachFile):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkOidRequest(google_apps_domain):
      return

    return self.process(google_apps_domain, app_id)


class _DeleteListFileTemp(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
  def process(self, google_apps_domain, app_id):
    # set response header
    self.setResponseHeader('Content-Type', 'application/json')

    # get parameter
    workflow_doc_id = self.request.get('workflow_doc_id')
    key_split_raw = self.request.get('key_split_raw', sateraito_inc.KEY_SPLIT_RAW)
    list_id_file_delete_raw = self.request.get('list_id_file_delete')

    list_id_file_delete = []
    if list_id_file_delete_raw != '':
      list_id_file_delete = list_id_file_delete_raw.split(key_split_raw)

    # remove all files uploaded but not publish
    q = sateraito_db.FileflowDoc.query()
    q = q.filter(sateraito_db.FileflowDoc.workflow_doc_id == workflow_doc_id)
    # q = q.filter(sateraito_db.FileflowDoc.del_flag == False)
    q = q.filter(sateraito_db.FileflowDoc.publish_flag == False)
    q = q.filter(sateraito_db.FileflowDoc.author_email == self.viewer_email)
    for key in q.iter(keys_only=True):
      row_file = key.get()

      # Delete files
      if row_file.cloud_storage:
        blobstore.delete(row_file.blob_key_cloud)
      elif row_file.attachment_type == 'gae_blobstore':
        blobstore.delete(row_file.blob_key)

      # Delete file in Database
      row_file.key.delete()

      # size decrement
      sateraito_db.FileSizeCounterShared.decrement(row_file.file_size)

    # revert deleted files
    for file_id in list_id_file_delete:
      row_file = sateraito_db.FileflowDoc.getInstance(file_id)
      if row_file is not None:
        row_file.del_flag = False
        row_file.put()

    sateraito_func.updateFreeSpaceStatus(google_apps_domain)

    # export json data
    return json.JSONEncoder().encode({
      'status': 'ok'
    })

class DeleteListFileTemp(_DeleteListFileTemp):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkGadgetRequest(google_apps_domain):
      return

    return self.process(google_apps_domain, app_id)

class DeleteListFileTempOid(_DeleteListFileTemp):

  def doAction(self, google_apps_domain, app_id):
    # set namespace
    if not self.setNamespace(google_apps_domain, app_id):
      return
    # check request
    if not self.checkOidRequest(google_apps_domain):
      return

    return self.process(google_apps_domain, app_id)


class TqCheckFileToTextResult(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

  def doAction(self, tenant_or_domain, app_id):
    # check retry count
    retry_cnt = self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']
    logging.info('retry_cnt=' + str(retry_cnt))
    if retry_cnt is not None:
      if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
        logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
        return

    # set namespace
    if not self.setNamespace(tenant_or_domain, app_id):
      return

    # get params
    doc_id = self.request.get('doc_id')
    logging.info('doc_id=' + str(doc_id))

    file_id = self.request.get('file_id')
    logging.info('file_id=' + str(file_id))

    viewer_email = self.request.get('viewer_email')
    logging.info('viewer_email=' + str(viewer_email))

    num_retry = 0
    num_retry_raw = self.request.get('num_retry')
    if str(num_retry_raw).isdigit():
      num_retry = int(num_retry_raw)

    # get workflow doc
    doc_row = sateraito_db.WorkflowDoc.getInstance(doc_id)
    if doc_row is None:
      logging.error('Not found doc to convert file to text search')
      return make_response('', 200)

    # check result
    row_fq = sateraito_db.FileToTextQueue.getInstance(file_id)
    if row_fq is None:
      logging.error('Not found FileToTextQueue: ' + file_id)
      return make_response('', 200)

    url_to_post = 'https://' + sateraito_inc.QUEUE_SERVER + '/a/' + sateraito_inc.QUEUE_SERVER_TENANT_FOR_FILE_TEXT_SEARCH + '/api/public/filetextsearch/get'
    payload = {
      'api_key': sateraito_inc.QUEUE_SERVER_API_KEY_FOR_FILE_TEXT_SEARCH,
      'token': row_fq.api_token,
    }
    result = urlfetch.fetch(
      url=url_to_post,
      payload=urllib.parse.urlencode(payload),
      method=urlfetch.POST,
      deadline=30
    )
    logging.info('result.status_code=' + str(result.status_code) + ' result.content=' + str(result.content))
    if result.status_code == 200:
      # create queue data
      logging.info('** status_code is 200')
      result_dict = json.JSONDecoder().decode(result.content.decode())
      if result_dict.get('code') == 0:
        # update status if chenged
        status = result_dict.get('status')
        logging.info('** code is 0 status=' + str(status))
        # update and save status
        row_fq.status = status
        row_fq.status_date = result_dict.get('status_date', '')
        row_fq.status_message = result_dict.get('status_message', '')
        # row_fq.put() --> put after
        if status == FILE_TO_TEXT_API_STATUS_SUCCESS:

          # succeeded case

          # need store converted text
          row_af = sateraito_db.FileflowDoc.getInstance(file_id)
          if row_af is None:
            logging.info('file deleted file_id=' + str(file_id))
          else:
            try:
              # row_af.converted_text = result_dict.get('result_text', '')
              row_af.convert_result = 'succeeded'
              row_af.put()
              row_af.saveConvertedText(result_dict.get('result_text', ''))
              time.sleep(1)

              sateraito_func.rebuildTextSearchIndexDoc(doc_row)

            except BaseException as e:
              logging.error('failed to save converted text:error: class name:' + e.__class__.__name__ + ' message=' + str(e))
              row_af = sateraito_db.FileflowDoc.getInstance(file_id)
              if row_af is None:
                logging.info('file deleted file_id=' + str(file_id))
              else:
                row_af.convert_result = 'convert ok but failed to save: ' + str(e)
                row_af.put()
        elif status == FILE_TO_TEXT_API_STATUS_FAILED:

          # failed case

          logging.error('failed to convert file_id=' + str(file_id))
          row_af = sateraito_db.FileflowDoc.getInstance(file_id)
          if row_af is None:
            logging.info('file deleted file_id=' + str(file_id))
          else:
            row_af.convert_result = 'failed to convert'
            row_af.put()
        else:

          # processing or queued case

          logging.debug('need retry num_retry=' + str(num_retry))
          # need retry
          if num_retry > 15:
            # 10 time retry failed
            logging.error('15 time retry failed')
            row_af = sateraito_db.FileflowDoc.getInstance(file_id)
            if row_af is None:
              logging.info('file deleted file_id=' + str(file_id))
            else:
              row_af.convert_result = '15 time retry failed'
              row_af.put()
            # save error message to queue data
            row_fq.queue_status = '15 time retry failed'
          # row_fq.put()
          else:
            row_fq.queue_status = 'retrying num_retry=' + str(num_retry)
            # go retry
            time_interval = 10 + (sateraito_func.timeToSleep(num_retry, max_interval=(2 * 60 * 60), hard_sleep=True))  # max 2 hours interval
            logging.debug('time_interval=' + str(time_interval))
            shared.attach_shared.checkFileToTextResult(tenant_or_domain, app_id, doc_id, file_id, viewer_email, num_retry=(num_retry + 1), countdown=time_interval)
        # update queue
        row_fq.put()

      else:
        logging.info('** code is NOT 0')
    else:
      # error
      logging.error('result.status_code=' + str(result.status_code) + ' result.content=' + str(result.content))

    return make_response('', 200)


class TqRegisterFileToTextServer(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

  def doAction(self, tenant_or_domain, app_id):
    # check retry count
    retry_cnt = self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']
    logging.info('retry_cnt=' + str(retry_cnt))
    if retry_cnt is not None:
      if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
        logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
        return

    # set namespace
    if not self.setNamespace(tenant_or_domain, app_id):
      return

    # get params
    doc_id = self.request.get('doc_id')
    logging.info('doc_id=' + str(doc_id))

    file_id = self.request.get('file_id')
    logging.info('file_id=' + str(file_id))

    file_name = self.request.get('file_name')
    logging.info('file_name=' + str(file_name))

    viewer_email = self.request.get('viewer_email')
    logging.info('viewer_email=' + str(viewer_email))

    # go kick
    shared.attach_shared.kickFileToTextServer(tenant_or_domain, app_id, doc_id, file_id, viewer_email)

    return make_response('', 200)


def add_url_rules(app):
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/getattachuploadurl',
                   view_func=GetUploadUrl.as_view('AttachGetUploadUrl'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/attachupload',
                   view_func=UploadHandler.as_view('AttachUploadHandler'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/fileupload',
                   view_func=FileUpload.as_view('AttachFileUpload'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/checkissamefileexists',
                   view_func=CheckIsSameFileExists.as_view('AttachCheckIsSameFileExists'))

  app.add_url_rule('/<string:tenant_or_domain>/<string:app_id>/attach/tq/checkfiletotextresult',
                   view_func=TqCheckFileToTextResult.as_view('AttachTqCheckFileToTextResult'))

  app.add_url_rule('/<string:tenant_or_domain>/<string:app_id>/attach/tq/registerfiletotextserver',
                   view_func=TqRegisterFileToTextServer.as_view('AttachTqRegisterFileToTextServer'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/get-by-workflow-doc-id',
                   view_func=GetByWorkflowDocID.as_view('AttachGetByWorkflowDocID'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/oid/get-by-workflow-doc-id',
                   view_func=GetByWorkflowDocIDOid.as_view('AttachGetByWorkflowDocIDOid'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/get-by-workflow-doc-id-admin',
                   view_func=GetByWorkflowDocIDAdmin.as_view('AttachGetByWorkflowDocIDAdmin'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/oid/get-by-workflow-doc-id-admin',
                   view_func=GetByWorkflowDocIDAdminOid.as_view('AttachGetByWorkflowDocIDAdminOid'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/delete-file-admin',
                   view_func=DeleteFileAdmin.as_view('AttachDeleteFileAdmin'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/oid/delete-file-admin',
                   view_func=DeleteFileAdminOid.as_view('AttachDeleteFileAdminOid'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/delete-file',
                   view_func=DeleteFile.as_view('AttachDeleteFile'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/oid/delete-file',
                   view_func=DeleteFileOid.as_view('AttachDeleteFileOid'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/get-my-file-shared',
                   view_func=GetMyFileShared.as_view('AttachGetMyFileShared'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/oid/get-my-file-shared',
                   view_func=GetMyFileSharedOid.as_view('AttachGetMyFileSharedOid'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/downloadattachedfile',
                   view_func=DownloadAttachedFile.as_view('AttachDownloadAttachedFile'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/downloadattachedfileadmin',
                   view_func=DownloadAttachedFileAdmin.as_view('AttachDownloadAttachedFileAdmin'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/oid/downloadattachedfile/<string:file_id>',
                   view_func=OidDownloadAttachedFile.as_view('AttachOidDownloadAttachedFile'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/oid/downloadattachedfileadmin/<string:file_id>',
                   view_func=OidDownloadAttachedFileAdmin.as_view('AttachOidDownloadAttachedFileAdmin'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/previewattachedfile',
                   view_func=PreviewAttachedFile.as_view('AttachPreviewAttachedFile'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/previewattachedfileadmin',
                   view_func=PreviewAttachedFileAdmin.as_view('AttachPreviewAttachedFileAdmin'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/updateattachfile',
                   view_func=UpdateAttachFile.as_view('AttachUpdateAttachFile'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/oid/updateattachfile',
                   view_func=UpdateAttachFileOid.as_view('AttachUpdateAttachFileOid'))

  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/deletelistfiletemp',
                   view_func=DeleteListFileTemp.as_view('AttachDeleteListFileTemp'))
  app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/attach/oid/deletelistfiletemp',
                   view_func=DeleteListFileTempOid.as_view('AttachDeleteListFileTempOid'))
