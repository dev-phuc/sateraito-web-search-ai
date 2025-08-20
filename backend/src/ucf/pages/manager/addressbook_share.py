# coding: utf-8

# import os,sys
# import wsgiref.handlers, cgi
# from google.appengine.ext import webapp
# from google.appengine.ext.webapp import template

from ucf.pages.manager.addressbook_share import *
from ucf.tablehelper.addressbook_share import *

# from ucf.config.ucfconfig import *
# from ucf.utils.ucfutil import *
# from ucf.utils.ucfxml import *
from ucf.utils.helpers import *
from ucf.utils.validates import *
from ucf.utils.models  import *

from ucf.gdata.spreadsheet.util import *

############################################################
## 共有アドレス帳：ページヘルパー
############################################################
class AddressBookSharePageHelper(ManageHelper):

	_config = None

	def __init__(self):
		# 親のコンストラクタをコール
		ManageHelper.__init__(self)

	def onLoad(self):
		u'''  '''
		param_file_name = 'manager/addressbook/share/config.xml'
		param_file_path = self.getParamFilePath(param_file_name)

		self._config = AddressBookShareConfig(param_file_path)

############################################################
## バリデーションチェッククラス 
############################################################
class AddressBookShareValidator(BaseValidator):
	u'''入力チェッククラス'''

	def validate(self, helper, vo):
		
		# 初期化
		self.init()

		unique_id = UcfUtil.getHashStr(vo, 'unique_id')

		check_name = ''
		check_key = ''
		check_value = ''

		cmd_prefix_length = len(helper._config._cmd_prefix)

		for k,v in vo.iteritems():
			# AutoCmdを処理
			if k.startswith(helper._config._cmd_prefix) and len(k) > cmd_prefix_length:

				cmd = v
				check_key = UcfUtil.subString(k, cmd_prefix_length)
				check_name = UcfUtil.getHashStr(vo, helper._config._dispname_prefix + check_key)
				check_value = UcfUtil.getHashStr(vo, check_key)
	
				self.applicateAutoCmd(check_value, check_key, check_name, cmd)

		#TODO unique_idがスプレッドシート検索に耐えられる値かどうかを判定（先頭数字ＮＧ、記号ＮＧ、全角数字ＮＧ....）

		# 重複チェック
		if self.total_count == 0:
			# 新規の場合のみチェック（更新時はunique_idは更新させない）
			if self.edit_type == UcfConfig.EDIT_TYPE_NEW:
				table_helper = AddressBookShareTableHelper.createInstance(AddressBookShareTableHelperConfig(helper.getParamFilePath(AddressBookShareTableHelperConfig._config_file_path)))
				vo_check = table_helper.getDataByUniqueID(unique_id)
				if vo_check != None:
					self.appendValidate('unique_id', UcfMessage.getMessage(UcfMessage.MSG_VC_ALREADY_EXIST, ()))

############################################################
## ビューヘルパー
############################################################
class AddressBookShareViewHelper(ViewHelper):

	def applicate(self, vo, helper):
		voVH = {}

		# ここで表示用変換を必要に応じて行うが、原則Djangoテンプレートのフィルタ機能を使う
		for k,v in vo.iteritems():
			voVH[k] = v	

		return voVH


############################################################
## 共有アドレス帳：設定ファイル用クラス
############################################################
class AddressBookShareConfig(UcfConfig):
#	PREFIX_SCOND_ORG = 'sk_org_'

	_cmd_prefix = "cmd_"
	_dispname_prefix = "dn_"

	CACHEKEY_PREFIX_ADDRESSBOOK_ORG = 'CACHEKEY_PREFIX_ADDRESSBOOK_SHARE_ORG'
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

