# coding: utf-8

# XML関連
#import xml.dom.minidom as dom
#import xml.xpath as xpath
from xml.etree import ElementTree

# import os,sys,math,string
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
import ucf.gdata.spreadsheet.util

############################################################
## 簡単見積（アンケートを少しカスタマイズしたもの）
############################################################

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
class QuestionnairePageHelper(FrontHelper):

	_SATERAITOAPPS_SERVICEPACK_CKBOX = ['FLD38', 'FLD39', 'FLD40', 'FLD41', 'FLD42', 'FLD55']

	QUEST_MASTERINFO_ENTRY_TEMPLATE_FILENAME = 'Templates/@entry'
	QUEST_MASTERINFO_CONFIRM_TEMPLATE_FILENAME = 'Templates/@confirm'
	QUEST_MASTERINFO_THANKS_TEMPLATE_FILENAME = 'Templates/@thanks'

	QUEST_MASTERINFO_SPREADSHEET_ACCOUNT = 'Spreadsheet/@account'
	QUEST_MASTERINFO_SPREADSHEET_PASSWORD = 'Spreadsheet/@password'
	QUEST_MASTERINFO_SPREADSHEET_KEY = 'Spreadsheet/@key'
	QUEST_MASTERINFO_WORKSHEET_NAME = 'Spreadsheet/@worksheet_name'

	QUEST_MASTERINFO_MAIL_FROM = 'ThankYouMail/From'
	QUEST_MASTERINFO_MAIL_CC = 'ThankYouMail/Cc'
	QUEST_MASTERINFO_MAIL_BCC = 'ThankYouMail/Bcc'
	QUEST_MASTERINFO_MAIL_REPLY_TO = 'ThankYouMail/ReplyTo'
	QUEST_MASTERINFO_MAIL_TO_FIELD = 'ThankYouMail/To/@field'
	QUEST_MASTERINFO_MAIL_SUBJECT = 'ThankYouMail/Subject'
	QUEST_MASTERINFO_MAIL_BODY = 'ThankYouMail/Body'
	QUEST_MASTERINFO_MAIL_BODYHTML = 'ThankYouMail/BodyHtml'


	QUEST_MASTERINFO_MANAGE_MAIL_TO = 'ManageConfirmMail/To'
	QUEST_MASTERINFO_MANAGE_MAIL_FROM = 'ManageConfirmMail/From'
	QUEST_MASTERINFO_MANAGE_MAIL_CC = 'ManageConfirmMail/Cc'
	QUEST_MASTERINFO_MANAGE_MAIL_BCC = 'ManageConfirmMail/Bcc'
	QUEST_MASTERINFO_MANAGE_MAIL_REPLY_TO = 'ManageConfirmMail/ReplyTo'
#	QUEST_MASTERINFO_MANAGE_MAIL_TO_FIELD = 'ManageConfirmMail/To/@field'
	QUEST_MASTERINFO_MANAGE_MAIL_SUBJECT = 'ManageConfirmMail/Subject'
	QUEST_MASTERINFO_MANAGE_MAIL_BODY = 'ManageConfirmMail/Body'
	QUEST_MASTERINFO_MANAGE_MAIL_BODYHTML = 'ManageConfirmMail/BodyHtml'

	QUEST_MASTERINFO_MANAGE_COMP_MAIL_TO = 'ManageCompleteMail/To'
	QUEST_MASTERINFO_MANAGE_COMP_MAIL_FROM = 'ManageCompleteMail/From'
	QUEST_MASTERINFO_MANAGE_COMP_MAIL_CC = 'ManageCompleteMail/Cc'
	QUEST_MASTERINFO_MANAGE_COMP_MAIL_BCC = 'ManageCompleteMail/Bcc'
	QUEST_MASTERINFO_MANAGE_COMP_MAIL_REPLY_TO = 'ManageCompleteMail/ReplyTo'
#	QUEST_MASTERINFO_MANAGE_COMP_MAIL_TO_FIELD = 'ManageCompleteMail/To/@field'
	QUEST_MASTERINFO_MANAGE_COMP_MAIL_SUBJECT = 'ManageCompleteMail/Subject'
	QUEST_MASTERINFO_MANAGE_COMP_MAIL_BODY = 'ManageCompleteMail/Body'
	QUEST_MASTERINFO_MANAGE_COMP_MAIL_BODYHTML = 'ManageCompletesMail/BodyHtml'


	QUEST_MASTERINFO_DEFAULT_VALUES_PREFIX = 'DefaultInfo/@'
	
	def __init__(self):
		FrontHelper.__init__(self)
		pass


	########################################################
	## ★見積金額計算ファンク START.
	########################################################
	def calculateQuickPrice(self, vo, master_info):
		''' 見積もり金額の算出（0円以外のものは全てここに追加してください。合計金額の算出に使用するため） '''
		#TODO パラメータＸＭＬ化必要？
		total_quick_price = 0

		# 年間利用料金（アカウント数×500円×12ヶ月）
		user_count = int(UcfUtil.getHashStr(vo, 'FLD07'))
		price_of_user = 6000
		quick_price = user_count * price_of_user

		vo['QP_FLD07'] = str(quick_price)
		total_quick_price += quick_price
		

		# DNSの変更作業、アカウント登録などの初期設定作業
		if UcfUtil.getHashStr(vo, 'FLD30') == 'CHECK':
			quick_price = 50000		# 5万円固定
			vo['QP_FLD30'] = str(quick_price)
			total_quick_price += quick_price

		# エンタープライズ導入支援ソリューション（単価１人１日５万円）
		if UcfUtil.getHashStr(vo, 'FLD36') == 'CHECK':
			v = UcfUtil.getHashStr(vo, 'FLD37')
			# 何人日
			if v == u'1日':
				user_count = 1
			elif v == u'2日':
				user_count = 2
			elif v == u'3日':
				user_count = 3
			elif v == u'4日':
				user_count = 4
			elif v == u'5日':
				user_count = 5
			elif v == u'10日':
				user_count = 10
			elif v == u'20日':
				user_count = 20
			elif v == u'1.5人月':
				user_count = 30
			elif v == u'2人月':
				user_count = 40
			else:
				user_count = 0

			# ５万円（１担当者/日）
			price_of_user = 50000	
			quick_price = user_count * price_of_user

			vo['QP_FLD37'] = str(quick_price)
			total_quick_price += quick_price

		# サテライトＡｐｐｓサービスパック（１人月額150 or 200 円 最低15000円）
#		v = UcfUtil.getHashStr(vo, 'FLD43')
		v = UcfUtil.getHashStr(vo, 'FLD07')

		
		# FLD38,39,40,41,42,55 のうち3つまでチェックなら150円、4つ以上だと200円で計算！！
		# 項目は_SATERAITOAPPS_SERVICEPACK_CKBOXに定義されています。
		check_cnt = 0
		ck_ary = self._SATERAITOAPPS_SERVICEPACK_CKBOX
		for ck in ck_ary:
			if UcfUtil.getHashStr(vo, ck) == 'CHECK':
				check_cnt += 1

		if check_cnt == 0:
			quick_price = 0
		else:
			if check_cnt <= 3:
				price_of_user = 150
			else:
				price_of_user = 200
			min_total_price = 15000

			if int(v) <= 0:
				quick_price = 0
			elif int(v) * price_of_user >= min_total_price:
				quick_price = int(v) * price_of_user
			else:
				quick_price = min_total_price

		# 1年分なので12をかける
		quick_price = quick_price * 12

		vo['QP_FLD43'] = str(quick_price)	# ここはFLD43でOK
		total_quick_price += quick_price

		# 合計見積金額
		vo['QP_TOTAL'] = str(total_quick_price)
	########################################################
	## ★見積金額計算ファンク END.
	########################################################



	def registEntry(self, vo, master_info):
		u''' アンケート回答を１つ新規登録 '''

		account  = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SPREADSHEET_ACCOUNT)
		password = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SPREADSHEET_PASSWORD)
		spreadsheet_key = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_SPREADSHEET_KEY)
		worksheet_name  = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_WORKSHEET_NAME)
		worksheet_id = None

		service = ucf.gdata.spreadsheet.util.getSpreadsheetsService(account, password, self.getRootPath())
		worksheet_id = ucf.gdata.spreadsheet.util.getWorksheetIdByName(service, spreadsheet_key, worksheet_name)

		#ワークシートが存在していればデータ登録
		if not worksheet_id:
			raise Exception([u'failed get worksheet by name, not exist worksheet', spreadsheet_key, worksheet_name])
			return

		else:
			#回答データのキー一覧を作成（チェックボックスの値がPOSTされない場合を防ぐための暫定措置）
#			keys = []
#			for k in vo.keys():
#				# 回答フィールドのキーなら追加
#				if k.startswith(_field_prefix):
#					keys.append(k)

			max_key = ''
			for k in vo.keys():
				# 回答フィールドのキーなら追加
				if k.startswith(_field_prefix) and (max_key == '' or k > max_key):
					max_key = k

			max_key_cnt = 0
			max_key_cnt = int(UcfUtil.subString(max_key, len(_field_prefix)))

			keys = []
			for i in range(max_key_cnt):
				keys.append(_field_prefix + str(i + 1).zfill(2))

			#並び替え
			keys.sort()

			#データ生成
			values=[]
			enq_date = str(UcfUtil.getNowLocalTime())
			values.append(enq_date)

			for key in keys:
#				values.append(vo[key])
				values.append(UcfUtil.getHashStr(vo, key))
#				self.response.out.write(key + ":" + UcfUtil.getHashStr(vo, key) + '<BR>')
#			return

			#レコード追加
			ucf.gdata.spreadsheet.util.addWorksheetRecord(service, spreadsheet_key, worksheet_id, values)

			#サンキューメール送信
			self.sendThankyouMail(vo, master_info)
		return

	def sendThankyouMail(self, vo, master_info):
		''' サンキューメールを送信する '''

		to_field = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_TO_FIELD )
		sender   = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_FROM )
		subject  = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_SUBJECT )
		body     = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_BODY )
		body_html= UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_BODYHTML )
		reply_to = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_REPLY_TO )
		cc       = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_CC )
		bcc      = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MAIL_BCC )



		#to_fieldが設定されていたらメール送信
		if to_field and to_field!='':

			to = UcfUtil.getHashStr(vo, to_field).encode('utf-8')

			#メール送信（TODO 差込データとしてはとりあえずVOをそのまま渡す）
			try:
				UcfMailUtil.sendOneMail(to=to, cc=cc, bcc=bcc, reply_to=reply_to, sender=sender, subject=subject, body=body, body_html=body_html, data=vo)
			#ログだけ、エラーにしない
			except Exception as e:
				self.outputErrorLog(e)

	def sendManageConfirmMail(self, vo, master_info):
		''' 管理者への確認メールを送信する '''

		to = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_MAIL_TO )
		sender   = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_MAIL_FROM )
		subject  = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_MAIL_SUBJECT )
		body     = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_MAIL_BODY )
		body_html= UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_MAIL_BODYHTML )
		reply_to = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_MAIL_REPLY_TO )
		cc       = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_MAIL_CC )
		bcc      = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_MAIL_BCC )


		#to_fieldが設定されていたらメール送信
		if to and to != '':

			#メール送信（TODO 差込データとしてはとりあえずVOをそのまま渡す）
			try:
				UcfMailUtil.sendOneMail(to=to, cc=cc, bcc=bcc, reply_to=reply_to, sender=sender, subject=subject, body=body, body_html=body_html, data=vo)
			#ログだけ、エラーにしない
			except Exception as e:
				self.outputErrorLog(e)

	def sendManageCompleteMail(self, vo, master_info):
		''' 管理者への完了メールを送信する '''

		to = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_COMP_MAIL_TO )
		sender   = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_COMP_MAIL_FROM )
		subject  = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_COMP_MAIL_SUBJECT )
		body     = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_COMP_MAIL_BODY )
		body_html= UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_COMP_MAIL_BODYHTML )
		reply_to = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_COMP_MAIL_REPLY_TO )
		cc       = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_COMP_MAIL_CC )
		bcc      = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_MANAGE_COMP_MAIL_BCC )


		#to_fieldが設定されていたらメール送信
		if to and to != '':

			#メール送信（TODO 差込データとしてはとりあえずVOをそのまま渡す）
			try:
				UcfMailUtil.sendOneMail(to=to, cc=cc, bcc=bcc, reply_to=reply_to, sender=sender, subject=subject, body=body, body_html=body_html, data=vo)
			#ログだけ、エラーにしない
			except Exception as e:
				self.outputErrorLog(e)


	def getQuestionnaireMasterInfo(self, master_id):
		info = {}

		# Xml版 (Bigtableで管理する場合は別途実装)
		param_file_name = master_id + '.xml'
		param_file_path = self.getLocalParamFilePath(param_file_name)
		if os.path.exists(param_file_path):
			xmlDoc = UcfXml.load(param_file_path)
			# ハッシュにして返す
			info = xmlDoc.exchangeToHash(isAttr=True, isChild=True)
			return info
		else:
			#self.redirectError(UcfMessage.getMessage(UcfMessage.MSG_NOT_EXIST_DATA, (master_id)))
			return

	def isConfirmQuestionnaire(self, master_info):
		'''確認画面ありかどうか'''
		#確認画面テンプレートHTML設定があれば、確認画面あり
		confirm_template_name = UcfUtil.getHashStr(master_info, self.QUEST_MASTERINFO_CONFIRM_TEMPLATE_FILENAME)
		return (confirm_template_name != '')

	def getDefaultAnswerValues(self, master_info):
		'''回答デフォルト値を取得'''
		default_values = {}
		
		for k,v in master_info.iteritems():
			# デフォルト値情報のみを抜き出す
			prefix = self.QUEST_MASTERINFO_DEFAULT_VALUES_PREFIX
			prefix_length = len(self.QUEST_MASTERINFO_DEFAULT_VALUES_PREFIX)
			if k.startswith(prefix) and len(k) > prefix_length:
				field_key = UcfUtil.subString(k, prefix_length)
				if not field_key in default_values:
					default_values[field_key] = v
		return default_values

	

		
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

############################################################
## ビューヘルパー
############################################################
class QuestionnaireViewHelper(ViewHelper):

	def applicate(self, vo, helper):
		voVH = {}

		# ここで表示用変換を必要に応じて行うが、原則Djangoテンプレートのフィルタ機能を使う
		for k,v in vo.iteritems():
			if k.startswith('QP_'):
				voVH[k] = UcfUtil.getNumberFormat(v)
			else:
				voVH[k] = v	
		
		return voVH

