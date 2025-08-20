#!/usr/bin/python
# coding: utf-8
#######################################
# 申込ページ（サテライトポータルサイト版、Works Mobile版）
#######################################

import os, re
import json
import jinja2
# import webapp2

# GAEGEN2対応:独自ロガー
# import logging
import sateraito_logger as logging

import datetime
import urllib
from google.appengine.api import namespace_manager
from google.appengine.api import memcache
from ucf.utils.ucfutil import UcfUtil
from ucf.utils import jinjacustomfilters
# GAEGEN2対応：SAML、SSO連携対応
from ucf.utils.ssofunc import SamlAuthnRequest  # LINE WORKS直接認証対応 2019.06.13
from ucf.utils import ssofunc
import sateraito_inc
import sateraito_db
import sateraito_func
import sateraito_page
import oem_func

cwd = os.path.dirname(__file__)
path = os.path.join(cwd, 'templates')
bcc = jinja2.MemcachedBytecodeCache(client=memcache.Client(), prefix='jinja2/bytecode/', timeout=None)
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path), auto_reload=False, bytecode_cache=bcc)
jinjacustomfilters.registCustomFilters(jinja_environment)


# G Suite 版申込ページ対応 2017.06.05
# class _ContractPage(sateraito_page._BasePage):
class _ContractPage(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):
  pass


# セットアップ入力画面
class RequestPage(_ContractPage):

  def renderPage(self, oem_company_code, sp_code, hl, user_language, my_lang, addon_tenant_status='',
                 sso_tenant_status='', vc_msgs=None):
    template_filename = 'contract_request.html'
    template = jinja_environment.get_template(template_filename)

    lang = my_lang.getMsgs()

    data = {
      'tenant': self.request.get('tenant'),
      'ssite_tenant': self.request.get('ssite_tenant'),
      'sso_for_authorize': self.request.get('sso_for_authorize'),
      'sso_tenant': self.request.get('sso_tenant'),
      # 'sso_public_key':self.request.get('sso_public_key'),					# OIDCSSO対応…申込時には不要に.SSOからのOIDCコールバック時にセットされる
      'worksmobile_domain': self.request.get('worksmobile_domain'),
      'worksmobile_saml_url': self.request.get('worksmobile_saml_url'),  # LINE WORKS直接認証対応 2019.06.13
      'worksmobile_saml_issuer': self.request.get('worksmobile_saml_issuer'),  # LINE WORKS直接認証対応 2019.06.13
      'worksmobile_saml_public_key': self.request.get('worksmobile_saml_public_key'),  # LINE WORKS直接認証対応 2019.06.13
      'workplace_domain': self.request.get('workplace_domain'),  # Workplace対応 2017.09.13
      'company_name': self.request.get('company_name'),
      'tanto_name': self.request.get('tanto_name'),
      'contact_mail_address': self.request.get('contact_mail_address'),
      'contact_tel_no': self.request.get('contact_tel_no'),
      'contact_prospective_account_num': self.request.get('contact_prospective_account_num'),
      # G Suite 版申込ページ対応…見込みアカウント数対応 2017.06.05
      'sso_operator_id': self.request.get('sso_operator_id'),
      'sso_operator_pwd': self.request.get('sso_operator_pwd'),
      'sso_tenant_status': sso_tenant_status,
      'addon_tenant_status': addon_tenant_status,
      'debug_mode': sateraito_inc.debug_mode,
      'sp_entity_id': sateraito_func.SP_ENTITY_ID,  # LINE WORKS直接認証対応 2019.06.13
      'lineworks_entity_id_prefix': sateraito_func.LINEWORKS_ENTITY_ID_PREFIX,  # LINE WORKS直接認証対応 2019.06.13
      'lineworks_saml_url_prefix': sateraito_func.LINEWORKS_SAML_URL_PREFIX,  # LINE WORKS直接認証対応 2019.06.13
      'my_site_url': sateraito_inc.my_site_url if sp_code == oem_func.SP_CODE_GSUITE else sateraito_inc.custom_domain_my_site_url,
      # LINE WORKS直接認証対応 2019.06.13
      'my_site_url_for_static': sateraito_inc.my_site_url if sp_code == oem_func.SP_CODE_GSUITE else sateraito_inc.custom_domain_my_site_url,
      # 'agreement_policy':self.request.get('agreement_policy'),
    }

    # G Suite 版申込ページ対応…G Suite 版はカスタムドメインを使わないので 2017.06.05
    # url_to_post = sateraito_inc.custom_domain_my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/request'
    if sp_code == oem_func.SP_CODE_GSUITE:
      url_to_post = sateraito_inc.my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/request'
    else:
      url_to_post = sateraito_inc.custom_domain_my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/request'

    values = {
      'url_to_post': url_to_post,
      'lang': lang,
      'hl': hl,
      'user_lang': user_language,
      'data': data,
      'vc_msgs': vc_msgs,
      'oem_company_code': oem_company_code,
      'sp_code': sp_code,
      'version': sateraito_func.getScriptVersionQuery(),
      'is_free_edition': sateraito_inc.IS_FREE_EDITION,
    }
    # render page
    # self.response.out.write(template.render(values))
    return template.render(values)

  @sateraito_page.convert_result_none_to_empty_str
  def get(self, oem_company_code, sp_code):  # g2対応 getとpostの両方あるのでdoActionにはしない
    logging.debug('**** requests *********************')
    logging.debug(self.request)
    hl = self.request.get('hl')
    if hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE
    user_language = sateraito_func.getActiveLanguage(hl, hl=sateraito_inc.DEFAULT_LANGUAGE)
    logging.debug('user_language=' + user_language)
    my_lang = sateraito_func.MyLang(user_language)
    lang = my_lang.getMsgs()

    # G Suite 版申込ページ対応…エラーページ対応 2017.06.05
    if sp_code == oem_func.SP_CODE_GSUITE:
      error_page_url = sateraito_inc.my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/failed'
    else:
      error_page_url = sateraito_inc.custom_domain_my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/failed'
    error_page_url = UcfUtil.appendQueryString(error_page_url, 'hl', hl)

    # OEMコードチェック＆SPコードチェック
    if not oem_func.isValidOEMCompanyCode(oem_company_code) or not oem_func.isValidSPCode(oem_company_code, sp_code):
      # G Suite 版申込ページ対応…エラーページ対応 2017.06.05
      self.session['error_msg'] = my_lang.getMsg('MSG_INVALID_ACCESS')
      self.redirect(str(error_page_url))
      # template_filename = 'contract_failed.html'
      # template = jinja_environment.get_template(template_filename)
      # values = {
      #		'lang': lang,
      #		'error_msg': my_lang.getMsg('MSG_INVALID_ACCESS'),
      #		}
      # self.response.out.write(template.render(values))
      return

    return self.renderPage(oem_company_code, sp_code, hl, user_language, my_lang)

  @sateraito_page.convert_result_none_to_empty_str
  def post(self, oem_company_code, sp_code):

    logging.debug('**** requests *********************')
    logging.debug(self.request)
    hl = self.request.get('hl')
    if hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE
    user_language = sateraito_func.getActiveLanguage(hl, hl=sateraito_inc.DEFAULT_LANGUAGE)
    logging.debug('user_language=' + user_language)
    my_lang = sateraito_func.MyLang(user_language)
    lang = my_lang.getMsgs()

    # G Suite 版申込ページ対応…エラーページ対応 2017.06.05
    if sp_code == oem_func.SP_CODE_GSUITE:
      error_page_url = sateraito_inc.my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/failed'
    else:
      error_page_url = sateraito_inc.custom_domain_my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/failed'
    error_page_url = UcfUtil.appendQueryString(error_page_url, 'hl', hl)

    # OEMコードチェック＆SPコードチェック
    if not oem_func.isValidOEMCompanyCode(oem_company_code) or not oem_func.isValidSPCode(oem_company_code, sp_code):
      # G Suite 版申込ページ対応…エラーページ対応 2017.06.05
      self.session['error_msg'] = my_lang.getMsg('MSG_INVALID_ACCESS')
      self.redirect(str(error_page_url))
      # template_filename = 'contract_failed.html'
      # template = jinja_environment.get_template(template_filename)
      # values = {
      #		'lang': lang,
      #		'error_msg': my_lang.getMsg('MSG_INVALID_ACCESS'),
      #		}
      # self.response.out.write(template.render(values))
      return

    # get params
    tenant = self.request.get('tenant')
    tenant = tenant.strip().lower()
    ssite_tenant = self.request.get('ssite_tenant')
    sso_for_authorize = self.request.get('sso_for_authorize')
    sso_tenant = self.request.get('sso_tenant')
    worksmobile_domain = self.request.get('worksmobile_domain')
    worksmobile_saml_url = self.request.get('worksmobile_saml_url')  # LINE WORKS直接認証対応 2019.06.13
    worksmobile_saml_issuer = self.request.get('worksmobile_saml_issuer')  # LINE WORKS直接認証対応 2019.06.13
    worksmobile_saml_public_key = self.request.get('worksmobile_saml_public_key')  # LINE WORKS直接認証対応 2019.06.13
    workplace_domain = self.request.get('workplace_domain')  # Workplace対応 2017.09.13
    # sso_public_key = self.request.get('sso_public_key')					# OIDCSSO対応…申込時には不要に.SSOからのOIDCコールバック時にセットされる
    company_name = self.request.get('company_name')
    tanto_name = self.request.get('tanto_name')
    contact_mail_address = self.request.get('contact_mail_address')
    contact_tel_no = self.request.get('contact_tel_no')
    contact_prospective_account_num = self.request.get('contact_prospective_account_num')  # G Suite 版申込ページ対応…見込みアカウント数対応 2017.06.05
    sso_operator_id = self.request.get('sso_operator_id')
    sso_operator_pwd = self.request.get('sso_operator_pwd')
    # agreement_policy = self.request.get('agreement_policy')
    # 画面上でのステータスを一応持ちまわる
    addon_tenant_status = self.request.get('addon_tenant_status')
    sso_tenant_status = self.request.get('sso_tenant_status')

    is_error = False
    vc_msgs = []
    # G Suite 版申込ページ対応…見込みアカウント数対応 2017.06.05
    # if not is_error and (tenant.strip() == '' or company_name.strip() == '' or tanto_name.strip() == '' or contact_mail_address.strip() == '' or contact_tel_no.strip() == ''):
    if not is_error and (tenant.strip() == '' or company_name.strip() == '' or tanto_name.strip() == '' or contact_mail_address.strip() == '' or contact_tel_no.strip() == '' or contact_prospective_account_num.strip() == ''):
      vc_msgs.append(my_lang.getMsg('INPUT_REQUIRED'))
      is_error = True
    if not is_error and (sp_code == oem_func.SP_CODE_SSITE and (ssite_tenant.strip() == '')):
      vc_msgs.append(my_lang.getMsg('INPUT_REQUIRED'))
      is_error = True
    # 申込簡単化対応 2018.02.05
    # if not is_error and (sp_code == oem_func.SP_CODE_WORKSMOBILE and (sso_for_authorize.strip() == '' or sso_tenant.strip() == '' or worksmobile_domain.strip() == '' or sso_public_key.strip() == '')):
    # LINE WORKS直接認証対応 2019.06.13
    # if not is_error and (sp_code == oem_func.SP_CODE_WORKSMOBILE and (sso_for_authorize.strip() == '' or sso_tenant.strip() == '')):
    if not is_error and (sp_code == oem_func.SP_CODE_WORKSMOBILE and (worksmobile_domain.strip() == '' or worksmobile_saml_url.strip() == '' or worksmobile_saml_issuer.strip() == '' or worksmobile_saml_public_key.strip() == '')):
      vc_msgs.append(my_lang.getMsg('INPUT_REQUIRED'))
      is_error = True
    # Workplace対応 2017.09.13
    # 申込簡単化対応 2018.02.05
    # if not is_error and (sp_code == oem_func.SP_CODE_WORKPLACE and (sso_for_authorize.strip() == '' or sso_tenant.strip() == '' or workplace_domain.strip() == '' or sso_public_key.strip() == '')):
    if not is_error and (sp_code == oem_func.SP_CODE_WORKPLACE and (sso_for_authorize.strip() == '' or sso_tenant.strip() == '')):
      vc_msgs.append(my_lang.getMsg('INPUT_REQUIRED'))
      is_error = True
    # 申込簡単化対応 2018.02.05
    # if not is_error and (agreement_policy != 'AGREEMENT'):
    #	vc_msgs.append(my_lang.getMsg('NEED_AGREEMENT_POLICY'))
    #	is_error = True

    # テナントが既に登録されていないかチェック
    if not sateraito_func.isValidNamespace(tenant):
      addon_tenant_status = 'invalid_format'
      is_error = True
    if not is_error:
      tenant_entry = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant)
      if tenant_entry is not None:
        addon_tenant_status = 'already_exist'
        vc_msgs.append(my_lang.getMsg('ALREADY_REGIST_TENANT_NAME'))
        is_error = True

    is_need_regist_new_sso_tenant = False
    # LINE WORKS直接認証対応 2019.06.13
    # if not is_error and sp_code in [oem_func.SP_CODE_WORKSMOBILE, oem_func.SP_CODE_WORKPLACE]:
    if not is_error and sp_code in [oem_func.SP_CODE_WORKPLACE]:
      # SSO側テナントが既に登録されていないかチェック
      if not is_error:
        if not sateraito_func.isValidNamespace(sso_tenant):
          sso_tenant_status = 'invalid_format'
          is_error = True
      if not is_error:
        sso_fqdn = sateraito_func.getSSOFQDN(sso_for_authorize)
        sso_api_results = ssofunc.checkSSOTenantExist(sso_fqdn, sso_tenant)
        logging.info(sso_api_results)
        if sso_api_results.get('code', '') != 0:
          logging.error(sso_api_results.get('msg', ''))
          vc_msgs.append(sso_api_results.get('msg', ''))
          is_error = True
        else:
          is_tenant_exist = sso_api_results.get('is_tenant_exist')
          if is_tenant_exist:
            sso_tenant_status = 'already_exist'
          else:
            if sso_for_authorize not in ['WORKPLACE', 'WORKSMOBILE']:
              vc_msgs.append(my_lang.getMsg('NOTFOUND_SSO_DOMAIN'))
              is_error = True
            elif sso_operator_id.strip() == '' or sso_operator_pwd.strip() == '':
              vc_msgs.append(my_lang.getMsg('INPUT_REQUIRED_SSO_OPERATOR'))
              is_error = True
          if not is_tenant_exist and sso_for_authorize in ['WORKPLACE', 'WORKSMOBILE']:
            is_need_regist_new_sso_tenant = True

    if is_error:
      return self.renderPage(oem_company_code, sp_code, hl, user_language, my_lang,
                             addon_tenant_status=addon_tenant_status, sso_tenant_status=sso_tenant_status,
                             vc_msgs=vc_msgs)
    # SSOにテナントを新規登録（G Suite 版SSOの場合は行わない。ここには入らない）
    # LINE WORKS直接認証対応 2019.06.13
    # if is_need_regist_new_sso_tenant and sp_code in [oem_func.SP_CODE_WORKSMOBILE, oem_func.SP_CODE_WORKPLACE]:
    if is_need_regist_new_sso_tenant and sp_code in [oem_func.SP_CODE_WORKPLACE]:
      sso_fqdn = sateraito_func.getSSOFQDN(sso_for_authorize)
      sso_api_results = ssofunc.createSSONewTenant(sso_fqdn, sso_tenant, sso_operator_id, sso_operator_pwd,
                                                   oem_company_code, sp_code, hl, user_language, company_name,
                                                   tanto_name, contact_mail_address, contact_tel_no,
                                                   contact_prospective_account_num)
      if sso_api_results.get('code', '') != 0:
        logging.error(sso_api_results)
        vc_msgs.append(my_lang.getMsg('FAILED_CREATE_SSO_TENANT') + ' ' + sso_api_results.get('msg', ''))
        return self.renderPage(oem_company_code, sp_code, hl, user_language, my_lang,
                               addon_tenant_status=addon_tenant_status, sso_tenant_status=sso_tenant_status,
                               vc_msgs=vc_msgs)

    # サードパーティCookie無効時に403ではなくメッセージを出す対応（stateに情報を含めてoidccallback側で制御）
    info = 'wep=1&hl=' + sateraito_func.getActiveLanguage('', hl=hl)
    # OIDCSSO対応
    if sp_code in [oem_func.SP_CODE_WORKSMOBILE, oem_func.SP_CODE_WORKPLACE]:
      # info += '&sso4auth=' + sso_for_authorize
      info += '&authkind=setup'
    info_base64 = UcfUtil.base64Encode(info)
    state = 'state-' + info_base64 + '-' + sateraito_func.dateString() + sateraito_func.randomString()
    logging.info('state=' + state)

    # state or tenant をキーに担当者情報などを一時テーブルにセット
    sateraito_func.setNamespace(tenant, '')
    contract_entry = sateraito_db.TenantContractEntry()
    contract_entry.oem_company_code = oem_company_code
    contract_entry.sp_code = sp_code
    contract_entry.state = state
    contract_entry.tenant = tenant
    contract_entry.ssite_tenant = ssite_tenant
    contract_entry.sso_for_authorize = sso_for_authorize
    contract_entry.sso_tenant = sso_tenant
    contract_entry.worksmobile_domain = worksmobile_domain
    contract_entry.worksmobile_saml_url = worksmobile_saml_url  # LINE WORKS直接認証対応 2019.06.13
    contract_entry.worksmobile_saml_issuer = worksmobile_saml_issuer  # LINE WORKS直接認証対応 2019.06.13
    contract_entry.sso_public_key = worksmobile_saml_public_key  # LINE WORKS直接認証対応 2019.06.13
    contract_entry.workplace_domain = workplace_domain  # Workplace対応 2017.09.13
    # contract_entry.sso_public_key = sso_public_key			# OIDCSSO対応…申込時には不要に.SSOからのOIDCコールバック時にセットされる
    contract_entry.company_name = company_name.strip()
    contract_entry.tanto_name = tanto_name.strip()
    contract_entry.contact_mail_address = contact_mail_address.strip()
    contract_entry.contact_tel_no = contact_tel_no.strip()
    contract_entry.contact_prospective_account_num = contact_prospective_account_num.strip()  # G Suite 版申込ページ対応…見込みアカウント数対応 2017.06.05
    contract_entry.put()

    # 認証
    # サテライトポータルサイト（サテライトポータルでOIDC認証）
    if sp_code == oem_func.SP_CODE_SSITE:

      # セッションでもいいのだがタイムラグが気になるのでCookieにする
      expires = UcfUtil.add_hours(UcfUtil.getNow(), 1).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
      self.setCookie('oidc_state', str(state), expires=expires)

      # 認証後にもどってくる用URLを設定
      # url_to_go_after_oidc_login = self.request.url
      url_to_go_after_oidc_login = sateraito_inc.custom_domain_my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/' + tenant + '/xtregist'
      # url_to_go_after_oidc_login = UcfUtil.appendQueryString(url_to_go_after_oidc_login, 'hl', hl)
      url_to_go_after_oidc_login = UcfUtil.appendQueryString(url_to_go_after_oidc_login, 'state', state)

      # セッションでもいいのだがタイムラグが気になるのでCookieにする
      # self.session['url_to_go_after_oidc_login'] = url_to_go_after_oidc_login
      # for 'multiple iframe gadget in a page' case login
      # self.setCookie(urllib.quote(state), str(url_to_go_after_oidc_login), living_sec=30)
      # self.setCookie(urllib.quote(state), str(url_to_go_after_oidc_login), expires=expires)  # g2対応
      self.setCookie(urllib.parse.quote(state), str(url_to_go_after_oidc_login), expires=expires)

      query_params = {}
      query_params['state'] = state
      # OIDCセキュリティ強化対応：nonceチェックを導入 2016.12.08
      nonce = UcfUtil.guid()
      self.session['nonce-' + state] = nonce
      query_params['nonce'] = nonce
      query_params['response_type'] = 'code id_token'
      query_params['client_id'] = sateraito_inc.SSITE_OIDC_CLIENT_ID
      query_params['redirect_uri'] = sateraito_inc.custom_domain_my_site_url + '/ssite/oidccallback'
      query_params['scope'] = 'openid'
      query_params['client_tenant'] = tenant  # SSITE独自クレーム. クライアント（アドオン）側のドメインをセット
      query_params['prompt'] = 'login'
      tenant_id = ssite_tenant  # SSITEのテナントID
      # url_to_go = sateraito_inc.SSITE_ROOT_URL + '/' + tenant_id + '/oauth2/authorize?' + urllib.urlencode(query_params)
      url_to_go = sateraito_inc.SSITE_ROOT_URL + '/' + tenant_id + '/oauth2/authorize?' + urllib.parse.urlencode(
        query_params)
      auth_uri = str(url_to_go)
      logging.info('auth_uri=' + auth_uri)
      self.redirect(auth_uri)
      return

    # OIDCSSO対応
    # Works Mobile（SSOで認証）
    # Workplace対応 2017.09.13
    # elif sp_code == oem_func.SP_CODE_WORKSMOBILE:
    # LINE WORKS直接認証対応 2019.06.13
    # elif sp_code in [oem_func.SP_CODE_WORKSMOBILE, oem_func.SP_CODE_WORKPLACE]:
    elif sp_code in [oem_func.SP_CODE_WORKPLACE]:
      # OIDCSSO対応…セットアップ時はSAMLではなくOIDC認証に変更
      # sso_entity_id, sso_login_endpoint = sateraito_func.createSSOIdProviderInfo(contract_entry)
      ## シングルサインオンとのSAML連携
      # samlsettings = sateraito_func.getSamlSettings(sateraito_inc.custom_domain_my_site_url, tenant, sso_entity_id, sso_login_endpoint, contract_entry.sso_public_key)
      # saml_request = SamlAuthnRequest(samlsettings, force_authn=False, is_passive=False, set_nameid_policy=True)
      # saml_request.redirect_to_idp(self, relay_state=state)
      # return

      # セッションでもいいのだがタイムラグが気になるのでCookieにする
      expires = UcfUtil.add_hours(UcfUtil.getNow(), 1).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
      self.setCookie('oidc_state', str(state), expires=expires)

      # 認証後にもどってくる用URLを設定
      url_to_go_after_oidc_login = sateraito_inc.custom_domain_my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/' + tenant + '/xtregist'
      url_to_go_after_oidc_login = UcfUtil.appendQueryString(url_to_go_after_oidc_login, 'state', state)

      # セッションでもいいのだがタイムラグが気になるのでCookieにする
      # self.session['url_to_go_after_oidc_login'] = url_to_go_after_oidc_login
      # for 'multiple iframe gadget in a page' case login
      # self.setCookie(urllib.quote(state), str(url_to_go_after_oidc_login), living_sec=30)
      # self.setCookie(urllib.quote(state), str(url_to_go_after_oidc_login), expires=expires)  # g2対応
      self.setCookie(urllib.parse.quote(state), str(url_to_go_after_oidc_login), expires=expires)

      query_params = {}
      query_params['state'] = state
      # OIDCセキュリティ強化対応：nonceチェックを導入 2016.12.08
      nonce = UcfUtil.guid()
      self.session['nonce-' + state] = nonce
      query_params['nonce'] = nonce
      query_params['response_type'] = 'code id_token'
      query_params['client_id'] = sateraito_inc.SSO_OIDC_CLIENT_ID
      query_params['redirect_uri'] = sateraito_inc.custom_domain_my_site_url + '/sso/oidccallback'
      query_params['scope'] = 'openid'
      query_params['client_tenant'] = tenant  # SSO独自クレーム. クライアント（アドオン）側のドメインをセット
      query_params['prompt'] = 'login'
      tenant_id = sso_tenant  # SSOのテナントID
      # url_to_go = 'https://' + sateraito_func.getSSOFQDN(sso_for_authorize) + '/a/' + tenant_id + '/oauth2/authorize?' + urllib.urlencode(query_params)
      url_to_go = 'https://' + sateraito_func.getSSOFQDN(
        sso_for_authorize) + '/a/' + tenant_id + '/oauth2/authorize?' + urllib.parse.urlencode(query_params)
      auth_uri = str(url_to_go)
      logging.info('auth_uri=' + auth_uri)
      self.redirect(auth_uri)
      return

    # LINE WORKS直接認証対応…LINE WORKS でSAML認証 2019.06.13
    elif sp_code in [oem_func.SP_CODE_WORKSMOBILE]:
      sso_entity_id, sso_login_endpoint = sateraito_func.createSSOIdProviderInfo(contract_entry)
      samlsettings = sateraito_func.getSamlSettings(sateraito_inc.custom_domain_my_site_url, tenant, sso_entity_id,
                                                    sso_login_endpoint, contract_entry.sso_public_key)
      saml_request = SamlAuthnRequest(samlsettings, force_authn=False, is_passive=False, set_nameid_policy=True)
      saml_request.redirect_to_idp(self, relay_state=state)
      return

    # G Suite 版申込ページ対応…G Suite 管理者でOIDC認証 2017.06.05
    elif sp_code == oem_func.SP_CODE_GSUITE:

      # 認証後にもどってくる用URLを設定
      url_to_go_after_oidc_login = sateraito_inc.my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/' + tenant + '/xtregist'
      add_querys = [
        ['state', state]
      ]
      # check OpenID Connect login
      google_apps_domain = tenant
      is_ok, body_for_not_ok = self._OIDCAutoLogin(google_apps_domain, with_error_page=True,
                                                   error_page_url=error_page_url, with_admin_consent=True,
                                                   with_regist_user_entry=True, is_force_auth=True, hl=hl,
                                                   url_to_go_after_oidc_login=url_to_go_after_oidc_login,
                                                   add_querys=add_querys)
      if not is_ok:
        return body_for_not_ok
      return


# 申込簡単化対応 2018.02.05 … アドオン及びSSOで入力テナントIDが使えるかをチェック
# TODO CSRFチェック（存在チェックだけなのでいいかな...）
class XtCheckTenantPage(_ContractPage):

  def doAction(self, oem_company_code, sp_code):
    params = {}
    params['addon_tenant_status'] = ''
    params['sso_tenant_status'] = ''

    is_only_addon = 'on' == self.request.get('is_only_addon')  # LINE WORKS直接認証対応 2019.06.13
    tenant = self.request.get('tenant')
    sso_tenant = self.request.get('sso_tenant')
    sso_for_authorize = self.request.get('sso_for_authorize')

    if not sateraito_func.isValidNamespace(tenant):
      params['addon_tenant_status'] = 'invalid_format'

    # LINE WORKS直接認証対応 2019.06.13
    # if not sateraito_func.isValidNamespace(sso_tenant):
    if not is_only_addon and not sateraito_func.isValidNamespace(sso_tenant):
      params['sso_tenant_status'] = 'invalid_format'

    # １．アドオン側テナントが既に登録されていないかチェック
    if params['addon_tenant_status'] == '':
      tenant_entry = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant)
      if tenant_entry is not None:
        # vc_msgs.append(my_lang.getMsg('ALREADY_REGIST_TENANT_NAME'))
        # self.outputResult(return_code=100, error_code='tenant_already_exist_in_addon', error_msg='', params=params)
        params['addon_tenant_status'] = 'already_exist'

    if params['addon_tenant_status'] == '':
      params['addon_tenant_status'] = 'no_exist_tenant'

    # LINE WORKS直接認証対応 2019.06.13
    if not is_only_addon:
      if params['sso_tenant_status'] == '':
        # ２．SSO側テナントが既に登録されていないかチェック
        sso_fqdn = sateraito_func.getSSOFQDN(sso_for_authorize)
        sso_api_results = ssofunc.checkSSOTenantExist(sso_fqdn, sso_tenant)
        if sso_api_results.get('code', '') != 0:
          logging.error(sso_api_results.get('msg', ''))
        else:
          is_tenant_exist = sso_api_results.get('is_tenant_exist')
          if is_tenant_exist:
            params['sso_tenant_status'] = 'already_exist'

      if params['sso_tenant_status'] == '':
        params['sso_tenant_status'] = 'no_exist_tenant'

    return self.outputResult(return_code=0, error_msg='', params=params)

  def outputResult(self, return_code, error_msg='', params=None):
    results = {} if params is None else params
    results['code'] = return_code
    results['error_msg'] = error_msg
    # if return_code != 0:
    logging.info(results)
    # self.response.out.write(json.JSONEncoder().encode(results))
    return json.JSONEncoder().encode(results)


# セットアップ処理画面
class XtRegistPage(_ContractPage):

  def doAction(self, oem_company_code, sp_code, tenant):

    logging.debug('**** requests *********************')
    logging.debug(self.request)
    sateraito_func.setNamespace(tenant, '')

    # 登録処理
    user_email = self.session.get('viewer_email', '')
    logging.info('user_email=' + str(user_email))
    state = self.request.get('state')
    logging.info('state=' + str(state))
    # is_admin = self.session.get('is_admin', False)
    # logging.info('is_admin=' + str(is_admin))

    hl = None
    states = state.split('-')
    if len(states) >= 3 and states[1] != '':
      info = UcfUtil.base64Decode(states[1])
      logging.debug('info=' + info)
      infos = info.split('&')
      for item in infos:
        ary = item.split('=')
        k = ary[0]
        v = ary[1] if len(ary) >= 2 else ''
        if k == 'hl':
          hl = v
    logging.debug('hl=' + str(hl))
    if hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE
    user_language = sateraito_func.getActiveLanguage(hl, hl=sateraito_inc.DEFAULT_LANGUAGE)
    logging.debug('user_language=' + user_language)
    my_lang = sateraito_func.MyLang(user_language)
    lang = my_lang.getMsgs()

    # G Suite 版申込ページ対応…エラーページ対応 2017.06.05
    if sp_code == oem_func.SP_CODE_GSUITE:
      error_page_url = sateraito_inc.my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/failed'
    else:
      error_page_url = sateraito_inc.custom_domain_my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/failed'
    error_page_url = UcfUtil.appendQueryString(error_page_url, 'hl', hl)

    user_entry = sateraito_db.GoogleAppsUserEntry.getInstance(tenant, user_email)
    if user_entry is None:
      logging.error('user_entry not found')
      # G Suite 版申込ページ対応…エラーページ対応 2017.06.05
      self.session['error_msg'] = my_lang.getMsg('INVALID_AUTH_CONTRACT')
      self.redirect(str(error_page_url))
      # template_filename = 'contract_failed.html'
      # template = jinja_environment.get_template(template_filename)
      # values = {
      #		'lang': lang,
      #		'error_msg': my_lang.getMsg('INVALID_AUTH_CONTRACT'),
      #		}
      # self.response.out.write(template.render(values))
      return

    # 管理者じゃなければ
    if not user_entry.is_apps_admin:
      logging.error('the user is not admin.')
      # G Suite 版申込ページ対応…エラーページ対応 2017.06.05
      self.session['error_msg'] = my_lang.getMsg('INVALID_AUTH_CONTRACT_BY_NOT_ADMIN')
      self.redirect(str(error_page_url))
      # template_filename = 'contract_failed.html'
      # template = jinja_environment.get_template(template_filename)
      # values = {
      #		'lang': lang,
      #		'error_msg': my_lang.getMsg('INVALID_AUTH_CONTRACT_BY_NOT_ADMIN'),
      #		}
      # self.response.out.write(template.render(values))
      return

    # state or tenant をキーに担当者情報などを一時テーブルから取得（↓でDomainEntryへの登録や営業メンバーにメール送信）
    contract_entry = sateraito_db.TenantContractEntry.getInstanceByState(state)
    if contract_entry is None or contract_entry.oem_company_code != oem_company_code or contract_entry.sp_code != sp_code:
      logging.error('invalid sp_code or oem_company_code.')
      # G Suite 版申込ページ対応…エラーページ対応 2017.06.05
      self.session['error_msg'] = my_lang.getMsg('MSG_INVALID_ACCESS')
      self.redirect(str(error_page_url))
      # template_filename = 'contract_failed.html'
      # template = jinja_environment.get_template(template_filename)
      # values = {
      #		'lang': lang,
      #		'error_msg': my_lang.getMsg('MSG_INVALID_ACCESS'),
      #		}
      # self.response.out.write(template.render(values))
      return

    contract_entry.is_verified = True  # 一応認証済みのフラグを立てておく
    contract_entry.put()

    sso_entity_id, sso_login_endpoint = sateraito_func.createSSOIdProviderInfo(contract_entry)

    # テナント情報取得
    tenant_entry = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant)
    logging.info('tenant_entry is None:' + str(tenant_entry is None))
    # 新規登録

    is_create_tenant_entry = False  # サンキューメールとセットアップ通知の統合対応 2017.09.15
    if tenant_entry is None:
      # create tenant entry and set oidc login flag on
      # G Suite 版申込ページ対応…G Suite 版の場合は、使用期限（30日）をセットしない 2017.06.05
      # tenant_entry = sateraito_func.registDomainEntry(tenant, tenant, user_email, contract_entry=contract_entry, is_set_dates=True)
      # GWS有償版申し込みページ対応…有償版は使用期限をセット 2022/09/13
      # is_set_dates = sp_code != oem_func.SP_CODE_GSUITE
      is_set_dates = sp_code != oem_func.SP_CODE_GSUITE or not sateraito_inc.IS_FREE_EDITION
      # サンキューメールとセットアップ通知の統合対応…registDomainEntry内でメール送信しないように対応 2017.09.15
      # tenant_entry = sateraito_func.registDomainEntry(tenant, tenant, user_email, contract_entry=contract_entry, is_set_dates=is_set_dates, not_use_memcache=True)
      tenant_entry = sateraito_func.registDomainEntry(tenant, tenant, user_email, contract_entry=contract_entry,
                                                      is_set_dates=is_set_dates, not_use_memcache=True,
                                                      not_send_setup_mail=True)
      is_create_tenant_entry = True  # サンキューメールとセットアップ通知の統合対応 2017.09.15

    ## G Suite 版申込ページ対応…ブラウザの戻るボタンで戻って処理した場合などにエラーしないようにチェック
    # if tenant_entry is None:
    #	logging.error('tenant entry is None. invalid process.')
    #	self.session['error_msg'] = my_lang.getMsg('MSG_INVALID_ACCESS')
    #	self.redirect(str(error_page_url))
    #	return

    # 各種情報をセット
    tenant_entry.is_ssite_tenant = contract_entry.sp_code in [oem_func.SP_CODE_SSITE]
    tenant_entry.ssite_tenant_id = contract_entry.ssite_tenant
    # Workplace対応 2017.09.13
    # tenant_entry.is_sso_tenant = contract_entry.sp_code in [oem_func.SP_CODE_WORKSMOBILE]
    tenant_entry.is_sso_tenant = contract_entry.sp_code in [oem_func.SP_CODE_WORKSMOBILE, oem_func.SP_CODE_WORKPLACE]
    tenant_entry.sso_entity_id = sso_entity_id
    tenant_entry.sso_login_endpoint = sso_login_endpoint
    tenant_entry.sso_public_key = contract_entry.sso_public_key  # OIDCSSO対応…SSOからのOIDCコールバック時にcontract_entryにセットされるのでここでTenantEntryにセット可能
    # 申込ページによって文字コードも切り替え（少し日本語優先に戻す対応） 2017.06.05
    tenant_entry.default_timezone = sateraito_func.getActiveTimeZone('Asia/Tokyo' if hl == 'ja' else 'Etc/UTC')
    tenant_entry.default_encoding = 'SJIS' if hl == 'ja' else 'UTF8'
    tenant_entry.put()

    # サンキューメール送信
    # サンキューメールとセットアップ通知の統合対応…↑ではなくここでメール送信 2017.09.15
    # sateraito_func.sendInstallNofificationMail(tenant_entry, contract_entry, my_lang)
    sateraito_func.sendThankyouMailAndSetupNotificationMail(tenant_entry, contract_entry, my_lang,
                                                            is_send_thankyou_mail=True,
                                                            is_send_setup_mail=is_create_tenant_entry)

    redirect_url = sateraito_inc.custom_domain_my_site_url + '/' + oem_company_code + '/' + sp_code + '/contract/' + tenant + '/thanks'
    redirect_url = UcfUtil.appendQueryString(redirect_url, 'hl', hl)
    self.redirect(str(redirect_url))
    return


# セットアップ完了画面
class ThanksPage(_ContractPage):

  def doAction(self, oem_company_code, sp_code, tenant):
    logging.debug('**** requests *********************')
    logging.debug(self.request)
    hl = self.request.get('hl')
    if hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE
    user_language = sateraito_func.getActiveLanguage('', hl=hl)
    logging.debug('user_language=' + user_language)
    my_lang = sateraito_func.MyLang(user_language)
    lang = my_lang.getMsgs()

    template_filename = 'contract_thanks.html'
    template = jinja_environment.get_template(template_filename)
    values = {
      'lang': lang,
      # G Suite 版申込ページ対応
      'hl': hl,
      'user_lang': user_language,
      'oem_company_code': oem_company_code,
      'sp_code': sp_code,
    }
    # self.response.out.write(template.render(values))
    return template.render(values)


# エラーページ（G Suite 版申込ページ対応）
class FailedPage(_ContractPage):

  def doAction(self, oem_company_code, sp_code):
    logging.debug('**** requests *********************')
    logging.debug(self.request)
    hl = self.request.get('hl')
    if hl == '':
      hl = sateraito_inc.DEFAULT_LANGUAGE
    user_language = sateraito_func.getActiveLanguage('', hl=hl)
    logging.debug('user_language=' + user_language)
    my_lang = sateraito_func.MyLang(user_language)
    lang = my_lang.getMsgs()

    error_msg = self.session.get('error_msg')
    template_filename = 'contract_failed.html'
    template = jinja_environment.get_template(template_filename)
    values = {
      'lang': lang,
      'hl': hl,
      'user_lang': user_language,
      'oem_company_code': oem_company_code,
      'sp_code': sp_code,
      'error_msg': error_msg,
    }
    # self.response.out.write(template.render(values))
    return template.render(values)


# app = webapp2.WSGIApplication([
# 	(r'/([^/]*)/([^/]*)/contract/request', RequestPage),
# 	(r'/([^/]*)/([^/]*)/contract/xtchecktenant', XtCheckTenantPage),		# 画面上からのAjaxによる入力チェック用…申込簡単化対応 2018.02.05
# 	(r'/([^/]*)/([^/]*)/contract/([^/]*)/xtregist', XtRegistPage),
# 	(r'/([^/]*)/([^/]*)/contract/([^/]*)/thanks', ThanksPage),
# 	(r'/([^/]*)/([^/]*)/contract/failed', FailedPage),				# G Suite 版申込ページ対応
# ], debug=sateraito_inc.debug_mode, config=sateraito_page.config)

def add_url_rules(app):
  app.add_url_rule('/<oem_company_code>/<sp_code>/contract/request',
                   view_func=RequestPage.as_view('ContractRequestPage'))
  app.add_url_rule('/<oem_company_code>/<sp_code>/contract/xtchecktenant',
                   view_func=XtCheckTenantPage.as_view(
                     'ContractXtCheckTenantPage'))  # 画面上からのAjaxによる入力チェック用…申込簡単化対応 2018.02.05
  app.add_url_rule('/<oem_company_code>/<sp_code>/contract/<tenant>/xtregist',
                   view_func=XtRegistPage.as_view('ContractXtRegistPage'))
  app.add_url_rule('/<oem_company_code>/<sp_code>/contract/<tenant>/thanks',
                   view_func=ThanksPage.as_view('ContractThanksPage'))
  app.add_url_rule('/<oem_company_code>/<sp_code>/contract/failed',
                   view_func=FailedPage.as_view('ContractFailedPage'))  # G Suite 版申込ページ対応
