# coding: utf-8

import os,sys

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
	ENCODING = 'cp932' #windows shift-jis
#	ENCODING = 'utf-8'
	# HTMLファイルのエンコード
#	FILE_CHARSET = 'Shift_JIS'
	FILE_CHARSET = 'cp932'
	# テンプレートフォルダパス
	TEMPLATES_FOLDER_PATH = 'templates'
	# テンプレートフォルダパス
	MOBILE_TEMPLATES_FOLDER_NAME = 'm'
	# filesフォルダパス
	#FILES_FOLDER_PATH = 'files'
	# パラメータファイルフォルダパス
	PARAM_FOLDER_PATH = 'params'

	COOKIE_DATE_FMT = '%a, %d-%b-%Y %H:%M:%S GMT'

#	#メールSMTPサーバ（システムメール）
#	MAIL_SMTP_SERVER = ''
#	#メール送信者（システムメール）
#	MAIL_SMTP_PORT = 587

#	#メール送信者（システムメール）
#	MAIL_SMTP_SENDER = ''

	# Modelのkey_nameのPREFIX
	KEY_PREFIX = 'KN_'

	# セッションタイムアウト（秒）
	SESSION_TIMEOUT = 1200
	# クッキーのセッションＩＤ
	SESSION_COOKIE_NAME = 'ucf-session-sid'

	# TIMEZONEの時間のずれ
	TIME_ZONE_HOUR = 9

	# スーパーバイザ店舗ＩＤ
	# 数字を含むとスプレッドシートでのログインチェックができないため変更（s0000000とかも変換されてしまうため）
#	SUPERVISOR_DEPT_ID = '00000000'
	SUPERVISOR_DEPT_ID = 'ssssssss'
	# 一般店舗ID
	DEFAULT_DEPT_ID = 'w0000000'

	# 管理ログインパスワード暗号化フラグ(on:有効. それ以外:無効)
	# オペレータデータソースなどによって切り替える必要あり
	MANAGE_LOGIN_PASSWORD_CRYPTOGRAPIC_FLAG = 'on'
	# 管理ログインパスワード暗号化キー（SSOシステムなどと同じにする必要があるので注意.クッキーパスワードの暗号化にも使用）
	MANAGE_LOGIN_PASSWORD_CRYPTOGRAPIC_KEY = 'AEDEAA25-6D38-41a6-A884-9FFBCF2AE08D'

	# クッキーキー
	COOKIE_KEY_MANAGE_AUTO_LOGIN = 'al'
	COOKIE_KEY_MANAGE_LOGIN_ID = 'UCID'
	COOKIE_KEY_MANAGE_LOGIN_PASSWORD = 'UCIDS'
	COOKIE_KEY_MANAGE_LOGIN_DEPTID = 'DPTID'
	COOKIE_KEY_MANAGE_LOGIN_MAIL_ADDRESS = 'UCMA'
	VALUE_MANAGE_AUTO_LOGIN = 'AUTO'

	####################################
	## キャリア定義
	VALUE_CAREER_TYPE_PC = "PC"					#PCサイト
	VALUE_CAREER_TYPE_MOBILE = "MB"			#モバイルサイト

	VALUE_CAREER_PC = "PC"							#PCプラウザ
	VALUE_CAREER_IMODE = "IMODE";
	VALUE_CAREER_EZWEB = "EZWEB";
	VALUE_CAREER_SOFTBANK = "SOFTBANK";
	VALUE_CAREER_MOBILE = "MOBILE"			#3キャリア以外のモバイル


	####################################
	## 管理用
	# セッションキー：管理用ログインＩＤ
	SESSIONKEY_MANAGE_LOGIN_ID = 'SKEYMLID'
	# セッションキー：管理用ログイン名称
	SESSIONKEY_MANAGE_LOGIN_NAME = 'SKEYMLIN'
	# セッションキー：管理用アクセス権限
	SESSIONKEY_MANAGE_ACCESS_AUTHORITY = 'SKEYMAA'
	# セッションキー：管理用オペレータ所属店舗ＩＤ
	SESSIONKEY_MANAGE_LOGIN_DEPT_ID = 'SKEYMDPTID'
	# セッションキー：管理用オペレータメールアドレス
	SESSIONKEY_MANAGE_LOGIN_MAIL_ADDRESS = 'SKEYMMA'

	####################################
	## フロント用
	# セッションキー：フロント用ログインＩＤ
	SESSIONKEY_LOGIN_ID = 'SKEYLID'
	# セッションキー：フロント用店舗ＩＤ
	SESSIONKEY_LOGIN_DEPT_ID = 'SKEYDPTID'

	####################################
	## 共通
	# セッションキー：エラー情報
	SESSIONKEY_ERROR_INFO = 'SKEYEINFO'

	# セッションキー:RURL
	SESSIONKEY_RURL = 'RURL'

	CACHEKEY_PREFIX_ABTESTMASTER = 'ABTM_'

	# デフォルト暗号化キー（SSOマネージャと同じ）
	CRYPTO_KEY = 'B11D7E41-57C7-4680-83B0-DCF73A437566'

	# REQUEST値：バリデーションチェック
	VC_CHECK = 'v'
	# REQUEST値：編集タイプ（新規）
	EDIT_TYPE_NEW = 'new'
	# REQUEST値：編集タイプ（編集）
	EDIT_TYPE_RENEW = 'renew'
	# REQUEST値：編集タイプ（削除）
	EDIT_TYPE_DELETE = 'delete'
	# REQUEST値：編集タイプ（CSVダウンロード）
	EDIT_TYPE_DOWNLOAD = 'download'
	# ステータスバック
	STATUS_BACK = 'b'

	# REQUESTキー:一覧チェックボックス
	REQUESTKEY_MANAGE_LIST_ITEM = 'itid'

	# REQUESTキー:RURL
	REQUESTKEY_RURL = 'RURL'

	# REQUESTキー:ページタイプ
	REQUESTKEY_PAGETYPE = 'ptp'

	# REQUESTキー:リダイレクト時パラメータ受け渡しキー（memcacheキー）
	REQUESTKEY_MEMCACHE_KEY = 'mck'

	# デフォルトThemeID
	DEFAULT_MANAGE_THEME_ID = 'ThemeBlue'

	# オペレータ権限
	# 管理者
	ACCESS_AUTHORITY_ADMIN = 'ADMIN'

	# グループＩＤ
	GROUP_ID_LIST = [(u'G01',u'グループ１'), (u'G02',u'グループ２'), (u'G03',u'グループ３'), (u'G04',u'グループ４')]

	# 都道府県
	ADDRESS_KEN_LIST = [(u'北海道',u'北海道'), (u'青森県',u'青森県'), (u'岩手県',u'岩手県'), (u'宮城県',u'宮城県'), (u'秋田県',u'秋田県'), (u'山形県',u'山形県'), (u'福島県',u'福島県'), (u'茨城県',u'茨城県'), (u'栃木県',u'栃木県'), (u'群馬県',u'群馬県'), (u'埼玉県',u'埼玉県'), (u'千葉県',u'千葉県'), (u'東京都',u'東京都'), (u'神奈川県',u'神奈川県'), (u'新潟県',u'新潟県'), (u'富山県',u'富山県'), (u'石川県',u'石川県'), (u'福井県',u'福井県'), (u'山梨県',u'山梨県'), (u'長野県',u'長野県'), (u'岐阜県',u'岐阜県'), (u'静岡県',u'静岡県'), (u'愛知県',u'愛知県'), (u'三重県',u'三重県'), (u'滋賀県',u'滋賀県'), (u'京都府',u'京都府'), (u'大阪府',u'大阪府'), (u'兵庫県',u'兵庫県'), (u'奈良県',u'奈良県'), (u'和歌山県',u'和歌山県'), (u'鳥取県',u'鳥取県'), (u'島根県',u'島根県'), (u'岡山県',u'岡山県'), (u'広島県',u'広島県'), (u'山口県',u'山口県'), (u'徳島県',u'徳島県'), (u'香川県',u'香川県'), (u'愛媛県',u'愛媛県'), (u'高知県',u'高知県'), (u'福岡県',u'福岡県'), (u'佐賀県',u'佐賀県'), (u'長崎県',u'長崎県'), (u'熊本県',u'熊本県'), (u'大分県',u'大分県'), (u'宮崎県',u'宮崎県'), (u'鹿児島県',u'鹿児島県'), (u'沖縄県',u'沖縄県')]

	##############################
	# URL

	# 管理

	# ログインページ
	URL_MANAGE_LOGIN = '/login'
	# エラーページ
	URL_MANAGE_ERROR = '/error'

	# フロント
	# ログインページ
	URL_LOGIN = '/login'
	# エラーページ
	URL_ERROR = '/error'

	# 採番関連
	# ワークフロー用
	NUMBERING_WORFROW_NUMBER_ID = 'WORKFROW'
	NUMBERING_WORFROW_NUMBER_SUB_ID = '001'
	NUMBERING_WORFROW_PREFIX = 'W'
	NUMBERING_WORFROW_SEQUENCE_NO_DIGIT = 8

	# 拡張アンケート用 お知らせページ
	NUMBERING_SITE_PAGE_NAME_NUMBER_ID = 'ENQ_SITES_PAGE_NAME'
	NUMBERING_SITE_PAGE_NAME_NUMBER_SUB_ID = '001'
	NUMBERING_SITE_PAGE_NAME_PREFIX = 'enq'
	NUMBERING_SITE_PAGE_SEQUENCE_NO_DIGIT = 0

#	# 拡張アンケート用 空のSitesページ用
#	NUMBERING_SITE_EMPTYPAGE_NAME_NUMBER_ID = 'ENQ_SITES_EMPTYPAGE_NAME'
#	NUMBERING_SITE_EMPTYPAGE_NAME_NUMBER_SUB_ID = '001'
#	NUMBERING_SITE_EMPTYPAGE_NAME_PREFIX = 'ep'
#	NUMBERING_SITE_EMPTYPAGE_SEQUENCE_NO_DIGIT = 0

	COOKIE_CRYPTOGRAPIC_KEY = 'a36d610b901b44a787ef608f8ffc07cc'

