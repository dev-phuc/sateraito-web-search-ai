#!/usr/bin/python
# coding: utf-8

# from flask import Flask, Response, render_template, request, make_response, session, redirect, after_this_request
# from flask.views import View, MethodView
from flask import Flask, Response, render_template, request, make_response, session, redirect

import sateraito_logger as logging
import datetime
import urllib
# from dateutil import zoneinfo, tz, parser
# from google.appengine.api import taskqueue
# from google.appengine.api import memcache
# from google.appengine.ext import ndb
from ucf.utils.ucfutil import UcfUtil
from ucf.utils.ssofunc import *  # GAEGEN2対応：SAML、SSO連携対応

import sateraito_inc
import sateraito_func
import sateraito_db
import sateraito_page


# import sateraito_black_list
# import oem_func				# LINE WORKS直接認証対応 2019.06.13

# class AcsPage(sateraito_page._AuthSSOGadget):
class AcsPage(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):
  @sateraito_func.convert_result_none_to_empty_str
  def get(self, tenant):
    try:
      return self._process(tenant)
    except Exception as e:
      logging.exception(e)
      return Response('System Error.', status=500)

  @sateraito_func.convert_result_none_to_empty_str
  def post(self, tenant):
    try:
      return self._process(tenant)
    except Exception as e:
      logging.exception(e)
      return Response('System Error.', status=500)

  def _process(self, tenant_or_domain):

    logging.debug('**** requests *********************')
    logging.debug(self.request)
    try:
      saml_response_with_base64 = self.request.get('SAMLResponse', '')
      relay_state = self.request.get('RelayState')
      logging.info('relay_state=' + relay_state)

      if saml_response_with_base64 == '':
        logging.warning('Invalid SAMLResponse.')
        # LINE WORKS直接認証対応…ついでにメッセージ画面の整備 2019.06.13
        # self.response.write('Invalid SAMLResponse.')
        hl = sateraito_inc.DEFAULT_LANGUAGE
        user_language = sateraito_func.getActiveLanguage('', hl=hl)
        my_lang = sateraito_func.MyLang(user_language)
        self.setSession('msg', 'Invalid SAMLResponse.')
        info_page_url = sateraito_inc.custom_domain_my_site_url + '/info'
        info_page_url = UcfUtil.appendQueryString(info_page_url, 'hl', hl)
        self.redirect(str(info_page_url))
        return

      # LINE WORKS直接認証対応…relay_stateは必須ではないので... 2019.06.13
      # if relay_state == '':
      #	logging.warning('Invalid RelayState.')
      #	self.response.write('Invalid RelayState.')
      #	return

      ## BASE64復号してSAMLResponseのXMLを取得
      # saml_response = UcfUtil.base64Decode(saml_response_with_base64)
      # logging.info(saml_response)

      # set namespace
      if not self.setNamespace(tenant_or_domain, ''):
        logging.warning('Invalid Tenant.')
        # LINE WORKS直接認証対応…ついでにメッセージ画面の整備 2019.06.13
        # self.response.write('Invalid Tenant.')
        hl = sateraito_inc.DEFAULT_LANGUAGE
        user_language = sateraito_func.getActiveLanguage('', hl=hl)
        my_lang = sateraito_func.MyLang(user_language)
        self.setSession('msg', 'Invalid Tenant.')
        info_page_url = sateraito_inc.custom_domain_my_site_url + '/info'
        info_page_url = UcfUtil.appendQueryString(info_page_url, 'hl', hl)
        self.redirect(str(info_page_url))
        return

      # LINE WORKS直接認証対応…LINE WORKSのSAML設定画面の「TEST」ボタンクリック時の判定 2019.06.13
      referer = self.request.headers.get('Referer', '')
      for_lineworks_test = referer.lower().find(sateraito_func.LINEWORKS_SAML_URL_PREFIX + 'test/') >= 0
      logging.info('for_lineworks_test=%s' % (for_lineworks_test))

      # state（relay_state）からセットアップ情報を取得（セットアップ時の認証かどうかの判定）
      for_setup = False
      contract_entry = None
      if relay_state.startswith('state-'):
        for_setup = True
        contract_entry = sateraito_db.TenantContractEntry.getInstanceByState(relay_state)
        if contract_entry is None or contract_entry.is_verified or contract_entry.tenant != tenant_or_domain:
          logging.warning('Invalid RelayState.')
          # LINE WORKS直接認証対応…ついでにメッセージ画面の整備 2019.06.13
          # self.response.write('Invalid RelayState.')
          hl = sateraito_inc.DEFAULT_LANGUAGE
          user_language = sateraito_func.getActiveLanguage('', hl=hl)
          my_lang = sateraito_func.MyLang(user_language)
          self.setSession('msg', 'Invalid RelayState.')
          info_page_url = sateraito_inc.custom_domain_my_site_url + '/info'
          info_page_url = UcfUtil.appendQueryString(info_page_url, 'hl', hl)
          self.redirect(str(info_page_url))
          return

      logging.info('for_setup=' + str(for_setup))
      # LINE WORKS直接認証対応…LINE WORKSのSAML設定画面の「TEST」ボタンクリック時の対応 2019.06.13
      # if not for_setup:
      domain_row = None
      sso_entity_id = ''
      if not for_setup and not for_lineworks_test:
        domain_row = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)
        if domain_row is None:
          logging.warning('Invalid Tenant.')
          # LINE WORKS直接認証対応…ついでにメッセージ画面の整備 2019.06.13
          # self.response.write('Invalid Tenant.')
          hl = sateraito_inc.DEFAULT_LANGUAGE
          user_language = sateraito_func.getActiveLanguage('', hl=hl)
          my_lang = sateraito_func.MyLang(user_language)
          self.setSession('msg', 'Invalid Tenant.')
          info_page_url = sateraito_inc.custom_domain_my_site_url + '/info'
          info_page_url = UcfUtil.appendQueryString(info_page_url, 'hl', hl)
          self.redirect(str(info_page_url))
          return

      # LINE WORKS直接認証対応…LINE WORKSのSAML設定画面の「TEST」ボタンクリック時の対応 2019.06.13
      if for_lineworks_test:
        samlsettings = sateraito_func.getSamlSettings(sateraito_inc.custom_domain_my_site_url, tenant_or_domain,
                                                      'dummy', 'dummy', '')
      elif not for_setup:
        samlsettings = self.getSamlSettings(tenant_or_domain, domain_row)
      else:
        sso_entity_id, sso_login_endpoint = sateraito_func.createSSOIdProviderInfo(contract_entry)
        samlsettings = sateraito_func.getSamlSettings(sateraito_inc.custom_domain_my_site_url, tenant_or_domain,
                                                      sso_entity_id, sso_login_endpoint, contract_entry.sso_public_key)

      saml_response = SamlResponse(samlsettings, saml_response_with_base64)
      # LINE WORKS直接認証対応…LINE WORKSのSAML設定画面の「TEST」ボタンクリック時の対応 2019.06.13
      # is_valid = saml_response.is_valid(self)
      is_valid = saml_response.is_valid(self, use_cert_in_samlresponse=for_lineworks_test)
      logging.info('is_valid=' + str(is_valid))
      if not is_valid:
        error_msg = UcfUtil.nvl(saml_response.get_error())
        logging.warning(error_msg)
        # LINE WORKS直接認証対応…ついでにメッセージ画面の整備 2019.06.13
        # self.response.write('Failed verify the signature.' + error_msg)
        hl = sateraito_inc.DEFAULT_LANGUAGE
        user_language = sateraito_func.getActiveLanguage('', hl=hl)
        my_lang = sateraito_func.MyLang(user_language)
        self.setSession('msg', 'Failed verify the signature.' + error_msg)
        info_page_url = sateraito_inc.custom_domain_my_site_url + '/info'
        info_page_url = UcfUtil.appendQueryString(info_page_url, 'hl', hl)
        self.redirect(str(info_page_url))
        return

      # LINE WORKS直接認証対応 2019.06.13
      idp_issuer = ''
      issuers = saml_response.get_issuers()
      for issuer in issuers:
        if issuer is not None and issuer != '':
          idp_issuer = issuer
          break
      logging.info('idp_issuer=%s' % (idp_issuer))
      is_sateraitosso = idp_issuer == sateraito_func.SSO_ENTITY_ID
      logging.info('is_sateraitosso=%s' % (is_sateraitosso))

      login_id = saml_response.get_nameid()
      logging.info('login_id=' + login_id)
      is_admin = 'true' == saml_response.get_isadmin()
      logging.info('is_admin=' + str(is_admin))
      uid = saml_response.get_uid()
      logging.info('uid=' + uid)
      familyname = saml_response.get_familyname()
      givenname = saml_response.get_givenname()

      # login_id、uid が取れたかどうかなどのチェック
      # LINE WORKS直接認証対応 2019.06.13
      # if login_id is None or login_id == '' or uid is None or uid == '':
      if login_id is None or login_id == '' or (is_sateraitosso and (uid is None or uid == '')):
        logging.warning('Invalid parameter. The nameid or uid is empty.')
        # LINE WORKS直接認証対応…ついでにメッセージ画面の整備 2019.06.13
        # self.response.write('Invalid parameter. The nameid or uid is empty.')
        hl = sateraito_inc.DEFAULT_LANGUAGE
        user_language = sateraito_func.getActiveLanguage('', hl=hl)
        my_lang = sateraito_func.MyLang(user_language)
        self.setSession('msg', 'Invalid parameter. The nameid or uid is empty.')
        info_page_url = sateraito_inc.custom_domain_my_site_url + '/info'
        info_page_url = UcfUtil.appendQueryString(info_page_url, 'hl', hl)
        self.redirect(str(info_page_url))
        return

      # LINE WORKS直接認証対応…LINE WORKSのSAMLからはユーザーID以外の内部ID、External Keyなどは取得できないためユーザーIDをセット... 2019.06.13
      if uid is None or uid == '':
        uid = login_id

      # LINE WORKS直接認証対応…LINE WORKSのSAMLResponseには管理者権限は含まれていないので... 2019.06.13
      # 1.セットアップしたユーザーを初期管理者扱いとする
      # 2.通常認証時はUserEntryから権限を取得して上書きする
      if idp_issuer.startswith(sateraito_func.LINEWORKS_ENTITY_ID_PREFIX):
        if for_setup:
          is_admin = True
        else:
          is_admin = sateraito_func.isWorkflowAdminForSSOGadget(login_id, tenant_or_domain,
                                                                do_not_include_additional_admin=True)
        logging.info('overwrite is_admin=%s' % (is_admin))

      # ログインセッションセット
      self.setSession('viewer_email', login_id)
      self.setSession('opensocial_viewer_id', uid)
      self.setSession('is_admin', is_admin)
      self.setSession('is_oidc_loggedin', True)  # _BasePage._checkOIDCRequest を流用したいがためにセットしておく

      self.viewer_email_raw = login_id
      self.viewer_email = login_id.lower()
      self.viewer_user_id = uid
      self.viewer_id = uid

      # LINE WORKS直接認証対応…LINE WORKSのSAML設定画面の「TEST」ボタンクリック時の対応 2019.06.13
      if not for_lineworks_test:

        # 認証情報など登録
        user_email = self.viewer_email
        sp_user_email = user_email.split('@')
        target_domain = ''
        if len(sp_user_email) >= 2:
          target_domain = sp_user_email[1].lower()
        logging.info('target_domain=' + target_domain)

        if not for_setup:
          host_name = domain_row.sso_entity_id
        else:
          host_name = sso_entity_id
        logging.info('host_name=' + str(host_name))
        if self.viewer_user_id is not None and self.viewer_user_id != '':
          # auth_token_living_days = 1
          rc = sateraito_func.RequestChecker()
          user_token = rc.registOrUpdateUserEntry(tenant_or_domain, user_email, target_domain, self.viewer_user_id,
                                                  host_name, self.viewer_user_id, is_admin)

        if not for_setup:
          sateraito_func.registDomainEntry(tenant_or_domain, tenant_or_domain, user_email)
          viewer_email_domain = target_domain
          if viewer_email_domain != tenant_or_domain:
            # プライマリドメインのネームスペースにセカンダリドメインレコードを登録するように修正 2017.11.09
            # sateraito_func.registDomainEntry(tenant_or_domain, viewer_email_domain, user_email)
            sateraito_func.registDomainEntry(tenant_or_domain, viewer_email_domain, user_email,
                                             not_send_setup_mail=True)

      # LINE WORKS直接認証対応…LINE WORKSのSAML設定画面の「TEST」ボタンクリック時の対応 2019.06.13
      if for_lineworks_test:
        hl = sateraito_inc.DEFAULT_LANGUAGE
        user_language = sateraito_func.getActiveLanguage('', hl=hl)
        my_lang = sateraito_func.MyLang(user_language)
        self.setSession('msg', my_lang.getMsg('LINEWORKS_SAMLTEST_SUCCEED'))
        info_page_url = sateraito_inc.custom_domain_my_site_url + '/info'
        info_page_url = UcfUtil.appendQueryString(info_page_url, 'hl', hl)
        self.redirect(str(info_page_url))
        return

      # 本来飛びたいページのURLを取得してリダイレクト
      if not for_setup:
        if relay_state != '':
          redirect_url = relay_state
        else:
          redirect_url = '/'
        # 高速化オプション対応：oidcパラメータを付与 2017.03.12
        redirect_url = UcfUtil.appendQueryString(redirect_url, 'oidc', 'cb')
      else:
        redirect_url = sateraito_inc.custom_domain_my_site_url + '/' + contract_entry.oem_company_code + '/' + contract_entry.sp_code + '/contract/' + contract_entry.tenant + '/xtregist'
        redirect_url = UcfUtil.appendQueryString(redirect_url, 'state', relay_state)

      logging.info('redirect_url=' + redirect_url)
      self.redirect(str(redirect_url))
    except Exception as e:
      logging.exception(e)
      self.response.write('faital error occured.')
      pass


def add_url_rules(app):
  app.add_url_rule('/<string:tenant>/saml/acs', view_func=AcsPage.as_view('SamlAcsPage'))
