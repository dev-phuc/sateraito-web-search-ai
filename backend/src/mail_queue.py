#!/usr/bin/python
# coding: utf-8

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'

from flask import render_template, request, make_response
import sateraito_logger as logging
import json

from google.appengine.api import taskqueue

import sateraito_inc
import sateraito_db
import sateraito_func
import sateraito_page
import sateraito_mail
import template_mail

'''
mail_queue.py

@since: 2012-02-19
@version: 2013-08-30
@author: Akitoshi Abe
'''


def sendUploadedNoticeMail(folder_code, list_file_id_new, list_file_name_new, workflow_doc_id, doc_url, upload_user_email, upload_user_name, google_apps_domain):
  folder_dict = sateraito_db.DocFolder.getDict(folder_code)
  doc_dict = sateraito_db.WorkflowDoc.getDict(workflow_doc_id)

  if len(folder_dict['notice_mails']) == 0:
    return
  for notice_mail in folder_dict['notice_mails']:
    if notice_mail is None or notice_mail == '':
      continue

    # bcc
    email_recipient_bcc = ''
    # to
    to = str(notice_mail).lower()
    if not sateraito_func.isMailAddress(to):
      continue

    # language ... if no user info found, set to default language(Japanese)
    user_language = sateraito_db.UserInfo.getUserLanguage(to, hl=sateraito_inc.DEFAULT_LANGUAGE)
    my_lang = sateraito_func.MyLang(user_language)

    template = template_mail.getTemplatesMailNotiFileUploaded({
      'to': to,
      'cc': '',
      'title_doc': doc_dict['title'],
      'doc_url': doc_url,
      'file_name': ', '.join(list_file_name_new),
      'folder_name': folder_dict['full_path_folder'],
      'upload_user_name': upload_user_name,
      'upload_user_email': upload_user_email,
    }, my_lang)

    addQueue2(
      template['sender'],
      template['subject'],
      template['to'],
      template['cc'],
      email_recipient_bcc,
      template['body'],
      upload_user_email
    )

def sendDeletedNoticeMail(folder_code, list_file_id_new, list_file_name_new, workflow_doc_id, doc_url, delete_user_email, delete_user_name, google_apps_domain):

  folder_dict = sateraito_db.DocFolder.getDict(folder_code)
  doc_dict = sateraito_db.WorkflowDoc.getDict(workflow_doc_id)
  if len(folder_dict['notice_mails']) == 0:
    return
  for notice_mail in folder_dict['notice_mails']:
    if notice_mail is None or notice_mail == '':
      continue

    # bcc
    email_recipient_bcc = ''
    # to
    to = str(notice_mail).lower()
    if not sateraito_func.isMailAddress(to):
      continue

    # language ... if no user info found, set to default language(Japanese)
    user_language = sateraito_db.UserInfo.getUserLanguage(to, hl=sateraito_inc.DEFAULT_LANGUAGE)
    my_lang = sateraito_func.MyLang(user_language)

    template = template_mail.getTemplatesMailNotiFileDeleted({
      'to': to,
      'cc': '',
      'title_doc': doc_dict['title'],
      'doc_url': doc_url,
      'file_name': ', '.join(list_file_name_new),
      'folder_name': folder_dict['full_path_folder'],
      'delete_user_name': delete_user_name,
      'delete_user_email': delete_user_email,
    }, my_lang)

    addQueue2(
      template['sender'],
      template['subject'],
      template['to'],
      template['cc'],
      email_recipient_bcc,
      template['body'],
      delete_user_email
    )

def sendNoticeMailHasNoticeDoc(workflow_doc_id, doc_url, folder_code, author_user_email, author_user_name, google_apps_domain, app_id):
  doc_dict = sateraito_db.WorkflowDoc.getDict(workflow_doc_id)
  folder_dict = sateraito_db.DocFolder.getDict(folder_code)

  if doc_dict['author_email'] not in doc_dict['notice_users']:
    doc_dict['notice_users'].append(doc_dict['author_email'])

  if doc_dict['author_email'] != author_user_email and author_user_email not in doc_dict['notice_users']:
    doc_dict['notice_users'].append(author_user_email)

  doc_dict['notice_users'] = list(set(doc_dict['notice_users']))  # remove email duplicate

  for notice_mail in doc_dict['notice_users']:
    if notice_mail is None or notice_mail == '':
      continue

    # bcc
    email_recipient_bcc = ''
    # to
    to = str(notice_mail).lower()
    if not sateraito_func.isMailAddress(to):
      continue

    # language ... if no user info found, set to default language(Japanese)
    user_language = sateraito_db.UserInfo.getUserLanguage(to, hl=sateraito_inc.DEFAULT_LANGUAGE)
    my_lang = sateraito_func.MyLang(user_language)
    template = template_mail.getTemplatesMailNotiHasAccessibleDoc({
      'to': to,
      'cc': '',
      'title_doc': doc_dict['title'],
      'folder_save': folder_dict['full_path_folder'],
      'doc_url': doc_url,
      'author_user_email': author_user_email,
      'author_user_name': author_user_name,
    }, my_lang)

    addQueue2(
      template['sender'],
      template['subject'],
      template['to'],
      template['cc'],
      email_recipient_bcc,
      template['body'],
      author_user_email
    )

def sendNoticeMailHasNoticeDocUpdate(workflow_doc_id, doc_url, folder_code, author_user_email, author_user_name, google_apps_domain, app_id):
  doc_dict = sateraito_db.WorkflowDoc.getDict(workflow_doc_id)
  folder_dict = sateraito_db.DocFolder.getDict(folder_code)

  if doc_dict['author_email'] not in doc_dict['notice_users']:
    doc_dict['notice_users'].append(doc_dict['author_email'])

  if doc_dict['author_email'] != author_user_email and author_user_email not in doc_dict['notice_users']:
    doc_dict['notice_users'].append(author_user_email)

  doc_dict['notice_users'] = list(set(doc_dict['notice_users']))  # remove email duplicate

  for notice_mail in doc_dict['notice_users']:
    if notice_mail is None or notice_mail == '':
      continue

    # bcc
    email_recipient_bcc = ''
    # to
    to = str(notice_mail).lower()
    if not sateraito_func.isMailAddress(to):
      continue

    # language ... if no user info found, set to default language(Japanese)
    user_language = sateraito_db.UserInfo.getUserLanguage(to, hl=sateraito_inc.DEFAULT_LANGUAGE)
    my_lang = sateraito_func.MyLang(user_language)

    template = template_mail.getTemplatesMailNotiHasAccessibleDocUpdate({
      'to': to,
      'cc': '',
      'title_doc': doc_dict['title'],
      'folder_save': folder_dict['full_path_folder'],
      'doc_url': doc_url,
      'author_user_email': author_user_email,
      'author_user_name': author_user_name,
    }, my_lang)

    addQueue2(
      template['sender'],
      template['subject'],
      template['to'],
      template['cc'],
      email_recipient_bcc,
      template['body'],
      author_user_email
    )

def sendNoticeMailHasNoticeDocDelete(workflow_doc_id, doc_url, folder_code, author_user_email, author_user_name, google_apps_domain, app_id):
  doc_dict = sateraito_db.WorkflowDoc.getDict(workflow_doc_id)
  folder_dict = sateraito_db.DocFolder.getDict(folder_code)

  if doc_dict['author_email'] not in doc_dict['notice_users']:
    doc_dict['notice_users'].append(doc_dict['author_email'])

  if doc_dict['author_email'] != author_user_email and author_user_email not in doc_dict['notice_users']:
    doc_dict['notice_users'].append(author_user_email)

  doc_dict['notice_users'] = list(set(doc_dict['notice_users']))  # remove email duplicate

  for notice_mail in doc_dict['notice_users']:
    if notice_mail is None or notice_mail == '':
      continue

    # bcc
    email_recipient_bcc = ''
    # to
    to = str(notice_mail).lower()
    if not sateraito_func.isMailAddress(to):
      continue

    # language ... if no user info found, set to default language(Japanese)
    user_language = sateraito_db.UserInfo.getUserLanguage(to, hl=sateraito_inc.DEFAULT_LANGUAGE)
    my_lang = sateraito_func.MyLang(user_language)

    template = template_mail.getTemplatesMailNotiHasAccessibleDocDeleted({
      'to': to,
      'cc': '',
      'title_doc': doc_dict['title'],
      'folder_save': folder_dict['full_path_folder'],
      'doc_url': doc_url,
      'author_user_email': author_user_email,
      'author_user_name': author_user_name,
    }, my_lang)

    addQueue2(
      template['sender'],
      template['subject'],
      template['to'],
      template['cc'],
      email_recipient_bcc,
      template['body'],
      author_user_email
    )

def addQueue2(sender, subject, to, cc=None, bcc=None, body=None, reply_to=None):
  # register task queue to send email
  # mail_q = taskqueue.Queue('mail-send-queue')
  mail_q = taskqueue.Queue('default')
  mail_t = taskqueue.Task(
    url='/tq/sendmail2',
    params={
      'sender': sender,
      'subject': subject,
      'to': to,
      'body': body,
      'cc': cc,
      'bcc': bcc,
      'reply_to': reply_to,
    },
    target=sateraito_func.getBackEndsModuleNameDeveloper('default'),
  )
  mail_q.add(mail_t)


class TqSendMail2(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
  """ Sending email
	"""
  def doAction(self):
    # check retry count
    retry_cnt = self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']
    logging.info('retry_cnt=' + str(retry_cnt))
    if retry_cnt is not None:
      if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
        logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
        return

    sender = self.request.get('sender')
    subject = self.request.get('subject')
    to = self.request.get('to')
    body = self.request.get('body')
    cc = self.request.get('cc')
    bcc = self.request.get('bcc')
    reply_to = self.request.get('reply_to')

    # logging.info(sender)
    # logging.info(subject)
    # logging.info(to)
    # logging.info(body)
    # logging.info(cc)
    # logging.info(bcc)
    # logging.info(reply_to)

    sateraito_mail.sendMail(to, subject, body, is_html=True)

    return make_response('', 200)


def add_url_rules(app):
  app.add_url_rule('/tq/sendmail2', view_func=TqSendMail2.as_view('TqSendMail2'))

