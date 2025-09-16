# coding: utf-8

import os,sys, logging, urllib

#GoogleDataApi
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree

# タイムアウトの延長
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(10)

import gdata.oauth
import gdata.sites.client
import gdata.sites.data
import gdata.service
import gdata.data
import gdata.alt.appengine
#import gdata.urlfetch
import atom.service
import gdata.sites
#import gdata.spreadsheet.text_db
import atom
import string
import sateraito_inc

from ucf.gdata.sites.client import *
import gdata.gauth


############################################
## gdata.sites.clientアクセスユーティリティ
############################################
class SitesUtil():

	def createContentEntry(link_parent):
		new_entry = gdata.sites.data.ContentEntry(kind='listitem')
		parent_link = atom.data.Link(rel=gdata.sites.data.SITES_PARENT_LINK_REL,
		                             type='application/atom+xml',
		                             href=link_parent)
		new_entry.link.append(parent_link)
		return new_entry
	createContentEntry = staticmethod(createContentEntry)

	def getSitesClient(app_name, domain, userid, password, site='site', apps_domain=None, **kwargs):
		u'''SitesClientを取得する'''
		client = UcfGDataSitesClient(site=site, domain=domain, **kwargs)

		client.ClientLogin(userid, password, app_name)

		# このおまじないはいらないっぽい（あるとエラーする）
		#gdata.alt.appengine.run_on_appengine(client, store_tokens=True,single_user_mode=True)
		#client.ProgrammaticLogin()
		#gdata.urlfetch.run_on_appengine(client)
		return client
	getSitesClient = staticmethod(getSitesClient)

	def getContentFeedByPath(client, path):
		u''' path指定でContentFeedを取得 '''
		kwargs = {}
		feed = client.getContentFeedByCond(path=path)
		return feed
	getContentFeedByPath = staticmethod(getContentFeedByPath)

	def uploadAttachmentFile(client, file_bytes_data, parent, content_type=None, title=None, description=None, folder_name=None, auth_token=None, **kwargs):
		u''' 指定親ページ、ファイルキャビネットページにファイルをアップロード '''
		# ファイルキャビネットへのアップの場合にフォルダ名が空指定だとエラーする環境を確認したのでNoneにする 2011/06/09　T.ASAO
		if folder_name == '':
			folder_name = None
		file_handle = gdata.data.MediaSource(file_handle=file_bytes_data, content_type=content_type, content_length=len(file_bytes_data), file_path=None, file_name=None)
#		file_handle.setFile(file_bytes_data, content_type)

		# 添付ファイルのみのFeedを取得 2011/11/30
		# parentを追加して、情報の取得量を少なくする 2012/03/14
		kind = 'attachment'
		uri = '%s?parent=%s&kind=%s' % (client.MakeContentFeedUri(), parent.GetNodeId(), kind)
		#uri = '%s?kind=%s' % (client.MakeContentFeedUri(), kind)
		feed = client.GetContentFeed(uri=uri)

		file = None
		# 添付ファイルのアドレスと、これから更新を行うアドレスが等しい場合、entryを取得 2011/11/30
		for attachment_entry in feed.entry:
			if attachment_entry.GetAlternateLink().href == parent.GetAlternateLink().href + '/' + title:
				file = attachment_entry
				break

		# file = client.GetEntry(parent.GetAlternateLink().href + '/' + title + '?attredirects=0&path=' + parent.GetAlternateLink().href)
		# アップロード対象と同名のファイルがすでにある場合、削除後にアップロード 2011/11/29
		if file:
			logging.info('update')
			file.title.text = title
			file.summary.text = description
			client.updateAttachmentEntry(file, file_handle)
		else:
			entry = client.UploadAttachment(file_handle, parent, content_type=content_type, title=title, description=description, folder_name=folder_name)
		# TODO client.UploadAttachmentからなぜか返ってこないので、ここでも返さない
#		return entry
	uploadAttachmentFile = staticmethod(uploadAttachmentFile)

	def deleteAttachmentFile(client, parent, content_type=None, title=None, **kwargs):
		u''' 指定ページを削除 2011/12/07 '''

		# 添付ファイルのみのFeedを取得 2011/11/30
		# parentを追加して、情報の取得量を少なくする 2012/03/14
		kind = 'attachment'
		uri = '%s?parent=%s&kind=%s' % (client.MakeContentFeedUri(), parent.GetNodeId(), kind)
		feed = client.GetContentFeed(uri=uri)
		file = None

		# 添付ファイルのアドレスと、これから更新を行うアドレスが等しい場合、entryを取得 2011/11/30
		for attachment_entry in feed.entry:
			if attachment_entry.GetAlternateLink().href == parent.GetAlternateLink().href + '/' + urllib.parse.quote(str(title)):
				file = attachment_entry
				break
		# 対象が見つかった場合、削除
		if file:
			logging.info('delete')
			client.deleteEntry(file)

		# TODO client.UploadAttachmentからなぜか返ってこないので、ここでも返さない
#		return entry
	deleteAttachmentFile = staticmethod(deleteAttachmentFile)

	def createListDataField():
		u''' リスト書き込み用のフィールドを作成する。 '''
		return gdata.sites.data.Field()
	createListDataField = staticmethod(createListDataField)

	def createListColumnField():
		u''' リスト書き込み用の列を作成する。 '''
		return  gdata.sites.data.Column()
	createListColumnField = staticmethod(createListColumnField)

	def searchAttachmentFile(client, parent, eid):
		u''' お知らせページに添付されている添付ファイルを全て取得する '''
		# ファイルキャビネットへのアップの場合にフォルダ名が空指定だとエラーする環境を確認したのでNoneにする 2011/06/09　T.ASAO
		if folder_name == '':
			folder_name = None
		file_handle = gdata.data.MediaSource(file_handle=file_bytes_data, content_type=content_type, content_length=len(file_bytes_data), file_path=None, file_name=None)

		# 添付ファイルのみのFeedを取得 2011/11/30
		# parentを追加して、情報の取得量を少なくする 2012/03/14
		kind = 'attachment'
		uri = '%s?parent=%s&kind=%s' % (client.MakeContentFeedUri(), parent, kind)
		feed = client.GetContentFeed(uri=uri)
		files = []
		# 添付ファイルのアドレスと、これから更新を行うアドレスが等しい場合、entryを取得 2011/11/30
		for attachment_entry in feed.entry:
			files.append(attachment_entry)

		return files
	searchAttachmentFile = staticmethod(searchAttachmentFile)

	def uploadAttachmentFileOtherUrl(client, file_bytes_data, parent, content_type=None, title=None, url_title=None, description=None, folder_name=None, auth_token=None, **kwargs):
		u''' ファイル名とURLが異なる状態でアップロードを行う '''
		# ファイルキャビネットへのアップの場合にフォルダ名が空指定だとエラーする環境を確認したのでNoneにする 2011/06/09　T.ASAO
		if folder_name == '':
			folder_name = None
		file_handle = gdata.data.MediaSource(file_handle=file_bytes_data, content_type=content_type, content_length=len(file_bytes_data), file_path=None, file_name=title)
		entry = client.UploadAttachment(file_handle, parent, content_type=content_type, title=title, description=description, folder_name=folder_name)
	uploadAttachmentFileOtherUrl = staticmethod(uploadAttachmentFileOtherUrl)


