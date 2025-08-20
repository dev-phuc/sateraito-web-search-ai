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
class ABTestCountValidator(BaseValidator):
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
		check_name = u'マスタＩＤ'
		check_key = 'master_id'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 20):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '20')))
		# 半角英数字チェック
		if not self.alphabetNumberValidator(check_value, ('_')):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_ALPHABETNUMBER, (check_name)))

		########################
		check_name = u'アクセス回数'
		check_key = 'access_count'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 10):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '10')))
		# 半角数字チェック
		if not self.numberValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NUMERIC, (check_name)))

		########################
		check_name = u'削除Ｆ'
		check_key = 'del_flag'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# リストチェック
		if not self.listPatternValidator(check_value, ('DEL')):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MATCHING, (check_name, 'DEL')))


		# 重複チェック
		if self.total_count == 0:
			pass


############################################################
## ビューヘルパー
############################################################
class ABTestCountViewHelper(ViewHelper):

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
			elif k == 'access_count':
				voVH[k] = UcfUtil.getNumberFormat(v)
			# exchangeVoの時点で行うのでここでは不要
#			elif k == 'date_created':
#				voVH[k] = self.formatDateTime(v)
#			elif k == 'date_changed':
#				voVH[k] = self.formatDateTime(v)
			else:
				voVH[k] = v	

		return voVH
