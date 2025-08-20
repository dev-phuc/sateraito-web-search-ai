# coding: utf-8
# from flask import Flask, Response, render_template, request, make_response, session, redirect, after_this_request, jsonify
from flask import render_template, request, make_response, redirect
# import os
# import os,sys,Cookie
# import sateraito_logger as logging
# from google.appengine.api import users

# デフォルトの文字コードの設定 2011/05/31
# if not hasattr(sys, "setdefaultencoding"):
# 	stdin = sys.stdin
# 	stdout = sys.stdout
# 	reload(sys)
# 	sys.setdefaultencoding('utf-8')
# 	sys.stdin = stdin
# 	sys.stdout = stdout

# from django.conf import settings # FILE文字コードの変更に使用 2011/05/31

# from google.appengine.api import users
# from google.appengine.ext import webapp
# from google.appengine.ext.webapp import template

# 管理画面のextends対策【../～.htmlを呼ぶ為】2011/05/31
#from ucf.loader.customtemplateloader import CustomTemplateLoader

# from ucf.utils.ucfutil import *
# from ucf.config.ucfconfig import *
# from ucf.config.ucfmessage import *
# from ucf.utils.models  import *
# from ucf.utils.ucfxml import *

from ucf.tablehelper.operator import *	# authLoginで使用
import sateraito_page

#from appengine_utilities import sessions

############################################################
## ヘルパー（共通）
############################################################
class Helper(sateraito_page._BasePage):

	# エラーページＵＲＬ（デフォルトから変更したい場合は各Pageにてセット）
	_error_page = None

	# ルートフォルダパス
	_root_folder_path = None

	# キャリアタイプ（PC,MB）
	_career_type = None
	# キャリア（PC,DOCOMO,AU,SOFTBANK）
	_career = None

	# ページタイプ
	_page_type = None

	# ページタイトル
	_page_title = None
	# メニューＩＤ
	_menu_id = None
#	# ページＩＤ
#	_page_id = None

	# Requestタイプ（GET or POST）
	_request_type = None

	def __init__(self):
#		# 親のコンストラクタをコール
#		webapp.RequestHandler.__init__(self)

		# self.sess = sessions

		# クラス変数の初期化（コンストラクタで明示的に行わないとインスタンス生成時に初期化されないため）
		# エラーページＵＲＬ
		self._error_page = ''

		# ルートフォルダパス
		self._root_folder_path = ''

		# ページタイプ
		self._page_type = ''

		# ページタイトル
		self._page_title = ''
		# メニューＩＤ
		self._menu_id = ''
#		# ページＩＤ
#		self._page_id = ''
		# Requestタイプ（GET or POST）
		self._request_type = ''

		# キャリアタイプ（PC,MB）
		self._career_type = ''
		# キャリア（PC,DOCOMO,AU,SOFTBANK）
		self._career = ''


	def init(self):
		u''' 抽象メソッドイメージ '''
		pass

	def onLoad(self):
		u''' オンロード（抽象メソッドイメージ）
			Helperを継承する一番子共のクラスで必要に応じてオーバーロードするためのメソッド
			先頭で初期化しておきたい処理などに使用
		 '''
		pass

	def render(self, template):
#		return os.path.join(os.path.dirname(__file__), template)
#		return os.path.join(os.getcwd(), template)
		return os.path.join(self.getAppRootFolderPath(), template)

	def getRootPath(self):
		u'''ルートパスを取得'''
		return self._root_folder_path

	def getAppRootFolderPath(self):
		u'''アプリケーションルートのフォルダパスを算出'''
		# 現在のURLを取得（例：http://xxx.domain/manager/xxxx?aaa=bb）
		current_url = request.url.lower()
		# 現在のＵＲＬの?より前を取得（例：http://xxx.domain/manager/xxxx）
		quest_index = current_url.find('?')
		if quest_index >= 0:
			current_url = UcfUtil.subString(current_url, 0, quest_index)
		# 現在のＵＲＬのドメイン部分を除く（例：manager/xxxx、manager/）
		if current_url.startswith("http://"):
			current_url = UcfUtil.subString(current_url, len("http://"))
		elif current_url.startswith("https://"):
			current_url = UcfUtil.subString(current_url, len("https://"))
		slash_index = current_url.find('/')
		if slash_index >= 0:
			current_url = UcfUtil.subString(current_url, slash_index)
		# 現在のＵＲＬのフォルダ部分のパスを取得（例：manager）
		slash_index = current_url.rfind('/')
		if slash_index >= 0:
			current_url = UcfUtil.subString(current_url, 0, slash_index)
		# スラッシュをバックスラッシュに変換
		current_url = current_url.replace('/', '\\').strip('\\')

		# 現在の作業ディレクトリパスを取得（例：c:\temp\webroot\manager）
		cwd_path = os.getcwd().lower().strip('/').strip('\\')
		
		# 現在の作業ディレクトリパスからルートパスを算出
		url_length = len(cwd_path) - len(current_url)
		result = UcfUtil.subString(cwd_path, 0, url_length)
		# 標準化
		result = os.path.normpath(result)

		# unix 環境の場合は、先頭に/をつける
		if result.find(':') < 0:
			result = '/' + result
		return result

	def getTemplateFolderPath(self):
		u'''テンプレートフォルダパスを取得'''
		return os.path.join(self.getAppRootFolderPath(), UcfConfig.TEMPLATES_FOLDER_PATH)

	def getTemplateFilePath(self, filename):
		u'''テンプレートファイルパスを取得'''
		return os.path.join(self.getTemplateFolderPath(), filename)

	def getLocalTemplateFolderPath(self):
		u'''ローカルテンプレートフォルダパスを取得(絶対パス)'''
		return os.path.normpath(os.path.join(os.getcwd(), UcfConfig.TEMPLATES_FOLDER_PATH))

	def getLocalTemplateFilePath(self, filename):
		u'''ローカルテンプレートファイルパスを取得(相対パス)'''
		return os.path.normpath(os.path.join(UcfConfig.TEMPLATES_FOLDER_PATH, filename))

	def getParamFolderPath(self):
		u'''パラメーターフォルダパスを取得'''
		return os.path.normpath(os.path.join(self.getAppRootFolderPath(), UcfConfig.PARAM_FOLDER_PATH))

	def getParamFilePath(self, filename):
		u'''パラメーターファイルパスを取得'''
		return os.path.normpath(os.path.join(self.getParamFolderPath(), filename))

	def getLocalParamFolderPath(self):
		u'''ローカルパラメーターフォルダパスを取得(絶対パス)'''
		return os.path.normpath(os.path.join(os.getcwd(), UcfConfig.PARAM_FOLDER_PATH))

	def getLocalParamFilePath(self, filename):
		u'''ローカルパラメーターファイルパスを取得(相対パス)'''
		return os.path.normpath(os.path.join(UcfConfig.PARAM_FOLDER_PATH, filename))

	def getRequestTopURL(self):
		u''' アクセスURLのルートURL（http://xxxxxxxx.com まで）を取得 '''
		current_url = request.url
		current_url_lower = current_url.lower()

		top_url = ''
		# ＵＲＬのドメイン部分を除く（例：manager/xxxx、manager/）
		if current_url_lower.startswith("http://"):
			part_url = UcfUtil.subString(current_url, len("http://"))
			top_url = 'http://' + part_url.split('/')[0]
		elif current_url_lower.startswith("https://"):
			part_url = UcfUtil.subString(current_url, len("https://"))
			top_url = 'https://' + part_url.split('/')[0]
		return top_url


	def judgeTargetCareer(self):
		u'''UserAgentからキャリアタイプを自動判定'''
		#環境変数の取得
		strAgent =  self.getUserAgent().lower()
		strJphone = self.getServerVariables("HTTP_X_JPHONE_MSNAME").lower()
		strAccept = self.getServerVariables("HTTP_ACCEPT").lower()

		# ユーザエージェント判定
		strTargetCareer = None
		strTargetCareerType = None

		# SoftBank
		if strJphone!='' or strAgent.find('j-phone')>=0 or strAgent.find('softbank')>=0 or strAgent.find('vodafone')>=0 or strAgent.find('mot-')>=0:
			strTargetCareer = UcfConfig.VALUE_CAREER_SOFTBANK
			strTargetCareerType = UcfConfig.VALUE_CAREER_TYPE_MOBILE
		# au
		elif strAgent.find('kddi')>=0 or strAgent.find('up.browser')>=0 or strAccept.find('hdml')>=0:
			strTargetCareer = UcfConfig.VALUE_CAREER_EZWEB
			strTargetCareerType = UcfConfig.VALUE_CAREER_TYPE_MOBILE
		# Docomo
		elif strAgent.find('docomo')>=0:
			strTargetCareer = UcfConfig.VALUE_CAREER_IMODE
			strTargetCareerType = UcfConfig.VALUE_CAREER_TYPE_MOBILE
		#デフォルトは、PC
		else:
			strTargetCareer = UcfConfig.VALUE_CAREER_PC
			strTargetCareerType = UcfConfig.VALUE_CAREER_TYPE_PC

		#内部変数にセット
		self._career = strTargetCareer
		self._career_type = strTargetCareerType

		return strTargetCareer, strTargetCareerType;

	def getPageID(self):
		u'''ページＩＤ的なものを取得'''
		current_url = request.url.lower()
		# 現在のＵＲＬの?より前を取得（例：http://xxx.domain/manager/xxxx）
		quest_index = current_url.find('?')
		if quest_index >= 0:
			current_url = UcfUtil.subString(current_url, 0, quest_index)
		# 現在のＵＲＬのドメイン部分を除く（例：manager/xxxx、manager/）
		if current_url.startswith("http://"):
			current_url = UcfUtil.subString(current_url, len("http://"))
		elif current_url.startswith("https://"):
			current_url = UcfUtil.subString(current_url, len("https://"))
		slash_index = current_url.find('/')
		if slash_index >= 0:
			current_url = UcfUtil.subString(current_url, slash_index)
		return current_url

	def get(self):
		# Django1.2バージョンアップ時、FILE文字コード変更 2011/05/31
		# settings.FILE_CHARSET = 'Shift_JIS'
		# settings.FILE_CHARSET = UcfConfig.FILE_CHARSET
		self.request.charset = UcfConfig.ENCODING
		self.response.charset = UcfConfig.ENCODING
		self._request_type = UcfConfig.REQUEST_TYPE_GET
		self.init()
		self.onLoad()
		self.processOfRequest()

	def post(self):
		# Django1.2バージョンアップ時、FILE文字コード変更 2011/05/31
		# settings.FILE_CHARSET = 'Shift_JIS'
		# settings.FILE_CHARSET = UcfConfig.FILE_CHARSET
		self.request.charset = UcfConfig.ENCODING
		self.response.charset = UcfConfig.ENCODING
		self._request_type = UcfConfig.REQUEST_TYPE_POST
		self.init()
		self.onLoad()
		self.processOfRequest()

	def processOfRequest(self):
		u'''Requestがきた場合の処理（抽象メソッドイメージ）'''
		pass

	def dispatch(self, template_name, vals, isLocal=False, isAutoSwitchMobileTemplate=False):
		
		# 管理画面のextends対策【../～.htmlを呼ぶ為】2011/05/31
		# views_path = os.path.join(self.getTemplateFolderPath(),'manager')
		# 'manager' を外した状態で動作できるよう変更 2011/06/03
		views_path = self.getTemplateFolderPath()

		# 
	#	template_dir = views_path
	#	if not template_name.rfind('/') == -1:
	#		template_name = os.path.join(template_dir, template_name)
	#		template_dir = template_name[:template_name.rfind('/')]

		# loader が３つある為、ファイルが見つからなかった場合に捜査件数が膨大になる→エラz
		# settings.TEMPLATE_LOADERS = (
		# 	 'django.template.loaders.filesystem.load_template_source'
		# 	,'django.template.loaders.app_directories.load_template_source'
		# 	,('ucf.loader.customtemplateloader.CustomTemplateLoader', views_path)
		# )

		# template_dirs = settings.TEMPLATE_DIRS
		#for template_dir in template_dirs:
		#	logging.info(template_dir)
		#	pass

		# モバイル用テンプレート自動切り替え
		if isAutoSwitchMobileTemplate and self._career_type==UcfConfig.VALUE_CAREER_TYPE_MOBILE:
			template_path = os.path.join(UcfConfig.MOBILE_TEMPLATES_FOLDER_NAME, template_name)
		else:
			template_path = template_name

		#logging.info(template_path)
		#logging.info(self.render(template_path))

		# レンダリング

		# 文字コード指定：これをやらないとmetaタグだけでは文字コードをブラウザが認識してくれないため。
		#self.response.headers['Content-Type'] = 'text/html; charset=' + UcfConfig.ENCODING + ';'
		#encodeとcharsetのマッピング対応 2009.5.20 Osamu Kurihara
		if UcfConfig.ENCODING=='cp932':
			# charset_string='Shift_JIS'
			charset_string = UcfConfig.FILE_CHARSET
		#マッピング定義がないものはUcfConfig.ENCODING
		else:
			charset_string=UcfConfig.ENCODING
		# self.response.headers['Content-Type'] = 'text/html; charset=' + charset_string + ';'
		self.setResponseHeader('Content-Type','text/html; charset=' + charset_string + ';')

		# レンダリング
		if(isLocal):
			# Django1.2バージョンアップ時、日本語の文字化けを防ぐ 2011/05/31
			#self.response.out.write(template.render(self.getLocalTemplateFilePath(template_path), vals))
			# self.response.out.write(template.render(self.getLocalTemplateFilePath(template_path), vals).encode('Shift_JIS'))
			# self.response.out.write(template.render(self.getLocalTemplateFilePath(template_path), vals).encode(UcfConfig.FILE_CHARSET))
			return render_template(self.getLocalTemplateFilePath(template_path),**vals)
		else:
			template_path = os.path.join(UcfConfig.TEMPLATES_FOLDER_PATH, template_path)
			# Django1.2バージョンアップ時、日本語の文字化けを防ぐ 2011/05/31
			#self.response.out.write(template.render(self.render(template_path), vals))
			# self.response.out.write(template.render(self.render(template_path), vals).encode('Shift_JIS'))
			# self.response.out.write(template.render(self.render(template_path), vals).encode(UcfConfig.FILE_CHARSET))
			return render_template(self.render(template_path), **vals)

	def setResponseHeaderForDownload(self, file_name, enc=UcfConfig.ENCODING):
		u'''CSVダウンロード用のレスポンスヘッダを設定'''

		#TODO 本番環境で日本語ファイル名がうまくいかない.エンコードの問題っぽいけど。→今ならいけるかも
		# Content-Disposition にマルチバイト文字を埋め込むときはUTF-8でよさそう Osamu Kurihara
		# self.response.headers['Content-Disposition'] = 'inline;filename=' + unicode(file_name).encode(enc)
		# self.response.headers['Content-Disposition'] = 'inline;filename=' + str(file_name, 'utf-8') .encode(enc)
		# self.response.headers['Content-Type'] = 'application/Octet-Stream-Dummy'
		self.setResponseHeader('Content-Disposition', 'inline;filename=' + str(file_name, 'utf-8') .encode(enc))
		self.setResponseHeader('Content-Type','application/Octet-Stream-Dummy')

	def redirectError(self, error_info):
		u'''エラーページに遷移'''
		self.setSession(UcfConfig.SESSIONKEY_ERROR_INFO, error_info)
#		self.redirect(self.getRootPath() + '/error')
		# logging.info(self._error_page)
		redirect(self.getRootPath() + self._error_page)

	############################################################
	## クッキー
	############################################################
# 	def getCookie(self, name):
# 		u'''クッキーの値を取得（なければNone）'''
# 		cookie = Cookie.SimpleCookie(self.request.headers.get('Cookie'))
# #		cookie = Cookie.SimpleCookie(os.environ.get('HTTP_COOKIE'))
# 		if cookie.get(name) is not None:
# #			return cookie.get(name).value
# 			value = cookie.get(name).value
# 			# 復号化
# 			try:
# 				value = UcfUtil.base64Decode(value)
# 			except:
# 				value = value
#
# 			return value
#
# 		else:
# 			return None
#
# 	def setCookie(self, name, value, expires='31-Dec-2999 23:59:59 GMT', path='/', domain=''):
# 		u'''クッキーの値をセット（期限指定無しの場合は無期限）'''
# 		# 暗号化
# 		try:
# 			value = UcfUtil.base64Encode(value)
#
# 		except:
# 			value = value
# 		self.response.headers.add_header('Set-Cookie', name + '=' + value, expires=expires,path=path,domain=domain)

	############################################################
	## セッション
	############################################################
# 	def setSession(self, key, value):
# 		u'''セッションのセット'''
# #		self.sess[key] = value
# 		# Django1.2バージョンアップ時、エラー画面の日本語の文字化けを防ぐ
# #		self.sess[key] = unicode(value).encode(UcfConfig.ENCODING)
# 		self.sess[key] = str(value, 'utf-8')

	# def getSession(self, key):
	# 	u'''セッションの取得'''
	# 	if key in self.sess:
	# 		return self.sess[key]
	# 	else:
	# 		return None

	############################################################
	## リクエスト値
	############################################################
# 	def getRequest(self, key):
# 		u'''Requestデータの取得'''
# 		# 同一名の複数POSTに対応
# #		value = self.request.get(key)
# 		value = ''
# 		list = self.requestParams.get(key)
# 		i = 0
# 		for v in list:
# 			if i > 0:
# 				value += ','
# 			value += v
# 			i += 1
# 		if value != None:
# 			# ファイルオブジェクトなどをスルーするために変換できないものは無視（微妙？） 2009/11/19 T.ASAO
# 			try:
# 				value = str(value, 'utf-8')	# unicodeに変換
# 			except:
# 				pass
#
# 		return value

	def getRequests(self, key):
		u'''Requestデータの取得(リスト形式で返す)'''
		# 同一名の複数POSTに対応
#		value = self.request.get(key)
		# list = request.arg(key)
		# for v in list:
		# 	v =  str(v, 'utf-8')	# unicodeに変換
		# return list
		return request.arg

	def getUserAgent(self):
		u'''UserAgentの取得'''
		return request.user_agent

	def getRequestHeaders(self, key=None):
		u'''HTTPリクエストヘッダー値の取得'''
		if key:
			return request.headers.get(key, '')
		else:
			#TODO できればCloneして返したい
			return request.headers

	def getServerVariables(self, key):
		u'''サーバー環境変数値Request.environの取得'''
		if key:
			return request.environ.get(key, '')
		else:
			#TODO できればCloneして返したい
			return request.environ

	############################################################
	## その他
	############################################################
	def createVoInfoForList(self, index, vo, vh, isMakeList=False, titles=None):
		u''' 一覧用 '''
		voinfo = UcfVoInfo()
		voinfo.index = index
		voinfo.each_low = index % 2	# 一覧の色分け用
		voinfo.setVo(vo, vh, None, self)

		if isMakeList:
			voList = []
			for title in titles:
				vo_v = UcfUtil.getHashStr(voinfo.vo, title)
				vh_v = UcfUtil.getHashStr(voinfo.voVH, title)
				data = UcfData(title, vh_v, vo_v)
				voList.append(data)

			voinfo.voList = voList

		return voinfo

	def outputErrorLog(self, e):
		u''' 例外をログ出力する （抽象メソッドイメージ）'''
		pass

############################################################
## 管理用：ページヘルパー
############################################################
class ManageHelper(Helper):
#	def __init__(self):
#		# 親のコンストラクタをコール
#		Helper.__init__(self)

	def init(self):
		u'''管理サイト用の初期化'''
		self._root_folder_path = '/manager'
		# エラーページＵＲＬ
		if self._error_page == None or self._error_page == '':
			self._error_page = UcfConfig.URL_MANAGE_ERROR

		#キャリア判定
		self.judgeTargetCareer()

		# ページタイプ
		self._page_type = UcfUtil.nvl(self.getRequest(UcfConfig.REQUESTKEY_PAGETYPE))

	def getAccessAuthority(self, menu_id, edit_type=''):
		u''' 権限チェック '''
		# ログ管理（管理者のみ）
		if menu_id == 'LOG':
			if not self.isAdmin():
				return False
			#ダウンロードはなし
			elif edit_type == UcfConfig.EDIT_TYPE_DOWNLOAD:
				return False
			#新規・編集はなし
			elif edit_type == UcfConfig.EDIT_TYPE_NEW:
				return False
			elif edit_type == UcfConfig.EDIT_TYPE_RENEW:
				return False
			# 削除はなし
			elif edit_type == UcfConfig.EDIT_TYPE_DELETE:
				return False

		# オペレータ管理
		elif menu_id == 'OPERATOR':
			# 新規登録は管理者のみ
			if not self.isAdmin() and edit_type == UcfConfig.EDIT_TYPE_NEW:
				return False
			#ダウンロードはなし
			elif edit_type == UcfConfig.EDIT_TYPE_DOWNLOAD:
				return False

		# ワークフロー設定管理
		elif menu_id == 'WORKFLOWMASTER':
			if not self.isAdmin():
				return False
			#ダウンロードはなし
			elif edit_type == UcfConfig.EDIT_TYPE_DOWNLOAD:
				return False

		# ワークフロー申請管理
		elif menu_id == 'WORKFLOW':
			# ページタイプ=gの場合
			if self._page_type == 'g':
				# 編集はなし
				if edit_type == UcfConfig.EDIT_TYPE_RENEW:
					return False

			# ページタイプ=デフォルトの場合
			else:
				# 新規登録は管理者のみ
				if not self.isAdmin() and edit_type == UcfConfig.EDIT_TYPE_NEW:
					return False

		# ABテスト設定管理
		elif menu_id == 'ABTESTMASTER':
			#ダウンロードはなし
			if edit_type == UcfConfig.EDIT_TYPE_DOWNLOAD:
				return False

		# ABテスト集計管理
		elif menu_id == 'ABTESTCOUNT':
			#新規はなし
			if edit_type == UcfConfig.EDIT_TYPE_NEW:
				return False

		# 会員管理
		elif menu_id == 'CUSTOMER':
			#ダウンロードはなし
			if edit_type == UcfConfig.EDIT_TYPE_DOWNLOAD:
				return False

		# 組織アドレス帳管理
		elif menu_id == 'ADDRESSBOOK':
			# ページタイプ=gの場合
			if self._page_type == 'g':
				# 編集はなし
				if edit_type == UcfConfig.EDIT_TYPE_RENEW:
					return False
				# ダウンロードはなし
				elif edit_type == UcfConfig.EDIT_TYPE_DOWNLOAD:
					return False

			# ページタイプ=デフォルトの場合
			else:
				# 編集はなし
				if edit_type == UcfConfig.EDIT_TYPE_RENEW:
					return False
				#ダウンロードはなし
				elif edit_type == UcfConfig.EDIT_TYPE_DOWNLOAD:
					return False

		# 共有アドレス帳管理
		elif menu_id == 'ADDRESSBOOK_SHARE':
			# ページタイプ=gの場合
			if self._page_type == 'g':
				# ダウンロードはなし
				if edit_type == UcfConfig.EDIT_TYPE_DOWNLOAD:
					return False

			# ページタイプ=デフォルトの場合
			else:
				#ダウンロードはなし
				if edit_type == UcfConfig.EDIT_TYPE_DOWNLOAD:
					return False



		return True

	def checkAccessAuthority(self, menu_id, edit_type='', not_redirect=False):
		u''' 権限チェック '''

		# ログ管理（管理者のみ）
		if self.getAccessAuthority(menu_id, edit_type):
			return True
		else:
			if not not_redirect:
				self.redirectError(UcfMessage.getMessage(UcfMessage.MSG_INVALID_ACCESS_AUTHORITY, ()))
			return False

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 管理用ログイン認証
	#+++ 自動ログインの関係でここに移動
	#+++++++++++++++++++++++++++++++++++++++
	def authLogin(self, isAutoLogin, login_id, password, dept_id, mail_address=''):
		isLogin = False
		valid_vo = None

		login_id = UcfUtil.nvl(login_id)
		dept_id = UcfUtil.nvl(dept_id)
		password = UcfUtil.nvl(password)
		mail_address = UcfUtil.nvl(mail_address)

		if login_id != '' and dept_id != '':
			table_helper = OperatorTableHelper.createInstance(OperatorTableHelperConfig(self.getParamFilePath(OperatorTableHelperConfig._config_file_path)))
			vo_list = table_helper.getByOperatorID(dept_id, login_id)
			for vo_item in vo_list:

				# パスワード暗号化対応 2009/07/29 T.ASAO
#				if UcfUtil.getHashStr(vo_item, 'password') == password:
				if self.decodeLoginPassword(UcfUtil.getHashStr(vo_item, 'password')) == password:
					valid_vo = vo_item
					isLogin = True
				else:
					isLogin = False
				break

		if isLogin:
			# ログインオペレータＩＤをセッションにセット
			self.setSession(UcfConfig.SESSIONKEY_MANAGE_LOGIN_ID, login_id)
			# ログインオペレータ名称をセッションにセット
			self.setSession(UcfConfig.SESSIONKEY_MANAGE_LOGIN_NAME, valid_vo['operator_name'])
			# ログインオペレータ店舗ＩＤをセッションにセット
			self.setSession(UcfConfig.SESSIONKEY_MANAGE_LOGIN_DEPT_ID, dept_id)
			# ログインオペレータ権限をセッションにセット
			self.setSession(UcfConfig.SESSIONKEY_MANAGE_ACCESS_AUTHORITY, valid_vo['access_authority'])
			# ログインオペレータメールアドレスをセッションにセット
			self.setSession(UcfConfig.SESSIONKEY_MANAGE_LOGIN_MAIL_ADDRESS, mail_address)

			# 自動ログイン対応 2009/07/28 T.ASAO
			# クッキーに自動ログインＦとログイン情報をセット
			if isAutoLogin:
				self.setCookieManageLoginInfo(True, login_id, self.encodeCookiePassword(password), dept_id, self.encodeCookiePassword(mail_address))
			# クッキーから自動ログインＦとログイン情報をクリア
			else:
				self.setCookieManageLoginInfo(False, '', '', '','')


		return isLogin, valid_vo
	#+++++++++++++++++++++++++++++++++++++++

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 管理用ログアウト
	#+++++++++++++++++++++++++++++++++++++++
	def logout(self):
		self.setSession(UcfConfig.SESSIONKEY_MANAGE_LOGIN_ID, '')
		self.setSession(UcfConfig.SESSIONKEY_MANAGE_LOGIN_NAME, '')
		self.setSession(UcfConfig.SESSIONKEY_MANAGE_ACCESS_AUTHORITY, '')
		self.setSession(UcfConfig.SESSIONKEY_MANAGE_LOGIN_DEPT_ID, '')
		self.setSession(UcfConfig.SESSIONKEY_MANAGE_LOGIN_MAIL_ADDRESS, '')

		# 動的ログイン関連情報のクリア 2009/07/29 T.ASAO
		self.setCookieManageLoginInfo(False, '', '', '','')
	#+++++++++++++++++++++++++++++++++++++++

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 管理用ログインチェック
	#+++++++++++++++++++++++++++++++++++++++
	def checkLogin(self, add_querys=None, isStaticLogin=False, not_redirect=False):
		u'''
		TITLE:管理用ログインチェック
		PARAMETER:
			add_querys:ログイン画面に追加するクエリーのハッシュ
			isStaticLogin:静的なログインをするならTrue
		'''

		data = self.getLoginOperatorID()
		# OpenID利用時、ログインしているユーザーが異なった場合は再度ログインする。
		# 現状機能の実装が困難な為、保留 2011/02/17
	#	AppsOpenID ,Domain = self.getOperatorConfig()
	#	user = users.get_current_user()
	#	if user:
	#		if user.email() != self.getLoginOperatorMailAddress() and AppsOpenID == 'Active':
	#			return False

		# セッション判定でログインしていなければ
		if data == None or data == '':
			# 自動ログイン判定 2009/07/29 T.ASAO
			# 自動ログインフラグがたっていればクッキーの値によってログインを試みる
			if self.isManageAutoLogin():
				login_id = self.getCookieManageLoginID()
				password = self.getCookieManagePassword()
				dept_id = self.getCookieManageDeptID()
				mail_address = self.getCookieManageMailAddress()

				# ログイン認証
				isLogin, valid_vo = self.authLogin(True, login_id, password, dept_id, mail_address)
			else:
				isLogin = False

			
			if not isLogin:
				if not not_redirect:
					# RURLの取得を行うか判定用 2011/04/08
					rurl_flag = False
					# page_type の取得を行うか判定用 2011/04/08
					page_type_flag = False

					# 静的ログインなら
					url = ''
					if isStaticLogin:
						url = self.getRootPath() + UcfConfig.URL_MANAGE_LOGIN
						# 静的ログインの場合、RURLの追加を行わない
						rurl_flag = True
					# 動的ログインなら
					else:
						# POST なら トップページに戻るように
						if self._request_type == 'POST':
							url = self.getRootPath() + UcfConfig.URL_MANAGE_LOGIN
						# GET ならこのページ自体に戻るように
						else:
							url = self.getRootPath() + UcfConfig.URL_MANAGE_LOGIN
							url = UcfUtil.appendQueryString(url, UcfConfig.REQUESTKEY_RURL, request.url)
							rurl_flag = True


					# クエリーを追加
					if add_querys != None:
						for k,v in add_querys.iteritems():
							url = UcfUtil.appendQueryString(url, k, v)
							if k == UcfConfig.REQUESTKEY_PAGETYPE:
								page_type_flag = True
							if k == UcfConfig.REQUESTKEY_RURL:
								rurl_flag = True
					# ページタイプが存在するとき、クエリーに追加 2011/04/08
					if self._page_type and not page_type_flag:
						url = UcfUtil.appendQueryString(url, UcfConfig.REQUESTKEY_PAGETYPE, self._page_type)
					# RURLを追加していない場合、追加 2011/04/08
					if not rurl_flag:
						# RURLを取得
						strRURL = UcfUtil.nvl(self.getSession(UcfConfig.SESSIONKEY_RURL))
						# RURLが空のとき、リファラから取得
						if strRURL == '' and UcfUtil.nvl(os.environ['HTTP_REFERER']) != '':
							strRURL = UcfUtil.nvl(os.environ['HTTP_REFERER'])
						url = UcfUtil.appendQueryString(url, UcfConfig.REQUESTKEY_RURL, strRURL)

					self.redirect(UcfUtil.exchangeUcfURL(url))

			return isLogin

		else:
			return True
	#+++++++++++++++++++++++++++++++++++++++

	#+++++++++++++++++++++++++++++++++++++++
	#+++ OpenIDのコンフィグを取得
	#+++++++++++++++++++++++++++++++++++++++
	def getOperatorConfig(self):
		u''' OpenIDの Configを読み込み、値を返す。 '''
		file_name = self.getParamFilePath("manager/operator/config.xml")
		if os.path.exists(file_name):
			xmlDoc = UcfXml.load(file_name)

			AppsOpenID = None
			Domain = None

			node = xmlDoc.selectSingleNode('Config//AppsOpenID')
			if node:
				AppsOpenID = node.getInnerText()
			
			node = xmlDoc.selectSingleNode('Config//Domain')
			if node:
				Domain =  node.getInnerText()

			return AppsOpenID, Domain
		else:
			return None , None
	#+++++++++++++++++++++++++++++++++++++++

	#+++++++++++++++++++++++++++++++++++++++
	#+++ デフォルト企業IDのコンフィグを取得
	#+++++++++++++++++++++++++++++++++++++++
	def getDeptConfig(self):
		u''' DeptIDの Configを読み込み、値を返す。 '''
		file_name = self.getParamFilePath("manager/operator/config.xml")
		if os.path.exists(file_name):
			xmlDoc = UcfXml.load(file_name)

			LoginDeptID = None
			DefaultDeptID = None

			node = xmlDoc.selectSingleNode('Config//LoginDeptID')
			if node:
				LoginDeptID =  node.getInnerText()

			node = xmlDoc.selectSingleNode('Config//DefaultDeptID')
			if node:
				DefaultDeptID =  node.getInnerText()

			return LoginDeptID, DefaultDeptID
		else:
			return None ,None

	#+++++++++++++++++++++++++++++++++++++++

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 自動ログインＦを取得
	#+++++++++++++++++++++++++++++++++++++++
	def isManageAutoLogin(self):
		return self.getCookie(UcfConfig.COOKIE_KEY_MANAGE_AUTO_LOGIN) == UcfConfig.VALUE_MANAGE_AUTO_LOGIN

	#+++++++++++++++++++++++++++++++++++++++
	#+++ クッキーログインＩＤを取得
	#+++++++++++++++++++++++++++++++++++++++
	def getCookieManageLoginID(self):
		return self.getCookie(UcfConfig.COOKIE_KEY_MANAGE_LOGIN_ID)

	#+++++++++++++++++++++++++++++++++++++++
	#+++ クッキーログインパスワードを取得
	#+++++++++++++++++++++++++++++++++++++++
	def getCookieManagePassword(self):
		return self.decodeCookiePassword(self.getCookie(UcfConfig.COOKIE_KEY_MANAGE_LOGIN_PASSWORD))

	#+++++++++++++++++++++++++++++++++++++++
	#+++ クッキーログイン店舗ＩＤを取得
	#+++++++++++++++++++++++++++++++++++++++
	def getCookieManageDeptID(self):
		return self.getCookie(UcfConfig.COOKIE_KEY_MANAGE_LOGIN_DEPTID)

	#+++++++++++++++++++++++++++++++++++++++
	#+++ クッキーログインメールアドレスを取得
	#+++++++++++++++++++++++++++++++++++++++
	def getCookieManageMailAddress(self):
		return self.decodeCookiePassword(self.getCookie(UcfConfig.COOKIE_KEY_MANAGE_LOGIN_MAIL_ADDRESS))

	#+++++++++++++++++++++++++++++++++++++++
	#+++ クッキー用にログイン用データをセット
	#+++++++++++++++++++++++++++++++++++++++
	def setCookieManageLoginInfo(self, auto_login_flag, login_id, password, dept_id,mail_address=''):
		# 自動ログインＦ
		self.setCookie(UcfConfig.COOKIE_KEY_MANAGE_AUTO_LOGIN, UcfConfig.VALUE_MANAGE_AUTO_LOGIN if auto_login_flag else '')
		# ログインＩＤ
		self.setCookie(UcfConfig.COOKIE_KEY_MANAGE_LOGIN_ID, login_id)
		# ログインパスワード
		self.setCookie(UcfConfig.COOKIE_KEY_MANAGE_LOGIN_PASSWORD, password)
		# ログイン店舗ＩＤ
		self.setCookie(UcfConfig.COOKIE_KEY_MANAGE_LOGIN_DEPTID, dept_id)
		# ログインメールアドレス
		self.setCookie(UcfConfig.COOKIE_KEY_MANAGE_LOGIN_MAIL_ADDRESS, mail_address)

	#+++++++++++++++++++++++++++++++++++++++
	#+++ クッキー用にパスワードを暗号化（MD5ではなくCrypto暗号化を採用）
	#+++++++++++++++++++++++++++++++++++++++
	def encodeCookiePassword(self, password):
		return self.encodeLoginPassword(password, isForce=True)

	#+++++++++++++++++++++++++++++++++++++++
	#+++ クッキー用にパスワードを複合化（MD5ではなくCrypto暗号化を採用）
	#+++++++++++++++++++++++++++++++++++++++
	def decodeCookiePassword(self, password):
		return self.decodeLoginPassword(password, isForce=True)

	#+++++++++++++++++++++++++++++++++++++++
	#+++ パスワードを暗号化（MD5ではなくCrypto暗号化を採用）
	#+++ 設定に依存
	#+++++++++++++++++++++++++++++++++++++++
	def encodeLoginPassword(self, password, isForce=False):
		if password != None and password != '':
			if isForce or UcfConfig.MANAGE_LOGIN_PASSWORD_CRYPTOGRAPIC_FLAG == 'on':
				return UcfUtil.enCrypto(str(password, 'utf-8'), UcfConfig.MANAGE_LOGIN_PASSWORD_CRYPTOGRAPIC_KEY)
			else:
				return password
		else:
			return ''
	#+++++++++++++++++++++++++++++++++++++++

	#+++++++++++++++++++++++++++++++++++++++
	#+++ パスワードを複合化（MD5ではなくCrypto暗号化を採用）
	#+++ 設定に依存
	#+++++++++++++++++++++++++++++++++++++++
	def decodeLoginPassword(self, password, isForce=False):
		if password != None and password != '':
			if isForce or UcfConfig.MANAGE_LOGIN_PASSWORD_CRYPTOGRAPIC_FLAG == 'on':
				try:
					return UcfUtil.deCrypto(str(password, 'utf-8'), UcfConfig.MANAGE_LOGIN_PASSWORD_CRYPTOGRAPIC_KEY)
				# 互換性のため、暗号化されていない値の場合は例外はキャッチして無視.TODO ログをはくなど必要！？
				except Exception as e:
					return password
			else:
				return password
		else:
			return ''
	#+++++++++++++++++++++++++++++++++++++++

	def checkBelongDeptID(self, target_dept_id):
		u'''管理用所属店舗ＩＤチェック'''
		isFilter = False
		if not self.isSuperVisor():
			if target_dept_id != self.getBelongDeptID():
				isFilter = True

		if isFilter:
			# エラーページに遷移
			self.redirectError(UcfMessage.getMessage(UcfMessage.MSG_INVALID_ACCESS_DATA_AUTHORITY, ()))
			return False

		return True


	def isSuperVisor(self):
		u'''管理用：スーパーバイザかどうか'''
		return self.getLoginDeptID() == UcfConfig.SUPERVISOR_DEPT_ID
	
	def isAdmin(self):
		u'''管理用：管理者かどうか'''
		temp = ',' + UcfUtil.nvl(self.getSession(UcfConfig.SESSIONKEY_MANAGE_ACCESS_AUTHORITY)).replace(' ', '') + ','

		result = None
		if ',' + UcfConfig.ACCESS_AUTHORITY_ADMIN + ',' in temp:
			result = True
		else:
			result = False
		return result
	
	def getLoginOperatorID(self):
		u'''管理用：ログインオペレータＩＤを取得'''
		return UcfUtil.nvl(self.getSession(UcfConfig.SESSIONKEY_MANAGE_LOGIN_ID))

	def getLoginOperatorName(self):
		u'''管理用：ログインオペレータ名を取得'''
		return UcfUtil.nvl(self.getSession(UcfConfig.SESSIONKEY_MANAGE_LOGIN_NAME))

	def getLoginDeptID(self):
		u'''管理用：ログイン店舗ＩＤを取得'''
		return UcfUtil.nvl(self.getSession(UcfConfig.SESSIONKEY_MANAGE_LOGIN_DEPT_ID))

	def getLoginOperatorMailAddress(self):
		u'''管理用：ログインオペレータメールアドレスを取得'''
		return UcfUtil.nvl(self.getSession(UcfConfig.SESSIONKEY_MANAGE_LOGIN_MAIL_ADDRESS))

	def checkDateChanged(self, model):
		u'''更新日時チェック'''

		req_date_changed = UcfUtil.nvl(self.getRequest('date_changed'))
#		if req_date_changed != None and req_date_changed != '' and req_date_changed != str(model.date_changed):
		if req_date_changed != '' and UcfUtil.getDateTime(req_date_changed) != UcfUtil.getLocalTime(str(model.date_changed)):
			return False
		else:
			return True

	def getParameterForList(self, each_page_count, default_scond):
		u''' 管理一覧画面用に必要なパラメータを計算して返す '''

		searched = UcfUtil.nvl(self.getRequest('searched'))
		stype = UcfUtil.nvl(self.getRequest('stype'))
		pno = UcfUtil.nvl(self.getRequest('pno'))	# ページ番号（１～）
		sconds = {}

		if pno == '':
			pno = 1
		else:
			pno = int(pno)
			if pno <= 0:
				pno = 1

		# 今回取得するデータＩＮＤＥＸ（FROM、TO）を取得
		from_index = each_page_count * (pno - 1)
		to_index = from_index + each_page_count - 1


		# 検索条件にデフォルト値を考慮した条件を生成
		# Request値のセット
		for argument in self.request:
			if argument.startswith("sk_"):
				v = UcfUtil.nvl(self.getRequest(argument))
				sconds[argument] = v
		# デフォルト値のマージ
		for k,v in default_scond.iteritems():
			if not k in sconds:
				sconds[k] = v

		# stypeを追加
		sconds['stype'] = stype

		# 検索条件用クエリーの生成
		scond_query = ''
		for k, v in  iter(sconds.items()):
			scond_query += k + "=" + UcfUtil.urlEncode(v) + "&"
		scond_query += "searched" + "=" + UcfUtil.urlEncode(searched) + "&"
		scond_query = scond_query.strip("&")


		return searched, pno, from_index, to_index, sconds, scond_query 
		
	def outputErrorLog(self, e):
		u''' 例外をログ出力する '''
		logging.error(e)

		strLogText = ''
		strLogText += str(type(e)) + "\r\n"
		strLogText += str(e) + "\r\n"
#		strLogText += str(e.__repr__()) + "\r\n"

		strHttpStatus = ''
#		strHttpStatus += '[Url]:' + request.url + "\n"
#		strHttpStatus += '[QueryString]:' + self.request.query_string + "\n"
#		strHttpStatus += '[Request]:' + "\n"
#		for argument in self.request.arguments():
#			strHttpStatus += argument + "=" + UcfUtil.nvl(self.getRequest(argument)) + "\n"
#		strHttpStatus += '[Headers]:' + "\n"
		# CONTENT_LENGTHの処理でたまにエラーが発生するのでtry catchしとく
		try:
			for k,v in self.request.headers.iteritems():
				strHttpStatus += str(k) + ':' + str(v) + "\n"
		except:
			pass

		unique_id = UcfUtil.guid()
		mdlLog = UCFMDLProcessLog(unique_id=unique_id,key_name=UcfConfig.KEY_PREFIX + unique_id)	
		mdlLog.comment = ''
		mdlLog.dept_id = UcfUtil.nvl(self.getLoginDeptID())
		mdlLog.log_type = 'MANAGE_ERROR'
		mdlLog.log_text = strLogText
		mdlLog.http_status =  str(strHttpStatus, UcfConfig.ENCODING)  #unicode(strHttpStatus, UcfConfig.ENCODING, 'ignore')
		mdlLog.customer_id = ''
		mdlLog.operator_id = self.getLoginOperatorID()
#		mdlLog.page_id = self._page_id
		mdlLog.page_id = self.getPageID()
		mdlLog.creator_name = 'SYSTEM'
		mdlLog.updater_name = 'SYSTEM'
		mdlLog.del_flag = ''
		mdlLog.put()


############################################################
## フロント用：ページヘルパー
############################################################
class FrontHelper(Helper):
#	def __init__(self):
#		# 親のコンストラクタをコール
#		Helper.__init__(self)

	def init(self):

		u'''フロントサイト用の初期化'''
		self._root_folder_path = ''
		# エラーページＵＲＬ
		if self._error_page == None or self._error_page == '':
			self._error_page = UcfConfig.URL_ERROR

		#キャリア判定
		self.judgeTargetCareer()

	def checkLogin(self, not_redirect=False):
		u'''フロント用ログインチェック'''
		data = self.getLoginCustomerID()
		# ログインしていなければ
		if data == None or data == '':
			if not not_redirect:
				self.redirect(UcfUtil.exchangeUcfURL(self.getRootPath() + UcfConfig.URL_LOGIN))
			return False
		else:
			return True

	def getLoginCustomerID(self):
		u'''フロント用：ログイン顧客ＩＤを取得'''
		return UcfUtil.nvl(self.getSession(UcfConfig.SESSIONKEY_LOGIN_ID))

	def getLoginDeptID(self):
		u'''フロント用：ログイン店舗ＩＤを取得'''
		return UcfUtil.nvl(self.getSession(UcfConfig.SESSIONKEY_LOGIN_DEPT_ID))


	def outputErrorLog(self, e):
		u''' 例外をログ出力する '''
		strLogText = ''
		strLogText += str(type(e)) + "\r\n"
		strLogText += str(e) + "\r\n"
#		strLogText += str(e.__repr__()) + "\r\n"

		strHttpStatus = ''
#		strHttpStatus += '[Url]:' + request.url + "\n"
#		strHttpStatus += '[QueryString]:' + self.request.query_string + "\n"
#		strHttpStatus += '[Request]:' + "\n"
#		for argument in self.request.arguments():
#			strHttpStatus += argument + "=" + UcfUtil.nvl(self.getRequest(argument)) + "\n"
#		strHttpStatus += '[Headers]:' + "\n"
		# CONTENT_LENGTHの処理でたまにエラーが発生するのでtry catchしとく
		try:
			for k,v in  iter(request.headers.items()): #self.request.headers.iteritems()
				strHttpStatus += str(k) + ':' + str(v) + "\n"
		except:
			pass

		logging.error(strLogText)

		unique_id = UcfUtil.guid()
		mdlLog = UCFMDLProcessLog(unique_id=unique_id,key_name=UcfConfig.KEY_PREFIX + unique_id)	
		mdlLog.comment = ''
		mdlLog.dept_id = self.getLoginDeptID()
		mdlLog.log_type = 'FRONT_ERROR'
		mdlLog.log_text = strLogText
		mdlLog.http_status = str(strHttpStatus, UcfConfig.ENCODING)  #unicode(strHttpStatus, UcfConfig.ENCODING, 'ignore')
		mdlLog.customer_id = self.getLoginCustomerID()
		mdlLog.operator_id = ''
#		mdlLog.page_id = self._page_id
		mdlLog.page_id = self.getPageID()
		mdlLog.creator_name = 'SYSTEM'
		mdlLog.updater_name = 'SYSTEM'
		mdlLog.del_flag = ''
		mdlLog.put()



############################################################
## ビューヘルパーの親クラス
############################################################
class ViewHelper():

	def applicate(self, vo, model, helper):
		return None

	def formatDateTime(self, dat):
		u'''日付を表示に適切な文字列に変換（日付型エンティティには不要.文字列フィールドで日付型の場合などに使用）'''
		result = ''
		if not dat is None:
			dat = UcfUtil.getLocalTime(dat)
			if not dat is None:
				result = dat.strftime('%Y/%m/%d %H:%M:%S')

		return result
	

############################################################
## １レコード分のVo情報をまとめて保持するクラス
############################################################
class UcfVoInfo():
	u'''１レコード分のVo情報をまとめて保持するクラス'''
	# インデックス
	index = None
	# インデックスを２で割った値（一覧表示制御用）
	each_row = None
	# Vo
	vo = None
	# 表示用Vo
	voVH = None
	# バリデーションチェック結果
	validator = None
	# リスト版Vo
	voList = None

	def __init__(self):
		# クラス変数の初期化（コンストラクタで明示的に行わないとインスタンス生成時に初期化されないため）
		self.index = 0
		# インデックスを２で割った値（一覧表示制御用）
		self.each_row = 0
		# Vo
		self.vo = None
		# 表示用Vo
		self.voVH = None
		# バリデーションチェック結果
		self.validator = None
		# リスト版Vo
		self.voList = None

	def exchangeEncoding(vo):
		u''' voデータを表示用に文字コードを変換  2011/06/01 現在この処理は不要'''
		for k,v in vo.iteritems():
			# ファイルオブジェクトなどをスルーするために変換できないものは無視（微妙？） 2009/11/19 T.ASAO
			try:
				# Django1.2バージョンアップ時、日本語の文字化けを防ぐ 2011/05/31
				#vo[k] = unicode(v).encode(UcfConfig.ENCODING)
				vo[k] = v
			except:
				pass

		return vo
	exchangeEncoding = staticmethod(exchangeEncoding)


	def setVo(self, vo, view_helper, model, helper, isWithoutExchangeEncode=False):
		u''' voをセットし同時にvoVHも作成するメソッド
			※エンコードを同時にする場合は必ずテンプレートに渡す直前で行うこと
		'''
		# vo自体をセット
		self.vo = vo
# 自動上書きは危険なのでコメントアウト
#		# 指定モデルがあればそれに基づいてVoを加工
#		if model <> None:
#		 for data in model.getReferenceData():
#			self.vo[data.name] = data.value

		# VHを作成
		if view_helper != None:
			self.voVH = view_helper.applicate(vo, helper)
			# 文字コード変換 不要な処理の為、削除 2011/06/01
			# if not isWithoutExchangeEncode:
			#	self.vo = UcfVoInfo.exchangeEncoding(self.vo)
			#	self.voVH = UcfVoInfo.exchangeEncoding(self.voVH)
		else:
			self.voVH = vo
			# 文字コード変換 不要な処理の為、削除 2011/06/01
			#if not isWithoutExchangeEncode:
			#	self.vo = UcfVoInfo.exchangeEncoding(self.vo)



	def setRequestToVo(helper):
		u'''Requestデータをハッシュにセット. '''
		vo = {}
		for argument in helper.request.arguments():
			vo[argument] = helper.getRequest(argument)
		return vo
	setRequestToVo = staticmethod(setRequestToVo)


	def margeRequestToVo(helper, vo, isKeyAppend=False):
		u'''Requestデータを指定VOにマージ '''
		for argument in helper.request.arguments():
			if argument in vo or isKeyAppend:
				vo[argument] = helper.getRequest(argument)
	margeRequestToVo = staticmethod(margeRequestToVo)


############################################################
## 各ページでテンプレートに渡すための共通変数群を管理するクラス
############################################################
class UcfParameter():
	u'''各ページでテンプレートに渡すための共通変数群を管理するクラス'''
	# 共通変数を定義
	edit_type = None
	target_id = None
	validation_check = None
	# POSTフラグ
	post_flag = None

	# 詳細系ページ用
	voinfo = None
	# 一覧系ページ用（UcfVoInfoリスト）
	voinfos = None
	# 一覧の件数
	all_count = None

	# エラー情報
	error_info = None

	# Requestパラメータ用
	request = None

	# それ以外のパラメータ用
	data = None
#	# POST
#	post = None

	def __init__(self):
		u'''コンストラクタ'''
		# クラス変数の初期化（コンストラクタで明示的に行わないとインスタンス生成時に初期化されないため）
		self.edit_type = ''
		self.target_id = ''
		self.validation_check = ''
		self.post_flag = ''
		self.voinfo = UcfVoInfo()
		self.voinfos = []
		self.all_count = 0
		self.error_info = None
		self.request = {}
		self.data = {}
#		self.post = []

	def setRequestData(self, helper):
		# Requestパラメータをそのままセット
		for argument in helper.request.arguments():
			value = helper.getRequest(argument)
			self.request[argument] = value
#			# POST用データをセット(TODO ポストデータのみの取得をしたい！！)
#			value = helper.request.get(argument)
#			self.post.append(UcfData(argument, value))


	def setParameterForList(self, index, each_page_count, from_index, to_index, pno, sconds, scond_query, default_scond, paging_disp_limit=11,is_only_inpage_data=False):
		u''' 一覧に必要な各種パラメータをセット '''
		# ページング表示件数
		# paging_disp_limit = 11
		# 最終ページ番号
		if not is_only_inpage_data:
			last_page_no = (index - 1) / each_page_count + 1
		else:
			last_page_no = -1

		# 一覧件数（表示件数）
		self.list_count = len(self.voinfos)
		# 一覧件数（実件数）
		if not is_only_inpage_data:
			self.data['real_count'] = index
		else:
			self.data['real_count'] = -1
		# 一覧FROM（1～)
		if not is_only_inpage_data:
			self.data['from_seq'] = from_index + 1 if from_index < index else index
		else:
			self.data['from_seq'] = from_index + 1

		# 一覧TO（1～)
		if not is_only_inpage_data:
			self.data['to_seq'] = to_index + 1 if to_index < index else index
		else:
			self.data['to_seq'] = to_index + 1
		# 1ページ内の最大件数
		self.data['each_page_count'] = each_page_count
		# ページ番号（１～）
		self.data['pno'] = pno

#		# 先頭ページ番号文字列（リンクを表示しないなら空）
#		self.data['first_page_pno'] = '1' if pno > 1  else ''
#		# 最終ページ番号文字列（リンクを表示しないなら空）
#		self.data['last_page_pno'] = str(last_page_no) if index > 0 and pno != last_page_no else ''
#		# 一つ前のページ番号文字列（リンクを表示しないなら空）
#		self.data['pre_page_pno'] = str(pno - 1) if pno > 1  else ''
#		# 次のページ番号文字列（リンクを表示しないなら空）
#		self.data['next_page_pno'] = str(pno + 1) if index > 0 and pno != last_page_no else ''

#リンクは表示するように変更 2009.4.1 Osamu Kurihara

		# 先頭ページ番号文字列（リンクを表示しないなら空）
		self.data['first_page_pno'] = '1' if pno > 1  else '1'
		# 最終ページ番号文字列（リンクを表示しないなら空）
		if not is_only_inpage_data:
			self.data['last_page_pno'] = str(last_page_no) if index > 0 else '1'
		else:
			self.data['last_page_pno'] = ''
		# 一つ前のページ番号文字列（リンクを表示しないなら空）
		self.data['pre_page_pno'] = str(pno - 1) if pno > 1  else '1'
		# 次のページ番号文字列（リンクを表示しないなら空）
		self.data['next_page_pno'] = str(pno + 1) if index > 0 else '1'

		# 先頭ページかどうか
		self.data['is_first_page'] = pno == 1
		# 最終ページかどうか
		self.data['is_last_page'] = (pno == last_page_no) and pno > 1

		#ページングリスト
		if index > 0:
			paging_start = 0
			paging_end = 0
			if pno - (paging_disp_limit / 2) > 1:
				paging_start = pno - (paging_disp_limit / 2)
			else:
				paging_start = 1
			if paging_start + paging_disp_limit - 1 < last_page_no:
				paging_end = paging_start + paging_disp_limit - 1
			else:
				paging_end = last_page_no

			if paging_end == last_page_no and paging_start > 1:
				if paging_end - (paging_disp_limit - 1) > 1:
					paging_start = paging_end - (paging_disp_limit - 1)
				else:
					paging_start = 1

			#ページングリストをセット
			self.data['paging_list'] = range(paging_start, paging_end+1)

		# 検索条件
		sconds2 = None
		if sconds != None:
			sconds2 = {}
			for k,v in sconds.iteritems():
				sconds2[k] = str(v, UcfConfig.ENCODING)
		self.data['sconds'] = sconds2
				
			
		# 検索条件クエリー
		self.data['scond'] = scond_query
#		self.data['scond_js'] = UcfUtil.escapeForJs(scond_query)
		# 検索条件JavaScriptArray（クリアボタン用に初期値をセット）
		scond_name_js = ''
		scond_value_js = ''
		if sconds != None:
			for k,v in sconds.iteritems():
				value = ''
				if k in default_scond:
					value = default_scond[k]
				scond_name_js += ',' + "'" + UcfUtil.escapeForJs(k) + "'"
				scond_value_js += ',' + "'" + UcfUtil.escapeForJs(value) + "'"
		scond_name_js = scond_name_js.strip(",")
		scond_value_js = scond_value_js.strip(",")
		self.data['scond_name_js'] = scond_name_js
		self.data['scond_value_js'] = scond_value_js

############################################################
## 管理用：管理メニューツリーを管理するクラス
############################################################
class UcfManageMenu():
	u'''管理用：管理メニューツリーを管理するクラス'''

	def getManageMenuGroupID(menu_id):
		u'''管理用：管理メニューのグループIDを返す'''
		#TODO 設定XMLから展開したい

		# デフォルト
		group_id=menu_id

		# ワークフロー設定管理
		if menu_id == 'WORKFLOWMASTER':
			group_id='WORKFLOW'

		# ワークフロー申請管理
		elif menu_id == 'WORKFLOW':
			group_id='WORKFLOW'

		# ABテスト設定管理
		elif menu_id == 'ABTESTMASTER':
			group_id='ABTEST'

		# ABテスト集計管理
		elif menu_id == 'ABTESTCOUNT':
			group_id='ABTEST'

		return group_id
	getManageMenuGroupID = staticmethod(getManageMenuGroupID)

	def getManageSubMenuList(helper):
		u''' サブメニューリスト取得(表示用なので文字コードエンコード済み)'''
		#TODO 設定XMLから展開したい

		menu_id = helper._menu_id
		list = []
		title=''
		url=''

		# 同じ管理メニュー
		title = helper._page_title + u'一覧'
		url = './list'
		UcfManageMenu.appendManageSubMenuList(list, title, url)

		if helper.getAccessAuthority(menu_id, UcfConfig.EDIT_TYPE_NEW):
			title = helper._page_title + u'新規作成'
			url = './regist?etp=new'
			UcfManageMenu.appendManageSubMenuList(list, title, url)

		## グループ管理メニュー追加
		# ワークフロー設定管理
		if menu_id == 'WORKFLOWMASTER':
			title = u'ワークフロー申請一覧'
			url = '../workflow/list'
			UcfManageMenu.appendManageSubMenuList(list, title, url)

			if helper.getAccessAuthority('WORKFLOW', UcfConfig.EDIT_TYPE_NEW):
				title = u'ワークフロー申請新規作成'
				url = '../workflow/regist?etp=new'
				UcfManageMenu.appendManageSubMenuList(list, title, url)

		# ワークフロー申請管理
		elif menu_id == 'WORKFLOW':
			title = u'ワークフロー設定一覧'
			url = '../master/list'
			UcfManageMenu.appendManageSubMenuList(list, title, url)

			if helper.getAccessAuthority('WORKFLOWMASTER', UcfConfig.EDIT_TYPE_NEW):
				title = u'ワークフロー設定新規作成'
				url = '../master/regist?etp=new'
				UcfManageMenu.appendManageSubMenuList(list, title, url)

		# ABテスト設定管理
		elif menu_id == 'ABTESTMASTER':
			title = u'ＡＢテスト集計一覧'
			url = '../count/list'
			UcfManageMenu.appendManageSubMenuList(list, title, url)

			if helper.getAccessAuthority('ABTESTCOUNT', UcfConfig.EDIT_TYPE_NEW):
				title = u'ＡＢテスト集計新規作成'
				url = '../count/regist?etp=new'
				UcfManageMenu.appendManageSubMenuList(list, title, url)

		# ABテスト集計管理
		elif menu_id == 'ABTESTCOUNT':
			title = u'ＡＢテスト設定一覧'
			url = '../master/list'
			UcfManageMenu.appendManageSubMenuList(list, title, url)

			if helper.getAccessAuthority('ABTESTMASTER', UcfConfig.EDIT_TYPE_NEW):
				title = u'ＡＢテスト設定新規作成'
				url = '../master/regist?etp=new'
				UcfManageMenu.appendManageSubMenuList(list, title, url)

#		# 共有アドレス帳管理
#		elif menu_id == 'ADDRESSBOOK_SHARE':
#			title = u'共有アドレス帳一覧'
#			url = '../share/list'
#			UcfManageMenu.appendManageSubMenuList(list, title, url)
#
#			if helper.getAccessAuthority('ADDRESSBOOK_SHARE', UcfConfig.EDIT_TYPE_NEW):
#				title = u'共有アドレス帳新規作成'
#				url = '../share/regist&etp=new'
#				UcfManageMenu.appendManageSubMenuList(list, title, url)

		return list
	getManageSubMenuList = staticmethod(getManageSubMenuList)

	def appendManageSubMenuList(list, title, url):
		u''' サブメニューリストにアイテム追加(内部メソッド)'''
		list_item = {}
		# 不要な処理の為、削除 2011/06/01
		# list_item['title'] = UcfUtil.exchangeEncoding(title)
		list_item['title'] = UcfUtil.nvl(title)
		list_item['url'] = url
		list.append(list_item)
	appendManageSubMenuList = staticmethod(appendManageSubMenuList)

############################################################
## 管理用：各ページでテンプレートに渡すためのパラメータクラス
############################################################
class UcfManageParameter(UcfParameter):
	u'''管理用：各ページでテンプレートに渡すためのパラメータクラス'''
	
	def __init__(self, helper):
		u'''管理用の一般的なパラメータをUcfParameterにセット'''

		# 親のコンストラクタをコール
		UcfParameter.__init__(self)

		# Requestパラメータをそのままセット
		self.setRequestData(helper)

		# 検索条件をセット（一覧ページはこの後上書きされる）
		self.data['scond'] = UcfUtil.nvl(helper.getRequest('scond'))

		# ログインオペレータＩＤ
		self.data['login_id'] = helper.getLoginOperatorID()
		# ログインオペレータ名称
		self.data['login_name'] = helper.getLoginOperatorName()
		# テーマＩＤ
		theme_id = UcfUtil.nvl(helper.getRequest('theme_id'))
		if theme_id == '':
			theme_id = UcfUtil.nvl(helper.getCookie('theme_id'))
		if theme_id == '':
			theme_id = UcfConfig.DEFAULT_MANAGE_THEME_ID
		self.data['theme_id'] = theme_id
		helper.setCookie('theme_id', theme_id)
		# ページタイトル
		# djangoテンプレートの変更に伴い、エンコードを削除
		# self.data['page_title'] = unicode(helper._page_title).encode(UcfConfig.ENCODING)
		self.data['page_title'] = helper._page_title
		
		# メニューＩＤ
		self.data['menu_id'] = helper._menu_id
		# スーパーバイザフラグ
		self.data['supervisor_flag'] = 'ON' if helper.isSuperVisor() else ''
		# 管理者フラグ
		self.data['admin_flag'] = 'ON' if helper.isAdmin() else ''

		# 各権限
		authority = {}
		authority[UcfConfig.EDIT_TYPE_RENEW] = 'ON' if helper.getAccessAuthority(helper._menu_id, UcfConfig.EDIT_TYPE_RENEW) else ''
		authority[UcfConfig.EDIT_TYPE_NEW] = 'ON' if helper.getAccessAuthority(helper._menu_id, UcfConfig.EDIT_TYPE_NEW) else ''
		authority[UcfConfig.EDIT_TYPE_DOWNLOAD] = 'ON' if helper.getAccessAuthority(helper._menu_id, UcfConfig.EDIT_TYPE_DOWNLOAD) else ''
		authority[UcfConfig.EDIT_TYPE_DELETE] = 'ON' if helper.getAccessAuthority(helper._menu_id, UcfConfig.EDIT_TYPE_DELETE) else ''
		self.data['authority'] = authority

		#サブメニュー
		self.data['submenu'] = UcfManageMenu.getManageSubMenuList(helper)

		# POSTフラグ
		self.post_flag = 'ON' if helper._request_type == UcfConfig.REQUEST_TYPE_POST else ''

		# リクエストにRURLが含まれていたらそのＵＲＬエンコード版をdataにセットする
		if helper.getRequest(UcfConfig.REQUESTKEY_RURL) != None:
			self.data['RURL_ENC'] = UcfUtil.urlEncode(helper.getRequest(UcfConfig.REQUESTKEY_RURL))




############################################################
## フロント用：各ページでテンプレートに渡すためのパラメータクラス
############################################################
class UcfFrontParameter(UcfParameter):
	u'''フロント用：各ページでテンプレートに渡すためのパラメータクラス'''
	
	def __init__(self, helper):
		u'''フロント用の一般的なパラメータをUcfParameterにセット'''

		# 親のコンストラクタをコール
		UcfParameter.__init__(self)

		# Requestパラメータをそのままセット
		self.setRequestData(helper)

		# ログイン顧客ＩＤ
		self.data['login_id'] = helper.getLoginCustomerID()
		
		# POSTフラグ
		self.post_flag = 'ON' if helper._request_type == UcfConfig.REQUEST_TYPE_POST else ''


############################################################
## MP対応 管理ページ用：Ajaxヘルパー
############################################################
class AjaxHelper(Helper):

	def __init__(self):
		# 親のコンストラクタをコール
		Helper.__init__(self)

	def get(self, domain=None):
		# Django1.2バージョンアップ時、FILE文字コード変更 2011/05/31
		# settings.FILE_CHARSET = 'Shift_JIS'
		# settings.FILE_CHARSET = UcfConfig.FILE_CHARSET
		# Ajaxの場合、UTF-8で送受信する為、デフォルト値を利用
		# self.request.charset = UcfConfig.ENCODING
		# self.response.charset = UcfConfig.ENCODING
		self._request_type = UcfConfig.REQUEST_TYPE_GET
		self.init()
		self.onLoad()
		self.processOfRequest(domain)

	def post(self, domain=None):
		# Django1.2バージョンアップ時、FILE文字コード変更 2011/05/31
		# settings.FILE_CHARSET = 'Shift_JIS'
		# settings.FILE_CHARSET = UcfConfig.FILE_CHARSET
		# Ajaxの場合、UTF-8で送受信する為、デフォルト値を利用
		# self.request.charset = UcfConfig.ENCODING
		# self.response.charset = UcfConfig.ENCODING
		self._request_type = UcfConfig.REQUEST_TYPE_POST
		self.init()
		self.onLoad()
		self.processOfRequest(domain)

	def processOfRequest(self, domain):
		u'''Requestがきた場合の処理（抽象メソッドイメージ）'''
		pass

############################################################
## MP対応 管理ページ用：MP管理ページ用ヘルパー
############################################################
class MPManagerHelper(Helper):

	def __init__(self):
		# 親のコンストラクタをコール
		Helper.__init__(self)
		self._error_page = UcfConfig.URL_ERROR
		#logging.info(UcfConfig.URL_ERROR)

	def get(self, domain=None):
		# Django1.2バージョンアップ時、FILE文字コード変更 2011/05/31
		# settings.FILE_CHARSET = 'Shift_JIS'
		# settings.FILE_CHARSET = UcfConfig.FILE_CHARSET
		# Ajaxの場合、UTF-8で送受信する為、デフォルト値を利用
		# self.request.charset = UcfConfig.ENCODING
		# self.response.charset = UcfConfig.ENCODING
		self._request_type = UcfConfig.REQUEST_TYPE_GET
		self.init()
		self.onLoad()
		self.processOfRequest(domain)

	def post(self, domain=None):
		# Django1.2バージョンアップ時、FILE文字コード変更 2011/05/31
		# settings.FILE_CHARSET = 'Shift_JIS'
		# settings.FILE_CHARSET = UcfConfig.FILE_CHARSET
		# Ajaxの場合、UTF-8で送受信する為、デフォルト値を利用
		# self.request.charset = UcfConfig.ENCODING
		# self.response.charset = UcfConfig.ENCODING
		self._request_type = UcfConfig.REQUEST_TYPE_POST
		self.init()
		self.onLoad()
		self.processOfRequest(domain)

	def processOfRequest(self, domain):
		u'''Requestがきた場合の処理（抽象メソッドイメージ）'''
		pass
	
	def getLoginCustomerID(self):
		return UcfUtil.nvl(self.getRequest('did'))