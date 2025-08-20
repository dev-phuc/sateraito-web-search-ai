# coding: utf-8

############################################
## メッセージ管理クラス
## TODO 設定ファイル化してもいいけど..
############################################
class UcfMessage():
	MSG_SYSTEM_ERROR = u'ただいまサイトが込み合っています。お手数をおかけしますがしばらくたってから再度お試しください。'

	MSG_VC_NEED = u'%sは必須です。'
	MSG_VC_MAXLENGTH = u'%sは%s文字以内でなければなりません。'
	MSG_VC_MINLENGTH = u'%sは%s文字以上でなければなりません。'
	MSG_VC_LENGTH = u'%sは%s文字でなければなりません。'
	MSG_VC_MATCHING = u'%sは「%s」のいずれかでなければなりません。'
	MSG_VC_ALPHABETNUMBER = u'%sは半角英数字でなければなりません。'
	MSG_VC_ALPHABET = u'%sは半角英字でなければなりません。'
	MSG_VC_MAILADDRESS = u'メールアドレスとして正しくありません。'
	MSG_VC_MAILADDRESS_EX = u'%sはメールアドレスとして正しくありません。'
	MSG_VC_NUMERIC = u'%sは半角数字でなければなりません。'
	MSG_VC_ZENKAKU = u'%sは全角でなければなりません。'
	MSG_VC_HANKAKU = u'%sは半角でなければなりません。'
	MSG_VC_ZENKAKU_HIRAGANA = u'%sは全角ひらがなでなければなりません。'
	MSG_VC_ZENKAKU_KATAKANA = u'%sは全角カタカナでなければなりません。'
	MSG_VC_DATE = u'%sは日付として正しくありません。「YYYY/MM/DD」形式で入力してください。'
	MSG_VC_DATETIME = u'%sは日時として正しくありません。「YYYY/MM/DD hh:mm:ss」形式で入力してください。'
	MSG_VC_REG_PATTERN = u'%sは適切な形式ではありません。'

	MSG_INVALID_DEPT_ID = u'この店舗ＩＤを指定することはできません。「%s」'
	MSG_INVALID_ACCESS_DATA_AUTHORITY = u'このデータにアクセスする権限がありません。'
	MSG_INVALID_ACCESS_AUTHORITY = u'この機能にアクセスする権限がありません。'
	MSG_VC_ALREADY_EXIST = u'このデータは既に存在します。'
	MSG_NOT_EXIST_DATA = u'このデータは存在しません。ＩＤ：「%s」'
	MSG_INVALID_PARAMETER = u'パラメータが不正です。KEY：「%s」'
	MSG_INVALID_PROCESS = u'この処理を行うことはできません。'
	MSG_EXIST_VC_ERROR = u'入力エラーがあります。'
	MSG_ALREADY_UPDATED_DATA = u'このデータは他で更新されています。やり直してください。'

	MSG_FAILED_UPDATE_DB = u'データベースの更新に失敗しました。メッセージ「%s」'

	MSG_CLEAR_LOGIN_STATUS = u'ログイン状態が破棄されました。再度ログインからやり直してください。'

	MSG_ERR_FAILED_GOOGLEAPPS_USERS = u'GoogleApps認証情報が取得できませんでした。管理者にお問い合わせください。'

	MSG_FAILED_UPLOAD_FILE_BY_SIZE = u'ファイルサイズが大きいためアップロードできませんでした。アップロード可能なファイルは１ＭＢまでです。'

	###########################
	## 管理用
	MSG_FAILED_MANAGE_LOGIN = u'ログインＩＤかパスワードが違います。やり直してください。'

	###########################
	## フロント用
	MSG_FAILED_LOGIN = u'ログインＩＤかパスワードが違います。やり直してください。'

	###########################
	## ワークフロー用
	MSG_NOTFOUND_VALID_WORKFLOWMASTER = u'有効なワークフロー設定がありません。ＩＤ「%s」'

	###########################
	## ガジェット版要
	MSG_RETRY_FROM_GADGET_PAGE = u'恐れ入りますがサイトのリンクより再度お試しください。'

	def getMessage(message_template, ls_param=()):
		u'''メッセージを作成'''
		result = message_template
		try:
			return result % ls_param
		except:
			return result.replace('%s', '')
	getMessage = staticmethod(getMessage)
