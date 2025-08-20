# coding: utf-8

import os,sys,datetime,logging,json
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.api import namespace_manager
from google.appengine.api import memcache

import sateraito_inc

from ucf.utils.ucfutil import *

############################################################
## モデルクラス群（モデルごとにファイル分けたほうがいいかな？import面倒？）
############################################################

############################################################
## モデル：親クラス
############################################################
class UCFModel(db.Model):

	@classmethod
	def getByKey(cls, key):
		entity = None
		if key is not None:
			if key.name() is not None:
				entity = cls.get_by_key_name(key.name())
			elif key.id() is not None:
				entity = cls.get_by_id(key.id())
		return entity

	def exchangeVo(self, timezone):
		u''' db.ModelデータをVoデータ(ハッシュ)に変換 '''
		vo = {}
		for prop in self.properties().values():
			if prop.get_value_for_datastore(self) != None:
				# リスト型
				if prop.name in self.getListTypes():
					vo[prop.name] = str(UcfUtil.listToCsv(prop.get_value_for_datastore(self)))
				# 日付型
				elif prop.name in self.getDateTimeTypes():
					vo[prop.name] = str(prop.get_value_for_datastore(self))
					# LocalTime対応（標準時刻からローカル時間に戻して表示に適切な形式に変換）
					vo[prop.name] = UcfUtil.nvl(UcfUtil.getLocalTime(UcfUtil.getDateTime(vo[prop.name]), timezone))
				else:
					vo[prop.name] = str(prop.get_value_for_datastore(self))
			else:
				vo[prop.name] = ''
		return vo

	def margeFromVo(self, vo, timezone):
		u''' db.ModelデータにVoデータ(ハッシュ)をマージ '''
		for prop in self.properties().values():
			if prop.name not in ('unique_id', 'date_created', 'date_changed'):
				if prop.name in vo:
					try:
						# 数値型
						if prop.name in self.getNumberTypes():
							prop.__set__(self, prop.make_value_from_datastore(int(vo[prop.name]) if vo[prop.name] != '' else 0))
						# Bool型
						elif prop.name in self.getBooleanTypes():
							prop.__set__(self, prop.make_value_from_datastore(True if vo[prop.name] == 'True' else False))
						# 日付型
						elif prop.name in self.getDateTimeTypes():
							if UcfUtil.nvl(vo[prop.name]) != '':
	#							prop.__set__(self, prop.make_value_from_datastore(UcfUtil.getDateTime(vo[prop.name])))
								prop.__set__(self, prop.make_value_from_datastore(UcfUtil.getUTCTime(UcfUtil.getDateTime(vo[prop.name]), timezone)))
							else:
								prop.__set__(self, prop.make_value_from_datastore(None))
						# リスト型
						elif prop.name in self.getListTypes():
							prop.__set__(self, UcfUtil.csvToList(vo[prop.name]))
						# Blob型
						elif prop.name in self.getBlobTypes():
							#prop.__set__(self, vo[prop.name])
							pass
						# References型
						elif prop.name in self.getReferencesTypes():
							pass
						else:
							prop.__set__(self, prop.make_value_from_datastore(str(vo[prop.name])))
					except BaseException as e:
						raise Exception('[' + prop.name + '=' + vo[prop.name] + ']'+ str(e))

	def getReferenceData(self):
		u''' 参照データの情報をUcfDataリストとして返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []
	getNumberTypes = staticmethod(getNumberTypes)

	def getBooleanTypes():
		u''' Bool型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []
	getBooleanTypes = staticmethod(getBooleanTypes)

	def getListTypes():
		u''' リスト型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []
	getListTypes = staticmethod(getListTypes)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getBlobTypes():
		u''' Blobフィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []
	getBlobTypes = staticmethod(getBlobTypes)

	def getReferencesTypes():
		u''' 参照型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []
	getReferencesTypes = staticmethod(getReferencesTypes)


############################################################
## モデル：親クラス
############################################################
class UCFModel2(ndb.Model):

	NDB_MEMCACHE_TIMEOUT = (60 * 60 * 24 * 2)

	@classmethod
	def getByKey(cls, key):
		entity = None
		if key is not None:
			entity = key.get()
		return entity

	def exchangeVo(self, timezone):
		u''' ndb.ModelデータをVoデータ(ハッシュ)に変換 '''
		vo = self.to_dict()
		for k, v in vo.iteritems():
			if v is not None:
				# リスト型
				if k in self.getListTypes():
					vo[k] = str(UcfUtil.listToCsv(v))
				# 日付型
				elif k in self.getDateTimeTypes():
					vo[k] = str(v)
					# LocalTime対応（標準時刻からローカル時間に戻して表示に適切な形式に変換）
					vo[k] = UcfUtil.nvl(UcfUtil.getLocalTime(UcfUtil.getDateTime(v), timezone))
				else:
					vo[k] = str(v)
			else:
				vo[k] = ''
		return vo

	def margeFromVo(self, vo, timezone):
		u''' ndb.ModelデータにVoデータ(ハッシュ)をマージ '''
		for prop in self._properties.values():
			#prop_name = prop.name
			prop_name = prop._name
			#logging.info(prop_name)
			if prop_name not in ['unique_id', 'date_created', 'date_changed']:
				if prop_name in vo:
					try:
						# 数値型
						if isinstance(prop, ndb.IntegerProperty):
							prop.__set__(self, int(vo[prop_name]) if vo[prop_name] != '' else 0)
						# Bool型
						elif isinstance(prop, ndb.BooleanProperty):
							prop.__set__(self, True if vo[prop_name] == 'True' else False)
						# 日付型
						elif isinstance(prop, ndb.DateTimeProperty):
							if UcfUtil.nvl(vo[prop_name]) != '':
								prop.__set__(self, UcfUtil.getUTCTime(UcfUtil.getDateTime(vo[prop_name]), timezone))
							else:
								prop.__set__(self, None)
						# リスト型（String）
						elif isinstance(prop, ndb.StringProperty) and prop._repeated:
							prop.__set__(self, UcfUtil.csvToList(vo[prop_name]))
						# String型
						elif isinstance(prop, ndb.StringProperty):
							prop.__set__(self, str(vo[prop_name]))
						# Blob型
						elif isinstance(prop, ndb.BlobProperty):
							#prop.__set__(self, vo[prop_name])
							pass
						## References型
						#elif prop_name in self.getReferencesTypes():
						#	pass
						else:
							prop.__set__(self, str(vo[prop_name]))
					except BaseException as e:
						raise Exception('[' + prop_name + '=' + vo[prop_name] + ']'+ str(e))

	def getReferenceData(self):
		u''' 参照データの情報をUcfDataリストとして返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []
	getNumberTypes = staticmethod(getNumberTypes)

	def getBooleanTypes():
		u''' Bool型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []
	getBooleanTypes = staticmethod(getBooleanTypes)

	def getListTypes():
		u''' リスト型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []
	getListTypes = staticmethod(getListTypes)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getBlobTypes():
		u''' Blobフィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []
	getBlobTypes = staticmethod(getBlobTypes)

	def getReferencesTypes():
		u''' 参照型フィールドがあればここでフィールド名のリストを返す（抽象メソッド） '''
		#TODO 自動判別したい
		return []
	getReferencesTypes = staticmethod(getReferencesTypes)



############################################################
## モデル：ユーザ
############################################################
class UCFMDLOperator(UCFModel2):
	u'''オペレータマスタをイメージしたモデル'''

	unique_id = ndb.StringProperty(required=True)
	comment = ndb.TextProperty()
	dept_id = ndb.StringProperty(indexed=False)
	#federated_domain = ndb.StringProperty()					# 小文字
	operator_id = ndb.StringProperty()								# ユーザメールアドレス
	operator_id_lower = ndb.StringProperty()					# ユーザメールアドレス（小文字）
	password = ndb.StringProperty(indexed=False)
	password_enctype = ndb.StringProperty()					# 「password」の暗号化対応（AES,DES デフォルト=DES）
	#employee_id = ndb.StringProperty()
	#employee_id_lower = ndb.StringProperty()				# 小文字のみ
	#password1 = ndb.StringProperty(indexed=False)
	#password1_enctype = ndb.StringProperty()					# 「password1」の暗号化対応（AES,DES デフォルト=DES）
	mail_address = ndb.StringProperty()
	sub_mail_address = ndb.StringProperty()					# 	予備のメールアドレス（パスワードリマインダ等で使用）
	last_name = ndb.StringProperty()
	first_name = ndb.StringProperty()
	last_name_kana = ndb.StringProperty()
	first_name_kana = ndb.StringProperty()

	#lineworks_id = ndb.StringProperty()								# LINE WORKS ID

	#alias_name = ndb.StringProperty()								# 別名（一覧など用）
	#nickname = ndb.StringProperty()									# ニックネーム（コミュニティ用）
	#federation_identifier = ndb.StringProperty()			# 統合ID
	account_stop_flag = ndb.StringProperty(indexed=False)
	access_authority = ndb.StringProperty(repeated=True)			# ユーザ権限…ADMIN or OPERATOR or MANAGER
	delegate_function = ndb.StringProperty(repeated=True)			# 委託管理メニュー…ACCOUNT, GROUP, ORGUNIT, ACSAPPLY
	delegate_management_groups = ndb.StringProperty(repeated=True)			# 委託管理する管理グループ…委任管理者が管理できるデータ（ユーザ、グループ、OUなど）のカテゴリ
	management_group = ndb.StringProperty()			# 管理グループ（例：営業部門）…この管理グループの管理を委託された委託管理者がこのデータを管理できるようになる
	#data_federation_group = ndb.StringProperty()			# データ連携管理グループ…外部システム連携グループ. 複数のADと連携する場合など、連携ツールが複数に分かれる場合に各ツールで管理するデータを制御する
	main_group_id = ndb.StringProperty()							# 小文字のみ
	profile_infos = ndb.StringProperty(repeated=True)
	profile_infos_lower = ndb.StringProperty(repeated=True)
	language = ndb.StringProperty(indexed=False)	# 言語設定
	#matrixauth_pin_code = ndb.StringProperty()			# マトリックス認証：PINコード（数字4ケタを想定）
	#matrixauth_pin_code_enctype = ndb.StringProperty()					# 「matrixauth_pin_code」の暗号化対応（AES,DES デフォルト=DES）
	#matrixauth_place_key = ndb.StringProperty()			# マトリックス認証：プレースキー（アルファベット4ケタを想定）
	password_reminder_key = ndb.StringProperty()
	password_reminder_expire = ndb.DateTimeProperty(indexed=True)
	#secret_password_question = ndb.StringProperty(indexed=False)
	#secret_password_answer = ndb.StringProperty(indexed=False)
	next_password_change_flag = ndb.StringProperty(indexed=True)
	password_expire = ndb.DateTimeProperty()
	password_expire_current_notified = ndb.DateTimeProperty()			# 最後に通知されたパスワード期限（繰り返し通知しないための制御で使用）
	password_history = ndb.StringProperty(repeated=True)
	password_change_date = ndb.DateTimeProperty()		# 最後にSSOパスワード「password」が更新された日時（連携ツールで使用）
	password_change_date2 = ndb.DateTimeProperty()		# 最後にユーザーのパスワードが更新された日時（CSVエクスポートなどで使用）
	#mailproxy_available_flag = ndb.StringProperty(indexed=False)
	#fp_app_available_flag = ndb.StringProperty(indexed=False)
	#mobile_user_id = ndb.StringProperty()
	#mobile_device_id = ndb.StringProperty()
	#device_mac_address = ndb.StringProperty(repeated=True)		# 利用可能端末のMACアドレス.アクセス制御に使用
	#client_certificate_cn = ndb.StringProperty(repeated=True)		# ユーザーにヒモづくクライアント証明書のコモンネーム　※クライアント証明書認証で個人を特定するために使用
	#client_certificate_cn_lower = ndb.StringProperty(repeated=True)		# ユーザーにヒモづくクライアント証明書のコモンネーム（小文字）　※クライアント証明書認証で個人を特定するために使用
	login_failed_count = ndb.IntegerProperty(indexed=False)
	login_lock_flag = ndb.StringProperty()
	login_lock_expire = ndb.DateTimeProperty(indexed=True)
	last_login_date = ndb.DateTimeProperty()
	login_count = ndb.IntegerProperty(indexed=False)
	login_password_length = ndb.IntegerProperty(indexed=False)

	# 連絡先・組織アドレス帳・ワークフロー関連項目
	contact_company = ndb.StringProperty()								# 会社名
	contact_company_office = ndb.StringProperty()								# 事業所
	contact_company_department = ndb.StringProperty()								# 部署
	contact_company_department2 = ndb.StringProperty()								# 課・グループ
	contact_company_post = ndb.StringProperty()								# 役職
	contact_email1 = ndb.StringProperty()								# メールアドレス（仕事）
	contact_email2 = ndb.StringProperty()								# メールアドレス（携帯）
	contact_tel_no1 = ndb.StringProperty()								# 電話番号
	contact_tel_no2 = ndb.StringProperty()								# FAX番号
	contact_tel_no3 = ndb.StringProperty()								# 携帯番号
	contact_tel_no4 = ndb.StringProperty()								# 内線
	contact_tel_no5 = ndb.StringProperty()								# ポケットベル
	contact_postal_country = ndb.StringProperty()								# 国、地域
	contact_postal_code = ndb.StringProperty()								# 郵便番号
	contact_postal_prefecture = ndb.StringProperty()								# 住所（都道府県）
	contact_postal_city = ndb.StringProperty()								# 住所（市区町村）
	contact_postal_street_address = ndb.TextProperty()								# 住所（番地）

	custom_attribute1 = ndb.StringProperty()								# 追加属性1 ※汎用SSOシステム等で使用する
	custom_attribute2 = ndb.StringProperty()								# 追加属性2
	custom_attribute3 = ndb.StringProperty()								# 追加属性3
	custom_attribute4 = ndb.StringProperty()								# 追加属性4
	custom_attribute5 = ndb.StringProperty()								# 追加属性5
	custom_attribute6 = ndb.StringProperty()								# 追加属性6
	custom_attribute7 = ndb.StringProperty()								# 追加属性7
	custom_attribute8 = ndb.StringProperty()								# 追加属性8
	custom_attribute9 = ndb.StringProperty()								# 追加属性9
	custom_attribute10 = ndb.StringProperty()								# 追加属性10

	date_created = ndb.DateTimeProperty(auto_now_add=True,indexed=True)
	date_changed = ndb.DateTimeProperty(auto_now_add=True,indexed=True)
	creator_name = ndb.StringProperty(indexed=False)
	updater_name = ndb.StringProperty(indexed=False)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created', 'date_changed', 'password_reminder_expire', 'password_expire', 'password_expire_current_notified', 'password_change_date', 'password_change_date2', 'login_lock_expire', 'last_login_date']
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す '''
		return ['login_failed_count', 'login_count', 'login_password_length']
	getNumberTypes = staticmethod(getNumberTypes)

	def getListTypes():
		u''' リスト型フィールドがあればここでフィールド名のリストを返す '''
		#return ['access_authority', 'delegate_function', 'delegate_management_groups', 'profile_infos', 'profile_infos_lower', 'password_history', 'device_mac_address', 'client_certificate_cn', 'client_certificate_cn_lower']
		return ['access_authority', 'delegate_function', 'delegate_management_groups', 'profile_infos', 'profile_infos_lower', 'password_history']
	getListTypes = staticmethod(getListTypes)


	def put(self, without_update_fulltext_index=False):

		if not without_update_fulltext_index:
			try:
				# update full-text indexes.
				UCFMDLOperator.addOperatorToTextSearchIndex(self)
			except Exception as e:
				logging.info('failed update operator full-text index. unique_id=' + self.unique_id)
				logging.exception(e)

		#if self.client_certificate_cn is None:
		#	self.client_certificate_cn_lower = None
		#else:
		#	self.client_certificate_cn_lower = UcfUtil.csvToList(UcfUtil.listToCsv(self.client_certificate_cn).lower())

		if self.profile_infos is not None:
			self.profile_infos_lower = []
			for profile_id in self.profile_infos:
				self.profile_infos_lower.append(profile_id.lower())
		else:
			self.profile_infos_lower = None

		ndb.Model.put(self)

	def delete(self):
		try:
			UCFMDLOperator.removeOperatorFromIndex(self.unique_id)
		except Exception as e:
			logging.info('failed delete operator full-text index. unique_id=' + self.unique_id)
			logging.exception(e)
		#ndb.Model.delete(self)
		self.key.delete()

	# フルテキストカタログから一覧用の取得フィールドを返す
	@classmethod
	def getReturnedFieldsForTextSearch(cls):
		#return ['unique_id', 'mail_address', 'employee_id', 'first_name', 'last_name', 'alias_name', 'nickname', 'federation_identifier', 'access_authority', 'account_stop_flag', 'login_lock_flag', 'profile_infos']
		return ['unique_id', 'operator_id', 'first_name', 'last_name', 'access_authority', 'account_stop_flag', 'login_lock_flag']

	# フルテキストインデックスからハッシュデータ化して返す
	@classmethod
	def getDictFromTextSearchIndex(cls, ft_result):
		dict = {}
		for field in ft_result.fields:
			if field.name in cls.getReturnedFieldsForTextSearch():
				dict[field.name] = field.value.strip('#')
		return dict

	# ユーザーを全文検索用インデックスに追加する関数
	@classmethod
	def addOperatorToTextSearchIndex(cls, entry):

		vo = entry.exchangeVo(sateraito_inc.DEFAULT_TIMEZONE)	# 日付関連の項目はインデックスしないのでデフォルトタイムゾーンでOKとする

		# 検索用のキーワードをセット
		keyword = ''
		keyword += ' ' + vo.get('comment', '')
		keyword += ' ' + vo.get('operator_id', '')
		keyword += ' ' + vo.get('mail_address', '')
		keyword += ' ' + vo.get('sub_mail_address', '')
		keyword += ' ' + vo.get('last_name', '')
		keyword += ' ' + vo.get('first_name', '')
		keyword += ' ' + vo.get('last_name_kana', '')
		keyword += ' ' + vo.get('first_name_kana', '')
		keyword += ' ' + vo.get('contact_company', '')
		keyword += ' ' + vo.get('contact_company_office', '')
		keyword += ' ' + vo.get('contact_company_department', '')
		keyword += ' ' + vo.get('contact_company_department2', '')
		keyword += ' ' + vo.get('contact_company_post', '')
		keyword += ' ' + vo.get('contact_email1', '')
		keyword += ' ' + vo.get('contact_email2', '')
		keyword += ' ' + vo.get('contact_tel_no1', '')
		keyword += ' ' + vo.get('contact_tel_no2', '')
		keyword += ' ' + vo.get('contact_tel_no3', '')
		keyword += ' ' + vo.get('contact_tel_no4', '')
		keyword += ' ' + vo.get('contact_tel_no5', '')
		keyword += ' ' + vo.get('contact_postal_code', '')
		keyword += ' ' + vo.get('contact_postal_prefecture', '')
		keyword += ' ' + vo.get('contact_postal_city', '')
		keyword += ' ' + vo.get('contact_postal_street_address', '')
		keyword += ' ' + vo.get('custom_attribute1', '')
		keyword += ' ' + vo.get('custom_attribute2', '')
		keyword += ' ' + vo.get('custom_attribute3', '')
		keyword += ' ' + vo.get('custom_attribute4', '')
		keyword += ' ' + vo.get('custom_attribute5', '')
		keyword += ' ' + vo.get('custom_attribute6', '')
		keyword += ' ' + vo.get('custom_attribute7', '')
		keyword += ' ' + vo.get('custom_attribute8', '')
		keyword += ' ' + vo.get('custom_attribute9', '')
		keyword += ' ' + vo.get('custom_attribute10', '')

		search_document = search.Document(
							doc_id = entry.unique_id,
							fields=[
								search.TextField(name='unique_id', value=vo.get('unique_id', '')),												# キー
								search.TextField(name='operator_id', value=vo.get('operator_id', '')),				# 検索用
								search.TextField(name='operator_id_lower', value=vo.get('operator_id_lower', '')),				# 検索用
								search.TextField(name='management_group', value='#' + vo.get('management_group', '') + '#'),	# 検索用
								search.TextField(name='mail_address', value=vo.get('mail_address', '')),									# 表示用
								search.TextField(name='first_name', value=vo.get('first_name', '')),									# 表示用
								search.TextField(name='last_name', value=vo.get('last_name', '')),									# 表示用
								search.TextField(name='access_authority', value='#' + vo.get('access_authority', '') + '#'),									# 表示用
								search.TextField(name='account_stop_flag', value='#' + vo.get('account_stop_flag', '') + '#'),									# 表示用
								search.TextField(name='login_lock_flag', value='#' + vo.get('login_lock_flag', '') + '#'),									# 表示用
								search.TextField(name='text', value=keyword),									# 検索
								search.DateField(name='created_date', value=UcfUtil.getNow())
							])

		index = search.Index(name='operator_index')
		index.put(search_document)

	# 全文検索用インデックスより指定されたunique_idを持つインデックスを削除する関数
	@classmethod
	def removeOperatorFromIndex(cls, unique_id):
		# remove text search index
		index = search.Index(name='operator_index')
		index.delete(unique_id)


############################################################
## モデル：組織グループ
############################################################
class UCFMDLOperatorGroup(UCFModel2):
	u'''オペレータグループをイメージしたモデル'''

	unique_id = ndb.StringProperty(required=True)
	comment = ndb.TextProperty()
	dept_id = ndb.StringProperty(indexed=False)
	#federated_domain = ndb.StringProperty()					# 小文字
	group_id = ndb.StringProperty()								# グループメールアドレス
	group_id_lower = ndb.StringProperty()					# グループメールアドレス（小文字）
	mail_address = ndb.StringProperty()
	group_name = ndb.StringProperty()
	access_authority = ndb.StringProperty(repeated=True)
	management_group = ndb.StringProperty()			# 管理グループ（例：営業部門）…この管理グループの管理を委託された委託管理者がこのデータを管理できるようになる
	#data_federation_group = ndb.StringProperty()			# データ連携管理グループ…外部システム連携グループ. 複数のADと連携する場合など、連携ツールが複数に分かれる場合に各ツールで管理するデータを制御する
	belong_members = ndb.StringProperty(repeated=True)		# 小文字のみ
	group_owners = ndb.StringProperty(repeated=True)		# 小文字のみ
	top_group_flag = ndb.StringProperty()
	main_group_id = ndb.StringProperty()							# 小文字のみ
	profile_infos = ndb.StringProperty(repeated=True)
	profile_infos_lower = ndb.StringProperty(repeated=True)

	# 連絡先関連項目
	contact_company = ndb.StringProperty()								# 会社名
	contact_company_office = ndb.StringProperty()								# 事業所
	contact_company_department = ndb.StringProperty()								# 部署
	contact_company_department2 = ndb.StringProperty()								# 課・グループ
	contact_company_post = ndb.StringProperty()								# 役職
	contact_email1 = ndb.StringProperty()								# メールアドレス（仕事）
	contact_email2 = ndb.StringProperty()								# メールアドレス（携帯）
	contact_tel_no1 = ndb.StringProperty()								# 電話番号
	contact_tel_no2 = ndb.StringProperty()								# FAX番号
	contact_tel_no3 = ndb.StringProperty()								# 携帯番号
	contact_tel_no4 = ndb.StringProperty()								# 内線
	contact_tel_no5 = ndb.StringProperty()								# ポケットベル
	contact_postal_country = ndb.StringProperty()								# 国、地域
	contact_postal_code = ndb.StringProperty()								# 郵便番号
	contact_postal_prefecture = ndb.StringProperty()								# 住所（都道府県）
	contact_postal_city = ndb.StringProperty()								# 住所（市区町村）
	contact_postal_street_address = ndb.TextProperty()								# 住所（番地）

	date_created = ndb.DateTimeProperty(auto_now_add=True,indexed=True)
	date_changed = ndb.DateTimeProperty(auto_now_add=True,indexed=True)
	creator_name = ndb.StringProperty(indexed=False)
	updater_name = ndb.StringProperty(indexed=False)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created', 'date_changed']
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す '''
		return []
	getNumberTypes = staticmethod(getNumberTypes)

	def getListTypes():
		u''' リスト型フィールドがあればここでフィールド名のリストを返す '''
		return ['access_authority', 'belong_members', 'profile_infos', 'profile_infos_lower', 'group_owners']
	getListTypes = staticmethod(getListTypes)

	def put(self):

		# オーナーはbelong_memberに存在するもののみ
		belong_members = self.belong_members
		group_owners = self.group_owners
		if group_owners is not None:
			for owner in group_owners:
				if belong_members is None or owner not in belong_members:
					group_owners.remove(owner)
		self.group_owners = group_owners

		if self.profile_infos is not None:
			self.profile_infos_lower = []
			for profile_id in self.profile_infos:
				self.profile_infos_lower.append(profile_id.lower())
		else:
			self.profile_infos_lower = None

		ndb.Model.put(self)


## モデル：採番マスタ
############################################################
class UCFMDLNumber(UCFModel):
	u'''採番マスタをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty(indexed=True)
	number_id = db.StringProperty()
	number_sub_id = db.StringProperty()
	prefix = db.StringProperty(indexed=False)
	sequence_no = db.IntegerProperty(indexed=False)
	sequence_no_digit = db.IntegerProperty(indexed=False)

	date_created = db.DateTimeProperty(auto_now_add=True,indexed=True)
	date_changed = db.DateTimeProperty(auto_now_add=True,indexed=True)
	creator_name = db.StringProperty(indexed=False)
	updater_name = db.StringProperty(indexed=False)

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す '''
		return ['sequence_no', 'sequence_digit']
	getNumberTypes = staticmethod(getNumberTypes)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created', 'date_changed']
	getDateTimeTypes = staticmethod(getDateTimeTypes)

############################################################
## モデル：企業ドメイン
############################################################
class UCFMDLDeptMaster(UCFModel):
	u'''企業ドメインをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty(indexed=False)
	tenant = db.StringProperty()					# 小文字
	title = db.StringProperty()
	active_flag = db.StringProperty(indexed=False)
	date_created = db.DateTimeProperty(auto_now_add=True,indexed=True)
	date_changed = db.DateTimeProperty(auto_now_add=True,indexed=True)
	creator_name = db.StringProperty(indexed=False)
	updater_name = db.StringProperty(indexed=False)

	office_ipaddresses = db.StringListProperty(indexed=False)			# 社内ネットワーク（各プロファイルで使用するための共通設定）
	xforwardedfor_active_flag = db.StringProperty(indexed=False)	# アクセス制御：X-Forwarded-For を優先して使用するフラグ　ACTIVE…有効
	xforwardedfor_whitelist = db.StringListProperty(indexed=False)	# アクセス制御：X-Forwarded-For使用時のREMOTE_ADDDR のホワイトリスト

	profile_infos = db.StringListProperty()			# 全体設定で利用するプロファイルID
	profile_infos_lower = db.StringListProperty()			# 全体設定で利用するプロファイルID（小文字）
	#hide_access_apply_link_flag = db.StringProperty(indexed=False)	# HIDDEN:ログインページやマイページにアクセス制御端末申請にリンクを表示しない
	hide_regist_sub_mail_address_link_flag = db.StringProperty(indexed=False)	# HIDDEN:マイページに予備のメールアドレス登録のリンクを表示しない
	language = db.StringProperty(indexed=False)	# 言語設定
	timezone = db.StringProperty(indexed=False)	# タイムゾーン
	file_encoding = db.StringProperty(indexed=False)	# CSVファイルの文字コード（デフォルトはShift_JIS）
	username_disp_type = db.StringProperty(indexed=False)			# ユーザ名表示タイプ. ENGLISH…名 姓 の順にする
	company_name = db.StringProperty()	# 会社名
	tanto_name = db.StringProperty()	# 担当者名
	contact_mail_address = db.StringProperty()	# 担当者メールアドレス
	contact_tel_no = db.StringProperty()	# 電話番号

	login_message = db.TextProperty()			# ログインページのメッセージ
	login_fontcolor = db.TextProperty()			# ログインページのフォントカラー：通常の文字列
	login_linkcolor = db.TextProperty()			# ログインページのフォントカラー：リンクカラー
	login_vccolor = db.TextProperty()			# ログインページのフォントカラー：VCメッセージなど
	login_messagecolor = db.TextProperty()			# ログインページのフォントカラー：メッセージボックス
	login_fontcolor_sp = db.TextProperty()			# ログインページのフォントカラー：通常の文字列（スマートフォンサイト）
	login_linkcolor_sp = db.TextProperty()			# ログインページのフォントカラー：リンクカラー（スマートフォンサイト）
	login_vccolor_sp = db.TextProperty()			# ログインページのフォントカラー：VCメッセージなど（スマートフォンサイト）
	login_messagecolor_sp = db.TextProperty()			# ログインページのフォントカラー：メッセージボックス（スマートフォンサイト）
	login_autocomplete_type = db.StringProperty(indexed=False)	# ログインボックスのオートコンプリートタイプ. ID:IDフィールドのみ BOTH:ID、パスワードともに. Empty:使用しない（デフォルト）
	#is_disp_login_domain_combobox = db.StringProperty(indexed=False)	# ログイン画面にドメイン選択ボックスを表示するかどうか（ACTIVE…表示する）
	is_disp_login_language_combobox = db.StringProperty(indexed=False)	# ログイン画面に言語設定ボックスを表示するかどうか（ACTIVE…表示する）
	#domaincombobox_config = db.TextProperty()			# ログイン画面のドメイン選択ボックスの表示設定
	#is_fix_word_login_id = db.StringProperty()			# ログインページの「ログインＩＤ」の文言を固定するオプション（ACTIVE…固定する） 2016.10.12

	md5_suffix_key = db.StringProperty(indexed=False)
	deptinfo_encode_key = db.StringProperty(indexed=False)
	login_history_max_export_cnt = db.IntegerProperty()			# ログイン履歴CSVエクスポート最大件数（0以下の場合はデフォルトの1000）
	login_history_save_term = db.IntegerProperty()			# ログイン履歴を保存する期間月数（0以下の場合はデフォルトの１２ヶ月）
	operation_log_save_term = db.IntegerProperty()			# オペレーションログを保存する期間月数（0以下の場合はデフォルトの６ヶ月）

	oem_company_code = db.StringProperty()					# OEM提供先企業コード（例：sateraito：サテライト）
	sp_codes = db.StringListProperty()					# 提供サービスコード. worksmobile,,,,

	logo_data_key = db.StringProperty()
	is_disp_login_custom_logo = db.StringProperty()	# ACTIVE…表示 ログイン画面にカスタムロゴを表示するかどうか（新デザイン時のみ）
	login_background_pc1_data_key = db.StringProperty()
	login_background_pc2_data_key = db.StringProperty()
	login_background_pc3_data_key = db.StringProperty()
	login_background_pc4_data_key = db.StringProperty()
	login_background_pc5_data_key = db.StringProperty()
	login_background_pc6_data_key = db.StringProperty()
	login_background_pc7_data_key = db.StringProperty()
	login_background_pc8_data_key = db.StringProperty()
	login_background_pc9_data_key = db.StringProperty()
	login_background_pc10_data_key = db.StringProperty()
	login_background_sp1_data_key = db.StringProperty()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created', 'date_changed', 'urgentsso_last_sync_timestamp']
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getListTypes():
		u''' リスト型フィールドがあればここでフィールド名のリストを返す '''
		return ['profile_infos', 'profile_infos_lower', 'xforwardedfor_whitelist', 'office_ipaddresses', 'sp_codes']
	getListTypes = staticmethod(getListTypes)

	def getBooleanTypes():
		u''' Bool型フィールドがあればここでフィールド名のリストを返す '''
		return []
	getBooleanTypes = staticmethod(getBooleanTypes)

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す '''
		return ['login_history_max_export_cnt', 'login_history_save_term', 'operation_log_save_term']
	getNumberTypes = staticmethod(getNumberTypes)

	def put(self):
		if self.profile_infos is not None:
			self.profile_infos_lower = []
			for profile_id in self.profile_infos:
				self.profile_infos_lower.append(profile_id.lower())
		else:
			self.profile_infos_lower = None
		db.Model.put(self)



############################################################
## モデル：アクセス制御：プロファイル
############################################################
class UCFMDLProfile(UCFModel):
	u'''アクセス制御用プロファイルをイメージしたモデル'''

	# 基本設定・共通設定
	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty(indexed=False)
	profile_id = db.StringProperty()
	profile_id_lower = db.StringProperty()				# 小文字のみ
	profile_name = db.StringProperty()
	date_created = db.DateTimeProperty(auto_now_add=True,indexed=True)
	date_changed = db.DateTimeProperty(auto_now_add=True,indexed=True)
	creator_name = db.StringProperty(indexed=False)
	updater_name = db.StringProperty(indexed=False)

	login_lock_available_flag = db.StringProperty()	# ログインロックフラグ. AVAILABLE…有効
	login_lock_max_failed_count = db.IntegerProperty(indexed=False)	# ログインロック：最大失敗回数
	login_lock_expire_info = db.StringProperty()		# ログインロック：期限設定
	passwordchange_unavailable_flag = db.StringProperty(indexed=False)		# パスワード変更・再設定を無効にするオプション：UNAVAILABLE…無効
	#passwordchange_sync_flag = db.StringProperty(indexed=False)		# パスワード一元管理オプション：SYNC…一元管理する
	password_strength_minlength = db.IntegerProperty(indexed=False)	# パスワード強度：最低長
	password_strength_options = db.StringProperty(indexed=False)	# パスワード強度：オプション
	password_history_policy = db.IntegerProperty(indexed=False)	# パスワード強度：履歴チェック世代
	password_expire_info = db.StringProperty(indexed=False)	# パスワード有効期限設定（NOEXPIRE,1MONTH,2MONTH,3MONTH,6MONTH,1YEAR）
	password_expire_notification = db.StringProperty(indexed=False)	# パスワード有効期限事前通知機能（1WEEK,2WEEK,1MONTH）

	# マイページリンク設定
	mypage_links = db.TextProperty()			# MYDOMAIN…私のドメイン、、、などマイページトップに表示するリンク設定

	## セールスフォース連携設定
	#salesforce_sso_active_flag = db.StringProperty(indexed=False)	# 有効フラグ ACTIVE…有効
	#salesforce_sso_user_id_field = db.StringProperty(indexed=False)	# セールスフォースへの連携アカウントIDと指定使用する項目
	## WorksMobile連携設定
	#worksmobile_sso_active_flag = db.StringProperty(indexed=False)	# 有効フラグ ACTIVE…有効
	#worksmobile_sso_user_id_field = db.StringProperty(indexed=False)	# WorksMobileへの連携アカウントIDと指定使用する項目
	## Dropbox連携設定
	#dropbox_sso_active_flag = db.StringProperty(indexed=False)	# 有効フラグ ACTIVE…有効
	#dropbox_sso_user_id_field = db.StringProperty(indexed=False)	# Dropboxへの連携アカウントIDと指定使用する項目
	## Facebook連携設定
	#facebook_sso_active_flag = db.StringProperty(indexed=False)	# 有効フラグ ACTIVE…有効
	#facebook_sso_user_id_field = db.StringProperty(indexed=False)	# Facebookへの連携アカウントIDと指定使用する項目
	## サテライトアドオン連携設定
	#sateraitoaddon_sso_active_flag = db.StringProperty(indexed=False)	# 有効フラグ ACTIVE…有効
	sateraitoaddon_sso_user_id_field = db.StringProperty(indexed=False)	# Facebookへの連携アカウントIDと指定使用する項目

	# アクセス制御関連共通設定
	acsctrl_active_flag = db.StringProperty(indexed=False)	# アクセス制御：有効フラグ ACTIVE…有効
	direct_approval_count = db.IntegerProperty(indexed=False)	# ユーザごとに指定台数は承認作業なしで自動承認とする台数
	is_direct_approval_by_mac_address = db.StringProperty(indexed=False)	# ACTIVE…ユーザに登録されたMACアドレスの場合は自動承認する

	## メールプロキシサーバー関連設定
	#is_use_whole_ipaddresses_for_mailproxy = db.StringProperty(indexed=False)	# アクセス制御：メールプロキシサーバー利用可能ネットワークIPアドレスとしてドメイン全体で指定したIPアドレスも使用. ACTIVE…有効
	#mailproxy_ipaddresses = db.StringListProperty(indexed=False)	# アクセス制御：IPアドレスリスト（111.111.111.111/xx 形式）
	#is_check_password_expire_for_mailproxy = db.StringProperty(indexed=False)	# パスワード期限をチェックするかどうか。ACTIVE…チェックする

	# ネットワーク関連設定
	is_use_whole_ipaddresses = db.StringProperty(indexed=False)	# アクセス制御：社内のIPアドレスとしてドメイン全体で指定したIPアドレスも使用. ACTIVE…有効
#	xforwardedfor_active_flag = db.StringProperty(indexed=False)	# アクセス制御：X-Forwarded-For を優先して使用するフラグ　ACTIVE…有効
#	xforwardedfor_whitelist = db.StringListProperty(indexed=False)	# アクセス制御：X-Forwarded-For使用時のREMOTE_ADDDR のホワイトリスト
	office_ipaddresses = db.StringListProperty(indexed=False)	# アクセス制御：IPアドレスリスト（111.111.111.111/xx 形式）

	# スマートフォン・タブレットオプション
	is_use_sp_config_for_tablet = db.StringProperty(indexed=False)	# iPad、Androidタブレットからのアクセス時はPCではなくスマートフォン扱いとする ACTIVE…有効
	is_use_spfp_config_via_office = db.StringProperty(indexed=False)	# 社内からのアクセス時もスマートフォン、ガラ携帯の設定を使用する ACTIVE…有効 （スマートフォン扱いのタブレットも含む）

	# 社内設定
	office_login_type = db.StringProperty()	# ログインタイプ（OPE,OPE1) ※デフォルト=OPE
	office_two_factor_auth_flag = db.StringProperty(indexed=False)	# 二要素認証を有効にするかどうか ACTIVE…有効
	office_autologin_available_flag = db.StringProperty()	# 自動ログイン有効フラグ.  AVAILABLE…有効
	office_auto_redirect_url = db.StringProperty(indexed=False)	# ユーザがダッシュボードにアクセスしてしまった際に自動で遷移するURL. デフォルト https://www.google.com/a/{domain}/
	office_auto_redirect_url_action_type = db.StringProperty(indexed=False)	# DASHBOARD…ダッシュボードにアクセスした場合のみ遷移。Empty：Gmailにアクセスした場合なども含めて遷移。
#	office_acsctrl_active_flag = db.StringProperty(indexed=False)	# アクセス制御：有効フラグ ACTIVE…有効
	office_useragents = db.StringListProperty(indexed=False)	# アクセス制御：ブラウザリスト（IE or CR or FF or ...）
	office_device_check_flag = db.StringProperty(indexed=False)	# アクセス制御：PC、スマホ端末制御をするかどうかのフラグ　ACTIVE…有効
	office_client_certificate_flag = db.StringProperty(indexed=False)	# クライアント証明書認証が必要かどうかフラグ　ACTIVE…有効
	office_client_certificate_info = db.TextProperty()	# クライアント証明書関連のチェック情報など（JSON）
	office_access_by_network_type = db.StringProperty(indexed=False)	# ネットワーク、環境単位でアクセスをブロックする設定（DENIED or 空（デフォルト））

	# 社外設定
	outside_login_type = db.StringProperty()	# ログインタイプ（OPE,OPE1) ※デフォルト=OPE
	outside_two_factor_auth_flag = db.StringProperty(indexed=False)	# 二要素認証を有効にするかどうか ACTIVE…有効
	outside_autologin_available_flag = db.StringProperty()	# 自動ログイン有効フラグ.  AVAILABLE…有効
	outside_auto_redirect_url = db.StringProperty(indexed=False)	# ユーザがダッシュボードにアクセスしてしまった際に自動で遷移するURL. デフォルト https://www.google.com/a/{domain}/
	outside_auto_redirect_url_action_type = db.StringProperty(indexed=False)	# DASHBOARD…ダッシュボードにアクセスした場合のみ遷移。Empty：Gmailにアクセスした場合なども含めて遷移。
#	outside_acsctrl_active_flag = db.StringProperty(indexed=False)	# アクセス制御：有効フラグ ACTIVE…有効
	outside_useragents = db.StringListProperty(indexed=False)	# アクセス制御：ブラウザリスト（IE or CR or FF or ...）
	outside_device_check_flag = db.StringProperty(indexed=False)	# アクセス制御：PC、スマホ端末制御をするかどうかのフラグ　ACTIVE…有効
	outside_client_certificate_flag = db.StringProperty(indexed=False)	# クライアント証明書認証が必要かどうかフラグ　ACTIVE…有効
	outside_client_certificate_info = db.TextProperty()	# クライアント証明書関連のチェック情報など（JSON）
	outside_access_by_network_type = db.StringProperty(indexed=False)	# ネットワーク、環境単位でアクセスをブロックする設定（DENIED or 空（デフォルト））

	# スマホ（社外）設定
	sp_login_type = db.StringProperty()	# ログインタイプ（OPE,OPE1) ※デフォルト=OPE
	sp_autologin_available_flag = db.StringProperty()	# 自動ログイン有効フラグ.  AVAILABLE…有効
	sp_two_factor_auth_flag = db.StringProperty(indexed=False)	# 二要素認証を有効にするかどうか ACTIVE…有効
	sp_auto_redirect_url = db.StringProperty(indexed=False)	# ユーザがダッシュボードにアクセスしてしまった際に自動で遷移するURL. デフォルト https://www.google.com/a/{domain}/
	sp_auto_redirect_url_action_type = db.StringProperty(indexed=False)	# DASHBOARD…ダッシュボードにアクセスした場合のみ遷移。Empty：Gmailにアクセスした場合なども含めて遷移。
#	sp_acsctrl_active_flag = db.StringProperty(indexed=False)	# アクセス制御：有効フラグ ACTIVE…有効
	sp_useragents = db.StringListProperty(indexed=False)	# アクセス制御：ブラウザリスト（IE or CR or FF or ...）
	sp_device_check_flag = db.StringProperty(indexed=False)	# アクセス制御：PC、スマホ端末制御をするかどうかのフラグ　ACTIVE…有効
	sp_client_certificate_flag = db.StringProperty(indexed=False)	# クライアント証明書認証が必要かどうかフラグ　ACTIVE…有効
	sp_client_certificate_info = db.TextProperty()	# クライアント証明書関連のチェック情報など（JSON）
	sp_access_by_network_type = db.StringProperty(indexed=False)	# ネットワーク、環境単位でアクセスをブロックする設定（DENIED or 空（デフォルト））

	## ガラ携帯（社外）設定
	#fp_login_type = db.StringProperty()	# ログインタイプ（OPE,OPE1) ※デフォルト=OPE
	#fp_two_factor_auth_flag = db.StringProperty(indexed=False)	# 二要素認証を有効にするかどうか ACTIVE…有効
	#fp_autologin_available_flag = db.StringProperty()	# 自動ログイン有効フラグ.  AVAILABLE…有効
	#fp_auto_redirect_url = db.StringProperty(indexed=False)	# ユーザがダッシュボードにアクセスしてしまった際に自動で遷移するURL. デフォルト https://www.google.com/a/{domain}/
	#fp_auto_redirect_url_action_type = db.StringProperty(indexed=False)	# DASHBOARD…ダッシュボードにアクセスした場合のみ遷移。Empty：Gmailにアクセスした場合なども含めて遷移。
#	fp_acsctrl_active_flag = db.StringProperty(indexed=False)	# アクセス制御：有効フラグ ACTIVE…有効
	#fp_useragents = db.StringListProperty(indexed=False)	# アクセス制御：ブラウザリスト（IE or CR or FF or ...）
	#fp_device_check_flag = db.StringProperty(indexed=False)	# アクセス制御：PC、スマホ端末制御をするかどうかのフラグ　ACTIVE…有効
	#fp_client_certificate_flag = db.StringProperty(indexed=False)	# クライアント証明書認証が必要かどうかフラグ　ACTIVE…有効
	#fp_client_certificate_info = db.TextProperty()	# クライアント証明書関連のチェック情報など（JSON）
	#fp_access_by_network_type = db.StringProperty(indexed=False)	# ネットワーク、環境単位でアクセスをブロックする設定（DENIED or 空（デフォルト））

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created', 'date_changed']
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す '''
		return ['login_lock_max_failed_count','password_strength_minlength','password_history_policy', 'direct_approval_count']
	getNumberTypes = staticmethod(getNumberTypes)

	def getListTypes():
		u''' リスト型フィールドがあればここでフィールド名のリストを返す '''
		#return ['mailproxy_ipaddresses', 'office_ipaddresses', 'office_useragents', 'outside_useragents', 'sp_useragents', 'fp_useragents']
		return ['mailproxy_ipaddresses', 'office_ipaddresses', 'office_useragents', 'outside_useragents', 'sp_useragents']
	getListTypes = staticmethod(getListTypes)


############################################################
## モデル：アクセス制御：プロファイルにヒモづく端末識別ID（MACアドレス）
############################################################
class UCFMDLDeviceDistinguishID(UCFModel2):

	unique_id = ndb.StringProperty(required=True)
	profile_unique_id = ndb.StringProperty()
	device_distinguish_ids_str = ndb.TextProperty()				# MACアドレス、Identifer for Vendor …数千件入る想定
	device_distinguish_ids_for_search = ndb.StringProperty(repeated=True)				# MACアドレス、Identifer for Vendor …数千件入る想定（小文字、:や-のカットなどを実施）
	date_created = ndb.DateTimeProperty(auto_now_add=True)
	date_changed = ndb.DateTimeProperty(auto_now=True)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created', 'date_changed']
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getListTypes():
		u''' リスト型フィールドがあればここでフィールド名のリストを返す '''
		return ['device_distinguish_ids_for_search']
	getListTypes = staticmethod(getListTypes)



############################################################
## モデル：ログイン履歴
############################################################
class UCFMDLLoginHistory(UCFModel2):
	u'''ログイン履歴をイメージしたモデル'''

	unique_id = ndb.StringProperty(required=True)
	comment = ndb.TextProperty()
	dept_id = ndb.StringProperty(indexed=False)
	operator_unique_id = ndb.StringProperty()			# ユーザＩＤ変更を考慮してユーザにヒモづく一覧を取得する際にはこれをキーとして取得
	operator_id = ndb.StringProperty()							# CSV出力時には必要だと思うので
	operator_id_lower = ndb.StringProperty()							# 小文字
	login_id = ndb.StringProperty()							# ログインで使用したＩＤ（ユーザＩＤ、社員ＩＤ）
	login_id_lower = ndb.StringProperty()							# 小文字（検索用）
	login_password = ndb.StringProperty(indexed=False)							# ログインで使用したパスワード（暗号化）※ハッキング対策などに使用するため一応保持
	login_password_enctype = ndb.StringProperty()							# ログインパスワードの暗号化タイプ（AES、DES デフォルト=DES）
	login_password_length = ndb.IntegerProperty(indexed=False)
	login_type = ndb.StringProperty(indexed=False)
	login_result = ndb.StringProperty()				# ログイン成功フラグ SUCCESS OR FAILED
	log_code = ndb.StringProperty()				# ID_FAILED など
	is_exist_log_detail = ndb.BooleanProperty()	# True…log_textを詳細テーブルに保持
	log_text = ndb.TextProperty()						# 別途詳細ログがあれば設定（is_exist_log_detail=Trueの場合は詳細テーブルに保持）
	user_agent = ndb.TextProperty()
	session_id = ndb.StringProperty()				# セッションＩＤ（取得できるのかな）
	cookie_auth_id = ndb.StringProperty()				# 認証ＩＤ（Ｃｏｏｋｉｅ認証実装時の認証ＩＤ）
	client_ip = ndb.StringProperty(indexed=False)
	client_x_forwarded_for_ip = ndb.StringProperty(indexed=False)
	use_profile_id = ndb.StringProperty()									# 認証時に使用したプロファイルＩＤ
	use_access_apply_unique_id = ndb.StringProperty()			# ログイン成功時に使用したアクセス申請データのユニークＩＤ
	target_career = ndb.StringProperty()
	target_env = ndb.StringProperty()		# 対象環境ID（office, outside, sp, fp)
	is_auto_login = ndb.StringProperty()		# AUTO…自動ログインでのアクセス
	mobile_user_id = ndb.StringProperty()
	mobile_device_id = ndb.StringProperty()
	access_date = ndb.DateTimeProperty()
	management_group = ndb.StringProperty()			# 管理グループ（例：営業部門）…この管理グループの管理を委託された委託管理者がこのデータを管理できるようになる
	date_created = ndb.DateTimeProperty(auto_now_add=True,indexed=True)
	date_changed = ndb.DateTimeProperty(auto_now_add=True,indexed=True)
	creator_name = ndb.StringProperty(indexed=False)
	updater_name = ndb.StringProperty(indexed=False)

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す '''
		return ['login_password_length']
	getNumberTypes = staticmethod(getNumberTypes)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created', 'date_changed', 'access_date']
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getBooleanTypes():
		u''' Bool型フィールドがあればここでフィールド名のリストを返す '''
		return ['is_exist_log_detail']
	getBooleanTypes = staticmethod(getBooleanTypes)


############################################################
## モデル：ログイン履歴詳細
############################################################
class UCFMDLLoginHistoryDetail(UCFModel2):
	u'''ログイン履歴詳細をイメージしたモデル'''

	unique_id = ndb.StringProperty(required=True)
	history_unique_id = ndb.StringProperty()
	log_text = ndb.TextProperty()
	date_created = ndb.DateTimeProperty(auto_now_add=True)

############################################################
## モデル：ログイン履歴（遅延登録用一時登録テーブル）
############################################################
class UCFMDLLoginHistoryForDelay(UCFModel2):
	u'''ログイン履歴（遅延登録用一時登録テーブル）'''

	unique_id = ndb.StringProperty(required=True)
	operator_unique_id = ndb.StringProperty()			# ユーザＩＤ変更を考慮してユーザにヒモづく一覧を取得する際にはこれをキーとして取得
	operator_id_lower = ndb.StringProperty()							# メールアドレス小文字
	params = ndb.TextProperty()				# ログイン履歴関連の情報（JSON）
	date_created = ndb.DateTimeProperty(auto_now_add=True)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created']
	getDateTimeTypes = staticmethod(getDateTimeTypes)

############################################################
## モデル：ログイン情報（成功、失敗）（遅延登録用一時登録テーブル）
############################################################
class UCFMDLLoginInfoForDelay(UCFModel2):
	u'''ログイン情報（成功、失敗）（遅延登録用一時登録テーブル）'''

	unique_id = ndb.StringProperty(required=True)
	operator_unique_id = ndb.StringProperty()			# ユーザＩＤ変更を考慮してユーザにヒモづく一覧を取得する際にはこれをキーとして取得
	operator_id_lower = ndb.StringProperty()							# メールアドレス小文字
	params = ndb.TextProperty()				# ログイン情報関連の情報（JSON）
	date_created = ndb.DateTimeProperty(auto_now_add=True)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created']
	getDateTimeTypes = staticmethod(getDateTimeTypes)



############################################################
## モデル：ファイル
############################################################
class UCFMDLFile(UCFModel):
	u'''ファイルテーブルをイメージしたモデル'''

	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty(indexed=False)
	data_key = db.StringProperty()			# キー：フロントからこのキーで取得
	data_kind = db.StringProperty()			# 種類（exportgroupcsv, exportaccountcsv, importgroupcsv, importaccountcsv,picture,....）
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
	is_use_item = db.BooleanProperty()		# UCFMDLFileItemを使う場合、True（1MB制限対策）
	text_data = db.TextProperty()
	blob_data = db.BlobProperty()
	status = db.StringProperty()		# SUCCESS:処理成功 FAILED:処理失敗
	deal_status = db.StringProperty()					# CREATING…作成中 FIN…処理完了
	expire_date = db.DateTimeProperty()				# このデータのアクセス期限（期限失効後はタスクにより削除）
	log_text = db.TextProperty()					# インポートなどのログ
	task_token = db.StringProperty()					# ＧＡＥのプロセスが強制ＫＩＬＬされた際のチェック用
	date_created = db.DateTimeProperty(auto_now_add=True,indexed=True)
	date_changed = db.DateTimeProperty(auto_now_add=True,indexed=True)
	creator_name = db.StringProperty(indexed=False)
	updater_name = db.StringProperty(indexed=False)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created', 'date_changed', 'last_download_date', 'last_upload_date', 'expire_date']
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す '''
		return ['data_size','upload_count','download_count']
	getNumberTypes = staticmethod(getNumberTypes)

	def getBooleanTypes():
		u''' Bool型フィールドがあればここでフィールド名のリストを返す '''
		return ['is_use_item']
	getBooleanTypes = staticmethod(getBooleanTypes)

	def getBlobTypes():
		u''' Blobフィールドがあればここでフィールド名のリストを返す '''
		return ['blob_data']
	getBlobTypes = staticmethod(getBlobTypes)

############################################################
## モデル：ファイルアイテム
############################################################
class UCFMDLFileItem(UCFModel):
	u'''ファイルテーブルをイメージしたモデル'''
	unique_id = db.StringProperty(required=True)
	data_key = db.StringProperty()
	item_order = db.IntegerProperty()
	text_data = db.TextProperty()
	blob_data = db.BlobProperty()
	date_created = db.DateTimeProperty(auto_now_add=True,indexed=True)
	date_changed = db.DateTimeProperty(auto_now_add=True,indexed=True)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created', 'date_changed']
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getNumberTypes():
		u''' 数値型フィールドがあればここでフィールド名のリストを返す '''
		return ['item_order']
	getNumberTypes = staticmethod(getNumberTypes)

	def getBlobTypes():
		u''' Blobフィールドがあればここでフィールド名のリストを返す '''
		return ['blob_data']
	getBlobTypes = staticmethod(getBlobTypes)



############################################################
## モデル：ID変更履歴、タスク管理
############################################################
class UCFMDLTaskChangeID(UCFModel):
	unique_id = db.StringProperty(required=True)
	comment = db.TextProperty()
	dept_id = db.StringProperty(indexed=False)
	task_type = db.StringProperty()			# change_operator_id,change_user_id,change_group_id
	task_deal_status = db.StringProperty()		# (Empty：ポーリング対象) WAIT：処理開始待ち PROCESSING：処理中 STOP:停止 STOP_INDICATING:停止指示中 FIN:処理完了
	task_status = db.StringProperty()		# SUCCESS:処理成功 FAILED:処理失敗
	task_status_date = db.DateTimeProperty()	# ステータス更新日
	task_start_date = db.DateTimeProperty()				# 最終タスク開始日
	task_end_date = db.DateTimeProperty()					# 最終タスク完了日
	execute_operator_id = db.StringProperty()					# 実行ユーザ
	log_text = db.TextProperty()					# ログ
	target_unique_id = db.StringProperty()		# 対象アカウント、グループ等のユニークID
	src_data_id = db.StringProperty()					# 元のアカウント、グループID
	dst_data_id = db.StringProperty()					# 変更後のアカウント、グループID
	date_created = db.DateTimeProperty(auto_now_add=True,indexed=True)
	date_changed = db.DateTimeProperty(auto_now_add=True,indexed=True)
	creator_name = db.StringProperty(indexed=False)
	updater_name = db.StringProperty(indexed=False)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created', 'date_changed', 'task_status_date', 'task_start_date', 'task_end_date']
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getBooleanTypes():
		u''' Bool型フィールドがあればここでフィールド名のリストを返す '''
		return []
	getBooleanTypes = staticmethod(getBooleanTypes)


############################################################
## モデル：二要素認証コード
############################################################
class UCFMDLTwoFactorAuth(UCFModel):
	u'''二要素認証のコードを管理（1ユーザ1レコード） '''
	unique_id = db.StringProperty(required=True)
	dept_id = db.StringProperty(indexed=False)
	operator_unique_id = db.StringProperty()			# ユーザＩＤ変更を考慮してユーザにヒモづく一覧を取得する際にはこれをキーとして取得
	two_factor_auth_code = db.StringProperty()		# 二要素認証コード
	auth_code_expire = db.DateTimeProperty()			# 二要素認証期限
	date_created = db.DateTimeProperty(auto_now_add=True,indexed=True)
	date_changed = db.DateTimeProperty(auto_now_add=True,indexed=True)

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['date_created', 'date_changed', 'auth_code_expire']
	getDateTimeTypes = staticmethod(getDateTimeTypes)


############################################################
## モデル：フルテキストインデックス初期設定バッチ処理用一時テーブル
############################################################
class UCFMDLTempForFullTextSearch(UCFModel):

	tenant = db.StringProperty()
	is_indexed_operator = db.BooleanProperty()


############################################################
## モデル：オペレーションログ
############################################################
class UCFMDLOperationLog(UCFModel2):

	unique_id = ndb.StringProperty(required=True)
	operation_date = ndb.DateTimeProperty()
	operator_id = ndb.StringProperty()
	operator_unique_id = ndb.StringProperty()
	screen = ndb.StringProperty()															# 大体のページなど。分類用？
	operation_type = ndb.StringProperty()													# 処理種別
	operation = ndb.StringProperty()																	# 検索条件に使いたいのでオペレーションに対して一意となるような値
	target_unique_id = ndb.StringProperty()												# 対象のデータの内部ID（operationによって入る値は決まってくる）
	target_data = ndb.StringProperty()												# 対象のデータの表示用ID（operationによって入る値は決まってくる）
	client_ip = ndb.StringProperty()
	is_api = ndb.BooleanProperty()														# APIからのアクセス
	detail = ndb.TextProperty()
	date_created = ndb.DateTimeProperty(auto_now_add=True)
	date_changed = ndb.DateTimeProperty(auto_now=True)

	@classmethod
	def addLog(cls, operator_id, operator_unique_id, screen, operation_type, target_data, target_unique_id, client_ip, detail, is_api=False, is_async=False):
		row = cls()
		row.unique_id = UcfUtil.guid()
		row.operator_id = operator_id
		row.operator_unique_id = operator_unique_id
		row.screen = screen
		row.operation_type = operation_type
		row.operation = screen + '_' + operation_type
		row.target_unique_id = target_unique_id
		row.target_data = target_data
		row.client_ip = client_ip
		row.is_api = is_api
		row.detail = detail
		row.operation_date = datetime.datetime.now(tz=None)
		if is_async:
			future = row.put_async()
		else:
			row.put()

	def getDateTimeTypes():
		u''' DateTime型フィールドがあればここでフィールド名のリストを返す '''
		return ['operation_date', 'date_created', 'date_changed']
	getDateTimeTypes = staticmethod(getDateTimeTypes)

	def getBooleanTypes():
		u''' Bool型フィールドがあればここでフィールド名のリストを返す '''
		return ['is_api']
	getBooleanTypes = staticmethod(getBooleanTypes)


############################################################
## モデル：ディクショナリ
############################################################
class Dictionary(UCFModel2):
	dictionary_id = ndb.StringProperty()  # 辞書のユニックID
	keyword = ndb.StringProperty(repeated=True)  # 辞書のキーワード
	keyword_hash = ndb.StringProperty()  # 辞書のキーワードハッシュ
	defining = ndb.StringProperty()  # キーワードの
	priority = ndb.IntegerProperty(default=0)  # 1,2,3,4,,,,,
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)

	@classmethod
	def DictionaryIndexCreate(cls, keyword, keyword_hash, defining, priority, dictionary_id):
		logging.info(keyword)
		# dictionaryIndex　作成
		tempDefining = json.loads(defining)
		defining_items = []
		for key, value in tempDefining.items():
			defining_items.append(tempDefining[key].strip())

		fields = [search.TextField(name='keyword', value=keyword),
				  search.TextField(name='keyword_hash', value=keyword_hash),
				  search.TextField(name='defining_value', value=','.join(defining_items)),
				  search.TextField(name='defining', value=defining),
				  search.NumberField(name='priority', value=UcfUtil.toInt(priority))]
		d = search.Document(doc_id=dictionary_id.strip(), fields=fields)
		try:
			add_result = search.Index(name='dictionaryIndex').put(d)
			logging.info(add_result)
		except search.Error:
			logging.info(search.Error)

	@classmethod
	def DictionaryIndexDelete(cls, arrId):
		try:
			for key in arrId:
				index = search.Index('dictionaryIndex')
				index.delete(key)
		except search.DeleteError:
			logging.exception("Error removing doc id %s.", key)


############################################################
## Save data by AIspeaker Bot
############################################################
class SendEmail(UCFModel2):
	id_conversation = ndb.StringProperty()  # id conversation
	email = ndb.StringProperty()  # email
	subject = ndb.StringProperty()  # subject
	content = ndb.StringProperty()  # content
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)
