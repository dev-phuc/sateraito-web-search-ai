# coding: utf-8

import os,sys
import sateraito_inc

############################################################
## 設定値定義クラス
############################################################
class UcfConfig():
	u'''設定値定義クラス'''

	# REQUESTタイプ：GET
	REQUEST_TYPE_GET = 'GET'
	# REQUESTタイプ：POST
	REQUEST_TYPE_POST = 'POST'

	# サイトのエンコード（UTF-8、shift_jis...）
#	ENCODING = 'shift_jis' 
#	ENCODING = 'cp932' #windows shift-jis
	ENCODING = 'utf-8'
	# HTMLファイルのエンコード
#	FILE_CHARSET = 'Shift_JIS'
#	FILE_CHARSET = 'cp932'
	FILE_CHARSET = 'UTF-8'
#	FILE_CHARSET_MOBILE = 'cp932'
	# ダウンロードCSVのエンコード
	DL_ENCODING = 'cp932'

	# テナントスクリプトフォルダパス
	TENANT_SCRIPT_FOLDER_PATH = 'tenant'
	# ドメインスクリプトフォルダパス
	DOMAIN_SCRIPT_FOLDER_PATH = 'domain'
	# テンプレートフォルダパス
	#TEMPLATES_FOLDER_PATH = 'templates'
	#TEMPLATES_FOLDER_PATH = 'templates_automatically'		# includeを取り除いたテンプレートファイル群
	TEMPLATES_FOLDER_PATH = 'templates_automatically' if not sateraito_inc.developer_mode else 'templates'

	# デフォルトのテンプレート言語フォルダ
	TEMPLATE_LANGUAGE_DEFAULT_FOLDER = 'default'
	# デフォルトのテンプレートデザインタイプフォルダ
	TEMPLATE_DEFAULT_DESIGN_TYPE = 'pc'
	# デフォルトのメッセージファイル名
	#MESSAGE_DEFAULT_FILE = 'default'
	MESSAGE_DEFAULT_FILE = 'ALL_ALL'
	MESSAGE_DEFAULT_LANGUAGE = 'en'
	# filesフォルダパス
	#FILES_FOLDER_PATH = 'files'
	# パラメータファイルフォルダパス
	PARAM_FOLDER_PATH = 'params'

	# Modelのkey_nameのPREFIX
	KEY_PREFIX = 'KN_'

	COOKIE_DATE_FMT = '%a, %d-%b-%Y %H:%M:%S GMT'

	# sateraito_inc で設定
#	# セッションタイムアウト（秒）
#	SESSION_TIMEOUT = 1200
	# クッキーのセッションＩＤ
	SESSION_COOKIE_NAME = 'ucf-session-sid'

	# TIMEZONE
	#TIME_ZONE_HOUR = 0			# こいつだけは処理上書き換えちゃう
	#TIMEZONE = sateraito_inc.DEFAULT_TIMEZONE			# こいつだけは処理上書き換えちゃう

	# グループ所属メンバーが何件以内なら、詳細情報を取得するかどうか
	MAX_MEMBER_CNT_FOR_GET_DETAIL_INFO = 200

#	# OpenID認証用クエリーキー
	REQUESTKEY_FOR_OPENIDAUTH = 'ah'
	# OpenID認証用MD5値サフィックス
	SUFFIX_FOR_OPENIDAUTH = 'abcde'

	# 
	QSTRING_UNIQUEID = 'unqid'

	# ログインパスワード暗号化フラグ(on:有効. それ以外:無効)
	# オペレータデータソースなどによって切り替える必要あり
	LOGIN_PASSWORD_CRYPTOGRAPIC_FLAG = 'on'
	# ログインパスワード暗号化キー（SSOシステムなどと同じにする必要があるので注意.クッキーパスワードの暗号化にも使用）
	LOGIN_PASSWORD_CRYPTOGRAPIC_KEY = 'AEDEAA25-6D38-41a6-A884-9FFBCF2AE08D'

	# クッキーキー
	COOKIE_KEY_AUTO_LOGIN = 'al'
	COOKIE_KEY_LOGIN_ID = 'UCID'
	COOKIE_KEY_LOGIN_PASSWORD = 'UCIDS'
	COOKIE_KEY_LOGIN_DEPTID = 'DPTID'
	COOKIE_KEY_LOGIN_MAIL_ADDRESS = 'UCMA'
	VALUE_AUTO_LOGIN = 'AUTO'
	COOKIE_KEY_RELAYSTATEURL = 'RSURL'
	COOKIE_KEY_DEVICE_DISTINGUISH_ID = 'ACSDDID'
	COOKIEKEY_LOGIN_DOMAINNAME = 'dn'		# クッキーキー：マルチドメイン対応.実際にログインしたドメインをCookieにセット
	COOKIEKEY_LEFTMENUCLASS = 'lm'		# クッキーキー：サイドメニューの開閉ステータス保持用
	COOKIE_KEY_DEVICE_MAC_ADDRESS = 'ma'
	COOKIE_KEY_IDENTIFIER_FOR_VENDOR = 'idvdr'

	####################################
	## キャリア定義
	VALUE_CAREER_TYPE_PC = "PC"					#PCサイト
	VALUE_CAREER_TYPE_SP = "SP"			#スマートフォンサイト
	VALUE_CAREER_TYPE_TABLET = "TABLET"			#タブレット
	VALUE_CAREER_TYPE_MOBILE = "MOBILE"			#モバイルサイト
	VALUE_CAREER_TYPE_API = "API"			#API

	VALUE_CAREER_PC = "PC"							#PCプラウザ
	VALUE_CAREER_IMODE = "IMODE"
	VALUE_CAREER_EZWEB = "EZWEB"
	VALUE_CAREER_SOFTBANK = "SOFTBANK"
	VALUE_CAREER_WILLCOM = "WILLCOM"
	VALUE_CAREER_MOBILE = "MOBILE"			#3キャリア以外のモバイル

	VALUE_DESIGN_TYPE_PC = "pc"
	VALUE_DESIGN_TYPE_SP = "sp"
	VALUE_DESIGN_TYPE_MOBILE = "m"
	VALUE_DESIGN_TYPE_API = "api"

	USERAGENTID_SSOCLIENT = "SSOCLIENT"			# これは変更不可

	####################################
	# セッションキー：CSRF用トークンプレフィクス
	SESSIONKEY_CSRF_TOKEN_PREFIX = 'CSRFTKN'
	# クライアントIPアドレス（オペレーションログ用）
	SESSIONKEY_CLIENTIP = 'CIP'
	# セッションキー：ログインＩＤ
	SESSIONKEY_LOGIN_ID = 'SKEYLID'
	# セッションキー：ログインオペレータＩＤ
	SESSIONKEY_LOGIN_OPERATOR_ID = 'SKEYLOID'
	# セッションキー：ログインオペレータユニークＩＤ
	SESSIONKEY_LOGIN_UNIQUE_ID = 'SKEYLUID'
	# セッションキー：ログイン名称
	SESSIONKEY_LOGIN_NAME = 'SKEYLIN'
	# セッションキー：アクセス権限
	SESSIONKEY_ACCESS_AUTHORITY = 'SKEYAA'
	# セッションキー：委任管理機能
	SESSIONKEY_DELEGATE_FUNCTION = 'SKEYDMF'
	# セッションキー：委任管理する管理グループ
	SESSIONKEY_DELEGATE_MANAGEMENT_GROUPS = 'SKEYDMMG'
	# セッションキー：オペレータ所属店舗ＩＤ
	SESSIONKEY_LOGIN_DEPT_ID = 'SKEYDPTID'
	# セッションキー：オペレータメールアドレス
	SESSIONKEY_LOGIN_MAIL_ADDRESS = 'SKEYMA'
	# セッションキー：X-Forwarded-ForIPアドレス
	SESSIONKEY_XFORWARDEDFOR_IP = 'XFF'
	# セッションキー：ログイン時の適用プロファイルユニークID
	SESSIONKEY_LOGIN_PROFILE_UNIQUE_ID = 'SKEYPUID'
	# セッションキー：ログイン時の適用対象環境種別（office, outside, sp, fp）
	SESSIONKEY_LOGIN_TARGET_ENV = 'SKEYTENV'
	# セッションキー：ユーザにパスワード変更を強制するフラグ
	SESSIONKEY_LOGIN_FORCE_PASSWORD_CHANGE = 'SKEYPFC'
	# セッションキー：自動遷移URL処理済みフラグ
	SESSIONKEY_ALREADY_DEAL_AUTO_REDIRECT_URL = 'SKEYADARU'
	# セッションキー：ログイン時のアプリケーションID
	SESSIONKEY_LOGIN_APPLICATION_ID = 'SKEYAPPID'
	# セッションキー：rurl_key
	SESSIONKEY_RURL_KEY	= 'SKEYRURLKEY'

	# セッションキー：クライアント認証が必要かどうかをセット（ログイン認証でプロファイルが確定したタイミングでセット）
	SESSION_KEY_IS_NEED_CLIENT_CERTIFICATE = 'isneedclientcertificate'
	# セッションキー：クライアント証明書認証結果
	SESSION_KEY_AUTH_CLIENT_CERTIFICATE = 'clientcertificateauth'
	# セッションキー：遅延ログイン履歴のユニークID
	SESSION_KEY_LOGIN_HISTORY_FOR_DELAY_UNIQUE_ID = 'loginhistorydelayid'
	# セッションキー：遅延ログイン情報のユニークID
	SESSION_KEY_LOGIN_INFO_FOR_DELAY_UNIQUE_ID = 'logininfodelayid'

	# セッションキー：MACアドレス
	SESSION_KEY_DEVICE_MAC_ADDRESS = 'SKYMCADDR'
	# セッションキー：IdenfierForVendor
	SESSION_KEY_IDENTIFIER_FOR_VENDOR = 'SKYIDVDR'
	# セッションキー：SSOアプリからの自動ログインであることを示すフラグ
	SESSION_KEY_SSODEVICE_AUTHLOGIN_FLAG = 'SKYSSODAL'

	# セッションに認証IDをセットする際のキー
	SESSIONKEY_AUTHID = 'authid'
	# Cookieに認証IDをセットする際のキー
	COOKIEKEY_AUTHID = 'a455431d1b604add95f9dc7e69b74c3e'

	# セッションキー：ログイン画面の端末申請の元の処理に戻るためのURL格納用
	SESSIONKEY_ORIGINAL_PROCESS_LINK_PREFIX = 'SKEYOPLK_'

	# 一時ログインキーRequestKey
	REQUESTKEY_TEMP_LOGIN_CHECK_ACTION_KEY = 'tc'

	#####################################
	#	一時的なログインのアクションキー
	#	アクセス申請
	TEMPLOGIN_ACTIONKEY_ACS_APPLY = 'taaa'
	#	メールプロキシAPI
	TEMPLOGIN_ACTIONKEY_CHECKLOGINAUTH_MAILPROXY = 'tacmp'

	# 一時キーの配列
	TEMPLOGIN_ACTIONKEY_LIST = [TEMPLOGIN_ACTIONKEY_ACS_APPLY]

	#####################################
	# 検索条件保持セッションキー
	# セッション保持用識別子Requestキー
	REQUESTKEY_SESSION_SCID = 'scid'
	# 検索条件保持セッションPREFIX
	SESSIONKEY_PREFIX_SEARCHCOND = 'sc:'
	# オペレータ一覧
	SESSIONKEY_SCOND_OPERATOR_LIST = 'f4ed32769d4041a58296b974d1626d34'
	# ユーザー一覧
	SESSIONKEY_SCOND_USER_LIST = '46b27a0d29ce44a9bf21fd1d03c6289e'
	# グループ一覧
	SESSIONKEY_SCOND_GROUP_LIST = 'd72383f436904ec8879e7a477e71b1aa'
	# ビジネスルール一覧
	SESSIONKEY_SCOND_BUSINESSRULE_LIST = '7e2fb233903d4273b512a294dc41edbc'
	# ログイン履歴
	SESSIONKEY_SCOND_LOGIN_HISTORY = '80fe752671664dc4b73f96dc623ddb2e'
	# オペレーションログ
	SESSIONKEY_SCOND_OPERATIONLOG = 'b969a3b2607c415e9d43bddc08e4f821'

	SESSIONKEY_SCOND_MASTERDATA_LIST = '21968e7a2743b4a3ba9c307a3abc0951'


	####################################
	## 共通
	# セッションキー：エラー情報
	SESSIONKEY_ERROR_INFO = 'SKEYEINFO'

	# セッションキー:RURL
	SESSIONKEY_RURL = 'RURL'

	# デフォルト暗号化キー（SSOマネージャと同じ）
	CRYPTO_KEY = 'B11D7E41-57C7-4680-83B0-DCF73A437566'
	COOKIE_CRYPTOGRAPIC_KEY = 'a36d610b901b44a787ef608f8ffc07cc'

	QSTRING_TYPE = 'tp'													# 編集タイプ
	QSTRING_TYPE2 = 'tp2'													# 編集タイプ２（コピー新規など用）
	QSTRING_STATUS = 'st'													# 編集ステータス

	# REQUEST値：バリデーションチェック
	VC_CHECK = 'v'
	# REQUEST値：編集タイプ（参照）
	EDIT_TYPE_REFER = 'r'
	# REQUEST値：編集タイプ（新規）
	EDIT_TYPE_NEW = 'n'
	# REQUEST値：編集タイプ（編集）
	EDIT_TYPE_RENEW = 'rn'
	# REQUEST値：編集タイプ（削除）
	EDIT_TYPE_DELETE = 'd'
	# REQUEST値：編集タイプ（スキップ）
	EDIT_TYPE_SKIP = 's'
	# REQUEST値：編集タイプ（コピー新規）
	EDIT_TYPE_COPYNEWREGIST = 'cn'
	# REQUEST値：編集タイプ（CSVダウンロード）
	EDIT_TYPE_DOWNLOAD = 'dl'
	# ステータスバック
	STATUS_BACK = 'b'

	# REQUESTキー:RURL
	REQUESTKEY_RURL = 'RURL'

	# REQUESTキーPREFIX:POSTデータ
	REQUESTKEY_POSTPREFIX = 'post_'

	# REQUESTキー:ページタイプ
	REQUESTKEY_PAGETYPE = 'ptp'

	# REQUESTキー:リダイレクト時パラメータ受け渡しキー（memcacheキー）
	REQUESTKEY_MEMCACHE_KEY = 'mck'

	# REQUESTキー：タスクの種類
	REQUESTKEY_TASK_TYPE = 'tk'

	# REQUESTキー：CSRF対策トークン
	REQUESTKEY_CSRF_TOKEN = 'token'

	# REQUESTキー：ワンタイム・ランダムパスワード用ランダムキー
	REQUESTKEY_MATRIXAUTH_RANDOMKEY = 'dcpk'

	# オペレータ権限
	# 特権管理者
	ACCESS_AUTHORITY_ADMIN = 'ADMIN'
	# 委託管理者
	ACCESS_AUTHORITY_OPERATOR = 'OPERATOR'
	# 一般ユーザ
	ACCESS_AUTHORITY_MANAGER = 'MANAGER'

	# 委託:オペレータ管理
	DELEGATE_FUNCTION_OPERATOR_CONFIG = 'OPERATOR'
	# 委託:ユーザ管理
	DELEGATE_FUNCTION_USER_CONFIG = 'USER'
	# 委託:組織(Group)管理
	DELEGATE_FUNCTION_GROUP_CONFIG = 'GROUP'
	# 委託:ビジネスルール管理
	DELEGATE_FUNCTION_BUSINESSRULE_CONFIG = 'BUSINESSRULE'

	DELEGATE_FUNCTION_MASTERDATA_CONFIG = 'MASTERDATA'

	# アクセス制御関連：申請なし端末件数の無制限をあらわす数
	DIRECT_APPROVAL_COUNT_UNLIMITED = '999999'

	REQUESTKEY_ACS_APPLY_STATUS = 'st'
	REQUESTVALUE_ACS_APPLY_STATUS_APPROVAL = '77a8aa3c3ce3415f94a4f389dd9c72cc'
	REQUESTVALUE_ACS_APPLY_STATUS_ENTRY = '27fcf0bb92f24b268af34a0e93d7632f'

	##############################
	# URL

	# ログインページ
	URL_LOGIN = '/login'
	# エラーページ
	URL_ERROR = '/error'


	# 採番関連
	# 企業ID（店舗ID）
	NUMBERING_NUMBER_ID_DEPT = 'DeptMaster'
	NUMBERING_NUMBER_SUB_ID_DEPT = '001'
	NUMBERING_PREFIX_DEPT = 'gbt'
	NUMBERING_SEQUENCE_NO_DIGIT_DEPT = 5

	# 認証APIのMD5SuffixKey（メールチェッカーMCAPPでも使用）
	MD5_SUFFIX_KEY_AUTHAPP = '288b79b66f2d49dc9d99e46658a0db3f'
	ENCODE_KEY_AUTHAPP = 'd1E4A6x4'

	# アドオン利用可能チェックAPIのMD5SuffixKey
	MD5_SUFFIX_KEY_CHECKADDONAVAILABLEDOMAIN = 'c21daaf5d9924370b3da157b6bcc4b5c'

	# クライアント証明書チェック機能のMD5SuffixKey
	MD5_SUFFIX_KEY_CHECKCLIENTCERTFICATION = '93c0f28ed97d44dd992363838fa15105'

	# 認証APIのMD5SuffixKey（checkauth2用）
	MD5_SUFFIX_KEY_CHECKAUTH2 = '0f6fc40dcecc462d9df170e7687b6e5b'
	ENCODE_KEY_CHECKAUTH2 = 'a9507dca'

	# アプリケーションID
	# スマートフォンセキュリティブラウザ（AUTHAPPと区別するためにあえて別にする）
	APPLICATIONID_SECURITYBROWSER = 'SECURITYBROWSER'
	# クライアント証明書チェック機能
	APPLICATIONID_CHECKCLIENTCERTFICATION = 'CHECKCLIENTCERTFICATION'

	# オペレーションログ
	# オペレーションタイプ（スクリーン＋オペレーションタイプが一意であること）
	OPERATION_TYPE_ADD = 'add'
	OPERATION_TYPE_MODIFY = 'modify'
	OPERATION_TYPE_REMOVE = 'remove'
	OPERATION_TYPE_CHANGEID = 'changeid'
	OPERATION_TYPE_ADD_MEMBERS = 'addmembers'
	OPERATION_TYPE_REMOVE_MEMBERS = 'removemembers'
	OPERATION_TYPE_ADD_DOMAIN = 'adddomain'
	OPERATION_TYPE_REMOVE_DOMAIN = 'removedomain'
	OPERATION_TYPE_ADD_PICTURE = 'addpicture'
	OPERATION_TYPE_REMOVE_PICTURE = 'removepicture'
	OPERATION_TYPE_MODIFY_DEVICE_DISTINGUISH_ID = 'modify_device_distinguish_id'

	# スクリーン
	SCREEN_OPERATOR = 'operator'
	SCREEN_USER = 'user'
	SCREEN_GROUP = 'group'
	SCREEN_BUSINESSRULE = 'businessrule'
	SCREEN_DASHBOARD = 'dashboard'
	SCREEN_MASTERDATA = 'masterdata'
	SCREEN_DICTIONARY = 'dictionary'

