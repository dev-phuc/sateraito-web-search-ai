#!/usr/bin/python
# coding: utf-8

__author__ = 'Tran Minh Phuc <phuc@vnd.sateraito.co.jp>'
'''
sateraito_db.py

@since: 2025-08-20
@version: 1.0.0
@author: Tran Minh Phuc
'''

import datetime, json

from dateutil import zoneinfo, tz
from google.appengine.api import namespace_manager

from sateraito_inc import developer_mode
if developer_mode:
    from google.cloud import ndb
    import memcache
else:
    from google.appengine.ext import ndb
    from google.appengine.api import memcache

import sateraito_inc
import sateraito_func
import sateraito_logger as logging

from sateraito_inc import NDB_MEMCACHE_TIMEOUT, DICT_MEMCACHE_TIMEOUT, DEFAULT_MAX_TOTAL_FILE_SIZE

DOWNLOAD_CSV_NAMESPACE = 'sateraito_download_csv'
LTCACHE_USER_LIST_UPDATING_KEY = 'ltcacheuserlistupdating'
LTCACHE_GROUP_LIST_UPDATING_KEY = 'ltcachegrouplistupdating'


# SSITE、SSOGadget対応：申込時の契約情報（一応一時テーブル扱い）
class TenantContractEntry(ndb.Model):
	state = ndb.StringProperty()
	tenant = ndb.StringProperty()
	sp_code = ndb.StringProperty()
	oem_company_code = ndb.StringProperty()
	ssite_tenant = ndb.StringProperty()
	sso_for_authorize = ndb.StringProperty()
	sso_tenant = ndb.StringProperty()
	sso_public_key = ndb.TextProperty()
	worksmobile_domain = ndb.StringProperty()
	worksmobile_saml_url = ndb.StringProperty()  # LINE WORKS直接認証対応 2019.06.13
	worksmobile_saml_issuer = ndb.StringProperty()  # LINE WORKS直接認証対応 2019.06.13
	worksmobile_saml_public_key = ndb.StringProperty()  # LINE WORKS直接認証対応 2019.06.13
	workplace_domain = ndb.StringProperty()  # Workplace対応 2017.09.13
	company_name = ndb.StringProperty()
	tanto_name = ndb.StringProperty()
	contact_mail_address = ndb.StringProperty()
	contact_tel_no = ndb.StringProperty()
	contact_prospective_account_num = ndb.StringProperty()  # G Suite 版申込ページ対応…見込みアカウント数対応 2017.06.05
	is_verified = ndb.BooleanProperty()
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)

	@classmethod
	def getInstanceByState(cls, state):
		# get datastore data
		q = cls.query()
		q = q.filter(cls.state == state)
		key = q.get(keys_only=True)
		row = key.get() if key is not None else None
		return row


class DomainAndAppId(ndb.Model):
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)
	google_apps_domain = ndb.StringProperty()
	app_id = ndb.StringProperty()

	@classmethod
	def addIfNotRegistered(cls, google_apps_domain, app_id, created_date=None):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace('')

		key_name = 'google_apps_domain=' + str(google_apps_domain) + '&app_id=' + app_id

		row = cls.get_by_id(key_name)
		if row is None:
			row = cls(id=key_name)
			row.google_apps_domain = google_apps_domain
			row.app_id = app_id
			if created_date is not None:
				row.created_date = created_date
			row.put()
		# set old namespace
		namespace_manager.set_namespace(old_namespace)

	@classmethod
	def isExists(cls, google_apps_domain, app_id):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace('')
		key_name = 'google_apps_domain=' + str(google_apps_domain) + '&app_id=' + app_id

		row = cls.get_by_id(key_name)
		is_exists = True
		if row is None:
			is_exists = False
		# set old namespace
		namespace_manager.set_namespace(old_namespace)
		return is_exists

class MultiDomainEntry(ndb.Model):
	# memcache entry expires in 10 min
	_memcache_expire_secs = 60 * 10

	created_date = ndb.DateTimeProperty(auto_now_add=True)
	primary_domain = ndb.StringProperty()
	sub_domain = ndb.StringProperty()

	# is_multidomain = ndb.BooleanProperty()

	@classmethod
	def getInstance(cls, sub_domain):

		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace('', '')

		q = cls.query()
		q = q.filter(MultiDomainEntry.sub_domain == sub_domain)
		row = q.get()
		namespace_manager.set_namespace(old_namespace)
		return row

	@classmethod
	def get_memcache_key(cls, subDomain):
		return 'class=MultiDomainEntry&subDomain=' + subDomain + '&g=2'

	@classmethod
	def getPrimaryDomain(cls, subDomain):
		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace('', '')

		strMemCacheKey = cls.get_memcache_key(subDomain)
		primaryDomain = memcache.get(strMemCacheKey, namespace="")
		if primaryDomain is None:
			logging.info('checkPrimaryDomain: memcache Not Found.')
			entity = cls.getInstance(subDomain)
			if entity is not None:
				primaryDomain = entity.primary_domain
			else:
				primaryDomain = subDomain

			memcache.set(strMemCacheKey, primaryDomain, namespace="", time=cls._memcache_expire_secs)
		else:
			pass
		namespace_manager.set_namespace(old_namespace)
		return primaryDomain

	# todo: edited by tan@vn.sateraito.co.jp

	@classmethod
	def setNameSpaceAndGetPrimaryDomain(cls, subDomain, onlyMultiDomain=True):
		if subDomain is None:
			return None

		primaryDomain = cls.getPrimaryDomain(subDomain)

		if (primaryDomain):
			if (sateraito_inc.USE_NAMESPACE):
				namespace_manager.set_namespace(primaryDomain)

			logging.info('setNameSpaceAndGetPrimaryDomain primary:' + primaryDomain);
		else:
			primaryDomain = subDomain
			if (sateraito_inc.USE_NAMESPACE):
				namespace_manager.set_namespace(subDomain)

		return primaryDomain

class GoogleAppsDomainEntry(ndb.Model):
	"""	Datastore class to store info about google apps domain
		This entity only exists in default app_id namespace
	"""
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)

	google_apps_domain = ndb.StringProperty()
	num_users = ndb.IntegerProperty()
	hide_ad = ndb.BooleanProperty()
	multi_domain_setting = ndb.BooleanProperty()
	secret_key = ndb.StringProperty()
	last_login_month = ndb.StringProperty()
	available_users = ndb.IntegerProperty()

	impersonate_email = ndb.StringProperty()
	is_oauth2_domain = ndb.BooleanProperty()

	is_ssite_tenant = ndb.BooleanProperty(default=False)
	ssite_tenant_id = ndb.StringProperty()
	is_sso_tenant = ndb.BooleanProperty(default=False)
	sso_entity_id = ndb.StringProperty()
	sso_login_endpoint = ndb.StringProperty()
	sso_public_key = ndb.TextProperty()
	is_free_mode = ndb.BooleanProperty()

	sp_code = ndb.StringProperty()
	oem_company_code = ndb.StringProperty()
	is_no_oem = ndb.BooleanProperty()  # OEM版アドオンの直契約対応：KDDI版アドオン環境で、KDDI管轄ではなくサテライト直契約の場合にTrue（これにより解約日などの連携を行わない制御をする）

	is_auto_create_impersonate_email = ndb.BooleanProperty()

	use_iframe_version_gadget = ndb.BooleanProperty()

	is_backup_available = ndb.BooleanProperty(default=False)  # バックアップツールによるバックアップが有効かどうか
	md5_suffix_key = ndb.StringProperty()  # for Sateraito EDI
	is_disable = ndb.BooleanProperty()  # このドメインを無効にする（契約解除、アンインストール時など）アドオンごとに制御できるようにブラックリストとダブルでチェック
	no_auto_logout = ndb.BooleanProperty()
	no_login_cache = ndb.BooleanProperty()  # SameSite対応の一環…高速化を標準とする対応 ログインキャッシュをOFFにするフラグ（高速化オプションの代わり）2019.12.28
	ssogadget_app_key = ndb.StringProperty()

	module_type = ndb.StringProperty()
	doc_save_terms = ndb.IntegerProperty()

	available_start_date = ndb.StringProperty()  # 利用開始日（YYYY/MM/DD 形式）
	charge_start_date = ndb.StringProperty()  # 課金開始日（YYYY/MM/DD 形式）
	cancel_date = ndb.StringProperty()  # 解約日（YYYY/MM/DD 形式）

	is_preview = ndb.BooleanProperty(default=True)
	attached_file_viewer_type = ndb.StringProperty(default='GOOGLEDRIVEVIEWER')  # 添付ファイルビューアーのタイプ（GOOGLEDRIVEVIEWER：Googleドライブビューアー、OFFICEVIEWER：Officeビューアー、SATERAITOVIEWER：独自ビューアー）※デフォルト＝GOOGLEDRIVEVIEWER

	mobile_sso_login = ndb.BooleanProperty(default=False)
	mobile_autologin_hours = ndb.IntegerProperty(default=336)  # 336 = 24 * 14
	mobile_session_minutes = ndb.IntegerProperty(default=30)
	mobile_loading_image = ndb.StringProperty(default='')

	def _pre_put_hook(self):
		# set to default app id namespace
		old_namespace = namespace_manager.get_namespace()
		google_apps_domain = sateraito_func.getDomainFromNamespace(old_namespace)
		namespace_manager.set_namespace(google_apps_domain)
		# clear memcache key
		memcache_key = GoogleAppsDomainEntry.getMemcacheKey(google_apps_domain, self.google_apps_domain)
		memcache.delete(memcache_key)
		# set old namespace
		namespace_manager.set_namespace(old_namespace)

	@classmethod
	def getById(cls, id):
		return cls.get_by_id(id, memcache_timeout=NDB_MEMCACHE_TIMEOUT)

	@classmethod
	def getMemcacheKey(cls, google_apps_domain, subdomain):
		if google_apps_domain == subdomain:
			subdomain = None
		# TODO:: only_dev
		return 'v3googleappsdomainentry.getdict?google_apps_domain=' + str(google_apps_domain) + '&subdomain=' + str(subdomain) + '&g=2'

	@classmethod
	def updateLastLoginMonth(cls, id):
		""" update last_login_month to current date
			if no need to update(last_login_month is already current), not update
			Return: True ... last_login_month is updated
							False .. last_login_month is not updated
		"""
		logging.info('updateLastLoginMonth:id=' + str(id))
		# set default app id namespace
		old_namespace = namespace_manager.get_namespace()
		google_apps_domain = sateraito_func.getDomainFromNamespace(old_namespace)
		namespace_manager.set_namespace(google_apps_domain)
		logging.info('updateLastLoginMonth:google_apps_domain=' + str(google_apps_domain))
		# update
		row = cls.getById(id)
		tz_utc = zoneinfo.gettz('UTC')
		current_time_utc = datetime.datetime.now(tz_utc)
		current_month = current_time_utc.strftime('%Y-%m')
		ret_val = False
		if (row.last_login_month is None) or (row.last_login_month != current_month):
			logging.info('updating GoogleAppsDomainEntry in updateLastLoginMonth')
			row.last_login_month = current_month
			row.put()
			ret_val = True
		# restore old namespace
		namespace_manager.set_namespace(old_namespace)
		return ret_val

	@classmethod
	def getDict(cls, google_apps_domain, subdomain=None):
		# GoogleAppsUserEntry only exists in default namespade(=google_apps_domain)
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)
		# check memcache
		memcache_key = cls.getMemcacheKey(google_apps_domain, subdomain)
		cached_dict = memcache.get(memcache_key)
		if cached_dict is not None:
			logging.info('GoogleAppsDomainEntry.getDict: found and respond cache')
			namespace_manager.set_namespace(old_namespace)
			return cached_dict
		# get data
		row = cls.getInstance(google_apps_domain, subdomain)
		if row is None:
			namespace_manager.set_namespace(old_namespace)
			return None
		row_dict = row.to_dict()
		row_dict['id'] = row.key.id()
		# set to memcache
		memcache.set(memcache_key, row_dict, time=DICT_MEMCACHE_TIMEOUT)
		namespace_manager.set_namespace(old_namespace)
		return row_dict

	@classmethod
	def getInstance(cls, google_apps_domain, subdomain=None, auto_create=False):

		# GoogleAppsUserEntry only exists in default namespade(=google_apps_domain)
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)

		q = cls.query()
		if subdomain is None:
			q = q.filter(cls.google_apps_domain == google_apps_domain)
		else:
			q = q.filter(cls.google_apps_domain == subdomain)
		row = None
		row_k = q.get(keys_only=True)
		if row_k is None:
			if auto_create:
				if subdomain is None:
					row = cls(id=google_apps_domain)
					row.google_apps_domain = google_apps_domain
					row.num_users = 0
					row.hide_ad = False
					row.multi_domain_setting = False
					row.secret_key = ''
					row.available_users = sateraito_inc.DEFAULT_AVAILABLE_USERS
					row.impersonate_email = ""
					row.is_auto_create_impersonate_email = True
					row.use_iframe_version_gadget = True
					row.is_oauth2_domain = True
					row.is_disable = False
					row.is_backup_available = False
					row.no_auto_logout = True  # True for new domain
					row.is_preview = True
					row.attached_file_viewer_type = 'GOOGLEDRIVEVIEWER'
					row.put()
				else:
					row = cls(id=subdomain)
					row.google_apps_domain = subdomain
					row.num_users = 0
					row.hide_ad = False
					row.multi_domain_setting = False
					row.secret_key = ''
					row.available_users = sateraito_inc.DEFAULT_AVAILABLE_USERS
					row.use_iframe_version_gadget = True
					row.is_oauth2_domain = True
					row.is_disable = False
					row.is_backup_available = False
					row.no_auto_logout = True  # True for new domain
					row.is_preview = True
					row.attached_file_viewer_type = 'GOOGLEDRIVEVIEWER'
					row.put()
		else:
			row = row_k.get(memcache_timeout=NDB_MEMCACHE_TIMEOUT)
			if row is not None:
				is_need_update = False
				if row.use_iframe_version_gadget is None:
					row.use_iframe_version_gadget = False
					is_need_update = True
				if row.is_disable is None:
					row.is_disable = False
					is_need_update = True
				if row.is_backup_available is None:
					row.is_backup_available = False
					is_need_update = True
				if row.no_auto_logout is None:
					row.no_auto_logout = False  # False for existing domain
					is_need_update = True
				if not row.is_oauth2_domain:
					row.is_oauth2_domain = True
				if row.is_preview is None:
					row.is_preview = True
					is_need_update = True
				if row.attached_file_viewer_type is None:
					row.attached_file_viewer_type = 'GOOGLEDRIVEVIEWER'
					is_need_update = True
				if is_need_update:
					row.put()
		namespace_manager.set_namespace(old_namespace)
		return row

	@classmethod
	def getDict2(cls, google_apps_domain, target_google_apps_domain=None, auto_create=False):
		if target_google_apps_domain is None:
			target_google_apps_domain = google_apps_domain
		logging.info('google_apps_domain' + google_apps_domain)
		logging.info('target_google_apps_domain' + target_google_apps_domain)

		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)
		# check memcache
		memcache_key = cls.getMemcacheKey(target_google_apps_domain, target_google_apps_domain)
		cached_dict = memcache.get(memcache_key)
		if cached_dict is not None:
			logging.info('GoogleAppsDomainEntry.getDict: found and respond cache')
			namespace_manager.set_namespace(old_namespace)
			return cached_dict
		# get data
		row = cls.getInstance2(google_apps_domain, target_google_apps_domain, auto_create)
		if row is None:
			namespace_manager.set_namespace(old_namespace)
			return None
		row_dict = row.to_dict()
		row_dict['id'] = row.key.id()
		# set to memcache
		memcache.set(memcache_key, row_dict, time=DICT_MEMCACHE_TIMEOUT)
		namespace_manager.set_namespace(old_namespace)
		return row_dict

	@classmethod
	def getInstance2(cls, google_apps_domain, target_google_apps_domain=None, auto_create=False):
		""" returns db object
		 if no db object found, create new db object and returns it
		"""
		if target_google_apps_domain is None:
			target_google_apps_domain = google_apps_domain

		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)
		# get data
		q = cls.query()
		q = q.filter(cls.google_apps_domain == target_google_apps_domain)
		# row_k = q.get(keys_only=True)
		row_k = q.get()
		row = None
		if row_k is None:
			if auto_create:
				# create new db object with default option
				row = cls(id=target_google_apps_domain)
				row.google_apps_domain = google_apps_domain
				row.num_users = 0
				row.hide_ad = False
				row.multi_domain_setting = False
				row.secret_key = ''
				row.available_users = sateraito_inc.DEFAULT_AVAILABLE_USERS
				row.impersonate_email = ""
				row.is_auto_create_impersonate_email = True
				row.use_iframe_version_gadget = True
				row.is_disable = False
				row.is_backup_available = False
				row.no_auto_logout = True  # True for new domain
				row.put()
		else:
			is_need_update = False
			if row_k.use_iframe_version_gadget is None:
				row_k.use_iframe_version_gadget = False
				is_need_update = True
			if row_k.is_disable is None:
				row_k.is_disable = False
				is_need_update = True
			if row_k.is_backup_available is None:
				row_k.is_backup_available = False
				is_need_update = True
			if row_k.no_auto_logout is None:
				row_k.no_auto_logout = False  # False for existing domain
				is_need_update = True

			if is_need_update:
				row_k.put()

			row = row_k
		namespace_manager.set_namespace(old_namespace)
		return row

	# SSITE対応
	@classmethod
	def isSSiteTenant(cls, tenant_or_domain, domain_dict=None):
		if domain_dict is None:
			domain_dict = cls.getDict2(tenant_or_domain, target_google_apps_domain=None, auto_create=False)
		if domain_dict is None or domain_dict.get('is_ssite_tenant') is None:
			return False
		return domain_dict.get('is_ssite_tenant')

	@classmethod
	def getSSiteTenantID(cls, tenant_or_domain, domain_dict=None):
		if domain_dict is None:
			domain_dict = cls.getDict2(tenant_or_domain, target_google_apps_domain=None, auto_create=False)
		if domain_dict is None or domain_dict.get('ssite_tenant_id') is None:
			return False
		return domain_dict.get('ssite_tenant_id')

	@classmethod
	def isSSOGadgetTenant(cls, tenant_or_domain, domain_dict=None):
		if domain_dict is None:
			domain_dict = cls.getDict2(tenant_or_domain, target_google_apps_domain=None, auto_create=False)
		if domain_dict is None or domain_dict.get('is_sso_tenant') is None:
			return False
		return domain_dict.get('is_sso_tenant')

	@classmethod
	def saveSSOAppKey(cls, google_apps_domain, app_key):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)
		bbs_setting = cls.getInstance(google_apps_domain, auto_create=True)
		bbs_setting.ssogadget_app_key = app_key
		bbs_setting.put()
		namespace_manager.set_namespace(old_namespace)

	@classmethod
	def getSSOAppKey(cls, google_apps_domain):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)
		domain_entry = cls.getInstance(google_apps_domain, auto_create=True)
		namespace_manager.set_namespace(old_namespace)
		return domain_entry.ssogadget_app_key

class GoogleAppsUserEntry(ndb.Model):
	"""	Datastore class to store user info
	"""
	user_email = ndb.StringProperty()
	user_id = ndb.StringProperty()
	google_apps_domain = ndb.StringProperty()
	opensocial_viewer_id = ndb.StringProperty()
	opensocial_container = ndb.StringProperty()
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)
	is_apps_admin = ndb.BooleanProperty()
	disable_user = ndb.BooleanProperty()
	user_token = ndb.StringProperty()
	token_expire_date = ndb.DateTimeProperty()
	oauth2_token = ndb.TextProperty()
	oauth2_batch_param = ndb.TextProperty()
	google_apps_groups = ndb.StringProperty(repeated=True)  # user's joining group
	google_apps_groups_updated_date = ndb.DateTimeProperty()
	entity_not_found = ndb.BooleanProperty()

	opensocial_viewer_id_for_sharepoint = ndb.StringProperty()  # SharePoint認証用
	opensocial_container_for_sharepoint = ndb.StringProperty()  # SharePoint認証用
	is_admin_for_sharepoint = ndb.BooleanProperty()  # SharePoint認証用
	user_token_for_sharepoint = ndb.StringProperty()  # SharePoint認証用
	token_expire_date_for_sharepoint = ndb.DateTimeProperty()  # SharePoint認証用

	check_key_ssite = ndb.StringProperty()

	def _pre_put_hook(self):
		old_namespace = namespace_manager.get_namespace()
		google_apps_domain = sateraito_func.getDomainFromNamespace(old_namespace)
		namespace_manager.set_namespace(google_apps_domain)
		# clear memcache key
		memcache_key_token = GoogleAppsUserEntry.getMemcacheKeyByToken(self.user_token)
		memcache.delete(memcache_key_token)
		memcache_key_user_email = GoogleAppsUserEntry.getMemcacheKey(self.user_email)
		memcache.delete(memcache_key_user_email)
		memcache_key_opensocial_id = GoogleAppsUserEntry.getMemcacheKeyOpenSocialId(self.opensocial_viewer_id, self.opensocial_container)
		memcache.delete(memcache_key_opensocial_id)
		memcache_key_dict_opensocial_id = GoogleAppsUserEntry.getMemcacheKeyDictByOpensocialId(self.opensocial_viewer_id, self.opensocial_container)
		memcache.delete(memcache_key_dict_opensocial_id)
		# restore old namespace
		namespace_manager.set_namespace(old_namespace)

	@classmethod
	def getMemcacheKey(cls, user_email):
		return 'script=googleappsuserentry-getinstance&user_email=' + user_email

	@classmethod
	def getMemcacheKeyOpenSocialId(cls, opensocial_viewer_id, opensocial_container):
		return 'script=getuserentry&opensocial_viewer_id=' + opensocial_viewer_id + '&opensocial_container=' + opensocial_container

	@classmethod
	def getMemcacheKeyByToken(cls, user_token):
		return 'script=getuserentry&user_token=' + str(user_token)

	@classmethod
	def getDictByToken(cls, google_apps_domain, user_token):
		if user_token is None:
			return None
		if user_token == '':
			return None
		# GoogleAppsUserEntry only exists in default namespade(=google_apps_domain)
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)

		# check memcache
		memcache_key = cls.getMemcacheKeyDictByToken(user_token)
		cached_dict = memcache.get(memcache_key)
		if cached_dict is not None:
			logging.info('GoogleAppsUserEntry.getDictByToken: found and respond cache')
			namespace_manager.set_namespace(old_namespace)
			return cached_dict

		row = cls.getInstanceByToken(google_apps_domain, user_token)
		if row is None:
			namespace_manager.set_namespace(old_namespace)
			return None
		row_dict = row.to_dict()
		row_dict['id'] = row.key.id()

		# set to memcache
		memcache.set(memcache_key, row_dict, time=DICT_MEMCACHE_TIMEOUT)

		namespace_manager.set_namespace(old_namespace)
		return row_dict

	def preloadDictToMemcacheByToken(self):
		memcache_key = GoogleAppsUserEntry.getMemcacheKeyDictByToken(self.user_token)
		# set to memcache
		row_dict = self.to_dict()
		row_dict['id'] = self.key.id()
		memcache.set(memcache_key, row_dict, time=DICT_MEMCACHE_TIMEOUT)

	@classmethod
	def getInstanceByToken(cls, google_apps_domain, user_token):
		if user_token is None:
			return None
		if user_token == '':
			return None
		# GoogleAppsUserEntry only exists in default namespade(=google_apps_domain)
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)

		q = cls.query()
		q = q.filter(cls.user_token == user_token)
		row_k = q.get(keys_only=True)
		if row_k is None:
			namespace_manager.set_namespace(old_namespace)
			return None
		row = row_k.get(memcache_timeout=NDB_MEMCACHE_TIMEOUT)
		namespace_manager.set_namespace(old_namespace)
		return row

	@classmethod
	def getDict(cls, google_apps_domain, user_email, auto_create=False):
		# GoogleAppsUserEntry only exists in default namespade(=google_apps_domain)
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)
		# get data
		row = cls.getInstance(google_apps_domain, user_email, auto_create)
		if row is None:
			namespace_manager.set_namespace(old_namespace)
			return None
		row_dict = row.to_dict()
		row_dict['id'] = row.key.id()
		namespace_manager.set_namespace(old_namespace)
		return row_dict

	@classmethod
	def getInstance(cls, google_apps_domain, user_email, auto_create=False):
		# GoogleAppsUserEntry only exists in default namespade(=google_apps_domain)
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)

		user_email_lower = str(user_email).lower()
		row = cls.get_by_id(user_email_lower, memcache_timeout=NDB_MEMCACHE_TIMEOUT)
		if row is None:
			if auto_create:
				rc = sateraito_func.RequestChecker()
				row = rc.putNewUserEntry(user_email, google_apps_domain, user_email.split('@')[1], '__not_set', sateraito_func.OPENSOCIAL_CONTAINER_GOOGLE_SITE, '__not_set')
				namespace_manager.set_namespace(old_namespace)
				return row
		namespace_manager.set_namespace(old_namespace)
		return row

	@classmethod
	def getByKey(cls, key):
		entity = None
		if key is not None:
			if key.id() is not None:
				entity = cls.get_by_id(key.id())
			elif key.name() is not None:
				entity = cls.get_by_id(key.name())
		return entity

	@classmethod
	def getMemcacheKeyDictByOpensocialId(cls, opensocial_viewer_id, opensocial_container):
		return 'script=googleappsuserentry-getdictbyopensocialid&opensocial_viewer_id=' + opensocial_viewer_id + '&opensocial_container=' + opensocial_container + '&g=2'

	@classmethod
	def getMemcacheKeyDictByToken(cls, user_token):
		return 'script=googleappsuserentry-getdictbytoken&user_token=' + str(user_token) + '&g=2'

	@classmethod
	def getDictByOpensocialId(cls, default_namespace_domain, opensocial_viewer_id, opensocial_container):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(default_namespace_domain)

		# check memcache
		memcache_key = cls.getMemcacheKeyDictByOpensocialId(opensocial_viewer_id, opensocial_container)
		cached_dict = memcache.get(memcache_key)
		if cached_dict is not None:
			logging.info('GoogleAppsUserEntry.getDictByOpensocialId: found and respond cache')
			namespace_manager.set_namespace(old_namespace)
			return cached_dict

		# get data
		row = cls.getInstanceByOpensocialId(default_namespace_domain, opensocial_viewer_id, opensocial_container)
		if row is None:
			namespace_manager.set_namespace(old_namespace)
			return None
		row_dict = row.to_dict()
		row_dict['id'] = row.key.id()
		# set to memcache
		memcache.set(memcache_key, row_dict, time=DICT_MEMCACHE_TIMEOUT)

		namespace_manager.set_namespace(old_namespace)
		return row_dict

	@classmethod
	def getInstanceByOpensocialId(cls, default_namespace_domain, opensocial_viewer_id, opensocial_container):
		""" GoogleAppsUserEntry only exists in default namespace=google_apps_domain
		"""
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(default_namespace_domain)

		# get user entry data from db
		q = cls.query()
		q = q.filter(cls.opensocial_viewer_id == opensocial_viewer_id)
		q = q.filter(cls.opensocial_container == opensocial_container)
		user_entry = q.get()

		namespace_manager.set_namespace(old_namespace)
		return user_entry


class UserInfo(ndb.Model):
	"""	Datastore class to store user information
"""

	google_apps_user_id = ndb.StringProperty()
	email = ndb.StringProperty()
	family_name = ndb.StringProperty()
	given_name = ndb.StringProperty()
	family_name_kana = ndb.StringProperty()
	given_name_kana = ndb.StringProperty()
	employee_id = ndb.StringProperty()
	company_name = ndb.StringProperty()
	department_1 = ndb.StringProperty()
	department_2 = ndb.StringProperty()
	department_3 = ndb.StringProperty()
	department_4 = ndb.StringProperty()
	job_title = ndb.StringProperty()
	department_code = ndb.StringProperty()
	company_email_1 = ndb.StringProperty()
	company_email_2 = ndb.StringProperty()
	personal_email_1 = ndb.StringProperty()
	personal_email_2 = ndb.StringProperty()
	company_phone_number_1 = ndb.StringProperty()
	company_extension_number_1 = ndb.StringProperty()
	company_phone_number_2 = ndb.StringProperty()
	personal_phone_number_1 = ndb.StringProperty()
	personal_phone_number_2 = ndb.StringProperty()
	mail_group = ndb.StringProperty(repeated=True)
	language = ndb.StringProperty(default='ja')
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)

	updatable_cols = [
		'family_name',
		'given_name',
		'family_name_kana',
		'given_name_kana',
		'employee_id',
		'company_name',
		'department_1',
		'department_2',
		'department_3',
		'department_4',
		'job_title',
		'department_code',
		'company_email_1',
		'company_email_2',
		'personal_email_1',
		'personal_email_2',
		'company_phone_number_1',
		'company_extension_number_1',
		'company_phone_number_2',
		'personal_phone_number_1',
		'personal_phone_number_2',
		'mail_group',
		'language',
	]

	@classmethod
	def getUserLanguage(cls, email, hl=None):
		user_info_dict = cls.getDict(email)
		if user_info_dict is None:
			return hl

		if 'language' not in user_info_dict:
			return hl

		return user_info_dict['language']

	def _post_put_hook(self, future):
		UserInfo.clearInstanceCache(self.email)

	@classmethod
	def _pre_delete_hook(cls, key):
		UserInfo.clearInstanceCache(key.id())

	def getValue(self, col_name):
		if col_name == 'family_name':
			return self.family_name
		if col_name == 'given_name':
			return self.given_name
		if col_name == 'family_name_kana':
			return self.family_name_kana
		if col_name == 'given_name_kana':
			return self.given_name_kana
		if col_name == 'employee_id':
			return self.employee_id
		if col_name == 'company_name':
			return self.company_name
		if col_name == 'department_1':
			return self.department_1
		if col_name == 'department_2':
			return self.department_2
		if col_name == 'department_3':
			return self.department_3
		if col_name == 'department_4':
			return self.department_4
		if col_name == 'job_title':
			return self.job_title
		if col_name == 'department_code':
			return self.department_code
		if col_name == 'company_email_1':
			return self.company_email_1
		if col_name == 'company_email_2':
			return self.company_email_2
		if col_name == 'personal_email_1':
			return self.personal_email_1
		if col_name == 'personal_email_2':
			return self.personal_email_2
		if col_name == 'company_phone_number_1':
			return self.company_phone_number_1
		if col_name == 'company_extension_number_1':
			return self.company_extension_number_1
		if col_name == 'company_phone_number_2':
			return self.company_phone_number_2
		if col_name == 'personal_phone_number_1':
			return self.personal_phone_number_1
		if col_name == 'personal_phone_number_2':
			return self.personal_phone_number_2
		if col_name == 'mail_group':
			return self.mail_group
		if col_name == 'language':
			return self.language

	def setValue(self, col_name, col_value):
		if col_name.strip() == '':
			# ignore
			return
		if col_name is None:
			# ignore
			return

		# mail_group
		if col_name == 'mail_group':
			col_value_splited = col_value.split(' ')
			self.mail_group = col_value_splited

		if col_name == 'family_name':
			self.family_name = col_value
		if col_name == 'given_name':
			self.given_name = col_value
		if col_name == 'family_name_kana':
			self.family_name_kana = col_value
		if col_name == 'given_name_kana':
			self.given_name_kana = col_value
		if col_name == 'employee_id':
			self.employee_id = col_value
		if col_name == 'company_name':
			self.company_name = col_value
		if col_name == 'department_1':
			self.department_1 = col_value
		if col_name == 'department_2':
			self.department_2 = col_value
		if col_name == 'department_3':
			self.department_3 = col_value
		if col_name == 'department_4':
			self.department_4 = col_value
		if col_name == 'job_title':
			self.job_title = col_value
		if col_name == 'department_code':
			self.department_code = col_value
		if col_name == 'company_email_1':
			self.company_email_1 = str(col_value).lower()
		if col_name == 'company_email_2':
			self.company_email_2 = str(col_value).lower()
		if col_name == 'personal_email_1':
			self.personal_email_1 = str(col_value).lower()
		if col_name == 'personal_email_2':
			self.personal_email_2 = str(col_value).lower()
		if col_name == 'company_phone_number_1':
			self.company_phone_number_1 = col_value
		if col_name == 'company_extension_number_1':
			self.company_extension_number_1 = col_value
		if col_name == 'company_phone_number_2':
			self.company_phone_number_2 = col_value
		if col_name == 'personal_phone_number_1':
			self.personal_phone_number_1 = col_value
		if col_name == 'personal_phone_number_2':
			self.personal_phone_number_2 = col_value
		if col_name == 'language':
			self.language = col_value

	@classmethod
	def getMemcacheKey(cls, email):
		return 'script=userinfo-getuserinfo&email=' + str(email) + '&g=2'

	@classmethod
	def clearInstanceCache(cls, email):
		memcache.delete(cls.getMemcacheKey(email))

	@classmethod
	def getDict(cls, email, reference_enabled=False, auto_create=False):
		# set other app_id namespace if set
		use_reference = False
		reference_app_id = ''
		old_namespace = namespace_manager.get_namespace()
		cache_checking_namespace = old_namespace
		google_apps_domain, old_app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(old_namespace)
		if reference_enabled:
			row_dict_o = OtherSetting.getDict()
			if row_dict_o is not None:
				if row_dict_o['enable_other_app_id_reference']:
					logging.info('other app_id reference enabled')
					use_reference = True
					reference_app_id = row_dict_o['reference_app_id']
					if reference_app_id == sateraito_func.DEFAULT_APP_ID:
						cache_checking_namespace = google_apps_domain
					else:
						cache_checking_namespace = google_apps_domain + sateraito_func.DELIMITER_NAMESPACE_DOMAIN_APP_ID + reference_app_id
					logging.info('cache_checking_namespace=' + str(cache_checking_namespace))

		# check memcache
		logging.info("email=%s" % email)
		memcache_key = cls.getMemcacheKey(email)
		logging.info("memcache_key=%s" % memcache_key)
		cached_dict = memcache.get(str(memcache_key), namespace=cache_checking_namespace)
		if cached_dict is not None:
			logging.info('UserInfo.getDict: found and respond cache')
			return cached_dict
		# get data
		row = cls.getInstance(email, reference_enabled, auto_create)
		if row is None:
			return None
		row_dict = row.to_dict()
		row_dict['id'] = row.key.id()
		# set to memcache
		memcache.set(memcache_key, row_dict, time=DICT_MEMCACHE_TIMEOUT, namespace=cache_checking_namespace)

		# set namespace to old namespace
		if use_reference:
			sateraito_func.setNamespace(google_apps_domain, old_app_id)

		return row_dict

	@classmethod
	def getInstance(cls, email, reference_enabled=False, auto_create=False):
		# set other app_id namespace if set
		use_reference = False
		reference_app_id = ''
		old_namespace = namespace_manager.get_namespace()
		google_apps_domain, old_app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(old_namespace)
		if reference_enabled:
			row_dict_o = OtherSetting.getDict()
			if row_dict_o is not None:
				if row_dict_o['enable_other_app_id_reference']:
					logging.info('other app_id reference enabled')
					use_reference = True
					reference_app_id = row_dict_o['reference_app_id']
					sateraito_func.setNamespace(google_apps_domain, reference_app_id)

		# get data
		email_lower = str(email).lower()
		user_info = cls.get_by_id(email_lower, memcache_timeout=NDB_MEMCACHE_TIMEOUT)
		if user_info is None:
			q = cls.query()
			q = q.filter(cls.email == email_lower)
			row_k = q.get(keys_only=True)
			if row_k is None:
				logging.info('UserInfo not found| auto_create=' + str(auto_create))
				if auto_create:
					user_info = cls()
					user_info.email = email_lower
					user_info.language = ''
					user_info.put()
					return user_info
				else:
					return None
			user_info = cls.get_by_id(row_k.id(), memcache_timeout=NDB_MEMCACHE_TIMEOUT)
		if user_info is not None:
			if user_info.language is None:
				user_info.language = ''
				user_info.put()

		# set namespace to old namespace
		if use_reference:
			sateraito_func.setNamespace(google_apps_domain, old_app_id)

		return user_info

	@classmethod
	def getUserName(cls, viewer_email):
		if viewer_email == '' or viewer_email is None:
			return ''
		q = cls.query()
		q.filter(cls.email == viewer_email)
		user_info = q.get()
		if user_info is None:
			return viewer_email
		return user_info.family_name + user_info.given_name

	@classmethod
	def getExportCsvHeader(cls):
		export_csv_header = ''
		export_csv_header += 'command,email,family_name,given_name,family_name_kana,given_name_kana,employee_id,company_name'
		export_csv_header += ',department_1,department_2,department_3,department_4,job_title,department_code'
		export_csv_header += ',company_email_1,company_email_2,personal_email_1,personal_email_2'
		export_csv_header += ',company_phone_number_1,company_extension_number_1,company_phone_number_2,personal_phone_number_1,personal_phone_number_2,mail_group,language'
		export_csv_header += '\r\n'
		return export_csv_header

	@classmethod
	def getAllEmails(cls):
		logging.info('getAllEmails')
		# get data
		ret_emails = []
		NUM_PER_PAGE = 100
		MAX_PAGES = 1000
		q = UserInfo.query()
		cursor = None
		for i in range(MAX_PAGES):
			logging.info('page ' + str(i))
			rows, cursor, have_more_rows = q.fetch_page(page_size=NUM_PER_PAGE, start_cursor=cursor)
			if len(rows) == 0:
				break
			for row_u in rows:
				# logging.info('row_u.email=' + str(row_u.email))
				if row_u.email:
					ret_emails.append(row_u.email)
			if not have_more_rows:
				break
		return ret_emails

	@classmethod
	def getUserInfo(cls, viewer_email):
		return cls.getInstance(viewer_email)


class LTCacheWorkflowUserList(ndb.Model):
	data_order = ndb.IntegerProperty()
	jsondata = ndb.TextProperty()
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)

	def _post_put_hook(self, future):
		LTCacheWorkflowUserList.clearInstanceCache()

	@classmethod
	def clearInstanceCache(cls):
		memcache.delete(cls.getMemcacheKey())

	@classmethod
	def getMemcacheKey(cls):
		return 'script=ltcacheworkflowuserlist.getjsondata?' + '&g=2'

	@classmethod
	def getJsondata(cls):
		# check memcache
		memcache_key = cls.getMemcacheKey()
		cached_dict = memcache.get(memcache_key)
		if cached_dict is not None:
			logging.info('LTCacheWorkflowUserList.getJsondata: found and respond cache')
			return cached_dict
		# get data
		jsondata = ''
		q = cls.query()
		q = q.order(cls.data_order)
		for key in q.iter(keys_only=True):
			row = key.get(memcache_timeout=NDB_MEMCACHE_TIMEOUT)
			jsondata += row.jsondata
		# set to memcache
		if len(jsondata) < memcache.MAX_VALUE_SIZE:
			memcache.set(memcache_key, jsondata, time=DICT_MEMCACHE_TIMEOUT)

		return jsondata

class LTCacheUserListUpdating(ndb.Model):
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)
	google_apps_domain = ndb.StringProperty()
	is_updating = ndb.BooleanProperty()

	@classmethod
	def isUpdating(cls, google_apps_domain):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)

		ret_val = False
		row = cls.get_by_id(LTCACHE_USER_LIST_UPDATING_KEY, use_cache=False, use_memcache=False)
		if row is None:
			ret_val = False
		else:
			expire_date = row.created_date + datetime.timedelta(minutes=60)
			if sateraito_func.isBiggerDate(datetime.datetime.now(), expire_date):
				ret_val = False
			else:
				ret_val = row.is_updating

		namespace_manager.set_namespace(old_namespace)
		return ret_val

	@classmethod
	def setUpdating(cls, google_apps_domain, is_updating):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)

		row = cls.get_by_id(LTCACHE_USER_LIST_UPDATING_KEY, use_cache=False, use_memcache=False)
		if row is None:
			new_row = cls(id=LTCACHE_USER_LIST_UPDATING_KEY)
			new_row.is_updating = is_updating
			new_row.google_apps_domain = google_apps_domain
			new_row.put()
		else:
			row.is_updating = is_updating
			row.put()
		namespace_manager.set_namespace(old_namespace)

class LTCacheUserList(ndb.Model):
	""" Datastore class to store info about google apps domain
		"""
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)
	google_apps_domain = ndb.StringProperty()
	data_order = ndb.IntegerProperty()
	number_of_entity = ndb.IntegerProperty()
	random_key = ndb.StringProperty()
	jsondata = ndb.TextProperty()

	@classmethod
	def saveJsondata(cls, google_apps_domain, jsondata):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)
		# 1. delete all lt cache
		q = cls.query()
		for key in q.iter(keys_only=True):
			key.delete()
			# 2. devide json data
		jsondata_length = len(jsondata)
		jsondatas = []
		NUM_STRING_PER_ENTITY = 1000 * 800    # 900 KB
		number_of_entity = (jsondata_length // NUM_STRING_PER_ENTITY) + 1
		logging.info('number_of_entity=' + str(number_of_entity))
		for i in range(0, number_of_entity):
			start_index = i * NUM_STRING_PER_ENTITY
			end_index = start_index + NUM_STRING_PER_ENTITY
			jsondatas.append(jsondata[start_index:end_index])
		random_key = sateraito_func.dateString() + sateraito_func.randomString()
		# 4. store json data to datastore
		for i in range(0, number_of_entity):
			new_data = cls(id='data_order=' + str(i))
			new_data.google_apps_domain = google_apps_domain
			new_data.jsondata = jsondatas[i]
			new_data.data_order = i
			new_data.number_of_entity = number_of_entity
			new_data.random_key = random_key
			new_data.put()
		namespace_manager.set_namespace(old_namespace)

	@classmethod
	def getJsondata(cls, google_apps_domain):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)
		# get data
		jsondata = ''
		created_date = None
		q = cls.query()
		q = q.order(cls.data_order)
		for i, key in enumerate(q.iter(keys_only=True)):
			logging.info('i=' + str(i))
			row = key.get()
			jsondata += row.jsondata
			created_date = row.created_date

		namespace_manager.set_namespace(old_namespace)
		return jsondata, created_date

class LTCacheGroupListUpdating(ndb.Model):
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)
	google_apps_domain = ndb.StringProperty()
	is_updating = ndb.BooleanProperty()

	@classmethod
	def isUpdating(cls, google_apps_domain):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)

		ret_val = False
		row = cls.get_by_id(LTCACHE_GROUP_LIST_UPDATING_KEY, use_cache=False, use_memcache=False)
		if row is None:
			ret_val = False
		else:
			expire_date = row.created_date + datetime.timedelta(minutes=60)
			if sateraito_func.isBiggerDate(datetime.datetime.now(), expire_date):
				ret_val = False
			else:
				ret_val = row.is_updating

		namespace_manager.set_namespace(old_namespace)
		return ret_val

	@classmethod
	def setUpdating(cls, google_apps_domain, is_updating):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)

		row = cls.get_by_id(LTCACHE_GROUP_LIST_UPDATING_KEY, use_cache=False, use_memcache=False)
		if row is None:
			new_row = cls(id=LTCACHE_GROUP_LIST_UPDATING_KEY)
			new_row.is_updating = is_updating
			new_row.google_apps_domain = google_apps_domain
			new_row.put()
		else:
			row.is_updating = is_updating
			row.put()
		namespace_manager.set_namespace(old_namespace)

class LTCacheGroupList(ndb.Model):
	""" Datastore class to store info about google apps domain
		"""
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)
	google_apps_domain = ndb.StringProperty()
	data_order = ndb.IntegerProperty()
	number_of_entity = ndb.IntegerProperty()
	random_key = ndb.StringProperty()
	jsondata = ndb.TextProperty()

	@classmethod
	def saveJsondata(cls, google_apps_domain, jsondata):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)
		# 1. delete all lt cache
		q = cls.query()
		for key in q.iter(keys_only=True):
			key.delete()
			# 2. devide json data
		jsondata_length = len(jsondata)
		jsondatas = []
		NUM_STRING_PER_ENTITY = 1000 * 800    # 900 KB
		number_of_entity = (jsondata_length // NUM_STRING_PER_ENTITY) + 1
		logging.info('number_of_entity=' + str(number_of_entity))
		for i in range(0, number_of_entity):
			start_index = i * NUM_STRING_PER_ENTITY
			end_index = start_index + NUM_STRING_PER_ENTITY
			jsondatas.append(jsondata[start_index:end_index])
		random_key = sateraito_func.dateString() + sateraito_func.randomString()
		# 4. store json data to datastore
		for i in range(0, number_of_entity):
			new_data = cls(id='data_order=' + str(i))
			new_data.google_apps_domain = google_apps_domain
			new_data.jsondata = jsondatas[i]
			new_data.data_order = i
			new_data.number_of_entity = number_of_entity
			new_data.random_key = random_key
			new_data.put()
		namespace_manager.set_namespace(old_namespace)

	@classmethod
	def getJsondata(cls, google_apps_domain):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)
		# get data
		jsondata = ''
		created_date = None
		q = cls.query()
		q = q.order(cls.data_order)
		for i, key in enumerate(q.iter(keys_only=True)):
			logging.info('i=' + str(i))
			row = key.get()
			jsondata += row.jsondata
			created_date = row.created_date

		namespace_manager.set_namespace(old_namespace)
		return jsondata, created_date


class MailSendLogEach(ndb.Model):
	send_id = ndb.StringProperty()
	sender = ndb.StringProperty()
	subject = ndb.StringProperty()
	to = ndb.StringProperty()
	body = ndb.TextProperty()
	receiver_name = ndb.StringProperty()
	created_date = ndb.DateTimeProperty(auto_now_add=True)


class APIKey(ndb.Model):
	unique_id = ndb.StringProperty()
	api_key = ndb.StringProperty()
	creator_email = ndb.StringProperty()
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)

class APIAccessToken(ndb.Model):
	access_token = ndb.StringProperty()
	impersonate_email = ndb.StringProperty()
	api_key = ndb.StringProperty()
	token_expire_date = ndb.DateTimeProperty()
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)
	num_auth = ndb.IntegerProperty(default=0)
	num_auth_failed = ndb.IntegerProperty(default=0)

	@classmethod
	def getInstance(cls, googleapps_domain, access_token):

		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(googleapps_domain, '')
		try:
			q = cls.query()
			q = q.filter(cls.access_token == access_token)
			key = q.get(keys_only=True)
			row = key.get() if key is not None else None
			return row
		finally:
			namespace_manager.set_namespace(old_namespace)

class OneTimeUserToken(ndb.Model):
	user_email = ndb.StringProperty()
	google_apps_domain = ndb.StringProperty()
	user_token = ndb.StringProperty()
	is_sharepoint_mode = ndb.BooleanProperty()
	token_expire_date = ndb.DateTimeProperty()
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)

	@classmethod
	def getByKey(cls, key):
		entity = None
		if key is not None:
			entity = cls.get_by_id(key.id())
		return entity


class BatchTimeLog(ndb.Model):
	"""	Datastore class to store user search history
	"""
	time_log_key = ndb.StringProperty()
	batch_time = ndb.DateTimeProperty()
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)

	@classmethod
	def registerTime(cls, time_log_key):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace('')
		row = cls.get_by_key_name(time_log_key)
		if row is None:
			row = cls(key_name=time_log_key)
			row.time_log_key = time_log_key
			row.put()
		row.batch_time = datetime.datetime.now()
		row.put()
		namespace_manager.set_namespace(old_namespace)

class BlobPointer(ndb.Model):
	"""	Datastore class to store user search history
	"""
	pointer_namespace = ndb.StringProperty()
	pointer_table = ndb.StringProperty()
	blob_creation = ndb.DateTimeProperty()
	blob_key = ndb.BlobKeyProperty()
	blob_filename = ndb.StringProperty()
	checked = ndb.BooleanProperty()
	checked_message = ndb.TextProperty()
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)

	@classmethod
	def registerNew(cls, blob_info, pointer_namespace, pointer_table='FileflowDoc'):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace('')
		new_row = cls()
		new_row.blob_creation = blob_info.creation
		new_row.blob_filename = blob_info.filename
		new_row.blob_key = blob_info.key()
		new_row.pointer_namespace = pointer_namespace
		new_row.pointer_table = pointer_table
		new_row.checked = False
		new_row.put()
		namespace_manager.set_namespace(old_namespace)

	@classmethod
	def registerNew2(cls, blob_info, pointer_namespace, pointer_table='FileflowDoc'):
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace('')
		new_row = cls()
		new_row.blob_creation = blob_info["creation"]
		new_row.blob_filename = blob_info["filename"]
		new_row.blob_key = blob_info["blob_key"]
		new_row.pointer_namespace = pointer_namespace
		new_row.pointer_table = pointer_table
		new_row.checked = False
		new_row.put()
		namespace_manager.set_namespace(old_namespace)

class OtherSetting(ndb.Model):
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	updated_date = ndb.DateTimeProperty(auto_now=True)
	doc_sort_setting = ndb.StringProperty()  # should be 'sort_by_published_date_desc' or 'sort_by_custom_sort_field_desc' or 'sort_by_custom_sort_field_asc'
	use_sateraito_address_popup = ndb.BooleanProperty()
	sateraito_address_popup_url_param = ndb.StringProperty()
	additional_admin_user_groups = ndb.StringProperty(repeated=True)
	limit_access_to_doc_management = ndb.BooleanProperty()
	access_allowd_user_groups = ndb.StringProperty(repeated=True)
	csv_fileencoding = ndb.StringProperty()
	allow_user_or_groups = ndb.StringProperty()
	cols_to_show = ndb.TextProperty()

	# get other app_id's UserInfo if below is enabled
	enable_other_app_id_reference = ndb.BooleanProperty(default=False)
	reference_app_id = ndb.StringProperty(default='')

	user_can_delete_doc = ndb.BooleanProperty(default=False)
	users_groups_can_delete_doc = ndb.StringProperty(repeated=True)

	# INTERNAL OPTION: add text data of attached file to Search API Index
	enable_attach_file_keyword_search_function = ndb.BooleanProperty(default=True)

	# For workflow doc - Send mail option when doc ...
	enable_send_mail_doc_create = ndb.BooleanProperty(default=False)
	enable_send_mail_doc_edit = ndb.BooleanProperty(default=False)
	enable_send_mail_doc_delete = ndb.BooleanProperty(default=False)

	def _post_put_hook(self, future):
		OtherSetting.clearInstanceCache()

	@classmethod
	def getMemcacheKey(cls):
		# TODO:: only_dev
		return 'v3script=othersetting-getinstance' + '&g=2'

	@classmethod
	def clearInstanceCache(cls):
		memcache.delete(cls.getMemcacheKey())

	@classmethod
	def getDict(cls, auto_create=False):
		# check memcache
		memcache_key = cls.getMemcacheKey()
		cached_dict = memcache.get(memcache_key)
		if cached_dict is not None:
			return cached_dict
		# get data
		row = cls.getInstance(auto_create)
		if row is None:
			return None
		row_dict = row.to_dict()
		row_dict['id'] = row.key.id()
		# set to memcache
		memcache.set(memcache_key, row_dict, time=DICT_MEMCACHE_TIMEOUT)
		return row_dict

	@classmethod
	def getInstance(cls, auto_create=False):
		# get data
		q = cls.query()
		key = q.get(keys_only=True)
		row = None
		if key is not None:
			row = key.get()
		if row is None:
			if auto_create:
				# normal case autocreate
				row = cls()
				row.doc_sort_setting = 'sort_by_published_date_desc'
				row.use_sateraito_address_popup = False
				row.limit_access_to_doc_management = False
				row.enable_other_app_id_reference = False
				row.reference_app_id = ''
				row.csv_fileencoding = sateraito_inc.CSV_ENCODING_DEFAULT
				row.enable_attach_file_keyword_search_function = True
				row.put()
				# other setting is CREATED --> first access to this namespace
				# create DomainAndAppId
				namespace_name = namespace_manager.get_namespace()
				sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)
			# DomainAndAppId.addIfNotRegistered(google_apps_domain, app_id)
		if row is not None:
			need_update = False
			if row.use_sateraito_address_popup is None:
				row.use_sateraito_address_popup = False
				need_update = True
			if row.limit_access_to_doc_management is None:
				row.limit_access_to_doc_management = False
				need_update = True
			if row.enable_other_app_id_reference is None:
				row.enable_other_app_id_reference = False
				need_update = True
			if row.reference_app_id is None:
				row.reference_app_id = ''
				need_update = True
			if row.csv_fileencoding is None:
				row.csv_fileencoding = sateraito_inc.CSV_ENCODING_DEFAULT
				need_update = True
			if row.user_can_delete_doc is None:
				row.user_can_delete_doc = False
				need_update = True
			if row.users_groups_can_delete_doc is None:
				row.users_groups_can_delete_doc = []
				need_update = True
			if row.enable_attach_file_keyword_search_function is None:
				row.enable_attach_file_keyword_search_function = True
				need_update = True
			if row.enable_send_mail_doc_create is None:
				row.enable_send_mail_doc_create = False
				need_update = True
			if row.enable_send_mail_doc_edit is None:
				row.enable_send_mail_doc_edit = False
				need_update = True
			if row.enable_send_mail_doc_delete is None:
				row.enable_send_mail_doc_delete = False
				need_update = True

			if need_update:
				row.put()

		return row

class OperationLog(ndb.Model):
	"""	Datastore class to store user search history
	"""
	operation_date = ndb.DateTimeProperty()
	created_date = ndb.DateTimeProperty(auto_now_add=True)
	user_id = ndb.StringProperty()
	user_email = ndb.StringProperty()

	operation = ndb.StringProperty()

	screen = ndb.StringProperty()
	type_log = ndb.StringProperty()
	detail = ndb.TextProperty()
