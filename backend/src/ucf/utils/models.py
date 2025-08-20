# coding: utf-8

import os,sys,datetime
from google.appengine.ext import db

from ucf.config.ucfconfig import *
from ucf.utils.ucfutil import *

############################################################
## モデルクラス群（モデルごとにファイル分けたほうがいいかな？import面倒？）
############################################################

############################################################
## モデル：親クラス
############################################################
class UCFModel(db.Model):

	def exchangeVo(self):
		u''' db.ModelデータをVoデータ(ハッシュ)に変換 '''
		vo = {}
		for prop in self.properties().values():
			if prop.get_value_for_datastore(self) != None:
				# リスト型
				if prop.name in self.getListTypes():
					vo[prop.name] = unicode(UcfUtil.listToCsv(prop.get_value_for_datastore(self)))
				# 日付型
				elif prop.name in self.getDateTimeTypes():
					vo[prop.name] = unicode(prop.get_value_for_datastore(self))
					# LocalTime対応（標準時刻からローカル時間に戻して表示に適切な形式に変換）
					vo[prop.name] = UcfUtil.nvl(UcfUtil.getLocalTime(UcfUtil.getDateTime(vo[prop.name])))
				else:
					vo[prop.name] = unicode(prop.get_value_for_datastore(self))
			else:
				vo[prop.name] = ''
		return vo

	def margeFromVo(self, vo, helper):
		u''' db.ModelデータにVoデータ(ハッシュ)をマージ '''
		for prop in self.properties().values():
			if prop.name not in ('unique_id', 'date_created', 'date_changed'):
				if prop.name in vo:
					# 数値型
					if prop.name in self.getNumberTypes():
						prop.__set__(self, prop.make_value_from_datastore(int(vo[prop.name])))
					# 日付型
					elif prop.name in self.getDateTimeTypes():
						if UcfUtil.nvl(vo[prop.name]) != '':
#							prop.__set__(self, prop.make_value_from_datastore(UcfUtil.getDateTime(vo[prop.name])))
							prop.__set__(self, prop.make_value_from_datastore(UcfUtil.getUTCTime(UcfUtil.getDateTime(vo[prop.name]))))
						else:
							prop.__set__(self, prop.make_value_from_datastore(None))
					# リスト型
					elif prop.name in self.getListTypes():
						prop.__set__(self, UcfUtil.csvToList(vo[prop.name]))
					# References型
					elif prop.name in self.getReferencesTypes():
						pass
					else:
						prop.__set__(self, prop.make_value_from_datastore(vo[prop.name]))


	def getReferenceData(self):
		u''' 参照データの情報をUcfDataリストとして返す（抽象メソッド） '''
		#TODO 自動判別したい
		return ()


	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return ()
	getNumberTypes = staticmethod(getNumberTypes)

	def getListTypes():
		u''' リスト型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return ()
	getListTypes = staticmethod(getListTypes)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return ()
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getReferencesTypes():
		u''' 参照型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return ()
	getReferencesTypes = staticmethod(getReferencesTypes)


############################################################
## モデル：ログ
############################################################
class UCFMDLProcessLog(UCFModel):
	u'''ログテーブルをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()

	log_type = db.StringProperty()
	log_text = db.TextProperty()
	http_status = db.TextProperty()
	customer_id = db.StringProperty()
	operator_id = db.StringProperty()
	page_id = db.StringProperty()
	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)


############################################################
## モデル：オペレータマスタ
############################################################
class UCFMDLOperator(UCFModel):
	u'''オペレータマスタをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	user_id = db.StringProperty()
	operator_id = db.StringProperty()
	operator_name = db.StringProperty()
	password = db.StringProperty()
	mail_address = db.StringProperty()
	access_authority = db.StringProperty()
	last_name = db.StringProperty()
	first_name = db.StringProperty()
	parent_groups = db.StringListProperty()
	attribute1 = db.StringProperty()
	attribute2 = db.StringProperty()
	attribute3 = db.StringProperty()
	attribute4 = db.StringProperty()
	attribute5 = db.StringProperty()
	attribute6 = db.StringProperty()
	attribute7 = db.StringProperty()
	attribute8 = db.StringProperty()
	attribute9 = db.StringProperty()
	attribute10 = db.StringProperty()
	attribute11 = db.StringProperty()
	attribute12 = db.StringProperty()
	attribute13 = db.StringProperty()
	attribute14 = db.StringProperty()
	attribute15 = db.StringProperty()
	attribute16 = db.StringProperty()
	attribute17 = db.StringProperty()
	attribute18 = db.StringProperty()
	attribute19 = db.StringProperty()
	attribute20 = db.StringProperty()
	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)


############################################################
## モデル：ABテスト設定マスタ
############################################################
class UCFMDLABTestMaster(UCFModel):
	u'''ＡＢテスト設定マスタをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	master_id = db.StringProperty()
	title = db.StringProperty()
	target_filter = db.TextProperty()
	script_text = db.TextProperty()
	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)


############################################################
## モデル：ABテスト集計テーブル
############################################################
class UCFMDLABTestCount(UCFModel):
	u'''ＡＢテストカウントアップテーブルをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	master_id = db.StringProperty()
	access_count = db.IntegerProperty(default=0)
	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す'''
		return ('access_count')
	getNumberTypes = staticmethod(getNumberTypes)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)


############################################################
## モデル：ワークフロー設定マスタ
############################################################
class UCFMDLWorkFlowMaster(UCFModel):
	u'''ワークフロー設定マスタをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	master_id = db.StringProperty()
	title = db.StringProperty()
	workflow_config = db.TextProperty()

	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)



############################################################
## モデル：ワークフローテーブル
############################################################
class UCFMDLWorkFlow(UCFModel):
	u'''ワークフローテーブルをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	master_id = db.StringProperty()

	template_id = db.StringProperty()
	apply_id = db.StringProperty()
	apply_operator_id = db.StringProperty()
	apply_date = db.DateTimeProperty(auto_now_add=True)
	input_template_id = db.TextProperty()
	confirm_template_id = db.TextProperty()
	thanks_template_id = db.TextProperty()
	status = db.StringProperty()
	approval_status = db.StringProperty()
	recog_seq_no = db.IntegerProperty()
	entry_detail = db.TextProperty()
	recognition_history = db.StringListProperty()
	recognition_history_comment = db.StringListProperty()
	last_recognition_name = db.StringProperty()
#	next_recognition_name = db.StringProperty()
	next_recognition_name = db.StringListProperty()
#	agency_recognition_name = db.StringProperty()
	next_recognition_type = db.StringProperty()
	agency_recognition_name = db.StringListProperty()
#	next_recognition_limit = db.StringProperty()
	next_recognition_limit = db.DateTimeProperty(auto_now_add=True)
#	last_recognition_date = db.StringProperty()
	last_recognition_date = db.DateTimeProperty()

	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	# back-referencesは行わない 2009/03/12 T.ASAO
#	ref_master = db.ReferenceProperty(UCFMDLWorkFlowMaster, collection_name='workflows')
	ref_master = db.ReferenceProperty(UCFMDLWorkFlowMaster)

	def getReferenceData(self):
		u''' 参照データの情報をUcfDataリストとして返す '''
		list = []
		# ワークフローマスタ
		if self.ref_master != None:
			list.append(UcfData('ref_master_title', self.ref_master.title))
			pass
		return list

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す '''
		return ('recog_seq_no')
	getNumberTypes = staticmethod(getNumberTypes)

	def getListTypes():
		u''' リスト型フィールドがあればここでフィールド名のリストを返す '''
		return ('recognition_history', 'recognition_history_comment', 'next_recognition_name', 'agency_recognition_name')
	getListTypes = staticmethod(getListTypes)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed', 'apply_date', 'next_recognition_limit', 'last_recognition_date')
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getReferencesTypes():
		u''' 参照型フィールドがあればここでフィールド名のリストを返す '''
		return ('ref_master')
	getReferencesTypes = staticmethod(getReferencesTypes)


############################################################
## モデル：会員マスタ
############################################################
class UCFMDLCustomer(UCFModel):
	u'''会員マスタをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	mail_address = db.StringProperty()
	password = db.StringProperty()
	name = db.StringProperty()
	name_kana = db.StringProperty()
	zip = db.StringProperty()
	address_ken = db.StringProperty()
	address2 = db.StringProperty()
	address3 = db.StringProperty()
	address4 = db.StringProperty()
	tel_no = db.StringProperty()
	fax_no = db.StringProperty()
	mobile_no = db.StringProperty()
	company_name = db.StringProperty()
	company_busho = db.StringProperty()
	company_post = db.StringProperty()
	member_type = db.StringProperty()
	point_use_stop_flag = db.StringProperty()
	group_id = db.StringListProperty(str)
	entry_date = db.StringProperty()
	exit_date = db.StringProperty()
	exit_reason = db.TextProperty()
	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getListTypes():
		u''' リスト型フィールドがあればここでフィールド名のリストを返す '''
		return ('group_id')
	getListTypes = staticmethod(getListTypes)

############################################################
## モデル：採番マスタ
############################################################
class UCFMDLNumber(UCFModel):
	u'''採番マスタをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	number_id = db.StringProperty()
	number_sub_id = db.StringProperty()
	prefix = db.StringProperty()
	sequence_no = db.IntegerProperty()
	sequence_no_digit = db.IntegerProperty()

	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()


	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す '''
		return ('sequence_no', 'sequence_digit')
	getNumberTypes = staticmethod(getNumberTypes)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)

############################################################
## モデル：MP_店舗
############################################################
class UCFMDLDeptMaster(UCFModel):
	u'''MP_店舗をイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	google_apps_domain = db.StringProperty()
	title = db.StringProperty()
	active_flag = db.StringProperty()
	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)

############################################################
## モデル：MP_拡張フォームカテゴリ(現在未使用)
############################################################
class UCFMDLExtFormCategory(UCFModel):
	u'''MP_拡張フォームカテゴリをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	title = db.StringProperty()
	enq_id = db.StringProperty()
	category_id = db.StringProperty()
	category_name = db.StringProperty()
	parent_category_id = db.StringProperty()
	active_flag = db.StringProperty()
	
	access_control_id = db.StringProperty()
	access_control_id_manage = db.StringProperty()

	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)

############################################################
## モデル：MP_拡張フォーム管理
############################################################
class UCFMDLExtFormMaster(UCFModel):
	u'''MP_拡張フォーム管理をイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	enq_id = db.StringProperty()
	title = db.StringProperty()
	category_id = db.StringProperty()
	category_name = db.StringProperty()
	active_flag = db.StringProperty()
	active_term_from = db.DateTimeProperty()
	active_term_to = db.DateTimeProperty()
	access_control_id = db.StringProperty()
	access_control_id_manage = db.StringProperty()
	enq_config = db.TextProperty()

	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('active_term_from', 'active_term_to', 'date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)

############################################################
## モデル：MP_拡張フォームテンプレート
############################################################
class UCFMDLExtFormTemplate(UCFModel):
	u'''MP_拡張フォームテンプレートをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	template_id = db.StringProperty()
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	title = db.StringProperty()
	template_html = db.TextProperty()

	# JSON形式の属性を設定 2012/03/21
	template_params = db.TextProperty()
	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)

############################################################
## モデル：MP_属性マスタ
############################################################
class UCFMDLAttributeDefine(UCFModel):
	u'''MP_属性マスタをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	dept_id = db.StringProperty()
	data_type = db.StringProperty()
	attribute_title1 = db.StringProperty()
	attribute_info1 = db.TextProperty()
	attribute_title2 = db.StringProperty()
	attribute_info2 = db.TextProperty()
	attribute_title3 = db.StringProperty()
	attribute_info3 = db.TextProperty()
	attribute_title4 = db.StringProperty()
	attribute_info4 = db.TextProperty()
	attribute_title5 = db.StringProperty()
	attribute_info5 = db.TextProperty()
	attribute_title6 = db.StringProperty()
	attribute_info6 = db.TextProperty()
	attribute_title7 = db.StringProperty()
	attribute_info7 = db.TextProperty()
	attribute_title8 = db.StringProperty()
	attribute_info8 = db.TextProperty()
	attribute_title9 = db.StringProperty()
	attribute_info9 = db.TextProperty()
	attribute_title10 = db.StringProperty()
	attribute_info10 = db.TextProperty()
	attribute_title11 = db.StringProperty()
	attribute_info11 = db.TextProperty()
	attribute_title12 = db.StringProperty()
	attribute_info12 = db.TextProperty()
	attribute_title13 = db.StringProperty()
	attribute_info13 = db.TextProperty()
	attribute_title14 = db.StringProperty()
	attribute_info14 = db.TextProperty()
	attribute_title15 = db.StringProperty()
	attribute_info15 = db.TextProperty()
	attribute_title16 = db.StringProperty()
	attribute_info16 = db.TextProperty()
	attribute_title17 = db.StringProperty()
	attribute_info17 = db.TextProperty()
	attribute_title18 = db.StringProperty()
	attribute_info18 = db.TextProperty()
	attribute_title19 = db.StringProperty()
	attribute_info19 = db.TextProperty()
	attribute_title20 = db.StringProperty()
	attribute_info20 = db.TextProperty()
	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)

############################################################
## モデル：MP_アクセス制御
############################################################
class UCFMDLAccessControl(UCFModel):
	u'''MP_アクセス制御をイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	title = db.StringProperty()
	access_control_id = db.StringProperty()
	auth_type = db.StringProperty()
	auth_accounts = db.StringListProperty()

	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)

############################################################
## モデル：MP_マスタ管理
############################################################
class UCFMDLSelectItemMaster(UCFModel):
	u'''MP_マスタ管理をイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty()
	title = db.StringProperty()
	master_id = db.StringProperty()
	master_type = db.StringProperty()
	values = db.StringListProperty()
	disps = db.StringListProperty()
	date_created = db.DateTimeProperty(auto_now_add=True)
	date_changed = db.DateTimeProperty(auto_now_add=True)
	creator_name = db.StringProperty()
	updater_name = db.StringProperty()
	del_flag = db.StringProperty()

	def getListTypes():
		u''' リスト型フィールドがあればここでフィールド名のリストを返す '''
		return ('values', 'disps')
	getListTypes = staticmethod(getListTypes)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('date_created', 'date_changed')
	getDateTimeTypes = staticmethod(getDateTimeTypes)

############################################################
## モデル：ファイル
############################################################
class UCFMDLFile(UCFModel):
	u'''ファイルテーブルをイメージしたモデル 2012/04/10'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty(indexed=False)
	data_key = db.StringProperty()			# キー：フロントからこのキーで取得
	data_kind = db.StringProperty()			# 種類（exportgroupcsv, exportaccountcsv, importgroupcsv, importaccountcsv,....）
	data_type = db.StringProperty()			# データタイプ（CSV,BINARY)
	content_type = db.StringProperty()			# MIMEコンテンツタイプ
	data_name = db.StringProperty()			# ファイル名
	data_path = db.StringProperty()
	data_size = db.IntegerProperty()
	blob_key = db.StringProperty()
	data_encoding = db.StringProperty()
	upload_operator_id = db.StringProperty()
	upload_operator_unique_id = db.StringProperty()
	upload_count = db.IntegerProperty()
	last_upload_operator_id = db.StringProperty()
	last_upload_operator_unique_id = db.StringProperty()
	last_upload_date = db.DateTimeProperty()
	download_operator_id = db.StringProperty()
	download_operator_unique_id = db.StringProperty()
	download_count = db.IntegerProperty()
	last_download_operator_id = db.StringProperty()
	last_download_operator_unique_id = db.StringProperty()
	last_download_date = db.DateTimeProperty()
	access_url = db.StringProperty()			# 実体が別のところにある場合、そのURLをセット
	text_data = db.TextProperty()
	blob_data = db.BlobProperty()
	deal_status = db.StringProperty()		# CREATING…作成中
	status = db.StringProperty()		# SUCCESS:処理成功 FAILED:処理失敗
	deal_status = db.StringProperty()					# CREATING…作成中 FIN…処理完了
	expire_date = db.DateTimeProperty()				# このデータのアクセス期限（期限失効後はタスクにより削除）
	log_text = db.TextProperty()					# インポートなどのログ
	date_created = db.DateTimeProperty(auto_now_add=True,indexed=False)
	date_changed = db.DateTimeProperty(auto_now_add=True,indexed=False)
	creator_name = db.StringProperty(indexed=False)
	updater_name = db.StringProperty(indexed=False)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ('', 'date_created', 'date_changed', 'last_download_date', 'last_upload_date', 'expire_date')
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す '''
		return ('', 'data_size','upload_count','download_count')
	getNumberTypes = staticmethod(getNumberTypes)
