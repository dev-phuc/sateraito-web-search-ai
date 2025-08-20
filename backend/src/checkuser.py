#!/usr/bin/python
# coding: utf-8

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'
# set default encodeing to utf-8
# from flask import Flask, Response, render_template, request, make_response, session, redirect, after_this_request, jsonify
from flask import render_template, request, make_response
# import os
import json
import sateraito_logger as logging
import random

from google.appengine.api import memcache, taskqueue, namespace_manager, urlfetch
# import gdata.alt.appengine
# import gdata.apps
# from gdata.service import RequestError
# from gdata.apps.service import AppsForYourDomainException

import sateraito_inc
import sateraito_func
import sateraito_db
import sateraito_black_list
import sateraito_page
# from google.appengine.ext import ndb


'''


@since: 2012-11-22
@version: 2013-06-17
@author: Akitoshi Abe
'''


def needToShowUpgradeLink(google_apps_domain):
	""" check if domain is in status to show upgrade link
	  Return: True if showing upgrade link is needed
	"""
	# Upgrade link is shown ONLY IN FREE edition
	if not sateraito_inc.IS_FREE_EDITION:
		return False
	# check number of users
	row_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
	if row_dict is None:
		return False
	available_users = row_dict['available_users']
	num_users = row_dict['num_users']
	logging.info('available_users=' + str(available_users) + ' num_users=' + str(num_users))
	if available_users is not None and num_users is not None:
		if available_users < num_users:
			return True
	return False


def isMultiDomainSetting(google_apps_domain):
	"""	check if google_apps_domain is multi domain setting enabled
	"""
	row_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
	if row_dict is None:
		return False
	else:
		return row_dict['multi_domain_setting']


def checkAndUpdateUserEmailEntityExist(google_apps_domain, viewer_email, google_apps_domain_to_check):
	""" check viewer_email value is correctly registered(not changed) email value
	  if not, update GoogleAppsUserEntry.entity_not_found = True
	"""
	# memcache entry expires in 2 hours
	memcache_expire_secs = 60 * 60 * 2
	memcache_key = 'script=isuseremailentityexist?viewer_email=' + str(viewer_email) + '&google_apps_domain_to_check=' + str(google_apps_domain_to_check) + '&g=2'
	# check if cached data exists
	cached_data = memcache.get(memcache_key)
	if cached_data is not None:
		logging.info('checkAndUpdateUserEmailEntityExist: not checking because recently checked')
		return sateraito_func.strToBool(cached_data)
	
	logging.info('checkAndUpdateUserEmailEntityExist: checking viewer_email=' + viewer_email + ' and domain=' + google_apps_domain_to_check)
	# # OAuth Token(gdata.auth)
	apps_service = sateraito_func.fetch_get_admin_sdk_service(google_apps_domain, viewer_email, google_apps_domain_to_check)
	email_to_get_name_splited = viewer_email.split('@')
	entity_not_found = False
	try:
		user_entry = apps_service.users().get(userKey=viewer_email).execute()
		# ニックネームであっても取得できてしまうのでIDをチェック
		user_name = user_entry["primaryEmail"].split('@')[0]
		logging.info(user_name)
		if user_entry is not None and str(user_name).lower() != email_to_get_name_splited[0].lower():
			logging.info('user entry is exist. but it is the nickname.')
			user_entry = None
	except BaseException as e:
		logging.warn('e=' + str(e))
		if hasattr(e, 'reason'):
			logging.info('reason=' + str(e.reason))
			if e.error_code == 1301 and e.reason == 'EntityDoesNotExist':
				entity_not_found = True
			else:
				raise e
		else:
			raise e

	logging.info('entity_not_found=' + str(entity_not_found))

	if entity_not_found:
		row = sateraito_db.GoogleAppsUserEntry.getInstance(google_apps_domain, viewer_email)
		if row is not None:
			if row.entity_not_found is None or row.entity_not_found == False:
				row.entity_not_found = True
				row.opensocial_viewer_id = row.opensocial_viewer_id + '_deleted'
				row.put()
	entity_found = not(entity_not_found)
	if entity_found:
		if not memcache.set(key=memcache_key, value=str(entity_found), time=memcache_expire_secs):
			logging.warning("Memcache set failed.")
	return entity_found


def updateLastLoginMonthAndNumUsers(user_email, domain_dict, google_apps_domain):
	google_apps_domain_of_user = sateraito_func.getDomainPart(user_email)
	if google_apps_domain_of_user == google_apps_domain:
		# primary domain user
		is_updated = sateraito_db.GoogleAppsDomainEntry.updateLastLoginMonth(domain_dict['id'])
		if is_updated:
			# update num_users once a month
			taskqueue.add(
						url='/' + google_apps_domain + '/tq/setnumusers',
						params={
								'user_email': user_email,
								},
						target=sateraito_func.getBackEndsModuleNameDeveloper('b1process'),
						countdown=10,
						)
	else:
		# secondary domain user
		logging.info('secondary domain user')
		subdomain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain, subdomain=google_apps_domain_of_user)
		is_updated = sateraito_db.GoogleAppsDomainEntry.updateLastLoginMonth(subdomain_dict['id'])
		if is_updated:
			# update num_users once a month
			taskqueue.add(
						url='/' + google_apps_domain + '/tq/setnumusers',
						params={
								'user_email': user_email,
								},
						target=sateraito_func.getBackEndsModuleNameDeveloper('b1process'),
						countdown=10,
						)


class CheckUser(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	""" Request handler to check user
	if opensocial viewer id is not found in Datastore, this handler returns url to popup
	"""

	def createToken(self):
		s = 'abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
		token = ''
		for j in range(64):
			token += random.choice(s)
		return token

	def doAction(self, google_apps_domain, app_id):

		# set namespace FOR GoogleAppsUserEntry --> only in google_apps_domain namespace
		self.setNamespace(google_apps_domain, app_id)
		
		# check request NOT CHECKING Datastore
		# in this check, pass the existence check in GoogleAppsUserEntry
		checker = sateraito_func.RequestChecker()
		if checker.checkContainerSign(self.request, check_user_db=False) == False:
			logging.exception('Illegal access')
			self.response.set_status(403)
			return
		# do not check domain matching(when check_user_db=False, user email is not get)

		# check if showing upgrade link is needed
		show_upgrade_link = needToShowUpgradeLink(google_apps_domain)

		ret_value = {}

		if (checker.opensocial_viewer_id is None) or (checker.opensocial_viewer_id == '') or (checker.opensocial_container is None) or (checker.opensocial_container == ''):
			# opensocial id is empty
			logging.exception('unable to get opensocial_id or opensocial_container')
			logging.info('opensocial_id=' + checker.opensocial_viewer_id)
			logging.info('opensocial_container=' + checker.opensocial_container)
			ret_value = {
				'user_exists' : False,
				'popup' : '',
				'hide_ad' : False,
				'is_error' : True,
				'token': '',
				'error_code' : 'unable_to_get_opensocial_id',
				'show_upgrade_link': show_upgrade_link,
			}
		else:
			# Check opsocial id in database
			user_dict = sateraito_db.GoogleAppsUserEntry.getDictByOpensocialId(google_apps_domain, checker.opensocial_viewer_id, checker.opensocial_container)
			
			if user_dict is None:
				# No user entry in database
				# create token and save opensocial_viewer_id to memcached database using token
				# it expires in an hour
				token = self.createToken()
				open_social_info = sateraito_func.OpenSocialInfo()
				open_social_info.saveInfo(token, checker.opensocial_container, checker.opensocial_viewer_id)
				multi_domain_setting = isMultiDomainSetting(checker.google_apps_domain_from_gadget_url)
				ret_value = {
					'user_exists' : False,
					'popup' : sateraito_inc.my_site_url + '/' + checker.google_apps_domain_from_gadget_url + '/openid/' + token + '/' + checker.google_apps_domain_from_gadget_url + '/before_popup.html',
					'popup_subdomain' : sateraito_inc.my_site_url + '/' + checker.google_apps_domain_from_gadget_url + '/' + token + '/popup_subdomain.html',
					'hide_ad' : False,
					'is_error' : False,
					'token': token,
					'multi_domain_setting': multi_domain_setting,
					'error_code' : '',
					'show_upgrade_link': show_upgrade_link,
					'lang' : '',
				}
			else:
				# user entry found
				
				# check user_email is correct value, check mark if not
				email_ok = checkAndUpdateUserEmailEntityExist(google_apps_domain, user_dict['user_email'], user_dict['google_apps_domain'])
				if not email_ok:
					# show authorize link in gadget
					token = self.createToken()
					open_social_info = sateraito_func.OpenSocialInfo()
					open_social_info.saveInfo(token, checker.opensocial_container, checker.opensocial_viewer_id)
					multi_domain_setting = isMultiDomainSetting(checker.google_apps_domain_from_gadget_url)
					ret_value = {
						'user_exists' : False,
						'popup' : sateraito_inc.my_site_url + '/' + checker.google_apps_domain_from_gadget_url + '/openid/' + token + '/' + checker.google_apps_domain_from_gadget_url + '/before_popup.html',
						'popup_subdomain' : sateraito_inc.my_site_url + '/' + checker.google_apps_domain_from_gadget_url + '/' + token + '/popup_subdomain.html',
						'hide_ad' : False,
						'is_error' : False,
						'token': token,
						'multi_domain_setting': multi_domain_setting,
						'error_code' : '',
						'show_upgrade_link': show_upgrade_link,
						'lang' : '',
					}
				else:
					# check domain_disabled
					domain_disabled = False
					if user_dict['google_apps_domain'] in sateraito_black_list.DOMAINS_TO_DISABLE:
						domain_disabled = True
					# check workflow admin or not
					is_workflow_admin = sateraito_func.isWorkflowAdmin(user_dict['user_email'], google_apps_domain, app_id)
					# check hide ad
					hide_ad = False
					domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
					if domain_dict is not None:
						hide_ad = domain_dict['hide_ad']
						
						google_apps_domain_of_user = sateraito_func.getDomainPart(user_dict['user_email'])
						
						if google_apps_domain_of_user == google_apps_domain:
							# primary domain user
							is_updated = sateraito_db.GoogleAppsDomainEntry.updateLastLoginMonth(domain_dict['id'])
							if is_updated:
								# update num_users once a month
								taskqueue.add(url='/' + google_apps_domain + '/tq/setnumusers',
															params={
																'user_email': user_dict['user_email'],
															},
															target=sateraito_func.getBackEndsModuleNameDeveloper('b1process'),
															countdown=10)
						else:
							# secondary domain user
							logging.info('secondary domain user')
							subdomain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain, subdomain=google_apps_domain_of_user)
							is_updated = sateraito_db.GoogleAppsDomainEntry.updateLastLoginMonth(subdomain_dict['id'])
							if is_updated:
								# update num_users once a month
								taskqueue.add(url='/' + google_apps_domain + '/tq/setnumusers',
															params={
																'user_email': user_dict['user_email'],
															},
															target=sateraito_func.getBackEndsModuleNameDeveloper('b1process'),
															countdown=10)
					
					user_disabled = user_dict['disable_user']
					if not user_disabled:
						if not sateraito_func.isOkToAccessAppId(user_dict['user_email'], google_apps_domain, app_id):
							user_disabled = True
					
					user_info_dict = sateraito_db.UserInfo.getDict(user_dict['user_email'])

					is_google_apps_admin = sateraito_func.check_user_is_admin(google_apps_domain, user_dict['user_email'])
					ret_value = {
								'user_exists': True,
								'popup': '',
								'is_error': False,
								'token': '',
								'hide_ad' : hide_ad,
								'error_code': '',
								'user_disabled': user_disabled,
								'domain_disabled': domain_disabled,
								'user_email': user_dict['user_email'],
								'is_workflow_admin': is_workflow_admin,
								'is_google_apps_admin': is_google_apps_admin,
								'show_upgrade_link': show_upgrade_link,
								'multi_domain_setting': domain_dict['multi_domain_setting'],
								'lang' : user_info_dict['language'] if user_info_dict is not None and user_info_dict['language'] is not None else '',
								}

		# export json data
		jsondata = json.JSONEncoder().encode(ret_value)
		return jsondata


class TqSetNumUsers(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	""" Update num_users of GoogleAppsDomainEntry
		Task Queue process
	"""
	
	def getNumUsers(self,google_apps_domain, viewer_email, target_google_apps_domain):
		""" Get number of users of google apps domain
		"""

		users = []
		apps_service = sateraito_func.fetch_get_admin_sdk_service(google_apps_domain, viewer_email, target_google_apps_domain)

		MAX_PAGING_CNT = 1000
		# create user list from feed

		page_token = None
		for i in range(MAX_PAGING_CNT):
			user_list = apps_service.users().list(domain=google_apps_domain , pageToken=page_token).execute()
			for each_user in user_list["users"]:
				users.append({
				'user_email': each_user["primaryEmail"],
				})
			page_token = user_list.get("nextPageToken")
			if page_token is None:
				break

		# number of users in domain
		return len(users)

	def doAction(self, google_apps_domain):
		# check retry count
		retry_cnt = self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']
		logging.info('retry_cnt=' + str(retry_cnt))
		if retry_cnt is not None:
			if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
				logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
				return
		
		# GoogleAppsDomainEntry only exists in default namespace
		namespace_manager.set_namespace(google_apps_domain)
		
		user_email = self.request.get('user_email')
		logging.info('user_email=' + user_email)
		num_users = None
		logging.info('start fetch')
		google_apps_domain_of_user = sateraito_func.getDomainPart(user_email)
		try:
			if sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(google_apps_domain):
				num_users = sateraito_func.getNumUsersSSite(google_apps_domain, user_email)
			else:
				num_users = self.getNumUsers(google_apps_domain, user_email, google_apps_domain_of_user)
		except urlfetch.DownloadError as instance:
			logging.warn('Gdata request timeout')
			return
		except Exception as e:
			logging.warn('e=' + str(e))
			logging.warn('return normal code to no retry')
			return
		logging.info('end fetch num_users=' + str(num_users))
		if num_users is not None:
			if google_apps_domain == google_apps_domain_of_user:
				# Primary domain case
				row = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain)
				if (row.num_users is None) or (row.num_users < num_users):
					row.num_users = num_users
					row.put()
					logging.info('saved new num_users=' + str(num_users))
			else:
				# sub domain case
				row = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain, subdomain=google_apps_domain_of_user)
				if (row.num_users is None) or (row.num_users < num_users):
					row.num_users = num_users
					row.put()
					logging.info('saved new num_users=' + str(num_users))

		return make_response('', 200)


class LoginCheck(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):

	def doAction(self, google_apps_domain):
		# check login
		is_ok, body_for_not_ok = self._OIDCAutoLogin(google_apps_domain)
		if not is_ok:
			return body_for_not_ok

		if self.request.get('rtct'):
			logging.info('LoginCheck:rtct')
		return make_response('<html><body>...<body></html>', 200)


def add_url_rules(app):
	app.add_url_rule('/<string:google_apps_domain>/logincheck',
									 view_func=LoginCheck.as_view('LoginCheck'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/checkuser',
									 view_func=CheckUser.as_view('CheckUser'))

	app.add_url_rule('/<string:google_apps_domain>/tq/setnumusers',
									 view_func=TqSetNumUsers.as_view('TqSetNumUsers'))
