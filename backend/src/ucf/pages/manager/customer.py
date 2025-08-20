# coding: utf-8

# XML関連
#import xml.dom.minidom as dom
#import xml.xpath as xpath
from xml.etree import ElementTree

# import os,sys,math
# from google.appengine.api import users
# from google.appengine.ext import webapp
# from google.appengine.ext.webapp import template
from ucf.utils.helpers import Helper, ViewHelper
from ucf.utils.validates import BaseValidator
from ucf.config.ucfconfig import *
from ucf.config.ucfmessage import *
from ucf.utils.ucfutil import *
from ucf.utils.models  import *


############################################################
## バリデーションチェッククラス 
############################################################
class CustomerValidator(BaseValidator):
	u'''入力チェッククラス'''
		
	def validate(self, helper, vo):
		
		# 初期化
		self.init()

		unique_id = UcfUtil.getHashStr(vo, 'unique_id')

		check_name = ''
		check_key = ''
		check_value = ''

		########################
		check_name = u'店舗ＩＤ'
		check_key = 'dept_id'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 長さチェック
		if not self.lengthValidator(check_value, 8):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_LENGTH, (check_name, '8')))
		# 半角英数字チェック
		if not self.alphabetNumberValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_ALPHABETNUMBER, (check_name)))
		# ログインオペレータとの整合性チェック
		if not helper.isSuperVisor():
			if helper.getLoginDeptID() != check_value:
				self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_INVALID_DEPT_ID, (check_value)))

		########################
		check_name = u'メールアドレス'
		check_key = 'mail_address'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 255):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '255')))
		# メールアドレスフォーマットチェック
		if not self.mailAddressValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAILADDRESS, (check_name, '255')))


		########################
		check_name = u'パスワード'
		check_key = 'password'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 12):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '12')))
		# 最小長チェック
		if not self.minLengthValidator(check_value, 5):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MINLENGTH, (check_name, '5')))
		# 半角英数字チェック
		if not self.alphabetNumberValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_ALPHABETNUMBER, (check_name)))


		########################
		check_name = u'顧客名'
		check_key = 'name'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 50):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '50')))

		########################
		check_name = u'顧客名カナ'
		check_key = 'name_kana'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 50):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '50')))
		# TODO カナチェック

		########################
		check_name = u'郵便番号'
		check_key = 'zip'
		check_value = UcfUtil.getHashStr(vo, check_key)
#		# 必須チェック
#		if not self.needValidator(check_value):
#			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 長さチェック
		if not self.lengthValidator(check_value, 7):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_LENGTH, (check_name, '7')))
		# 半角数字チェック
		if not self.numberValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NUMERIC, (check_name)))

		########################
		check_name = u'都道府県'
		check_key = 'address_ken'
		check_value = UcfUtil.getHashStr(vo, check_key)
#		# 必須チェック
#		if not self.needValidator(check_value):
#			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 長さチェック
		if not self.maxLengthValidator(check_value, 5):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '5')))



		########################
		check_name = u'住所２'
		check_key = 'address2'
		check_value = UcfUtil.getHashStr(vo, check_key)
#		# 必須チェック
#		if not self.needValidator(check_value):
#			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 長さチェック
		if not self.maxLengthValidator(check_value, 100):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '100')))

		########################
		check_name = u'住所３'
		check_key = 'address3'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 長さチェック
		if not self.maxLengthValidator(check_value, 100):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '100')))

		########################
		check_name = u'住所４'
		check_key = 'address4'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 長さチェック
		if not self.maxLengthValidator(check_value, 100):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '100')))

		########################
		check_name = u'電話番号'
		check_key = 'tel_no'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 長さチェック
		if not self.maxLengthValidator(check_value, 14):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '14')))
		# 半角数字チェック
		if not self.numberValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NUMERIC, (check_name)))

		########################
		check_name = u'ＦＡＸ番号'
		check_key = 'fax_no'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 長さチェック
		if not self.maxLengthValidator(check_value, 14):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '14')))
		# 半角数字チェック
		if not self.numberValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NUMERIC, (check_name)))

		########################
		check_name = u'モバイル番号'
		check_key = 'mobile_no'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 長さチェック
		if not self.maxLengthValidator(check_value, 14):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '14')))
		# 半角数字チェック
		if not self.numberValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NUMERIC, (check_name)))

		########################
		check_name = u'会社名称'
		check_key = 'company_name'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 長さチェック
		if not self.maxLengthValidator(check_value, 50):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '50')))

		########################
		check_name = u'所属部署'
		check_key = 'company_busho'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 長さチェック
		if not self.maxLengthValidator(check_value, 50):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '50')))

		########################
		check_name = u'役職'
		check_key = 'company_post'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 長さチェック
		if not self.maxLengthValidator(check_value, 50):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '50')))

		########################
		check_name = u'会員種別'
		check_key = 'member_type'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# リストチェック
		if not self.listPatternValidator(check_value, ('member', 'exit')):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MATCHING, (check_name, 'member exit')))

		########################
		check_name = u'ポイント停止Ｆ'
		check_key = 'point_use_stop_flag'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# リストチェック
		if not self.listPatternValidator(check_value, ('STOP')):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MATCHING, (check_name, 'STOP')))

		########################
		check_name = u'グループＩＤ'
		check_key = 'group_id'
		list = UcfUtil.csvToList(UcfUtil.getHashStr(vo, check_key))
		# リストチェック
		isError = False
		for v in list:
			check_value = v
			if not self.listPatternValidator(check_value, ('G01', 'G02', 'G03', 'G04')):
				isError = True
				break
		if isError:
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MATCHING, (check_name, 'G01 G02 G03 G04')))

		########################
		check_name = u'入会日'
		check_key = 'entry_date'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 日付チェック
		if not self.dateValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_DATE, (check_name)))

		########################
		check_name = u'退会日'
		check_key = 'exit_date'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 日付チェック
		if not self.dateValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_DATE, (check_name)))

		########################
		check_name = u'退会理由'
		check_key = 'exit_reason'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 長さチェック
		if not self.maxLengthValidator(check_value, 500):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '500')))

		########################
		check_name = u'削除Ｆ'
		check_key = 'del_flag'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# リストチェック
		if not self.listPatternValidator(check_value, ('DEL')):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MATCHING, (check_name, 'DEL')))


		# 重複チェック
		if self.total_count == 0:

			###############################################
			# メールアドレス
			gql = ""
			# WHERE句
			wheres = []
			wheres.append("dept_id='" + UcfUtil.escapeGql(UcfUtil.nvl(vo['dept_id'])) + "'")
			# 削除データはＯＫ
			wheres.append("del_flag=''")
			wheres.append("mail_address='" + UcfUtil.escapeGql(UcfUtil.nvl(vo['mail_address'])) + "'")
			gql += UcfUtil.getToGqlWhereQuery(wheres)

			models = UCFMDLCustomer.gql(gql)

			for model in models:
				# 新規以外の場合は対象のユニークＩＤ以外の場合のみエラーとする(TODO GQLがノットイコールに対応していないため)
				if self.edit_type == "new" or model.unique_id <> unique_id:
					self.appendValidate('mail_address', UcfMessage.getMessage(UcfMessage.MSG_VC_ALREADY_EXIST, ()))
					break

############################################################
## ビューヘルパー
############################################################
class CustomerViewHelper(ViewHelper):

	def applicate(self, vo, helper):
		voVH = {}

		# ここで表示用変換を必要に応じて行うが、原則Djangoテンプレートのフィルタ機能を使う
		for k,v in vo.iteritems():
			if k == 'del_flag':
				if v == 'DEL':
					voVH[k] = u'削除する'
				elif v == '':
					voVH[k] = u'削除しない'
				else:
					voVH[k] = v
			elif k == 'member_type':
				if v == 'member':
					voVH[k] = u'有効会員'
				elif v == 'exit':
					voVH[k] = u'退会'
				else:
					voVH[k] = v
			elif k == 'point_use_stop_flag':
				if v == 'STOP':
					voVH[k] = u'使用停止'
				elif v == '':
					voVH[k] = u'使用可能'
				else:
					voVH[k] = v
			elif k == 'group_id':
				disp = ''
				list = UcfUtil.csvToList(v)
				for value in list:
					value2 = value.replace(' ', '')
					for list_item in UcfConfig.GROUP_ID_LIST:
						if value2 == list_item[0]:
							disp = disp + '/' + list_item[1]
							break
				disp = disp.strip('/')
				voVH[k] = disp

			elif k == 'password':
				voVH[k] = '*********'
			# exchangeVoの時点で行うのでここでは不要
#			elif k == 'date_created':
#				voVH[k] = self.formatDateTime(v)
#			elif k == 'date_changed':
#				voVH[k] = self.formatDateTime(v)
			else:
				voVH[k] = v	
		
		return voVH
