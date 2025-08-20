#!/usr/bin/python
# coding: utf-8

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'

# set default encodeing to utf-8
from flask import render_template, request, make_response
import os
import json
import urllib
import base64
import time

import httpagentparser

from google.appengine.ext import ndb, blobstore
# from google.appengine.api import memcache
# from google.appengine.ext.webapp import blobstore_handlers
# from google.appengine.api import namespace_manager
# # from google.appengine.api import files # todo: edited start: tan@vn.sateraito,co,jp (version: 1)
# from google.appengine.api.urlfetch import DownloadError  # todo: edited start: tan@vn.sateraito,co,jp (version: 3)
# from google.appengine.api import taskqueue
# from google.appengine.api import app_identity
# from google.appengine.api import urlfetch
# from google.appengine.api import urlfetch_errors
from google.appengine.api import urlfetch, urlfetch_errors, taskqueue, namespace_manager

# import google.appengine.api.runtime

import sateraito_logger as logging
import sateraito_inc
import sateraito_func
import sateraito_db
import sateraito_page

'''
attach_shared.py

@since: 2017-11-27
@version: 2020-06-30
@author: Akitoshi Abe
'''

MAX_ATTACH_FILE_SIZE = 1024 * 1024 * 200  # 200MB


# def checkFileToTextResult(tenant_or_domain, app_id, doc_id, template_type, file_id, viewer_email, num_retry=0, countdown=1):
# 	queue = taskqueue.Queue('default')
# 	task = taskqueue.Task(
# 		url='/' + tenant_or_domain + '/' + app_id + '/attach/tq/checkfiletotextresult',
# 		params={
# 			'template_type': template_type,
# 			'doc_id': doc_id,
# 			'file_id': file_id,
# 			'viewer_email': viewer_email,
# 			'num_retry': str(num_retry),
# 			},
# 		target=sateraito_func.getBackEndsModuleNameDeveloper('f1process'),
# 		countdown=countdown
# 	)
# 	queue.add(task)

# from http://ebstudio.info/home/xdoc2txt.html
CONVERT_ALLOWED_EXTENTION = [
	'.rtf',
	'.pdf', '.wri',
	'.txt',
	'.csv',
	'.doc', '.docx',
	'.xls', '.xlsx',
	'.ppt', '.pptx',
	'.htm', '.html',
	'.eml',
	'.sxw', '.sxc', '.sxi', '.sxd',  # OpenOffice.org
	'.odt', '.ods', '.odp', '.odg',  # Open Document
	'.jaw', '.jtw', '.jbw', '.juw', '.jfw', '.jvw', '.jtd', '.jtt',  # Ichitaro
	'.oas', '.oa2', '.oa3',  # OASYS/Win
	'.bun',  # MATSU
	'.wj2', '.wj3', '.wk3', '.wk4', '.123',  # Lotus 123
]

def checkFileToTextResult(tenant_or_domain, app_id, doc_id, file_id, viewer_email, num_retry=0, countdown=1):
	queue = taskqueue.Queue('default')
	task = taskqueue.Task(
		url='/' + tenant_or_domain + '/' + app_id + '/attach/tq/checkfiletotextresult',
		params={
			'doc_id': doc_id,
			'file_id': file_id,
			'viewer_email': viewer_email,
			'num_retry': str(num_retry),
			},
		# target=sateraito_func.getBackEndsModuleNameDeveloper('f1process'),
		countdown=countdown
	)
	queue.add(task)


def kickFileToTextServerAsync(tenant_or_domain, app_id, doc_id, file_id, file_name, viewer_email, countdown=10):
	# @return True if file-to-text-server kicked
	logging.debug('kickFileToTextServerAsync file_name=' + str(file_name))
	# check file extension
	path, ext = os.path.splitext(file_name)
	if str(ext).lower() not in CONVERT_ALLOWED_EXTENTION:
		logging.info('ext=' + str(ext) + ' not allowed to convert')
		return False
	queue = taskqueue.Queue('default')
	task = taskqueue.Task(
		url='/' + tenant_or_domain + '/' + app_id + '/attach/tq/registerfiletotextserver',
		params={
			'doc_id': doc_id,
			'file_id': file_id,
			'file_name': file_name,
			'viewer_email': viewer_email,
			},
		target=sateraito_func.getBackEndsModuleNameDeveloper('f2process'),
		countdown=countdown,
	)
	queue.add(task)
	return True


def kickFileToTextServer(tenant_or_domain, app_id, doc_id, file_id, viewer_email):
	# use pull mode for all
	return _kickFileToTextServerPullMode(tenant_or_domain, app_id, doc_id, file_id, viewer_email)


def _kickFileToTextServerPullMode(tenant_or_domain, app_id, doc_id, file_id, viewer_email):
	logging.info('** _kickFileToTextServerPullMode')
	row_at = sateraito_db.FileflowDoc.getInstance(file_id)
	if row_at is None:
		# attached file deleted case
		logging.info('not found FileflowDoc file_id=' + str(file_id) + ' possibly deleted')
		return
	file_pull_url = row_at.createFilePullUrl(tenant_or_domain, app_id)
	time.sleep(1)  # for datastore put of createFilePullUrl
	url_to_post = 'https://' + sateraito_inc.QUEUE_SERVER + '/a/' + sateraito_inc.QUEUE_SERVER_TENANT_FOR_FILE_TEXT_SEARCH + '/api/public/filetextsearch/request'
	logging.info('url_to_post=' + str(url_to_post))
	payload = {
		'api_key': sateraito_inc.QUEUE_SERVER_API_KEY_FOR_FILE_TEXT_SEARCH,
		'data_type': 'file',
		'file_send_type': 'pull',
		'file_pull_url': file_pull_url,
	}
	logging.info('payload=' + str(payload))
	# go kick
	try:
		# set longer urlfetch timeout
		result = urlfetch.fetch(
			url=url_to_post,
			payload=urllib.parse.urlencode(payload),
			method=urlfetch.POST,
			deadline=(60 * 5),  # 5 min
		)
		logging.info('result.status_code=' + str(result.status_code) + ' result.content=' + str(result.content))
		if result.status_code == 200:
			# create queue data
			result_dict = json.JSONDecoder().decode(result.content.decode())
			if result_dict.get('code') == 0:
				# succeed
				row_q = sateraito_db.FileToTextQueue()
				row_q.doc_id = doc_id
				row_q.file_id = row_at.file_id
				row_q.api_token = result_dict.get('token')
				row_q.status = ''  # status unknown at this moment
				row_q.file_name = row_at.file_name
				row_q.put()
				checkFileToTextResult(tenant_or_domain, app_id, doc_id, row_at.file_id, viewer_email, countdown=10)
		
		else:
			# error
			logging.error('result.status_code=' + str(result.status_code) + ' result.content=' + str(result.content))
	except urlfetch_errors.PayloadTooLargeError as e:
		logging.warn('error: class name:' + e.__class__.__name__ + ' message=' + str(e))
		row_at.convert_result = 'PayloadTooLargeError: file too large'
		row_at.put()
	except urlfetch_errors.InvalidURLError as e:
		logging.warn('error: class name:' + e.__class__.__name__ + ' message=' + str(e))
		row_at.convert_result = 'InvalidURLError: Request body too large: file too large'
		row_at.put()


def _kickFileToTextServerPushMode(tenant_or_domain, app_id, doc_id, template_type, file_id, viewer_email):
	logging.info('** _kickFileToTextServerPushMode')
	row_at = sateraito_db.FileflowDoc.getInstance(file_id)

	blob_key = None
	if row_at.cloud_storage:
		blob_key = row_at.blob_key_cloud
	else:
		blob_key = row_at.blob_key

	blob_reader = blobstore.BlobReader(blob_key, buffer_size=(1024 * 1024 * 2))  # set buffer size to 2MB: for big size file
	url_to_post = 'https://' + sateraito_inc.QUEUE_SERVER + '/a/' + sateraito_inc.QUEUE_SERVER_TENANT_FOR_FILE_TEXT_SEARCH + '/api/public/filetextsearch/request'
	# create multipart/form-data
	content_type, body = sateraito_func.encode_multipart_formdata(
		[
			('api_key', sateraito_inc.QUEUE_SERVER_API_KEY_FOR_FILE_TEXT_SEARCH),
			('data_type', 'file'),
		],
		[
			('file', row_at.file_name, blob_reader.read())
		],
		row_at.mime_type)
	logging.debug('content_type=' + str(content_type))
	# logging.debug('body=' + str(body))
	# go kick
	try:
		# set longer urlfetch timeout
		result = urlfetch.fetch(
			url=url_to_post,
			payload=body,
			method=urlfetch.POST,
			headers={'Content-Type': content_type},
			deadline=(60 * 5),  # 5 min
		)
		logging.info('result.status_code=' + str(result.status_code) + ' result.content=' + str(result.content))
		if result.status_code == 200:
			# create queue data
			result_dict = json.JSONDecoder().decode(result.content.decode())
			if result_dict.get('code') == 0:
				# succeed
				row_q = sateraito_db.FileToTextQueue()
				row_q.doc_id = doc_id
				row_q.file_id = row_at.file_id
				row_q.api_token = result_dict.get('token')
				row_q.status = ''  # status unknown at this moment
				row_q.file_name = row_at.file_name
				row_q.put()
				checkFileToTextResult(tenant_or_domain, app_id, doc_id, template_type, row_at.file_id, viewer_email, countdown=10)
	
		else:
			# error
			logging.error('result.status_code=' + str(result.status_code) + ' result.content=' + str(result.content))
	except urlfetch_errors.PayloadTooLargeError as e:
		logging.warn('error: class name:' + e.__class__.__name__ + ' message=' +str(e))
		row_at.convert_result = 'PayloadTooLargeError: file too large'
		row_at.put()
	except urlfetch_errors.InvalidURLError as e:
		logging.warn('error: class name:' + e.__class__.__name__ + ' message=' +str(e))
		row_at.convert_result = 'InvalidURLError: Request body too large: file too large'
		row_at.put()


def checkFileIdsAttached(doc_id, file_ids):
	# check files
	wrong_file_ids = []
	all_ids_attached = True
	for file_id in file_ids:
		q = sateraito_db.FileflowDoc.query()
		q = q.filter(sateraito_db.FileflowDoc.workflow_doc_id == doc_id)
		q = q.filter(sateraito_db.FileflowDoc.file_id == file_id)
		key = q.get(keys_only=True)
		if key is None:
			logging.info('file_id:' + str(file_id) + ' not found')
			all_ids_attached = False
			wrong_file_ids.append(file_id)

	return all_ids_attached, wrong_file_ids


def isImageFile(attached_file):
	mime_type = str(attached_file.mime_type).lower()
	if mime_type == 'image/png':
		return True
	if mime_type == 'image/x-ms-bmp' or mime_type == 'image/bmp' or mime_type == 'image/x-bmp':
		return True
	if mime_type == 'image/jpeg':
		return True
	if mime_type == 'image/gif':
		return True

	return False


def getImageMimeTypeByExtension(file_name):
	root, ext = os.path.splitext(str(file_name).lower())
	if ext == '.gif':
		return 'image/gif'
	if ext == '.jpg' or ext == '.jpeg':
		return 'image/jpeg'
	if ext == '.png':
		return 'image/png'
	if ext == '.bmp':
		return 'image/bmp'
	return None


class SateraitoMimeType:
	types_map = []
	def __init__(self):
		self.types_map = [
			{"extension": ".3dm", "mime_type": "x-world/x-3dmf"},
			{"extension": ".3dmf", "mime_type": "x-world/x-3dmf"},
			{"extension": ".a", "mime_type": "application/octet-stream"},
			{"extension": ".a", "mime_type": "application/octet-stream"},
			{"extension": ".aab", "mime_type": "application/x-authorware-bin"},
			{"extension": ".aam", "mime_type": "application/x-authorware-map"},
			{"extension": ".aas", "mime_type": "application/x-authorware-seg"},
			{"extension": ".abc", "mime_type": "text/vnd.abc"},
			{"extension": ".acgi", "mime_type": "text/html"},
			{"extension": ".afl", "mime_type": "video/animaflex"},
			{"extension": ".ai", "mime_type": "application/postscript"},
			{"extension": ".ai", "mime_type": "application/postscript"},
			{"extension": ".aif", "mime_type": "audio/aiff"},
			{"extension": ".aif", "mime_type": "audio/x-aiff"},
			{"extension": ".aif", "mime_type": "audio/x-aiff"},
			{"extension": ".aifc", "mime_type": "audio/aiff"},
			{"extension": ".aifc", "mime_type": "audio/x-aiff"},
			{"extension": ".aifc", "mime_type": "audio/x-aiff"},
			{"extension": ".aiff", "mime_type": "audio/aiff"},
			{"extension": ".aiff", "mime_type": "audio/x-aiff"},
			{"extension": ".aiff", "mime_type": "audio/x-aiff"},
			{"extension": ".aim", "mime_type": "application/x-aim"},
			{"extension": ".aip", "mime_type": "text/x-audiosoft-intra"},
			{"extension": ".ani", "mime_type": "application/x-navi-animation"},
			{"extension": ".aos", "mime_type": "application/x-nokia-9000-communicator-add-on-software"},
			{"extension": ".aps", "mime_type": "application/mime"},
			{"extension": ".arc", "mime_type": "application/octet-stream"},
			{"extension": ".arj", "mime_type": "application/arj"},
			{"extension": ".arj", "mime_type": "application/octet-stream"},
			{"extension": ".art", "mime_type": "image/x-jg"},
			{"extension": ".asf", "mime_type": "video/x-ms-asf"},
			{"extension": ".asm", "mime_type": "text/x-asm"}, {"extension": ".asp", "mime_type": "text/asp"},
			{"extension": ".asx", "mime_type": "application/x-mplayer2"},
			{"extension": ".asx", "mime_type": "video/x-ms-asf"},
			{"extension": ".asx", "mime_type": "video/x-ms-asf-plugin"},
			{"extension": ".au", "mime_type": "audio/basic"}, {"extension": ".au", "mime_type": "audio/x-au"},
			{"extension": ".au", "mime_type": "audio/basic"},
			{"extension": ".avi", "mime_type": "application/x-troff-msvideo"},
			{"extension": ".avi", "mime_type": "video/avi"},
			{"extension": ".avi", "mime_type": "video/msvideo"},
			{"extension": ".avi", "mime_type": "video/x-msvideo"},
			{"extension": ".avi", "mime_type": "video/x-msvideo"},
			{"extension": ".avs", "mime_type": "video/avs-video"},
			{"extension": ".bat", "mime_type": "text/plain"},
			{"extension": ".bcpio", "mime_type": "application/x-bcpio"},
			{"extension": ".bcpio", "mime_type": "application/x-bcpio"},
			{"extension": ".bin", "mime_type": "application/mac-binary"},
			{"extension": ".bin", "mime_type": "application/macbinary"},
			{"extension": ".bin", "mime_type": "application/octet-stream"},
			{"extension": ".bin", "mime_type": "application/x-binary"},
			{"extension": ".bin", "mime_type": "application/x-macbinary"},
			{"extension": ".bin", "mime_type": "application/octet-stream"},
			{"extension": ".bm", "mime_type": "image/bmp"}, {"extension": ".bmp", "mime_type": "image/bmp"},
			{"extension": ".bmp", "mime_type": "image/x-windows-bmp"},
			{"extension": ".bmp", "mime_type": "image/x-ms-bmp"},
			{"extension": ".boo", "mime_type": "application/book"},
			{"extension": ".book", "mime_type": "application/book"},
			{"extension": ".boz", "mime_type": "application/x-bzip2"},
			{"extension": ".bsh", "mime_type": "application/x-bsh"},
			{"extension": ".bz", "mime_type": "application/x-bzip"},
			{"extension": ".bz2", "mime_type": "application/x-bzip2"},
			{"extension": ".c", "mime_type": "text/plain"}, {"extension": ".c", "mime_type": "text/x-c"},
			{"extension": ".c", "mime_type": "text/plain"}, {"extension": ".c++", "mime_type": "text/plain"},
			{"extension": ".cat", "mime_type": "application/vnd.ms-pki.seccat"},
			{"extension": ".cc", "mime_type": "text/plain"}, {"extension": ".cc", "mime_type": "text/x-c"},
			{"extension": ".ccad", "mime_type": "application/clariscad"},
			{"extension": ".cco", "mime_type": "application/x-cocoa"},
			{"extension": ".cdf", "mime_type": "application/cdf"},
			{"extension": ".cdf", "mime_type": "application/x-cdf"},
			{"extension": ".cdf", "mime_type": "application/x-netcdf"},
			{"extension": ".cdf", "mime_type": "application/x-cdf"},
			{"extension": ".cdf", "mime_type": "application/x-netcdf"},
			{"extension": ".cer", "mime_type": "application/pkix-cert"},
			{"extension": ".cer", "mime_type": "application/x-x509-ca-cert"},
			{"extension": ".cha", "mime_type": "application/x-chat"},
			{"extension": ".chat", "mime_type": "application/x-chat"},
			{"extension": ".class", "mime_type": "application/java"},
			{"extension": ".class", "mime_type": "application/java-byte-code"},
			{"extension": ".class", "mime_type": "application/x-java-class"},
			{"extension": ".com", "mime_type": "application/octet-stream"},
			{"extension": ".com", "mime_type": "text/plain"},
			{"extension": ".conf", "mime_type": "text/plain"},
			{"extension": ".cpio", "mime_type": "application/x-cpio"},
			{"extension": ".cpio", "mime_type": "application/x-cpio"},
			{"extension": ".cpp", "mime_type": "text/x-c"},
			{"extension": ".cpt", "mime_type": "application/mac-compactpro"},
			{"extension": ".cpt", "mime_type": "application/x-compactpro"},
			{"extension": ".cpt", "mime_type": "application/x-cpt"},
			{"extension": ".crl", "mime_type": "application/pkcs-crl"},
			{"extension": ".crl", "mime_type": "application/pkix-crl"},
			{"extension": ".crt", "mime_type": "application/pkix-cert"},
			{"extension": ".crt", "mime_type": "application/x-x509-ca-cert"},
			{"extension": ".crt", "mime_type": "application/x-x509-user-cert"},
			{"extension": ".csh", "mime_type": "application/x-csh"},
			{"extension": ".csh", "mime_type": "text/x-script.csh"},
			{"extension": ".csh", "mime_type": "application/x-csh"},
			{"extension": ".css", "mime_type": "application/x-pointplus"},
			{"extension": ".css", "mime_type": "text/css"}, {"extension": ".css", "mime_type": "text/css"},
			{"extension": ".cxx", "mime_type": "text/plain"},
			{"extension": ".dcr", "mime_type": "application/x-director"},
			{"extension": ".deepv", "mime_type": "application/x-deepv"},
			{"extension": ".def", "mime_type": "text/plain"},
			{"extension": ".der", "mime_type": "application/x-x509-ca-cert"},
			{"extension": ".dif", "mime_type": "video/x-dv"},
			{"extension": ".dir", "mime_type": "application/x-director"},
			{"extension": ".dl", "mime_type": "video/dl"}, {"extension": ".dl", "mime_type": "video/x-dl"},
			{"extension": ".dll", "mime_type": "application/octet-stream"},
			{"extension": ".doc", "mime_type": "application/msword"},
			{"extension": ".doc", "mime_type": "application/msword"},
			{"extension": ".docm", "mime_type": "application/vnd.ms-word.document.macroEnabled.12"},
			{"extension": ".docx",
			 "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
			{"extension": ".dot", "mime_type": "application/msword"},
			{"extension": ".dot", "mime_type": "application/msword"},
			{"extension": ".dotm", "mime_type": "application/vnd.ms-word.template.macroEnabled.12"},
			{"extension": ".dotx",
			 "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.template"},
			{"extension": ".dp", "mime_type": "application/commonground"},
			{"extension": ".drw", "mime_type": "application/drafting"},
			{"extension": ".dump", "mime_type": "application/octet-stream"},
			{"extension": ".dv", "mime_type": "video/x-dv"},
			{"extension": ".dvi", "mime_type": "application/x-dvi"},
			{"extension": ".dvi", "mime_type": "application/x-dvi"},
			{"extension": ".dwf", "mime_type": "drawing/x-dwf (old)"},
			{"extension": ".dwf", "mime_type": "model/vnd.dwf"},
			{"extension": ".dwg", "mime_type": "application/acad"},
			{"extension": ".dwg", "mime_type": "image/vnd.dwg"},
			{"extension": ".dwg", "mime_type": "image/x-dwg"},
			{"extension": ".dxf", "mime_type": "application/dxf"},
			{"extension": ".dxf", "mime_type": "image/vnd.dwg"},
			{"extension": ".dxf", "mime_type": "image/x-dwg"},
			{"extension": ".dxr", "mime_type": "application/x-director"},
			{"extension": ".el", "mime_type": "text/x-script.elisp"},
			{"extension": ".elc", "mime_type": "application/x-bytecode.elisp (compiled elisp)"},
			{"extension": ".elc", "mime_type": "application/x-elc"},
			{"extension": ".eml", "mime_type": "message/rfc822"},
			{"extension": ".env", "mime_type": "application/x-envoy"},
			{"extension": ".eps", "mime_type": "application/postscript"},
			{"extension": ".eps", "mime_type": "application/postscript"},
			{"extension": ".es", "mime_type": "application/x-esrehber"},
			{"extension": ".etx", "mime_type": "text/x-setext"},
			{"extension": ".etx", "mime_type": "text/x-setext"},
			{"extension": ".evy", "mime_type": "application/envoy"},
			{"extension": ".evy", "mime_type": "application/x-envoy"},
			{"extension": ".exe", "mime_type": "application/octet-stream"},
			{"extension": ".exe", "mime_type": "application/octet-stream"},
			{"extension": ".f", "mime_type": "text/plain"},
			{"extension": ".f", "mime_type": "text/x-fortran"},
			{"extension": ".f77", "mime_type": "text/x-fortran"},
			{"extension": ".f90", "mime_type": "text/plain"},
			{"extension": ".f90", "mime_type": "text/x-fortran"},
			{"extension": ".fdf", "mime_type": "application/vnd.fdf"},
			{"extension": ".fif", "mime_type": "application/fractals"},
			{"extension": ".fif", "mime_type": "image/fif"}, {"extension": ".fli", "mime_type": "video/fli"},
			{"extension": ".fli", "mime_type": "video/x-fli"},
			{"extension": ".flo", "mime_type": "image/florian"},
			{"extension": ".flx", "mime_type": "text/vnd.fmi.flexstor"},
			{"extension": ".fmf", "mime_type": "video/x-atomic3d-feature"},
			{"extension": ".for", "mime_type": "text/plain"},
			{"extension": ".for", "mime_type": "text/x-fortran"},
			{"extension": ".fpx", "mime_type": "image/vnd.fpx"},
			{"extension": ".fpx", "mime_type": "image/vnd.net-fpx"},
			{"extension": ".frl", "mime_type": "application/freeloader"},
			{"extension": ".funk", "mime_type": "audio/make"}, {"extension": ".g", "mime_type": "text/plain"},
			{"extension": ".g3", "mime_type": "image/g3fax"}, {"extension": ".gif", "mime_type": "image/gif"},
			{"extension": ".gif", "mime_type": "image/gif"}, {"extension": ".gl", "mime_type": "video/gl"},
			{"extension": ".gl", "mime_type": "video/x-gl"},
			{"extension": ".gsd", "mime_type": "audio/x-gsm"},
			{"extension": ".gsm", "mime_type": "audio/x-gsm"},
			{"extension": ".gsp", "mime_type": "application/x-gsp"},
			{"extension": ".gss", "mime_type": "application/x-gss"},
			{"extension": ".gtar", "mime_type": "application/x-gtar"},
			{"extension": ".gtar", "mime_type": "application/x-gtar"},
			{"extension": ".gz", "mime_type": "application/x-compressed"},
			{"extension": ".gz", "mime_type": "application/x-gzip"},
			{"extension": ".gzip", "mime_type": "application/x-gzip"},
			{"extension": ".gzip", "mime_type": "multipart/x-gzip"},
			{"extension": ".h", "mime_type": "text/plain"}, {"extension": ".h", "mime_type": "text/x-h"},
			{"extension": ".h", "mime_type": "text/plain"},
			{"extension": ".hdf", "mime_type": "application/x-hdf"},
			{"extension": ".hdf", "mime_type": "application/x-hdf"},
			{"extension": ".help", "mime_type": "application/x-helpfile"},
			{"extension": ".hgl", "mime_type": "application/vnd.hp-hpgl"},
			{"extension": ".hh", "mime_type": "text/plain"}, {"extension": ".hh", "mime_type": "text/x-h"},
			{"extension": ".hlb", "mime_type": "text/x-script"},
			{"extension": ".hlp", "mime_type": "application/hlp"},
			{"extension": ".hlp", "mime_type": "application/x-helpfile"},
			{"extension": ".hlp", "mime_type": "application/x-winhelp"},
			{"extension": ".hpg", "mime_type": "application/vnd.hp-hpgl"},
			{"extension": ".hpgl", "mime_type": "application/vnd.hp-hpgl"},
			{"extension": ".hqx", "mime_type": "application/binhex"},
			{"extension": ".hqx", "mime_type": "application/binhex4"},
			{"extension": ".hqx", "mime_type": "application/mac-binhex"},
			{"extension": ".hqx", "mime_type": "application/mac-binhex40"},
			{"extension": ".hqx", "mime_type": "application/x-binhex40"},
			{"extension": ".hqx", "mime_type": "application/x-mac-binhex40"},
			{"extension": ".hta", "mime_type": "application/hta"},
			{"extension": ".htc", "mime_type": "text/x-component"},
			{"extension": ".htm", "mime_type": "text/html"}, {"extension": ".htm", "mime_type": "text/html"},
			{"extension": ".html", "mime_type": "text/html"},
			{"extension": ".html", "mime_type": "text/html"},
			{"extension": ".htmls", "mime_type": "text/html"},
			{"extension": ".htt", "mime_type": "text/webviewhtml"},
			{"extension": ".htx", "mime_type": "text/html"},
			{"extension": ".ice", "mime_type": "x-conference/x-cooltalk"},
			{"extension": ".ico", "mime_type": "image/x-icon"},
			{"extension": ".idc", "mime_type": "text/plain"}, {"extension": ".ief", "mime_type": "image/ief"},
			{"extension": ".ief", "mime_type": "image/ief"}, {"extension": ".iefs", "mime_type": "image/ief"},
			{"extension": ".iges", "mime_type": "application/iges"},
			{"extension": ".iges", "mime_type": "model/iges"},
			{"extension": ".igs", "mime_type": "application/iges"},
			{"extension": ".igs", "mime_type": "model/iges"},
			{"extension": ".ima", "mime_type": "application/x-ima"},
			{"extension": ".imap", "mime_type": "application/x-httpd-imap"},
			{"extension": ".inf", "mime_type": "application/inf"},
			{"extension": ".ins", "mime_type": "application/x-internett-signup"},
			{"extension": ".ip", "mime_type": "application/x-ip2"},
			{"extension": ".isu", "mime_type": "video/x-isvideo"},
			{"extension": ".it", "mime_type": "audio/it"},
			{"extension": ".iv", "mime_type": "application/x-inventor"},
			{"extension": ".ivr", "mime_type": "i-world/i-vrml"},
			{"extension": ".ivy", "mime_type": "application/x-livescreen"},
			{"extension": ".jam", "mime_type": "audio/x-jam"},
			{"extension": ".jav", "mime_type": "text/plain"},
			{"extension": ".jav", "mime_type": "text/x-java-source"},
			{"extension": ".java", "mime_type": "text/plain"},
			{"extension": ".java", "mime_type": "text/x-java-source"},
			{"extension": ".jcm", "mime_type": "application/x-java-commerce"},
			{"extension": ".jfif", "mime_type": "image/jpeg"},
			{"extension": ".jfif", "mime_type": "image/pjpeg"},
			{"extension": ".jfif-tbnl", "mime_type": "image/jpeg"},
			{"extension": ".jpe", "mime_type": "image/jpeg"},
			{"extension": ".jpe", "mime_type": "image/pjpeg"},
			{"extension": ".jpe", "mime_type": "image/jpeg"},
			{"extension": ".jpeg", "mime_type": "image/jpeg"},
			{"extension": ".jpeg", "mime_type": "image/pjpeg"},
			{"extension": ".jpeg", "mime_type": "image/jpeg"},
			{"extension": ".jpg", "mime_type": "image/jpeg"},
			{"extension": ".jpg", "mime_type": "image/pjpeg"},
			{"extension": ".jpg", "mime_type": "image/jpeg"},
			{"extension": ".jps", "mime_type": "image/x-jps"},
			{"extension": ".js", "mime_type": "application/x-javascript"},
			{"extension": ".js", "mime_type": "application/x-javascript"},
			{"extension": ".jut", "mime_type": "image/jutvision"},
			{"extension": ".kar", "mime_type": "audio/midi"},
			{"extension": ".kar", "mime_type": "music/x-karaoke"},
			{"extension": ".ksh", "mime_type": "application/x-ksh"},
			{"extension": ".ksh", "mime_type": "text/x-script.ksh"},
			{"extension": ".ksh", "mime_type": "text/plain"},
			{"extension": ".la", "mime_type": "audio/nspaudio"},
			{"extension": ".la", "mime_type": "audio/x-nspaudio"},
			{"extension": ".lam", "mime_type": "audio/x-liveaudio"},
			{"extension": ".latex", "mime_type": "application/x-latex"},
			{"extension": ".latex", "mime_type": "application/x-latex"},
			{"extension": ".lha", "mime_type": "application/lha"},
			{"extension": ".lha", "mime_type": "application/octet-stream"},
			{"extension": ".lha", "mime_type": "application/x-lha"},
			{"extension": ".lhx", "mime_type": "application/octet-stream"},
			{"extension": ".list", "mime_type": "text/plain"},
			{"extension": ".lma", "mime_type": "audio/nspaudio"},
			{"extension": ".lma", "mime_type": "audio/x-nspaudio"},
			{"extension": ".log", "mime_type": "text/plain"},
			{"extension": ".lsp", "mime_type": "application/x-lisp"},
			{"extension": ".lsp", "mime_type": "text/x-script.lisp"},
			{"extension": ".lst", "mime_type": "text/plain"},
			{"extension": ".lsx", "mime_type": "text/x-la-asf"},
			{"extension": ".ltx", "mime_type": "application/x-latex"},
			{"extension": ".lzh", "mime_type": "application/octet-stream"},
			{"extension": ".lzh", "mime_type": "application/x-lzh"},
			{"extension": ".lzx", "mime_type": "application/lzx"},
			{"extension": ".lzx", "mime_type": "application/octet-stream"},
			{"extension": ".lzx", "mime_type": "application/x-lzx"},
			{"extension": ".m", "mime_type": "text/plain"}, {"extension": ".m", "mime_type": "text/x-m"},
			{"extension": ".m1v", "mime_type": "video/mpeg"},
			{"extension": ".m1v", "mime_type": "video/mpeg"},
			{"extension": ".m2a", "mime_type": "audio/mpeg"},
			{"extension": ".m2v", "mime_type": "video/mpeg"},
			{"extension": ".m3u", "mime_type": "audio/x-mpequrl"},
			{"extension": ".man", "mime_type": "application/x-troff-man"},
			{"extension": ".man", "mime_type": "application/x-troff-man"},
			{"extension": ".map", "mime_type": "application/x-navimap"},
			{"extension": ".mar", "mime_type": "text/plain"},
			{"extension": ".mbd", "mime_type": "application/mbedlet"},
			{"extension": ".mc$", "mime_type": "application/x-magic-cap-package-1.0"},
			{"extension": ".mcd", "mime_type": "application/mcad"},
			{"extension": ".mcd", "mime_type": "application/x-mathcad"},
			{"extension": ".mcf", "mime_type": "image/vasa"}, {"extension": ".mcf", "mime_type": "text/mcf"},
			{"extension": ".mcp", "mime_type": "application/netmc"},
			{"extension": ".me", "mime_type": "application/x-troff-me"},
			{"extension": ".me", "mime_type": "application/x-troff-me"},
			{"extension": ".mht", "mime_type": "message/rfc822"},
			{"extension": ".mht", "mime_type": "message/rfc822"},
			{"extension": ".mhtml", "mime_type": "message/rfc822"},
			{"extension": ".mhtml", "mime_type": "message/rfc822"},
			{"extension": ".mid", "mime_type": "application/x-midi"},
			{"extension": ".mid", "mime_type": "audio/midi"},
			{"extension": ".mid", "mime_type": "audio/x-mid"},
			{"extension": ".mid", "mime_type": "audio/x-midi"},
			{"extension": ".mid", "mime_type": "music/crescendo"},
			{"extension": ".mid", "mime_type": "x-music/x-midi"},
			{"extension": ".midi", "mime_type": "application/x-midi"},
			{"extension": ".midi", "mime_type": "audio/midi"},
			{"extension": ".midi", "mime_type": "audio/x-mid"},
			{"extension": ".midi", "mime_type": "audio/x-midi"},
			{"extension": ".midi", "mime_type": "music/crescendo"},
			{"extension": ".midi", "mime_type": "x-music/x-midi"},
			{"extension": ".mif", "mime_type": "application/x-frame"},
			{"extension": ".mif", "mime_type": "application/x-mif"},
			{"extension": ".mif", "mime_type": "application/x-mif"},
			{"extension": ".mime", "mime_type": "message/rfc822"},
			{"extension": ".mime", "mime_type": "www/mime"},
			{"extension": ".mjf", "mime_type": "audio/x-vnd.audioexplosion.mjuicemediafile"},
			{"extension": ".mjpg", "mime_type": "video/x-motion-jpeg"},
			{"extension": ".mm", "mime_type": "application/base64"},
			{"extension": ".mm", "mime_type": "application/x-meme"},
			{"extension": ".mme", "mime_type": "application/base64"},
			{"extension": ".mod", "mime_type": "audio/mod"},
			{"extension": ".mod", "mime_type": "audio/x-mod"},
			{"extension": ".moov", "mime_type": "video/quicktime"},
			{"extension": ".mov", "mime_type": "video/quicktime"},
			{"extension": ".mov", "mime_type": "video/quicktime"},
			{"extension": ".movie", "mime_type": "video/x-sgi-movie"},
			{"extension": ".movie", "mime_type": "video/x-sgi-movie"},
			{"extension": ".mp2", "mime_type": "audio/mpeg"},
			{"extension": ".mp2", "mime_type": "audio/x-mpeg"},
			{"extension": ".mp2", "mime_type": "video/mpeg"},
			{"extension": ".mp2", "mime_type": "video/x-mpeg"},
			{"extension": ".mp2", "mime_type": "video/x-mpeq2a"},
			{"extension": ".mp2", "mime_type": "audio/mpeg"},
			{"extension": ".mp3", "mime_type": "audio/mpeg3"},
			{"extension": ".mp3", "mime_type": "audio/x-mpeg-3"},
			{"extension": ".mp3", "mime_type": "video/mpeg"},
			{"extension": ".mp3", "mime_type": "video/x-mpeg"},
			{"extension": ".mp3", "mime_type": "audio/mpeg"}, {"extension": ".mp4", "mime_type": "video/mp4"},
			{"extension": ".mpa", "mime_type": "audio/mpeg"},
			{"extension": ".mpa", "mime_type": "video/mpeg"},
			{"extension": ".mpa", "mime_type": "video/mpeg"},
			{"extension": ".mpc", "mime_type": "application/x-project"},
			{"extension": ".mpe", "mime_type": "video/mpeg"},
			{"extension": ".mpe", "mime_type": "video/mpeg"},
			{"extension": ".mpeg", "mime_type": "video/mpeg"},
			{"extension": ".mpeg", "mime_type": "video/mpeg"},
			{"extension": ".mpg", "mime_type": "audio/mpeg"},
			{"extension": ".mpg", "mime_type": "video/mpeg"},
			{"extension": ".mpg", "mime_type": "video/mpeg"},
			{"extension": ".mpga", "mime_type": "audio/mpeg"},
			{"extension": ".mpp", "mime_type": "application/vnd.ms-project"},
			{"extension": ".mpt", "mime_type": "application/x-project"},
			{"extension": ".mpv", "mime_type": "application/x-project"},
			{"extension": ".mpx", "mime_type": "application/x-project"},
			{"extension": ".mrc", "mime_type": "application/marc"},
			{"extension": ".ms", "mime_type": "application/x-troff-ms"},
			{"extension": ".ms", "mime_type": "application/x-troff-ms"},
			{"extension": ".mv", "mime_type": "video/x-sgi-movie"},
			{"extension": ".my", "mime_type": "audio/make"},
			{"extension": ".mzz", "mime_type": "application/x-vnd.audioexplosion.mzz"},
			{"extension": ".nap", "mime_type": "image/naplps"},
			{"extension": ".naplps", "mime_type": "image/naplps"},
			{"extension": ".nc", "mime_type": "application/x-netcdf"},
			{"extension": ".nc", "mime_type": "application/x-netcdf"},
			{"extension": ".ncm", "mime_type": "application/vnd.nokia.configuration-message"},
			{"extension": ".nif", "mime_type": "image/x-niff"},
			{"extension": ".niff", "mime_type": "image/x-niff"},
			{"extension": ".nix", "mime_type": "application/x-mix-transfer"},
			{"extension": ".nsc", "mime_type": "application/x-conference"},
			{"extension": ".nvd", "mime_type": "application/x-navidoc"},
			{"extension": ".nws", "mime_type": "message/rfc822"},
			{"extension": ".o", "mime_type": "application/octet-stream"},
			{"extension": ".o", "mime_type": "application/octet-stream"},
			{"extension": ".obj", "mime_type": "application/octet-stream"},
			{"extension": ".oda", "mime_type": "application/oda"},
			{"extension": ".oda", "mime_type": "application/oda"},
			{"extension": ".omc", "mime_type": "application/x-omc"},
			{"extension": ".omcd", "mime_type": "application/x-omcdatamaker"},
			{"extension": ".omcr", "mime_type": "application/x-omcregerator"},
			{"extension": ".p", "mime_type": "text/x-pascal"},
			{"extension": ".p10", "mime_type": "application/pkcs10"},
			{"extension": ".p10", "mime_type": "application/x-pkcs10"},
			{"extension": ".p12", "mime_type": "application/pkcs-12"},
			{"extension": ".p12", "mime_type": "application/x-pkcs12"},
			{"extension": ".p12", "mime_type": "application/x-pkcs12"},
			{"extension": ".p7a", "mime_type": "application/x-pkcs7-signature"},
			{"extension": ".p7c", "mime_type": "application/pkcs7-mime"},
			{"extension": ".p7c", "mime_type": "application/x-pkcs7-mime"},
			{"extension": ".p7c", "mime_type": "application/pkcs7-mime"},
			{"extension": ".p7m", "mime_type": "application/pkcs7-mime"},
			{"extension": ".p7m", "mime_type": "application/x-pkcs7-mime"},
			{"extension": ".p7r", "mime_type": "application/x-pkcs7-certreqresp"},
			{"extension": ".p7s", "mime_type": "application/pkcs7-signature"},
			{"extension": ".part", "mime_type": "application/pro_eng"},
			{"extension": ".pas", "mime_type": "text/pascal"},
			{"extension": ".pbm", "mime_type": "image/x-portable-bitmap"},
			{"extension": ".pbm", "mime_type": "image/x-portable-bitmap"},
			{"extension": ".pcl", "mime_type": "application/vnd.hp-pcl"},
			{"extension": ".pcl", "mime_type": "application/x-pcl"},
			{"extension": ".pct", "mime_type": "image/x-pict"},
			{"extension": ".pcx", "mime_type": "image/x-pcx"},
			{"extension": ".pdb", "mime_type": "chemical/x-pdb"},
			{"extension": ".pdf", "mime_type": "application/pdf"},
			{"extension": ".pdf", "mime_type": "application/pdf"},
			{"extension": ".pfunk", "mime_type": "audio/make"},
			{"extension": ".pfunk", "mime_type": "audio/make.my.funk"},
			{"extension": ".pfx", "mime_type": "application/x-pkcs12"},
			{"extension": ".pgm", "mime_type": "image/x-portable-graymap"},
			{"extension": ".pgm", "mime_type": "image/x-portable-greymap"},
			{"extension": ".pgm", "mime_type": "image/x-portable-graymap"},
			{"extension": ".pic", "mime_type": "image/pict"},
			{"extension": ".pict", "mime_type": "image/pict"},
			{"extension": ".pkg", "mime_type": "application/x-newton-compatible-pkg"},
			{"extension": ".pko", "mime_type": "application/vnd.ms-pki.pko"},
			{"extension": ".pl", "mime_type": "text/plain"},
			{"extension": ".pl", "mime_type": "text/x-script.perl"},
			{"extension": ".pl", "mime_type": "text/plain"},
			{"extension": ".plx", "mime_type": "application/x-pixclscript"},
			{"extension": ".pm", "mime_type": "image/x-xpixmap"},
			{"extension": ".pm", "mime_type": "text/x-script.perl-module"},
			{"extension": ".pm4", "mime_type": "application/x-pagemaker"},
			{"extension": ".pm5", "mime_type": "application/x-pagemaker"},
			{"extension": ".png", "mime_type": "image/png"}, {"extension": ".png", "mime_type": "image/png"},
			{"extension": ".pnm", "mime_type": "application/x-portable-anymap"},
			{"extension": ".pnm", "mime_type": "image/x-portable-anymap"},
			{"extension": ".pnm", "mime_type": "image/x-portable-anymap"},
			{"extension": ".pot", "mime_type": "application/mspowerpoint"},
			{"extension": ".pot", "mime_type": "application/vnd.ms-powerpoint"},
			{"extension": ".pot", "mime_type": "application/vnd.ms-powerpoint"},
			{"extension": ".potm", "mime_type": "application/vnd.ms-powerpoint.template.macroEnabled.12"},
			{"extension": ".potx",
			 "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.template"},
			{"extension": ".pov", "mime_type": "model/x-pov"},
			{"extension": ".ppa", "mime_type": "application/vnd.ms-powerpoint"},
			{"extension": ".ppa", "mime_type": "application/vnd.ms-powerpoint"},
			{"extension": ".ppam", "mime_type": "application/vnd.ms-powerpoint.addin.macroEnabled.12"},
			{"extension": ".ppm", "mime_type": "image/x-portable-pixmap"},
			{"extension": ".ppm", "mime_type": "image/x-portable-pixmap"},
			{"extension": ".pps", "mime_type": "application/mspowerpoint"},
			{"extension": ".pps", "mime_type": "application/vnd.ms-powerpoint"},
			{"extension": ".pps", "mime_type": "application/vnd.ms-powerpoint"},
			{"extension": ".ppsm", "mime_type": "application/vnd.ms-powerpoint.slideshow.macroEnabled.12"},
			{"extension": ".ppsx",
			 "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.slideshow"},
			{"extension": ".ppt", "mime_type": "application/mspowerpoint"},
			{"extension": ".ppt", "mime_type": "application/powerpoint"},
			{"extension": ".ppt", "mime_type": "application/vnd.ms-powerpoint"},
			{"extension": ".ppt", "mime_type": "application/x-mspowerpoint"},
			{"extension": ".ppt", "mime_type": "application/vnd.ms-powerpoint"},
			{"extension": ".pptm", "mime_type": "application/vnd.ms-powerpoint.presentation.macroEnabled.12"},
			{"extension": ".pptx",
			 "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation"},
			{"extension": ".ppz", "mime_type": "application/mspowerpoint"},
			{"extension": ".pre", "mime_type": "application/x-freelance"},
			{"extension": ".prt", "mime_type": "application/pro_eng"},
			{"extension": ".ps", "mime_type": "application/postscript"},
			{"extension": ".ps", "mime_type": "application/postscript"},
			{"extension": ".psd", "mime_type": "application/octet-stream"},
			{"extension": ".pvu", "mime_type": "paleovu/x-pv"},
			{"extension": ".pwz", "mime_type": "application/vnd.ms-powerpoint"},
			{"extension": ".pwz", "mime_type": "application/vnd.ms-powerpoint"},
			{"extension": ".py", "mime_type": "text/x-script.phyton"},
			{"extension": ".py", "mime_type": "text/x-python"},
			{"extension": ".pyc", "mime_type": "applicaiton/x-bytecode.python"},
			{"extension": ".pyc", "mime_type": "application/x-python-code"},
			{"extension": ".pyo", "mime_type": "application/x-python-code"},
			{"extension": ".qcp", "mime_type": "audio/vnd.qcelp"},
			{"extension": ".qd3", "mime_type": "x-world/x-3dmf"},
			{"extension": ".qd3d", "mime_type": "x-world/x-3dmf"},
			{"extension": ".qif", "mime_type": "image/x-quicktime"},
			{"extension": ".qt", "mime_type": "video/quicktime"},
			{"extension": ".qt", "mime_type": "video/quicktime"},
			{"extension": ".qtc", "mime_type": "video/x-qtc"},
			{"extension": ".qti", "mime_type": "image/x-quicktime"},
			{"extension": ".qtif", "mime_type": "image/x-quicktime"},
			{"extension": ".ra", "mime_type": "audio/x-pn-realaudio"},
			{"extension": ".ra", "mime_type": "audio/x-pn-realaudio-plugin"},
			{"extension": ".ra", "mime_type": "audio/x-realaudio"},
			{"extension": ".ra", "mime_type": "audio/x-pn-realaudio"},
			{"extension": ".ram", "mime_type": "audio/x-pn-realaudio"},
			{"extension": ".ram", "mime_type": "application/x-pn-realaudio"},
			{"extension": ".ras", "mime_type": "application/x-cmu-raster"},
			{"extension": ".ras", "mime_type": "image/cmu-raster"},
			{"extension": ".ras", "mime_type": "image/x-cmu-raster"},
			{"extension": ".ras", "mime_type": "image/x-cmu-raster"},
			{"extension": ".rast", "mime_type": "image/cmu-raster"},
			{"extension": ".rdf", "mime_type": "application/xml"},
			{"extension": ".rexx", "mime_type": "text/x-script.rexx"},
			{"extension": ".rf", "mime_type": "image/vnd.rn-realflash"},
			{"extension": ".rgb", "mime_type": "image/x-rgb"},
			{"extension": ".rgb", "mime_type": "image/x-rgb"},
			{"extension": ".rm", "mime_type": "application/vnd.rn-realmedia"},
			{"extension": ".rm", "mime_type": "audio/x-pn-realaudio"},
			{"extension": ".rmi", "mime_type": "audio/mid"},
			{"extension": ".rmm", "mime_type": "audio/x-pn-realaudio"},
			{"extension": ".rmp", "mime_type": "audio/x-pn-realaudio"},
			{"extension": ".rmp", "mime_type": "audio/x-pn-realaudio-plugin"},
			{"extension": ".rng", "mime_type": "application/ringing-tones"},
			{"extension": ".rng", "mime_type": "application/vnd.nokia.ringing-tone"},
			{"extension": ".rnx", "mime_type": "application/vnd.rn-realplayer"},
			{"extension": ".roff", "mime_type": "application/x-troff"},
			{"extension": ".roff", "mime_type": "application/x-troff"},
			{"extension": ".rp", "mime_type": "image/vnd.rn-realpix"},
			{"extension": ".rpm", "mime_type": "audio/x-pn-realaudio-plugin"},
			{"extension": ".rt", "mime_type": "text/richtext"},
			{"extension": ".rt", "mime_type": "text/vnd.rn-realtext"},
			{"extension": ".rtf", "mime_type": "application/rtf"},
			{"extension": ".rtf", "mime_type": "application/x-rtf"},
			{"extension": ".rtf", "mime_type": "text/richtext"},
			{"extension": ".rtx", "mime_type": "application/rtf"},
			{"extension": ".rtx", "mime_type": "text/richtext"},
			{"extension": ".rtx", "mime_type": "text/richtext"},
			{"extension": ".rv", "mime_type": "video/vnd.rn-realvideo"},
			{"extension": ".s", "mime_type": "text/x-asm"}, {"extension": ".s3m", "mime_type": "audio/s3m"},
			{"extension": ".saveme", "mime_type": "application/octet-stream"},
			{"extension": ".sbk", "mime_type": "application/x-tbook"},
			{"extension": ".scm", "mime_type": "application/x-lotusscreencam"},
			{"extension": ".scm", "mime_type": "text/x-script.guile"},
			{"extension": ".scm", "mime_type": "text/x-script.scheme"},
			{"extension": ".scm", "mime_type": "video/x-scm"},
			{"extension": ".sdml", "mime_type": "text/plain"},
			{"extension": ".sdp", "mime_type": "application/sdp"},
			{"extension": ".sdp", "mime_type": "application/x-sdp"},
			{"extension": ".sdr", "mime_type": "application/sounder"},
			{"extension": ".sea", "mime_type": "application/sea"},
			{"extension": ".sea", "mime_type": "application/x-sea"},
			{"extension": ".set", "mime_type": "application/set"},
			{"extension": ".sgm", "mime_type": "text/sgml"},
			{"extension": ".sgm", "mime_type": "text/x-sgml"},
			{"extension": ".sgm", "mime_type": "text/x-sgml"},
			{"extension": ".sgml", "mime_type": "text/sgml"},
			{"extension": ".sgml", "mime_type": "text/x-sgml"},
			{"extension": ".sgml", "mime_type": "text/x-sgml"},
			{"extension": ".sh", "mime_type": "application/x-bsh"},
			{"extension": ".sh", "mime_type": "application/x-sh"},
			{"extension": ".sh", "mime_type": "application/x-shar"},
			{"extension": ".sh", "mime_type": "text/x-script.sh"},
			{"extension": ".sh", "mime_type": "application/x-sh"},
			{"extension": ".shar", "mime_type": "application/x-bsh"},
			{"extension": ".shar", "mime_type": "application/x-shar"},
			{"extension": ".shar", "mime_type": "application/x-shar"},
			{"extension": ".shtml", "mime_type": "text/html"},
			{"extension": ".shtml", "mime_type": "text/x-server-parsed-html"},
			{"extension": ".sid", "mime_type": "audio/x-psid"},
			{"extension": ".sit", "mime_type": "application/x-sit"},
			{"extension": ".sit", "mime_type": "application/x-stuffit"},
			{"extension": ".skd", "mime_type": "application/x-koan"},
			{"extension": ".skm", "mime_type": "application/x-koan"},
			{"extension": ".skp", "mime_type": "application/x-koan"},
			{"extension": ".skt", "mime_type": "application/x-koan"},
			{"extension": ".sl", "mime_type": "application/x-seelogo"},
			{"extension": ".smi", "mime_type": "application/smil"},
			{"extension": ".smil", "mime_type": "application/smil"},
			{"extension": ".snd", "mime_type": "audio/basic"},
			{"extension": ".snd", "mime_type": "audio/x-adpcm"},
			{"extension": ".snd", "mime_type": "audio/basic"},
			{"extension": ".so", "mime_type": "application/octet-stream"},
			{"extension": ".sol", "mime_type": "application/solids"},
			{"extension": ".spc", "mime_type": "application/x-pkcs7-certificates"},
			{"extension": ".spc", "mime_type": "text/x-speech"},
			{"extension": ".spl", "mime_type": "application/futuresplash"},
			{"extension": ".spr", "mime_type": "application/x-sprite"},
			{"extension": ".sprite", "mime_type": "application/x-sprite"},
			{"extension": ".src", "mime_type": "application/x-wais-source"},
			{"extension": ".src", "mime_type": "application/x-wais-source"},
			{"extension": ".ssi", "mime_type": "text/x-server-parsed-html"},
			{"extension": ".ssm", "mime_type": "application/streamingmedia"},
			{"extension": ".sst", "mime_type": "application/vnd.ms-pki.certstore"},
			{"extension": ".step", "mime_type": "application/step"},
			{"extension": ".stl", "mime_type": "application/sla"},
			{"extension": ".stl", "mime_type": "application/vnd.ms-pki.stl"},
			{"extension": ".stl", "mime_type": "application/x-navistyle"},
			{"extension": ".stp", "mime_type": "application/step"},
			{"extension": ".sv4cpio", "mime_type": "application/x-sv4cpio"},
			{"extension": ".sv4crc", "mime_type": "application/x-sv4crc"},
			{"extension": ".sv4crc", "mime_type": "application/x-sv4crc"},
			{"extension": ".svf", "mime_type": "image/vnd.dwg"},
			{"extension": ".svf", "mime_type": "image/x-dwg"},
			{"extension": ".svr", "mime_type": "application/x-world"},
			{"extension": ".svr", "mime_type": "x-world/x-svr"},
			{"extension": ".swf", "mime_type": "application/x-shockwave-flash"},
			{"extension": ".swf", "mime_type": "application/x-shockwave-flash"},
			{"extension": ".t", "mime_type": "application/x-troff"},
			{"extension": ".t", "mime_type": "application/x-troff"},
			{"extension": ".talk", "mime_type": "text/x-speech"},
			{"extension": ".tar", "mime_type": "application/x-tar"},
			{"extension": ".tar", "mime_type": "application/x-tar"},
			{"extension": ".tbk", "mime_type": "application/toolbook"},
			{"extension": ".tbk", "mime_type": "application/x-tbook"},
			{"extension": ".tcl", "mime_type": "application/x-tcl"},
			{"extension": ".tcl", "mime_type": "text/x-script.tcl"},
			{"extension": ".tcl", "mime_type": "application/x-tcl"},
			{"extension": ".tcsh", "mime_type": "text/x-script.tcsh"},
			{"extension": ".tex", "mime_type": "application/x-tex"},
			{"extension": ".tex", "mime_type": "application/x-tex"},
			{"extension": ".texi", "mime_type": "application/x-texinfo"},
			{"extension": ".texi", "mime_type": "application/x-texinfo"},
			{"extension": ".texinfo", "mime_type": "application/x-texinfo"},
			{"extension": ".text", "mime_type": "application/plain"},
			{"extension": ".text", "mime_type": "text/plain"},
			{"extension": ".tgz", "mime_type": "application/gnutar"},
			{"extension": ".tgz", "mime_type": "application/x-compressed"},
			{"extension": ".tif", "mime_type": "image/tiff"},
			{"extension": ".tif", "mime_type": "image/x-tiff"},
			{"extension": ".tif", "mime_type": "image/tiff"},
			{"extension": ".tiff", "mime_type": "image/tiff"},
			{"extension": ".tiff", "mime_type": "image/x-tiff"},
			{"extension": ".tiff", "mime_type": "image/tiff"},
			{"extension": ".tr", "mime_type": "application/x-troff"},
			{"extension": ".tr", "mime_type": "application/x-troff"},
			{"extension": ".tsi", "mime_type": "audio/tsp-audio"},
			{"extension": ".tsp", "mime_type": "application/dsptype"},
			{"extension": ".tsp", "mime_type": "audio/tsplayer"},
			{"extension": ".tsv", "mime_type": "text/tab-separated-values"},
			{"extension": ".tsv", "mime_type": "text/tab-separated-values"},
			{"extension": ".turbot", "mime_type": "image/florian"},
			{"extension": ".txt", "mime_type": "text/plain"},
			{"extension": ".txt", "mime_type": "text/plain"},
			{"extension": ".uil", "mime_type": "text/x-uil"},
			{"extension": ".uni", "mime_type": "text/uri-list"},
			{"extension": ".unis", "mime_type": "text/uri-list"},
			{"extension": ".unv", "mime_type": "application/i-deas"},
			{"extension": ".uri", "mime_type": "text/uri-list"},
			{"extension": ".uris", "mime_type": "text/uri-list"},
			{"extension": ".ustar", "mime_type": "application/x-ustar"},
			{"extension": ".ustar", "mime_type": "multipart/x-ustar"},
			{"extension": ".ustar", "mime_type": "application/x-ustar"},
			{"extension": ".uu", "mime_type": "application/octet-stream"},
			{"extension": ".uu", "mime_type": "text/x-uuencode"},
			{"extension": ".uue", "mime_type": "text/x-uuencode"},
			{"extension": ".vcd", "mime_type": "application/x-cdlink"},
			{"extension": ".vcf", "mime_type": "text/x-vcard"},
			{"extension": ".vcs", "mime_type": "text/x-vcalendar"},
			{"extension": ".vda", "mime_type": "application/vda"},
			{"extension": ".vdo", "mime_type": "video/vdo"},
			{"extension": ".vew", "mime_type": "application/groupwise"},
			{"extension": ".viv", "mime_type": "video/vivo"},
			{"extension": ".viv", "mime_type": "video/vnd.vivo"},
			{"extension": ".vivo", "mime_type": "video/vivo"},
			{"extension": ".vivo", "mime_type": "video/vnd.vivo"},
			{"extension": ".vmd", "mime_type": "application/vocaltec-media-desc"},
			{"extension": ".vmf", "mime_type": "application/vocaltec-media-file"},
			{"extension": ".voc", "mime_type": "audio/voc"},
			{"extension": ".voc", "mime_type": "audio/x-voc"},
			{"extension": ".vos", "mime_type": "video/vosaic"},
			{"extension": ".vox", "mime_type": "audio/voxware"},
			{"extension": ".vqe", "mime_type": "audio/x-twinvq-plugin"},
			{"extension": ".vqf", "mime_type": "audio/x-twinvq"},
			{"extension": ".vql", "mime_type": "audio/x-twinvq-plugin"},
			{"extension": ".vrml", "mime_type": "application/x-vrml"},
			{"extension": ".vrml", "mime_type": "model/vrml"},
			{"extension": ".vrml", "mime_type": "x-world/x-vrml"},
			{"extension": ".vrt", "mime_type": "x-world/x-vrt"},
			{"extension": ".vsd", "mime_type": "application/x-visio"},
			{"extension": ".vst", "mime_type": "application/x-visio"},
			{"extension": ".vsw", "mime_type": "application/x-visio"},
			{"extension": ".w60", "mime_type": "application/wordperfect6.0"},
			{"extension": ".w61", "mime_type": "application/wordperfect6.1"},
			{"extension": ".w6w", "mime_type": "application/msword"},
			{"extension": ".wav", "mime_type": "audio/wav"},
			{"extension": ".wav", "mime_type": "audio/x-wav"},
			{"extension": ".wav", "mime_type": "audio/x-wav"},
			{"extension": ".wb1", "mime_type": "application/x-qpro"},
			{"extension": ".wbmp", "mime_type": "image/vnd.wap.wbmp"},
			{"extension": ".web", "mime_type": "application/vnd.xara"},
			{"extension": ".wiz", "mime_type": "application/msword"},
			{"extension": ".wiz", "mime_type": "application/msword"},
			{"extension": ".wk1", "mime_type": "application/x-123"},
			{"extension": ".wmf", "mime_type": "windows/metafile"},
			{"extension": ".wml", "mime_type": "text/vnd.wap.wml"},
			{"extension": ".wmlc", "mime_type": "application/vnd.wap.wmlc"},
			{"extension": ".wmls", "mime_type": "text/vnd.wap.wmlscript"},
			{"extension": ".wmlsc", "mime_type": "application/vnd.wap.wmlscriptc"},
			{"extension": ".word", "mime_type": "application/msword"},
			{"extension": ".wp", "mime_type": "application/wordperfect"},
			{"extension": ".wp5", "mime_type": "application/wordperfect"},
			{"extension": ".wp5", "mime_type": "application/wordperfect6.0"},
			{"extension": ".wp6", "mime_type": "application/wordperfect"},
			{"extension": ".wpd", "mime_type": "application/wordperfect"},
			{"extension": ".wpd", "mime_type": "application/x-wpwin"},
			{"extension": ".wq1", "mime_type": "application/x-lotus"},
			{"extension": ".wri", "mime_type": "application/mswrite"},
			{"extension": ".wri", "mime_type": "application/x-wri"},
			{"extension": ".wrl", "mime_type": "application/x-world"},
			{"extension": ".wrl", "mime_type": "model/vrml"},
			{"extension": ".wrl", "mime_type": "x-world/x-vrml"},
			{"extension": ".wrz", "mime_type": "model/vrml"},
			{"extension": ".wrz", "mime_type": "x-world/x-vrml"},
			{"extension": ".wsc", "mime_type": "text/scriplet"},
			{"extension": ".wsdl", "mime_type": "application/xml"},
			{"extension": ".wsrc", "mime_type": "application/x-wais-source"},
			{"extension": ".wtk", "mime_type": "application/x-wintalk"},
			{"extension": ".xbm", "mime_type": "image/x-xbitmap"},
			{"extension": ".xbm", "mime_type": "image/x-xbm"},
			{"extension": ".xbm", "mime_type": "image/xbm"},
			{"extension": ".xbm", "mime_type": "image/x-xbitmap"},
			{"extension": ".xdr", "mime_type": "video/x-amt-demorun"},
			{"extension": ".xgz", "mime_type": "xgl/drawing"},
			{"extension": ".xif", "mime_type": "image/vnd.xiff"},
			{"extension": ".xl", "mime_type": "application/excel"},
			{"extension": ".xla", "mime_type": "application/excel"},
			{"extension": ".xla", "mime_type": "application/x-excel"},
			{"extension": ".xla", "mime_type": "application/x-msexcel"},
			{"extension": ".xla", "mime_type": "application/vnd.ms-excel"},
			{"extension": ".csv", "mime_type": "application/vnd.ms-excel"},
			{"extension": ".xlam", "mime_type": "application/vnd.ms-excel.addin.macroEnabled.12"},
			{"extension": ".xlb", "mime_type": "application/excel"},
			{"extension": ".xlb", "mime_type": "application/vnd.ms-excel"},
			{"extension": ".xlb", "mime_type": "application/x-excel"},
			{"extension": ".xlb", "mime_type": "application/vnd.ms-excel"},
			{"extension": ".xlc", "mime_type": "application/excel"},
			{"extension": ".xlc", "mime_type": "application/vnd.ms-excel"},
			{"extension": ".xlc", "mime_type": "application/x-excel"},
			{"extension": ".xld", "mime_type": "application/excel"},
			{"extension": ".xld", "mime_type": "application/x-excel"},
			{"extension": ".xlk", "mime_type": "application/excel"},
			{"extension": ".xlk", "mime_type": "application/x-excel"},
			{"extension": ".xll", "mime_type": "application/excel"},
			{"extension": ".xll", "mime_type": "application/vnd.ms-excel"},
			{"extension": ".xll", "mime_type": "application/x-excel"},
			{"extension": ".xlm", "mime_type": "application/excel"},
			{"extension": ".xlm", "mime_type": "application/vnd.ms-excel"},
			{"extension": ".xlm", "mime_type": "application/x-excel"},
			{"extension": ".xls", "mime_type": "application/excel"},
			{"extension": ".xls", "mime_type": "application/vnd.ms-excel"},
			{"extension": ".xls", "mime_type": "application/x-excel"},
			{"extension": ".xls", "mime_type": "application/x-msexcel"},
			{"extension": ".xls", "mime_type": "application/excel"},
			{"extension": ".xls", "mime_type": "application/vnd.ms-excel"},
			{"extension": ".xlsb", "mime_type": "application/vnd.ms-excel.sheet.binary.macroEnabled.12"},
			{"extension": ".xlsm", "mime_type": "application/vnd.ms-excel.sheet.macroEnabled.12"},
			{"extension": ".xlsx",
			 "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
			{"extension": ".xlt", "mime_type": "application/excel"},
			{"extension": ".xlt", "mime_type": "application/x-excel"},
			{"extension": ".xlt", "mime_type": "application/vnd.ms-excel"},
			{"extension": ".xltm", "mime_type": "application/vnd.ms-excel.template.macroEnabled.12"},
			{"extension": ".xltx",
			 "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.template"},
			{"extension": ".xlv", "mime_type": "application/excel"},
			{"extension": ".xlv", "mime_type": "application/x-excel"},
			{"extension": ".xlw", "mime_type": "application/excel"},
			{"extension": ".xlw", "mime_type": "application/vnd.ms-excel"},
			{"extension": ".xlw", "mime_type": "application/x-excel"},
			{"extension": ".xlw", "mime_type": "application/x-msexcel"},
			{"extension": ".xm", "mime_type": "audio/xm"},
			{"extension": ".xml", "mime_type": "application/xml"},
			{"extension": ".xml", "mime_type": "text/xml"}, {"extension": ".xml", "mime_type": "text/xml"},
			{"extension": ".xmz", "mime_type": "xgl/movie"},
			{"extension": ".xpdl", "mime_type": "application/xml"},
			{"extension": ".xpix", "mime_type": "application/x-vnd.ls-xpix"},
			{"extension": ".xpm", "mime_type": "image/x-xpixmap"},
			{"extension": ".xpm", "mime_type": "image/xpm"},
			{"extension": ".xpm", "mime_type": "image/x-xpixmap"},
			{"extension": ".x-png", "mime_type": "image/png"},
			{"extension": ".xsl", "mime_type": "application/xml"},
			{"extension": ".xsr", "mime_type": "video/x-amt-showrun"},
			{"extension": ".xwd", "mime_type": "image/x-xwd"},
			{"extension": ".xwd", "mime_type": "image/x-xwindowdump"},
			{"extension": ".xwd", "mime_type": "image/x-xwindowdump"},
			{"extension": ".xyz", "mime_type": "chemical/x-pdb"},
			{"extension": ".z", "mime_type": "application/x-compress"},
			{"extension": ".z", "mime_type": "application/x-compressed"},
			{"extension": ".zip", "mime_type": "application/x-compressed"},
			{"extension": ".zip", "mime_type": "application/x-zip-compressed"},
			{"extension": ".zip", "mime_type": "application/zip"},
			{"extension": ".zip", "mime_type": "multipart/x-zip"},
			{"extension": ".zip", "mime_type": "application/zip"},
			{"extension": ".zoo", "mime_type": "application/octet-stream"},
			{"extension": ".zsh", "mime_type": "text/x-script.zsh"}
		]

		pass
	#def get_extensions_for_type(self, general_type):
	#  for ext in self.mts.types_map:
	#    if ext == general_type:
	#      return self.mts.types_map[ext]
	def get_extensions_from_mime_type(self, _type):
		_type = _type.lower()
		results = []
		for row in self.types_map:
			if row["mime_type"] == _type:
				#results.append({
				#  'extension': ext,
				#  'mime_type' : self.types_map[ext]
				#})
				results.append(row["extension"])
		return results
	def get_mime_type_from_extensions(self, _extensions):
		_extensions = _extensions.lower()
		results = []
		for row in self.types_map:
			if row["extension"] == _extensions:
				#results.append({
				#  'extension': ext,
				#  'mime_type' : self.types_map[ext]
				#})
				results.append(row["mime_type"])
		return results
	def checkMimeTypeInAcessList(self, access_list, mime_type_check, flag=False):
		""" access_list ... list of extension ex). ['xls','csv']
		    mime_type_check ... ex) application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
		"""
		_mimetypes = self.get_extensions_from_mime_type(mime_type_check)
		if flag is False:
			# "allow list" case: if file is in access_list, upload OK
			for mime_type in access_list:
				if str('.' + mime_type) in _mimetypes:
					return True
			return False
		else:
			# "deny list" case: if file is in access_list, upload NOT OK
			for mime_type in access_list:
				if str('.' + mime_type) in _mimetypes:
					return False
			return True


class AttachExportPage(sateraito_page._BasePage):
	
	def setHeader(self, file_name, mime_type, inline=False, show_in_browser=False):
		logging.info('setHeader inline=' + str(inline) + ' show_in_browser=' + str(show_in_browser))
		browser_name = ''
		dist_name = ''
		# user_agentが、「AndroidDownloadManager」などの場合にエラーするので、try～catch
		try:
			result = httpagentparser.detect(request.user_agent)
			logging.debug('httpagent detect result=' + str(result))
			if 'browser' in result:
				browser_name = result['browser']['name']
			if 'dist' in result:
				dist_name = result['dist']['name']
		except Exception as instance:
			logging.info('useragent=' + str(request.user_agent))
			logging.info(str(instance))
			browser_name = ''
		logging.info('browser_name=' + str(browser_name) + ' dist_name=' + str(dist_name))
		
		encode_filename_by_b64 = True
		# for IE and Safari and Edge
		# Edge対応 2016.03.15
		#if browser_name == 'Microsoft Internet Explorer' or browser_name == 'Safari':
		if browser_name == 'Microsoft Internet Explorer' or browser_name == 'Safari' or browser_name == 'MSEdge':
			encode_filename_by_b64 = False
		# for iPhone and Android
		if dist_name == 'Android' or dist_name == 'iPhone' or dist_name == 'IPhone' or dist_name == 'iPad' or dist_name == 'IPad':
			encode_filename_by_b64 = False
		# for Google Drive preview function
		if dist_name == '' and browser_name == '':
			encode_filename_by_b64 = False
		
		if encode_filename_by_b64:
			# for other browser
			filename = base64.b64encode(str(file_name).encode('utf8'))
		else:
			# for IE, Safari, iPhone, Android and Google Drive Viewer
			filename = urllib.parse.quote(str(file_name).encode('utf8'))
		
		if encode_filename_by_b64:
			# for other browser
			logging.info('for other browser:b64 encode')
			self.setResponseHeader('Content-Type', 'public')
			if inline or show_in_browser:
				self.setResponseHeader('Content-Disposition', self.createContentDispositionUtf8(file_name,type='inline')) #'inline; filename="=?utf-8?B?' + filename + '?="')
			else:
				self.setResponseHeader('Content-Disposition', self.createContentDispositionUtf8(file_name,type='attachment')) #'attachment; filename="=?utf-8?B?' + filename + '?="')
			self.setResponseHeader('Content-Type', str(mime_type) + '; charset=utf-8')
		else:
			logging.info('for IE: just quote')
			self.setResponseHeader('Content-Control', 'public')
			if inline or show_in_browser:
				self.setResponseHeader('Content-Disposition', self.createContentDispositionUtf8(file_name,type='inline')) #'inline; filename="' + filename + '"')
			else:
				self.setResponseHeader('Content-Disposition', self.createContentDispositionUtf8(file_name,type='attachment')) #'attachment; filename="' + filename + '"')
			self.setResponseHeader('Content-Control', str(mime_type) + '; charset=utf-8')


def checkDownloadPrivOfCategory(file_id, viewer_email, viewer_user_id, row_doc, tenant_or_domain, other_setting, inline, row_af, do_not_log_operation, screen, mode):
	# for publshed doc: Need check download priv of category
	if inline and isImageFile(row_af):
		# file is Image and trying to show inline of rich text ---> OK to send file even if it is not allowed to download
		return True

	if other_setting.allow_access_author_and_approver:
		if sateraito_func.isOkToAccessDocObj(viewer_email, row_doc, tenant_or_domain, other_setting=other_setting, mode=mode):
			# ok to download
			return True
		else:
			logging.warn('have no priv to download file file_id=' + file_id + ' doc_id=' + row_doc.doc_id + ' category_code=' + row_doc.doc_category_code)
			#self.response.set_status(403)
			if not do_not_log_operation:
				detail = u'FAILED: have no priv to download file on category: file_id=' + file_id + ' category_code=' + row_doc.doc_category_code
				sateraito_db.OperationLog.addLog(viewer_user_id, viewer_email, sateraito_db.OPERATION_DOWNLOAD_FILE, screen, row_doc.doc_id, row_doc.doc_title, detail=detail)
			return False
	else:
		user_accessible_info = sateraito_db.UserAccessibleInfo.getInstance(viewer_email, auto_create=True)
		is_downloadable_category = sateraito_db.DocCategory.isDownloadableCategory(row_doc.doc_category_code, user_accessible_info)
		logging.debug('##### is_downloadable_category=' + str(is_downloadable_category))
		if not is_downloadable_category:
			# check template_viewer, if user is template_viewer, he can download file even if prohibited by category setting
			if row_doc.template_id in sateraito_func.getViewableTemplateIds(viewer_email, tenant_or_domain,
																			user_accessible_info=user_accessible_info):
				# user is template_viewer, he can download
				return True
			else:
				logging.warn('have no priv to download file file_id=' + file_id + ' doc_id=' + row_doc.doc_id + ' category_code=' + row_doc.doc_category_code)
				#self.response.set_status(403)
				if not do_not_log_operation:
					detail = u'FAILED: have no priv to download file on category: file_id=' + file_id + ' category_code=' + row_doc.doc_category_code
					sateraito_db.OperationLog.addLog(viewer_user_id, viewer_email, sateraito_db.OPERATION_DOWNLOAD_FILE, screen, row_doc.doc_id, row_doc.doc_title, detail=detail)
				return False
	return True


class _DownloadAttachedFile(blobstore.BlobstoreDownloadHandler, AttachExportPage):
	
	def downloadFile(self, tenant_or_domain, viewer_email, viewer_user_id, file_id,
					inline=False, screen='', do_not_log_operation=False, is_comment_attach=False,
					show_in_browser=False, skip_ip_address_check=False, is_action_response_attach=False,
					area_manager_mode=False):
		"""
		Args:
			tenant_or_domain: string
			viewer_email: string
			file_id: string
			inline: boolean ... for PDF inline showing in browser or inline image file showing
			screen: string ... for operation log
			do_notlog_operation: boolean
		"""
		# get file
		row_af = None
		if is_comment_attach:
			row_af = sateraito_db.AttachedFile3.getInstance(file_id)
			if row_af is None:
				logging.warn('file_id ' + str(file_id) + ' not found on AttachedFile3')
				return
		elif is_action_response_attach:
			row_af = sateraito_db.AttachedFile4.getInstance(file_id)
			if row_af is None:
				logging.warn('file_id ' + str(file_id) + ' not found on AttachedFile4')
				return
		else:
			row_af = sateraito_db.AttachedFile.getInstance(file_id)
			if row_af is None:
				logging.warn('file_id ' + str(file_id) + ' not found on AttachedFile2')
				return
		
		doc_id = row_af.doc_id
		logging.info('doc_id=' + str(doc_id))
		attached_by_user_email = row_af.attached_by_user_email
		logging.debug('viewer_email=' + viewer_email)
		logging.info('attached_by_user_email=' + attached_by_user_email)

		file_name = row_af.file_name
		mime_type = row_af.mime_type
		other_setting = sateraito_db.OtherSetting.getInstance()
		# ip address check
		if not skip_ip_address_check:
			ip_address_ok = self.checkAllowedIPAddressToDownload(other_setting=other_setting)
			logging.debug('##### ip_address_ok=' + str(ip_address_ok))
			if not ip_address_ok:
				logging.warn('ip address is not OK, have no priv to download file file_id=' + file_id + ' doc_id=' + doc_id)
				#self.response.set_status(403)
				return
		
# 		# mime check ---> changed to extension check
# 		mime_ok = self.checkAllowedMimeToDownload(mime_type, other_setting=other_setting)
# 		if not mime_ok:
# 			logging.warn('mime is not OK, have no priv to download file file_id=' + file_id + ' doc_id=' + doc_id)
# 			self.response.set_status(403)
# 			return
		# extension check
		access_mime_type_attach_file_to_download = other_setting.access_mime_type_attach_file_to_download
		if len(access_mime_type_attach_file_to_download) > 0:
			# need check file by extension
			logging.debug('check by extension...')
			if not sateraito_func.checkByExtension(file_name, access_mime_type_attach_file_to_download, other_setting.access_mime_type_attach_file_to_download_flag):
				# not OK
				logging.warn('mime is not OK, have no priv to download file file_id=' + file_id + ' doc_id=' + doc_id)
				return

		#
		# check DOWNLOAD PRIV of category
		#
		# doc is None ---> user is creating new doc, so OK to download by author
		row_doc = sateraito_db.WorkflowDoc.getInstance(doc_id)
		if row_doc is None:
			if attached_by_user_email != viewer_email:
				# doc not found --> now creating new doc
				# File attach user should be same as file download user
				logging.error('doc not found and attached_by_user_email != viewer_email')
				return make_response('', 400)
			else:
				# unsaved draft doc case:OK to send
				pass
		else:
			if row_doc.published:
				# # for publshed doc: Need check download priv of category
				# if inline and isImageFile(row_af):
				# 	# file is Image and trying to show inline of rich text ---> OK to send file even if it is not allowed to download
				# 	pass
				# elif other_setting.allow_access_author_and_approver:
				# 	if sateraito_func.isOkToAccessDocObj(self.viewer_email, row_doc, tenant_or_domain, other_setting=other_setting, mode=self.mode):
				# 		# ok to download
				# 		pass
				# 	else:
				# 		logging.warn('have no priv to download file file_id=' + file_id + ' doc_id=' + doc_id + ' category_code=' + row_doc.doc_category_code)
				# 		self.response.set_status(403)
				# 		if not do_not_log_operation:
				# 			detail = u'FAILED: have no priv to download file on category: file_id=' + file_id + ' category_code=' + row_doc.doc_category_code
				# 			sateraito_db.OperationLog.addLog(viewer_user_id, viewer_email, sateraito_db.OPERATION_DOWNLOAD_FILE, screen, doc_id, row_doc.doc_title, detail=detail)
				# 		return
				# else:
				# 	user_accessible_info = sateraito_db.UserAccessibleInfo.getInstance(viewer_email, auto_create=True)
				# 	is_downloadable_category = sateraito_db.DocCategory.isDownloadableCategory(row_doc.doc_category_code, user_accessible_info)
				# 	logging.debug('##### is_downloadable_category=' + str(is_downloadable_category))
				# 	if not is_downloadable_category:
				# 		# check template_viewer, if user is template_viewer, he can download file even if prohibited by category setting
				# 		if row_doc.template_id in sateraito_func.getViewableTemplateIds(self.viewer_email, tenant_or_domain):
				# 			# user is template_viewer, he can download
				# 			pass
				# 		else:
				# 			logging.warn('have no priv to download file file_id=' + file_id + ' doc_id=' + doc_id + ' category_code=' + row_doc.doc_category_code)
				# 			self.response.set_status(403)
				# 			if not do_not_log_operation:
				# 				detail = u'FAILED: have no priv to download file on category: file_id=' + file_id + ' category_code=' + row_doc.doc_category_code
				# 				sateraito_db.OperationLog.addLog(viewer_user_id, viewer_email, sateraito_db.OPERATION_DOWNLOAD_FILE, screen, doc_id, row_doc.doc_title, detail=detail)
				# 			return
				check_download = False
				area_store_address_list = None
				if area_manager_mode:
					area_store_address_list = sateraito_func.getAreaStoreAddressList(self.viewer_email, other_setting=other_setting)
					for store_email in area_store_address_list:
						check_download_each = checkDownloadPrivOfCategory(file_id, store_email, '', row_doc, tenant_or_domain, other_setting, inline, row_af, do_not_log_operation, screen, self.mode)
						if check_download_each:
							logging.debug('found downloadable')
							check_download = True
							break
				else:
					check_download = checkDownloadPrivOfCategory(file_id, self.viewer_email, viewer_user_id, row_doc, tenant_or_domain, other_setting, inline, row_af, do_not_log_operation, screen, self.mode)
				if not check_download:
					return
		
		# check action response priv
		if is_action_response_attach:
			if attached_by_user_email != viewer_email:
				ok_to_view_action_response = sateraito_func.isActionResponseViewerDoc(tenant_or_domain, self.viewer_email, row_doc)
				if not ok_to_view_action_response:
					return

		# todo: edited start: tan@vn.sateraito.co.jp (version: 3)
		# file_name = row_af.file_name
		# mime_type = row_af.mime_type
		# todo: edited end
		
		# alfresa special
		root, ext = os.path.splitext(file_name)
		if str(ext).lower() == '.xlsx':
			if mime_type == 'application/vnd.ms-excel':
				logging.info('** need update: file_name=' + str(file_name) + ' mime_type=' + str(mime_type))
				row_af.mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
				row_af.put()
				mime_type = row_af.mime_type
		if str(ext).lower() == '.docx':
			if mime_type == 'application/msword':
				logging.info('** need update: file_name=' + str(file_name) + ' mime_type=' + str(mime_type))
				row_af.mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
				row_af.put()
				mime_type = row_af.mime_type
		if str(ext).lower() == '.pptx':
			if mime_type == 'application/vnd.ms-powerpoint':
				logging.info('** need update: file_name=' + str(file_name) + ' mime_type=' + str(mime_type))
				row_af.mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
				row_af.put()
				mime_type = row_af.mime_type
		
		# try to correct wrong mime-type by 1)Notes Data import tool bug, 2)attached pdf from PC which have no acrobat application
		if mime_type == 'application/x-unknown' or (mime_type == 'application/x-octet-stream' and str(ext).lower() == '.pdf'):
			logging.info('correcting mime type for file_id=' + str(file_id))
			mime_type_list = SateraitoMimeType().get_mime_type_from_extensions(ext)
			if len(mime_type_list) > 0:
				mime_type = mime_type_list[0]
				if sateraito_inc.debug_mode:
					logging.info('** found mime_type:' + str(mime_type))
		
		# check priv
		if viewer_email != attached_by_user_email:
			
			# step1. check comment attach file and show_all_version_doc_comment case
			download_ok_rare_case = False
			row_t = sateraito_db.WorkflowTemplate.getInstance(row_doc.template_id, get_deleted=True)
			show_all_version_doc_comment = row_t.show_all_version_doc_comment
			if is_comment_attach and show_all_version_doc_comment and not row_doc.published:
				# get latest published version of doc and if priv is ok, allow download
				row_doc_latest_published = sateraito_db.WorkflowDoc.getLatestPublishedDoc(row_doc.doc_id)
				if sateraito_func.isOkToAccessDocObj(viewer_email, row_doc_latest_published, tenant_or_domain, mode=self.mode):
					logging.info('DOWNLOAD OK:comment attach file and show_all_version_doc_comment case')
					# OK to Download!!!
					download_ok_rare_case = True
			
			# step2. normal case(if accessible to doc, OK to download attach)
			if not download_ok_rare_case:
				# go check
				download_ok = False
				if area_manager_mode:
					area_store_address_list = sateraito_func.getAreaStoreAddressList(viewer_email, other_setting=other_setting)
					for store_email in area_store_address_list:
						download_ok_each = sateraito_func.isOkToAccessDocObj(store_email, row_doc, tenant_or_domain, mode=self.mode)
						if download_ok_each:
							logging.debug('found download ok')
							download_ok = True
							break
				else:
					download_ok = sateraito_func.isOkToAccessDocObj(viewer_email, row_doc, tenant_or_domain, mode=self.mode)
				# raise error if not ok
				if not download_ok:
					logging.warn('not ok to access file')
					
					if not do_not_log_operation or is_comment_attach:
						detail = u'FAILED: have no priv file_id=' + file_id + ' file name=' + str(file_name) + ' category_code=' + str(row_doc.doc_category_code)
						sateraito_db.OperationLog.addLog(viewer_user_id, viewer_email, sateraito_db.OPERATION_DOWNLOAD_FILE, screen, doc_id, str(row_doc.doc_title), detail=detail)
					return
		
		# go export attached file
		logging.info('mime_type=' + str(mime_type))
		if mime_type == 'application/x-unknown':
			# presume unknown mime type file
			new_mime_type = getImageMimeTypeByExtension(file_name)
			if new_mime_type is not None:
				mime_type = new_mime_type
				logging.info('* presumed unknown mime type by file extension:mime_type=' + str(mime_type))
		self.setHeader(file_name, mime_type, inline=inline, show_in_browser=show_in_browser)
		
		# 2020.06.26 新Googleサイト用添付ファイル対応
		self.setCookieFileDownloadTokenFromParam()

		# download operation logging
		# doc is None --> user is creating new doc, download operation should not be logged
		if do_not_log_operation or row_doc is None or is_comment_attach:
			pass
		else:
			detail = u'file_id=' + file_id + ' file name=' + str(file_name) + ' category_code=' + str(row_doc.doc_category_code)
			sateraito_db.OperationLog.addLog(viewer_user_id, viewer_email, sateraito_db.OPERATION_DOWNLOAD_FILE, screen, doc_id, str(row_doc.doc_title), detail=detail)

		# new version(max 200MB)
		logging.debug('start send blob')
		logging.debug('finished send blob')
		# self.send_blob(row_af.blob_ref, content_type=mime_type)
		return self.send_blob_file(self.send_blob,row_af.blob_ref,content_type=mime_type)
		
	def downloadPdfPrintformFile(self, tenant_or_domain, app_id, doc_id, layout_id, viewer_email):
		logging.info('doc_id=' + str(doc_id))
		# row_doc = sateraito_db.WorkflowDoc.getInstance(doc_id)
		# attached_by_user_email = row_doc.author_email
		# logging.debug('viewer_email=' + viewer_email)
		# logging.info('attached_by_user_email=' + attached_by_user_email)
		# #
		# row_p = sateraito_db.PDFCreateQueue.getInstance(doc_id, layout_id)
		#
		# file_name = row_p.file_name + '.pdf'
		# mime_type = 'application/pdf'
		# other_setting = sateraito_db.OtherSetting.getInstance()
		#
		# # check priv
		# if not (sateraito_func.isOkToAccessDocObj(viewer_email, row_doc, tenant_or_domain, mode=self.mode)):
		# 	logging.warn('not ok to access file')
		# 	self.response.set_status(403)
		# 	return
		# # get fullpath file name
		# gcs_bucket_name = app_identity.get_default_gcs_bucket_name()
		# fullpath_filename = '/' + gcs_bucket_name + '/pdf_printform/' + tenant_or_domain + '/' + app_id + '/' + row_p.doc_id + '/' + row_p.layout_id + '.pdf'
		# # go export attached file
		# self.setHeader(file_name, mime_type)
		# blobstore_filename = '/gs' + fullpath_filename
		# gcs_blob_key = blobstore.create_gs_key(blobstore_filename)
		# self.send_blob(gcs_blob_key)


class _GetActionResponseAttachedFileList(sateraito_page._BasePage):

	def getData(self, tenant_or_domain, row_doc, user_action_id, branch_number, viewer_email):
		# get file list
		attached_file_list = []
		# if sateraito_func.isOkToAccessDocId(viewer_email, doc_id, tenant_or_domain, mode=self.mode):
		if sateraito_func.isOkToAccessDocObj(viewer_email, row_doc, tenant_or_domain, mode=self.mode):
			logging.debug('ok to access')
			q = sateraito_db.AttachedFile4.query()
			q = q.filter(sateraito_db.AttachedFile4.doc_id == row_doc.doc_id)
			q = q.filter(sateraito_db.AttachedFile4.user_action_id == user_action_id)
			q = q.filter(sateraito_db.AttachedFile4.respond_user_email == viewer_email)
			q = q.order(-sateraito_db.AttachedFile4.created_date)
			for key in q.iter(keys_only=True):
				row = key.get()
				if row is None:
					# second try
					row = key.get(use_cache=False, use_memcache=False)
				# check branch_number
				if branch_number is None:
					if row.branch_number is not None:
						continue
				else:
					if row.branch_number != branch_number:
						continue
				attached_file_list.append({
					'file_id': row.file_id,
					'file_name': row.file_name,
					'is_open_as_google_doc_viewer': sateraito_func.checkOpenAsGoogleDocViewer(tenant_or_domain, row.mime_type),
					'is_photo_report': row.is_photo_report,
					'is_photo_report_draft': row.is_photo_report_draft,
					'question_no': row.question_no,
				})
		# export json data
		jsondata = json.JSONEncoder().encode(attached_file_list)
		return jsondata


class _UploadHandlerActionResponse(blobstore.BlobstoreUploadHandler, sateraito_page._BasePage):

	def goAttach(self, tenant_or_domain, app_id, blob_info, doc_id, user_action_id, branch_number, question_no, is_photo_report):
		file_size = blob_info.size
		logging.info('file size=%d' % file_size)
		if file_size > MAX_ATTACH_FILE_SIZE:
			# self.response.out.write('status=too_big')
			ret_dict = {
				'status': 'error',
				'error_code': 'too_big',
			}
			return ret_dict

		file_id = sateraito_func.createNewFileId()

		blob_key = blob_info.key()

		new_blob_info_to_get_file_name = blobstore.BlobInfo(blob_key)
		file_name = new_blob_info_to_get_file_name.filename
		logging.info('file_name=' + file_name)
		file_name = sateraito_func.normalizeFileName(file_name)  # なぜかDB側にC:\などからフルパスで入っている場合があるのでとりあえずここではじく
		logging.info('file_name_normalize=' + file_name)

		# check by file extension
		logging.debug('blob_info.content_type=' + str(blob_info.content_type))
		row_o = sateraito_db.OtherSetting.getInstance()
		access_mime_type_attach_file_to_upload_list = row_o.access_mime_type_attach_file_to_upload
		if len(access_mime_type_attach_file_to_upload_list) > 0:
			# need check file by extension
			logging.debug('check by extension...')
			if not sateraito_func.checkByExtension(file_name, access_mime_type_attach_file_to_upload_list, row_o.access_mime_type_attach_file_to_upload_flag):
				# not OK
				logging.info('wrong extension')
				# self.response.out.write('status=mime_type_is_not_access')
				ret_dict = {
					'status': 'error',
					'error_code': 'mime_type_is_not_access',
				}
				return ret_dict

		row = sateraito_db.AttachedFile4()
		row.file_id = file_id
		row.doc_id = doc_id
		row.user_action_id = user_action_id
		if branch_number is not None:
			row.branch_number = branch_number
		row.respond_user_email = self.viewer_email
		row.is_photo_report = is_photo_report
		if is_photo_report:
			row.is_photo_report_draft = True  # draft at first
			if question_no is not None:
				row.question_no = question_no
		row.file_name = file_name
		row.blob_ref = blob_key
		row.mime_type = blob_info.content_type
		row.attached_by_user_email = self.viewer_email
		row.put()

		# update flag
		q_r = sateraito_db.UserActionResponse.query()
		q_r = q_r.filter(sateraito_db.UserActionResponse.user_action_id == user_action_id)
		q_r = q_r.filter(sateraito_db.UserActionResponse.user_email == self.viewer_email)
		keys_r = q_r.fetch(keys_only=True)
		rows_r = ndb.get_multi(keys_r)
		for row_r in rows_r:
			if branch_number is None or branch_number == '':
				if row_r.user_action_response_branch_number is None:
					# go update
					row_r.has_attach_file = True
					row_r.put()
					break
			else:
				if row_r.user_action_response_branch_number == int(branch_number):
					# go update
					row_r.has_attach_file = True
					row_r.put()
					break
		#
		# key_r = q_r.get(keys_only=True)
		# if key_r is not None:
		# 	row_r = key_r.get()
		# 	row_r.has_attach_file = True
		# 	row_r.put()

		# register blob pointer
		sateraito_db.BlobPointer.registerNew(blob_info, namespace_manager.get_namespace(), pointer_table='AttachedFile4')
		ret_dict = {
			'status': 'ok',
			'error_code': '',
			'file_id': file_id,
		}
		return ret_dict

