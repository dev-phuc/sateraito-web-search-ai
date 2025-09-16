# coding: utf-8

try:
  from xml.etree import cElementTree as ElementTree
except ImportError:
  try:
    import cElementTree as ElementTree
  except ImportError:
    try:
      from xml.etree import ElementTree
    except ImportError:
      from elementtree import ElementTree
import urllib
import gdata
import atom.service
import gdata.service
import gdata.apps
import atom

import gdata.alt.appengine

CONTENT_FEED_TEMPLATE2 = '/feeds/content/%s/%s/%s/'


###########################################
## gdata.apps.AppsService ��������̂͂���Ȃ̂Ōp���N���X������Ă�������I�I
###########################################
class UcfGDataAppsService(gdata.apps.service.AppsService):

	def getContentFeedByCond(self, pageid=None, path=None, parent=None, kind=None, include_deleted=False, include_draft=False, max_results=None):
		u''' �����w���ContentFeed���擾 '''
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
			return self.GetContentFeed(url=self.MakeContentFeedUriByPageID(pageid))
		else:
			return self.GetContentFeed()

	def updateContentEntry(self, entry):
		u''' �X�V '''
		self.post(entry, self.make_content_feed_uri())

	def registContentEntry(self, entry):
		u''' �V�K '''
		self.post(entry, self.make_content_feed_uri())

	def updateAnnouncementEntry(self, entry):
		u''' �X�V '''
		# self.post(entry, self.make_content_feed_uri())
		self.Update(entry)


	def registAnnouncementEntry(self, entry, title, html ,number):
		u''' ���m�点�y�[�W ���e '''
		return self.CreatePage('announcement', title, html=unicode(html,'shift_jis').encode('utf-8'), page_name=number ,parent=entry)

	def getContentAccessURL(self, pagepath, pagename):
		url = '%s://%s/a/%s/%s%s/%s?attredirects=0' % ('http', self.host, self.domain, self.site, pagepath, pagename)
		return url

	def deleteEntry(self, entry):
		self.Delete(entry, auth_token=self.auth_token)
