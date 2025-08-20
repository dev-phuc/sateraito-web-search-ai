#!/usr/bin/python
# coding: utf-8

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'

import os

# GAEGEN2対応:独自ロガー
# import logging
import sateraito_logger as logging

import jinja2
from google.appengine.ext import ndb
from google.appengine.api import memcache

# from gdata.apps.service import AppsForYourDomainException  # g2対応
from apiclient.errors import HttpError
# from oauth2client.client import AccessTokenRefreshError  # g2対応
from google.auth.exceptions import RefreshError
import sateraito_inc
import sateraito_func
import sateraito_page
import sateraito_db
#import oem_func		# G Suite 版申込ページ対応 2017.06.05

cwd = os.path.dirname(__file__)
path = os.path.join(cwd, 'templates')
bcc = jinja2.MemcachedBytecodeCache(client=memcache.Client(), prefix='jinja2/bytecode/', timeout=None)
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path), auto_reload=False, bytecode_cache=bcc)

MARK_SATERAITO_WORKFLOW_PORTAL_URL = '[sateraito-estorage-menu-url '

"""
domain.py

@since: 2011-11-05
@version: 2023-08-08
@author: Akitoshi Abe
"""

#def getRedirectUrl(google_apps_domain, viewer_email):
#	""" get custom url from group sateraito-workflow-group@yourdomain.com description
#	Args: viewer_email .. email address of user
#	Return: custom my portal url
#					if not defined, returns gadgets url showing page url
#	"""
#	target_google_apps_domain = (viewer_email.split('@'))[1]
#	default_redirect_url = sateraito_inc.my_site_url + '/' + target_google_apps_domain + '/introducing'
#	# if you get email correctry, you can get his calendar data even if he has not log on to this script or other user's request
#
#	apps_service = sateraito_func.fetch_get_admin_sdk_service(google_apps_domain, viewer_email, target_google_apps_domain)
#	groups_service = apps_service.groups()
#	try:
#		feed = groups_service.get(groupKey=sateraito_inc.FILE_SETTING_GROUP_ID + '@' + google_apps_domain).execute()
#	except BaseException, instance:
#		# EntityDoesNotExist
#		return default_redirect_url
#	except:
#		return default_redirect_url
#
#	logging.info('feed=' + str(feed))
#	description = feed['description']
#	if description is None:
#		return default_redirect_url
#
#	if MARK_SATERAITO_WORKFLOW_PORTAL_URL in description:
#		start_index = description.find(MARK_SATERAITO_WORKFLOW_PORTAL_URL)
#		if start_index >= 0:
#			end_index = description.find(']', start_index)
#			if end_index >= 0:
#				user_specified_url = description[start_index + len(MARK_SATERAITO_WORKFLOW_PORTAL_URL):end_index]
#				# myportal_url must start http:// or https://
#				if user_specified_url.startswith('http://') or user_specified_url.startswith('https://'):
#					return user_specified_url
#	return default_redirect_url

def getRedirectUrl(domain_entry, viewer_email, google_apps_domain):
	""" get custom url from group sateraito-workflow-group@yourdomain.com description
	Args: viewer_email .. email address of user
	Return: custom my portal url
					if not defined, returns gadgets url showing page url
	"""
	default_redirect_url = sateraito_inc.my_site_url + '/' + google_apps_domain + '/introducing'
	# if you get email correctry, you can get his calendar data even if he has not log on to this script or other user's request

	# prepare for run on appengine
	# set timeout setting to 10 sec(max value)
	# but gadget timeouts for 10 secs, longer timeout sec on server is for memcached and retry
	#gdata.alt.appengine.run_on_appengine(groups_service, deadline=10)
	try:
		if domain_entry is None or domain_entry.is_auto_create_impersonate_email or (domain_entry.impersonate_email is None or domain_entry.impersonate_email == ''):
			is_admin = sateraito_func.check_user_is_admin(google_apps_domain, viewer_email, do_not_use_impersonate_mail=True)
			if is_admin:
				logging.info('Redirect to introducing. Because "impersonate_email" is empty or "is_auto_create_impersonate_email" == True.')
				return default_redirect_url, True

		directory_service = sateraito_func.fetch_get_admin_sdk_service(google_apps_domain, viewer_email)
		try:
			group = directory_service.groups().get(groupKey=sateraito_inc.DOCUMENT_SETTING_GROUP_ID + '@' + google_apps_domain).execute()
		except Exception as instance:
			# EntityDoesNotExist
			return default_redirect_url, False


	# except AccessTokenRefreshError as e:  # g2対応
	except RefreshError as e:
		# EntityDoesNotExist
		return default_redirect_url, False
	# except AppsForYourDomainException as instance:
	# 	return default_redirect_url, False
	except HttpError as e:
		logging.info(str(e))
		if e.resp.status == 404:
			logging.info('class name: ' + e.__class__.__name__ + 'message=' + str(e))
			return default_redirect_url, False
		elif e.resp.status == 403:
			# impersonate_mail have no priv to use Admin SDK Directory API
			logging.info('class name:' + e.__class__.__name__ + ' message=' +str(e))
			return default_redirect_url, False
		else:
			raise e

	description = group['description']
	if description is None or description == '':
		return default_redirect_url, False

	logging.info(description)
	if MARK_SATERAITO_WORKFLOW_PORTAL_URL in description:
		start_index = description.find(MARK_SATERAITO_WORKFLOW_PORTAL_URL)
		if start_index >= 0:
			end_index = description.find(']', start_index)
			if end_index >= 0:
				user_specified_url = description[start_index + len(MARK_SATERAITO_WORKFLOW_PORTAL_URL):end_index]
				# myportal_url must start http:// or https://
				if user_specified_url.startswith('http://') or user_specified_url.startswith('https://'):
					return str(user_specified_url), False
	return default_redirect_url, False

#class MainPage(sateraito_page._OidBasePage):
#
#	# memcache entry expires in 10 min
#	memcache_expire_secs = 10 * 60
#
#	def _memcache_key(self, viewer_email):
#		google_apps_domain = (viewer_email.split('@'))[1]
#		return 'script=domain&google_apps_domain=' + google_apps_domain
#
#	def get(self, google_apps_domain):
#		# check login
#		if not self._OIDCAutoLogin(google_apps_domain):
#			return
#		# check if cached data exists
#		cached_data = memcache.get(self._memcache_key(self.viewer_email))
#		if cached_data is not None:
#			logging.info('found and redirect to cached url')
#			self.redirect(cached_data)
#			return
#		# get redirect url which is stored to group description
#		redirect_url = getRedirectUrl(google_apps_domain, self.viewer_email)
#		logging.info('redirect_url=' + redirect_url)
#		# save it to memcache
#		if not memcache.set(key=self._memcache_key(self.viewer_email), value=redirect_url, time=self.memcache_expire_secs):
#			logging.warning("Memcache set failed.")
#		logging.info('user OK, redirecting url=' + redirect_url)
#		self.redirect(redirect_url)

class MainPage(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):

	# memcache entry expires in 10 min
	memcache_expire_secs = 10 * 60

	def _memcache_key(self, viewer_email):
		google_apps_domain = (viewer_email.split('@'))[1]
		return 'script=domain&google_apps_domain=' + google_apps_domain + '&g=2'

	def doAction(self, tenant_or_domain):
		try:
			# check login
			is_ok, body_for_not_ok = self._OIDCAutoLogin(tenant_or_domain)
			# if not self._OIDCAutoLogin(tenant_or_domain):
			if not is_ok:
				return body_for_not_ok

			domain_entry = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)
			if domain_entry is None or domain_entry.is_auto_create_impersonate_email or (domain_entry.impersonate_email is None or domain_entry.impersonate_email==''):
				pass
			else:
				# check if cached data exists
				cached_data = memcache.get(self._memcache_key(self.viewer_email))
				if cached_data is not None:
					logging.info('found and redirect to cached url')
					self.redirect(cached_data)
					return
			# get redirect url which is stored to group description
			redirect_url, is_noset_memcache = getRedirectUrl(domain_entry,self.viewer_email,tenant_or_domain)
			logging.info('redirect_url=' + redirect_url)
			# save it to memcache
			if not is_noset_memcache:
				if not memcache.set(key=self._memcache_key(self.viewer_email), value=redirect_url, time=self.memcache_expire_secs):
					logging.warning("Memcache set failed.")
			logging.info('user OK, redirecting url=' + redirect_url)
			self.redirect(redirect_url)
		except Exception as e:
			logging.exception(e)
			values={
				'google_apps_domain': tenant_or_domain,
				'my_site_url': sateraito_inc.my_site_url,
				'version': sateraito_func.getScriptVersionQuery(),
				'vscripturl': sateraito_func.getScriptVirtualUrl(),
				# 'vscriptliburl': sateraito_func.getScriptLibVirtualUrl(),
				# 'lang': hl,
			}
			logging.info('NOT INSTALL')
			template = jinja_environment.get_template('not_installed.html')
			# start http body
			# self.response.out.write(template.render(values))
			return template.render(values)

class LoginPage(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):

	def doAction(self, tenant_or_domain):
		# check login
		redirect_url = sateraito_inc.my_site_url + '/domain/v2/' + tenant_or_domain
		# check login
		is_ok, body_for_not_ok = self.oidAutoLogin(tenant_or_domain, kozukasan_method=True, kozukasan_redirect_to=redirect_url)
		if not is_ok:
			# not logged in: login and go to v2 MainPage
			return body_for_not_ok

		self.redirect(redirect_url)

# app = webapp2.WSGIApplication([
# 							('/domain/([^/]*)', LoginPage),
# 							('/domain/v2/([^/]*)', MainPage),
# 							 ], debug=sateraito_inc.debug_mode, config=sateraito_page.config)

def add_url_rules(app):
	app.add_url_rule('/domain/<tenant_or_domain>',
									 view_func=LoginPage.as_view('DomainLoginPage'))

	app.add_url_rule('/domain/v2/<tenant_or_domain>',
									 view_func=MainPage.as_view('DomainMainPage'))
