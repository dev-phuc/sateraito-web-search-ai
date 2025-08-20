#!/usr/bin/python
# coding: utf-8

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'

import os
import jinja2
# import webapp2
import urllib

# GAEGEN2対応:独自ロガー
# import logging
import sateraito_logger as logging

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.api import namespace_manager
from google.appengine.api.urlfetch import DownloadError
# import gdata.apps.service  # g2対応
# import gdata.alt.appengine
# from gdata.apps.service import AppsForYourDomainException
# from oauth2client.client import OAuth2WebServerFlow  # g2対応
from oauthlib.oauth2 import WebApplicationClient
import sateraito_inc
import sateraito_func
import sateraito_db
import sateraito_page
from sateraito_func import OpenSocialInfo
from sateraito_func import RequestChecker
from ucf.utils.ucfutil import UcfUtil

cwd = os.path.dirname(__file__)
path = os.path.join(cwd, 'templates')
bcc = jinja2.MemcachedBytecodeCache(client=memcache.Client(), prefix='jinja2/bytecode/', timeout=None)
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path), auto_reload=False, bytecode_cache=bcc)

'''
popup.py

@since 2012-08-01
@version 2015-04-28
@author Akitoshi Abe
'''


class _LogoutPage(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

  #	# OpenID認証がキャッシュされてしまうのを考慮して毎回認証（でもある程度キャッシュしてもOK）
  #	def _reCheckOpenIDLogin(self, continue_param, google_apps_domain):
  #
  #		# ガジェットのURL指定対応
  #		hl = self.request.get('hl')
  #		if hl is None or hl == '':
  #			hl = sateraito_inc.DEFAULT_LANGUAGE
  #
  #		user = users.get_current_user()
  #
  #		if user is not None:
  #			# if user logged in, force logout
  #			logging.info('user id found, clearing cookie...')
  #			self.removeAppsCookie()
  #
  #		if not sateraito_func.isMultiDomainSetting(google_apps_domain):
  #			#logging.info('user is None, redirecting login url')
  #			login_url = users.create_login_url(dest_url=continue_param, federated_identity=google_apps_domain)
  #			logging.info('login_url=' + login_url)
  #			self.response.out.write('<html><head>')
  #			self.response.out.write('<meta http-equiv="refresh" content="1;URL=' + login_url + '">')
  #			self.response.out.write('</head><body></body></html>')
  #		else:
  #			#logging.info('user is None, redirecting login url')
  #			redirect_url = sateraito_inc.my_site_url + '/' + google_apps_domain + '/authsubdomain'
  #			redirect_url = UcfUtil.appendQueryString(redirect_url, 'hl', hl)
  #			redirect_url = UcfUtil.appendQueryString(redirect_url, 'continue_param', continue_param)
  #			login_url = users.create_login_url(dest_url=continue_param, federated_identity=google_apps_domain)
  #
  #			values = {
  #				'primary_auth_url': login_url,
  #				'secondary_auth_url': redirect_url,
  #				'google_apps_domain':google_apps_domain,
  #				'lang':hl,
  #			}
  #			template = jinja_environment.get_template('select_auth_domain.html')
  #			self.response.out.write(template.render(values))
  #
  #		return False
  #
  #	def _isAuthOpenIDLogin(self, token, google_apps_domain):
  #		# tokenチェック
  #		if token is not None and token != '':
  #			check_token = memcache.get('auth_openid?token=' + token)
  #			logging.info('_isAuthOpenIDLogin=' + str(check_token) + ':' + token)
  #			if token == str(check_token):
  #				return True
  #		return False

  def removeAppsCookie(self):
    self.removeCookie('GAPS')
    self.removeCookie('ACSID')
    self.removeCookie('SACSID')
    self.removeCookie('APISID')
    self.removeCookie('SAPISID')

  def removeCookie(self, cookie_name):
    # set past date to cookie --> cookie will be deleted
    # self.response.headers.add_header('Set-Cookie', cookie_name + '=deleted; expires=Fri, 31-Dec-2000 23:59:59 GMT; path=/;')
    if sateraito_func.isSameSiteCookieSupportedUA(self.request.headers.get('User-Agent')):
      self.response.headers.add_header('Set-Cookie', cookie_name + '=deleted; expires=Fri, 31-Dec-2000 23:59:59 GMT; path=/;SameSite=None;secure;')
    else:
      self.response.headers.add_header('Set-Cookie', cookie_name + '=deleted; expires=Fri, 31-Dec-2000 23:59:59 GMT; path=/;secure;')


class Popup2(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
  '''
  open popup2.html to close popup window
  '''
  def doAction(self):
    # ガジェットのURL指定対応
    hl = self.request.get('hl')
    logging.info('hl=' + str(hl))
    if hl is None or hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE
    template = jinja_environment.get_template('popup2.html')
    # start http body
    # self.response.out.write(template.render({'hl':hl, 'user_lang':hl}))
    return template.render({'hl': hl, 'user_lang': hl, 'vscripturl': sateraito_func.getScriptVirtualUrl()})


class Popup3(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):

  def doAction(self, tenant_or_domain):

    logging.info('tenant_or_domain=' + str(tenant_or_domain))
    # ガジェットのURL指定対応
    hl = self.request.get('hl')
    if hl is None or hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE

    # check login
    is_ok, body_for_not_ok = self.oidAutoLogin(tenant_or_domain)
    if not is_ok:
      return body_for_not_ok
    # loginCheck = self.oidAutoLogin(google_apps_domain)
    # logging.debug(loginCheck)
    # if not loginCheck.get('status'):
    # 	if loginCheck.get('is_oidc_need_show_signin_link'):
    # 		logging.debug('is_oidc_need_show_signin_link=' + str(True))
    # 		return make_response('is_oidc_need_show_signin_link', 200)
    # 	else:
    # 		if loginCheck.get('response'):
    # 			return loginCheck.get('response')
    # 	return
    logging.info('viewer_email=' + str(self.viewer_email))
    return self.redirect('/popup2.html?hl=' + UcfUtil.urlEncode(hl))


class PopupSubdomain(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
  """	Popup screen for subdomain user
  """

  def get(self, tenant_or_domain, token):

    # ガジェットのURL指定対応
    hl = self.request.get('hl')
    if hl is None or hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE

    values = {
      'google_apps_domain': tenant_or_domain,
      'hl':hl,
      'user_lang':hl,
    }
    template = jinja_environment.get_template('popup_subdomain.html')
    # self.response.out.write(template.render(values))
    return template.render(values)

  def post(self, tenant_or_domain, token):  # g2対応：getとpostで動きが違うのでこっちはpostのままにしておく

    # ガジェットのURL指定対応
    hl = self.request.get('hl')
    if hl is None or hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE

    target_google_apps_domain = str(self.request.get('target_google_apps_domain')).lower()
    return self.redirect(sateraito_inc.my_site_url + '/' + tenant_or_domain + '/openid/' + token + '/' + target_google_apps_domain + '/before_popup.html?hl=' + UcfUtil.urlEncode(hl))


class BeforePopup(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):

  def _processOAuth2(self, tenant_or_domain, token, target_google_apps_domain, hl=sateraito_inc.DEFAULT_LANGUAGE):
    # Check OpenID Connect login user
    is_oidc_loggedin = self.session.get('is_oidc_loggedin')
    if is_oidc_loggedin is None or not is_oidc_loggedin:
      # if user logged in, force logout
      logging.info('user id found, clearing cookie...')
      self.removeAppsCookie()
    # go login by openid connect
    state = 'state-' + sateraito_func.dateString() + sateraito_func.randomString()
    logging.info('state=' + state)
    self.session['state'] = state
    dest_url = sateraito_inc.my_site_url + '/' + tenant_or_domain + '/openid/' + token + '/' + target_google_apps_domain + '/popup.html?hl=' + UcfUtil.urlEncode(hl)
    self.session['url_to_go_after_oidc_login'] = dest_url
    # create web server flow and redirect to auth url
    # GAE Gen2対応
    # flow = OAuth2WebServerFlow(
    # 						client_id=sateraito_inc.WEBAPP_CLIENT_ID,
    # 						client_secret=sateraito_inc.WEBAPP_CLIENT_SECRET,  # client_secret を渡すとエラーになる
    dictParam = dict(
      # Google+API、Scope廃止対応 2019.02.01
      # scope=['https://www.googleapis.com/auth/plus.me', 'https://www.googleapis.com/auth/plus.profile.emails.read'],
      scope=['openid', 'email'],
      redirect_uri=sateraito_inc.my_site_url + '/oidccallback',
      state=state,
      openid_realm=sateraito_inc.my_site_url,
      access_type='online',
      # hd=google_apps_domain		# セカンダリドメインユーザーが認証できないのでコメントアウト
    )
    # GAE Gen2対応
    # auth_uri = flow.step1_get_authorize_url()
    client = WebApplicationClient(sateraito_inc.WEBAPP_CLIENT_ID)
    auth_uri = client.prepare_request_uri(
      'https://accounts.google.com/o/oauth2/auth',
      **dictParam
    )

    logging.info('auth_uri=' + str(auth_uri))
    # SameSite対応…iOS12でCookieがうまくセットされないのでPOSTに変更 2019.10.28
    # → 効果なしだったのでredirectに戻す
    self.redirect(auth_uri)
    # post_items = []
    # spurl = auth_uri.split('?')
    # query_string = spurl[1] if len(spurl) >= 2 else ''
    # querys = query_string.split('&')
    # for query in querys:
    #	one_query = query.split('=')
    #	post_items.append({'name':one_query[0], 'value':UcfUtil.urlDecode(one_query[1]) if len(one_query) > 1 else ''})
    # action_url = spurl[0]
    # values = {
    #	'action_url':action_url
    #	,'post_items':post_items
    #	,'WaitMilliSeconds':0
    # }
    # template = jinja_environment.get_template('post.html')
    # self.response.out.write(template.render(values))

  def doAction(self, tenant_or_domain, token, target_google_apps_domain):

    # ガジェットのURL指定対応
    hl = self.request.get('hl')
    if hl is None or hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE

    # if sateraito_func.isOauth2Domain(tenant_or_domain):

    return self._processOAuth2(tenant_or_domain, token, target_google_apps_domain, hl=hl)

  # else:
  # 	self._processOAuth1(tenant_or_domain, token, target_google_apps_domain, hl=hl)


class Popup(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):
  """	save relation of opensocial id and user email
  After bind, log out and redirect to popup2.html
  """

  def doAction(self, tenant_or_domain, token, target_google_apps_domain):

    logging.info('target_google_apps_domain=' + str(target_google_apps_domain))

    # check login
    is_ok, body_for_not_ok = self.oidAutoLogin(tenant_or_domain, skip_domain_compatibility=True)
    if not is_ok:
      return body_for_not_ok

    logging.info('viewer_email=' + str(self.viewer_email))

    # ガジェットのURL指定対応
    hl = self.request.get('hl')
    if hl is None or hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE

    # Check GoogleApps Domain
    google_apps_domain_from_user_email = sateraito_func.getDomainPart(self.viewer_email)
    if not sateraito_func.isOauth2Domain(tenant_or_domain):
      if tenant_or_domain != google_apps_domain_from_user_email and target_google_apps_domain != google_apps_domain_from_user_email:
        logging.exception(
          'google apps domain does not match: ' + tenant_or_domain + ' and ' + google_apps_domain_from_user_email)
        values = {
          'google_apps_domain': google_apps_domain_from_user_email,
          'my_site_url': sateraito_inc.my_site_url,
          'my_site_url_for_static': sateraito_inc.my_site_url,
          'version': sateraito_func.getScriptVersionQuery(),
          'vscripturl': sateraito_func.getScriptVirtualUrl(),
          'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
          'hl': hl,
          'user_lang': hl,
        }
        logging.info('NOT_INSTALLED')
        template = jinja_environment.get_template('not_installed.html')
        # start http body
        # self.response.out.write(template.render(values))
        return template.render(values)
    else:  # ※Oauth2の場合は必ずgoogle_apps_domain=target_google_apps_domainがセットされてくるのでここで置き換え（サブドメイン用の「認証する」廃止に伴い）
      target_google_apps_domain = google_apps_domain_from_user_email

    # set namespace
    namespace_manager.set_namespace(tenant_or_domain)

    # Get opensocial_viewer_id from memcached db
    opensocial_info = OpenSocialInfo()
    opensocial_info.loadInfo(token)

    if opensocial_info.viewer_id is not None and target_google_apps_domain != '':
      rc = RequestChecker()

      logging.info('viewer_email=' + str(self.viewer_email))
      logging.info('viewer_user_id=' + str(self.viewer_user_id))
      logging.info('opensocial_viewer_id=' + opensocial_info.viewer_id)

      # これにより管理者かどうかの取得と本Apps契約内のユーザーかどうかの判定を兼ねる
      is_admin = False
      try:
        is_admin = rc.checkAppsAdmin(self.viewer_email, tenant_or_domain)  # ※ここでセットするドメインはnamespaceのドメイン（それによってOAuth2かどうかを判定するので）
        logging.info(is_admin)
      # except sateraito_func.NotInstalledException as instance:
      except Exception as instance:
        # ドメイン内ユーザーではない
        logging.error(instance)
        values = {
          'google_apps_domain': google_apps_domain_from_user_email,
          'my_site_url': sateraito_inc.my_site_url,
          'my_site_url_for_static': sateraito_inc.my_site_url,
          'version': sateraito_func.getScriptVersionQuery(),
          'vscripturl': sateraito_func.getScriptVirtualUrl(),
          'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
          'hl': hl,
          'user_lang': hl,
        }
        template = jinja_environment.get_template('not_installed.html')
        # start http body
        logging.info('NOT_INSTALLED')
        # self.response.out.write(template.render(values))
        return template.render(values)

      try:
        rc.putNewUserEntry(self.viewer_email,
								tenant_or_domain,
								target_google_apps_domain,
								opensocial_info.viewer_id,
								opensocial_info.container,
								self.viewer_user_id,
                is_admin)
        logging.info('putNewUserEntry:' + self.viewer_email + ':' + tenant_or_domain + ':' + opensocial_info.viewer_id + ':' + opensocial_info.container)
      # except AppsForYourDomainException as instance:  # g2対応 取り急ぎBaseExceptionでキャッチ
      except BaseException as e:
        logging.error('error: class name:' + str(e.__class__.__name__) + ' message=' + str(e))
        # Application not installed to your domain
        values = {
          'google_apps_domain': tenant_or_domain,
          'my_site_url': sateraito_inc.my_site_url,
          'my_site_url_for_static': sateraito_inc.my_site_url,
          'version': sateraito_func.getScriptVersionQuery(),
          'vscripturl': sateraito_func.getScriptVirtualUrl(),
          'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
          'hl': hl,
          'user_lang': hl,
        }
        logging.info('NOT_INSTALLED')
        template = jinja_environment.get_template('not_installed.html')
        # start http body
        # self.response.out.write(template.render(values))
        return template.render(values)

      # Save Number of GoogleApps domain user
      # ※↑でチェックするので↓では自動でGoogleAppsDomainEntryに追加してOK
      if target_google_apps_domain != '':
        # sateraito_func.saveGoogleAppsDomainEntry(self.viewer_email, target_google_apps_domain)
        sateraito_func.registDomainEntry(tenant_or_domain, target_google_apps_domain, self.viewer_email)

      # logout and go to popup2.html page(auto close script)
      # create_logout_url が GAEだけでなくGoogleApps全体をログアウトするように変更になったため呼ばないように変更（認証タイプ=Google Accounts API の場合にその挙動となるとのこと） 2015.07.02
      # logout_url = users.create_logout_url('popup2.html?hl=' + UcfUtil.urlEncode(hl))
      # self.redirect(logout_url)
      self.redirect('/popup2.html?hl=' + UcfUtil.urlEncode(hl))


class PopupOid(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):

  def doAction(self, tenant_or_domain):

    logging.info('google_apps_domain=' + str(tenant_or_domain))

    # check login
    is_ok, body_for_not_ok = self.oidAutoLogin(tenant_or_domain)
    if not is_ok:
      return body_for_not_ok

    logging.info('viewer_email=' + str(self.viewer_email))

    hl = self.request.get('hl')
    if hl is None or hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE

    # Check GoogleApps Domain
    google_apps_domain_from_user_email = sateraito_func.getDomainPart(self.viewer_email)
    user_language = hl
    target_google_apps_domain = google_apps_domain_from_user_email

    # set namespace
    namespace_manager.set_namespace(tenant_or_domain)

    if target_google_apps_domain != '':
      rc = RequestChecker()

      logging.info('viewer_email=' + str(self.viewer_email))

      # これにより管理者かどうかの取得と本Apps契約内のユーザーかどうかの判定を兼ねる
      is_admin = False
      try:
        is_admin = rc.checkAppsAdmin(self.viewer_email, tenant_or_domain)  # ※ここでセットするドメインはnamespaceのドメイン（それによってOAuth2かどうかを判定するので）
        logging.info(is_admin)
      except Exception as instance:
        logging.error(instance)
        values = {
          'google_apps_domain': google_apps_domain_from_user_email,
          'my_site_url': sateraito_inc.my_site_url,
          'my_site_url_for_static': sateraito_inc.my_site_url,
          'version': sateraito_func.getScriptVersionQuery(),
          'vscripturl': sateraito_func.getScriptVirtualUrl(),
          'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
          'hl': hl,
          'user_lang': user_language,
        }
        template = jinja_environment.get_template('not_installed.html')
        # start http body
        logging.info('NOT_INSTALLED')
        # self.response.out.write(template.render(values))
        return template.render(values)

      try:
        rc.putNewUserEntry(self.viewer_email,
                           tenant_or_domain,
                           target_google_apps_domain,
                           self.viewer_id if self.viewer_id is not None and self.viewer_id != '' else '__not_set',
                           sateraito_func.OPENSOCIAL_CONTAINER_GOOGLE_SITE,
                           self.viewer_user_id,
                           is_admin)
        logging.info('putNewUserEntry:' + self.viewer_email + ':' + tenant_or_domain + ':' + self.viewer_id + ':' + '')
      # except AppsForYourDomainException as instance:  # g2対応：取り急ぎBaseExceptionでキャッチ
      except BaseException as e:
        logging.error('error: class name:' + e.__class__.__name__ + ' message=' + str(e))
        # Application not installed to your domain
        values = {
          'google_apps_domain': tenant_or_domain,
          'my_site_url': sateraito_inc.my_site_url,
          'my_site_url_for_static': sateraito_inc.my_site_url,
          'version': sateraito_func.getScriptVersionQuery(),
          'vscripturl': sateraito_func.getScriptVirtualUrl(),
          'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
          'hl': hl,
          'user_lang': user_language,
        }
        logging.info('NOT_INSTALLED')
        template = jinja_environment.get_template('not_installed.html')
        # start http body
        # self.response.out.write(template.render(values))
        return template.render(values)

    # Save Number of GoogleApps domain user
    if target_google_apps_domain != '':
      sateraito_func.registDomainEntry(tenant_or_domain, target_google_apps_domain, self.viewer_email)

    user_info_found = False
    if self.viewer_email is not None and self.viewer_email != '':
      user_info = sateraito_db.UserInfo.getInstance(self.viewer_email)
      user_info_found = True
      if user_info is None:
        user_info_found = False

    # domain_row = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)
    # hide_ad = sateraito_func.noneToFalse(domain_row.hide_ad)

    # get language
    user_language = sateraito_func.getUserLanguage(self.viewer_email, hl=hl)

    # for gadget property
    lang_file = sateraito_func.getLangFileName(user_language)

    # check domain_disabled
    domain_disabled = False
    if sateraito_func.isDomainDisabled(tenant_or_domain):
      domain_disabled = True

    is_workflow_admin = sateraito_func.isWorkflowAdmin(self.viewer_email, tenant_or_domain)

    # 管理者ガジェットからのアクセスかどうかを判定…文書のアクセス権判定で「管理者ならOK」とするかどうかに使用 2016.10.06
    # ※「docdetail」へのクエリーで判定（セキュリティを考慮して、admin=1 のような単純なものではなく何かのハッシュ値などにすること）※リファラーで判定はパターンを抑えきれないのでNG

    values = {
      'hl': hl,
      'user_lang': user_language,
      'google_apps_domain': tenant_or_domain,
      'my_site_url': sateraito_inc.my_site_url,
      'my_site_url_for_static': sateraito_inc.my_site_url,
      'version': sateraito_func.getScriptVersionQuery(),
      'vscripturl': sateraito_func.getScriptVirtualUrl(),
      'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
      'lang_file': lang_file,
      'extjs_locale_file': sateraito_func.getExtJsLocaleFileName(user_language),
      'is_oidc_need_show_signin_link': False,
      'popup': '',
      'user_info_found': user_info_found,
      'viewer_email': self.viewer_email,
      'primary_email': '',
      'user_disabled': False,  # user_entryからほんとは取得するが実際使っていないので..
      'domain_disabled': domain_disabled,
      # 'is_workflow_admin':is_admin,
      'is_workflow_admin': is_workflow_admin,
    }
    logging.debug(values)
    template = jinja_environment.get_template('popup_oidc.html')
    # start http body
    # self.response.out.write(template.render(values))
    return template.render(values)


# app = webapp2.WSGIApplication([
#   ('/([^/]*)/openid/([^/]*)/([^/]*)/before_popup.html$', BeforePopup),
#   ('/([^/]*)/openid/([^/]*)/([^/]*)/popup.html$', Popup),
#   ('/popup2.html$', Popup2),
#   ('/([^/]*)/([^/]*)/popup_subdomain.html$', PopupSubdomain),
#   ('/([^/]*)/popup_oidc.html$', PopupOid),
#   ('/([^/]*)/popup3.html$', Popup3),
# ], debug=sateraito_inc.debug_mode, config=sateraito_page.config)

def add_url_rules(app):
  app.add_url_rule('/<tenant_or_domain>/openid/<token>/<target_google_apps_domain>/before_popup.html',
                   view_func=BeforePopup.as_view('BeforePopup'))

  app.add_url_rule('/<tenant_or_domain>/openid/<token>/<target_google_apps_domain>/popup.html',
                   view_func=Popup.as_view('Popup'))

  app.add_url_rule('/popup2.html',
                   view_func=Popup2.as_view('Popup2'))

  app.add_url_rule('/<tenant_or_domain>/<token>/popup_subdomain.html',
                   view_func=PopupSubdomain.as_view('PopupSubdomain'))

  app.add_url_rule('/<tenant_or_domain>/popup_oidc.html',
                   view_func=PopupOid.as_view('PopupOid'))		# PopupOid2に移行のため廃止予定 2016.10.21 ....

  app.add_url_rule('/<tenant_or_domain>/popup3.html',
                   view_func=Popup3.as_view('Popup3'))
