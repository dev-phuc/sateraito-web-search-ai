# coding: utf-8

# import os,sys,math,logging
# import re
# from google.appengine.api import users
# from google.appengine.ext import webapp
# from google.appengine.ext.webapp import template
from ucf.utils.helpers import *
from ucf.utils.validates import BaseValidator
from ucf.config.ucfconfig import *
from ucf.config.ucfmessage import *
from ucf.utils.ucfutil import *
from ucf.utils.ucfxml import *
from ucf.utils.models  import *
from ucf.utils.mailutil import *
from ucf.utils.numbering import *

from xml.etree import ElementTree
from ucf.gdata.sites.util import SitesUtil

############################################################
## ちょっとした定数（このpy内でのみ使用可能.呼び出しもとのpyから使用する場合はファンクを介すること）
############################################################
_field_prefix = "FLD"
_cmd_prefix = "cmd_"
_field_type_prefix = "ftp_"
_seq_prefix = "SEQ"
_flow_group_prefix = "GP_"
_flow_type_prefix = "tp_"
_flow_agency_prefix = "agency_"
_dispname_prefix = "dn_"

_FIELD_TYPE = {'LINK':'LINK', 'FILE':'FILE'}

#_ACTION_TYPE = {'APPLY':'APPLY', 'CIRCULATE':'CIRCULATE', 'RECOG':'RECOG', 'DENY':'DENY'}
_ACTION_TYPE = {'APPLY':'APPLY', 'CANCEL':'CANCEL', 'CIRCULATE':'CIRCULATE', 'AGENCY_CIRCULATE':'AGENCY_CIRCULATE', 'RECOG':'RECOG', 'AGENCY_RECOG':'AGENCY_RECOG', 'APPROVAL':'APPROVAL', 'AGENCY_APPROVAL':'AGENCY_APPROVAL', 'DENY':'DENY', 'AGENCY_DENY':'AGENCY_DENY', 'AGENCY_DENY':'AGENCY_DENIED', 'AGENCY_CIRCULATED':'AGENCY_CIRCULATED', 'AGENCY_RECOGNIZED':'AGENCY_RECOGNIZED', 'AGENCY_APPROVED':'AGENCY_APPROVED'}



############################################################
## バリデーションチェッククラス （ワークフローエントリー用）
############################################################
class UwfEntryValidator(BaseValidator):
	u'''入力チェッククラス'''
		
	def validate(self, helper, vo):
		
		# 初期化
		self.init()

		unique_id = UcfUtil.getHashStr(vo, 'unique_id')

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
## バリデーションチェッククラス（ワークフロー承認用）
############################################################
class WorkFlowRecogValidator(BaseValidator):
	u'''入力チェッククラス'''
		
	def validate(self, helper, vo, sub_auth):
		
		# 初期化
		self.init()

		unique_id = UcfUtil.getHashStr(vo, 'unique_id')

		check_name = ''
		check_key = ''
		check_value = ''

		########################
		check_name = u'コメント'
		check_key = 'recog_comment'
#		check_value = UcfUtil.getHashStr(vo, check_key)
		check_value = UcfUtil.nvl(helper.getRequest(check_key))
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 25):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '25')))

		# 重複チェック
		if self.total_count == 0:
			pass



############################################################
## バリデーションチェッククラス（ワークフロー申請管理用）
############################################################
class WorkFlowValidator(BaseValidator):
	u'''入力チェッククラス'''
		
	def validate(self, helper, vo):
		
		# 初期化
		self.init()

		unique_id = UcfUtil.getHashStr(vo, 'unique_id')

		check_name = ''
		check_key = ''
		check_value = ''

		########################
		check_name = u'設定ＩＤ'
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
		check_name = u'申請フォームＩＤ'
		check_key = 'template_id'
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
		check_name = u'申請者ＩＤ'
		check_key = 'apply_operator_id'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 100):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '100')))
		## 半角英数字チェック IDに記号を含む事がある為、削除 2011/03/04
		#if not self.alphabetNumberValidator(check_value, ('_')):
		#	self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_ALPHABETNUMBER, (check_name)))

		########################
		check_name = u'申請日時'
		check_key = 'apply_date'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 日付型チェック
		if not self.dateValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_DATE, (check_name)))


		########################
		check_name = u'ステータス'
		check_key = 'status'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 20):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '20')))
		# 半角英数字チェック
		if not self.alphabetNumberValidator(check_value, ('_')):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_ALPHABETNUMBER, (check_name)))
		# TODO 値チェック

		########################
		check_name = u'決裁ステータス'
		check_key = 'approval_status'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 20):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '20')))
		# 半角英数字チェック
		if not self.alphabetNumberValidator(check_value, ('_')):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_ALPHABETNUMBER, (check_name)))
		# TODO 値チェック

		########################
		check_name = u'申請SEQNO'
		check_key = 'recog_seq_no'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 半角数字チェック
		if not self.numberValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NUMERIC, (check_name)))

		########################
		check_name = u'申請情報'
		check_key = 'entry_detail'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# TODO ＸＭＬ型チェック

		########################
		check_name = u'最終承認者ＩＤ'
		check_key = 'last_recognition_name'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 100):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '100')))
		## 半角英数字チェック IDに記号を含む事がある為、削除 2011/03/04
		#if not self.alphabetNumberValidator(check_value, ('_')):
		#	self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_ALPHABETNUMBER, (check_name)))

		########################
		check_name = u'次回承認者ＩＤ'
		check_key = 'next_recognition_name'
		check_value = UcfUtil.getHashStr(vo, check_key)
		## 最大長チェック 複数ID入力時にほぼ無制限に文字が入る為、削除 2011/03/04
		#if not self.maxLengthValidator(check_value, 100):
		#	self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '100')))
		## 半角英数字チェック IDに記号を含む事がある為、削除 2011/03/04
		#if not self.alphabetNumberValidator(check_value, ('_,')):
		#	self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_ALPHABETNUMBER, (check_name)))

		########################
		check_name = u'次回承認タイプ'
		check_key = 'next_recognition_type'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# リストチェック
		if not self.listPatternValidator(check_value, ('APPROVAL', 'RECOG', 'CIRCULATE')):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MATCHING, (check_name, 'APPROVAL RECOG CIRCULATE')))

		########################
		check_name = u'代理承認者ＩＤ'
		check_key = 'agency_recognition_name'
		check_value = UcfUtil.getHashStr(vo, check_key)
		## 最大長チェック 複数ID入力時にほぼ無制限に文字が入る為、削除 2011/03/04
		#if not self.maxLengthValidator(check_value, 100):
		#	self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '100')))
		## 半角英数字チェック IDに記号を含む事がある為、削除 2011/03/04
		#if not self.alphabetNumberValidator(check_value, ('_,')):
		#	self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_ALPHABETNUMBER, (check_name)))

		########################
		check_name = u'次回承認期限'
		check_key = 'next_recognition_limit'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 日付型チェック
		if not self.dateValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_DATE, (check_name)))

		########################
		check_name = u'最終承認日時'
		check_key = 'last_recognition_date'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 日付型チェック
		if not self.dateValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_DATE, (check_name)))


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
## バリデーションチェッククラス（ワークフロー設定管理用）
############################################################
class WorkFlowMasterValidator(BaseValidator):
	u'''入力チェッククラス'''
		
	def validate(self, helper, vo):
		
		# 初期化
		self.init()

		unique_id = UcfUtil.getHashStr(vo, 'unique_id')

		check_name = ''
		check_key = ''
		check_value = ''

		########################
		check_name = u'設定ＩＤ'
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
		check_name = u'設定名称'
		check_key = 'title'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# 最大長チェック
		if not self.maxLengthValidator(check_value, 100):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_MAXLENGTH, (check_name, '100')))

		########################
		check_name = u'承認フロー設定'
		check_key = 'workflow_config'
		check_value = UcfUtil.getHashStr(vo, check_key)
		# 必須チェック
		if not self.needValidator(check_value):
			self.appendValidate(check_key, UcfMessage.getMessage(UcfMessage.MSG_VC_NEED, (check_name)))
		# TODO ＸＭＬ型チェック


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
			# 設定ＩＤ
			'''
			q = UCFMDLWorkFlowMaster.all()
			q.filter("dept_id=", UcfUtil.nvl(vo['dept_id']))
			q.filter("del_flag=", '')
			q.filter("master_id=", UcfUtil.nvl(vo['master_id']))
			models = q.fetch(1)	#データ不備さえなければ1件取れば判別できるので！少し危険だが..

			for model in models:
				# 新規以外の場合は対象のユニークＩＤ以外の場合のみエラーとする(TODO GQLがノットイコールに対応していないため)
				if self.edit_type == "new" or model.unique_id <> unique_id:
					self.appendValidate('master_id', UcfMessage.getMessage(UcfMessage.MSG_VC_ALREADY_EXIST, ()))
					break
			'''

			gql = ""
			# WHERE句
			wheres = []
			wheres.append("dept_id='" + UcfUtil.escapeGql(UcfUtil.nvl(vo['dept_id'])) + "'")
			# 削除データはＯＫ
			wheres.append("del_flag=''")
			wheres.append("master_id='" + UcfUtil.escapeGql(UcfUtil.nvl(vo['master_id'])) + "'")
			gql += UcfUtil.getToGqlWhereQuery(wheres)
			models = UCFMDLWorkFlowMaster.gql(gql)

			for model in models:
				# 新規以外の場合は対象のユニークＩＤ以外の場合のみエラーとする(TODO GQLがノットイコールに対応していないため)
				if self.edit_type == "new" or model.unique_id <> unique_id:
					self.appendValidate('master_id', UcfMessage.getMessage(UcfMessage.MSG_VC_ALREADY_EXIST, ()))
					break


############################################################
## ビューヘルパー
############################################################
class UwfEntryViewHelper(ViewHelper):

	def applicate(self, vo, helper):
		voVH = {}

		# ここで表示用変換を必要に応じて行うが、原則Djangoテンプレートのフィルタ機能を使う
		for k,v in vo.iteritems():
			voVH[k] = v	

		return voVH

############################################################
## ビューヘルパー（ワークフロー申請管理用）
############################################################
class WorkFlowViewHelper(ViewHelper):

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
			# exchangeVoの時点で行うのでここでは不要
#			elif k == 'date_created':
#				voVH[k] = self.formatDateTime(v)
#			elif k == 'date_changed':
#				voVH[k] = self.formatDateTime(v)

			# 承認履歴
			elif k == 'recognition_history':
				disp = ''
				list = UcfUtil.csvToList(v)
				for value in list:
					# disp = disp + '\r\n' + unicode(value).encode('utf-8').replace(' ', '')
					disp = disp + '\r\n' + value.replace(' ', '')
				disp = disp.strip('\r\n')
				voVH[k] = disp

			# 承認履歴コメント
			elif k == 'recognition_history_comment':
				disp = ''
				list = UcfUtil.csvToList(v)
				for value in list:
#					disp = disp + '\r\n' + value.replace(' ', '')
					# disp = disp + '\r\n' + unicode(value).encode('utf-8')
					disp = disp + '\r\n' + value
				disp = disp.strip('\r\n')
				voVH[k] = disp

			# 次回承認タイプ
			elif k == 'next_recognition_type':
				if v == 'RECOG':
					voVH[k] = u'承認'
				elif v == 'APPROVAL':
					voVH[k] = u'決裁'
				elif v == 'CIRCULATE':
					voVH[k] = u'閲覧'
				else:
					voVH[k] = v

			# 申請日時
			elif k == 'apply_date':
				if v == '':
					voVH[k] = v
				else:
#					# ローカルタイムに変換
#					date = UcfUtil.nvl(UcfUtil.getLocalTime(UcfUtil.getDateTime(v)))
#					voVH[k] = date
					voVH[k] = v


			# ステータス
			elif k == 'status':
				if v == '':
					voVH[k] = u'申請中'
				elif v == 'PROCESSING':
					voVH[k] = u'処理中'
				elif v == 'DENIED':
					voVH[k] = u'否認/差戻'
				elif v == 'PROCESSED':
					voVH[k] = u'処理済'
				elif v == 'CANCELED':
					voVH[k] = u'申請取消'
				else:
					voVH[k] = v

			# 決裁ステータス
			elif k == 'approval_status':
				if v == '':
					voVH[k] = u'未決裁'
				elif v == 'APPROVED':
					voVH[k] = u'決裁済'
				else:
					voVH[k] = v

			# 次回承認期限
			elif k == 'next_recognition_limit':
				if v == '':
					voVH[k] = v
				else:
#					# ローカルタイムに変換
#					date = UcfUtil.nvl(UcfUtil.getLocalTime(UcfUtil.getDateTime(v)))
#					voVH[k] = date
					voVH[k] = v

			# 最終承認日
			elif k == 'last_recognition_date':
				if v == '':
					voVH[k] = v
				else:
#					# ローカルタイムに変換
#					date = UcfUtil.nvl(UcfUtil.getLocalTime(UcfUtil.getDateTime(v)))
#					voVH[k] = date
					voVH[k] = v

			# 被代理情報
			elif k == 'agency_process_history':
				disp = ''
				list = UcfUtil.csvToList(v)
				for value in list:
					value_ary = value.split('/')
					agency_action_type = value_ary[0]
					agency_operator_id = value_ary[1]

					# 代理閲覧された場合
					if agency_action_type == getActionType('AGENCY_CIRCULATED'):
						disp = disp + '\r\n' + u'被代理閲覧' + '(' + agency_operator_id + ')'
					# 代理承認された場合
					elif agency_action_type == getActionType('AGENCY_RECOGNIZED'):
						disp = disp + '\r\n' + u'被代理承認' + '(' + agency_operator_id + ')'
					# 代理決裁された場合
					elif agency_action_type == getActionType('AGENCY_APPROVED'):
						disp = disp + '\r\n' + u'被代理決裁' + '(' + agency_operator_id + ')'
					# 代理否認された場合
					elif agency_action_type == getActionType('AGENCY_DENIED'):
						disp = disp + '\r\n' + u'被代理否認/差戻' + '(' + agency_operator_id + ')'

				disp = disp.strip('\r\n')
				voVH[k] = disp


			else:
				voVH[k] = v	
		return voVH



############################################################
## ビューヘルパー（ワークフロー詳細：ワークフロー順序用）
############################################################
class WorkFlowSequenceViewHelper(ViewHelper):

	def applicate(self, vo, helper):
		voVH = {}
		# ここで表示用変換を必要に応じて行うが、原則Djangoテンプレートのフィルタ機能を使う
		for k,v in vo.iteritems():
			# 承認タイプ
			if k == 'flow_type':
				if v == 'RECOG':
					voVH[k] = u'承認'
				elif v == 'APPROVAL':
					voVH[k] = u'決裁'
				elif v == 'CIRCULATE':
					voVH[k] = u'閲覧'
				else:
					voVH[k] = v

			# ＩＤタイプ
			elif k == 'id_type':
				if v == 'OPERATOR':
					voVH[k] = u'オペレータ'
				elif v == 'GROUP':
					voVH[k] = u'グループ'
				else:
					voVH[k] = v

			# 処理済フラグ
			elif k == 'deal_flag':
				if v == 'DEAL':
					voVH[k] = u'済'
				elif v == '':
					voVH[k] = u'未'
				else:
					voVH[k] = v

			else:
				voVH[k] = v	
		
		return voVH



############################################################
## ビューヘルパー（ワークフロー申請の履歴一覧用）
############################################################
class WorkFlowHistoryViewHelper(ViewHelper):

	def applicate(self, vo, helper):
		voVH = {}

		# ここで表示用変換を必要に応じて行うが、原則Djangoテンプレートのフィルタ機能を使う
		for k,v in vo.iteritems():
			# アクションタイプ

			if k == 'action_type':
				if v == 'APPLY':
					voVH[k] = u'申請'
				elif v == 'CANCEL':
					voVH[k] = u'申請取消'
				elif v == 'CIRCULATE':
					voVH[k] = u'閲覧'
				elif v == 'AGENCY_CIRCULATE':
					voVH[k] = u'代理閲覧'
				elif v == 'APPROVAL':
					voVH[k] = u'決裁'
				elif v == 'AGENCY_APPROVAL':
					voVH[k] = u'代理決裁'
				elif v == 'RECOG':
					voVH[k] = u'承認'
				elif v == 'AGENCY_RECOG':
					voVH[k] = u'代理承認'
				elif v == 'DENY':
					voVH[k] = u'否認/差戻'
				elif v == 'AGENCY_DENY':
					voVH[k] = u'代理否認/差戻'
				elif v == 'AGENCY_CIRCULATED':
					voVH[k] = u'被代理閲覧'
				elif v == 'AGENCY_APPROVED':
					voVH[k] = u'被代理決裁'
				elif v == 'AGENCY_DENIED':
					voVH[k] = u'被代理否認/差戻'
				elif v == 'AGENCY_RECOGNIZED':
					voVH[k] = u'被代理承認'
				else:
					voVH[k] = v

			# 日時
			elif k == 'action_date':
				if v == '':
					voVH[k] = v
				else:
					# yyyy-mm-dd hh:MM-ss形式をyyyy/mm/dd hh:MM-ss形式に変換
					date = v
					date = UcfUtil.getDateTime(date)
					date = UcfUtil.nvl(date)
					voVH[k] = date

			else:
				voVH[k] = v	
		
		return voVH




############################################################
## ビューヘルパー（ワークフロー設定管理用）
############################################################
class WorkFlowMasterViewHelper(ViewHelper):

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
			# exchangeVoの時点で行うのでここでは不要
#			elif k == 'date_created':
#				voVH[k] = self.formatDateTime(v)
#			elif k == 'date_changed':
#				voVH[k] = self.formatDateTime(v)

			else:
				voVH[k] = v	
		
		return voVH



############################################################
## ちょっとしたファンク ※_incイメージ（こんなところにかいてもいいのかな～）
############################################################
def getActionType(key):
	u''' アクションタイプから１つ値を取得 '''
	return UcfUtil.getHashStr(_ACTION_TYPE, key)

def getAllActionType():
	u''' アクションタイプ辞書を取得 '''
	return _ACTION_TYPE

def getValidOperator(helper, operator_id):
	u''' 有効なオペレータ情報を取得 '''

	result = None
	if operator_id != '':
		gql = ""
		wheres = []
		wheres.append("dept_id='" + UcfUtil.escapeGql(helper.getLoginDeptID()) + "'")
		wheres.append("del_flag=''")
		wheres.append("operator_id='" + UcfUtil.escapeGql(operator_id) + "'")
		gql += UcfUtil.getToGqlWhereQuery(wheres)
		models = UCFMDLOperator.gql(gql)
		result = None
		for model in models:
			result = model
			break
	return result

def getValidWorkFlowMaster(helper, master_id, dept_id):
	u''' 有効なワークフロー設定マスタを取得 '''
	gql = ""
	wheres = []
	wheres.append("dept_id='" + UcfUtil.escapeGql(dept_id) + "'")
	wheres.append("del_flag=''")
	wheres.append("master_id='" + UcfUtil.escapeGql(master_id) + "'")
	gql += UcfUtil.getToGqlWhereQuery(wheres)
	mdlMasters = UCFMDLWorkFlowMaster.gql(gql)
	mdlMaster = None
	for model in mdlMasters:
		mdlMaster = model
		break
	return mdlMaster

def registWorkFlowEntry(helper, mdlMaster, vo):
	u''' ワークフロー申請を１つ新規登録 '''

	# マスタから設定XMLをロードしておく（TODO 文字コード変換を何とかしたい） 2011/06/08 Djangoテンプレート更新に伴い文字コード変換を削除
	# xmlConfig = UcfXml.loadXml(unicode(mdlMaster.workflow_config).encode('utf-8'))
	xmlConfig = UcfXml.loadXml(mdlMaster.workflow_config)

	# 添付ファイルの処理（HTTPアップロード）
	# hash_attach_info･･･KEY:フィールド名（例･･･「FLD001」）VALUE:[アップロード先のＵＲＬ, ファイル名]
	hash_attach_info = uploadAttachmentFilesToGoogleSites(helper, vo, xmlConfig)

	# type=FILEのvo値を加工
	for k,v in hash_attach_info.iteritems():
		field_name = k
		file_info = v
		vo[field_name] = file_info[0]

	unique_id = UcfUtil.guid()
	mdlData = UCFMDLWorkFlow(unique_id=unique_id,key_name=UcfConfig.KEY_PREFIX + unique_id)

#	# Voからモデルにマージ
#	mdlData.margeFromVo(vo, helper)
	# 管理コメント（空）
	mdlData.comment = ''
	# 店舗ＩＤ（ログインオペレータの店舗ＩＤ）
	mdlData.dept_id = helper.getLoginDeptID()
	# 申請ID
	# 申請IDの生成
	number = Numbering(helper.getLoginDeptID(),UcfConfig.NUMBERING_WORFROW_NUMBER_ID,UcfConfig.NUMBERING_WORFROW_NUMBER_SUB_ID,UcfConfig.NUMBERING_WORFROW_PREFIX,UcfConfig.NUMBERING_WORFROW_SEQUENCE_NO_DIGIT)
	mdlData.apply_id = number.countup()
	# 表示用にIDを格納
	vo['apply_id'] = mdlData.apply_id

	# ワークフロー設定ＩＤ
	mdlData.master_id = mdlMaster.master_id
	# 申請フォームＩＤ
	mdlData.template_id = UcfUtil.nvl(vo['tpid'])
	# 申請者
	mdlData.apply_operator_id = UcfUtil.nvl(helper.getLoginOperatorID())
	# 申請日時
	mdlData.apply_date = UcfUtil.getNow()

	# 入力テンプレートID
	mdlData.input_template_id = UcfUtil.nvl(vo['input_template_id'])
	# 確認テンプレートID
	mdlData.confirm_template_id = UcfUtil.nvl(vo['confirm_template_id'])
	# 完了テンプレートID
	mdlData.thanks_template_id = UcfUtil.nvl(vo['thanks_template_id'])

	# ステータス
	mdlData.status = ''
	# 決裁ステータス
	mdlData.approval_status = ''
	# 承認SEQNO
	mdlData.recog_seq_no = 0

	# 最初のオペレータＩＤを保持する変数（あとで使用する）
	first_flow_id_list = []
	first_agency_flow_id_list = []
	# 最初のオペレータが何をするか（承認）
	first_flow_type = ''


	###############################################
	# 申請情報（XML）
	root = UcfXml.createNode('Ucf')
	# 入力ボックス情報の作成
	form_info = UcfXml.createNode('FormInfo')
	root.append(form_info)

	cmd_prefix_length = len(_cmd_prefix)
	field_prefix_length = len(_field_prefix)
	seq_prefix_length = len(_seq_prefix)
	field_type_prefix_length = len(_field_type_prefix)
	flow_type_prefix_length = len(_flow_type_prefix)
	flow_agency_prefix_length = len(_flow_agency_prefix)

	# チェックボックス・ラジオボタンが選択されていない場合などPOSTされない項目の処理に対応 2010/01/29 T.ASAO
	# 処理したキーをセットしておく（最後に未処理項目を「cmd_」からループして処理するため）
	hash_deal = {}

	# 入力フォーム分だけItemノードを作成
	for k,v in vo.iteritems():
		isAppend = False
		# fld_
		if k.startswith(_field_prefix) and len(k) > field_prefix_length:
			isAppend = True
		# SEQ
		elif k.startswith(_seq_prefix) and len(k) > seq_prefix_length:
			isAppend = True
		# tp_
		elif k.startswith(_flow_type_prefix) and len(k) > flow_type_prefix_length:
			isAppend = True
		# agency_
		elif k.startswith(_flow_agency_prefix) and len(k) > flow_agency_prefix_length:
			isAppend = True
		else:
			isAppend = False

		if isAppend == True:
			dealEntryItem(k, v, vo, form_info, hash_attach_info, hash_deal)

	# cmdで再度ループ
	for k,v in vo.iteritems():
		# cmd_
		if k.startswith(_cmd_prefix) and len(k) > cmd_prefix_length:
			field_key = UcfUtil.subString(k, cmd_prefix_length)
			if not 'field_key' in hash_deal:
				field_value = UcfUtil.getHashStr(vo, field_key)
				dealEntryItem(field_key, field_value, vo, form_info, hash_attach_info, hash_deal)

	# 申請情報の作成
	apply_info = UcfXml.createNode('ApplyInfo')
	# 申請情報の数分だけ処理（まわすのではなく１から順番に処理）
	idx = 1
	while True:
		key = _field_prefix + UcfUtil.nvl(idx)
#		if vo.has_key(key) == False:
		if not key in hash_deal:
			break

		field_id = UcfUtil.nvl(idx)
		field_name = UcfUtil.getHashStr(vo, _dispname_prefix + key)
		field_type = UcfUtil.getHashStr(vo, _field_type_prefix + key)


		# タイプ="FILE" の場合はセットする値を加工
		if field_type == _FIELD_TYPE['FILE']:
			if key in hash_attach_info:
				file_info = hash_attach_info[key]
				field_value = file_info[1]
				url = file_info[0]
			else:
				field_value = ''
				url = ''
		elif field_type == 'LINK':
			field_value = UcfUtil.getHashStr(vo, key)
			url = field_value
		else:
			field_value = UcfUtil.getHashStr(vo, key)
			url = ''

		# 改行を含む情報に対応 2011/01/07
		item = UcfXml.createNode('Item')
		apply_info.append(item)
		item.setAttribute('id', field_id)
		item.setAttribute('name', field_name)
		# item.setAttribute('value', field_value)
		item.setAttribute('value_type', 'INNERTEXT')
		item.setAttribute('ftp', field_type)
		item.setAttribute('url', url)
		item.setInnerText(field_value)

		idx += 1
	root.append(apply_info)


	# 承認フロー情報の作成
	flow_info = UcfXml.createNode('RecogFlowInfo')
	# 最終決裁者のitemノードpositionを保持（有効値.１～）
	last_approval_cnt = 0
	# 承認の数分だけ処理（まわすのではなく１から順番に処理）
	idx = 1
	idx_real = 0
	while True:

		flow_key = _seq_prefix + UcfUtil.nvl(idx)
		# POSTされてこない場合にフローが終了してしまうので下に移動
#		if vo.has_key(flow_key) == False:
#			break

		# オペレータＩＤなどの情報を解析して取り出す
		flow_id, id_type, flow_id_list = analysisFlowIDInfo(vo, flow_key, xmlConfig)

		# 承認タイプ（承認、閲覧、決裁）
		flow_type = UcfUtil.getHashStr(vo, _flow_type_prefix + flow_key)	# RECOG or CIRCULATE or APPROVAL

		# ↑の承認者IDではなくフロータイプでの判定に変更
		if flow_type == '':
			break

		# 代理承認（代理承認指定があるなら）
		agency_flow_id = ''
		agency_id_type = ''
		agency_flow_id_list = []
		if _flow_agency_prefix + flow_key in vo:
			agency_flow_id, agency_id_type, agency_flow_id_list = analysisFlowIDInfo(vo, _flow_agency_prefix + flow_key, xmlConfig)

		# 承認者、代理承認者のどちらかが指定されている場合のみ有効とする 2011/01/06
		if flow_id != '' or agency_flow_id != '':
			idx_real += 1

			item = UcfXml.createNode('Item')
			flow_info.append(item)
			item.setAttribute('flow_id', flow_id)
			item.setAttribute('id_type', id_type)
			item.setAttribute('flow_type', flow_type)
			item.setAttribute('agency_flow_id', agency_flow_id)
			item.setAttribute('agency_id_type', agency_id_type)
			item.setAttribute('last_approval_flag', '')	# 最終決裁者Ｆ（あとでセット）

			# 最終決裁者itemノードpositionを更新
			if flow_type == 'APPROVAL':
	#			last_approval_cnt = idx
				last_approval_cnt = idx_real

			# 最初の承認オペレータＩＤと代理承認オペレータＩＤをセット
	#		if idx == 1:
			if idx_real == 1:
				first_flow_id_list = flow_id_list
				first_agency_flow_id_list = agency_flow_id_list
				first_flow_type = flow_type

		idx += 1

	# 最終決裁者Ｆを更新
	items = flow_info.selectNodes('Item')
	idx = 1
	for item in items:
		if idx == last_approval_cnt:
			item.setAttribute('last_approval_flag', 'LAST')
			break
		idx += 1

	root.append(flow_info)

	mdlData.entry_detail = root.outerXml()

	###############################################

	# 承認履歴（リスト）（申請者をここにセット）
	mdlData.recognition_history = [UcfUtil.nvl(helper.getLoginOperatorID()) + '/' + getActionType('APPLY')]
	# 承認履歴コメント（リスト）（申請者用１つ追加）
	comment = ''
#	now = UcfUtil.nvl(UcfUtil.getNow())
#	now = UcfUtil.getNow().strftime('%Y-%m-%d %H:%M:%S')
	now = UcfUtil.getLocalTime(UcfUtil.getNow()).strftime('%Y-%m-%d %H:%M:%S')
	mdlData.recognition_history_comment = [UcfUtil.nvl(helper.getLoginOperatorID()) + '/' + now + '/' + comment]
	# 最終承認者ＩＤ（空）
	mdlData.last_recognition_name = ''
	# 次回承認者ＩＤ（リスト）.最初のオペレータＩＤをセット（複数いる場合は複数セット）
	
	mdlData.next_recognition_name = first_flow_id_list
	# 次回承認タイプ.（RECOG or CIRCULATE or APPROVAL）
	mdlData.next_recognition_type = first_flow_type
	# 代理承認者ＩＤ（リスト）.最初の代理オペレータＩＤをセット（複数いる場合は複数セット）
	mdlData.agency_recognition_name = first_agency_flow_id_list
	# 次回承認期限. 設定マスタから取得した日数を足した日時をセット
	nodRecogLimitTerm = xmlConfig.selectSingleNode('Config/RecogLimitTerm')
	if nodRecogLimitTerm != None and nodRecogLimitTerm.getInnerText() != '':
		recog_limit_term = int(nodRecogLimitTerm.getInnerText())
	else:
		recog_limit_term = 0
	mdlData.next_recognition_limit = UcfUtil.add_days(UcfUtil.getNow(), recog_limit_term)
	# 最終承認日時.（空というか）
	mdlData.last_recognition_date = None
	mdlData.ref_master = mdlMaster

	mdlData.creator_name = UcfUtil.nvl(helper.getLoginOperatorID())
	mdlData.updater_name = UcfUtil.nvl(helper.getLoginOperatorID())
	mdlData.date_created = UcfUtil.getNow()
	mdlData.date_changed = UcfUtil.getNow()
	mdlData.del_flag = ''

	# 更新処理
	mdlData.put()

	# 初回申請者にメール送信
	nodNotificationMail = xmlConfig.selectSingleNode('NotificationMail')

	if nodNotificationMail != None:
		mail_info = nodNotificationMail.exchangeToHash(isAttr=True, isChild=True)
#		to = UcfUtil.getHashStr(mail_info, 'To')
		sender   = UcfUtil.getHashStr(mail_info, 'From')
		subject  = UcfUtil.getHashStr(mail_info, 'Subject')
		body     = UcfUtil.getHashStr(mail_info, 'Body')
		body_html= UcfUtil.getHashStr(mail_info, 'BodyHtml')
		reply_to = UcfUtil.getHashStr(mail_info, 'ReplyTo')
		cc       = UcfUtil.getHashStr(mail_info, 'Cc')
		bcc      = UcfUtil.getHashStr(mail_info, 'Bcc')

		for first_flow_id in first_flow_id_list:
			
			try:
				to = ''
				# 追加 Operatorテーブル未使用時処理追加
				domain = UcfUtil.getMailDomain(helper.getLoginOperatorMailAddress())
				# オペレｰタＩＤからオペレータ情報を取得しメールアドレスをToにセット
				mdlOperator = getValidOperator(helper, first_flow_id)
				if mdlOperator != None:
					voOperator = mdlOperator.exchangeVo()
					to = UcfUtil.getHashStr(voOperator, 'mail_address')
				# 追加 オペレータ情報が取得できず、ドメインが取得できたとき、IDからアドレス作成
				elif domain:
					to = first_flow_id + '@' + domain
				# メールアドレスが取得できればメール送信
				if to != '':
					UcfMailUtil.sendOneMail(to=to, cc=cc, bcc=bcc, reply_to=reply_to, sender=sender, subject=subject, body=body, body_html=body_html)

			#ログだけ、エラーにしない
			except Exception, e:
				helper.outputErrorLog(e)

def dealEntryItem(k, v, vo, form_info, hash_attach_info, hash_deal):
	u''' 申請登録：１アイテムに関して処理 '''
	check_key = k
	cmd = UcfUtil.getHashStr(vo, _cmd_prefix + check_key)
	check_name = UcfUtil.getHashStr(vo, _dispname_prefix + check_key)
	field_type = UcfUtil.getHashStr(vo, _field_type_prefix + check_key)

	# タイプ="FILE" の場合はセットする値を加工
	if field_type == _FIELD_TYPE['FILE']:
		if check_key in hash_attach_info:
			file_info = hash_attach_info[check_key]
			check_value = file_info[1]
			url = file_info[0]
		else:
			check_value = ''
			url = ''
	elif field_type == 'LINK':
		check_value = v
		url = check_value
	else:
		check_value = v
		url = ''
	
	item = UcfXml.createNode('Item')
	form_info.append(item)
	item.setAttribute('id', check_key)
	item.setAttribute('name', check_name)
	item.setAttribute('cmd', cmd)
	item.setAttribute('value', check_value)
	item.setAttribute('ftp', field_type)
	item.setAttribute('url', url)

	hash_deal[k] = ''


def editFileDataVo(helper, mdlMaster, vo):
	u''' ファイルデータ項目の値を加工 '''
	# マスタから設定XMLをロードしておく（TODO 文字コード変換を何とかしたい）
	# xmlConfig = UcfXml.loadXml(unicode(mdlMaster.workflow_config).encode('utf-8'))
	xmlConfig = UcfXml.loadXml(mdlMaster.workflow_config)
	


def analysisFlowIDInfo(vo, flow_key, xmlConfig):
	u''' オペレータＩＤなどの情報を解析して取り出す '''

	flow_group_prefix_length = len(_flow_group_prefix)

	# 承認者ＩＤ(オペレータＩＤあるいはグループＩＤ)
	flow_id = ''	# オペレータID or グループID
	id_type = ''	# OPERATOR or GROUP
	temp = UcfUtil.getHashStr(vo, flow_key)
	# グループＩＤの場合
	if temp.startswith(_flow_group_prefix) and len(temp) > flow_group_prefix_length:
		flow_id = UcfUtil.subString(temp, flow_group_prefix_length)
		id_type = 'GROUP'

	# オペレータＩＤの場合
	elif temp != '':
		flow_id = temp
		id_type = 'OPERATOR'

	if flow_id != '':
		flow_id_list = getWorkFlowOperatorIDList(vo, flow_id, id_type, xmlConfig)
	else:
		flow_id_list = []

	return flow_id, id_type, flow_id_list


def uploadAttachmentFilesToGoogleSites(helper, vo, xmlConfig):
	u''' 添付ファイルの処理（GoogleSitesにHTTPアップロード）'''

	INFO_XPATH = 'Config/FileAttachmentSitesInfo'
	nodAttachmentSitesInfo = xmlConfig.selectSingleNode(INFO_XPATH)

	# nodAttachmentSitesInfoのイメージ
	u'''
	<!-- 申請書添付ファイルのアップロード先情報 -->
	<FileAttachmentSitesInfo>
		<!-- 対象サイツのドメイン（指定無しならAppsではなくGoogleアカウントのSitesとなる） -->
		<Domain>satelaito.jp</Domain>
		<!-- 対象のサイト名（指定無しならAppsではなくGoogleアカウントのSitesとなる） -->
		<SiteName>gbtdemo</SiteName>
		<!-- サイト内の対象ページのパス（サイト名の下から指定.「/」ではじめること） -->
		<PagePath>/Home/workflow_files</PagePath>
		<!-- サブフォルダ名※アップロードページがファイルキャビネットページの場合のみ有効 -->
		<FolderName>休暇申請用</FolderName>
		<!-- サイツページにアクセスするアカウント情報 -->
		<!-- アカウント（※UcfSSOManager.exe or UcfTools.exe にて暗号化） -->
		<Account>xxxxxxxxxxxxxxxxxx</Account>
		<!-- パスワード（※UcfSSOManager.exe or UcfTools.exe にて暗号化） -->
		<Password>xxxxxx</Password>
	</FileAttachmentSitesInfo>
	'''

	# 結果 KEY:フィールド名（例･･･「FLD001」）VALUE:[アップロード先のＵＲＬ, ファイル名]
	hash_result = {}

	# FILE数分だけ処理
	pagepath = None
	client = None
	page_entry = None

	int_no = 0	# 連番用

	field_type_prefix_length = len(_field_type_prefix)
	for k,v in vo.iteritems():
		if k.startswith(_field_type_prefix) and len(k) > field_type_prefix_length and v == _FIELD_TYPE['FILE']:
			field_name = UcfUtil.subString(k, field_type_prefix_length)
			file_bytes_data = helper.request.get(field_name)

			# HTTPアップロードされたファイルの各種情報を取得（ベタ過ぎだがとりあえず）
			original_file_name = ''
			content_type = ''
			binary = helper.request.body_file.vars[field_name]
			if binary != None and not isinstance(binary, str):
				original_file_name = unicode(binary.filename, UcfConfig.ENCODING, 'ignore')
				content_type =  UcfUtil.nvl(binary.headers['content-type']).encode('utf-8')
	
			if file_bytes_data != None and original_file_name != '':
				if client == None:
					if nodAttachmentSitesInfo == None:
						raise Exception, ['failed get master info node.', str(INFO_XPATH)]

					# 各パラメータを設定ファイルかワークフローマスタから取得
					appname = 'Satelaito WorkFlow System' #TODO 
					node = nodAttachmentSitesInfo.selectSingleNode('PagePath')
					path = node.getInnerText() if node else ''
					node = nodAttachmentSitesInfo.selectSingleNode('Domain')
					domainname = node.getInnerText() if node else ''
					node = nodAttachmentSitesInfo.selectSingleNode('SiteName')
					sitename = node.getInnerText() if node else ''
					node = nodAttachmentSitesInfo.selectSingleNode('Account')
					account = node.getInnerText() if node else ''
					if account != '':
						account = UcfUtil.deCrypto(account, UcfConfig.CRYPTO_KEY)
					node = nodAttachmentSitesInfo.selectSingleNode('Password')
					password = node.getInnerText() if node else ''
					if password != '':
						password = UcfUtil.deCrypto(password, UcfConfig.CRYPTO_KEY)
					node = nodAttachmentSitesInfo.selectSingleNode('FolderName')
					folder_name = node.getInnerText() if node else ''
					node = nodAttachmentSitesInfo.selectSingleNode('FileNameType')
#					file_name_type = node.getInnerText() if node else 'TYPE1'

					client = SitesUtil.getSitesClient(appname, domainname, account, password, sitename)
					feed = SitesUtil.getContentFeedByPath(client, path=path)
					for entry in feed.entry:
						page_entry = entry
						pagepath = path
						break

					if page_entry == None:
						raise Exception, ['failed get file upload sites page entry.', str(sitename), str(path)]

				int_no += 1

				# ファイルタイトルを決定
				title = ''
				description=''
#				# TYPE1:オペレータＩＤ+日付+元のファイル名（デフォルト）
#				if file_name_type == 'TYPE1':
				datNow = UcfUtil.getLocalTime(UcfUtil.getNow())
				title += helper.getLoginOperatorID() + '_'
				title += datNow.strftime('%Y') + datNow.strftime('%m') + datNow.strftime('%d') + datNow.strftime('%H') + datNow.strftime('%M') + datNow.strftime('%S') + '_'
#					title += original_file_name
				title += UcfUtil.nvl(int_no)				# TODO 添付ファイルの場合、「sites:pageName」が指定でできなっぽい＆SitesUtil.uploadAttachmentFileから結果Entryが取得できないため
				# titleから自動でページ名を作成させるしかない.すなわち推測できるページ名にすることが必要！！

				# ファイル説明（※かわりに説明に名称などをセット）
				description = 'ID;' + helper.getLoginOperatorID() + '\r\n' + 'DATE:' + UcfUtil.nvl(datNow) + '\r\n' + 'FILE;' + original_file_name + '\r\n'

				# ファイルアップロード
				pagename = title	# TODO 添付ファイルでもこれが指定できればいいのに！！なぜだ！
				SitesUtil.uploadAttachmentFile(client, file_bytes_data, page_entry, content_type=content_type, title=title, description=description, folder_name=folder_name)
				logging.info(title)
#				helper.response.out.write(client.getContentAccessURL(pagepath, pagename))
				hash_result[field_name] = [client.getContentAccessURL(pagepath, pagename), original_file_name]

	return hash_result

def getWorkFlowOperatorIDList(vo, flow_id, id_type, xmlConfig):
	u''' オペレータＩＤ一覧を解析して取り出す '''

	flow_id_list = []

	if flow_id != '':
		# グループＩＤの場合
		if id_type == 'GROUP':
			# グループからオペレータ一覧を取得（設定マスタのXML定義より）
			# 指定グループＩＤのItemノードを検索（条件式が使えないので1件ずつループして調べる..）
			lstItem = xmlConfig.selectNodes('RecogFlowList' + '/' + 'Item')

			for item in lstItem:
				item_id = item.getAttribute('id')
				if item_id == flow_id:
					lstOperator = item.selectNodes('Operator')
					for ope in lstOperator:
						operator_id = ope.getAttribute('id')
						if operator_id != '':
							flow_id_list.append(operator_id)
					break

		# オペレータＩＤの場合
		else:
			flow_id_list = UcfUtil.csvToList(flow_id.replace(' ', ''))

	return flow_id_list


def getSelfActionWaiteCount(helper, flow_type_list, agency=False):
	u''' 自分宛の承認や閲覧待ち件数を取得 '''

	gql = ""

	# WHERE句
	wheres = []

	# 店舗ＩＤ
	# スーパーバイザじゃない場合は自分の店舗のみ（※実際にはここは通らない前提.index数制限により）
	if not helper.isSuperVisor():
		sk_dept_id = helper.getLoginDeptID()
		wheres.append("dept_id = '" + UcfUtil.escapeGql(sk_dept_id) + "'")

	# 削除Ｆ
	wheres.append("del_flag=''")

	# 処理済、申請取り消しの場合は、next_recognition_nameと4を空にするのでstatus条件は不要
#	# ステータスが未処理 or 処理中 or 否認/差し戻しのもののみ対象（処理済、申請取消以外という意味だがnot検索ができないため）
#	sk_status = []
#	sk_status.append('')
#	sk_status.append('PROCESSING')
#	sk_status.append('DENIED')
#	in_query = UcfUtil.listToGqlInQuery(sk_status)
#	wheres.append("status in (" + in_query + ")")

	# 自分あての閲覧、承認待ち（flow_type_listに基づく）のものを取得
	if agency == False:
		sk_next_recognition_name = []
		sk_next_recognition_name.append(helper.getLoginOperatorID())
		in_query = UcfUtil.listToGqlInQuery(sk_next_recognition_name)
		wheres.append("next_recognition_name in (" + in_query + ")")
	else:
		sk_agency_recognition_name = []
		sk_agency_recognition_name.append(helper.getLoginOperatorID())
		in_query = UcfUtil.listToGqlInQuery(sk_agency_recognition_name)
		wheres.append("agency_recognition_name in (" + in_query + ")")

	sk_next_recognition_type = flow_type_list
	in_query = UcfUtil.listToGqlInQuery(sk_next_recognition_type)
	wheres.append("next_recognition_type in (" + in_query + ")")

	gql += UcfUtil.getToGqlWhereQuery(wheres)

	models = UCFMDLWorkFlow.gql(gql)
	return models.count()


def getApplyDetailList(helper, voWorkFlow, encode=None):
	u''' 申請情報XMLから申請内容を取得 '''
	ucfp = UcfManageParameter(helper)

	index = 0
	entry_detail = UcfUtil.getHashStr(voWorkFlow, 'entry_detail')
	if entry_detail != '':
		if encode:
			# 2011/06/08 Djangoテンプレート更新に伴い文字コード変換を削除
			# root = UcfXml.loadXml(unicode(entry_detail,encode).encode('utf-8'))
			root = UcfXml.loadXml(entry_detail)
		else:
			# 2011/06/08 Djangoテンプレート更新に伴い文字コード変換を削除
			# root = UcfXml.loadXml(unicode(entry_detail).encode('utf-8'))
			root = UcfXml.loadXml(entry_detail)
		# 申請情報
		items = root.selectNodes('ApplyInfo/Item')
		for item in items:
			vo = item.attributes()
			# 改行を含む値に対応 2011/01/07
			# value_typeが'INNERTEXT'の場合、innerTextの値でvalueを上書き
			if vo.get('value_type','') == 'INNERTEXT':
				vo['value'] = item.getInnerText()
			
			voinfo = helper.createVoInfoForList(index, vo, None)
			ucfp.voinfos.append(voinfo)

			index += 1

	# 一覧用のパラメータ各種をセット
	ucfp.setParameterForList(index, -1, 0, index, 1, None, None, None)
	# 詳細LIKEに2段組なのでTDがちょうど良いかどうかのフラグをセットしておく
	ucfp.data['valid_td_count_flag'] = 1 if index % 2 == 0 else 0

	return ucfp

def getWorkFlowSequenceList(helper, voWorkFlow, xmlConfig, encode=None):
	u''' 申請情報XMLからワークフロー順序情報を取得 '''
	ucfp = UcfManageParameter(helper)

	# グループからグループ名を取得（設定マスタのXML定義より）
	hashGroupName = {}
	lstItem = xmlConfig.selectNodes('RecogFlowList' + '/' + 'Item')

	for item in lstItem:
		item_id = item.getAttribute('id')
		item_name = item.getAttribute('name')
		hashGroupName[item_id] = item_name

	recog_seq_no = int(UcfUtil.getHashStr(voWorkFlow, 'recog_seq_no')) if UcfUtil.getHashStr(voWorkFlow, 'recog_seq_no') != None else 0

	index = 0
	entry_detail = UcfUtil.getHashStr(voWorkFlow, 'entry_detail')
	if entry_detail != '':
		if encode:
			# 2011/06/08 Djangoテンプレート更新に伴い文字コード変換を削除
			# root = UcfXml.loadXml(unicode(entry_detail,encode).encode('utf-8'))
			root = UcfXml.loadXml(entry_detail)
		else:
			# 2011/06/08 Djangoテンプレート更新に伴い文字コード変換を削除
			# root = UcfXml.loadXml(unicode(entry_detail).encode('utf-8'))
			root = UcfXml.loadXml(entry_detail)
		# ワークフロー順序情報
		items = root.selectNodes('RecogFlowInfo/Item')
		for item in items:
			vo = item.attributes()

			# グループなら
			if UcfUtil.getHashStr(vo, 'id_type') == 'GROUP':
				vo['flow_name'] = UcfUtil.getHashStr(hashGroupName, UcfUtil.getHashStr(vo, 'flow_id'))
			# オペレータなら
			else:
				flow_id_list = UcfUtil.csvToList(UcfUtil.getHashStr(vo, 'flow_id').replace(' ', ''))
				flow_name_list = []
				for i in range(len(flow_id_list)):
					flow_id = flow_id_list[i]
					if flow_id != '':
						# オペレータマスタからオペレータ情報を取得しオペレータ名などをセット
						voOperator = getValidOperator(helper, flow_id)
						if voOperator != None:
							flow_name_list.append(voOperator.operator_name)
						else:
							flow_name_list.append(flow_id)
				vo['flow_name'] = UcfUtil.listToCsv(flow_name_list)

			# 現在の承認フローＳＥＱから、済かどうかを判定
			if int(recog_seq_no) > index:
				vo['deal_flag'] = 'DEAL'
			else:
				vo['deal_flag'] = ''
			# 現在の承認フローＳＥＱから、済かどうかを判定（自分も含める）
			if int(recog_seq_no) >= index:
				vo['deal_flag2'] = 'DEAL'
			else:
				vo['deal_flag2'] = ''

			voinfo = helper.createVoInfoForList(index, vo, WorkFlowSequenceViewHelper())
			ucfp.voinfos.append(voinfo)

			index += 1

	# 一覧用のパラメータ各種をセット
	ucfp.setParameterForList(index, -1, 0, index, 1, None, None, None)
	return ucfp


def getWorkFlowHistoryList(helper, voWorkFlow):
	u''' ワークフロー履歴一覧を取得 '''
	ucfp = UcfManageParameter(helper)

	recognition_history_list = UcfUtil.csvToList(UcfUtil.getHashStr(voWorkFlow, 'recognition_history'))
	recognition_history_comment_list = UcfUtil.csvToList(UcfUtil.getHashStr(voWorkFlow, 'recognition_history_comment'))

	index = 0
	for idx in range(len(recognition_history_list)):
		recognition_history = recognition_history_list[idx]
		recognition_history_comment = recognition_history_comment_list[idx]

		vo = {}
	
		split_history = recognition_history.split('/')
		split_history_comment = recognition_history_comment.split('/')
		vo['operator_id'] = split_history[0]
		vo['action_type'] = split_history[1]
		vo['action_date'] = split_history_comment[1]
		vo['comment'] = split_history_comment[2]

		# オペレータマスタからオペレータ情報を取得しオペレータ名などをセット
		voOperator = getValidOperator(helper, UcfUtil.getHashStr(vo, 'operator_id'))
		if voOperator != None:
			vo['operator_name'] = voOperator.operator_name
		else:
			vo['operator_name'] = vo['operator_id']
			
		voinfo = helper.createVoInfoForList(index, vo, WorkFlowHistoryViewHelper())
		ucfp.voinfos.append(voinfo)

		index += 1

	# 一覧用のパラメータ各種をセット
	ucfp.setParameterForList(index, -1, 0, index, 1, None, None, None)

	return ucfp


def getSubAuthority(helper, vo):
	u''' 機能別権限情報を作成 '''
	sub_authority = {}

	if helper._page_type == 'g':
		# 承認タイプチェック
		status = UcfUtil.getHashStr(vo, 'status')
		approval_status = UcfUtil.getHashStr(vo, 'approval_status')
		apply_operator_id = UcfUtil.getHashStr(vo, 'apply_operator_id')
		next_recognition_name_list = UcfUtil.csvToList(UcfUtil.getHashStr(vo, 'next_recognition_name'))
		agency_recognition_name_list = UcfUtil.csvToList(UcfUtil.getHashStr(vo, 'agency_recognition_name'))
		next_recognition_type = UcfUtil.getHashStr(vo, 'next_recognition_type')
		operator_id = UcfUtil.nvl(helper.getLoginOperatorID())

		valid_count = 0
		# 申請取消する（処理が終わっていないかつ決裁済ではなく自分の申請なら）
		if (status != 'PROCESSED' and status != 'CANCELED') and approval_status != 'APPROVED' and apply_operator_id == helper.getLoginOperatorID():
			sub_authority['CANCEL'] = 'ON'
			valid_count += 1
		else:
			sub_authority['CANCEL'] = ''
		# 閲覧する
		if (status != 'PROCESSED' and status != 'CANCELED') and next_recognition_type == 'CIRCULATE' and operator_id in next_recognition_name_list:
			sub_authority['CIRCULATE'] = 'ON'
			valid_count += 1
		else:
			sub_authority['CIRCULATE'] = ''
		# 代理閲覧する
		if (status != 'PROCESSED' and status != 'CANCELED') and next_recognition_type == 'CIRCULATE' and operator_id in agency_recognition_name_list:
			sub_authority['AGENCY_CIRCULATE'] = 'ON'
			valid_count += 1
		else:
			sub_authority['AGENCY_CIRCULATE'] = ''
		# 承認する
		if (status != 'PROCESSED' and status != 'CANCELED') and next_recognition_type == 'RECOG' and operator_id in next_recognition_name_list:
			sub_authority['RECOG'] = 'ON'
			valid_count += 1
		else:
			sub_authority['RECOG'] = ''
		# 代理承認する（通常の承認対象者の場合は対象としない）
		if (status != 'PROCESSED' and status != 'CANCELED') and next_recognition_type == 'RECOG' and (not operator_id in next_recognition_name_list and operator_id in agency_recognition_name_list):
			sub_authority['AGENCY_RECOG'] = 'ON'
			valid_count += 1
		else:
			sub_authority['AGENCY_RECOG'] = ''
		# 決裁する
		if (status != 'PROCESSED' and status != 'CANCELED') and next_recognition_type == 'APPROVAL' and operator_id in next_recognition_name_list:
			sub_authority['APPROVAL'] = 'ON'
			valid_count += 1
		else:
			sub_authority['APPROVAL'] = ''
		# 代理決裁する（通常の決裁対象者の場合は対象としない）
		if (status != 'PROCESSED' and status != 'CANCELED') and next_recognition_type == 'APPROVAL' and (not operator_id in next_recognition_name_list and operator_id in agency_recognition_name_list):
			sub_authority['AGENCY_APPROVAL'] = 'ON'
			valid_count += 1
		else:
			sub_authority['AGENCY_APPROVAL'] = ''
		# 否認/差戻する
		if (status != 'PROCESSED' and status != 'CANCELED') and (next_recognition_type == 'APPROVAL' or next_recognition_type == 'RECOG') and operator_id in next_recognition_name_list:
			sub_authority['DENY'] = 'ON'
			valid_count += 1
		else:
			sub_authority['DENY'] = ''
		# 代理否認/差戻する（通常の否認対象者の場合は対象としない）
		if (status != 'PROCESSED' and status != 'CANCELED') and (next_recognition_type == 'APPROVAL' or next_recognition_type == 'RECOG') and (not operator_id in next_recognition_name_list and operator_id in agency_recognition_name_list):
			sub_authority['AGENCY_DENY'] = 'ON'
			valid_count += 1
		else:
			sub_authority['AGENCY_DENY'] = ''
		# 否認/差戻あるいは代理否認/差戻が有効の場合にセット(差し戻し選択ボックス用)
		if sub_authority['DENY'] == 'ON' or sub_authority['AGENCY_DENY'] == 'ON':
			sub_authority['EACH_DENY'] = 'ON'
			valid_count += 1
		else:
			sub_authority['EACH_DENY'] = ''

		# 転送する（TODO 未実装）
		sub_authority['ESCALATION'] = ''

		# いずれかの承認タイプが有効なら立てるフラグ
		if valid_count > 0:
			sub_authority['EXIST_VALID_RECOG'] = 'ON'
		else:
			sub_authority['EXIST_VALID_RECOG'] = ''


	return sub_authority


def getAgencyProcessHistory(helper, voWorkFlow):
	u''' 代理処理された場合の情報を取得してセット(パフォーマンス度外視) '''

	agency_process_history = []

	recognition_history_list = UcfUtil.csvToList(UcfUtil.getHashStr(voWorkFlow, 'recognition_history'))
	recognition_history_comment_list = UcfUtil.csvToList(UcfUtil.getHashStr(voWorkFlow, 'recognition_history_comment'))
	for idx in range(len(recognition_history_list)):
		recognition_history = recognition_history_list[idx]
		recognition_history_comment = recognition_history_comment_list[idx]

		agency_action_type = ''
		# 被代理閲覧されたものなら
		if recognition_history == helper.getLoginOperatorID() + '/' + getActionType('AGENCY_CIRCULATED'):
			agency_action_type = getActionType('AGENCY_CIRCULATED')
		# 被代理承認されたものなら
		elif recognition_history == helper.getLoginOperatorID() + '/' + getActionType('AGENCY_RECOGNIZED'):
			agency_action_type = getActionType('AGENCY_RECOGNIZED')
		# 被代理決裁されたものなら
		elif recognition_history == helper.getLoginOperatorID() + '/' + getActionType('AGENCY_APPROVED'):
			agency_action_type = getActionType('AGENCY_APPROVED')
		# 被代理否認/差戻されたものなら
		elif recognition_history == helper.getLoginOperatorID() + '/' + getActionType('AGENCY_DENIED'):
			agency_action_type = getActionType('AGENCY_DENIED')

		if agency_action_type != '':
			split_history = recognition_history.split('/')
			split_history_comment = recognition_history_comment.split('/')
			agency_process_history.append(agency_action_type + '/' + split_history_comment[2])


	return agency_process_history

def createWorkfrowConfigXml(self,arrWorkfrowConfig):
	u''' ワークフローの設定を配列からXMLに格納する。 '''

	strNodes  = '<Ucf>'
	strNodes += '<Config>'
	strNodes += '<RecogLimitTerm>' + arrWorkfrowConfig['recog_limit_term'] + '</RecogLimitTerm>'
	strNodes += '<FileAttachmentSitesInfo>'
	strNodes += '<Domain>' + arrWorkfrowConfig['file_attachment_domain'] + '</Domain>'
	strNodes += '<SiteName>' + arrWorkfrowConfig['file_attachment_site_name'] + '</SiteName>'
	strNodes += '<PagePath>' + arrWorkfrowConfig['file_attachment_page_path'] + '</PagePath>'
	strNodes += '<FolderName>' + arrWorkfrowConfig['file_attachment_folder_name'] + '</FolderName>'

	# データが見つかった場合暗号化を行う。 2011/06/08 Djangoテンプレート更新に伴い文字コード変換を削除
	# strFileAttachmentAccount = unicode(arrWorkfrowConfig['file_attachment_account']).encode('utf-8')
	strFileAttachmentAccount = arrWorkfrowConfig['file_attachment_account']
	if strFileAttachmentAccount:
		strFileAttachmentAccount = UcfUtil.enCrypto(strFileAttachmentAccount.encode('ASCII'),UcfConfig.CRYPTO_KEY)
	strNodes += '<Account>' + strFileAttachmentAccount + '</Account>'

	strFileAttachmentPassword = ''
	
	if not strFileAttachmentAccount:
		strFileAttachmentPassword = ''
	elif arrWorkfrowConfig['file_attachment_password_new']:
		# 2011/06/08 Djangoテンプレート更新に伴い文字コード変換を削除
		# strFileAttachmentPassword = UcfUtil.enCrypto(unicode(arrWorkfrowConfig['file_attachment_password_new']).encode('utf-8'),UcfConfig.CRYPTO_KEY)
		strFileAttachmentPassword = UcfUtil.enCrypto(arrWorkfrowConfig['file_attachment_password_new'].encode('ASCII'),UcfConfig.CRYPTO_KEY)
	else:
		# 新しいパスワードがなかった場合古いものを使用 2011/06/08 Djangoテンプレート更新に伴い文字コード変換を削除
		# strFileAttachmentPassword = UcfUtil.enCrypto( unicode(self.getSession('OPW')).encode('utf-8'),UcfConfig.CRYPTO_KEY)
		strFileAttachmentPassword = UcfUtil.enCrypto(self.getSession('OPW').encode('ASCII'),UcfConfig.CRYPTO_KEY)
	strNodes += '<Password>' + strFileAttachmentPassword + '</Password>'
	strNodes += '</FileAttachmentSitesInfo>'
	strNodes += '</Config>'
	strNodes += '' + arrWorkfrowConfig['recog_flow_list'] + ''
	strNodes += '<NotificationMail>'
	strNodes += '<From>' + arrWorkfrowConfig['notification_from'] + '</From>'
	strNodes += '<Subject><![CDATA[' + arrWorkfrowConfig['notification_subject'] + ']]></Subject>'
	strNodes += '<Body><![CDATA[' + arrWorkfrowConfig['notification_body'] + ']]></Body>'
	strNodes += '</NotificationMail>'
	strNodes += '<ApprovalNotificationMail>'
	strNodes += '<From>' + arrWorkfrowConfig['approval_notification_from'] + '</From>'
	strNodes += '<Subject><![CDATA[' + arrWorkfrowConfig['approval_notification_subject'] + ']]></Subject>'
	strNodes += '<Body><![CDATA[' + arrWorkfrowConfig['approval_notification_body'] + ']]></Body>'
	strNodes += '</ApprovalNotificationMail>'
	strNodes += '<SendingBackMail>'
	strNodes += '<From>' + arrWorkfrowConfig['sending_backMail_from'] + '</From>'
	strNodes += '<Subject><![CDATA[' + arrWorkfrowConfig['sending_backMail_subject'] + ']]></Subject>'
	strNodes += '<Body><![CDATA[' + arrWorkfrowConfig['sending_backMail_body'] + ']]></Body>'
	strNodes += '</SendingBackMail>'
	strNodes += '</Ucf>'

	return strNodes

def getWorkFrowConfigForXml(self,xmlConfig_Data):
	u''' ワークフローの設定をXMLから配列に格納する。 '''
	#xmlConfig_Data = UcfXml.loadXml(strConfigXml)
	arrWorkfrowConfig = {}
	arrWorkfrowConfig['recog_limit_term'] = getXmlText(xmlConfig_Data,'Config//RecogLimitTerm')
	arrWorkfrowConfig['file_attachment_domain'] = getXmlText(xmlConfig_Data,'Config//Domain')
	arrWorkfrowConfig['file_attachment_site_name'] = getXmlText(xmlConfig_Data,'Config//SiteName')
	arrWorkfrowConfig['file_attachment_page_path'] = getXmlText(xmlConfig_Data,'Config//PagePath')
	arrWorkfrowConfig['file_attachment_folder_name'] = getXmlText(xmlConfig_Data,'Config//FolderName')
	# 2011/06/08 Djangoテンプレート更新に伴い文字コード変換を削除
	# arrWorkfrowConfig['file_attachment_account'] = UcfUtil.deCrypto(getXmlText(xmlConfig_Data,'Config//Account').encode('utf-8'),UcfConfig.CRYPTO_KEY)
	arrWorkfrowConfig['file_attachment_account'] = UcfUtil.deCrypto(getXmlText(xmlConfig_Data,'Config//Account'),UcfConfig.CRYPTO_KEY)
	arrWorkfrowConfig['file_attachment_password_new'] = ''
	strFileAttachmentPassword = u'※未設定です'
	#  2011/06/08 Djangoテンプレート更新に伴い文字コード変換を削除
	# if UcfUtil.deCrypto(getXmlText(xmlConfig_Data,'Config//Password').encode('utf-8'),UcfConfig.CRYPTO_KEY):
	if UcfUtil.deCrypto(getXmlText(xmlConfig_Data,'Config//Password') ,UcfConfig.CRYPTO_KEY):
		strFileAttachmentPassword = u'********'
	arrWorkfrowConfig['file_attachment_password'] = strFileAttachmentPassword
	# 2011/06/08 Djangoテンプレート更新に伴い文字コード変換を削除
	# self.setSession('OPW',UcfUtil.deCrypto(getXmlText(xmlConfig_Data,'Config//Password').encode('utf-8'),UcfConfig.CRYPTO_KEY))
	self.setSession('OPW',UcfUtil.deCrypto(getXmlText(xmlConfig_Data,'Config//Password'),UcfConfig.CRYPTO_KEY))

	# outerXmlを使わない為に手動で分解、再生成
	#strRecogFlowList = ''
	#xmlNode = xmlConfig_Data.selectSingleNode('RecogFlowList')
	#for nodItem in xmlNode.selectNodes('Item'):
	#	strRecogFlowList += '<Item id=\"' + nodItem.getAttribute('id') + '\" name=\"' + nodItem.getAttribute('name') + '\">\n'
	#	for nodOperator in nodItem.selectNodes('Operator'):
	#		strRecogFlowList += '<Operator id=\"' + nodOperator.getAttribute('id') + '\" />\n'
	#	strRecogFlowList += '</Item>\n'
	#arrWorkfrowConfig['recog_flow_list'] = strRecogFlowList
	#arrWorkfrowConfig['recog_flow_list'] = unicode(ElementTree.tostring(xmlNode._element,'utf-8'),'utf-8', 'ignore')
	arrWorkfrowConfig['recog_flow_list'] = getXmlText(xmlConfig_Data,'RecogFlowList','true')

	arrWorkfrowConfig['notification_from'] = getXmlText(xmlConfig_Data,'NotificationMail//From')
	arrWorkfrowConfig['notification_subject'] = getXmlText(xmlConfig_Data,'NotificationMail//Subject')
	arrWorkfrowConfig['notification_body'] = getXmlText(xmlConfig_Data ,'NotificationMail//Body')
	arrWorkfrowConfig['approval_notification_from'] = getXmlText(xmlConfig_Data ,'ApprovalNotificationMail//From')
	arrWorkfrowConfig['approval_notification_subject'] = getXmlText(xmlConfig_Data ,'ApprovalNotificationMail//Subject')
	arrWorkfrowConfig['approval_notification_body'] = getXmlText(xmlConfig_Data ,'ApprovalNotificationMail//Body')
	arrWorkfrowConfig['sending_backMail_from'] = getXmlText(xmlConfig_Data ,'SendingBackMail//From')
	arrWorkfrowConfig['sending_backMail_subject'] = getXmlText(xmlConfig_Data ,'SendingBackMail//Subject')
	arrWorkfrowConfig['sending_backMail_body'] = getXmlText(xmlConfig_Data ,'SendingBackMail//Body')

	return arrWorkfrowConfig

def getWorkFrowConfigForRequest(self):
	u''' ワークフローの設定をリクエストから配列に格納する。 '''
	arrWorkfrowConfig = {}
	arrWorkfrowConfig['recog_limit_term'] = self.getRequest('recog_limit_term')
	arrWorkfrowConfig['file_attachment_domain'] = self.getRequest('file_attachment_domain')
	arrWorkfrowConfig['file_attachment_site_name'] = self.getRequest('file_attachment_site_name')
	arrWorkfrowConfig['file_attachment_page_path'] = self.getRequest('file_attachment_page_path')
	arrWorkfrowConfig['file_attachment_folder_name'] = self.getRequest('file_attachment_folder_name')
	arrWorkfrowConfig['file_attachment_account'] = self.getRequest('file_attachment_account')
	arrWorkfrowConfig['file_attachment_password'] = self.getRequest('file_attachment_password')
	
	arrWorkfrowConfig['file_attachment_password_new'] = self.getRequest('file_attachment_password_new')
	arrWorkfrowConfig['recog_flow_list'] = self.getRequest('recog_flow_list')
	arrWorkfrowConfig['notification_from'] = self.getRequest('notification_from')
	arrWorkfrowConfig['notification_subject'] = self.getRequest('notification_subject')
	arrWorkfrowConfig['notification_body'] = self.getRequest('notification_body')
	arrWorkfrowConfig['approval_notification_from'] = self.getRequest('approval_notification_from')
	arrWorkfrowConfig['approval_notification_subject'] = self.getRequest('approval_notification_subject')
	arrWorkfrowConfig['approval_notification_body'] = self.getRequest('approval_notification_body')
	arrWorkfrowConfig['sending_backMail_from'] = self.getRequest('sending_backMail_from')
	arrWorkfrowConfig['sending_backMail_subject'] = self.getRequest('sending_backMail_subject')
	arrWorkfrowConfig['sending_backMail_body'] = self.getRequest('sending_backMail_body')

	return arrWorkfrowConfig

def getXmlText(xmlNode, strText ,isXML=None):
	u'''指定名称のノード内テキストを取得する。'''
	nodText = xmlNode.selectSingleNode(strText)

	if nodText and isXML:
		try:
			return nodText.outerXml()
		except:
			pass
	if nodText:
		try:
			return nodText.getInnerText()
		except:
			return ''
	else:
		return ''

def setUnicodeForHach(arrTarget):
	u'''ハッシュの内容をShift_JISにエンコードして返却する。'''
	arrData = {}
	for key,value in arrTarget.iteritems():
		try:
			arrData[key] = value.encode(ucfconfig.ENCODING)
		except:
			arrData[key] = value
	return arrData

