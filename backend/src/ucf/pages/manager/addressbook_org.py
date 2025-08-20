# coding: utf-8

# import os,sys
# import wsgiref.handlers, cgi
# from google.appengine.ext import webapp
# from google.appengine.ext.webapp import template
from google.appengine.api import memcache

from ucf.config.ucfconfig import *
from ucf.utils.ucfutil import *
from ucf.utils.ucfxml import *
from ucf.utils.helpers import *
from ucf.utils.validates import *
from ucf.utils.models  import *
from ucf.tablehelper.addressbook_org import *

from ucf.gdata.spreadsheet.util import *

############################################################
## 組織アドレス帳：ページヘルパー
############################################################
class AddressBookPageHelper(ManageHelper):
	_config = None

	def __init__(self):
		# 親のコンストラクタをコール
		ManageHelper.__init__(self)

	def onLoad(self):
		u'''  '''
		param_file_name = 'manager/addressbook/org/config.xml'
		param_file_path = self.getParamFilePath(param_file_name)

		self._config = AddressBookConfig(param_file_path)

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 組織情報ＸＭＬを作成
	#+++++++++++++++++++++++++++++++++++++++
	def createOrgXml(self):
		tablehelper_config = AddressBookTableHelperConfig(self.getParamFilePath(AddressBookTableHelperConfig._config_file_path))
		table_helper = AddressBookTableHelper.createInstance(AddressBookTableHelperConfig(self.getParamFilePath(AddressBookTableHelperConfig._config_file_path)))
		spreadsheet_key = tablehelper_config.getSpreadsheetID()
		worksheet_name = tablehelper_config.getWorksheetName()

		cache_key = AddressBookConfig.CACHEKEY_PREFIX_ORG_XML + spreadsheet_key + worksheet_name

		org_tree = memcache.get(cache_key)

#		org_tree = None

		# キャッシュになければデータソース（スプレッドシート）をなめて作成
		if org_tree == None:
			# 設定ファイルから組織項目情報を取得
			nodOrgFields = self._config.getOrgFields()

			sconds = {}
#			table_helper.beginGetListByCond(sconds)
			table_helper.beginGetListByCond(sconds=sconds, start_index=1, max_results=200, is_read_all_results=True)

			# 全組織ＸＭＬを作成
			root = UcfXml.createNode('Ucf')
			_SEP_ORG_ID = '!"#$%&'
			hash_exist = {}	# 組織存在判定用ハッシュ

			dummy_category_id = 0
			while table_helper.read():
				vo = table_helper.getCurrentVo()
				current_org_level = 0	
				parent = root
				check_key = ''

				for item in nodOrgFields:
					item_id = item.getAttribute('id')
#						item_disp_name = item.getAttribute('disp_name')
					# 現在の組織階層（1～） 
					current_org_level += 1
					# カテゴリＩＤ
					org_id = UcfUtil.getHashStr(vo, item_id)
					# カテゴリ名称（TODO 同じ）
					org_name = org_id

					# 空組織名があった時点でその下は無視
					if org_id == '':
						break

#					# TODO テスト用に組織ＩＤを上書き(全角ＩＤだとエラーするので.取得順、データが変わらなければ問題ないはず.キャッシュしてるし)
#					org_id = UcfUtil.nvl(dummy_category_id)
					dummy_category_id += 1

					# 組織名称をノードとして作成
					# まず存在チェック
					check_key = (check_key + _SEP_ORG_ID + org_id) if current_org_level > 1 else org_id
					# 該当の組織が既に存在すればスルー
					if hash_exist.has_key(check_key):
						current = hash_exist[check_key]
					# 存在しなければ作成(親の下に)
					else:
						current = UcfXml.createNode("Org")
						current.setAttribute('id', org_id)
						current.setAttribute('name', org_name)
						parent.append(current)
						hash_exist[check_key] = current
					parent = current

			org_tree = root
			# キャッシュにセット
			memcache.add(cache_key, org_tree, 3600)	# ６０分キャッシュ

		return org_tree


############################################################
## 組織アドレス帳：設定ファイル用クラス
############################################################
class AddressBookConfig(UcfConfig):
#	PREFIX_SCOND_ORG = 'sk_org_'
	CACHEKEY_PREFIX_ADDRESSBOOK_ORG = 'CACHEKEY_PREFIX_ADDRESSBOOK_ORG'
	CACHEKEY_PREFIX_ORG_XML = 'CACHEKEY_PREFIX_ORG_XML'

	_crypto_key = UcfConfig.CRYPTO_KEY

	MASTERINFO_SPREADSHEET_ACCOUNT = 'Spreadsheet/@account'
	MASTERINFO_SPREADSHEET_PASSWORD = 'Spreadsheet/@password'
	MASTERINFO_SPREADSHEET_KEY = 'Spreadsheet/@key'
	MASTERINFO_WORKSHEET_NAME = 'Spreadsheet/@worksheet_name'
	GMAILURL = 'Config/GMailURL'

	_xmlConfig = None
	_config_info = None

	def __init__(self, param_file_path):
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

	def getListFields(self):
		u''' 設定ファイルから一覧表示項目情報を取得 '''
		return self._xmlConfig.selectNodes('ListFields/Item')

	def getOrgFields(self):
		u''' 設定ファイルから組織として扱う項目情報を取得 '''
		return self._xmlConfig.selectNodes('OrgFields/Item')

	def getGMailMailAddressID(self):
		u''' 設定ファイルからGMAILメールアドレスフィールドを取得 '''
		result = ''
		item = self._xmlConfig.selectSingleNode('GMailFields/MailAddress/Item')
		if item != None:
			result = item.getAttribute('id')
		return result
	
	def getGMailNameIDs(self):
		u''' 設定ファイルからGMAIL名前フィールド一覧を取得 '''
		result = []
		for item in self._xmlConfig.selectNodes('GMailFields/Name/Item'):
			result.append(item.getAttribute('id'))
		return result
	
	def getGMailMailAddressFields(self):
		u''' 設定ファイルからGMAILメールアドレス項目情報を取得 '''
		return self._xmlConfig.selectNodes('GMailFields/MailAddress/Item')

	def getGMailURL(self):
		u''' 設定ファイルの値を取得：GMAILURL '''
		return UcfUtil.getHashStr(self._config_info, self.GMAILURL)

