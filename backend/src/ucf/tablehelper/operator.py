# coding: utf-8

# import os,sys,Cookie
# from google.appengine.api import users
# from google.appengine.ext import webapp
# from google.appengine.ext.webapp import template
#
# from ucf.utils.ucfutil import *
# from ucf.config.ucfconfig import *
# from ucf.config.ucfmessage import *
# from ucf.utils.ucfxml import *
# from ucf.utils.models import *
from ucf.utils.tablehelper import *
from ucf.gdata.spreadsheet.util import *



############################################################
## UcfMDLOPeratorへのアクセスを管理するクラス
############################################################
class OperatorTableHelper(TableHelper):
	
	#+++++++++++++++++++++++++++++++++++++++
	#+++ コンストラクタ
	#+++++++++++++++++++++++++++++++++++++++
	def __init__(self):
		TableHelper.__init__(self)
		pass

	def createInstance(config):
		u'''インスタンスを作成
				※ここでどちらのインスタンスを返すかでソースを切り替える
				※シングルトンパターンでも良いかもしれないが、リスト関連のやり方によるので保留
				config:TableHelperConfig
		 '''
		return OperatorBigTableTableHelper(config)
#		return OperatorSpreadsheetTableHelper(config)
	createInstance = staticmethod(createInstance)



############################################################
## スプレッドシート用
############################################################
class OperatorSpreadsheetTableHelper(OperatorTableHelper,SpreadsheetTableHelper):

	#+++++++++++++++++++++++++++++++++++++++
	#+++ コンストラクタ
	#+++++++++++++++++++++++++++++++++++++++
	def __init__(self, config):
		OperatorTableHelper.__init__(self)
		SpreadsheetTableHelper.__init__(self, config)

	def getByOperatorID(self, dept_id, operator_id):
		u''' オペレータＩＤで有効なオペレータを取得（ログイン用） '''

		# TODO 毎回XMLから取得するのか？？？

		# 各種値を取得
		account, password, spreadsheet_key, worksheet_name = self._config.getSpreadsheetAuthInfo()
#		account = self._config.getAccount()
#		password = self._config.getPassword()
#		spreadsheet_key = self._config.getSpreadsheetID()
#		worksheet_name = self._config.getWorksheetName()
#		worksheet_id = None

		# ワークシートの取得
#		service = getSpreadsheetsService(account, password, self.getRootPath())	# TODO getRootPathのようなデータソースに依存するパラメータをどのように渡すか
		service = getSpreadsheetsService(account, password, UcfUtil.guid())	
		worksheet_id = getWorksheetIdByName(service, spreadsheet_key, worksheet_name)

		#ワークシートが存在していなければエラー
		if not worksheet_id:
			raise Exception([u'failed get worksheet by name, not exist worksheet', spreadsheet_key, worksheet_name])
			return

		# タイトルなどのスプレッドシートに関するデータを取得
		self.getSpreadSheetTitleInfo(service, spreadsheet_key, worksheet_id)

		# データ取得（スプレッドシート用のクエリーをベタで作成）
		# フルテキスト検索に変更 2010/02/23 T.ASAO
		# WHERE句
#		wheres = []
#
#		title_ex = self._titles_ex[self._hash_title_idx[UcfUtil.getHashStr(self._hash_id_to_title, 'operator_id')]]	# Spreadsheetの内部IDに変換
#		wheres.append(self.createOneSpreadsheetWhereQuery(title_ex, operator_id))
#		title_ex = self._titles_ex[self._hash_title_idx[UcfUtil.getHashStr(self._hash_id_to_title, 'del_flag')]]	# Spreadsheetの内部IDに変換
#		wheres.append(self.createOneSpreadsheetWhereQuery(title_ex, 'ACTIVE'))# TODO 決めうち...
#		title_ex = self._titles_ex[self._hash_title_idx[UcfUtil.getHashStr(self._hash_id_to_title, 'dept_id')]]	# Spreadsheetの内部IDに変換
#		wheres.append(self.createOneSpreadsheetWhereQuery(title_ex, dept_id))
#
#		query = createListQuery(wheres)
#		feed = getListFeedByCond(service, spreadsheet_key, worksheet_id, query.encode('utf-8'))	# utf-8固定

		fulltext_values = []
		fulltext_values.append(operator_id)
		fulltext_values.append(dept_id)

		feed = getListFeedByFullText(service, spreadsheet_key, worksheet_id, fulltext_values)

		if not isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
			raise Exception([u'not SpreadsheetsListFeed instance.', spreadsheet_key, worksheet_name])
			return

		# List型で取得してみる
		self.beginSelect(feed)
		result = []
		while self.read():

			vo = self.getCurrentVo()

			# フルテキスト検索に伴い値の整合性チェック 2010/02/23 T.ASAO
			if UcfUtil.nvl(vo['operator_id']).lower() != operator_id.lower():
				continue
			if UcfUtil.nvl(vo['dept_id']).lower() != dept_id.lower():
				continue
			if UcfUtil.nvl(vo['del_flag']).lower() != 'ACTIVE'.lower():	# TODO 決めうち
				continue

			result.append(vo)
		self.closeSelect()
		u'''
		result = []
		for i, entry in enumerate(feed.entry):
			vo = {}
			for key in entry.custom:
				# key:SS側の内部ID
				# title:変換前のタイトル
				# value:値
				# id:フィールドID

				title = self._titles[self._hash_title_idx_ex[key]]
				id = UcfUtil.getHashStr(self._hash_title_to_id, title)
				if id != '':
					value = entry.custom[key].text
					vo[id] = unicode(value)
			result.append(vo)

		'''
		return result
	
############################################################
## BigTable用
############################################################
class OperatorBigTableTableHelper(OperatorTableHelper,BigTableTableHelper):

	#+++++++++++++++++++++++++++++++++++++++
	#+++ コンストラクタ
	#+++++++++++++++++++++++++++++++++++++++
	def __init__(self, config):
		OperatorTableHelper.__init__(self)
		BigTableTableHelper.__init__(self, config)

	def getByOperatorID(self, dept_id, operator_id):
		u'''
		TITLE:オペレータＩＤで有効なオペレータを取得（ログイン用）
		PARAMETER:
			dept_id:ログイン店舗ID
			operator_id:ログインオペレータId
		RETURN:Vo
		'''

		gql = ""
		wheres = []
		wheres.append("dept_id='" + UcfUtil.escapeGql(dept_id) + "'")
		wheres.append("del_flag=''")
		wheres.append("operator_id='" + UcfUtil.escapeGql(operator_id) + "'")

		gql += UcfUtil.getToGqlWhereQuery(wheres)

		models = UCFMDLOperator.gql(gql)

		# List型で取得してみる
		self.beginSelect(models)
		result = []
		while self.read():
			result.append(self.getCurrentVo())
		self.closeSelect()

		u'''
		result = []
		for model in models:
			result.append(model.exchangeVo())
		'''
		return result

############################################################
## オペレータ：設定ファイル用クラス
############################################################
class OperatorTableHelperConfig(TableHelperConfig):

	_config_file_path = 'manager/operator/tablehelper_config.xml'

