#!/usr/bin/python
# coding: utf-8

__author__ = 'Tran Minh Phuc <phuc@vnd.sateraito.co.jp>'

import sateraito_inc

def getTemplatesMailNotiFileDeleted(entry, my_lang):
	message_subject = my_lang.getMsg('FILE_DELETED_MAIL_SUBJECT').replace('%1', entry['file_name'])

	message_body = my_lang.getMsg('FILE_DELETED_MAIL_BODY')
	message_body = message_body.replace('%1', entry['file_name'])
	message_body = message_body.replace('%2', entry['folder_name'])
	message_body = message_body.replace('%3', entry['delete_user_name'])
	message_body = message_body.replace('%4', entry['delete_user_email'])
	message_body = message_body.replace('%5', entry['doc_url'])
	message_body = message_body.replace('%6', entry['title_doc'])
	if sateraito_inc.IS_FREE_EDITION:
		message_body += my_lang.getMsg('AUTO_MAIL_FOOTER')

	message_body += u'\n'
	message_body += u'\n'
	# remove \r
	message_body.replace('\r', '')

	return {
		'sender': sateraito_inc.MESSAGE_SENDER_EMAIL,
		'subject': message_subject,
		'to': entry['to'],
		'cc': entry['cc'],
		'body': message_body
	}

def getTemplatesMailNotiFileUploaded(entry, my_lang):
	message_subject = my_lang.getMsg('FILE_UPLOADED_MAIL_SUBJECT').replace('%1', entry['file_name'])

	message_body = my_lang.getMsg('FILE_UPLOADED_MAIL_BODY')
	message_body = message_body.replace('%1', entry['file_name'])
	message_body = message_body.replace('%2', entry['folder_name'])
	message_body = message_body.replace('%3', entry['upload_user_name'])
	message_body = message_body.replace('%4', entry['upload_user_email'])
	message_body = message_body.replace('%5', entry['doc_url'])
	message_body = message_body.replace('%6', entry['title_doc'])
	if sateraito_inc.IS_FREE_EDITION:
		message_body += my_lang.getMsg('AUTO_MAIL_FOOTER')

	message_body += u'\n'
	message_body += u'\n'
	# remove \r
	message_body.replace('\r', '')

	return {
		'sender': sateraito_inc.MESSAGE_SENDER_EMAIL,
		'subject': message_subject,
		'to': entry['to'],
		'cc': entry['cc'],
		'body': message_body
	}

def getTemplatesMailNotiHasAccessibleDoc(entry, my_lang):
	message_subject = my_lang.getMsg('HAS_NEW_DOC_ACCESSIBLE_MAIL_SUBJECT').replace('%1', entry['title_doc'])

	message_body = my_lang.getMsg('HAS_NEW_DOC_ACCESSIBLE_MAIL_BODY')
	message_body = message_body.replace('%1', entry['title_doc'])
	message_body = message_body.replace('%2', entry['doc_url'])
	message_body = message_body.replace('%3', entry['folder_save'])
	message_body = message_body.replace('%4', entry['author_user_name'])
	message_body = message_body.replace('%5', entry['author_user_email'])
	if sateraito_inc.IS_FREE_EDITION:
		message_body += my_lang.getMsg('AUTO_MAIL_FOOTER')

	message_body += u'\n'
	message_body += u'\n'
	# remove \r
	message_body.replace('\r', '')

	return {
		'sender': sateraito_inc.MESSAGE_SENDER_EMAIL,
		'subject': message_subject,
		'to': entry['to'],
		'cc': entry['cc'],
		'body': message_body
	}

def getTemplatesMailNotiHasAccessibleDocUpdate(entry, my_lang):
	message_subject = my_lang.getMsg('HAS_DOC_ACCESSIBLE_UPDATE_MAIL_SUBJECT').replace('%1', entry['title_doc'])

	message_body = my_lang.getMsg('HAS_DOC_ACCESSIBLE_UPDATE_MAIL_BODY')
	message_body = message_body.replace('%1', entry['title_doc'])
	message_body = message_body.replace('%2', entry['doc_url'])
	message_body = message_body.replace('%3', entry['folder_save'])
	message_body = message_body.replace('%4', entry['author_user_name'])
	message_body = message_body.replace('%5', entry['author_user_email'])
	if sateraito_inc.IS_FREE_EDITION:
		message_body += my_lang.getMsg('AUTO_MAIL_FOOTER')

	message_body += u'\n'
	message_body += u'\n'
	# remove \r
	message_body.replace('\r', '')

	return {
		'sender': sateraito_inc.MESSAGE_SENDER_EMAIL,
		'subject': message_subject,
		'to': entry['to'],
		'cc': entry['cc'],
		'body': message_body
	}

def getTemplatesMailNotiHasAccessibleDocDeleted(entry, my_lang):
	message_subject = my_lang.getMsg('HAS_DOC_ACCESSIBLE_DELETED_MAIL_SUBJECT').replace('%1', entry['title_doc'])

	message_body = my_lang.getMsg('HAS_DOC_ACCESSIBLE_DELETED_MAIL_BODY')
	message_body = message_body.replace('%1', entry['title_doc'])
	message_body = message_body.replace('%2', entry['folder_save'])
	message_body = message_body.replace('%3', entry['author_user_name'])
	message_body = message_body.replace('%4', entry['author_user_email'])
	if sateraito_inc.IS_FREE_EDITION:
		message_body += my_lang.getMsg('AUTO_MAIL_FOOTER')

	message_body += u'\n'
	message_body += u'\n'
	# remove \r
	message_body.replace('\r', '')

	return {
		'sender': sateraito_inc.MESSAGE_SENDER_EMAIL,
		'subject': message_subject,
		'to': entry['to'],
		'cc': entry['cc'],
		'body': message_body
	}
