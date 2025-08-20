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
class OperatorValidator(BaseValidator):
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
		check_name = u'オペレータＩＤ'
		check_key = 'operator_id'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 100):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '100')))
		# 半角英数字チェック
		# 記号の入力が不可能となる為、チェック方法を変更
	#	if not self.alphabetNumberValidator(check_value):
	#		self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_ALPHABETNUMBER, (check_name)))
		self.applicateAutoCmd(check_value, check_key, check_name, "A[-_.]")

		########################
		check_name = u'オペレータ名'
		check_key = 'operator_name'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 50):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '50')))

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
		check_name = u'アクセス権限'
		check_key = 'access_authority'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# リストチェック
		if not self.listPatternValidator(check_value, ('ADMIN', 'MANAGER')):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MATCHING, (check_name, 'ADMIN MANAGER')))

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
			# オペレータＩＤ
			'''
			q = UCFMDLOperator.all()
			q.filter("dept_id=", UcfUtil.nvl(vo['dept_id']))
			q.filter("del_flag=", '')
			q.filter("operator_id=", UcfUtil.nvl(vo['operator_id']))
			models = q.fetch(1)	#データ不備さえなければ1件取れば判別できるので！少し危険だが..

			for model in models:
				# 新規以外の場合は対象のユニークＩＤ以外の場合のみエラーとする(TODO GQLがノットイコールに対応していないため)
				if self.edit_type == "new" or model.unique_id <> unique_id:
					self.appendValidate('operator_id', UcfMessage.getMessage(UcfMessage.MSG_VC_ALREADY_EXIST, ()))
					break
			'''

			gql = ""
			# WHERE句
			wheres = []
			wheres.append("dept_id='" + UcfUtil.escapeGql(UcfUtil.nvl(vo['dept_id'])) + "'")
			# 削除データはＯＫ
			wheres.append("del_flag=''")
			wheres.append("operator_id='" + UcfUtil.escapeGql(UcfUtil.nvl(vo['operator_id'])) + "'")
			gql += UcfUtil.getToGqlWhereQuery(wheres)
			models = UCFMDLOperator.gql(gql)

			for model in models:
				# 新規以外の場合は対象のユニークＩＤ以外の場合のみエラーとする(TODO GQLがノットイコールに対応していないため)
				if self.edit_type == "new" or model.unique_id <> unique_id:
					self.appendValidate('operator_id', UcfMessage.getMessage(UcfMessage.MSG_VC_ALREADY_EXIST, ()))
					break


############################################################
## ビューヘルパー
############################################################
class OperatorViewHelper(ViewHelper):

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
			elif k == 'access_authority':
				if v == 'ADMIN':
					voVH[k] = u'管理権限'
				elif v == 'MANAGER':
					voVH[k] = u'一般オペレータ'
				else:
					voVH[k] = v
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
