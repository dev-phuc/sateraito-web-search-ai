# coding: utf-8

# XML関連
#import xml.dom.minidom as dom
#import xml.xpath as xpath
from xml.etree import ElementTree

# import os,sys,math,string
# import logging,traceback
# from google.appengine.api import users
# from google.appengine.ext import webapp
# from google.appengine.ext.webapp import template
# from google.appengine.api import mail

from ucf.utils.helpers import *
from ucf.utils.validates import BaseValidator
from ucf.config.ucfconfig import *
from ucf.config.ucfmessage import *
from ucf.utils.ucfutil import *
from ucf.utils.mailutil  import *
from ucf.utils.models  import *
from ucf.utils.ucfxml import *

from ucf.tablehelper.timecard import *
#import ucf.gdata.spreadsheet.util
from ucf.gdata.spreadsheet.util import *

############################################################
## ちょっとした定数（このpy内でのみ使用可能）
############################################################
_field_prefix = "FLD"
_cmd_prefix = "cmd_"
_field_type_prefix = "ftp_"
_seq_prefix = "SEQ"
_dispname_prefix = "dn_"

############################################################
## ローカルFUNC
############################################################
class TimecardPageHelper(ManageHelper):

#	QUEST_MASTERINFO_MAIL_FROM = 'ThankYouMail/From'
#	QUEST_MASTERINFO_MAIL_CC = 'ThankYouMail/Cc'
#	QUEST_MASTERINFO_MAIL_BCC = 'ThankYouMail/Bcc'
#	QUEST_MASTERINFO_MAIL_REPLY_TO = 'ThankYouMail/ReplyTo'
#	QUEST_MASTERINFO_MAIL_TO_FIELD = 'ThankYouMail/To/@field'
#	QUEST_MASTERINFO_MAIL_SUBJECT = 'ThankYouMail/Subject'
#	QUEST_MASTERINFO_MAIL_BODY = 'ThankYouMail/Body'
#	QUEST_MASTERINFO_MAIL_BODYHTML = 'ThankYouMail/BodyHtml'
#
#	QUEST_MASTERINFO_DEFAULT_VALUES_PREFIX = 'DefaultInfo/@'
	
	def __init__(self):
		ManageHelper.__init__(self)
		pass

	def registEntry(self, pType, polling_date, userdata, config):
		u''' アンケート回答を１つ新規登録 '''

#		account  = UcfUtil.getHashStr(config, self.QUEST_MASTERINFO_SPREADSHEET_ACCOUNT)
#		password = UcfUtil.getHashSftr(config, self.QUEST_MASTERINFO_SPREADSHEET_PASSWORD)
#		spreadsheet_key = UcfUtil.getHashStr(config, self.QUEST_MASTERINFO_SPREADSHEET_KEY)
#		worksheet_name  = UcfUtil.getHashStr(config, self.QUEST_MASTERINFO_WORKSHEET_NAME)
		account = config.getAccount()
		password = config.getPassword()
		spreadsheet_key = UcfUtil.getHashStr(userdata,'spreadsheet_key')
		worksheet_name = UcfUtil.getHashStr(userdata, 'operator_name')
		worksheet_id = None

		service = getSpreadsheetsService(account, password, self.getRootPath())
		#service = getSpreadsheetsService(account, password, UcfUtil.guid())	
		worksheet_id = getWorksheetIdByName(service, spreadsheet_key, worksheet_name)

		pDate = str(polling_date.date())
		pTime = str(polling_date.time())

		#ワークシートが存在していればデータ登録
		if not worksheet_id:
			raise Exception([u'failed get worksheet by name, not exist worksheet', spreadsheet_key, worksheet_name])
			return

		else:

			# 該当日付のレコードを取得
			# データ取得（スプレッドシート用のクエリーをベタで作成）
			# WHERE句
			wheres = []
			wheres.append(config.getTimecardFieldTitle('date') + '=' + pDate)
			query = createListQuery(wheres)
			logging.debug("query:%s spreadsheet_key:%s",[query],[spreadsheet_key])
			logging.debug("userdata:%s",userdata)
			feed = getListFeedByCond(service, spreadsheet_key, worksheet_id, query.encode('utf-8'))	# utf-8固定

			# 該当行があれば更新
			if feed and len(feed.entry)>0:
				entry = feed.entry[0]

				data={}
				for label, custom in entry.custom.iteritems():
					data[label] = custom.text

				#登録値をセット
				data = self.makeRegistData(data, pType, polling_date, userdata['operator_name'], config)

				#更新
				#updateWorksheetRecord(service, feed.entry, data)
				service.UpdateRow(entry, data)

			else:
				data={}
				#登録値をセット
				data = self.makeRegistData(data, pType, polling_date, userdata['operator_name'], config)
				#更新
				service.InsertRow(data, spreadsheet_key, worksheet_id)

			#サンキューメール送信
			#self.sendThankyouMail(userdata, config)
		return

	def makeRegistData(self, data, pType, polling_date, name, config):
		'''タイムカード打刻用のデータを作成する'''
		pDate = str(polling_date.date())
		pTime = str(polling_date.time())

		data[config.getTimecardFieldTitle('date')] = pDate
		data[config.getTimecardFieldTitle('name')] = name
		data[config.getTimecardFieldTitle('sender')] = self.getLoginOperatorID()
		data[config.getTimecardFieldTitle('sender_info')] = self.request.remote_addr

		if pType=='CHECKIN':
				data[config.getTimecardFieldTitle('checkin')] = pTime
		elif pType=='CHECKOUT':
				data[config.getTimecardFieldTitle('checkout')] = pTime
		elif pType=='TEMPIN':
				data[config.getTimecardFieldTitle('tempin')] = pTime
		elif pType=='TEMPOUT':
				data[config.getTimecardFieldTitle('tempout')] = pTime

		return data

	def sendThankyouMail(self, vo, config):
		''' サンキューメールを送信する '''

		to_field = UcfUtil.getHashStr(config, self.QUEST_MASTERINFO_MAIL_TO_FIELD )
		sender   = UcfUtil.getHashStr(config, self.QUEST_MASTERINFO_MAIL_FROM )
		subject  = UcfUtil.getHashStr(config, self.QUEST_MASTERINFO_MAIL_SUBJECT )
		body     = UcfUtil.getHashStr(config, self.QUEST_MASTERINFO_MAIL_BODY )
		body_html= UcfUtil.getHashStr(config, self.QUEST_MASTERINFO_MAIL_BODYHTML )
		reply_to = UcfUtil.getHashStr(config, self.QUEST_MASTERINFO_MAIL_REPLY_TO )
		cc       = UcfUtil.getHashStr(config, self.QUEST_MASTERINFO_MAIL_CC )
		bcc      = UcfUtil.getHashStr(config, self.QUEST_MASTERINFO_MAIL_BCC )



		#to_fieldが設定されていたらメール送信
		if to_field and to_field!='':

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

			to = UcfUtil.getHashStr(vo, to_field).encode('utf-8')

			#メール送信（TODO 差込データとしてはとりあえずVOをそのまま渡す）
			try:
				UcfMailUtil.sendOneMail(to=to, cc=cc, bcc=bcc, reply_to=reply_to, sender=sender, subject=subject, body=body, body_html=body_html, data=vo)
			#ログだけ、エラーにしない
			except Exception,e:
				self.outputErrorLog(e)

	def getTimecardConfigInfo(self):
#		info = {}

		# Xml版 (Bigtableで管理する場合は別途実装)
		param_file_name = 'manager/timecard/timecard_config.xml'
#		param_file_path = self.getLocalParamFilePath(param_file_name)
		param_file_path = self.getParamFilePath(param_file_name)

#		if os.path.exists(param_file_path):
#			xmlDoc = UcfXml.load(param_file_path)
#			# ハッシュにして返す
#			info = xmlDoc.exchangeToHash(isAttr=True, isChild=True)
#			return info
#		else:
#			#self.redirectError(UcfMessage.getMessage(UcfMessage.MSG_NOT_EXIST_DATA, (master_id)))
#			return

		return TimecardTableHelperConfig(param_file_path)


		
############################################################
## バリデーションチェッククラス （アンケートエントリー用）
############################################################
class TimecardEntryValidator(BaseValidator):
	u'''入力チェッククラス'''
		
	def validate(self, helper, vo):
		pass

############################################################
## ビューヘルパー（ワークフロー申請管理用）
############################################################
class TimecardViewHelper(ViewHelper):

	def applicate(self, vo, helper):
		voVH = {}

		# ここで表示用変換を必要に応じて行うが、原則Djangoテンプレートのフィルタ機能を使う
		for k,v in vo.iteritems():
			voVH[k] = v	
		
		return voVH

