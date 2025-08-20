# coding: utf-8

# import os,sys,Cookie
# from google.appengine.api import users
# from google.appengine.ext import webapp
# from google.appengine.ext.webapp import template
#
# from ucf.utils.ucfutil import *
# from ucf.config.ucfconfig import *
# from ucf.config.ucfmessage import *
from ucf.utils.ucfxml import *
from ucf.utils.models import *
from ucf.gdata.spreadsheet.util import *

############################################################
## TableHelper用設定クラス：親クラス
############################################################
class TableHelperConfig(UcfConfig):
	_crypto_key = UcfConfig.CRYPTO_KEY

	MASTERINFO_SPREADSHEET_ACCOUNT = 'Spreadsheet/@account'
	MASTERINFO_SPREADSHEET_PASSWORD = 'Spreadsheet/@password'
	MASTERINFO_SPREADSHEET_KEY = 'Spreadsheet/@key'
	MASTERINFO_WORKSHEET_NAME = 'Spreadsheet/@worksheet_name'

	_xmlConfig = None
	_config_info = None

	#+++++++++++++++++++++++++++++++++++++++
	#+++ コンストラクタ
	#+++++++++++++++++++++++++++++++++++++++
	def __init__(self, param_file_path):		# PageHelperのgetParamFilePathがよべないためパスをパラメータとしている
		self._xmlConfig	= self.getConfig(param_file_path)
		self._config_info = self.exchangeConfigToHash(self._xmlConfig)

	def getConfig(self, param_file_path):
		u''' 設定ファイル取得 '''
		if os.path.exists(param_file_path):
			xmlConfig = UcfXml.load(param_file_path)
			return xmlConfig
		else:
			return None

	def exchangeConfigToHash(self, xmlConfig):
		u''' 設定ファイルの情報をハッシュに変換 '''
		if xmlConfig != None:
			# ハッシュにして返す
			info = xmlConfig.exchangeToHash(isAttr=True, isChild=True)
			return info
		else:
			return None

	def getFieldDefine(self):
		u''' 設定ファイルからフィールド情報を取得 '''
		return self._xmlConfig.selectNodes('FieldDefine/Item')

	def getAccount(self):
		u''' 設定ファイルの値を取得：アカウント '''
		return UcfUtil.deCrypto(UcfUtil.getHashStr(self._config_info, self.MASTERINFO_SPREADSHEET_ACCOUNT), self._crypto_key)

	def getPassword(self):
		u''' 設定ファイルの値を取得：パスワード '''
		return UcfUtil.deCrypto(UcfUtil.getHashStr(self._config_info, self.MASTERINFO_SPREADSHEET_PASSWORD), self._crypto_key)

	def getSpreadsheetID(self):
		u''' 設定ファイルの値を取得：スプレッドシートＩＤ '''
		return UcfUtil.getHashStr(self._config_info, self.MASTERINFO_SPREADSHEET_KEY)

	def getWorksheetName(self):
		u''' 設定ファイルの値を取得：ワークシート名 '''
		return UcfUtil.getHashStr(self._config_info, self.MASTERINFO_WORKSHEET_NAME)

	def getSpreadsheetAuthInfo(self):
		u''' スプレッドシートアクセス関連情報をまとめて取得 '''
		account = self.getAccount()
		password = self.getPassword()
		spreadsheet_key = self.getSpreadsheetID()
		worksheet_name = self.getWorksheetName()

		return account, password, spreadsheet_key, worksheet_name


############################################################
## データソースへのアクセスを管理する親クラス
############################################################
class TableHelper():
	#+++++++++++++++++++++++++++++++++++++++
	#+++ コンストラクタ
	#+++++++++++++++++++++++++++++++++++++++
	def __init__(self):
		self._processing_flag = False	# このインスタンスで一覧取得の処理中かどうかのフラグ
		self._current_vo = None
		self._current_entry = None
		self._current_idx = None
		pass

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 取得処理開始
	#+++++++++++++++++++++++++++++++++++++++
	def	beginSelectProcess(self):
		u'''
		TITLE:取得処理開始
		PARAMETER:
		RETURN:
		'''
		if self._processing_flag:
			raise Exception([u'dealing other process.'])
			return

		self._processing_flag = True

		self._current_vo = None
		self._current_entry = None
		self._current_idx = 0

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 取得処理終了
	#+++++++++++++++++++++++++++++++++++++++
	def closeSelectProcess(self):
		u'''
		TITLE:取得処理終了
		PARAMETER:
		RETURN:
		'''
		self._processing_flag = False
		self._current_vo = None
		self._current_entry = None
		self._current_idx = 0
		pass

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 現在のVoを取得
	#+++++++++++++++++++++++++++++++++++++++
	def getCurrentVo(self):
		u'''
		TITLE:現在のVoを取得
		PARAMETER:
		RETURN:Vo
		'''
		return self._current_vo

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 現在の生のデータを取得（Entry or Model）
	#+++++++++++++++++++++++++++++++++++++++
	def getCurrentData(self):
		u'''
		TITLE:現在の生のデータを取得（Entry or Model）
		PARAMETER:
		RETURN:Entry or Model
		'''
		return self._current_entry

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 現在のインデックスを取得
	#+++++++++++++++++++++++++++++++++++++++
	def getCurrentIndex(self):
		u'''
		TITLE:現在のインデックスを取得
		PARAMETER:
		RETURN:インデックス（0～）
		'''
		return self._current_idx

	#+++++++++++++++++++++++++++++++++++++++
	#+++ １件取得（抽象メソッド）
	#+++++++++++++++++++++++++++++++++++++++
#	def read(self):
#		u'''
#		TITLE:１件取得（抽象メソッド）
#		PARAMETER:
#		RETURN:現在のvo
#		'''
#		raise Exception, [u'called abstract method.']

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 実際のデータソース用のTableHelperクラスのインスタンスを生成して返す
	#+++++++++++++++++++++++++++++++++++++++
	def createInstance(config):
		u'''
		TITLE:実際のデータソースアクセスクラスのインスタンスを返す（抽象メソッド）
		PARAMETER:
		RETURN:TableHelperの子クラスのインスタンス
		'''
		raise Exception([u'called abstract method.'])
	createInstance = staticmethod(createInstance)


############################################################
## BigTableへのアクセスを管理する親クラス
############################################################
class BigTableTableHelper(TableHelper):
	#+++++++++++++++++++++++++++++++++++++++
	#+++ コンストラクタ
	#+++++++++++++++++++++++++++++++++++++++
	def __init__(self, config):
		TableHelper.__init__(self)
		self._config = config

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 取得処理開始
	#+++++++++++++++++++++++++++++++++++++++
	def beginSelect(self, models):
		u'''
		TITLE:取得処理開始
		PARAMETER:
			models:GqlQuery
		RETURN:
		'''
		self.beginSelectProcess()
		self._data_source = models

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 取得処理完了
	#+++++++++++++++++++++++++++++++++++++++
	def closeSelect(self):
		u'''
		TITLE:取得処理完了
		PARAMETER:
		RETURN:
		'''
		self.closeSelectProcess()
		self._data_source = None

	#+++++++++++++++++++++++++++++++++++++++
	#+++ １件取得
	#+++++++++++++++++++++++++++++++++++++++
	def read(self):
		u'''
		TITLE:１件取得
		PARAMETER:
		RETURN:True…データあり False…データなし
		'''
		vo = None
		model = None
		if self._data_source.count() > self._current_idx:
			model = self._data_source[self._current_idx]
			vo = model.exchangeVo()
			self._current_idx += 1

		self._current_vo = vo
		self._current_entry = model
		return vo != None

	#+++++++++++++++++++++++++++++++++++++++
	#+++ GQLのWhere句を生成
	#+++++++++++++++++++++++++++++++++++++++
	def getToGqlWhereQuery(self, wheres):
		u'''
		TITLE:GQLのWhere句を生成して返す. TODO UcfUtilからは将来的に削除したい
		PARAMETER:
			wheres:where句１つ１つのリスト（例：field_a='aaa'）
		RETURN:WHERE句（例：WHERE field_a='aaa' and field_b='bbb'）
		'''
		return UcfUtil.getToGqlWhereQuery(wheres)

############################################################
## Spreadsheetへのアクセスを管理する親クラス
############################################################
class SpreadsheetTableHelper(TableHelper):
	#+++++++++++++++++++++++++++++++++++++++
	#+++ コンストラクタ
	#+++++++++++++++++++++++++++++++++++++++
	def __init__(self, config):
		TableHelper.__init__(self)
		self._config = config

		self._titles = None
		self._titles_ex = None
		self._hash_title_idx = None
		self._hash_title_idx_ex = None
		self._hash_title_to_id = None
		self._hash_id_to_title = None

		self.__service = None
		self.__data_source_index = 0
		self.__is_read_all_results = False

		self._data_source = None

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 取得処理開始
	#+++++++++++++++++++++++++++++++++++++++
	def beginSelect(self, feed, service=None, is_read_all_results=False):
		u'''
		TITLE:取得処理開始
		PARAMETER:
			feed:ListFeed
			service:
			is_read_all_results:True･･･start_index, max_resultsで指定された結果セットを順に対象データがなくなるまで取得する
		RETURN:
		'''
		self.beginSelectProcess()
		self.__service = service
		self._data_source = feed
		self.__data_source_index = 0
		self.__is_read_all_results = is_read_all_results

	def __refleshSelect(self, feed):
		self._data_source = feed
		self.__data_source_index = 0


	#+++++++++++++++++++++++++++++++++++++++
	#+++ 取得処理完了
	#+++++++++++++++++++++++++++++++++++++++
	def closeSelect(self):
		u'''
		TITLE:取得処理完了
		PARAMETER:
		RETURN:
		'''
		self.closeSelectProcess()
		self._data_source = None
		self.__service = None
		self.__data_source_index = 0

	#+++++++++++++++++++++++++++++++++++++++
	#+++ １件取得
	#+++++++++++++++++++++++++++++++++++++++
	def read(self):
		u'''
		TITLE:１件取得
		PARAMETER:
		RETURN:True…データあり False…データなし
		'''
		vo = None
		entry = None
		if self._data_source != None and len(self._data_source.entry) > self.__data_source_index:
			vo = {}
			entry = self._data_source.entry[self.__data_source_index]

			# entry.customからまわすと空の項目が取得できないのでtitle配列からまわすように変更 2009/07/09 T.ASAO
#			self._test = ''
#
#			for title in self._titles:
#				id = UcfUtil.getHashStr(self._hash_title_to_id, title)
#
#				title_ex = self._titles_ex[self._hash_title_idx[title]]
#				element = entry.custom[title_ex]
#				if element != None:
#					vo[id] = unicode(UcfUtil.nvl(element.text))
#				else:
#					vo[id] = unicode('')
#
			for key in entry.custom:
				# key:SS側の内部ID
				# title:変換前のタイトル
				# value:値
				# id:フィールドID

				# スプレッドシートに予期しないカラムがあってもエラーしないように修正 2010/01/29 T.ASAO
#				title = self._titles[self._hash_title_idx_ex[key]]
				if key in self._hash_title_idx_ex:
					title = self._titles[self._hash_title_idx_ex[key]]
					id = UcfUtil.getHashStr(self._hash_title_to_id, title)
					if id != '':
						value = entry.custom[key].text
						vo[id] = str(UcfUtil.nvl(value))

			self._current_idx += 1
			self.__data_source_index += 1

			self._current_vo = vo
			self._current_entry = entry
			return vo != None

		# 現在のrecordsetを最後まで回したら次のRecordSetの取得を試みる
		elif self.__is_read_all_results and self._data_source != None and self.__service != None:
			new_feed = getNextListFeed(self.__service, self._data_source)
			if new_feed != None:
				self.__refleshSelect(new_feed)
				return self.read()

		return False


	#+++++++++++++++++++++++++++++++++++++++
	#+++ スプレッドシートタイトルに関する各種情報を作成して返す
	#+++++++++++++++++++++++++++++++++++++++
	def getSpreadSheetTitleInfo(self, service, spreadsheet_key, worksheet_id):
		u'''
		TITLE:スプレッドシートタイトルに関する各種情報を作成して返す
		PARAMETER:
			service:
			spreadsheet_key:
			worksheet_id:
		RETURN:

		SET
			_titles:タイトル一覧ハッシュ（スプレッドシートに表示されているものそのもの）
			_titles_ex:内部ID一覧ハッシュ（スプレッドシートが内部で保持しているID）
			_hash_title_idx:ハッシュ.key…スプレッドシートタイトル value…カラムのインデックス（0～）
			_hash_title_idx_ex:ハッシュ.key…スプレッドシート内部ID value…カラムのインデックス（0～）
			_hash_title_to_id:ハッシュ. key…スプレッドシートタイトル value…フィールドID
			_hash_id_to_title:ハッシュ. key…フィールドID value…スプレッドシートタイトル
		'''

		# タイトル一覧取得（変換前.表示されたままのやつ）
		self._titles = getWorksheetTitleList(service, spreadsheet_key, worksheet_id, no_title_exchange=True)
		# タイトル一覧取得（変換後.内部保持ＩＤ）
		self._titles_ex = convertStringsToWorksheetTitleList(self._titles)

		# 外部ＩＤをキーとして何番目にあるかのハッシュを作成
		self._hash_title_idx = {}
		i = 0
		for title in self._titles:
			self._hash_title_idx[title] = i
			i += 1
		# 内部ＩＤをキーとして何番目にあるかのハッシュを作成
		self._hash_title_idx_ex = {}
		i = 0
		for title in self._titles_ex:
			self._hash_title_idx_ex[title] = i
			i += 1

		# フィールド定義を取得
		lstFields = self._config.getFieldDefine()

		self._hash_title_to_id = {}
		self._hash_id_to_title = {}
		for item in lstFields:
			id = item.getAttribute('id')
			title = item.getAttribute('title')
			if title != '' and id != '':
				self._hash_id_to_title[id] = title
				self._hash_title_to_id[title] = id

#		return titles, titles_ex, hash_title_idx, hash_title_idx_ex, hash_title_to_id, hash_id_to_title

	#+++++++++++++++++++++++++++++++++++++++
	#+++ スプレッドシートListFeedクエリーの１Where句を生成
	#+++++++++++++++++++++++++++++++++++++++
	def createOneSpreadsheetWhereQuery(self, key, value, eq='E'):
		u'''
		TITLE:スプレッドシートListFeedクエリーの１Where句を生成
		PARAMETER:
			key:スプレッドシート内部ＩＤ
			value:検索値（空はＮＧ）
			eq:Equation：E…＝（デフォルト） LT…＜　GT…＞
		RETURN:Where句文字列
		'''
		if eq == 'E':
			query = key + '=' + value
		elif eq == 'LLK':
			query = '(' + key + '>=' + value + ' and ' + key + '<' + ''.join(value + u'\uFFE0') + ')'	# FFFDだとUTF-8エンコーディングがエラーするので
		elif eq == 'LT':
			query = key + '<' + value
		elif eq == 'LTE':
			query = key + '<=' + value
		elif eq == 'GT':
			query = key + '>' + value
		elif eq == 'GTE':
			query = key + '>=' + value
		else:
			query = key + '=' + value

		return query

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 本当に正しいレコードかの整合性チェック（フルテキスト検索の結果用）
	#+++++++++++++++++++++++++++++++++++++++
	def checkOneRecord(self, vo, key, v, eq='E'):
		u'''
		TITLE:本当に正しいレコードかの整合性チェック（フルテキスト検索の結果用）
		PARAMETER:
			vo:データVo
			key:フィールドＩＤ
			value:検索値
			eq:Equation：E…＝（デフォルト） LT…＜　GT…＞
		RETURN:有効レコード=True
		'''

		if eq == 'E':
			if UcfUtil.nvl(vo[key]).lower() != v.lower():
				return False
		elif eq == 'LLK':
			if not UcfUtil.nvl(vo[key]).lower().startswith(v.lower()):
				return False
		elif eq == 'LT':
			if UcfUtil.nvl(vo[key]) >= v:
				return False
		elif eq == 'LTE':
			if UcfUtil.nvl(vo[key]) > v:
				return False
		elif eq == 'GT':
			if UcfUtil.nvl(vo[key]) <= v:
				return False
		elif eq == 'GTE':
			if UcfUtil.nvl(vo[key]) < v:
				return False
		else:
			if UcfUtil.nvl(vo[key]).lower() != v.lower():
				return False

		return True

	#+++++++++++++++++++++++++++++++++++++++
	#+++ スプレッドシートから１件エントリを取得
	#+++++++++++++++++++++++++++++++++++++++
	def getEntryByListFeed(self, service, feed):
		u'''
		TITLE:スプレッドシートから１件エントリを取得
		ABSTRACT:存在しなければ例外発生
		PARAMETER:
			wheres:条件リスト
		RETURN:entry１件
		'''

		# List型で取得してみる
		self.beginSelect(feed, service=service)
		entry = None
		while self.read():
			entry = self.getCurrentData()
			break
		self.closeSelect()

		return entry
	
