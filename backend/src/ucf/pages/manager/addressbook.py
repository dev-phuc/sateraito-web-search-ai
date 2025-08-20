# coding: utf-8

# import os,sys
# import wsgiref.handlers, cgi
# from google.appengine.ext import webapp
# from google.appengine.ext.webapp import template
#
# from ucf.config.ucfconfig import *
# from ucf.utils.ucfutil import *
# from ucf.utils.ucfxml import *
from ucf.utils.helpers import *
# from ucf.utils.validates import *
from ucf.utils.models  import *

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
		param_file_name = 'manager/addressbook/config.xml'
		param_file_path = self.getParamFilePath(param_file_name)

		self._config = AddressBookConfig(param_file_path)


############################################################
## 組織アドレス帳：設定ファイル用クラス
############################################################
class AddressBookConfig(UcfConfig):
#	PREFIX_SCOND_ORG = 'sk_org_'
	CACHEKEY_PREFIX_ADDRESSBOOK_ORG = 'CACHEKEY_PREFIX_ADDRESSBOOK_ORG'
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

