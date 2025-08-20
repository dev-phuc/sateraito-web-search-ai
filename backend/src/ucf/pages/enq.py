# coding: utf-8

# XML関連
#import xml.dom.minidom as dom
#import xml.xpath as xpath
from xml.etree import ElementTree

# import os,sys,math,string, binascii, logging, datetime, base64, re, urllib
# from google.appengine.api import users
# from google.appengine.ext import webapp
# from google.appengine.ext.webapp import template
# from google.appengine.api import mail
# from google.appengine.ext import db
from django.template.context import Context
from django.template import  Template
from django.utils import simplejson

# タイムアウトの延長
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(10)

from ucf.utils.helpers import *
from ucf.utils.validates import BaseValidator
from ucf.config.ucfconfig import *
from ucf.config.ucfmessage import *
from ucf.utils.ucfutil import *
from ucf.utils.mailutil  import *
from ucf.utils.models  import *
from ucf.utils.ucfxml import *
import ucf.gdata.spreadsheet.util
import license.sateraito_inc

from html_editor.editor_func import ConvertHtmlWithJson
from license.sateraito_func import OperatorAttribute
from ucf.gdata.sites.util import SitesUtil
from ucf.utils.numbering import *

############################################################
## ちょっとした定数（このpy内でのみ使用可能）
############################################################
_field_prefix = "FLD"
_cmd_prefix = "cmd_"
_field_type_prefix = "ftp_"
_seq_prefix = "SEQ"
_dispname_prefix = "dn_"
_ext_prefix = "ext_"

_title = '詳細'
_DETAIL_SITES_PAGE = 'DETAIL_SITES_PAGE'
_index_list = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
_FIELD_TYPE = {'LINK':'LINK', 'FILE':'FILE'}

_name_prefix = "nm_"
_type_prefix = "tp_"

############################################################
## ローカルFUNC
############################################################
class QuestionnairePageHelper(FrontHelper):

	QUEST_MASTERINFO_ENTRY_TEMPLATE_FILENAME = 'Templates/@entry'
	QUEST_MASTERINFO_CONFIRM_TEMPLATE_FILENAME = 'Templates/@confirm'
	QUEST_MASTERINFO_THANKS_TEMPLATE_FILENAME = 'Templates/@thanks'
	QUEST_MASTERINFO_SITES_TEMPLATE_FILENAME = 'Templates/@sites'

	QUEST_MASTERINFO_SPREADSHEET_ACCOUNT = 'Spreadsheet/@account'
	QUEST_MASTERINFO_SPREADSHEET_PASSWORD = 'Spreadsheet/@password'
	QUEST_MASTERINFO_SPREADSHEET_KEY = 'Spreadsheet/@key'
	QUEST_MASTERINFO_WORKSHEET_NAME = 'Spreadsheet/@worksheet_name'
	QUEST_MASTERINFO_ENCRYPT = 'Spreadsheet/@encrypt'
	QUEST_MASTERINFO_APPEND_LINK = 'Spreadsheet/@append_link'

	# SelectCondition取得用
	QUEST_SELECT_CONDITION_SPREAD_SHEET = 'spreadsheet'
	QUEST_SELECT_CONDITION_SITES_INFO = 'sitesinfo'
	QUEST_SELECT_CONDITION_SITESLIST_INFO = 'siteslistinfo'
	QUEST_SELECT_CONDITION_CONNECTION = 'connection'

	# 条件式取得用
	QUEST_SELECT_CONDITION_EXPRESSION = 'Expression'
	QUEST_SELECT_CONDITION_EXPRESSION_TARGET = 'target'
	QUEST_SELECT_CONDITION_EXPRESSION_EQUATION = 'equation'
	QUEST_SELECT_CONDITION_EXPRESSION_VALUE = 'value'
	QUEST_SELECT_CONDITION_EXPRESSION_QUO = 'quo'
	QUEST_SELECT_CONDITION_EXPRESSION_TYPE = 'type'

	# SelectConditionから選択されたタブ取得用
	QUEST_SELECT_CONDITION_ACCOUNT = '/@account'
	QUEST_SELECT_CONDITION_PASSWORD = '/@password'
	QUEST_SELECT_CONDITION_KEY = '/@key'
	QUEST_SELECT_CONDITION_WORKSHEET_NAME = '/@worksheet_name'
	QUEST_SELECT_CONDITION_DOMAIN = '/@domain'
	QUEST_SELECT_CONDITION_SITESID = '/@sites_id'
	QUEST_SELECT_CONDITION_PAGEPATH = '/@page_path'
	QUEST_SELECT_CONDITION_TITLE = '/@title'
	QUEST_SELECT_CONDITION_ENCRYPT = '/@encrypt'
	QUEST_SELECT_CONDITION_APPEND_LINK = '/@append_link'

	QUEST_SITESINFO_ACCOUNT = 'SitesInfo/@account'
	QUEST_SITESINFO_PASSWORD = 'SitesInfo/@password'
	QUEST_SITESINFO_DOMAIN = 'SitesInfo/@domain'
	QUEST_SITESINFO_SITESID = 'SitesInfo/@sites_id'
	QUEST_SITESINFO_PAGEPATH = 'SitesInfo/@page_path'
	QUEST_SITESINFO_TITLE = 'SitesInfo/@title'
	QUEST_SITESINFO_ENCRYPT = 'SitesInfo/@encrypt'

	QUEST_SITESLIST_INFO_ACCOUNT = 'SitesListInfo/@account'
	QUEST_SITESLIST_INFO_PASSWORD = 'SitesListInfo/@password'
	QUEST_SITESLIST_INFO_DOMAIN = 'SitesListInfo/@domain'
	QUEST_SITESLIST_INFO_SITESID = 'SitesListInfo/@sites_id'
	QUEST_SITESLIST_INFO_PAGEPATH = 'SitesListInfo/@page_path'
	QUEST_SITESLIST_INFO_ENCRYPT = 'SitesListInfo/@encrypt'
	QUEST_SITESLIST_INFO_APPEND_LINK = 'SitesListInfo/@append_link'

	QUEST_MASTERINFO_MAIL_FROM = 'ThankYouMail/From'
	QUEST_MASTERINFO_MAIL_CC = 'ThankYouMail/Cc'
	QUEST_MASTERINFO_MAIL_CC_FIELD = 'ThankYouMail/Cc/@field'
	QUEST_MASTERINFO_MAIL_BCC = 'ThankYouMail/Bcc'
	QUEST_MASTERINFO_MAIL_BCC_FIELD = 'ThankYouMail/Bcc/@field'
	QUEST_MASTERINFO_MAIL_REPLY_TO = 'ThankYouMail/ReplyTo'
	QUEST_MASTERINFO_MAIL_TO = 'ThankYouMail/To'
	QUEST_MASTERINFO_MAIL_TO_FIELD = 'ThankYouMail/To/@field'
	QUEST_MASTERINFO_MAIL_SUBJECT = 'ThankYouMail/Subject'
	QUEST_MASTERINFO_MAIL_BODY = 'ThankYouMail/Body'
	QUEST_MASTERINFO_MAIL_BODYHTML = 'ThankYouMail/BodyHtml'

	QUEST_FILE_ATTACHMENT_DOMAIN = 'FileAttachmentSitesInfo/Domain'
	QUEST_FILE_ATTACHMENT_SITE_NAME = 'FileAttachmentSitesInfo/SiteName'
	QUEST_FILE_ATTACHMENT_PAGE_PATH = 'FileAttachmentSitesInfo/PagePath'
	QUEST_FILE_ATTACHMENT_FOLDER_NAME = 'FileAttachmentSitesInfo/FolderName'
	QUEST_FILE_ATTACHMENT_ACCOUNT = 'FileAttachmentSitesInfo/Account'
	QUEST_FILE_ATTACHMENT_PASSWORD = 'FileAttachmentSitesInfo/Password'

	QUEST_MASTERINFO_DEFAULT_VALUES_PREFIX = 'DefaultInfo/@'

	QUEST_MASTERINFO_TARGET_FILTER = 'TargetFilter/Field'
	QUEST_MASTERINFO_FIELD_INFO = 'FieldInfo/Field'
	QUEST_MASTERINFO_SELECT_CONDITION = 'SelectCondition/Condition'

	def get(self, domain=None):
		#settings.FILE_CHARSET = UcfConfig.FILE_CHARSET
		self.request.charset = UcfConfig.ENCODING
		self.response.charset = UcfConfig.ENCODING
		self._request_type = UcfConfig.REQUEST_TYPE_POST
		self.init()
		self.onLoad()
		self.processOfRequest(domain)

	def post(self, domain=None):
		#settings.FILE_CHARSET = UcfConfig.FILE_CHARSET
		self.request.charset = UcfConfig.ENCODING
		self.response.charset = UcfConfig.ENCODING
		self._request_type = UcfConfig.REQUEST_TYPE_POST
		self.init()
		self.onLoad()
		self.processOfRequest(domain)

	def __init__(self):
		FrontHelper.__init__(self)
		pass

	def registEntry(self, vo, master_info, sites_url, field_info, attachment_file_urls, number, edit_url, mail_address):
		u''' アンケート回答を１つ新規登録 '''

		account  = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SPREADSHEET_ACCOUNT)
		password = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SPREADSHEET_PASSWORD)
		if UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_ENCRYPT).upper() == 'TRUE':
			password = UcfUtil.deCrypto(password,UcfConfig.CRYPTO_KEY)
		spreadsheet_key = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SPREADSHEET_KEY)
		worksheet_name  = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_WORKSHEET_NAME)
		worksheet_id = None
		append_url = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_APPEND_LINK)
		# spreadsheet_keyが存在しないとき、処理を終了
		if spreadsheet_key == '':
			# 正常に登録されて終了したと判断する
			return True, True
		service = ucf.gdata.spreadsheet.util.getSpreadsheetsService(account, password, self.getRootPath())
		worksheet_id = ucf.gdata.spreadsheet.util.getWorksheetIdByName(service, spreadsheet_key, worksheet_name)
		#ワークシートが存在していればデータ登録
		if not worksheet_id:
			raise Exception([u'failed get worksheet by name, not exist worksheet', spreadsheet_key, worksheet_name])
			return False, False
		else:
			#回答データのキー一覧を作成
			keys = []
			for k in vo.keys():
				# 回答フィールドのキーなら追加
				if k.startswith(_field_prefix):
					keys.append(k)
			#並び替え
			keys.sort()
			logging.info("key:"+str(keys))
			#データ生成
			values=[]
			enq_date = str(UcfUtil.getNowLocalTime())
			# No
			values.append(number)
			# 投稿日
			values.append(enq_date)
			# 投稿者
			values.append(mail_address)

			for key in keys:
				# 添付ファイルの場合、リンクを表示
				if attachment_file_urls and key in attachment_file_urls:
					if key.startswith(_field_prefix):
						if attachment_file_urls[key][0] == '#':
							# リンクがない場合、空欄
							field = ''
						else:
							field = u'=hyperlink("' + attachment_file_urls[key][0] + u'";"' + attachment_file_urls[key][1] + '|' + attachment_file_urls[key][0] + u'")'
						values.append(field)
				else:
					values.append(vo[key])
					logging.info("vo[key]:"+str(vo[key]))
			# データを追加する
			# お知らせページが存在し、append_link が true の時、URLを追加
			if append_url.upper() == 'TRUE' and sites_url != None and sites_url != '':
				field = '=hyperlink("' + str(sites_url) + '";"' + str(sites_url) + '")'
				values.append(field)
			# 回答欄の作成だけは行う
			elif append_url.upper() == 'TRUE':
				field = ''
				values.append(field)
			edit_field = u'=hyperlink("' + edit_url + '&type=spread' + u'";"' + u'編集する' + u'")'
			values.append(edit_field)
			#レコード追加
			logging.info(values)
			ucf.gdata.spreadsheet.util.addWorksheetRecord(service, spreadsheet_key, worksheet_id, values)
			return True, True

	def updateEntry(self, vo, master_info, sites_url, field_info, attachment_file_urls, number, edit_url, mail_address):
		u''' アンケート回答を１つ更新：スプレッドシート '''

		account  = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SPREADSHEET_ACCOUNT)
		password = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SPREADSHEET_PASSWORD)
		if UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_ENCRYPT).upper() == 'TRUE':
			password = UcfUtil.deCrypto(password,UcfConfig.CRYPTO_KEY)
		spreadsheet_key = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SPREADSHEET_KEY)
		worksheet_name  = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_WORKSHEET_NAME)
		worksheet_id = None
		append_url = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_APPEND_LINK)
		# spreadsheet_keyが存在しないとき、処理を終了
		if spreadsheet_key == '':
			# 正常に登録されて終了したと判断する
			return True, True
		service = ucf.gdata.spreadsheet.util.getSpreadsheetsService(account, password, self.getRootPath())
		worksheet_id = ucf.gdata.spreadsheet.util.getWorksheetIdByName(service, spreadsheet_key, worksheet_name)
		#ワークシートが存在していればデータ登録
		if not worksheet_id:
			raise Exception([u'failed get worksheet by name, not exist worksheet', spreadsheet_key, worksheet_name])
			return False, False
		else:
			#回答データのキー一覧を作成
			keys = []
			for k in vo.keys():
				# 回答フィールドのキーなら追加
				if k.startswith(_field_prefix):
					keys.append(k)
			#並び替え
			keys.sort()

			#データ生成
			enq_date = str(UcfUtil.getNowLocalTime())
			data = {}
			count = 1
			for key in keys:
				# 添付ファイルの場合、リンクを表示
				if attachment_file_urls and key in attachment_file_urls:
					if key.startswith(_field_prefix):
						if attachment_file_urls[key][0] == '#':
							# リンクがない場合、空欄
							field = ''
						else:
							# field = u'=hyperlink("' + attachment_file_urls[key][0] + u'";"' + attachment_file_urls[key][1] + u'")'
							field = u'=hyperlink("' + attachment_file_urls[key][0] + u'";"' + attachment_file_urls[key][1] + '|' + attachment_file_urls[key][0] + u'")'
						if 'dn_' + key in vo:
							data[vo['dn_' + key]] = field
						data[u'回答' + str(count)] = field
				else:
					if 'dn_' + key in vo:
						data[vo['dn_' + key]] = vo[key]
					data[u'回答' + str(count)] = vo[key]
				count += 1

			# データを追加する
			# お知らせページが存在し、append_link が true の時、URLを追加
			if append_url.upper() == 'TRUE' and sites_url != None and sites_url != '':
				field = '=hyperlink("' + str(sites_url) + '";"' + str(sites_url) + '")'
				data[u'回答' + str(count)] = field
				data[u'詳細'] = field
				count += 1
			# 空欄上書きの原因となっている為、何も行わない 2013/01/18 T.Seki
			## 回答欄の作成だけは行う
			#elif append_url.upper() == 'TRUE':
			#	data[u'回答' + str(count)] = ''
			#	data[u'詳細'] = ''
			#	count += 1
			# 編集 を追加する
			edit_field = u'=hyperlink("' + edit_url + '&type=spread' + u'";"' + u'編集する' + u'")'
			data[u'回答' + str(count)] = edit_field
			data[u'編集'] = edit_field
			# WHERE句
			wheres = []
			wheres.append(u'no' + '=' + number)
			query = createListQuery(wheres)
			feed = getListFeedByCond(service, spreadsheet_key, worksheet_id, query.encode('utf-8'))
			if len(feed.entry) == 1:
				entry = feed.entry[0]
				ucf.gdata.spreadsheet.util.updateWorksheetRecord(service, entry, data)
			return True, True

	
	def registEntrySites(self, vo, master_info, field_info, attachment_file_urls, number, is_via_subpage=False, apps_domain=None):
		u''' 生成ページをサイツに登録 
			is_via_subpage…サブページとして作ってからお知らせページの子として移動する！（500件問題対策）
		'''
		ucfp = UcfFrontParameter(self)

		account  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_ACCOUNT)
		password = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_PASSWORD)
		if UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_ENCRYPT).upper() == 'TRUE':
			password = UcfUtil.deCrypto(password,UcfConfig.CRYPTO_KEY)
		domain = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_DOMAIN)
#		if domain == '' and len(account.split('@')) > 1:
#			domain = account.split('@')[1]
		if domain == '':
			domain = 'site'
		sites_id  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_SITESID)
		page_path  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_PAGEPATH)
		title = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_TITLE)
		url = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SITES_TEMPLATE_FILENAME)

		target_entry = None
		# sites_idが存在しないとき、処理を終了
		if sites_id == '':
			# 正常に登録されて終了したと判断する
			return True, True, '', attachment_file_urls, True
		client = None

		try:
			client = SitesUtil.getSitesClient('sateraito-apps-kakuchou-form', domain, account, password, site=sites_id, apps_domain=apps_domain)

			# 既存ページの存在確認
			logging.info('************************************************************************')
			logging.info('client:'+str(client))
			logging.info('page_path:'+str(page_path))
			feed = SitesUtil.getContentFeedByPath(client, page_path)
			logging.info('feed:'+str(feed))
			for entry in feed.entry:
				logging.info('entry:'+str(entry))
				target_entry = entry
				break
		except Exception as e:
			logging.info('registEntrySites1: ' + str(e))

			# 既存ページが存在しない場合にはエラーが発生したとして処理する
			self.outputErrorLog(e)
			return False, False, None, attachment_file_urls, False

		logging.info('is_via_subpage:'+str(is_via_subpage))

		# 削除処理の為に外で宣言
		parent = None
		try:
			if target_entry:
				#サイツページが存在していれば更新
				# 新しいページ（一時的なページ）をサイトに作成(ページへのリンクを取得)
				html = 'アップロードに失敗しました'
				title = UcfUtil.editInsertTag(title, vo, '[$$', '$$]')
				logging.info('title:'+str(title))
				link = None
				# 通常パターン…お知らせページの子ページとして直接作成
				if not is_via_subpage:
					logging.info('html:'+str(html))
					logging.info('target_entry:'+str(target_entry))
					link = client.registAnnouncementEntry(target_entry, title, html, number)
					logging.info('link:'+str(link))
				# サブページとして作ってから移動するパターン（500件問題）
				else:

					# 存在する既存ページの下にあるお知らせページを取得する
					feed = None
					target_feed = None
					# target_entry（お知らせページ）のコンテンツIDを取得し、それをuriに設定して子要素を取得
					kind = 'announcement'
					# 負荷軽減のため取得を1件にする 2012/10/19 T.ASAO
					#uri = '%s?parent=%s' % (client.MakeContentFeedUri(), target_entry.GetNodeId())
					uri = '%s?parent=%s&max-results=0' % (client.MakeContentFeedUri(), target_entry.GetNodeId())
					logging.info('uri=' + uri)
					try:
						target_feed = client.GetContentFeed(uri=uri)
					except Exception as e:
						logging.error(e)
						# 見つからなかった場合エラー
						return False, False, None, attachment_file_urls, True
					logging.info(len(target_feed.entry))

					# 移動先のページパスを作成
					dest_page_path = ''
					if page_path.endswith('/'):
						dest_page_path = page_path + number
					else:
						dest_page_path = page_path + '/' + number

					logging.info('dest_page_path=' + dest_page_path)

					# 移動先のページの存在チェック
					# 一見書き込みに成功しているかのような動作をするため、ここには入らないように注意
					dest_entry = None
					dest_feed = SitesUtil.getContentFeedByPath(client, dest_page_path)
					for entry in dest_feed.entry:
						dest_entry = entry
						break
					if dest_entry:
						# すでに存在する場合、処理を終了する（成功？失敗？とりあえず失敗か.ないはずだからここにきているわけだから）
						return False, False, None, attachment_file_urls, True

					if target_feed is not None:
						# お知らせページのサブページのどれかに対して一時的にサブページを作成
						for entry_child_entry in target_feed.entry:	# （enq001～） …1つ目でbreakする
							try:
								logging.info('entry_child_entry:'+str(entry_child_entry))
								logging.info('html:'+str(html))
								logging.info('SUPPORT_KINDS[1]:'+str(gdata.sites.data.SUPPORT_KINDS[1]))
								logging.info('SUPPORT_KINDS[0]:'+str(gdata.sites.data.SUPPORT_KINDS[0]))
								# 投稿されたページ（entry_child_entry）には直接サブページが作れないため（権限の問題かな）、announcement（お知らせ）ページを1つはさんでその下に作成する
								parent = client.CreatePage(gdata.sites.data.SUPPORT_KINDS[1], title, html=html, page_name=number, parent=entry_child_entry)	# SUPPORT_KIND[1]…announcement
								logging.info('link parent:'+str(parent.GetAlternateLink().href))
								link = client.CreatePage(gdata.sites.data.SUPPORT_KINDS[0], title, html=html, page_name=number, parent=parent)							# SUPPORT_KIND[0]…announcementspage
								break
							except Exception as e:
								logging.error(e)
								logging.info(entry_child_entry.kind())
								return False, False, None, attachment_file_urls, True

					# kind = announcement, parent = target_entry.id.text[target_entry.id.text.rfind('/') + 1:] に書き換える
					# target_entryへアップロードの実行(linkのデータを移動する ※ link.page_name(親ページID)を変更することで、移動する!)
					for link_node in link.link:
						if link_node.rel.endswith('parent'):
							link_node.href = target_entry.id.text
					link.content = gdata.sites.data.Content(text=html)
					created_entry = client.updateEntry(link)
					# parent を削除
					logging.info('page_delete : ' + parent.GetAlternateLink().href)
					client.deleteEntry(parent)

				link_href = None
				if link:
					# 登録したlinkを利用して添付ファイル用リンク作成
					#self.createAttachmentFilesIntendUrl(vo, client, field_info, attachment_file_urls, number, sites_id, link)
					link_href = link.GetAlternateLink().href
				return True, True, link_href, attachment_file_urls, True
			#存在してなければ新規
			else:
				# TODO とりあえず既存ページがある前提
				return False, False, None, attachment_file_urls, False
		except Exception as e:
			logging.info('registEntrySites2 ' + str(e))
			self.outputErrorLog(e)
			# 作成されたページが残っていた場合の対策として、ここで作成したページを削除する 2013/03/13
			if parent is not None:
				logging.info('page_delete : ' + parent.GetAlternateLink().href)
				client.deleteEntry(parent)
			# お知らせページは存在している
			return False, False, None, attachment_file_urls, True

	def updateEntrySites(self, vo, master_info, field_info, attachment_file_urls, number, edit_url, dept_id, operator, apps_domain=None):
		u''' サイツページを更新 '''
		ucfp = UcfFrontParameter(self)

		account  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_ACCOUNT)
		password = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_PASSWORD)
		if UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_ENCRYPT).upper() == 'TRUE':
			password = UcfUtil.deCrypto(password,UcfConfig.CRYPTO_KEY)
		domain = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_DOMAIN)
#		if domain == '' and len(account.split('@')) > 1:
#			domain = account.split('@')[1]
		if domain == '':
			domain = 'site'
		sites_id  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_SITESID)
		page_path  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_PAGEPATH)
		title = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_TITLE)
		url = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SITES_TEMPLATE_FILENAME)

		target_entry = None
		# sites_idが存在しないとき、処理を終了
		if sites_id == '':
			# 正常に登録されて終了したと判断する
			return True, True, '', attachment_file_urls

		entry = None
		try:
			client = SitesUtil.getSitesClient('sateraito-apps-kakuchou-form', domain, account, password, site=sites_id, apps_domain=apps_domain)

			# 既存ページの存在確認
			feed = SitesUtil.getContentFeedByPath(client, page_path)
			for entry_data in feed.entry:
				target_entry = entry_data
				break
			# 更新対象ページの存在確認
			target_feed = SitesUtil.getContentFeedByPath(client, page_path + '/' + number)
			for entry_data in target_feed.entry:
				entry = entry_data
				break
			#サイツページが存在していれば更新
			if target_entry and entry:
				# 添付ファイルを登録する場合、先にアドレスを作成(作成済みなため、削除)
				# self.createAttachmentFilesIntendUrl(vo, client, field_info, attachment_file_urls, number, sites_id, target_entry)
				#回答データの一覧を作成
				keys = {}
				for k,v in vo.items():
					# 添付ファイルの場合、内容の変更
					if attachment_file_urls and k in attachment_file_urls:
						if k.startswith(_field_prefix):
							if attachment_file_urls[k][0] == '#':
								# リンクがない場合、空欄
								keys[k] = ''
							else:
								keys[k] = (u'<a href="' + attachment_file_urls[k][0] + u'">' + attachment_file_urls[k][1] + u'</a>')
					# 回答フィールドなら追加
					elif k.startswith(_field_prefix):
						# ファイルオブジェクトなどをスルーするために変換できないものは無視
						try:
							keys[k] = v
						except:
							pass
				# 画像取得用にTOPのURLをセット 04/15
				keys['DETAIL_TOP_URL'] = target_entry.GetAlternateLink().href

				vals = {
					 'voVH': keys
					,'EDIT_URL': edit_url + '&type=sites'
					,'my_site_url': license.sateraito_inc.my_site_url
					,'domain': domain
					,'ope': operator
					,'ATTACHMENT_URL': vo['ATTACHMENT_URL']
				}
				# パラメータをHTMLに埋め込み、テキストとして取得
				html = self.getSitesHtml(url,vals, dept_id)
				# titleへパラメータを埋め込む
				title = UcfUtil.editInsertTag(title, vo, '[$$', '$$]')
				entry.title.text = title
				entry.content = gdata.sites.data.Content(text=html)
				client.updateAnnouncementEntry(entry)
				link = entry.GetAlternateLink().href
				self.uploadAttachmentFilesForDetailPage(vo, client, entry, field_info, attachment_file_urls, sites_id)
				return True, True, link, attachment_file_urls
			#存在してなければ新規
			else:
				# TODO とりあえず既存ページがある前提
				return False, False, None, attachment_file_urls
		except Exception as e:
			logging.info('updateEntrySites ' + str(e))
			# エラーにはせず、ログを出力
			self.outputErrorLog(e)
			if entry is not None:
				link = entry.GetAlternateLink().href
			else:
				link = None
			return False, False, link, attachment_file_urls

	def updateEntrySitesRetry(self, vo, master_info, field_info, attachment_file_urls, number, edit_url, dept_id, operator, apps_domain=None):
		u''' サイツページを更新 '''
		ucfp = UcfFrontParameter(self)

		account  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_ACCOUNT)
		password = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_PASSWORD)
		if UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_ENCRYPT).upper() == 'TRUE':
			password = UcfUtil.deCrypto(password,UcfConfig.CRYPTO_KEY)
		domain = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_DOMAIN)
#		if domain == '' and len(account.split('@')) > 1:
#			domain = account.split('@')[1]
		if domain == '':
			domain = 'site'
		sites_id  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_SITESID)
		page_path  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_PAGEPATH)
		title = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_TITLE)
		url = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SITES_TEMPLATE_FILENAME)

		target_entry = None
		# sites_idが存在しないとき、処理を終了
		if sites_id == '':
			# 正常に登録されて終了したと判断する
			return None

		client = SitesUtil.getSitesClient('sateraito-apps-kakuchou-form', domain, account, password, site=sites_id, apps_domain=apps_domain)
		entry = None

		# 既存ページの存在確認
		feed = SitesUtil.getContentFeedByPath(client, page_path)
		for entry_data in feed.entry:
			target_entry = entry_data
			break
		# 存在する既存ページの下にあるお知らせページを取得する
		feed = None
		target_feed = None
		# target_entry のコンテンツIDを取得し、それをuriに設定して子要素を取得
		kind = 'announcement'
		uri = '%s?parent=%s' % (client.MakeContentFeedUri(), target_entry.GetNodeId())
		try:
			target_feed = client.GetContentFeed(uri=uri)
		except Exception as e:
			# 見つからなかった場合、そのまま処理を継続
			pass
		# 移動先予定のURLがすでに存在する場合、処理を中止
		# 一見書き込みに成功しているかのような動作をするため、ここには入らないように注意
		dest_page_path = ''
		if page_path.endswith('/'):
			dest_page_path = page_path + number
		else:
			dest_page_path = page_path + '/' + number
		dest_entry = None
		dest_feed = SitesUtil.getContentFeedByPath(client, dest_page_path)
		for entry in dest_feed.entry:
			dest_entry = entry
			break
		if dest_entry:
			# すでに存在する場合、処理を終了する
			return None
		
#		feed = SitesUtil.getContentFeedByPath(client, page_path)
#		for entry_data in feed.entry:
#			target_entry = entry_data
#			break

		#サイツページが存在していれば更新
		if target_entry:
			# 添付ファイルを登録する場合、先にアドレスを作成(作成済みなため、削除)
			#回答データの一覧を作成
			keys = {}
			for k,v in vo.items():
				# 添付ファイルの場合、内容の変更
				if attachment_file_urls and k in attachment_file_urls:
					if k.startswith(_field_prefix):
						if attachment_file_urls[k][0] == '#':
							# リンクがない場合、空欄
							keys[k] = ''
						else:
							keys[k] = (u'<a href="' + attachment_file_urls[k][0] + u'">' + attachment_file_urls[k][1] + u'</a>')
				# 回答フィールドなら追加
				elif k.startswith(_field_prefix):
					# ファイルオブジェクトなどをスルーするために変換できないものは無視
					try:
						keys[k] = v
					except:
						pass
			# 画像取得用にTOPのURLをセット 04/15
			keys['DETAIL_TOP_URL'] = target_entry.GetAlternateLink().href
			vals = {
				 'voVH': keys
				,'EDIT_URL': edit_url + '&type=sites'
				,'my_site_url': license.sateraito_inc.my_site_url
				,'domain': domain
				,'ope': operator
				,'ATTACHMENT_URL': vo['ATTACHMENT_URL']
			}
			# パラメータをHTMLに埋め込み、テキストとして取得
			html = self.getSitesHtml(url,vals,dept_id)

			# titleへパラメータを埋め込む
			title = UcfUtil.editInsertTag(title, vo, '[$$', '$$]')
			link = None
			parent = None
			if target_feed is not None:
				for entry_child_entry in target_feed.entry:
					try:
						# link = client.registAnnouncementEntry(entry_child_entry, title, html, number)
						# 投稿されたページ（entry_child_entry）には直接サブページが作れないため（権限の問題かな）、announcement（お知らせ）ページを1つはさんでその下に作成する
						parent = client.CreatePage(gdata.sites.data.SUPPORT_KINDS[1], title, html='', page_name=number, parent=entry_child_entry)	# SUPPORT_KIND[1]…announcement
						link = client.CreatePage(gdata.sites.data.SUPPORT_KINDS[0], title, html='', page_name=number, parent=parent)							# SUPPORT_KIND[0]…announcementspage
						break
					except Exception as e:
						logging.info(e)
						logging.info(entry_child_entry.kind())
						pass

			# kind = announcement, parent = target_entry.id.text[target_entry.id.text.rfind('/') + 1:] に書き換える
			# target_entryへアップロードの実行(linkのデータを移動する ※ link.page_name(親ページID)を変更することで、移動する!)
			for link_node in link.link:
				if link_node.rel.endswith('parent'):
					link_node.href = target_entry.id.text
			link.content = gdata.sites.data.Content(text=html)
			result = client.updateEntry(link)
			self.uploadAttachmentFilesForDetailPage(vo, client, link, field_info, attachment_file_urls, sites_id)
			# parent を削除
			client.deleteEntry(parent)
			return result

		#存在してなければ新規
		else:
			# TODO とりあえず既存ページがある前提
			return None

	def registEntryListSites(self, vo, master_info, sites_url, filter_xml, field_info, attachment_file_urls, apps_domain=None):
		u''' サイツのリストに登録 '''
		ucfp = UcfFrontParameter(self)
		# master_info から必要な情報を取得
		account = UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_ACCOUNT)
		password = UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_PASSWORD)
		if UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_ENCRYPT).upper() == 'TRUE':
			password = UcfUtil.deCrypto(password,UcfConfig.CRYPTO_KEY)

		domain = UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_DOMAIN)
		logging.info('domain:'+str(domain))
#		if domain == '' and len(account.split('@')) > 1:
#			domain = account.split('@')[1]
		if domain == '':
			domain = 'site'
		sites_id = UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_SITESID)
		page_path = UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_PAGEPATH)
		append_url = UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_APPEND_LINK)

		logging.info('sites_id:'+str(sites_id))
		logging.info('page_path:'+str(page_path))
		logging.info('append_url:'+str(append_url))
		# field等の設定に使用するindexの内容をここで作成
		target_entry = None
		content = None
		field_name = {}
		field_value = {}
		# sites_idが存在しないとき、処理を終了

		if sites_id == '':
			# 正常に登録されて終了したと判断する
			return True, True, ''
		try:
			# Client取得
			client = SitesUtil.getSitesClient('sateraito-apps-kakuchou-form', domain, account, password, site=sites_id, apps_domain=apps_domain)
			# 既存ページの存在確認
			feed = SitesUtil.getContentFeedByPath(client, page_path)
			logging.info('feed:'+str(feed))
			for entry in feed.entry:
				logging.info('entry:'+str(entry))
				target_entry = entry
				break

			# 取得したリクエストの列名、内容を別々に格納
			logging.info('vo.item:'+str(vo.items()))
			for k, v in vo.items():
				if attachment_file_urls and k in attachment_file_urls:
					# 添付ファイルの場合、内容の変更
					field_value[k] = '<a href="' + attachment_file_urls[k][0] + '">' + attachment_file_urls[k][1] + '</a>'
					logging.info('field_value[k]:'+str(field_value[k]))
				elif k.startswith(_field_prefix):
					field_value[k] = v
					logging.info('else field_value[k]:'+str(field_value[k]))
				if k.startswith(_dispname_prefix):
					# dn_ を除く部分をkeyとする。
					field_name[k[3:]] = v
			# ListItemを取得
			li = client.GetContentFeed(target_entry.feed_link.href)
			logging.info('li:'+str(li))
			# Columnの値を作成
			create_flag = self.createColumnNode(target_entry, field_name, filter_xml)
			logging.info('create_flag:'+str(create_flag))
			# エラーが発生した場合、終了
			logging.info("target_entry.data.column:"+str(target_entry.data.column))
			if target_entry.data.column is None:
				return False, False

			# アイテムを作成に必要な情報が不明な為、既存のListItemを使用
			for entry in li.entry:
				content = entry
				logging.info('content:'+str(content))
				break

			# Fieldの値を作成
			d = UcfUtil.getNow()
			now = UcfUtil.getLocalTime(d)
			now_date = str(now.strftime("%Y/%m/%d %H:%M:%S"))
			logging.info("content:"+str(content))
			logging.info("field_name:"+str(field_name))
			logging.info("field_value:"+str(field_value))
			logging.info("filter_xml:"+str(filter_xml))
			logging.info("sites_url:"+str(sites_url))
			logging.info("append_url:"+str(append_url))
			logging.info("now_date:"+str(now_date))

			self.createFieldNode(content, field_name, field_value, filter_xml, sites_url, append_url, now_date)
			# エラーが発生した場合、終了
			if content.field is None:
				return False, False, ''
			#サイツページが存在していれば更新
			#タイトル列を変更するためにアップロード
			if target_entry and create_flag:
				logging.info('target_entry:'+str(target_entry))
				client.updateAnnouncementEntry(target_entry)

			# 作成したListItemを、アップロード
			upload_content = client.post(content, client.make_content_feed_uri(), auth_token=None)
			logging.info('upload_content:'+str(upload_content))
			return True, True, upload_content.GetNodeId()
		except Exception as e:
			# エラーにはせず、ログを出力
			logging.info('registEntryListSites ' + str(e))
			self.outputErrorLog(e)
			return False, False, ''

	def updateEntryListSites(self, vo, master_info, sites_url, filter_xml, field_info, attachment_file_urls, node_id, apps_domain=None):
		u''' サイツのリストを更新 '''
		ucfp = UcfFrontParameter(self)
		# master_info から必要な情報を取得
		account  = UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_ACCOUNT)
		password = UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_PASSWORD)
		if UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_ENCRYPT).upper() == 'TRUE':
			password = UcfUtil.deCrypto(password,UcfConfig.CRYPTO_KEY)

		domain = UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_DOMAIN)
#		if domain == '' and len(account.split('@')) > 1:
#			domain = account.split('@')[1]
		if domain == '':
			domain = 'site'
		sites_id  = UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_SITESID)
		page_path  = UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_PAGEPATH)
		append_url = UcfUtil.getHashStr(master_info, self.QUEST_SITESLIST_INFO_APPEND_LINK)

		# field等の設定に使用するindexの内容をここで作成
		target_entry = None
		content = None
		field_name = {}
		field_value = {}
		# sites_idが存在しないとき、処理を終了
		if sites_id == '':
			# 正常に登録されて終了したと判断する
			return True, True
		try:
			# Client取得
			client = SitesUtil.getSitesClient('sateraito-apps-kakuchou-form', domain, account, password, site=sites_id, apps_domain=apps_domain)
			# 既存ページの存在確認
			feed = SitesUtil.getContentFeedByPath(client, page_path)
			for entry in feed.entry:
				target_entry = entry
				break

			# 取得したリクエストの列名、内容を別々に格納
			for k, v in vo.items():
				if attachment_file_urls and k in attachment_file_urls:
					# 添付ファイルの場合、内容の変更
					field_value[k] = '<a href="' + attachment_file_urls[k][0] + '">' + attachment_file_urls[k][1] + '</a>'
				elif k.startswith(_field_prefix):
					field_value[k] = v
				if k.startswith(_dispname_prefix):
					# dn_ を除く部分をkeyとする。
					field_name[k[3:]] = v
			# ListItemを取得
			li = client.GetContentFeed(target_entry.feed_link.href)
			# Columnの値を作成
			create_flag = self.createColumnNode(target_entry, field_name, filter_xml)
			# エラーが発生した場合、終了
			if target_entry.data.column is None:
				return False, False
			# 編集対象を捜査（idが一致するか）
			content = None
			for entry2 in li.entry:
				if entry2.GetNodeId() == node_id:
					content = entry2
					break
			if content:
				date = ''
				for item in content.field:
					if item.index == 'A':
						date = item.text
						break
				self.createFieldNode(content, field_name, field_value, filter_xml, sites_url, append_url, date)
				client.updateAnnouncementEntry(content)
			# Fieldの値を上書き
			# self.createFieldNode(content, field_name, field_value, filter_xml, sites_url, append_url, str(now.strftime("%Y/%m/%d %H:%M:%S")))
			# 対象が存在しない時、正常終了と判断
			if content is None:
				return True, True
			# エラーが発生した場合、終了
			elif content.field is None:
				return False, False
			#サイツページが存在していれば更新
			if target_entry and create_flag:
				client.updateAnnouncementEntry(target_entry)

			# 作成したListItemを、アップロード
		#	client.post(content, client.make_content_feed_uri(), auth_token=None)
			return True, True
		except Exception as e:
			# エラーにはせず、ログを出力
			logging.info('updateEntryListSites ' + str(e))
			self.outputErrorLog(e)
			return False, False

	def createColumnNode(self, target_entry , field_name, filter_xml):
		set_flag = True
		# 一覧の列名がすでにセットされているかチェック
		try:
			if filter_xml is None or filter_xml == []:
				for i in range(len(field_name.keys())):
					key = _field_prefix+ str(i + 1).zfill(2)
					if target_entry.data.column[i + 1].name != field_name[key]:
						# 列名が一致しない場合、False
						set_flag = False
						break
			else:
				index = 1
				for node in filter_xml:
					key = node.getAttribute('id')
					# 列名が一致しない場合、False
					if key == 'URL':
						if target_entry.data.column[index].name != str(_title, 'utf-8'):
							set_flag = False
							break
					else:
						if target_entry.data.column[index].name != field_name[key]:
							set_flag = False
							break
					index += 1
		except Exception as e:
			# ログを出力し、処理を継続する
			self.outputErrorLog(e)
			logging.info('createColumnNode 1 ' + str(e))
			set_flag = False
		# 全て一致した場合、Falseを返して処理を終わる
		if set_flag:
			return False;

		url_flag = False
		# 列名を再生成
		target_entry.data.column = []
		index= 0
		try:
			# 先頭の投稿日を追加
			column = SitesUtil.createListColumnField()
			column.index = _index_list[index]
			column.name = str("投稿日","utf-8")
			target_entry.data.column.append(column)
			# フィルターが存在しない場合、全て出力
			if filter_xml is None or filter_xml == []:
				for i in range(len(field_name.keys())):
					key = _field_prefix+ str(i + 1).zfill(2)
					column = SitesUtil.createListColumnField()
					column.index = _index_list[index + 1]
					column.name = field_name[key]
					target_entry.data.column.append(column)
					index += 1
			else:
				# フィルターが存在する場合、それを適用する
				for node in filter_xml:
					key = node.getAttribute('id')
					column = SitesUtil.createListColumnField()
					column.index = _index_list[index + 1]
					index += 1
					if key == 'URL':
						# keyが'URL'の場合、フラグを成立させる
						url_flag = True
						column.name = str(_title, 'utf-8')
						target_entry.data.column.append(column)
					else:
						column.name = field_name[key]
						target_entry.data.column.append(column)
			# フラグが成立しなかった場合、末尾へ追加
			if url_flag == False:
				# 末尾にお知らせへのリンク(詳細)を追加
				column = SitesUtil.createListColumnField()
				column.index = _index_list[index + 1]
				column.name = str(_title,"utf-8")
				target_entry.data.column.append(column)
			return True
		except Exception as e:
			# エラーにはせず、ログを出力
			self.outputErrorLog(e)
			logging.info('createColumnNode 2 ' + str(e))
			# ゴミを残さない為、すべて削除
			target_entry.data.column = None
			return False

	def createFieldNode(self, content, field_name, field_value, filter_xml, sites_url, append_url, date):
		url_flag = False
		# フィールドを初期化
		content.field = []
		field_index = 0
		try:
			field = SitesUtil.createListDataField()
			logging.info("field:"+str(field))
			# 先頭に投稿日を設定
			field.index = _index_list[field_index]
			field.name = str("投稿日","utf-8")
			field.text = date
			content.field.append(field)
			if filter_xml is None or filter_xml == []:
				# 所得リクエスト内容からフィールドを作成
				for i in range(len(field_name.keys())):
					key = _field_prefix + str(i + 1).zfill(2)
					# 新規追加列を作成する。
					field = SitesUtil.createListDataField()
					field.index = _index_list[i + 1]
					field.name = field_name[key]
					field.text = field_value[key]
					#print _index_list[i], key, str(field_name[key]).encode('Shift_JIS'),str(field_value[key]).encode('Shift_JIS')
					content.field.append(field)
					field_index += 1
				# URLの追加を行わない場合、ここで空のアイテムを追加
				logging.info('append_url.upper:'+str(append_url.upper()))
				if append_url.upper() != 'TRUE' or sites_url is None or sites_url == '':
					url_flag = True
					field = SitesUtil.createListDataField()
					field.index = _index_list[field_index + 1]
					field.name = str(_title,"utf-8")
					# 空欄の場合、エラーになる為空のリンクで対処
					field.text = u'<a href="">※詳細無し</a>'
					field_index += 1
					content.field.append(field)
			else:
				for node in filter_xml:
					key = node.getAttribute('id')
					if not key:
						key = ''
					field = SitesUtil.createListDataField()
					field.index = _index_list[field_index + 1]
					if key.upper() == 'URL':
						url_flag = True
						if node.getAttribute('link_disp') is not None and append_url == 'true' and sites_url != '' and sites_url is not None:
							field.name = str(_title,"utf-8")
							field.text = str('<a href="' + str(sites_url) + '">' + str(node.getAttribute('link_disp').encode('utf-8')) + '</a>', 'utf-8')

						else:
							field.name = str(_title,"utf-8")
							# 空欄の場合、エラーになる為空のリンクで対処
							field.text = u'<a href="">※詳細無し</a>'
						field_index += 1
						content.field.append(field)
					else:
						field.name = field_name[key]
						field.text = field_value[key]
						content.field.append(field)
						field_index += 1
			# お知らせページが存在し、append_url が true の時、URLを追加
			if append_url.upper() == 'TRUE' and sites_url is not None and sites_url != '' and url_flag == False:
				field = SitesUtil.createListDataField()
				field.index = _index_list[field_index + 1]
				field.name = str(_title,"utf-8")
				field.text = str('<a href="' + str(sites_url) + '">' + str(sites_url) + '</a>', 'utf-8')
				content.field.append(field)
			return
		except Exception as e:
			# エラーにはせず、ログを出力
			self.outputErrorLog(e)
			logging.info('createFieldNode ' + str(e))
			# ゴミを残さない為、すべて削除
			content.field = None
			return

	def getSitesHtml(self, html_file_name , vals, dept_id):
		info = {}
		# HTMLファイルのパスを作成
		# html_file_path = './templates/' + html_file_name

		html_text = ''
		gql = ""
		wheres = []
		wheres.append("template_id='" + html_file_name + "'")
		wheres.append("del_flag=''")
		wheres.append("dept_id='" + dept_id + "'")

		gql += UcfUtil.getToGqlWhereQuery(wheres)
		models = UCFMDLExtFormTemplate.gql(gql)
		# BigtableからテンプレートHTMLを取得

		for model in models:
			html_text = model.template_html
			break
		html_text = Template(html_text)
		context_html = Context(vals)
		if context_html and html_text:
			# ファイルが存在した場合、Djangoテンプレートに沿って値の埋め込み
			return html_text.render(context_html)
		else:
			# エラーの場合、何も返さない
			return

	def sendThankyouMail(self, vo, master_info):
		''' サンキューメールを送信する '''

		# Toが固定の場合に対応 2011/04/27 
		to_field = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_TO_FIELD )
		to       = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_TO )
		# google app engine管理者のメールアドレスで固定するため削除 2011/09/02
		# sender   = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_FROM )
		sender   = license.sateraito_inc.SENDER_EMAIL
		subject  = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_SUBJECT )
		body     = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_BODY )
		body_html= UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_BODYHTML )
		reply_to = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_REPLY_TO )
		cc       = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_CC )
		cc_field = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_CC_FIELD )
		bcc      = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_BCC )
		bcc_field= UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_BCC_FIELD )

		#to_fieldが設定されていたらメール送信
		if (to and to!='') or (to_field and to_field!='') or (cc and cc!='') or (cc_field and cc_field!='') or (bcc and bcc!='') or (bcc_field and bcc_field!=''):
#			#キーワード辞書
#			kw = {}
#			kw['to'] = UcfUtil.getHashStr(vo, to_field).encode('utf-8')
#			kw['sender'] = sender.encode('utf-8')
#			kw['subject'] = subject.encode('utf-8')
#			kw['body'] = body.encode('utf-8')
#			#オプションキーワード辞書
#			if reply_to and reply_to != '':
#				kw['reply_to'] = reply_to.encode('utf-8')
#			if cc and cc != '':
#				kw['cc'] = cc.encode('utf-8')
#			if bcc and bcc != '':
#				kw['bcc'] = bcc.encode('utf-8')
#			if body_html and body_html != '':
#				kw['html'] = body_html.encode('utf-8')
#
#			#メール送信
#			try:
#					message = mail.EmailMessage(**kw)
#					message.send()
#			#ログだけ、エラーにしない
#			except Exception,e:
#				self.outputErrorLog(e)

			# to_field 優先として、あれば上書き
			if to_field and to_field!='':
				# ','区切りで分割する。
				to_fields = to_field.split(',')
				to = ''
				# 複数存在する場合、','区切りで格納
				for field in to_fields:
					if to == '':
						to += UcfUtil.getHashStr(vo, field.strip()).encode('utf-8')
					else:
						to += ',' + UcfUtil.getHashStr(vo, field.strip()).encode('utf-8')

			# cc_field 優先として、あれば上書き
			if cc_field and cc_field!='':
				# ','区切りで分割する。
				cc_fields = cc_field.split(',')
				cc = ''
				# 複数存在する場合、','区切りで格納
				for field in cc_fields:
					if cc == '':
						cc += UcfUtil.getHashStr(vo, field.strip()).encode('utf-8')
					else:
						cc += ', ' + UcfUtil.getHashStr(vo, field.strip()).encode('utf-8')

			# bcc_field 優先として、あれば上書き
			if bcc_field and bcc_field!='':
				# ','区切りで分割する。
				bcc_fields = bcc_field.split(',')
				bcc = ''
				# 複数存在する場合、','区切りで格納
				for field in bcc_fields:
					if bcc == '':
						bcc += UcfUtil.getHashStr(vo, field.strip()).encode('utf-8')
					else:
						bcc += ',' + UcfUtil.getHashStr(vo, field.strip()).encode('utf-8')
			#メール送信（TODO 差込データとしてはとりあえずVOをそのまま渡す）
			try:
				UcfMailUtil.sendOneMail(to=to, cc=cc, bcc=bcc, reply_to=reply_to, sender=sender, subject=subject, body=body, body_html=body_html, data=vo)
			#ログだけ、エラーにしない
			except Exception as e:
				logging.info('sendThankyouMail ' + str(e))
				self.outputErrorLog(e)

	def getConfigXml(self, dept_id, master_id):
		gql = ""
		wheres = []
		wheres.append("enq_id='" + master_id + "'")
		wheres.append("del_flag=''")
		wheres.append("dept_id='" + dept_id + "'")
		gql += UcfUtil.getToGqlWhereQuery(wheres)
		models = UCFMDLExtFormMaster.gql(gql)

		for model in models:
			xmldata = model.enq_config
			try:
				xmldata = str(xmldata.encode('cp932'), 'cp932')
			except BaseException as e:
				logging.info('getConfigXml ' + str(e))
			active_flag = True
			# 年月日以外0に
			date = datetime.datetime.now()
			now_date = datetime.datetime(date.year, date.month, date.day)
			if model.active_flag != 'ACTIVE':
				active_flag = False
			if model.active_term_from > now_date or now_date > model.active_term_to:
				active_flag = False
			return xmldata, active_flag
			break
		return '', False

	def getQuestionnaireMasterInfo(self, xml_text, master_id):
		'''  アンケート設定情報の取得 '''
		info = {}
		xmlDoc = UcfXml.loadXml(xml_text)
		if xmlDoc:
			# ハッシュにして返す
			info = xmlDoc.exchangeToHash(isAttr=True, isChild=True)
			return info
		else:
			#self.redirectError(UcfMessage.getMessage(UcfMessage.MSG_NOT_EXIST_DATA, (master_id)))
			return

	def getQuestionnaireTargetFilter(self, xml_text, master_id):
		''' アンケートフィルタ情報の取得 '''
		xml = ''

		xmlDoc = UcfXml.loadXml(xml_text)
		if xmlDoc:
			# ノードを返す
			xml = xmlDoc.selectNodes(self.QUEST_MASTERINFO_TARGET_FILTER)
			return xml
		else:
			#self.redirectError(UcfMessage.getMessage(UcfMessage.MSG_NOT_EXIST_DATA, (master_id)))
			return None

	def getQuestionnaireFieldInfo(self, xml_text, master_id):
		''' アンケート添付ファイル情報の取得 '''
		xml = ''

		xmlDoc = UcfXml.loadXml(xml_text)
		if xmlDoc:
			# ノードを返す
			xml = xmlDoc.selectNodes(self.QUEST_MASTERINFO_FIELD_INFO)
			return xml
		else:
			return None

	def getQuestionnaireSelectConditionInfo(self, vo, master_info, master_id, master_xml):
		''' アップロード先選択条件から、アップロード先情報を作成 '''
		xml = ''

		sites_info_id = ''
		list_sites_info_id = ''
		spread_sheet_info_id = ''

		xmlDoc = UcfXml.loadXml(master_xml)
		if xmlDoc:
			# ノードを返す
			xml = xmlDoc.selectNodes(self.QUEST_MASTERINFO_SELECT_CONDITION)

#		for k,v in master_info.items():
#			print str(k).encode('shift_jis'),str(v).encode('shift_jis')
		add_flag = False
		for node in xml:
			connection = node.getAttribute(self.QUEST_SELECT_CONDITION_CONNECTION)

			# 比較方法がない場合、ANDを基本とする
			if not connection:
				connection = 'AND'
			expressions = node.selectNodes(self.QUEST_SELECT_CONDITION_EXPRESSION)
			expressions_result = []
			# 条件式の数だけループ
			for expression in expressions:
				expression_value = expression.getAttribute(self.QUEST_SELECT_CONDITION_EXPRESSION_VALUE)
				expression_quo = expression.getAttribute(self.QUEST_SELECT_CONDITION_EXPRESSION_QUO)
				expression_type = expression.getAttribute(self.QUEST_SELECT_CONDITION_EXPRESSION_TYPE)
				expression_equation = expression.getAttribute(self.QUEST_SELECT_CONDITION_EXPRESSION_EQUATION)
				expression_target = expression.getAttribute(self.QUEST_SELECT_CONDITION_EXPRESSION_TARGET)

				# getAttribute で取得した場合、Noneが入る事があるので、空欄で上書く。
				if not expression_value:
					expression_value = ''
				if not expression_quo:
					expression_quo = ''
				if not expression_type:
					expression_type = ''
				if not expression_equation:
					expression_equation = ''
				if not expression_target:
					expression_target = ''

				value = None
				target = vo[expression_target]
				# quo が on の場合、valueは値として扱う
				if expression_quo.upper() == 'ON':
					value = expression_value
				else:
					# value を変数として扱う
					value = vo[expression_value]
				# typeによるチェック
				if expression_type.upper() == 'STRING':
					pass
				# 何も入力がない場合もSTRINGとして扱う。
				else:
					pass
				# expression_equationによる比較
				if expression_equation.upper() == 'E':
					if value == target:
						expressions_result.append(True)
					else:
						expressions_result.append(False)
				elif expression_equation.upper() == 'NE':
					if value != target:
						expressions_result.append(True)
					else:
						expressions_result.append(False)
			# 結果格納用
			result = None
			# or
			if connection.upper() == 'OR':
				for s in expressions_result:
					if s:
						result = True
						break
					else:
						result = False
			# defaultではandとして結果を出す。
			else:
				for s in expressions_result:
					if s:
						result = True
					else:
						result = False
						break
			if result:
				# お知らせ画面
				if node.getAttribute(self.QUEST_SELECT_CONDITION_SITES_INFO):
					sites_info_id = node.getAttribute(self.QUEST_SELECT_CONDITION_SITES_INFO)
				# リスト画面
				if node.getAttribute(self.QUEST_SELECT_CONDITION_SITESLIST_INFO):
					list_sites_info_id = node.getAttribute(self.QUEST_SELECT_CONDITION_SITESLIST_INFO)
				# スプレッドシート
				if node.getAttribute(self.QUEST_SELECT_CONDITION_SPREAD_SHEET):
					spread_sheet_info_id = node.getAttribute(self.QUEST_SELECT_CONDITION_SPREAD_SHEET)
				# 結果を格納できた時点でループ終了
				add_flag = True

				break
		if add_flag == False:
			# ひとつも検索項目に該当しなかった場合、デフォルトの書き込み先へ
			sites_info_id = 'SitesInfo'
			list_sites_info_id = 'SitesListInfo'
			spread_sheet_info_id = 'Spreadsheet'

		sites_info = self.setTargetLocation('SitesInfo', sites_info_id, master_info)
		list_sites_info = self.setTargetLocation('SitesListInfo', list_sites_info_id, master_info)
		spread_sheet_info = self.setTargetLocation('Spreadsheet', spread_sheet_info_id, master_info)

		return sites_info, list_sites_info, spread_sheet_info

	def getEditTargetSpreadsheet(self, master_info, master_xml):
		''' 編集時に、書き込み先のスプレッドシートを判別、取得する '''
		xml = ''
		spread_sheet_info_ids = []
		spread_sheet_infos = []

		xmlDoc = UcfXml.loadXml(master_xml)
		if xmlDoc:
			# ノードを返す
			xml = xmlDoc.selectNodes(self.QUEST_MASTERINFO_SELECT_CONDITION)

		add_flag = False
		for node in xml:
			# スプレッドシート
			if node.getAttribute(self.QUEST_SELECT_CONDITION_SPREAD_SHEET):
				spread_sheet_info_ids.append(node.getAttribute(self.QUEST_SELECT_CONDITION_SPREAD_SHEET))
				spread_sheet_infos.append(self.setTargetLocation('Spreadsheet', str(node.getAttribute(self.QUEST_SELECT_CONDITION_SPREAD_SHEET)), master_info))

		if spread_sheet_info_ids == []:
			# ひとつも検索項目に該当しなかった場合、デフォルトの書き込み先へ
			spread_sheet_info_ids.append('Spreadsheet')
			spread_sheet_infos.append(self.setTargetLocation('Spreadsheet', 'Spreadsheet', master_info))

		return spread_sheet_infos, spread_sheet_info_ids

	def setTargetLocation(self, default_id, id, master_info):
		'''更新先への接続情報を取得する'''

		location_info = {}
		if id:
			location_info[default_id + self.QUEST_SELECT_CONDITION_ACCOUNT] = UcfUtil.getHashStr(master_info, id + self.QUEST_SELECT_CONDITION_ACCOUNT)
			location_info[default_id + self.QUEST_SELECT_CONDITION_PASSWORD] = UcfUtil.getHashStr(master_info, id + self.QUEST_SELECT_CONDITION_PASSWORD)
			location_info[default_id + self.QUEST_SELECT_CONDITION_KEY] = UcfUtil.getHashStr(master_info, id + self.QUEST_SELECT_CONDITION_KEY)
			location_info[default_id + self.QUEST_SELECT_CONDITION_WORKSHEET_NAME] = UcfUtil.getHashStr(master_info, id + self.QUEST_SELECT_CONDITION_WORKSHEET_NAME)
			location_info[default_id + self.QUEST_SELECT_CONDITION_DOMAIN] = UcfUtil.getHashStr(master_info, id + self.QUEST_SELECT_CONDITION_DOMAIN)
			location_info[default_id + self.QUEST_SELECT_CONDITION_SITESID] = UcfUtil.getHashStr(master_info, id + self.QUEST_SELECT_CONDITION_SITESID)
			location_info[default_id + self.QUEST_SELECT_CONDITION_PAGEPATH] = UcfUtil.getHashStr(master_info, id + self.QUEST_SELECT_CONDITION_PAGEPATH)
			location_info[default_id + self.QUEST_SELECT_CONDITION_TITLE] = UcfUtil.getHashStr(master_info, id + self.QUEST_SELECT_CONDITION_TITLE)
			location_info[default_id + self.QUEST_SELECT_CONDITION_ENCRYPT] = UcfUtil.getHashStr(master_info, id + self.QUEST_SELECT_CONDITION_ENCRYPT)
			location_info[default_id + self.QUEST_SELECT_CONDITION_APPEND_LINK] = UcfUtil.getHashStr(master_info, id + self.QUEST_SELECT_CONDITION_APPEND_LINK)

		not_none_flag = False
		# ひとつでも値が見つかればTrueに
		for item in location_info.values():
			if item:
				not_none_flag = True

		# すべての項目がNoneの場合default_idの値を使用(すべて空の場合でもおそらくデフォルトが使用される)
		if not_none_flag:
			pass
		else:
		#	location_info[default_id + self.QUEST_SELECT_CONDITION_ACCOUNT] = UcfUtil.getHashStr(master_info, default_id + self.QUEST_SELECT_CONDITION_ACCOUNT)
		#	location_info[default_id + self.QUEST_SELECT_CONDITION_PASSWORD] = UcfUtil.getHashStr(master_info, default_id + self.QUEST_SELECT_CONDITION_PASSWORD)
		#	location_info[default_id + self.QUEST_SELECT_CONDITION_KEY] = UcfUtil.getHashStr(master_info, default_id + self.QUEST_SELECT_CONDITION_KEY)
		#	location_info[default_id + self.QUEST_SELECT_CONDITION_WORKSHEET_NAME] = UcfUtil.getHashStr(master_info, default_id + self.QUEST_SELECT_CONDITION_WORKSHEET_NAME)
		#	location_info[default_id + self.QUEST_SELECT_CONDITION_DOMAIN] = UcfUtil.getHashStr(master_info, default_id + self.QUEST_SELECT_CONDITION_DOMAIN)
		#	location_info[default_id + self.QUEST_SELECT_CONDITION_SITESID] = UcfUtil.getHashStr(master_info, default_id + self.QUEST_SELECT_CONDITION_SITESID)
		#	location_info[default_id + self.QUEST_SELECT_CONDITION_PAGEPATH] = UcfUtil.getHashStr(master_info, default_id + self.QUEST_SELECT_CONDITION_PAGEPATH)
		#	location_info[default_id + self.QUEST_SELECT_CONDITION_TITLE] = UcfUtil.getHashStr(master_info, default_id + self.QUEST_SELECT_CONDITION_TITLE)
		#	location_info[default_id + self.QUEST_SELECT_CONDITION_ENCRYPT] = UcfUtil.getHashStr(master_info, default_id + self.QUEST_SELECT_CONDITION_ENCRYPT)
		#	location_info[default_id + self.QUEST_SELECT_CONDITION_APPEND_LINK] = UcfUtil.getHashStr(master_info, default_id + self.QUEST_SELECT_CONDITION_APPEND_LINK)

			# 見つからない場合、書き込みを行わないように変更
			location_info[default_id + self.QUEST_SELECT_CONDITION_ACCOUNT] = ''
			location_info[default_id + self.QUEST_SELECT_CONDITION_PASSWORD] = ''
			location_info[default_id + self.QUEST_SELECT_CONDITION_KEY] = ''
			location_info[default_id + self.QUEST_SELECT_CONDITION_WORKSHEET_NAME] = ''
			location_info[default_id + self.QUEST_SELECT_CONDITION_DOMAIN] = ''
			location_info[default_id + self.QUEST_SELECT_CONDITION_SITESID] = ''
			location_info[default_id + self.QUEST_SELECT_CONDITION_PAGEPATH] = ''
			location_info[default_id + self.QUEST_SELECT_CONDITION_TITLE] = ''
			location_info[default_id + self.QUEST_SELECT_CONDITION_ENCRYPT] = ''
			location_info[default_id + self.QUEST_SELECT_CONDITION_APPEND_LINK] = ''


		#sitesのアドレス取得用に用意しておく
		location_info[self.QUEST_MASTERINFO_SITES_TEMPLATE_FILENAME] = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SITES_TEMPLATE_FILENAME)
		return location_info

	def isConfirmQuestionnaire(self, master_info):
		'''確認画面ありかどうか'''
		#確認画面テンプレートHTML設定があれば、確認画面あり
		confirm_template_name = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_CONFIRM_TEMPLATE_FILENAME)
		return (confirm_template_name != '')

	def getDefaultAnswerValues(self, master_info, mail_address, domain, operator):
		'''回答デフォルト値を取得'''
		default_values = {}

		for k,v in master_info.iteritems():
			# デフォルト値情報のみを抜き出す
			prefix = self.QUEST_MASTERINFO_DEFAULT_VALUES_PREFIX
			prefix_length = len(self.QUEST_MASTERINFO_DEFAULT_VALUES_PREFIX)
			if k.startswith(prefix) and len(k) > prefix_length and not k.endswith('_type'):
				field_key = UcfUtil.subString(k, prefix_length)
				if not field_key in default_values:
					default_values[field_key] = v
				if k + '_type' in master_info:
					if master_info[k + '_type'] == 'MY_MAIL':
						default_values[field_key] = mail_address
					elif master_info[k + '_type'] == 'DOMAIN':
						default_values[field_key] = domain
					elif master_info[k + '_type'] == 'NOW_DATE':
						time = UcfUtil.getNowLocalTime()
						default_values[field_key] = time.strftime('%Y/%m/%d')
					elif UcfUtil.nvl(master_info[k + '_type']) in operator:
						default_values[field_key] = operator[master_info[k + '_type']]

		return default_values

	def getOldAnswerValues(self, master_info, fid, field_info):
		'''編集用に旧値を取得'''
		account  = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SPREADSHEET_ACCOUNT)
		password = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SPREADSHEET_PASSWORD)
		if UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_ENCRYPT).upper() == 'TRUE':
			logging.info('account:'+str(account))
			logging.info('pass:'+str(password))
			password = UcfUtil.deCrypto(password,UcfConfig.CRYPTO_KEY)
		spreadsheet_key = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SPREADSHEET_KEY)
		worksheet_name  = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_WORKSHEET_NAME)
		logging.info('spreadsheet_key:'+str(spreadsheet_key))
		logging.info('worksheet_name:'+str(worksheet_name))
		worksheet_id = None
		append_url = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_APPEND_LINK)
		# spreadsheet_keyが存在しないとき、処理を終了
		if spreadsheet_key == '':
			# 正常に登録されて終了したと判断する
			return {}, ''
		service = ucf.gdata.spreadsheet.util.getSpreadsheetsService(account, password, self.getRootPath())
		worksheet_id = ucf.gdata.spreadsheet.util.getWorksheetIdByName(service, spreadsheet_key, worksheet_name)
		logging.info('worksheet_id:'+str(worksheet_id))
		#ワークシートが存在していればデータ登録
		if not worksheet_id:
			raise Exception([u'failed get worksheet by name, not exist worksheet', spreadsheet_key, worksheet_name])
			return {}, ''
		else:
			#データ生成
			enq_date = str(UcfUtil.getNowLocalTime())

			vo = {}
			vo_count = 1
			# WHERE句
			wheres = []
			wheres.append(u'no' + '=' + fid)
			query = createListQuery(wheres)
			logging.info('query:'+str(query))
			feed = getListFeedByCond(service, spreadsheet_key, worksheet_id, query.encode('utf-8'))
			create_user = ''
			logging.info('entry:'+str(feed.entry))
			if len(feed.entry) == 1:
				entry = feed.entry[0]
				sheet_title = ucf.gdata.spreadsheet.util.getWorksheetTitleList(service, spreadsheet_key, worksheet_id)
				logging.info('sheet_title:'+str(sheet_title))
				# 正しい順番のタイトル列を取得
				for title in sheet_title:
					logging.info('title:'+str(title))
					if title != 'no' and title != u'投稿日' and title != u'投稿者':
						for key in entry.custom:
							if key == title:
								if entry.custom[key].text:
									vo[_field_prefix + str(vo_count).rjust(2,'0')] = entry.custom[key].text
									# 添付ファイルの場合、nm_に名前を表示
									for node in field_info:
										field_name = node.getAttribute('id')
										if field_name == _field_prefix + str(vo_count).rjust(2,'0'):
											custom_split = str(entry.custom[key].text).split('|')
											if len(custom_split) > 1:
												vo[_name_prefix + _field_prefix + str(vo_count).rjust(2,'0')] = custom_split[0]
												vo['url_' + _field_prefix + str(vo_count).rjust(2,'0')] = custom_split[1]
											else:
												vo[_name_prefix + _field_prefix + str(vo_count).rjust(2,'0')] = entry.custom[key].text
												vo['url_' + _field_prefix + str(vo_count).rjust(2,'0')] = entry.custom[key].text
											break
								break
						vo_count += 1
					elif title == u'投稿者':
						create_user = entry.custom[title].text
			return vo, create_user

			#	ucf.gdata.spreadsheet.util.updateWorksheetRecord(service, entry, data)

#	def registSites(self, title, html, master_info):
#		u''' 生成ページをサイツに登録 '''
#
#		account  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_ACCOUNT)
#		password = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_PASSWORD)
#		domain = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_DOMAIN)
#		sites_id  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_SITESID)
#		page_path  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_PAGEPATH)
#
#		target_entry = None
#		client = SitesUtil.getSitesClient('Sateraito Office Application', domain, account, password, site=sites_id)
#		# 既存ページの存在確認
#		feed = SitesUtil.getContentFeedByPath(client, page_path)
#		for entry in feed.entry:
#			target_entry = entry
#			break
#
#
#		#サイツページが存在していれば更新
#		if target_entry:
#			target_entry.title = title
#			target_entry.html = html
##			pagename = None
#			client.updateContentEntry(target_entry)
#
#		#存在してなければ新規
#		else:
#			# TODO とりあえず既存ページがある前提
#			pass
#
#	def getTemplateResultHtml(self, template_name, vals):
#		u''' テンプレートに情報を埋め込んだHTMLを返す '''
#
#		str_html = ''
#
#		template_path = template_name
#
#		isLocal = True
#		if isLocal:
#			str_html = template.render(self.getLocalTemplateFilePath(template_path), vals)
#		else:
#			template_path = os.path.join(UcfConfig.TEMPLATES_FOLDER_PATH, template_path)
#			str_html = template.render(self.render(template_path), vals)
#
#		return str_html

	def setAttachmentFilesParam(self, vo, field_info):
		u''' 添付ファイル用に値を変更する '''
		is_sucess_edit_attachfiles = False
		try:
			if field_info != None and field_info != []:
				for node in field_info:
					# 対応した値を取得し、格納する。
					key = node.getAttribute('id')
					type = node.getAttribute('type')
					original_file_name = ''
					content_type = ''
					blob_key = ''
					file_size = 0

					# 見つからない場合にNoneが入る為、空欄で上書き
					if not type:
						type = ''
					# typeが'FILE'の場合のみ実装
					if type.upper() == _FIELD_TYPE['FILE']:
						file_bytes_data = self.request.get(key)
						binary = self.request.body_file.vars[key]
						# バイナリが文字列型だった場合はスルー
						if binary != None and not isinstance(binary, str):
							original_file_name = str(binary.filename, UcfConfig.ENCODING, 'ignore')
							file_size = len(file_bytes_data)
							content_type = str(binary.headers['content-type'])
							# vo['len_' + key] = file_size
							logging.info('file_size=' + str(file_size))
							# 1MB判定
							if file_size <= 1024000:
								blob_key, original_file_name = self.setAttachmentFiles(file_bytes_data, binary)
								is_sucess_edit_attachfiles = True
							else:
								is_sucess_edit_attachfiles = False
								break
						else:
							original_file_name = vo[_name_prefix + key]
							blob_key, original_file_name = self.setAttachmentFiles(file_bytes_data, None)
							is_sucess_edit_attachfiles = True
						# 文字列に\を含む場合、最後の\以降をoriginal_file_nameに
						if original_file_name.rfind('\\') != -1:
							original_file_name = original_file_name[original_file_name.rfind('\\') + 1:]
					# ファイル名の表示に使用
					# データが空の場合の動作として、処理を追加 2013/02/19
					if original_file_name != '':
						vo[_name_prefix + key] = original_file_name
					else:
						vo[_name_prefix + key] = vo['o' + _name_prefix + key]
					
					# ファイルのタイプを保持（アップロード時にバイナリが解析できれば不要になる）
					vo[_type_prefix + key] = content_type
					# Base64で変換したファイルをセット 2011/04/11 アップロード用対策版
					# vo[key] = base64.b64encode(file_bytes_data)
					vo[key] = blob_key
					# vo[key] = UcfUtil.enCrypto(file_bytes_data, UcfConfig.CRYPTO_KEY)
			else:
				is_sucess_edit_attachfiles = True
		except Exception as e:
			is_sucess_edit_attachfiles = False
			# エラーにはせず、ログを出力
			logging.info(e)
			self.outputErrorLog(e)

		return is_sucess_edit_attachfiles

	def setAttachmentFiles(self, file_bytes_data, binary):
		key = ''
		# 取得に使用するkey,ファイル名を返却
		# binaryが無ければ終了
		if binary is None:
			return key, file_bytes_data
		# ファイル名、ファイルタイプを取得
		original_file_name = str(binary.filename, UcfConfig.ENCODING, 'ignore')
		content_type = str(binary.headers['content-type'])
		# IE設定対策(ローカルパス表示回避)
		if original_file_name.rfind('\\') != -1:
			original_file_name = original_file_name[original_file_name.rfind('\\') + 1:]
		unique_id = UcfUtil.guid()
		key = UcfUtil.guid()
		model = UCFMDLFile(unique_id=unique_id)
		model.data_key = key
		model.data_type = 'BINARY'
		model.content_type = content_type
		model.data_name = original_file_name
		# db.Blobを使用して変換を行わないと格納できない(?)
		model.blob_data = file_bytes_data
		now_date = UcfUtil.getNow()
		# アクセス期限を設定
		expire_date = now_date + datetime.timedelta(days=1)
		# 削除日付を設定
		# この削除日付を使用して一日一回削除処理を実行する
		model.expire_date = expire_date
		model.date_created = now_date
		model.date_changed = now_date
		model.creator_name = 'SYSTEM'
		model.updater_name = 'SYSTEM'
		model.put()
		return key, original_file_name

	def getAttachmentFiles(self, key):
		binary = ''
		# 受け取ったバイナリデータと同様のものを作成する。(出来る？)
		# 無理な場合、必要なデータをばらばらで渡す。
		# 戻るボタン使用時のファイル情報保持については、後回しでもOK？
		gql = ""
		wheres = []
		wheres.append("data_key='" + UcfUtil.escapeGql(key) + "'")
		gql += UcfUtil.getToGqlWhereQuery(wheres)
		models = UCFMDLFile.gql(gql)
		if not models:
			return None
		blob_data = None
		for model in models:
			blob_data = model.blob_data
			break
		return blob_data


	def setAttachmentFilesParamForRetrn(self, vo, field_info):
		u''' 戻るボタンによる遷移用に値を変更する '''
		try:
			if field_info != None and field_info != []:
				for node in field_info:
					# 対応した値を取得し、格納する。
					key = node.getAttribute('id')
					type = node.getAttribute('type')
					original_file_name = ''
					content_type = ''
					# 見つからない場合にNoneが入る為、空欄で上書き
					if not type:
						type = ''
					# typeが'FILE'の場合のみ、旧の値を適用
					if type.upper() == _FIELD_TYPE['FILE']:
						vo[_name_prefix + key] = vo['o' + _name_prefix + key]
			return
		except Exception as e:
			# エラーにはせず、ログを出力
			logging.info('setAttachmentFilesParamForRetrn ' + str(e))
			self.outputErrorLog(e)
			return None

	def escapeJs(self, vo, force=False):
		u''' 添付ファイル用に値を変更する '''
		try:
			for k,v in vo.iteritems():
				# extjsの場合のみ、処理
				if _ext_prefix + k in vo or force:
					value = v
					value = value.replace('\n', '\\n')
					value = value.replace('\r', '\\r')
					value = value.replace('\'', '\\\'')
					vo[k] = value
			return
		except Exception as e:
			# エラーにはせず、ログを出力
			logging.info('escapeJs ' + str(e))
			self.outputErrorLog(e)
			return

	def makeVo(self, vo):
		u''' 何も入っていない項目を、空欄に変更する '''
		try:
			add_vo = {}
			for k,v in vo.iteritems():
				# cmd_もしくはdn_があった場合、空欄を入れる
				if k.startswith(_cmd_prefix):
					field_id = k.replace(_cmd_prefix, '')
					if not field_id in vo:
						# cmd があるが、内容が空の場合、空欄をセット
						add_vo[field_id] = ''
			# 追加項目を連結
			vo.update(add_vo)
			return
		except Exception as e:
			# エラーにはせず、ログを出力
			logging.info('makeVo ' + str(e))
			self.outputErrorLog(e)
			return

	def createAttachmentFilesIntendUrl(self, vo, client, field_info, attachment_file_urls, number, sites_id, target_entry):
		u''' 添付ファイルをアップロードする予定のURLをあらかじめ作成する。(お知らせページ) '''
		# 結果 KEY: _name_prefix + フィールド名（例･･･「FLD001」）VALUE:[title, description]
		hash_result = {}
		operator_id = sites_id

		# FILE数分だけ処理
		int_no = 0	# 連番用
		# 入力無しや、空のときは処理終了
		if field_info is None or field_info == []:
			return
		# ファイル名の末尾に番号をふるために使用
		file_name_count = {}
		file_names = self.getAttachmentFileNames(client, target_entry, sites_id)

		for node in field_info:
			type = node.getAttribute('type')
			# 見つからない場合にNoneが入る為、空欄で上書く
			if not type:
				type = ''
			if type.upper() == _FIELD_TYPE['FILE'] and node.getAttribute('upload_type') == _DETAIL_SITES_PAGE:
				field_name = node.getAttribute('id')
				# 見つからない場合にNoneが入る為、空欄で上書き
				if not field_name:
					field_name = ''
				original_file_name = vo[_name_prefix + field_name]

				del_flag = ''
				if 'del_' + field_name in vo:
					del_flag = vo['del_' + field_name]
				logging.info('del_flag  : ' + str(del_flag))
				# 削除の場合、スルー
				if del_flag == 'del':
					logging.info(str(field_name) + ' : this is del')
					attachment_file_urls[field_name] = ['#', u'ファイル無し']
					continue
				# データがないときはスルー
				elif vo[field_name] is None or vo[field_name] == '':
					# 旧値が存在する場合、それを使用
					if original_file_name and vo['url_' + field_name]:
						attachment_file_urls[field_name] = [vo['url_' + field_name], original_file_name]
					else:
						attachment_file_urls[field_name] = ['#', u'ファイル無し']
					continue
				int_no += 1
				# 拡張子を取得
				original_file_base_name = ''
				original_file_extension = ''
				if original_file_name.rfind('.') != -1:
					original_file_base_name = original_file_name[:original_file_name.rfind('.')]
					original_file_extension = original_file_name[original_file_name.rfind('.'):]
				# url用のファイル名を作成する
				original_file_name_url = str(original_file_name)
				# ファイルタイトルを決定
				# タイトルの命名方法を変更 2011/11/29
				title = original_file_name
				description=''
				datNow = UcfUtil.getLocalTime(UcfUtil.getNow())
				#title += operator_id + '_'
				#title += datNow.strftime('%Y') + datNow.strftime('%m') + datNow.strftime('%d') + datNow.strftime('%H') + datNow.strftime('%M') + datNow.strftime('%S') + '_'
				#title += UcfUtil.nvl(int_no)
				#title += original_file_extension

				# _ 付きnumber追加
				end_flag = True
				for names in file_names:
					# 同名のファイルが見つかった場合、ループへ
					if names[2] == original_file_name or original_file_name in file_name_count:
						end_flag = False
						break
					else:
						# 同名ファイルがなかった場合、カウントを準備
						file_name_count[original_file_name] = 1
				if end_flag:
					pass
				else:
					inc_number = 1
					# 同名のファイルが見つかった場合、カウント数を引き継ぐ
					if  original_file_name in file_name_count:
						inc_number = file_name_count[original_file_name]

					while(1):
						num_end_flag = True
						for names in file_names:
							if names[2][:names[2].rfind('.')] == original_file_base_name + '_' + str(inc_number):
								num_end_flag = False
								break
						# ファイル名が一致しなかった場合無限ループを抜ける
						if num_end_flag:
							title = original_file_base_name + '_' +  str(inc_number) + original_file_extension
							original_file_name_url = title
							# 同名のファイルが合った場合の為にカウント数を渡す
							file_name_count[original_file_name] = inc_number + 1
							break
						else:
							inc_number += 1

				pagename = title
				# ファイル説明（※かわりに説明に名称などをセット）
				description='ID:' + operator_id + '\r\n' + 'DATE:' + UcfUtil.nvl(datNow) + '\r\n' + 'FILE:' + original_file_name + '\r\n'
				attachment_file_urls[_name_prefix + field_name] = title, description
				attachment_file_urls[field_name] = [target_entry.GetAlternateLink().href + '/' + original_file_name_url, title]
		return

	def uploadAttachmentFilesForUpload(self, vo, sites_info, field_info, attachment_file_urls, number, apps_domain=None):
		u''' サイツページを更新 '''
		ucfp = UcfFrontParameter(self)

		account  = UcfUtil.getHashStr(sites_info, self.QUEST_SITESINFO_ACCOUNT)
		password = UcfUtil.getHashStr(sites_info, self.QUEST_SITESINFO_PASSWORD)
		if UcfUtil.getHashStr(sites_info, self.QUEST_SITESINFO_ENCRYPT).upper() == 'TRUE':
			password = UcfUtil.deCrypto(password,UcfConfig.CRYPTO_KEY)
		domain = UcfUtil.getHashStr(sites_info, self.QUEST_SITESINFO_DOMAIN)
		if domain == '':
			domain = 'site'
		sites_id  = UcfUtil.getHashStr(sites_info, self.QUEST_SITESINFO_SITESID)
		page_path  = UcfUtil.getHashStr(sites_info, self.QUEST_SITESINFO_PAGEPATH)

		target_entry = None
		# sites_idが存在しないとき、処理を終了
		if sites_id == '':
			# 正常に登録されて終了したと判断する
			return True, True, '', attachment_file_urls
		try:
			client = SitesUtil.getSitesClient('sateraito-apps-kakuchou-form', domain, account, password, site=sites_id, apps_domain=apps_domain)
			entry = None
			# 既存ページの存在確認
			feed = SitesUtil.getContentFeedByPath(client, page_path)
			for entry_data in feed.entry:
				target_entry = entry_data
				break
			# 更新対象ページの存在確認
			target_feed = SitesUtil.getContentFeedByPath(client, page_path + '/' + number)
			for entry_data in target_feed.entry:
				entry = entry_data
				break
			#サイツページが存在していれば更新
			if target_entry and entry:
				# 添付ファイルを登録する場合、先にアドレスを作成(作成済みなため、削除)
				self.createAttachmentFilesIntendUrl(vo, client, field_info, attachment_file_urls, number, sites_id, entry)
				return attachment_file_urls
		except Exception as e:
			logging.info(str(e))
			# エラーにはせず、ログを出力
			self.outputErrorLog(e)
			return attachment_file_urls

	def uploadAttachmentFilesForDetailPage(self, vo, client, page_entry, field_info, attachment_file_urls, sites_id):
		u''' 添付ファイルの処理(お知らせページへアップロード) '''
		# 別メソッドで、仮に作成したURLの field_name, title を保持しておき、ここに渡す。

		# 結果 KEY:フィールド名（例･･･「FLD001」）VALUE:[アップロード先のＵＲＬ, ファイル名]
		hash_result = {}
		operator_id = sites_id

		# FILE数分だけ処理
		int_no = 0	# 連番用

		# 入力無しや、空のときは処理終了
		if field_info is None or field_info == []:
			return

		# clientが取得できなかった場合、アップロードを行わずに終了
		if client is None:
			return
		for node in field_info:
			type = node.getAttribute('type')
			# 見つからない場合にNoneが入る為、空欄で上書く
			if not type:
				type = ''
			if type.upper() == _FIELD_TYPE['FILE'] and node.getAttribute('upload_type') == _DETAIL_SITES_PAGE:
				field_name = node.getAttribute('id')
				# 見つからない場合にNoneが入る為、空欄で上書く
				if not field_name:
					field_name = ''
				# 添付ファイルのバイナリ取得 2011/04/11 アップロード用対策版
				#file_bytes_data = base64.b64decode(vo[field_name])
				file_bytes_data = self.getAttachmentFiles(vo[field_name])
				#file_bytes_data = UcfUtil.deCrypto(vo[field_name], UcfConfig.CRYPTO_KEY)
				original_file_name = UcfUtil.nvl(vo[_name_prefix + field_name])
				content_type = UcfUtil.nvl(vo[_type_prefix + field_name]).encode('utf-8')
				#binary = UcfUtil.nvl(vo[field_name])
				del_flag = ''
				if 'del_' + field_name in vo:
					del_flag = vo['del_' + field_name]
				if del_flag == 'del':
					# 削除フラグが立っている場合、削除
					content_type = UcfUtil.nvl(vo[_type_prefix + field_name]).encode('utf-8')
					original_file_base_name = ''
					original_file_extension = ''
					if vo['o' + _name_prefix + field_name].rfind('.') != -1:
						# 削除先旧ファイル名を取得
						original_file_base_name = vo['o' + _name_prefix + field_name][:vo['o' + _name_prefix + field_name].rfind('.')]
						original_file_extension = vo['o' + _name_prefix + field_name][vo['o' + _name_prefix + field_name].rfind('.'):]
					# 一致しなかった場合は、何もしない

					match_item = re.match(page_entry.GetAlternateLink().href + '/(' + original_file_base_name + '(_[0-9]+)?' + original_file_extension + ')', vo['url_' + field_name])
					if not match_item is None:
						title = match_item.group(1)
						SitesUtil.deleteAttachmentFile(client, page_entry, content_type=content_type, title=title)
				#elif binary != '' and original_file_name != '' and content_type != '' and attachment_file_urls[field_name]:
				elif file_bytes_data != '' and original_file_name != '' and content_type != '' and attachment_file_urls[field_name]:
					int_no += 1
					# ファイル説明とタイトルをセット
					title, description = attachment_file_urls[_name_prefix + field_name]
					SitesUtil.uploadAttachmentFile(client, file_bytes_data, page_entry, content_type=content_type, title=title, description=description, folder_name=None)
		return

	def uploadAttachmentFilesToGoogleSites(self, vo, master_info, field_info, apps_domain=None):
		u''' 添付ファイルの処理 (ファイルキャビネット等) '''
		domainname = UcfUtil.getHashStr(master_info, self.QUEST_FILE_ATTACHMENT_DOMAIN )
		sitename   = UcfUtil.getHashStr(master_info, self.QUEST_FILE_ATTACHMENT_SITE_NAME )
		path  = UcfUtil.getHashStr(master_info, self.QUEST_FILE_ATTACHMENT_PAGE_PATH )
		folder_name     = UcfUtil.getHashStr(master_info, self.QUEST_FILE_ATTACHMENT_FOLDER_NAME )
		account = UcfUtil.getHashStr(master_info, self.QUEST_FILE_ATTACHMENT_ACCOUNT )
		password = UcfUtil.getHashStr(master_info, self.QUEST_FILE_ATTACHMENT_PASSWORD )
		password = UcfUtil.deCrypto(password, UcfConfig.CRYPTO_KEY)

		# 結果 KEY:フィールド名（例･･･「FLD001」）VALUE:[アップロード先のＵＲＬ, ファイル名]
		hash_result = {}
		operator_id = sitename
		# FILE数分だけ処理
		pagepath = None
		client = None
		page_entry = None
		int_no = 0	# 連番用

		# 入力無しや、空のときは処理終了
		if field_info is None or field_info == []:
			return
		# ファイル名の末尾に番号をふるために使用
		file_name_count = {}
		for node in field_info:
			type = node.getAttribute('type')
			if not type:
				type = ''
			# タイプチェック
			if type.upper() == _FIELD_TYPE['FILE'] and node.getAttribute('upload_type') != _DETAIL_SITES_PAGE:
				# タイプ指定が正常な場合、何も行わない
				pass
			else:
				# 添付ファイルの書き込み先がデフォルトではない場合、次のループへ
				continue

			# client、pagepath、page_entryは、一度作成したら以降保持する。
			if client is None:
				client = SitesUtil.getSitesClient('announcement', domainname, account, password, sitename, apps_domain=apps_domain)
				feed = SitesUtil.getContentFeedByPath(client, path=path)
				for entry in feed.entry:
					page_entry = entry
					pagepath = path
					break
				if page_entry == None:
					# raise Exception, ['failed get file upload sites page entry.', str(sitename), str(path)]
					raise Exception("failed get file upload sites page entry. sitename=" + str(sitename) + " path=" + str(path))

				file_names = self.getAttachmentFileNames(client, page_entry, None)

			field_name = node.getAttribute('id')
			# 見つからない場合、Noneが入る為、空欄で上書き
			if not field_name:
				field_name = ''
			del_flag = ''
			if 'del_' + field_name in vo:
				del_flag = vo['del_' + field_name]
			
			# delフラグが存在している場合、削除処理
			if del_flag == 'del':
				content_type = UcfUtil.nvl(vo[_type_prefix + field_name]).encode('utf-8')
				original_file_base_name = ''
				original_file_extension = ''
				if vo[_name_prefix + field_name].rfind('.') != -1:
					original_file_base_name = vo[_name_prefix + field_name][:vo[_name_prefix + field_name].rfind('.')]
					original_file_extension = vo[_name_prefix + field_name][vo[_name_prefix + field_name].rfind('.'):]
				# 一致しなかった場合は、何もしない
				match_item = re.match(page_entry.GetAlternateLink().href + '/(' + original_file_base_name + '(_[0-9]+)?' + original_file_extension + ')', vo['url_' + field_name])
				if match_item:
					title = match_item.group(1)
					logging.info('uploadAttachmentFilesToGoogleSites ' + str(content_type))
					SitesUtil.deleteAttachmentFile(client, page_entry, content_type=content_type, title=title)
				hash_result[field_name] = ['#', u'ファイル無し']

			else:
				# 添付ファイルのバイナリ取得 2011/04/11 アップロード用対策版
				#file_bytes_data = base64.b64decode(vo[field_name])
				file_bytes_data = self.getAttachmentFiles(vo[field_name])
				# file_bytes_data = UcfUtil.deCrypto(vo[field_name], UcfConfig.CRYPTO_KEY)

				original_file_name = UcfUtil.nvl(vo[_name_prefix + field_name])
				content_type = UcfUtil.nvl(vo[_type_prefix + field_name]).encode('utf-8')
				#binary = UcfUtil.nvl(vo[field_name])

				int_no += 1
				#if binary != '' and original_file_name != '' and content_type != '':
				if file_bytes_data != '' and original_file_name != '' and content_type != '':
					# 拡張子と拡張子抜きのファイル名を取得
					original_file_base_name = ''
					original_file_extension = ''
					if original_file_name.rfind('.') != -1:
						original_file_base_name = original_file_name[:original_file_name.rfind('.')]
						original_file_extension = original_file_name[original_file_name.rfind('.'):]
					# ファイルタイトルを決定
					# ファイルアップロード後の変換に合わせて文字を削除
					original_file_name_url = str(original_file_name)

					# タイトルの命名方法を変更 2011/11/29
					title = ''
					description=''
					datNow = UcfUtil.getLocalTime(UcfUtil.getNow())
					#title += operator_id + '_'
					#title += datNow.strftime('%Y') + datNow.strftime('%m') + datNow.strftime('%d') + datNow.strftime('%H') + datNow.strftime('%M') + datNow.strftime('%S') + '_'
					#title += UcfUtil.nvl(int_no)
					#title += original_file_extension
					title += original_file_base_name

					# 2つめ以降の同名ファイルは、番号を振る。

					# _ 付きnumber追加
					end_flag = True
					for names in file_names:
						# 同名のファイルが見つかった場合、ループ
						if names[2] == original_file_name or original_file_name in file_name_count:
							end_flag = False
							break
						else:
							# 同名ファイルがなかった場合、カウントを準備
							file_name_count[original_file_name] = 1
					if end_flag:
						pass
					else:
						inc_number = 1
						# 同名のファイルが見つかった場合、カウント数を引き継ぐ
						if  original_file_name in file_name_count:
							inc_number = file_name_count[original_file_name]

						while(1):
							num_end_flag = True
							for names in file_names:
								if names[2][:names[2].rfind('.')] == original_file_base_name + '_' + str(inc_number):
									num_end_flag = False
									break
							# ファイル名が一致しなかった場合無限ループを抜ける
							if num_end_flag:
								title = original_file_base_name + '_' +  str(inc_number) + original_file_extension
								original_file_name_url = title
								# 同名のファイルが合った場合の為にカウント数を渡す
								file_name_count[original_file_name] = inc_number + 1
								break
							else:
								inc_number += 1

					# ファイル説明（※かわりに説明に名称などをセット）
					description='ID:' + operator_id + '\r\n' + 'DATE:' + UcfUtil.nvl(datNow) + '\r\n' + 'FILE:' + original_file_name + '\r\n'
					# ファイルアップロード
					pagename = title
					SitesUtil.uploadAttachmentFile(client, file_bytes_data, page_entry, content_type=content_type, title=title, description=description, folder_name=folder_name)
					# client.getContentAccessURL の生成URLは、誤っている可能性があるため、変更
					# hash_result[field_name] = [client.getContentAccessURL(pagepath, pagename), original_file_name]
					hash_result[field_name] = [page_entry.GetAlternateLink().href + '/' + original_file_name_url, original_file_name]
				# ファイルがアップロードされていない場合、以前の値を使用
				elif vo[_name_prefix + field_name] != '' and vo['url_' + field_name]:
					hash_result[field_name] = [vo['url_' + field_name], vo[_name_prefix + field_name]]
				else:
					hash_result[field_name] = ['#', u'ファイル無し']
		return hash_result

	def createAttachmentFilesEntryData(self, master_info, sites_id, page_path, apps_domain=None):
		u''' ファイルアップロード先の情報を取得 '''
		account  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_ACCOUNT)
		password = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_PASSWORD)
		if UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_ENCRYPT).upper() == 'TRUE':
			password = UcfUtil.deCrypto(password,UcfConfig.CRYPTO_KEY)
		domain = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_DOMAIN)
		if domain == '':
			domain = 'site'
		# sites_id  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_SITESID)
		# page_path  = UcfUtil.getHashStr(master_info, self.QUEST_SITESINFO_PAGEPATH)

		# field等の設定に使用するindexの内容をここで作成
		target_entry = None
		content = None
		field_name = {}
		field_value = {}
		if sites_id == '':
			return None, None
		try:
			# Client取得
			client = SitesUtil.getSitesClient('sateraito-apps-kakuchou-form', domain, account, password, site=sites_id, apps_domain=apps_domain)
			# 既存ページの存在確認
			feed = SitesUtil.getContentFeedByPath(client, page_path)
			for entry in feed.entry:
				target_entry = entry
				break
			return client, target_entry
		except Exception as e:
			logging.info('createAttachmentFilesEntryData ' + str(e))
			# エラーにはせず、ログを出力
			self.outputErrorLog(e)
			return None, None

	def getAttachmentFileNames(self, client, entry, enq_id):
		u''' 添付ファイルのみのFeedを取得 2011/11/30 '''
		kind = 'attachment'
		# uri = '%s?kind=%s' % (client.MakeContentFeedUri(), kind)
		# 親の指定を追加し、検索範囲を削減 2012/03/22
		uri = '%s?parent=%s&kind=%s' % (client.MakeContentFeedUri(), entry.GetNodeId(), kind)
		# uri = '%s?kind=%s' % (entry.GetAlternateLink().href, kind)
		try:
			feed = client.GetContentFeed(uri=uri)
			files = []
			count = 0
			# 添付ファイルのアドレスと、これから更新を行うアドレスが等しい場合、entryを取得 2011/11/30
			for attachment_entry in feed.entry:
				if str(attachment_entry.GetAlternateLink().href)[:str(attachment_entry.GetAlternateLink().href).rfind('/')] == (entry.GetAlternateLink().href):
					files.append([attachment_entry.GetAlternateLink().href, attachment_entry, attachment_entry.title.text, str(count)])
					count += 1
			return files
		except Exception as e:
			logging.info('getAttachmentFileNames None or Error = ' + str(e))
			# エラーにはせず、ログを出力
			return None

	def uploadAttachmentFilesEntryDataSingle(self, file_bytes_data, bynary, client, sites_id, target_entry, file_name):
		u''' 添付ファイルのアップロード '''
		original_file_name = ''
		original_file_name_url = ''
		# バイナリが文字列型だった場合はスルー
		if bynary != None and not isinstance(bynary, str):
			original_file_name = str(bynary.filename, UcfConfig.ENCODING, 'ignore')
			content_type = str(bynary.headers['content-type'])
		else:
			original_file_name = ''
		# 文字列に\を含む場合、最後の\以降をoriginal_file_nameとして取得
		if original_file_name.rfind('\\') != -1:
			original_file_name = original_file_name[original_file_name.rfind('\\') + 1:]
		## スペースをアンダーバーに置き換え 2012/05/14 削除
		original_file_name = original_file_name
		original_file_base_name = ''
		original_file_extension = ''
		# 一度拡張子とファイル名に分ける
		if original_file_name.rfind('.') != -1:
			original_file_base_name = original_file_name[:original_file_name.rfind('.')]
			original_file_extension = original_file_name[original_file_name.rfind('.'):]
		original_file_name_url = str(original_file_name)

		end_flag = True
		for names in file_name:
			if names[2] == original_file_name:
				end_flag = False
				break
		if end_flag:
			pass
		else:
			number = 1
			while(1):
				num_end_flag = True
				for names in file_name:
					if names[2][:names[2].rfind('.')] == original_file_base_name + '_' + str(number):
						num_end_flag = False
						break
				# ファイル名が一致しなかった場合無限ループを抜ける
				if num_end_flag:
					original_file_name = original_file_base_name + '_' +  str(number) + original_file_extension
					break
				else:
					number += 1
		datNow = UcfUtil.getLocalTime(UcfUtil.getNow())
		description='ID:' + sites_id + '\r\n' + 'DATE:' + UcfUtil.nvl(datNow) + '\r\n' + 'FILE:' + original_file_name + '\r\n'
		# アップロード処理
		SitesUtil.uploadAttachmentFileOtherUrl(client, file_bytes_data, target_entry, content_type=content_type, title=original_file_name, url_title=original_file_name_url, description=description, folder_name=None)
		return

	def deleteAttachmentFileEntryData(self, client, item_names, file_path):
		u''' 添付ファイルの削除処理 '''
		try:
			entry = None
			# 既存ページの存在確認
			logging.info(file_path)
			for item in item_names:
				logging.info(item[0])
				if item[0] == file_path:
					entry = item[1]
					break
			if entry:
				client.deleteEntry(entry)
				logging.info('OK')
				return True
			else:
				logging.info('file not found.' + file_path)
				return False
		except Exception as e:
			# エラーにはせず、ログを出力
			logging.info(str(e))
			logging.info('NG')
			return False

	def enq_dispatch(self, template_name, vals, dept_id):

		# 文字コード指定：これをやらないとmetaタグだけでは文字コードをブラウザが認識してくれないため。
		#self.response.headers['Content-Type'] = 'text/html; charset=' + UcfConfig.ENCODING + ';'
		#encodeとcharsetのマッピング対応 2009.5.20 Osamu Kurihara
		if UcfConfig.ENCODING=='cp932':
			# charset_string='Shift_JIS'
			charset_string = UcfConfig.FILE_CHARSET
		#マッピング定義がないものはUcfConfig.ENCODING
		else:
			charset_string=UcfConfig.ENCODING
		self.setResponseHeader('Content-Type', 'text/html; charset=' + charset_string + ';')
		html_text = ''
		gql = ""
		wheres = []
		wheres.append("template_id='" + template_name + "'")
		wheres.append("del_flag=''")
		wheres.append("dept_id='" + dept_id + "'")

		gql += UcfUtil.getToGqlWhereQuery(wheres)
		models = UCFMDLExtFormTemplate.gql(gql)
		# BigtableからテンプレートHTMLを取得

		for model in models:
			#html_text = str(model.template_html)
			# HTMLエディタを使用した場合に対応する為、取得方法を一部変更 2012/03/27
			template_params = model.template_params
			json_data = {}
			# template_paramsが存在しない場合は空の辞書を使用
			if template_params is None or template_params == 'None':
				pass
			else:
				json_data = simplejson.loads(template_params)
			script_param, html_param = ConvertHtmlWithJson.getUserEntry(json_data)
			html_text = ConvertHtmlWithJson.createHtmlTemplate(str(model.template_html), script_param, html_param, vals)
			logging.info('script_param:'+str(script_param))
			logging.info('html_param:'+str(html_param))
			logging.info('html_text:'+str(html_text))
			break

		html_text = Template(html_text)
		context_html = Context(vals)
		# html_show = template.render(html_text, vals).encode(UcfConfig.FILE_CHARSET)

		# self.response.out.write(html_text.render(context_html).encode(UcfConfig.FILE_CHARSET))
		return html_text.render(context_html).encode(UcfConfig.FILE_CHARSET)

############################################################
## バリデーションチェッククラス （アンケートエントリー用）
############################################################
class QuestionnaireEntryValidator(BaseValidator):
	u'''入力チェッククラス'''
		
	def validate(self, helper, vo):
		
		# 初期化
		self.init()

		check_name = ''
		check_key = ''
		check_value = ''

		cmd_prefix_length = len(_cmd_prefix)

		for k,v in vo.iteritems():
			# AutoCmdを処理
			if k.startswith(_cmd_prefix) and len(k) > cmd_prefix_length:
				cmd = v
				check_key = UcfUtil.subString(k, cmd_prefix_length)
				check_name = UcfUtil.getHashStr(vo, _dispname_prefix + check_key)
				check_value = UcfUtil.getHashStr(vo, check_key)
				self.applicateAutoCmd(check_value, check_key, check_name, cmd)
		# 重複チェック
		if self.total_count == 0:
			pass
	def validate_in_file(self, helper, vo, field_info):
		# 初期化
		self.init()
		check_name = ''
		check_key = ''
		check_value = ''
		cmd_prefix_length = len(_cmd_prefix)
		mega_byte_size = 1048576
		field_names = []
		if field_info is None or field_info == []:
			pass
		else:
			for node in field_info:
				type = node.getAttribute('type')
				if not type:
					type = ''
				if type.upper() == _FIELD_TYPE['FILE']:
					field_names.append(node.getAttribute('id'))
		for k,v in vo.iteritems():
			# AutoCmdを処理
			if k.startswith(_cmd_prefix) and len(k) > cmd_prefix_length:
				cmd = v
				if UcfUtil.subString(k, cmd_prefix_length) in field_names:
					check_key = UcfUtil.subString(k, cmd_prefix_length)
					check_name = UcfUtil.getHashStr(vo, _dispname_prefix + check_key)
					check_value = UcfUtil.getHashStr(vo, 'nm_' + check_key)
				else:
					check_key = UcfUtil.subString(k, cmd_prefix_length)
					check_name = UcfUtil.getHashStr(vo, _dispname_prefix + check_key)
					check_value = UcfUtil.getHashStr(vo, check_key)
				self.applicateAutoCmd(check_value, check_key, check_name, cmd)
			if k.startswith('len_'):
				if int(v) >= mega_byte_size:
					check_key = UcfUtil.subString(k, len('len_'))
					self.appendValidate(check_key , u'%sはサイズが1MB以下のファイルを指定して下さい。' % UcfUtil.getHashStr(vo, _dispname_prefix + check_key))

		# 重複チェック
		if self.total_count == 0:
			pass

############################################################
## ビューヘルパー（ワークフロー申請管理用）
############################################################
class QuestionnaireViewHelper(ViewHelper):

	def applicate(self, vo, helper):
		voVH = {}

		# ここで表示用変換を必要に応じて行うが、原則Djangoテンプレートのフィルタ機能を使う
		for k,v in vo.iteritems():
			voVH[k] = v	
		
		return voVH

