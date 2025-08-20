# coding: utf-8

# import os,sys
# import logging
# from django.conf import settings # FILE文字コードの変更に使用 2011/05/31

# from google.appengine.api import users
# from ucf.config.ucfconfig import *

# from ucf.utils.ucfutil import *
# from ucf.config.ucfconfig import *
# from ucf.config.ucfmessage import *
# from ucf.utils.models  import *
# from ucf.utils.ucfxml import *

from ucf.tablehelper.operator import *	# authLoginで使用
# from appengine_utilities import sessions

from license.sateraito_func import GoogleAppsDomainEntry

class CheckLogin():

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 管理用ログインチェック
	#+++++++++++++++++++++++++++++++++++++++
	def checkLogin(self, add_querys=None, isStaticLogin=False, not_redirect=False):
		data = self.getLoginOperatorID()
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

			return isLogin

		else:
			return True
	checkLogin = staticmethod(checkLogin)

	#+++++++++++++++++++++++++++++++++++++++
	#+++ 管理用ログインチェック
	#+++++++++++++++++++++++++++++++++++++++
	def mpCheckLogin(self, add_querys=None, isStaticLogin=False, not_redirect=False):
		u'''
		TITLE:管理用ログインチェック
		PARAMETER:
			add_querys:ログイン画面に追加するクエリーのハッシュ
			isStaticLogin:静的なログインをするならTrue
		'''

		try:
			# Check login user
			user = users.get_current_user()
			if user == None:
				# userが存在しない場合、認証失敗
				login_url = users.create_login_url('http://uc-gbt-mp.appspot.com/enq/entry?mid=otomodachi', None, 'satelaito.jp')
				self.redirect(login_url)
				return
			# Check GoogleApps Domain
			user_email = user.email()
			#self.response.out.write(user_email)
			google_apps_domain = user_email.split('@')
			# domainが取得できなかった場合、False
			if google_apps_domain[1] == None or google_apps_domain[1] == '':
				return False
			else:
				# Check opsocial id in database
				#self.response.out.write(google_apps_domain[1])
				logging.info(google_apps_domain[1])
				query = GoogleAppsDomainEntry.gql("where google_apps_domain = :1", google_apps_domain[1])
				user_entries = query.get()
				if user_entries is None:
					# クエリがなければFalse
					return False
			return True
		except BaseException as e:
			self.outputErrorLog(e)
			self.redirectError(UcfMessage.getMessage(UcfMessage.MSG_SYSTEM_ERROR, ()))
			return
	mpCheckLogin = staticmethod(mpCheckLogin)

