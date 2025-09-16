# coding: utf-8

import os,sys, logging

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

from gdata.sites.client import SitesClient

CONTENT_FEED_TEMPLATE2 = '/feeds/content/%s/%s/%s/'

###########################################
## gdata.sites.SitesClient をいじるのはいやなので継承クラスを作っていじくる！！
###########################################
class UcfGDataSitesClient(gdata.sites.client.SitesClient):


	def modify_request(self, http_request):
		http_request = gdata.sites.client.SitesClient.modify_request(self, http_request)

		if self.path:
			gdata.client._add_query_param('path', self.path, http_request)
		if self.kind:
			gdata.client._add_query_param('kind', self.kind.join(','), http_request)
		if self.include_deleted:
			gdata.client._add_query_param('include-deleted', self.include_deleted, http_request)
		if self.include_draft:
			gdata.client._add_query_param('include-draft', self.include_draft, http_request)
		if self.max_results:
			gdata.client._add_query_param('max-results', self.max_results, http_request)

		return http_request

	ModifyRequest = modify_request

	def getContentFeedByCond(self, pageid=None, path=None, parent=None, kind=None, include_deleted=False, include_draft=False, max_results=None):
		u''' 条件指定でContentFeedを取得 '''
		self.path=path
		self.kind=kind
		if max_results:
			self.max_results=max_results
		else:
			if path or pageid:
				self.max_results = None
			else:
				self.max_results = 10000
		self.include_deleted=include_deleted
		self.include_draft=include_draft

		if pageid:
			return self.GetContentFeed(url=self.MakeContentFeedUriByPageID(pageid), auth_token=self.auth_token)
		else:
			return self.GetContentFeed(auth_token=self.auth_token)

	def updateContentEntry(self, entry):
		u''' 更新 '''
		self.post(entry, self.make_content_feed_uri(), auth_token=self.auth_token)

	def registContentEntry(self, entry):
		u''' 新規 '''
		self.post(entry, self.make_content_feed_uri(), auth_token=self.auth_token)

	def updateAnnouncementEntry(self, entry):
		u''' ※非推奨（updateEntry推奨） '''
		self.updateEntry(entry)

	def updateEntry(self, entry):
		u''' 更新 '''
		#self.post(entry, self.make_content_feed_uri())
		self.Update(entry, auth_token=self.auth_token)

	def updateAttachmentEntry(self, entry, file_handle):
		u''' 添付ファイル更新 '''
		self.Update(entry, media_source=file_handle, auth_token=self.auth_token)

	def deleteEntry(self, entry):
		u''' 削除 '''
		# self.post(entry, self.make_content_feed_uri())
		self.Delete(entry, auth_token=self.auth_token)

	def registAnnouncementEntry(self, entry, title, html ,number):
		u''' お知らせページ 投稿 を登録'''
		# Django1.2バージョンアップ時、日本語が出力されなくなる為の対応 2011/05/31
		#return self.CreatePage('announcement', title, html=unicode(html,'shift_jis').encode('utf-8'), page_name=number ,parent=entry)
		return self.CreatePage('announcement', title, html=html, page_name=number, parent=entry, auth_token=self.auth_token)

	def registAnnouncementPageEntry(self, entry, title, html ,number):
		u''' お知らせページ を登録'''
		return self.CreatePage('announcementpage', title, html=html, page_name=number, parent=entry, auth_token=self.auth_token)

	def registFilecabinetEntry(self, entry, title, html ,number):
		u''' ファイルキャビネットページ を登録 '''
		return self.CreatePage('filecabinet', title, html=html, page_name=number, parent=entry, auth_token=self.auth_token)

	def registWebPageEntry(self, entry, title, html ,number):
		u''' Webページ を登録'''
		return self.CreatePage('webpage', title, html=html, page_name=number, parent=entry, auth_token=self.auth_token)

	def getContentAccessURL(self, pagepath, pagename):
		url = '%s://%s/a/%s/%s%s/%s?attredirects=0' % ('http', self.host, self.domain, self.site, pagepath, pagename)
		return url
