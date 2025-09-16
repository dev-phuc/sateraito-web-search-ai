#!/usr/bin/python
# coding: utf-8

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'
'''
sateraito_func.py

@since: 2014-06-07
@version: 2015-04-28
'''

import os
import re
import datetime
import random
import json
import time
from functools import wraps

import lxml
import lxml.html

from sateraito_inc import flask_docker
import sateraito_logger as logging

from dateutil import zoneinfo, tz, relativedelta
from google.appengine.api import namespace_manager, urlfetch, runtime
from googleapiclient.discovery import build

if flask_docker:
	import memcache
	import taskqueue
else:
	from google.appengine.api import memcache
	from google.appengine.api import taskqueue
    
# from oauth2client.client import AccessTokenRefreshError
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError

import sateraito_inc
import sateraito_db
import oem_func
import sateraito_black_list

from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(sateraito_inc.URLFETCH_TIMEOUT_SECOND)

from bs4 import BeautifulSoup, Comment
from utilities import IPy

# g2対応
import google_auth_httplib2

from apisso import ssoclient
from apissite import ssiteclient

from ucf.utils.ucfutil import UcfUtil
from ucf.utils.ucfxml import UcfXml

import apiclient
import google_auth_httplib2
import google.oauth2

import sateraito_search

OPENSOCIAL_CONTAINER_GOOGLE_SITE = 'http://sites.google.com'
OPENSOCIAL_CONTAINER_SSITE = 'https://sateraito-sites'  # ガジェット認証を簡易認証ではなくOIDCに対応できれば不要（id_tokenのissからとれるので）

API_TIMEOUT_SECONDS = 10
API_TIMEOUT_SECONDS_DRIVE = (60 * 60 * 1)

# 有効なタイムゾーンリスト（長いので末尾に）
ACTIVE_TIMEZONES = [
	'Pacific/Midway',
	'Pacific/Niue',
	'Pacific/Pago_Pago',
	'Pacific/Honolulu',
	'Pacific/Rarotonga',
	'Pacific/Tahiti',
	'Pacific/Marquesas',
	'America/Anchorage',
	'Pacific/Gambier',
	'America/Los_Angeles',
	'America/Tijuana',
	'America/Vancouver',
	'America/Whitehorse',
	'Pacific/Pitcairn',
	'America/Dawson_Creek',
	'America/Denver',
	'America/Edmonton',
	'America/Hermosillo',
	'America/Mazatlan',
	'America/Phoenix',
	'America/Yellowknife',
	'America/Belize',
	'America/Chicago',
	'America/Costa_Rica',
	'America/El_Salvador',
	'America/Guatemala',
	'America/Managua',
	'America/Mexico_City',
	'America/Regina',
	'America/Tegucigalpa',
	'America/Winnipeg',
	'Pacific/Easter',
	'Pacific/Galapagos',
	'America/Bogota',
	'America/Cayman',
	'America/Grand_Turk',
	'America/Guayaquil',
	'America/Havana',
	'America/Iqaluit',
	'America/Jamaica',
	'America/Lima',
	'America/Montreal',
	'America/Nassau',
	'America/New_York',
	'America/Panama',
	'America/Port-au-Prince',
	'America/Rio_Branco',
	'America/Toronto',
	'America/Caracas',
	'America/Antigua',
	'America/Asuncion',
	'America/Barbados',
	'America/Boa_Vista',
	'America/Campo_Grande',
	'America/Cuiaba',
	'America/Curacao',
	'America/Guyana',
	'America/Halifax',
	'America/Manaus',
	'America/Martinique',
	'America/Port_of_Spain',
	'America/Porto_Velho',
	'America/Puerto_Rico',
	'America/Santiago',
	'America/Santo_Domingo',
	'America/Thule',
	'Antarctica/Palmer',
	'Atlantic/Bermuda',
	'America/St_Johns',
	'America/Araguaina',
	'America/Bahia',
	'America/Belem',
	'America/Cayenne',
	'America/Fortaleza',
	'America/Godthab',
	'America/Maceio',
	'America/Miquelon',
	'America/Montevideo',
	'America/Paramaribo',
	'America/Recife',
	'America/Sao_Paulo',
	'Antarctica/Rothera',
	'Atlantic/Stanley',
	'America/Noronha',
	'Atlantic/South_Georgia',
	'America/Scoresbysund',
	'Atlantic/Azores',
	'Atlantic/Cape_Verde',
	'Africa/Abidjan',
	'Africa/Accra',
	'Africa/Bamako',
	'Africa/Banjul',
	'Africa/Bissau',
	'Africa/Casablanca',
	'Africa/Conakry',
	'Africa/Dakar',
	'Africa/El_Aaiun',
	'Africa/Freetown',
	'Africa/Lome',
	'Africa/Monrovia',
	'Africa/Nouakchott',
	'Africa/Ouagadougou',
	'Africa/Sao_Tome',
	'America/Danmarkshavn',
	'Atlantic/Canary',
	'Atlantic/Faroe',
	'Atlantic/Reykjavik',
	'Atlantic/St_Helena',
	'Etc/UTC',
	'Europe/Lisbon',
	'Africa/Algiers',
	'Africa/Bangui',
	'Africa/Brazzaville',
	'Africa/Ceuta',
	'Africa/Douala',
	'Africa/Kinshasa',
	'Africa/Lagos',
	'Africa/Libreville',
	'Africa/Luanda',
	'Africa/Malabo',
	'Africa/Ndjamena',
	'Africa/Niamey',
	'Africa/Porto-Novo',
	'Africa/Tunis',
	'Africa/Windhoek',
	'Europe/Amsterdam',
	'Europe/Andorra',
	'Europe/Belgrade',
	'Europe/Berlin',
	'Europe/Brussels',
	'Europe/Budapest',
	'Europe/Copenhagen',
	'Europe/Gibraltar',
	'Europe/Luxembourg',
	'Europe/Madrid',
	'Europe/Malta',
	'Europe/Monaco',
	'Europe/Oslo',
	'Europe/Paris',
	'Europe/Prague',
	'Europe/Rome',
	'Europe/Stockholm',
	'Europe/Tirane',
	'Europe/Vienna',
	'Europe/Zurich',
	'Africa/Blantyre',
	'Africa/Bujumbura',
	'Africa/Cairo',
	'Africa/Gaborone',
	'Africa/Harare',
	'Africa/Johannesburg',
	'Africa/Kigali',
	'Africa/Lubumbashi',
	'Africa/Lusaka',
	'Africa/Maputo',
	'Africa/Maseru',
	'Africa/Mbabane',
	'Africa/Tripoli',
	'Asia/Amman',
	'Asia/Beirut',
	'Asia/Damascus',
	'Asia/Gaza',
	'Asia/Jerusalem',
	'Asia/Nicosia',
	'Europe/Athens',
	'Europe/Bucharest',
	'Europe/Chisinau',
	'Europe/Helsinki',
	'Europe/Istanbul',
	'Europe/Riga',
	'Europe/Sofia',
	'Europe/Tallinn',
	'Europe/Vilnius',
	'Africa/Addis_Ababa',
	'Africa/Asmara',
	'Africa/Dar_es_Salaam',
	'Africa/Djibouti',
	'Africa/Kampala',
	'Africa/Khartoum',
	'Africa/Mogadishu',
	'Africa/Nairobi',
	'Antarctica/Syowa',
	'Asia/Aden',
	'Asia/Baghdad',
	'Asia/Bahrain',
	'Asia/Kuwait',
	'Asia/Qatar',
	'Asia/Riyadh',
	'Europe/Kaliningrad',
	'Europe/Minsk',
	'Indian/Antananarivo',
	'Indian/Comoro',
	'Indian/Mayotte',
	'Asia/Tehran',
	'Asia/Baku',
	'Asia/Dubai',
	'Asia/Muscat',
	'Asia/Tbilisi',
	'Europe/Moscow',
	'Europe/Samara',
	'Indian/Mahe',
	'Indian/Mauritius',
	'Indian/Reunion',
	'Antarctica/Mawson',
	'Asia/Aqtau',
	'Asia/Aqtobe',
	'Asia/Ashgabat',
	'Asia/Dushanbe',
	'Asia/Karachi',
	'Asia/Tashkent',
	'Indian/Kerguelen',
	'Indian/Maldives',
	'Asia/Colombo',
	'Asia/Katmandu',
	'Antarctica/Vostok',
	'Asia/Almaty',
	'Asia/Bishkek',
	'Asia/Dhaka',
	'Asia/Thimphu',
	'Asia/Yekaterinburg',
	'Indian/Chagos',
	'Asia/Rangoon',
	'Indian/Cocos',
	'Antarctica/Davis',
	'Asia/Bangkok',
	'Asia/Hovd',
	'Asia/Jakarta',
	'Asia/Omsk',
	'Asia/Phnom_Penh',
	'Asia/Vientiane',
	'Indian/Christmas',
	'Antarctica/Casey',
	'Asia/Brunei',
	'Asia/Choibalsan',
	'Asia/Hong_Kong',
	'Asia/Krasnoyarsk',
	'Asia/Kuala_Lumpur',
	'Asia/Macau',
	'Asia/Makassar',
	'Asia/Manila',
	'Asia/Shanghai',
	'Asia/Singapore',
	'Asia/Taipei',
	'Asia/Ulaanbaatar',
	'Australia/Perth',
	'Asia/Dili',
	'Asia/Irkutsk',
	'Asia/Jayapura',
	'Asia/Pyongyang',
	'Asia/Seoul',
	'Asia/Tokyo',
	'Pacific/Palau',
	'Australia/Adelaide',
	'Australia/Darwin',
	'Antarctica/DumontDUrville',
	'Asia/Yakutsk',
	'Australia/Brisbane',
	'Australia/Hobart',
	'Australia/Sydney',
	'Pacific/Guam',
	'Pacific/Port_Moresby',
	'Pacific/Saipan',
	'Asia/Vladivostok',
	'Pacific/Efate',
	'Pacific/Guadalcanal',
	'Pacific/Kosrae',
	'Pacific/Noumea',
	'Pacific/Norfolk',
	'Asia/Kamchatka',
	'Asia/Magadan',
	'Pacific/Auckland',
	'Pacific/Fiji',
	'Pacific/Funafuti',
	'Pacific/Kwajalein',
	'Pacific/Majuro',
	'Pacific/Nauru',
	'Pacific/Tarawa',
	'Pacific/Wake',
	'Pacific/Wallis',
	'Pacific/Apia',
	'Pacific/Enderbury',
	'Pacific/Fakaofo',
	'Pacific/Tongatapu',
	'Pacific/Kiritimati'
]

MAX_APPROVE_LEVEL = 20

MAX_NUM_OF_SORTING_DOC = 10000        # this value is GAE system limitation on 2012-12 version of fulltext search

# max number of result for query
NUM_MAX_RESULTS = 500

# numbers of documents to show doc create/approve gadget
NUM_DOC_PER_PAGE = 50

GADGET_ADMIN_CONSOLE = 'admin_console'
GADGET_USER_CONSOLE = 'user_console'

DELIMITER_NAMESPACE_DOMAIN_APP_ID = '_____'
DEFAULT_APP_ID = 'default'

MODE_SHAREPOINT = 'sharepoint'
MODE_SSITE = 'ssite'
MODE_SSOGADGET = 'ssogadget'

WF_USERLIST_INDEX = 'WF_USERLIST_INDEX'

MESS_SUCCESS_CODE = 'SUCCESS'
MESS_BAD_REQUEST_CODE = 'BAD_REQUEST'
MESS_CREATE_SUCCESS_CODE = 'CREATE_SUCCESS'
MESS_CREATE_ERROR_CODE = 'CREATE_ERROR'
MESS_NOT_FOUND_CODE = 'NOT_FOUND'
MESS_INVALID_EMAIL_CODE = 'INVALID_EMAIL'
MESS_UNAUTHORIZED_CODE = 'UNAUTHORIZED'
NOT_FOUND_PARAM_REQ_CODE = 'NOT_FOUND_PARAM_REQ'
UNAUTHORIZED_ADMIN_CODE = 'UNAUTHORIZED_ADMIN'
DUPLICATE_FOLDER_CODE = 'DUPLICATE_FOLDER_CODE'
ROW_CODE_NOT_FOUND = 'ROW_CODE_NOT_FOUND'

INDEX_SEARCH_FILE = 'INDEX_FILE'
INDEX_SEARCH_WORKFLOW_DOC = 'INDEX_WORKFLOW_DOC'
INDEX_SEARCH_MASTER_DATA = 'INDEX_MASTER_DATA'

TYPE_LOG_FOR_FILE = 'LOG_FOR_FILE'
TYPE_LOG_FOR_CATEGORIE = 'LOG_FOR_CATEGORIE'
TYPE_LOG_FOR_DOC_FOLDER = 'LOG_FOR_DOC_FOLDER'
TYPE_LOG_FOR_WORKFLOW_DOC = 'LOG_FOR_WORKFLOW_DOC'
TYPE_LOG_FOR_IMPORT_CSV = 'LOG_FOR_IMPORT_CSV'

KEY_FILTER_DOC_ALL = 'falldoc'
KEY_FILTER_DELETED_DOC = 'fdeldoc'
KEY_FILTER_NOT_DELETED_DOC = 'fnotdeldoc'

ACTION_DELETE_FILE = 'delete_file'
ACTION_UPLOAD_FILE = 'upload_file'
ACTION_DOWNLOAD_FILE = 'download_file'

CLIENT_INFO_MASTER_CODE = 'client_master'
CURRENCY_MASTER_CODE = 'currency_master'

LIST_CURRENCY_DEFAULT_JA = ['円', 'ドル', '元', 'ウォン', 'ユーロ']
LIST_CURRENCY_DEFAULT_EN = ['Yen', 'Dollar', 'Yuan', 'Won', 'Euro']

ACTIVE_LANGUAGES = [ 'ja', 'en' ]
LANGUAGES_MSGID = {
	'ja':'LANGUAGE_JAPANESE',
	'en':'LANGUAGE_ENGLISH'
}

# LINE WORKS直接認証対応…変数化 2019.06.13
SSO_ENTITY_ID = 'https://sateraito-sso/IDP'
SP_ENTITY_ID = sateraito_inc.custom_domain_site_fqdn			# ※ 例：workflow.sateraito.jp （xxx.sateraito.jp形式ならOK）
LINEWORKS_ENTITY_ID_PREFIX = 'https://auth.worksmobile.com/saml2/'
LINEWORKS_SAML_URL_PREFIX = 'https://auth.worksmobile.com/saml2/idp/'

MIME_TYPE_ATTACH_FILE_LINK = [
	'application/vnd.google-apps.shortcut',
	'application/vnd.google-apps.drawing',
	'application/vnd.google-apps.spreadsheet',
	'application/vnd.google-apps.form',
	'application/vnd.google-apps.script',
	'application/vnd.google-apps.map',
	'application/vnd.google-apps.presentation',
	'application/vnd.google-apps.document',
	'application/vnd.google-apps.folder',
]

TEXT_SEARCH_TOKEN_CHARS = ['!', '"', '%', '(', ')', '*', ',', '-', '|', '/', '[', ']', ']', '^', '`', ':', '=', '>', '?', '@', '{', '}', '~', '$']

def getCodeAndReason(error_content):
	error_code = None
	error_reason = None
	try:
		error = json.JSONDecoder().decode(error_content).get('error', None)
		if error is not None:
			error_code = error.get('code')
			logging.debug('error_code:' + str(error_code))
			error_message = error.get('message')
			logging.debug('error_message:' + str(error_message))
			errors = error.get('errors')
			if isinstance(errors, list):
				error_reason = errors[0].get('reason')
				logging.debug('error_reason:' + str(error_reason))
	except BaseException as e:
		logging.info('error: class name:' + e.__class__.__name__ + ' message=' + str(e))

	return error_code, error_reason

def fetch_get_drive_v2_service(google_apps_domain, viewer_email, num_retry=0, do_not_retry=False):
	try:
		calendar_service = _get_drive_service(viewer_email, google_apps_domain)
		return calendar_service
	# except AccessTokenRefreshError as e:  # g2対応
	except RefreshError as e:
		logging.warn('class name:' + e.__class__.__name__ + ' message=' + str(e) + ' num_retry=' + str(num_retry))
		raise e
	except BaseException as e:
		if do_not_retry:
			raise e
		logging.warn('class name:' + e.__class__.__name__ + ' message=' + str(e) + ' num_retry=' + str(num_retry))
		if num_retry > 3:
			raise e
		else:
			sleep_time = timeToSleep(num_retry)
			logging.info('sleeping ' + str(sleep_time))
			time.sleep(sleep_time)
			return fetch_get_drive_v2_service(viewer_email, google_apps_domain, (num_retry + 1), do_not_retry=do_not_retry)

def fetch_get_calendar_v3_service(google_apps_domain, viewer_email, num_retry=0, do_not_retry=False):
	try:
		calendar_service = _get_calendar_service(viewer_email, google_apps_domain)
		return calendar_service
	# except AccessTokenRefreshError as e:  # g2対応
	except RefreshError as e:
		logging.warn('class name:' + e.__class__.__name__ + ' message=' + str(e) + ' num_retry=' + str(num_retry))
		raise e
	except BaseException as e:
		if do_not_retry:
			raise e
		logging.warn('class name:' + e.__class__.__name__ + ' message=' + str(e) + ' num_retry=' + str(num_retry))
		if num_retry > 3:
			raise e
		else:
			sleep_time = timeToSleep(num_retry)
			logging.info('sleeping ' + str(sleep_time))
			time.sleep(sleep_time)
			return fetch_get_calendar_v3_service(viewer_email, google_apps_domain, (num_retry + 1), do_not_retry=do_not_retry)

def fetch_get_admin_sdk_service(google_apps_domain, viewer_email, target_google_apps_domain=None, do_not_use_impersonate_mail=False, credentials=None):
	old_namespace = namespace_manager.get_namespace()
	namespace_manager.set_namespace('')
	impersonate_email = ""
	if do_not_use_impersonate_mail:
		impersonate_email = viewer_email
	else:
		row_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
		if row_dict is not None:
			impersonate_email = row_dict["impersonate_email"]
		if impersonate_email == "":
			impersonate_email = viewer_email

	logging.info('impersonate_email:' + impersonate_email)
	# memcache_expire_secs = 30 * 60 * 1
	# memcache_key = 'script=getappservice&google_app_domain=' + google_app_domain + '&email_to_check=' + impersonate_email
	if credentials is not None:
		service = build('admin', 'directory_v1', credentials=credentials)
	else:
		credentials = get_authorized_http(impersonate_email, google_apps_domain, sateraito_inc.OAUTH2_SCOPES)
		service = build('admin', 'directory_v1', credentials=credentials)

	# set old namespace
	namespace_manager.set_namespace(old_namespace)
	return service


def get_authorized_http(viewer_email, google_apps_domain, scope=sateraito_inc.OAUTH2_SCOPES, timeout_seconds=API_TIMEOUT_SECONDS, is_sub=False):
	logging.info('get_authorized_http')
	if is_sub is True:
		logging.debug('is_sub:True')

	logging.debug('=========get_authorized_http:scope===============')
	logging.debug(scope)

	old_namespace = namespace_manager.get_namespace()
	logging.debug(old_namespace)
	try:
		namespace_manager.set_namespace(google_apps_domain)
		memcache_expire_secs = 60 * 60 * 1
		memcache_key = 'script=getauthorizedhttp&v=2&google_apps_domain=' + google_apps_domain + '&email_to_check=' + viewer_email + '&scope=' + str(scope) + '&g=2'

		# （参考）https://developers.google.com/identity/protocols/oauth2/service-account
		credentials = google.oauth2.service_account.Credentials.from_service_account_info(
			sateraito_inc.SERVICE_ACCOUNT_INFO,
			scopes=scope,
		)
		credentials = credentials.with_subject(viewer_email)
		dict_token_info = memcache.get(memcache_key)
		# @UndefinedVariable
		bool_token_is_valid = False
		if dict_token_info:
			logging.debug('get_authorized_http: cache found.')
			credentials.token = dict_token_info.get('token')
			credentials.expiry = dict_token_info.get('expiry')
			bool_token_is_valid = credentials.valid

		if not bool_token_is_valid:
			http = apiclient.http.build_http()
			request = google_auth_httplib2.Request(http)
			credentials.refresh(request)
			if credentials.valid:
				dict_token_info = {
					'token': credentials.token,
					'expiry': credentials.expiry,
				}
				if not memcache.set(key=memcache_key, value=dict_token_info, time=memcache_expire_secs):  # @UndefinedVariable
					logging.warning("get_authorized_http: Memcache set failed.")
				else:
					logging.warning('get_authorized_http: credentials.refresh')

			logging.debug('credentials.token	= ' + str(credentials.token))
			logging.debug('credentials.expiry = ' + str(credentials.expiry))

		# return http
		return credentials
	except Exception as e:
		logging.exception(e)
	finally:
		# set old namespace
		namespace_manager.set_namespace(old_namespace)

def getImpersonateEmail(google_apps_domain):
	impersonate_email = ''
	row = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain)
	if row is not None:
		impersonate_email = noneToZeroStr(row.impersonate_email)
	return impersonate_email

def fetch_google_app_service(viewer_email, google_app_domain, do_not_use_impersonate_mail=False, credentials=None):
	old_namespace = namespace_manager.get_namespace()
	namespace_manager.set_namespace(google_app_domain)
	impersonate_email = ""
	if do_not_use_impersonate_mail:
		impersonate_email = viewer_email
	else:
		row_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_app_domain)
		if row_dict is not None:
			impersonate_email = row_dict["impersonate_email"]
		if impersonate_email == "":
			impersonate_email = viewer_email

	logging.info('impersonate_email:' + impersonate_email)
	if credentials is not None:
		service = build('admin', 'directory_v1', credentials=credentials)
	else:
		credentials = get_authorized_http(impersonate_email, google_app_domain, sateraito_inc.OAUTH2_SCOPES)
		service = build('admin', 'directory_v1', credentials=credentials)

	# set old namespace
	namespace_manager.set_namespace(old_namespace)
	return service


def check_user_is_admin(google_apps_domain, viewer_email, num_retry=0, do_not_use_impersonate_mail=False,	credentials=None):
	# user_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, viewer_email)
	# if user_dict is not None and 'is_apps_admin' in user_dict:
	# 	return user_dict['is_apps_admin']

	try:
		app_service = fetch_google_app_service(viewer_email, google_apps_domain, do_not_use_impersonate_mail=do_not_use_impersonate_mail, credentials=credentials)
		user_entry = app_service.users().get(userKey=viewer_email).execute()
		logging.info('user_entry:' + str(user_entry))
		if user_entry["isAdmin"] == 'true' or user_entry["isAdmin"] == 'True' or user_entry["isAdmin"]:
			return True
		return False
	# except AccessTokenRefreshError as e:  # g2対応
	except RefreshError as e:
		logging.warn('class name: ' + e.__class__.__name__ + 'message=' + str(e))
		raise ImpersonateMailException()
	except HttpError as e:
		if '403' in str(e):
			# Not Authorized ---> IMPERSONATE_MAIL IS NOT GOOGLE APPS ADMIN, but existing user
			logging.error('class name:' + e.__class__.__name__ + 'message=' + str(e))
			if do_not_use_impersonate_mail:
				return False
			else:
				raise ImpersonateMailException()
		else:
			logging.error('class name:' + e.__class__.__name__ + 'message=' + str(e))
			raise e
	except Exception as instance:
		logging.warn('error in check_user_is_admin:' + instance.__class__.__name__ + 'message=' + str(instance))
		if num_retry > 3:
			raise instance
		else:
			sleep_time = timeToSleep(num_retry)
			logging.info('sleep_time ' + str(sleep_time))
			time.sleep(sleep_time)
			return check_user_is_admin(viewer_email, google_apps_domain, (num_retry + 1))


# mail address easy check
def isMailAddress(str_param):
	if str_param is None or str_param == '':
		return False
	atmark_splited = str(str_param).split('@')
	if len(atmark_splited) < 2:
		return False
	# period_splited = str(atmark_splited).split('.')
	# if len(period_splited) < 2:
	# 	return False
	return True


def updateFreeSpaceStatus(google_apps_domain):
	total_file_size = sateraito_db.FileSizeCounterShared.get_total()
	domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
	if domain_dict['max_total_file_size'] <= sateraito_db.DEFAULT_MAX_TOTAL_FILE_SIZE:
		max_total_file_size = sateraito_db.DEFAULT_MAX_TOTAL_FILE_SIZE
	else:
		max_total_file_size = domain_dict['max_total_file_size']
	if max_total_file_size < total_file_size:
		# capacity over
		if not domain_dict['is_capacity_over']:
			domain = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain)
			domain.is_capacity_over = True
			domain.put()
	else:
		# capacity safe
		if domain_dict['is_capacity_over']:
			domain = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain)
			domain.is_capacity_over = False
			domain.put()


def convertToJPTime(utctime_rfc3339):
	"""  Convert UTC based datetime to JST based datetime(+09:00)
		Args string utctime_rfc3339 ... YYYY-MM-DDTHH:MI:SS
		Return string YYYY-MM-DD HH:MI:SS(localtime)
	"""
	# create UTC datetime
	utctime_rfc3339_splited = utctime_rfc3339.split('.')  # cut off microtime
	utctime_rfc3339_splited_date_and_time = utctime_rfc3339_splited[0].split('T')  # devide date and time
	time_parts = utctime_rfc3339_splited_date_and_time[1].split(':')
	utctime_dt = datetime.datetime.strptime(utctime_rfc3339_splited_date_and_time[0], '%Y-%m-%d')
	utctime_dt = utctime_dt + datetime.timedelta(hours=int(time_parts[0]))
	utctime_dt = utctime_dt + datetime.timedelta(minutes=int(time_parts[1]))
	utctime_dt = utctime_dt + datetime.timedelta(seconds=int(time_parts[2]))

	return toShortLocalTime(utctime_dt)

# seconds to wait till next retry
# 1, 2, 4, 8, 16, 32, 60, 60, 60, 60,  ...(default max interval)
# 3, 6, 12, 24, 48, 60, 60, 60, 60, 60,  ...(default max interval, hard_sleep)
# 1, 2, 4, 8, 16, 32, 64, 128, 256, 512,  ...(max_interval=7200)
# 3, 6, 12, 24, 48, 96, 192, 384, 768, 1536,  ...(max_interval=7200, hard_sleep)
def timeToSleep(num_retry, max_interval=60, hard_sleep=False):
	sleep_time = 2 ** num_retry
	if hard_sleep:
		sleep_time = sleep_time * 3
	if sleep_time > max_interval:
		sleep_time = max_interval
	return sleep_time

def addCheckAccessibleInfoQueue(google_apps_domain, app_id, email, countdown=10):
	queue = taskqueue.Queue('default')
	task = taskqueue.Task(
		url='/' + google_apps_domain + '/' + app_id + '/textsearch/tq/checkaccessibleinfo',
		params={
			'user_email': email
		},
		target=getBackEndsModuleNameDeveloper('b1process'),
		countdown=countdown
	)
	queue.add(task)

def addUpdateAccessibleInfoForAllDoc(google_apps_domain, app_id, countdown=10):
	# immediate update accessible info
	queue = taskqueue.Queue('update-accessible-info')
	task = taskqueue.Task(
		url='/' + google_apps_domain + '/' + app_id + '/docfolder/tq/updateaccessibleinfo',
		params={
		},
		target=getBackEndsModuleNameDeveloper('b1process'),
		countdown=countdown
	)
	queue.add(task)

def addUpdateFolderTextSearchDocQueue(google_apps_domain, app_id, email, folder_code, countdown=10):
	queue = taskqueue.Queue('default')
	task = taskqueue.Task(
		url='/' + google_apps_domain + '/' + app_id + '/docfolder/tq/updatefoldertextsearchdoc',
		params={
			'user_email': email,
			'folder_code': folder_code,
		},
		target=getBackEndsModuleNameDeveloper('b1process'),
		countdown=countdown
	)
	queue.add(task)


def getAllDocFolderNos(google_apps_domain, app_id):
	row = sateraito_db.AllDocFolder.getInstance()
	if row is None:
		requestUpdateAllFolder(google_apps_domain, app_id)
		return False, []
	update_time_info_dict = sateraito_db.UpdateTimeInfo.getDict()
	if row.rebuild_finish_date < update_time_info_dict['doc_folder_updated_date']:
		requestUpdateAllFolder(google_apps_domain, app_id)
		return False, []
	else:
		return True, row.folder_nos


def requestUpdateAllFolder(google_apps_domain, app_id, defer=0):
	logging.info("requestUpdateAllFolder")
	# request update
	queue = taskqueue.Queue('default')
	task = taskqueue.Task(
		url='/' + google_apps_domain + '/' + app_id + '/docfolder/tq/updatealldocfoldernos',  # Update folder to folder
		countdown=defer,
		target=getBackEndsModuleNameDeveloper('default'),
	)
	queue.add(task)


def getScriptVersionQuery():
	return UcfUtil.md5(sateraito_inc.version)


def isOkToAccessDocId(user_email, doc_id, google_apps_domain, app_id):
	""" check if user is ok to access for the document """
	row_dict = sateraito_db.WorkflowDoc.getDict(doc_id)
	if row_dict is None:
		return False
	else:
		return isOkToAccessDocDict(user_email, row_dict, google_apps_domain, app_id)


def isOkToAccessDocObj(user_email, row_doc, google_apps_domain, app_id=None, user_accessible_info_dict=None):
	""" check if user can access workflow document --> DEPRECATED, should use isOkToAccessDocDict
	"""
	if row_doc is None:
		return False

	# check doc_type base check
	if user_accessible_info_dict is None:
		user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(user_email, auto_create=True)
		if user_accessible_info_dict is None:
			if isWorkflowAdmin(user_email, google_apps_domain, app_id):
				return True
			return False

	google_apps_user_entry_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, user_email)
	is_fulltext_ready = isFulltextReady(user_accessible_info_dict, google_apps_user_entry_dict)

	# check logic if fulltext ready
	if is_fulltext_ready:
		logging.info('fulltext ready. check priv by user_accessible_info saved data...')
		doc_dict = row_doc.to_dict()
		is_accessible = checkDocPrivByUserInfo(doc_dict, user_accessible_info_dict)
		if is_accessible:
			return True
		else:
			if isWorkflowAdmin(user_email, google_apps_domain, app_id):
				return True
			return False

	# check logic even if not fulltext ready
	is_folder_ok = sateraito_db.DocFolder.isAccessibleFolder(row_doc['folder_code'], user_accessible_info_dict)
	if is_folder_ok:
		return True
	# check if I am WorkflowAdmin User
	if isWorkflowAdmin(user_email, google_apps_domain, app_id):
		return True
	return False


def isOkToAccessDocDict(user_email, doc_dict, google_apps_domain, app_id=None, user_accessible_info_dict=None):
	""" check if user can access workflow document
	"""
	if doc_dict is None:
		return False

	if user_accessible_info_dict is None:
		user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(user_email, auto_create=True)
		if user_accessible_info_dict is None:
			if isWorkflowAdmin(user_email, google_apps_domain, app_id):
				return True
			return False

	google_apps_user_entry_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, user_email)
	is_fulltext_ready = isFulltextReady(user_accessible_info_dict, google_apps_user_entry_dict)

	# check logic if fulltext ready
	if is_fulltext_ready:
		logging.info('fulltext ready. check priv by user_accessible_info saved data...')
		is_accessible = checkDocPrivByUserInfo(doc_dict, user_accessible_info_dict)
		if is_accessible:
			return True
		else:
			if isWorkflowAdmin(user_email, google_apps_domain, app_id):
				return True
			return False

	# check logic even if not fulltext ready
	is_folder_ok = sateraito_db.DocFolder.isAccessibleFolder(doc_dict['folder_code'], user_accessible_info_dict)
	if is_folder_ok:
		return True
	# check if I am WorkflowAdmin User
	if isWorkflowAdmin(user_email, google_apps_domain, app_id):
		return True
	return False


def getUserInfoName(email, with_space=False):
	row_dict = sateraito_db.UserInfo.getDict(email)
	if row_dict is not None:
		if with_space:
			return row_dict['family_name'] + ' ' + row_dict['given_name']
		else:
			return row_dict['family_name'] + row_dict['given_name']
	return ''


def loggingRuntimeStatus():
	""" output backend memory status and shutting down signal to GAE log
		"""
	is_shutting_down = runtime.is_shutting_down()
	current_memory_usage = runtime.memory_usage().current
	logging.info('** current_memory_usage=' + str(current_memory_usage) + ' is_shutting_down=' + str(is_shutting_down))


def isValidAppId(app_id):
	# app_id must
	#  not start from '_'
	#  contain only alphabet, numeric and _ and - character
	#  not contain '_____'
	if app_id is None or app_id == '':
		return True
	regexp = re.compile('^[0-9A-Za-z_\-]+$')
	if regexp.search(app_id) is None:
		# app_id have prohibited character
		return False
	if app_id[0:1] == '_':
		# app_id starts with '_'
		return False
	if app_id.find(DELIMITER_NAMESPACE_DOMAIN_APP_ID) != -1:
		# app_id contains '_____'
		return False
	return True


def setNamespace(google_apps_domain, app_id):
	"""  Args: google_apps_domain
				app_id
	Return: True is app_id is correct, false is not
	"""
	# app_id check
	if not isValidAppId(app_id):
		logging.warn('wrong app_id:' + str(app_id))
		return False
	namespace_name = google_apps_domain
	if app_id is None or app_id == '' or app_id == DEFAULT_APP_ID:
		# if app_id is default app id, namespace_name == google_apps_domain
		pass
	else:
		namespace_name += DELIMITER_NAMESPACE_DOMAIN_APP_ID + app_id
	logging.info('setNamespace google_apps_domain=%s, app_id=%s, namespace=%s' % (google_apps_domain, app_id, namespace_name))
	namespace_manager.set_namespace(namespace_name)
	return True


def getDomainAndAppIdFromNamespaceName(namespace_name):
	if namespace_name == sateraito_db.DOWNLOAD_CSV_NAMESPACE:
		return '', ''
	google_apps_domain = ''
	app_id = ''
	splited = namespace_name.split(DELIMITER_NAMESPACE_DOMAIN_APP_ID)
	num_splited = len(splited)
	if num_splited > 1:
		google_apps_domain = splited[0]
		app_id = splited[1]
	else:
		google_apps_domain = namespace_name
		app_id = DEFAULT_APP_ID
	return google_apps_domain, app_id


def checkGroupUpdated(google_apps_domain, app_id, viewer_email):
	"""
		return: True ... need update accessible info
						False .. no need to update accessible info
	"""
	# fetch data from google
	ret_groups = []
	try:
		ret_groups = getMyJoiningGroup(google_apps_domain, viewer_email, viewer_email)
	except urlfetch.DownloadError as instance:
		logging.warn('Gdata request timeout')
		return False
	# check if updating userInfo is needed
	user_entry = sateraito_db.GoogleAppsUserEntry.getInstance(google_apps_domain, viewer_email)
	group_updated = False
	if user_entry is not None:
		if user_entry.google_apps_groups is None:
			# google_apps_groups not set ---> need update priv using user joining groups
			group_updated = True
		elif not isSameMembers(ret_groups, user_entry.google_apps_groups):
			# my joining groups changed --> need update priv based on new user joining groups
			group_updated = True
	# if user's joining group is changed, accessible category is needed to update based on his joining group
	if group_updated:
		logging.info('need update UserInfo.google_apps_groups: send task queue')
		# update group info
		user_entry.google_apps_groups = ret_groups
		user_entry.google_apps_groups_updated_date = datetime.datetime.now()
		user_entry.put()
	return group_updated


def isOkToAccessAppId(user_email, google_apps_domain, app_id):
	""" check if user allowed to use the app_id
	"""
	old_namspace = namespace_manager.get_namespace()
	setNamespace(google_apps_domain, app_id)
	other_setting = sateraito_db.OtherSetting.getInstance(auto_create=True)
	namespace_manager.set_namespace(old_namspace)

	# check.1 is limit setting on
	if not other_setting.limit_access_to_doc_management:
		return True
	# check.2 is user is member of allowed group member
	set1 = set(other_setting.access_allowed_user_groups)
	user_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, user_email)
	set2 = set(user_dict['google_apps_groups'])
	set2.add(user_email)
	if len(set1 & set2) > 0:
		return True
	# check.3 if user admin --> OK to access
	is_workflow_admin = isWorkflowAdmin(user_email, google_apps_domain, app_id)
	if is_workflow_admin:
		return True
	return False

def isOkToDeleteWorkflowDoc(user_email, google_apps_domain, app_id, other_setting=None):
	""" check if user allowed to edit workflow app
	"""

	if other_setting is None:
		old_namspace = namespace_manager.get_namespace()
		setNamespace(google_apps_domain, app_id)
		other_setting = sateraito_db.OtherSetting.getDict(auto_create=True)
		namespace_manager.set_namespace(old_namspace)

	# check.1 is can edit doc setting on
	if not other_setting['user_can_delete_doc']:
		return False
	if len(other_setting['users_groups_can_delete_doc']) == 0:  # allow all user
		return True

	# check.2 is user is member of allowed group member
	set1 = set(other_setting['users_groups_can_delete_doc'])

	user_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, user_email)
	set2 = set(user_dict['google_apps_groups'])
	set2.add(user_email)
	if len(set1 & set2) > 0:
		return True
	# # check.3 if user admin --> OK to access
	# is_workflow_admin = isWorkflowAdmin(user_email, google_apps_domain)
	# if is_workflow_admin:
	# 	return True
	return False


def getUserInfoOAuth2(user_email, google_apps_domain):
	# get from GoogleApps name
	try:
		app_service = fetch_google_app_service(user_email, google_apps_domain)
		user_entry = app_service.users().get(userKey=user_email).execute()
	except BaseException as instance:
		# entry does not exists
		logging.warn('instance=' + str(instance))
	else:
		return user_entry

def getUserInfo(google_apps_domain, user_email):
	# get from GoogleApps name
	ret_user_name = user_email

	try:
		# SSOGadget対応
		if sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(google_apps_domain, domain_dict=None):
			logging.info('isSSOGadgetTenant')
			user_entry = getUserInfoSSOGadget(google_apps_domain, user_email)
		# SSiteGadget対応
		elif sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(google_apps_domain, domain_dict=None):
			logging.info('isSSiteTenant')
			user_entry = getUserInfoSSiteGadget(google_apps_domain, user_email)
		else:
			user_entry = getUserInfoOAuth2(user_email, google_apps_domain)
	except BaseException as instance:
		# entry does not exists
		logging.warn('instance=' + str(instance))
	else:
		return user_entry

def getUserName(google_apps_domain, user_email):
	# get from GoogleApps name
	ret_user_name = user_email

	try:
		# SSOGadget対応
		if sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(google_apps_domain, domain_dict=None):
			logging.info('isSSOGadgetTenant')
			user_entry = getUserInfoSSOGadget(google_apps_domain, user_email)
			return str(user_entry['given_name'])

		# SSiteGadget対応
		elif sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(google_apps_domain, domain_dict=None):
			logging.info('isSSiteTenant')
			user_entry = getUserInfoSSiteGadget(google_apps_domain, user_email)
			return str(user_entry['name']['fullName'])

		else:
			user_entry = getUserInfoOAuth2(user_email, google_apps_domain)
			return str(user_entry['name']['fullName'])

	except BaseException as instance:
		# entry does not exists
		logging.warn('instance=' + str(instance))

	return ''

def getUserLocaleAndTimezone(viewer_email):

	cached_data = memcache.get('_ger_user_locale_and_timezone?viewer_email=' + viewer_email)
	if cached_data is not None:
		cached_data_splited = str(cached_data).split('|')
		if len(cached_data_splited) == 2:
			logging.info('found and respond _ger_user_locale_and_timezone cache')
			return cached_data_splited[0], cached_data_splited[1]

	# if you get email correctry, you can get his calendar data even if he has not log on to this script or other user's request
	google_apps_domain = viewer_email.split('@')[1]
	service = fetch_get_calendar_v3_service(google_apps_domain, viewer_email)

	# get calendar setting feed
	try:
		calendar = service.calendars().get(calendarId=viewer_email).execute()
	except BaseException as e:
		logging.info('instance=' + str(e))
		logging.warn('Request Error, returns default locale and timezone')
		return 'ja', 'Asia/Tokyo'

	# get locale and timezone
	locale = ''
	timezone_name = ''
	if calendar["location"]:
		locale = calendar["location"]
	if calendar["timeZone"]:
		timezone_name = calendar["timeZone"]

	logging.info('locale=' + locale)
	logging.info('timezone=' + timezone_name)
	# save to memory cache: 10 mins
	if not memcache.set(key='_ger_user_locale_and_timezone?viewer_email=' + viewer_email + '&g=2', value=locale + '|' + timezone_name, time=(60 * 10)):
		logging.warning("Memcache set failed.")
	return locale, timezone_name


def getMyJoiningGroup(google_apps_domain, email_to_check, viewer_email):
	# memcache entry expires in 10 min
	memcache_expire_secs = 60 * 30
	memcache_key = 'script=getMyJoiningGroup?google_apps_domain=' + google_apps_domain + '&email_to_check=' + email_to_check + '&g=2'

	# check if cached data exists
	cached_data = memcache.get(memcache_key)
	if cached_data is not None:
		logging.info('_getMyJoiningGroup: found and respond cached data')
		return cached_data

	# SSOGadget対応
	if sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(google_apps_domain):
		groups = getMyJoiningGroupSSOGadget(google_apps_domain, email_to_check)
	# SSiteGadget対応
	elif sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(google_apps_domain):
		groups = getMyJoiningGroupSSiteGadget(google_apps_domain, email_to_check, viewer_email)
	else:
		# OAuth2対応
		groups = _getMyJoiningGroupOAuth2(google_apps_domain, email_to_check, viewer_email)
	logging.info('getMyJoiningGroup groups=' + str(groups))

	# add data to cache
	if not memcache.set(key=memcache_key, value=groups, time=memcache_expire_secs):
		logging.warning("Memcache set failed.")
	return groups

def getGroupListAll(directory_service, page_token, num_retry=0, do_not_retry=False):
	logging.debug('getGroupListAll')
	try:
		# fill 'my_customer' as customer  https://developers.google.com/admin-sdk/directory/v1/reference/groups/list
		group_list = directory_service.groups().list(customer='my_customer', pageToken=page_token, fields="groups(description,email,name),nextPageToken").execute()
		logging.info('group_list:' + str(group_list))
		return group_list
	except HttpError as e:
		logging.warn('class name:' + e.__class__.__name__ + ' message=' + str(e))
		# Load Json body
		logging.info('e.content=' + str(e.content))
		error_code, error_reason = getCodeAndReason(e.content)
		# Implementing exponential backoff
		if do_not_retry:
			raise e
		if error_code == 403 and error_reason in ['rateLimitExceeded', 'userRateLimitExceeded', 'quotaExceeded']:
			logging.warn('** userRateLimitExceeded')
			if num_retry > 3:
				raise e
			else:
				sleep_time = timeToSleep(num_retry)
				logging.info('sleep ' + str(sleep_time))
				time.sleep(sleep_time)
				return getGroupListAll(directory_service, page_token, (num_retry + 1))
		raise e

def getGroupList(directory_service, email_to_check, num_retry=0):
	# memcache entry expires in 60 min
	memcache_expire_secs = 60 * 60
	memcache_key = 'script=getgrouplist?email_to_check=' + email_to_check + '&g=2'
	# check if cached data exists
	cached_data = memcache.get(memcache_key)
	if cached_data is not None:
		logging.info('getgrouplist: found and respond cached data')
		return cached_data
	page_token = None
	groups = []
	try:
		while True:
			group_list = directory_service.groups().list(userKey=email_to_check, pageToken=page_token, fields="groups(email),nextPageToken").execute()
			if 'groups' in group_list:
				groups.extend(group_list['groups'])
			page_token = group_list.get('nextPageToken')
			if page_token is None:
				break
		# add data to cache
		if not memcache.set(key=memcache_key, value=groups, time=memcache_expire_secs):
			logging.warning("Memcache set failed.")
		return groups
	except BaseException as e:
		logging.info('error: class name:' + e.__class__.__name__ + ' message=' + str(e))
		if num_retry < 10:
			sleep_time = timeToSleep(num_retry)
			logging.info('retrying ' + str(num_retry))
			time.sleep(sleep_time)
			return getGroupList(directory_service, email_to_check, (num_retry + 1))
		else:
			raise e

def _getMyJoiningGroupOAuth2(google_apps_domain, email_to_check, viewer_email, directory_service=None, processed_group_emails=None):
	""" Get all groups for a member
				@param {str} google_apps_domain
				@param {str} email_to_check
				@param {str} viewer_email
				@param {object} directory_service
				@return {list}
		"""
	logging.info('_getMyJoiningGroupOAuth2 processed_group_emails=' + str(processed_group_emails))

	# 処理済みグループ判別用set
	if processed_group_emails is None:
		processed_group_emails = set([])

	groups = []
	google_apps_domain_of_viewer_email = getDomainPart(viewer_email)
	if directory_service is None:
		directory_service = fetch_google_app_service(viewer_email, google_apps_domain)
		logging.info(
			'_getMyJoiningGroupOAuth2: google_apps_domain_of_viewer_email=' + str(google_apps_domain_of_viewer_email))

	group_list = getGroupList(directory_service, email_to_check)
	for each_group in group_list:
		group_email = str(each_group['email']).lower()
		if not (group_email in processed_group_emails) and (isCompatibleDomain(google_apps_domain, google_apps_domain_of_viewer_email) or isCompatibleDomain(google_apps_domain, getDomainPart(group_email))):
			groups.append(group_email)
			processed_group_emails.add(group_email)
			parent_groups = _getMyJoiningGroupOAuth2(google_apps_domain, group_email, viewer_email, directory_service=directory_service, processed_group_emails=processed_group_emails)
			groups.extend(parent_groups)

	# remove duplicate
	groups = list(set(groups))
	return groups

def isSameMembers(list_1, list_2):
	""" Args:
				list_1: list
				list_2: list
		Returns:
				boolean
		"""
	set_1 = set(list_1)
	set_2 = set(list_2)
	if len(set_1 - set_2) == 0 and len(set_2 - set_1) == 0:
		return True
	return False


def getDomainFromNamespace(namespace_name):
	splited = namespace_name.split(DELIMITER_NAMESPACE_DOMAIN_APP_ID)
	num_splited = len(splited)
	if num_splited == 2:
		return splited[0]
	return namespace_name


def isFutureDate(publish_start_date):
	tz_utc = zoneinfo.gettz('UTC')
	datetime_now = datetime.datetime.now(tz_utc)
	datetime_now_native = datetime_now.replace(tzinfo=None)
	is_future_date = False
	if publish_start_date is not None:
		publish_start_date_native = publish_start_date.replace(tzinfo=None)
		if publish_start_date_native > datetime_now_native:
			is_future_date = True
	return is_future_date


def specialDateToNone(datetime_param):
	if datetime_param is None:
		return None
	if datetime_param <= datetime.datetime(1970, 1, 2, 0, 0, 0):
		return None
	return datetime_param


def datetimeToUnixtime(datetime_param):
	return time.mktime(datetime_param.timetuple())


def createSearchDoc(row):
	""" create index document for textsearch
	"""
	return sateraito_search.create_search_doc(row)

def createSearchFile(row):
	""" create index document for textsearch
	"""
	return sateraito_search.create_search_file(row)


def rebuildTextSearchIndex(doc_id):
	""" re-build fulltext search index for doc
		using doc_id
	"""
	row_doc = sateraito_db.WorkflowDoc.getInstance(doc_id)
	if row_doc is None:
		removeDocFromIndex(doc_id)
	else:
		rebuildTextSearchIndexDoc(row_doc)


def rebuildTextSearchIndexDoc(row_doc, row_grp_view_def=None):
	""" re-build fulltext search index for doc
		using WorkflowDoc instance
	"""
	if row_doc is not None:
		removeDocFromIndex(row_doc.workflow_doc_id)
		addDocToTextSearchIndex(row_doc)


def addDocToTextSearchIndex(row_doc, is_update=False):
	""" add doc to textsearch index
		Args: row_doc ... WorkflowDoc object
	"""
	sateraito_search.add_doc_to_text_search_index(row_doc, is_update)

def addFileToTextSearchIndex(row_doc):
	""" add file to textsearch index
		Args: row_doc ... FileflowDoc object
	"""
	return sateraito_search.add_file_to_text_search_index(row_doc)


def buildCustomSortFieldValue(doc_values_dict, custom_sort_fields, doc_title):
	""" create string values to set custom sort field from document content values
	"""
	ret_text = u''
	custom_sort_fields_array = str(custom_sort_fields).split(' ')
	for custom_sort_field_name in custom_sort_fields_array:
		if custom_sort_field_name == 'doc_title':
			ret_text += doc_title
			continue
		if custom_sort_field_name + '__display_value' in doc_values_dict:
			ret_text += doc_values_dict[custom_sort_field_name + '__display_value']
			continue
		if custom_sort_field_name in doc_values_dict:
			ret_text += str(doc_values_dict[custom_sort_field_name])
			continue
	return ret_text


def buildCustomSortFieldNumberValue(doc_values_dict, custom_sort_fields, doc_title):
	""" create string values to set custom sort field from document content values
	"""
	ret_text = u''
	custom_sort_fields_array = str(custom_sort_fields).split(' ')
	for custom_sort_field_name in custom_sort_fields_array:
		if custom_sort_field_name == 'doc_title':
			if str(doc_title).isdigit():
				ret_text += str(doc_title)
			continue
		if custom_sort_field_name + '__display_value' in doc_values_dict:
			field_value = doc_values_dict[custom_sort_field_name + '__display_value']
			if str(field_value).isdigit():
				ret_text += str(field_value)
			continue
		if custom_sort_field_name in doc_values_dict:
			field_value = doc_values_dict[custom_sort_field_name]
			if str(field_value).isdigit():
				ret_text += str(field_value)
			continue
	ret_number = 0
	try:
		ret_number = int(ret_text)
	except ValueError:
		pass
	return ret_number


def removeDocFromIndex(workflow_doc_id, num_retry=0):
	return sateraito_search.remove_doc_from_index(workflow_doc_id, num_retry=num_retry)


def removeFileFromIndex(file_id, num_retry=0):
	return sateraito_search.remove_file_from_index(file_id, num_retry=num_retry)


def getPossibleCheckKeys(user_email, secret_key):
	possible_check_keys = []
	tz_user_local = zoneinfo.gettz('Asia/Tokyo')
	tz_utc = zoneinfo.gettz('UTC')
	stamp_datetime_utc = datetime.datetime.now(tz_utc)
	stamp_datetime_localtime = stamp_datetime_utc.replace(tzinfo=tz.tzutc()).astimezone(tz_user_local)
	for i in [-3, -2, -1, 0, 1, 2, 3]:
		yyyymmdd = (stamp_datetime_localtime + datetime.timedelta(i)).strftime('%Y%m%d')
		possible_check_keys.append(UcfUtil.md5.new(user_email + yyyymmdd + secret_key).hexdigest())
	return possible_check_keys


def strToBool(str_param):
	if str_param.lower() == 'true':
		return True
	return False


def boolToStr(bool_param):
	if bool_param:
		return 'True'
	return 'False'


def noneToFalse(bool_param):
	if bool_param is None:
		return False
	return bool_param


def isFulltextReady(user_accessible_info_dict, google_apps_user_entry_dict):
	""" check accessible_folder data is newer than folder data
		and accessible_doc_type data is newer than doc_type data
		If newer, it is OK to use fulltext type priv checking
	"""
	return False

	# need_update = False
	# if user_accessible_info_dict['accessible_cat_and_type_updated_date'] is None:
	# 	logging.info('accessible_cat_and_type_updated_date')
	# 	need_update = True
	# elif user_accessible_info_dict['need_update']:
	# 	logging.info('need_update')
	# 	need_update = True
	# else:
	# 	update_time_info_dict = sateraito_db.UpdateTimeInfo.getDict()
	# 	logging.info('accessible_cat_and_type_updated_date')
	# 	logging.info(user_accessible_info_dict['accessible_cat_and_type_updated_date'])
	# 	logging.info('doc_folder_updated_date')
	# 	logging.info(update_time_info_dict['doc_folder_updated_date'])
	# 	logging.info('doc_type_updated_date')
	# 	logging.info(update_time_info_dict['doc_type_updated_date'])
	#
	# 	if user_accessible_info_dict['accessible_cat_and_type_updated_date'] < update_time_info_dict['doc_folder_updated_date']:
	# 		need_update = True
	# 	elif user_accessible_info_dict['accessible_cat_and_type_updated_date'] < update_time_info_dict['doc_type_updated_date']:
	# 		need_update = True
	# 	elif google_apps_user_entry_dict['google_apps_groups_updated_date'] is not None:
	# 		logging.info('google_apps_groups_updated_date')
	# 		logging.info(google_apps_user_entry_dict['google_apps_groups_updated_date'])
	# 		if user_accessible_info_dict['updated_date'] < google_apps_user_entry_dict['google_apps_groups_updated_date']:
	# 			need_update = True
	# 		else:
	# 			# email = user_accessible_info_dict['email']
	# 			# user_info_dict = sateraito_db.UserInfo.getDict(email)
	# 			#
	# 			# logging.info('user_accessible_info_dict.updated_date')
	# 			# logging.info(user_accessible_info_dict['updated_date'])
	# 			# logging.info('user_info_dict.updated_date')
	# 			# logging.info(user_info_dict['updated_date'])
	#
	# 			if user_accessible_info_dict['updated_date'] < google_apps_user_entry_dict['updated_date']:
	# 				need_update = True

	# return not need_update


def checkDocPrivByUserInfo(doc_dict, user_accessible_info_dict):
	folder_code = doc_dict['folder_code']
	# check user priv
	is_accessible = True
	# check folder code
	if folder_code is not None and folder_code != '':
		is_accessible = sateraito_db.DocFolder.isAccessibleFolder(folder_code, user_accessible_info_dict)
	if is_accessible:
		logging.info('checkDocPrivByUserInfo: folder and doc_type is OK, checking docs priv')
		return True
	else:
		logging.info('checkDocPrivByUserInfo: return False')
		return False

def checkCsrf(request):
	"""
		AJax の Post で呼び出されたリクエストの CSRF（クロスサイトリクエストフォージェリ）をチェック。
		問題がない場合は True を返す
	"""

	headers = request.headers

	strHost = headers.get('Host')
	strOrigin = headers.get('Origin')
	strXRequestedWith = headers.get('X-Requested-With')

	# カスタムドメイン対応
	if strHost != sateraito_inc.site_fqdn and strHost != sateraito_inc.custom_domain_site_fqdn:
		logging.error('Invalid Request Header : Host : ' + str(strHost))
		return False

	# カスタムドメイン対応
	if strOrigin is not None and strOrigin != sateraito_inc.my_site_url and strOrigin != sateraito_inc.custom_domain_my_site_url:
		logging.error('Invalid Request Header : Origin : ' + str(strOrigin))
		return False

	# if (strXRequestedWith != 'XMLHttpRequest'):
	# 	logging.error('Invalid Request Header : X-Requested-With : ' + str(strXRequestedWith))
	# 	return False

	logging.info('csrf token is ok.')
	return True

# def getScriptVirtualUrl():
# 	return '/js/' if not sateraito_inc.debug_mode else '/js/debug/'

def strToDate(str_param):
	""" convert string YYYY-MM-DD HH:MI:SS to datetime obj(Tokyo Timezone)
	"""
	if str_param is None:
		return None
	if str_param.strip() == '':
		return None
	datetime_splited = str_param.split(' ')
	date_splited = (datetime_splited[0]).split('-')
	year = int(date_splited[0])
	month = int(date_splited[1])
	day = int(date_splited[2])
	hour = 0
	minutes = 0
	second = 0
	if len(datetime_splited) >= 2:
		time_splited = (datetime_splited[1]).split(':')
		hour = int(time_splited[0])
		minutes = int(time_splited[1])
		if len(time_splited) >= 3:
			second = int(time_splited[2])
	tz_user_local = zoneinfo.gettz('Asia/Tokyo')
	return datetime.datetime(year, month, day, hour, minutes, second, 0, tz_user_local)


def strToUTCDate(utctime_rfc3339):
	"""  Convert UTC based datetime string
	"""
	utctime_rfc3339_splited = utctime_rfc3339.split('.')  # cut off microtime
	utctime_rfc3339_splited_date_and_time = utctime_rfc3339_splited[0].split('T')  # devide date and time
	time_parts = utctime_rfc3339_splited_date_and_time[1].split(':')
#  utctime_dt = datetime.datetime.strptime(utctime_rfc3339_splited[0], '%Y-%m-%dT%H:%M:%S')  ##### this code can not be used because some data have over 24 value for hour part
	utctime_dt = datetime.datetime.strptime(utctime_rfc3339_splited_date_and_time[0], '%Y-%m-%d')
	utctime_dt = utctime_dt + datetime.timedelta(hours=int(time_parts[0]))
	utctime_dt = utctime_dt + datetime.timedelta(minutes=int(time_parts[1]))
	utctime_dt = utctime_dt + datetime.timedelta(seconds=int(time_parts[2]))
	return utctime_dt


def toUtcTime(date_localtime, timezone=None):
	""" Args: date_localtime ... datetime
												timezone ... timezone name
				Return: datetime
		"""
	if date_localtime is None:
		return None
	if timezone is None:
		timezone = sateraito_inc.DEFAULT_TIMEZONE
		#  tz_user_local = zoneinfo.gettz('Asia/Tokyo')
	tz_user_local = zoneinfo.gettz(timezone)
	tz_utc = tz.tzutc()
	return date_localtime.replace(tzinfo=tz_user_local).astimezone(tz_utc)


def toLocalTime(date_utc, timezone=None):
	"""
		Args: data_utc ... datetime
		Returns: datetime
		"""
	if date_utc is None:
		return None
	if timezone is None:
		timezone = sateraito_inc.DEFAULT_TIMEZONE
	tz_user_local = zoneinfo.gettz(timezone)
	return date_utc.replace(tzinfo=tz.tzutc()).astimezone(tz_user_local)


def toShortLocalTime(date_utc, timezone=None):
	"""
	Args: date_utc ... datetime
	Returns: string YYYY-MM-DD HH:MI:SS
	"""
	if date_utc is None:
		return ''
	if timezone is None:
		timezone = sateraito_inc.DEFAULT_TIMEZONE
	local_time = toLocalTime(date_utc, timezone)
	return (str(local_time).split('.'))[0]

def toShortLocalDate(date_utc, timezone=sateraito_inc.DEFAULT_TIMEZONE):
	"""
	Args: date_utc ... datetime
	Returns: string YYYY-MM-DD
	"""
	return toShortLocalTime(date_utc, timezone).split(' ')[0]

def getLocalDate(date_utc):
	"""
	Args: date_utc ... datetime
	Returns: string YYYY-MM-DD
	"""
	if date_utc is None:
		return ''
	local_date_time = toShortLocalTime(date_utc)
	return (str(local_date_time).split(' '))[0]

def toLocalDate(date_utc, timezone=None):
	"""
	Args: date_utc ... datetime
	Returns: string YYYY-MM-DD
	"""
	if date_utc is None:
		return ''
	local_date_time = toShortLocalTime(date_utc, timezone)
	return (str(local_date_time).split(' '))[0]

def isCompatibleDomain(google_apps_domain, possible_sub_domain):
	if google_apps_domain == possible_sub_domain:
		return True
	sub_domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain, subdomain=possible_sub_domain)
	if sub_domain_dict is not None:
		# sub domain entry found in primary domain namespace --> OK!
		return True
	return False


def noneToZeroStr(string_param):
	if string_param is None:
		return ''
	return string_param


def listDiff(list_1, list_2):
	set_1 = set(list_1)
	set_2 = set(list_2)
	set_diff = set_1 - set_2
	return list(set_diff)


def getDomainPart(email_address):
	a_email_address = email_address.split('@')
	if len(a_email_address) > 1:
		return a_email_address[1]
	else:
		return ''


# 各通知メールの件名用申請番号…apply_noがあればそれを取得。なければ申請番号（doc_no）。どちらもなければ空
def getDocNoForMailSubject(doc):
	subject_doc_no = ''
	if doc.apply_no is not None and doc.apply_no != '':
		subject_doc_no = doc.apply_no
	elif doc.doc_values is not None and doc.doc_values != '':
		doc_values_dict = json.JSONDecoder().decode(doc.doc_values)
		if 'doc_no' in doc_values_dict:
			subject_doc_no = doc_values_dict['doc_no']
	return subject_doc_no


def createNewUserToken():
	""" create new user token string
	"""
	# create 64-length random string
	s = 'abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
	random_string = ''
	for j in range(64):
		random_string += random.choice(s)
	return random_string


def dateString():
	# create date string
	dt_now = datetime.datetime.now()
	return dt_now.strftime('%Y%m%d%H%M%S')


def randomString(string_length=16):
	# create 16-length random string
	s = 'abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
	random_string = ''
	for j in range(string_length):
		random_string += random.choice(s)
	return random_string


def dateTimeToString(_datetime):
	if _datetime is None:
		return None
	return _datetime.strftime("%Y/%m/%d %H:%M")

def createImportId():
	""" create new import id string
	"""
	return 'imp-' + dateString() + randomString()

def createCsvDownloadId():
	""" create new csv download id string
	"""
	return 'csvdl-' + dateString() + randomString()


def isUserAppsAdmin(google_apps_domain, user_email):
	"""
		check if current user is google apps admin user
		Return:
				True ... this user is google apps admin
				False ... this user is not google apps admin
		"""
	# user_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, user_email)
	# if user_dict is not None and 'is_apps_admin' in user_dict:
	# 	return user_dict['is_apps_admin']

	# google_app_domain = (user_email.split('@'))[1]
	app_service = fetch_google_app_service(user_email, google_apps_domain)
	try:
		user_entry = app_service.users().get(userKey=user_email).execute()
		if user_entry["isAdmin"] == 'true' or user_entry["isAdmin"] == 'True' or user_entry["isAdmin"]:
			return True
	except Exception as instant:
		return False
	return False

def isUserMemberOfBbsGroup(user_email, google_apps_domain):
	# SSO対応
	if sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(google_apps_domain):
		group_id = sateraito_inc.DOCUMENT_SETTING_GROUP_ID + '@' + google_apps_domain
		return isUserMemberOfBbsGroupSSOGadget(google_apps_domain, user_email, group_id)
	# SSITE対応
	elif sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(google_apps_domain):
		group_id = sateraito_inc.DOCUMENT_SETTING_GROUP_ID + '@' + google_apps_domain
		return isUserMemberOfBbsGroupSSiteGadget(google_apps_domain, user_email, group_id)
	else:
		return _isUserMemberOfBbsGroup(user_email, google_apps_domain)

def getGroupMembersSSOGadget(google_apps_domain, viewer_email, group_id):
	is_group = False
	group_members = []
	ssogadget_app_key = sateraito_db.GoogleAppsDomainEntry.getSSOAppKey(google_apps_domain)
	if ssogadget_app_key != '':
		client = ssoclient.SSOClient(google_apps_domain, ssogadget_app_key, viewer_email)
		access_token = client.getAccessToken()
		if access_token != '':
			groups = client.getGroupListObject(access_token)
			for group in groups:
				if group_id == group['email']:
					groups = groups.extend(group['members'])
					is_group = True

	return is_group, group_members

def isUserMemberOfBbsGroupSSOGadget(google_apps_domain, user_email, group_id):
	is_group, group_members = getGroupMembersSSOGadget(google_apps_domain, user_email, group_id)
	is_member = False
	if user_email in group_members:
		is_member = True
	return is_member

def isUserMemberOfBbsGroupSSiteGadget(google_apps_domain, user_email, group_id):
	is_group, group_members, user_members = getGroupMembersSSiteGadget(google_apps_domain, user_email, group_id)
	is_member = False
	if user_email in group_members or user_email in user_members:
		is_member = True
	return is_member

def _isUserMemberOfBbsGroup(user_email, google_apps_domain):
	"""
check if the user is member of sateraito-bbs-group@example.com
Args:
	user_email .. email to check user
	checker .... checker object
"""
	logging.info('isUserMemberOfBbsGroup user_email=' + str(user_email))

	app_service = fetch_google_app_service(user_email, google_apps_domain)
	#logging.info('app_service:' + str(app_service))
	is_member = False
	try:
		#is_member = groups_service.IsMember(user_email, sateraito_inc.DOCUMENT_SETTING_GROUP_ID)

		member = app_service.members().get(groupKey=sateraito_inc.DOCUMENT_SETTING_GROUP_ID + '@' + google_apps_domain, memberKey=user_email).execute()
		if member is not None:
			is_member = True

	except urlfetch.DownloadError as instance:
		# GData request timeout
		logging.info('instance=' + str(instance))
		logging.warn('Gdata request timeout')
		return
	except Exception as instance:
		is_member = False

	logging.info('is_member=' + str(is_member))
	return is_member

def isWorkflowAdminForApps(user_email, tenant_or_domain, app_id=None, do_not_include_additional_admin=False):
	"""
	check if user is workflow admin user
	Args:
		user_email ... user to check
	Return:
		true ... user_email is GoogleApps admin or member of workflow group
	"""
	logging.info('isWorkflowAdmin user_email=' + str(user_email))

	# step1. check OtherInfo.additional_admin_user_groups
	# if not do_not_include_additional_admin:
	#     if isUserMemberOfAdditionalWorkflowAdmin(user_email, tenant_or_domain):
	#         logging.info('user is a member of ADDITIONAL admin user')
	#         return True

	#
	# below is needed API call: memory cache to reduce api call
	#

	# memcache entry expires in 10 min
	memcache_expire_secs = 60 * sateraito_inc.IS_WORKFLOW_ADMIN_CACHE_MINUTES
	memcache_key = 'script=isworkflowadmin?user_email=' + user_email + '&g=2'
	# check if cached data exists
	cached_data = memcache.get(memcache_key)
	if cached_data is not None:
		logging.info('isWorkflowAdmin: found and respond cached data')
		return strToBool(cached_data)

	# workflow admin(ok to use admin console gadget)
	is_workflow_admin = False

	# check if user is member of sateraito-workflow-group@example.com
	is_user_apps_admin = isUserAppsAdmin(tenant_or_domain, user_email)
	if is_user_apps_admin:
		logging.info('user is apps admin')
		is_workflow_admin = True
	elif isUserMemberOfBbsGroup(user_email, tenant_or_domain):
		logging.info('user is member of workflow group')
		is_workflow_admin = True
	else:
		logging.info('user is not apps admin, not member of workflow group')
		if not do_not_include_additional_admin:
			if ifUserMemberOfAdditionalWorkflowAdmin(user_email, tenant_or_domain, app_id):
				logging.info('user is a member of ADDITIONAL admin user')
				is_workflow_admin = True

	# set to memcache
	if not memcache.set(key=memcache_key, value=boolToStr(is_workflow_admin), time=memcache_expire_secs):
		logging.warning("Memcache set failed.")

	return is_workflow_admin

# new version of isWorkflowAdmin
def isWorkflowAdmin(user_email, tenant_or_domain, app_id=None, do_not_include_additional_admin=False, mode='', domain_dict=None):
	if domain_dict is None:
		domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict2(tenant_or_domain, auto_create=False)

	if sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(tenant_or_domain, domain_dict=domain_dict):
		return isWorkflowAdminForSSite(user_email, tenant_or_domain, app_id=app_id, do_not_include_additional_admin=do_not_include_additional_admin)
	elif sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(tenant_or_domain, domain_dict=domain_dict):
		return isWorkflowAdminForSSOGadget(user_email, tenant_or_domain, app_id=app_id, do_not_include_additional_admin=do_not_include_additional_admin)
	elif mode == MODE_SHAREPOINT:
		return isWorkflowAdminForSharePoint(user_email, tenant_or_domain, app_id=app_id, do_not_include_additional_admin=do_not_include_additional_admin)
	else:
		return isWorkflowAdminForApps(user_email, tenant_or_domain, app_id=app_id, do_not_include_additional_admin=do_not_include_additional_admin)

def ifUserMemberOfAdditionalWorkflowAdmin(user_email, google_apps_domain, app_id):
	""" check if user is a member of ADDITIONAL admin user which is set on admin console Other Settings tab
	"""
	logging.info('ifUserMemberOfAdditionalWorkflowAdmin')
	old_namspace = namespace_manager.get_namespace()
	setNamespace(google_apps_domain, app_id)
	other_setting = sateraito_db.OtherSetting.getInstance(auto_create=True)
	namespace_manager.set_namespace(old_namspace)

	user_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, user_email, auto_create=True)
	if user_dict is None:
		return False
	set1 = set(other_setting.additional_admin_user_groups)
	logging.info('set1=' + str(set1))
	set2 = set(user_dict['google_apps_groups'])
	set2.add(user_email)
	logging.info('set2=' + str(set2))
	if len(set1 & set2) > 0:
		return True
	return False

def setImpersonateEmail(google_apps_domain, impersonate_email ,is_auto_create_impersonate_email, domain_entry=None):

	if domain_entry is None:
		domain_entry = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain)
	domain_entry.impersonate_email = impersonate_email
	domain_entry.is_auto_create_impersonate_email = is_auto_create_impersonate_email
	domain_entry.put()
	q = sateraito_db.GoogleAppsDomainEntry.query()
	for key in q.iter(keys_only=True):
		row = key.get()
		if row is not None:
			if row.google_apps_domain != google_apps_domain:
				row.impersonate_email = impersonate_email
				row.is_auto_create_impersonate_email = is_auto_create_impersonate_email
				row.put()
	return domain_entry

# 指定ドメイン環境にアクセスするための正しい管理者アカウントかを判定
def isValidImpersonateEmail(impersonate_email, google_apps_domain):
	logging.info('isValidImpersonateEmail')
	is_valid_impersonate_email = False
	try:
		app_service = fetch_google_app_service(impersonate_email, google_apps_domain, do_not_use_impersonate_mail=True)
		if impersonate_email.split('@')[1].lower() == google_apps_domain:
			user_entry = app_service.users().get(userKey=impersonate_email).execute()
		else:
			user_entry = app_service.users().get(userKey='dummy@' + google_apps_domain).execute()

		is_valid_impersonate_email = True
	# except AccessTokenRefreshError as e:  # g2対応
	except RefreshError as e:
		logging.info(e)
		if str(e) == 'invalid_grant':
			is_valid_impersonate_email = True
		elif str(e) == 'access_denied':
			logging.warning('Not installed to your domain')
			is_valid_impersonate_email = False
		else:
			logging.warning('Not installed to your domain')
			is_valid_impersonate_email = False
	except HttpError as e:
		if e.resp.status == 404:
			logging.info(e)
			is_valid_impersonate_email = True
		else:
			logging.info('Not installed to your domain')
			logging.info(e)
			is_valid_impersonate_email = False
	logging.info('Result=' + str(is_valid_impersonate_email))
	return is_valid_impersonate_email

# 最終利用月を更新
def updateDomainLastLoginMonth(google_apps_domain):
	old_namespace = namespace_manager.get_namespace()
	namespace_manager.set_namespace(google_apps_domain)
	try:
		q = sateraito_db.GoogleAppsDomainEntry.gql("where google_apps_domain = :1", google_apps_domain)
		domain_entry = q.get()
		if domain_entry is not None:
			return domain_entry.updateLastLoginMonth()
		return False
	finally:
		namespace_manager.set_namespace(old_namespace)

def isMultiDomainSetting(google_apps_domain):
	'''
	check if google_apps_domain is multi domain setting enabled
	'''
	q = sateraito_db.GoogleAppsDomainEntry.all()
	q.filter('google_apps_domain =', google_apps_domain)
	row = q.get()
	if row is None:
		return False
	else:
		if row.multi_domain_setting is None:
			row.multi_domain_setting = False
			row.put()
			return False
		return row.multi_domain_setting

def GetGadgetNames():
	return [
			GADGET_ADMIN_CONSOLE,
			GADGET_USER_CONSOLE,
			]


def encode_multipart_formdata(fields, files, mimetype='image/png'):
	"""
	Args:
		fields: A sequence of (name, value) elements for regular form fields.
		files: A sequence of (name, filename, value) elements for data to be
			uploaded as files.

	Returns:
		A sequence of (content_type, body) ready for urlfetch.
	"""
	logging.info('encode_multipart_formdata mimetype=' + str(mimetype))
	boundary = str('sateraito___boundary-' + randomString() + '___' + dateString())
	crlf = str('\r\n')
	line = []
	for (key, value) in fields:
		line.append(str('--' + boundary))
		line.append(str('Content-Disposition: form-data; name="%s"' % key))
		line.append(str(''))
		line.append(str(value))
	for (key, filename, value) in files:
		line.append(str('--' + boundary))
		line.append(str('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename)))
		line.append(str('Content-Type: %s' % mimetype))
		line.append(str('Content-Transfer-Encoding: binary'))
		line.append(str(''))
		line.append(str(value))
	line.append(str('--%s--' % boundary))
	line.append(str(''))
	body = crlf.join(line)
	content_type = str('multipart/form-data; boundary=%s' % boundary)
	return content_type, body
# todo: edited start: tan@vn.sateraito.co.jp (version: 2)

def exchangeLanguageCode(lang):
	if lang == 'cn':
		return 'zh-cn'
	elif lang == 'in':
		return 'id'
	else:
		return lang

def getActiveLanguage(language, hl=sateraito_inc.DEFAULT_LANGUAGE):
	language = exchangeLanguageCode(language)
	return language if language in ACTIVE_LANGUAGES else hl

def none2ZeroStr(string_param):
	if string_param is None:
		return ''
	if not isinstance(string_param, str):
		return str(string_param)
	return string_param

def getExtJsLocaleFileName(lang):

	lang = lang.lower()

	logging.info('getExtJsLocaleFileName....')
	logging.info('lang=' + lang)

	locale_file = 'ext-lang-en.js'
	if lang == 'de':
		locale_file = 'ext-lang-de.js'
	elif lang == 'en':
		locale_file = 'ext-lang-en.js'
	elif lang == 'en_bg':
		locale_file = 'ext-lang-en_GB.js'
	elif lang == 'es':
		locale_file = 'ext-lang-es.js'
	elif lang == 'fi':
		locale_file = 'ext-lang-fi.js'
	elif lang == 'fr' or lang == 'fr-be' or lang == 'fr-lu' or lang == 'fr-ch':
		locale_file = 'ext-lang-fr.js'
	elif lang == 'fr-ca':
		locale_file = 'ext-lang-fr_CA.js'
	elif lang == 'id':
		locale_file = 'ext-lang-id.js'
	elif lang == 'it':
		locale_file = 'ext-lang-it.js'
	elif lang == 'ja' or lang == 'ja-jp':
		locale_file = 'ext-lang-ja.js'
	elif lang == 'ko' or lang == 'ko_kr':
		locale_file = 'ext-lang-ko.js'
	elif lang == 'lt':
		locale_file = 'ext-lang-lt.js'
	elif lang == 'pt':
		locale_file = 'ext-lang-pt.js'
	elif lang == 'pt-br':
		locale_file = 'ext-lang-pt_BR.js'
	elif lang == 'ru':
		locale_file = 'ext-lang-ru.js'
	elif lang == 'sv' or lang == 'sv_se':
		locale_file = 'ext-lang-sv_SE.js'
	elif lang == 'th':
		locale_file = 'ext-lang-th.js'
	elif lang == 'tr':
		locale_file = 'ext-lang-tr.js'
	elif lang == 'vi':
		locale_file = 'ext-lang-vn.js'
	elif lang == 'cn' or lang == 'zh-cn':
		locale_file = 'ext-lang-zh_CN.js'
	elif lang == 'zh-tw':
		locale_file = 'ext-lang-zh_TW.js'

	logging.info('locale_file=' + locale_file)

	return locale_file

def getLangFileName(lang):

	lang = lang.lower()
	logging.info('getLangFileName....')

	#lang_file = 'ALL_ALL.xml'
	lang_file = 'ALL_ALL.xml'
	if lang == 'cs':
		lang_file = 'cs_ALL.xml'
	elif lang == 'da':
		lang_file = 'da_ALL.xml'
	elif lang == 'de':
		lang_file = 'de_ALL.xml'
	elif lang == 'es':
		lang_file = 'es_ALL.xml'
	elif lang == 'en':
		lang_file = 'en_ALL.xml'
	elif lang == 'fr':
		lang_file = 'fr_ALL.xml'
	elif lang == 'hi':
		lang_file = 'hi_ALL.xml'
	elif lang == 'id':
		lang_file = 'id_ALL.xml'
	elif lang == 'it':
		lang_file = 'it_ALL.xml'
	elif lang == 'ja':
		lang_file = 'ja_ALL.xml'
	elif lang == 'km':
		lang_file = 'km_ALL.xml'
	elif lang == 'ko':
		lang_file = 'ko_ALL.xml'
	elif lang == 'lo':
		lang_file = 'lo_ALL.xml'
	elif lang == 'mn':
		lang_file = 'mn_ALL.xml'
	elif lang == 'ms':
		lang_file = 'ms_ALL.xml'
	elif lang == 'pl':
		lang_file = 'pl_ALL.xml'
	elif lang == 'pt':
		lang_file = 'pt_ALL.xml'
	elif lang == 'ru':
		lang_file = 'ru_ALL.xml'
	elif lang == 'sv':
		lang_file = 'sv_ALL.xml'
	elif lang == 'th':
		lang_file = 'th_ALL.xml'
	elif lang == 'tl':
		lang_file = 'tl_ALL.xml'
	elif lang == 'tr':
		lang_file = 'tr_ALL.xml'
	elif lang == 'vi':
		lang_file = 'vi_ALL.xml'
	elif lang == 'zh-cn':
		lang_file = 'zh_CN_ALL.xml'
	elif lang == 'zh-tw':
		lang_file = 'zh_TW_ALL.xml'

	logging.info('lang_file=' + lang_file)

	return lang_file

def getUserLanguage(viewer_email, user_info=None, hl=sateraito_inc.DEFAULT_LANGUAGE):
	logging.info('hl default =' + str(hl))
	if hl is None or hl == '':
		hl = sateraito_inc.DEFAULT_LANGUAGE
	if viewer_email == '' or viewer_email is None:
		return getActiveLanguage('', hl=hl)
	if user_info is None:
		user_info = sateraito_db.UserInfo.getInstance(viewer_email)
		logging.info('user_info:' + str(user_info))
	if user_info is None or user_info.language is None:
		return getActiveLanguage('', hl=hl)
	return getActiveLanguage(user_info.language, hl=hl)

def get_calendar_service(viewer_email, google_apps_domain, num_retry=0, do_not_retry=False):
	try:
		calendar_service = _get_calendar_service(viewer_email, google_apps_domain)
		return calendar_service
	# except AccessTokenRefreshError as e:  # g2対応
	except RefreshError as e:
		logging.warn('class name:' + e.__class__.__name__ + ' message=' + str(e) + ' num_retry=' + str(num_retry))
		raise e
	except BaseException as e:
		if do_not_retry:
			raise e
		logging.warn('class name:' + e.__class__.__name__ + ' message=' + str(e) + ' num_retry=' + str(num_retry))
		if num_retry > 3:
			raise e
		else:
			sleep_time = timeToSleep(num_retry)
			logging.info('sleeping ' + str(sleep_time))
			time.sleep(sleep_time)
			return get_calendar_service(viewer_email, google_apps_domain, (num_retry + 1), do_not_retry=do_not_retry)

def _get_calendar_service(viewer_email, google_apps_domain):
	# Calendar API can be used by only Google Apps Admin user
	#	http = get_authorized_http(viewer_email, google_apps_domain, is_sub=True)
	credentials = get_authorized_http(viewer_email, google_apps_domain, scope=sateraito_inc.OAUTH2_SCOPES_CALENDAR)
	# build Calendar service
	return build('calendar', 'v3', credentials=credentials)

def _get_drive_service(viewer_email, google_apps_domain):
	# Drive API can be used by only Google Apps Admin user
	credentials = get_authorized_http(viewer_email, google_apps_domain, scope=sateraito_inc.OAUTH2_SCOPES_DRIVE)
	# build Drive service
	return build('drive', 'v2', credentials=credentials)

def convertListToDictExport(doc_values, key):
	result = []
	values = doc_values[key]
	if (key + '__display_value') in doc_values:
		display_values = doc_values[key + '__display_value']
		value = []
		if isinstance(doc_values[key + '__display_value'], list):
			for i in range(len(values)):
				value.append({'display_value': display_values[i], 'value': values[i]})
		else:
			for i in range(len(values)):
				value.append({'display_value': values[i], 'value': values[i]})
		result = value
	else:
		result = doc_values[key]

	return result

def getLanguageUsing(user_language, viewer_email, google_apps_domain):
	if user_language is None or user_language == '':
		settings_entry = None
		try:
			calender_service = get_calendar_service(viewer_email, google_apps_domain)
			settings_entry = calender_service.settings().get(setting='locale').execute()
			logging.info(settings_entry)
		# except AccessTokenRefreshError as e:  # g2対応
		except RefreshError as e:
			# スコープが許可されていない（access_denied）、無効なユーザー（invalid_grant）、カレンダーサービスがOFF（access_denied）
			logging.warning('class name:' + e.__class__.__name__ + ' message=' + str(e))
		except HttpError as e:
			# カレンダーサービスがOFF（Invalid Credentials）
			if e.resp.status == 401:
				logging.warning('class name:' + e.__class__.__name__ + ' message=' + str(e))
			else:
				logging.error('class name:' + e.__class__.__name__ + ' message=' + str(e))

		# 言語切替対応
		# my_lang = MyLang(sateraito_inc.DEFAULT_LANGUAGE)
		user_language = getUserLanguage(viewer_email, hl=settings_entry.get('value', '') if settings_entry is not None else '')

	return user_language


def createShortURL(url):
	shorten_url = ''
	try:
		if url != '':
			# URL Shortener APIからFireBase Dynamic Link への切り替え
			# post_data = {}
			# post_data['longUrl'] = url
			post_data = {
				'dynamicLinkInfo': {
					'domainUriPrefix': 'https://' + sateraito_inc.APP_CODE_FOR_FIREBASE + '.page.link',
					'link': url
				},
				'suffix': {
					'option': 'SHORT'
				}
			}

			logging.debug(post_data)
			payload = json.JSONEncoder().encode(post_data)
			headers = {'Content-Type': 'application/json'}
			result = None
			retry_cnt = 0
			while True:
				try:
					# URL Shortener APIからFireBase Dynamic Link への切り替え
					# result = urlfetch.fetch(url='https://www.googleapis.com/urlshortener/v1/url?key=' + sateraito_inc.API_KEY, payload=payload, headers=headers, method=urlfetch.POST, deadline=10, follow_redirects=True)
					result = urlfetch.fetch(
						url='https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=' + sateraito_inc.API_KEY_FOR_FIREBASE,
						payload=payload, headers=headers, method=urlfetch.POST, deadline=10, follow_redirects=True)
					break
				except Exception as e:
					if retry_cnt < 3:
						logging.warning('retry' + '(' + str(retry_cnt) + ')... ' + str(e))
						retry_cnt += 1
					else:
						raise e
			if result.status_code != 200:
				raise Exception(result.content)
			result_json = {}
			result_json = json.JSONDecoder().decode(result.content)
			# URL Shortener APIからFireBase Dynamic Link への切り替え
			# shorten_url = result_json.get('id', '')
			shorten_url = result_json.get('shortLink', '')
	except BaseException as e:
		logging.warning(e)
		shorten_url = url

	return shorten_url

def isDomainDisabled(google_apps_domain, target_google_apps_domain=None):
	# row = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain, cache_ok=True)
	row = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain, target_google_apps_domain)
	if row is None:
		return True

	# SSITE、SSOGadget対応：oem_company_codeによってチェック制御 2017.01.30
	#	if row.oem_company_code is None or (row.oem_company_code in oem_func.getBlackListTargetOEMCompanyCodes()):
	if row.oem_company_code is None or (row.oem_company_code in oem_func.getBlackListTargetOEMCompanyCodes()):
		if google_apps_domain in sateraito_black_list.DOMAINS_TO_DISABLE:
			return True

	# SSITE、SSOGadget対応：oem_company_codeによってチェック制御 2017.01.30
	# G Suite版以外は解約者リストを見ない対応 2017.08.28
	# if row.oem_company_code is None or (row.oem_company_code in oem_func.getBlackListTargetOEMCompanyCodes()):

	# # TODO GWS版契約管理対応…最終的には解約リストチェックは行わないように対応予定（タイミングを見てここをコメントアウト）
	# if (row.oem_company_code is None or (row.oem_company_code in oem_func.getBlackListTargetOEMCompanyCodes())) and (
	# 	row.sp_code is None or (row.sp_code in oem_func.getBlackListTargetSPCodes())):
	# 	if google_apps_domain in sateraito_black_list.DOMAINS_TO_DISABLE:
	# 		return True

	is_need_update = False
	if row.is_disable is None:
		row.is_disable = False
		is_need_update = True
	if row.available_start_date is None:
		row.available_start_date = ''
		is_need_update = True
	if row.charge_start_date is None:
		row.charge_start_date = ''
		is_need_update = True
	if row.cancel_date is None:
		row.cancel_date = ''
		is_need_update = True
	if row.is_backup_available is None:
		row.is_backup_available = False
		is_need_update = True
	if is_need_update:
		row.put()

	# is_disable フラグもチェックするように変更 2018.07.06
	if row.is_disable == True:
		return True

	# TODO GWS版契約管理対応…切り替えまではサテライト直契約テナントは解約日チェックを行わないようにここでreturnする。解約日がだんだんと連携されてくるようになるため（タイミングを見てここもコメントアウト）
	# if (sateraito_inc.appspot_domain != 'kddi-crm' or row.is_no_oem) and (
	# 	row.oem_company_code is None or (row.oem_company_code in oem_func.getBlackListTargetOEMCompanyCodes())) and (
	# 	row.sp_code is None or (row.sp_code in oem_func.getBlackListTargetSPCodes())):
	# 	return False

	# 解約日をチェックするように対応 2013/11/13
	if row.cancel_date != '':
		now = UcfUtil.getNow()  # 標準時  g2対応：UTCのawareである事に注意
		cancel_date = UcfUtil.add_days(UcfUtil.getDateTime(row.cancel_date), 1)  # 解約日は利用可とするため1日たしておく
		# return now >= cancel_date
		return isBiggerDate(now, cancel_date)

	return False

# SameSite対応…SameSite=NoneをつけるかどうかをU/Aで判断
# ext-chrome-grid-hack.jsのisSameSiteCookieSupportedBrowserと合わせること
def isSameSiteCookieSupportedUA(strAgent):
	# logging.debug('isSameSiteCookieSupportedUA strAgent=' + str(strAgent))
	# if sateraito_inc.developer_mode:
	# 	return False
	
	# エクセルビルダーを開いた場合に strAgent=AppEngine-Google; (+http://code.google.com/appengine) のような値が入る
	# デフォルトをTrueにしてiOS12の場合だけFalseになるよう変更 2023-06-22
	# is_supported = False
	is_supported = True

	if strAgent is not None:
		strAgent = strAgent.lower()

		# iOS12の場合はセットしない
		if strAgent.find('AppleWebKit'.lower())>=0 and (strAgent.find('iPhone'.lower()) >= 0 or strAgent.find('iPad'.lower()) >= 0) and strAgent.find('OS 12_'.lower()) >= 0:
			is_supported = False

		# まずはスモールスタートで Chromeのみセットしてみる
		# セキュリティブラウザ、Teamsアプリを除外 2019.12.12
		#elif (strAgent.find('Chrome'.lower())>=0 or strAgent.find('CriOS'.lower())>=0) and strAgent.find('Edge'.lower())<0 and strAgent.find('Edg/'.lower())<0:
		# Chromeの旧バージョンをざっくり除外（Ver 63などでSameSite=NoneがついているとNGなことが分かったので） 2019.12.13 
		#elif (strAgent.find('Chrome'.lower())>=0 or strAgent.find('CriOS'.lower())>=0) and strAgent.find('Edge'.lower())<0 and strAgent.find('Edg/'.lower())<0 and strAgent.find('/SateraitoSecurityBrowser'.lower())<0 and strAgent.find('Teams/'.lower())<0:
		# Edgeブラウザも対象に追加 2020.09.18
		#elif (strAgent.find('Chrome'.lower())>=0 or strAgent.find('CriOS'.lower())>=0) and strAgent.find('Edge'.lower())<0 and strAgent.find('Edg/'.lower())<0 and strAgent.find('/SateraitoSecurityBrowser'.lower())<0 and strAgent.find('Teams/'.lower())<0 and (strAgent.find('Chrome/6'.lower())<0 and strAgent.find('Chrome/5'.lower())<0):
		# セキュリティブラウザの判定を除外 2021.02.10
		#elif (strAgent.find('Chrome'.lower())>=0 or strAgent.find('CriOS'.lower())>=0) and strAgent.find('/SateraitoSecurityBrowser'.lower())<0 and strAgent.find('Teams/'.lower())<0 and (strAgent.find('Chrome/6'.lower())<0 and strAgent.find('Chrome/5'.lower())<0):
		elif (strAgent.find('Chrome'.lower())>=0 or strAgent.find('CriOS'.lower())>=0) and strAgent.find('Teams/'.lower())<0 and (strAgent.find('Chrome/6'.lower())<0 and strAgent.find('Chrome/5'.lower())<0):
			is_supported = True
		elif (strAgent.find('firefox') >= 0):  # Firefox を追加
			is_supported = True

		## MacのSafariで有効にしてみる 2020.01.10
		## Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Safari/605.1.15
		#elif strAgent.find('Macintosh;'.lower())>=0 and strAgent.find('Safari/'.lower())>=0 and strAgent.find('Chrome'.lower())<0:
		#	is_supported = True

	logging.info('isSameSiteCookieSupportedUA=%s' % (is_supported))
	return is_supported

# 静的コンテンツキャッシュ障害対応・・・Staticコンテンツ用のMySiteURLを返す 2020.09.15
def getMySiteURLForStaticContents(tenant, request_url, nocheck_request_url=False):
	# 障害復旧に伴い本機能はコメントアウト 2020.09.23
	#tenant_entry = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant, cache_ok=True)
	#if not sateraito_inc.developer_mode and tenant_entry is not None and tenant_entry.use_appspot_fullpath_url_for_css_include:
	#	return 'https://' + sateraito_inc.appspot_domain + '.appspot.com'
	return getMySiteURL(tenant, request_url, nocheck_request_url=nocheck_request_url)

# MySiteURLを取得
def getMySiteURL(tenant_or_domain, request_url, nocheck_request_url=False, domain_dict=None, ssl=True):
	is_custom_domain = False

	# URLから判断できる場合はそうする（検索負荷もないしキャッシュのタイムラグもないため）
	is_judge_ok = False
	if not nocheck_request_url and request_url is not None:
		sp1 = request_url.split('?')
		sp = sp1[0].split('/')
		if len(sp) >= 3:
			request_fqdn = sp[2]
			if request_fqdn.lower() == sateraito_inc.custom_domain_site_fqdn.lower():
				is_custom_domain = True
				is_judge_ok = True
			elif request_fqdn.lower() == sateraito_inc.site_fqdn.lower():
				is_custom_domain = False
				is_judge_ok = True

	# URLから判断できない場合はDB参照（自動承認のバッチ処理など）
	# ～URLから判別できないパターン～
	# ・cron実行（frontends、backendsともに）
	# ・taskqueue（frontends以外）
	if not is_judge_ok:
		is_custom_domain = isCustomDomainMode(tenant_or_domain)
		is_judge_ok = True

	my_site_url = ''
	# カスタムドメインモードかを判別
	if is_custom_domain:
		if ssl:
			my_site_url = sateraito_inc.custom_domain_my_site_url
		else:
			my_site_url = sateraito_inc.custom_domain_my_site_no_ssl_url
	else:
		if ssl:
			my_site_url = sateraito_inc.my_site_url
		else:
			my_site_url = sateraito_inc.my_site_no_ssl_url

	return my_site_url


# カスタムドメインモードかを判別
def isCustomDomainMode(tenant_or_domain, is_with_cache=True):
	is_custom_domain_mode = False
	row = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)
	if row is None:
		is_custom_domain_mode = False
	else:
		# SSITE対応：サテライトサイトの場合はカスタムドメイン
		# is_custom_domain_mode = row.is_custom_domain_mode
		is_custom_domain_mode = row.is_ssite_tenant

	logging.info('is_custom_domain_mode=' + str(is_custom_domain_mode))
	return is_custom_domain_mode

# SameSite対応の一環…高速化を標準とする対応…ReportsAPIサービス
def get_admin_report_service(viewer_email, google_apps_domain, num_retry=0, do_not_retry=False):
	try:
		admin_report_service = _get_admin_report_service(viewer_email, google_apps_domain)
		return admin_report_service
	# except AccessTokenRefreshError as e:  # g2対応
	except RefreshError as e:
		logging.warning('class name:' + e.__class__.__name__ + ' message=' + str(e) + ' num_retry=' + str(num_retry))
		raise e
	except BaseException as e:
		if do_not_retry:
			logging.warning('class name:' + e.__class__.__name__ + ' message=' + str(e) + ' num_retry=' + str(num_retry))
			raise e
		if num_retry > 3:
			raise e
		else:
			sleep_time = timeToSleep(num_retry)
			logging.debug('sleeping ' + str(sleep_time))
			time.sleep(sleep_time)
	return get_admin_report_service(viewer_email, google_apps_domain, (num_retry + 1), do_not_retry=do_not_retry)

def _get_admin_report_service(viewer_email, google_apps_domain):
	# http, access_token = get_authorized_http(viewer_email, google_apps_domain, sateraito_inc.OAUTH2_SCOPES_ADMIN_REPORT)
	credentials = get_authorized_http(viewer_email, google_apps_domain, sateraito_inc.OAUTH2_SCOPES_ADMIN_REPORT)
	return build('admin', 'reports_v1', credentials=credentials)

def checkTimeLastLogin(google_apps_domain):
	row = sateraito_db.GoogleAppsDomainEntry.getDict2(google_apps_domain)
	if row is None:
		return False
	else:
		if 'last_login_month' in row and row['last_login_month']:
			last_month_login = datetime.datetime.strptime(row['last_login_month'], '%Y-%m')
		else:
			return True

	current_time = datetime.datetime.now()
	rdelta = relativedelta.relativedelta(current_time, last_month_login)
	if rdelta.years >= 1 or rdelta.months > 3:
		return False

	return True

# todo: edited start: phuc@vnd.sateraito.co.jp

def getBackEndsModuleNameDeveloper(module_name):
	module_name = 'default'

	if sateraito_inc.developer_version:
		return sateraito_inc.developer_version + '.' + module_name

	return module_name

# sateraito new ui 2020-05-07
def getScriptVirtualUrl(new_ui=False):
	# if new_ui:
	# 	return '/build/js/' if not sateraito_inc.debug_mode else '/build/js/debug/'
	return '/js/' if not sateraito_inc.debug_mode else '/js/debug/'

def getHtmlBuilderScriptVirtualUrl(new_ui=False):
	# if new_ui:
	# 	return '/build/htmlbuilder/js/' if not sateraito_inc.debug_mode else '/build/htmlbuilder/js/debug/'
	return '/htmlbuilder/js/' if not sateraito_inc.debug_mode else '/htmlbuilder/js/debug/'

def convertTemplateFileName(template_filename, new_ui=False):
	# if new_ui:
	# 	return 'new_ui/' + template_filename
	return template_filename

def getNewUISetting(self, tenant_or_domain, domain_dict=None):
	# sateraito new ui 2020-05-07
	if domain_dict is None:
		domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(tenant_or_domain)

	new_ui = False
	# if domain_dict:
	# 	new_ui = noneToFalse(domain_dict.get('new_ui'))
	# if self.request.get('new_ui', False):
	# 	new_ui = strToBool(self.request.get('new_ui'))

	new_ui_afu = noneToFalse(domain_dict.get('new_ui_afu'))

	new_ui_config = {
		'active': 'material',
		'themes': {
			'material': {
				'font-size': 13,
				'size': 'large',  # small, medium, large
				'skin': 'blue',  # light, green, orange, red, blue-tiki, blue-sencha
			}
		}
	}
	new_ui_config_raw = domain_dict.get('new_ui_config')

	try:
		if new_ui_afu and self.viewer_email:
			row_d = sateraito_db.GoogleAppsUserEntry.getDict(tenant_or_domain, self.viewer_email)
			new_ui_user_conf = row_d.get('new_ui') if row_d.get('new_ui') is not None else False
			if new_ui_user_conf:
				new_ui_config_raw = row_d.get('new_ui_config')
	except BaseException as e:
		pass

	if new_ui_config_raw:
		new_ui_config_raw = json.JSONDecoder().decode(new_ui_config_raw)
		new_ui_config.update(new_ui_config_raw)

	return new_ui, json.JSONEncoder().encode(new_ui_config), new_ui_afu

# ネームスペースとして正しい文字列化を判定…申込簡単化対応 2018.02.05
def isValidNamespace(namespace_name):
	if namespace_name is None or namespace_name == '':
		return False
	regexp = re.compile('^[0-9A-Za-z._-]{0,100}$')
	if regexp.search(namespace_name) is None:
		# namespace_name have prohibited character
		return False
	return True

# SSOのFQDNを取得…申込簡単化対応 2018.02.05
def getSSOFQDN(sso_for_authorize):
	sso_fqdn = ''
	if sso_for_authorize in ['WORKSMOBILE', 'WORKPLACE']:
		sso_fqdn = 'sso.sateraito.jp'
	elif sso_for_authorize == 'APPS_PAID':
		if sateraito_inc.debug_mode:
			sso_fqdn = 'sateraito-dev2.appspot.com'
		else:
			sso_fqdn = 'sateraito-apps-sso.appspot.com'
	elif sso_for_authorize == 'APPS_FREE':
		sso_fqdn = 'sateraito-apps-sso3.appspot.com'
	elif sso_for_authorize == 'APPS_KDDI':
		sso_fqdn = 'kddi-sso.appspot.com'
	return sso_fqdn

# SSOGadget対応
def createSSOIdProviderInfo(contract_entry):
	# LINE WORKS直接認証対応…LINE WORKSとのSAMLかサテライトSSOとのSAMLかによって分岐 2019.06.13
	if contract_entry.worksmobile_saml_issuer is not None and contract_entry.worksmobile_saml_issuer != '':
		sso_entity_id = contract_entry.worksmobile_saml_issuer
		sso_login_endpoint = contract_entry.worksmobile_saml_url
		return sso_entity_id, sso_login_endpoint
	else:
		sso_fqdn = getSSOFQDN(contract_entry.sso_for_authorize)
		# LINE WORKS直接認証対応…変数化 2019.06.13
		# sso_entity_id = 'https://sateraito-sso/IDP'
		sso_entity_id = SSO_ENTITY_ID
		sso_login_endpoint = 'https://' + sso_fqdn + '/a/' + contract_entry.sso_tenant + '/sso/login'
		return sso_entity_id, sso_login_endpoint

# SSOGadget対応：SAML連携設定を取得
def getSamlSettings(my_site_url, tenant_or_domain, idp_entity_id, idp_login_endpoint, sso_public_key):
	sp_data = {
		# LINE WORKS直接認証対応…変数化 2019.06.13
		# 'entityId': 'workflow.sateraito.jp',
		'entityId': SP_ENTITY_ID,
		'assertionConsumerService': {
			'url': my_site_url + '/' + tenant_or_domain + '/saml/acs'
		},
		'singleLogoutService': {
			'url': ''
		},
		'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified'
	}
	idp_data = {
		'entityId': idp_entity_id,
		'singleSignOnService': {
			'url': idp_login_endpoint
		},
		'singleLogoutService': {
			'url': ''      # ※今のところログアウト連携はなし
		},
		'x509cert': sso_public_key
	}

	security = {
		'authnRequestsSigned': False,
		'wantAssertionsSigned': False,
		'signMetadata': False
	}

	samlsettings = {
		'strict': False,
		'sp_data': sp_data,
		'idp_data': idp_data,
		'security': sp_data,
		}
	return samlsettings

# ドメインエントリの登録、更新
# Google Workspace 版申込ページ対応 2017.06.05
def registDomainEntry(tenant_or_domain, target_tenant_or_domain, requestor, contract_entry=None, is_set_dates=False, not_use_memcache=False, not_send_setup_mail=False):
	domain_entry = None
	if requestor != '':
		#target_google_apps_domain = requestor.split('@')[1].lower()

#		token = memcache.get('regist_domain_entry?google_apps_domain=' + target_tenant_or_domain)
		token = memcache.get('regist_domain_entry?google_apps_domain=' + tenant_or_domain + '&target_google_apps_domain=' + target_tenant_or_domain)
		if not_use_memcache or token is None:
			# token作成
			token = UcfUtil.guid()

			# タスクに追加した時点で処理1日はタスク登録が走らないようにmemcache更新…valueはトークン（チェックに使用）
			# tokenチェックが間に合わない可能性があるので、addより前にセット
#			memcache.set(key='regist_domain_entry?google_apps_domain=' + target_tenant_or_domain, value=token, time=(1440 * 60))
			memcache.set(key='regist_domain_entry?google_apps_domain=' + tenant_or_domain + '&target_google_apps_domain=' + target_tenant_or_domain + '&g=2', value=token, time=(1440 * 60))

			# 該当のレコードがない場合は、即時作成したほうがよさそうなのでここで作成（その後はタスク）
			domain_entry = insertDomainEntry(tenant_or_domain, target_tenant_or_domain, contract_entry=contract_entry, is_set_dates=is_set_dates, not_send_setup_mail=not_send_setup_mail)
			# Save Number of GoogleApps domain user
			params = {
				'requestor': requestor
				, 'target_tenant_or_domain': target_tenant_or_domain
				, 'token': token
				, 'type': 'start'
			}
			# taskに追加 まるごと
			import_q = taskqueue.Queue('domain-set-queue')
			# import_q = taskqueue.Queue('domain-set-queue')
			import_t = taskqueue.Task(
				url='/' + tenant_or_domain + '/tq/registdomainentry',
				params=params,
				target=getBackEndsModuleNameDeveloper('commonprocess'),
				countdown='5'
			)
			#logging.info('run task')
			import_q.add(import_t)
	return domain_entry

# DomainEntryに1件登録（存在しない場合だけ.以降はタスクで処理）
def insertDomainEntry(google_apps_domain, target_google_apps_domain, contract_entry=None, is_set_dates=False, not_send_setup_mail=False):
	logging.debug('insertDomainEntry start...')
	google_apps_domain = google_apps_domain.lower()
	old_namespace = namespace_manager.get_namespace()
	setNamespace(google_apps_domain, '')

	# プライマリドメインのネームスペースにセカンダリドメインレコードを登録するように修正 2017.11.09
	# q =	sateraito_db.GoogleAppsDomainEntry.gql("where google_apps_domain = :1", google_apps_domain)
	q = sateraito_db.GoogleAppsDomainEntry.gql("where google_apps_domain = :1", target_google_apps_domain)
	new_domain_entry = q.get()
	if new_domain_entry is None:
		new_domain_entry = sateraito_db.GoogleAppsDomainEntry()
		# プライマリドメインのネームスペースにセカンダリドメインレコードを登録するように修正 2017.11.09
		# new_domain_entry.google_apps_domain = google_apps_domain
		new_domain_entry.google_apps_domain = target_google_apps_domain
		new_domain_entry.num_users = 0
		new_domain_entry.hide_ad = False
		new_domain_entry.multi_domain_setting = False
		if sateraito_inc.IS_FREE_EDITION:
			new_domain_entry.available_users = sateraito_inc.DEFAULT_AVAILABLE_USERS
		new_domain_entry.impersonate_email = ''
		new_domain_entry.is_oauth2_domain = False
		new_domain_entry.use_iframe_version_gadget = True  # 新規インストールドメインはiFrame版 2016.03.27
		new_domain_entry.no_auto_logout = True  # True for new domain		# 新規環境では高速化オプションを有効にセット 2016.08.25

		# SSITE、SSOGadget対応：代理店や元サービス情報をセット 2017.01.30
		if contract_entry is not None:
			new_domain_entry.sp_code = contract_entry.sp_code
			new_domain_entry.oem_company_code = contract_entry.oem_company_code

		# SSITE、SSOGadget対応：30日利用制限をかける対応 2017.01.25
		if is_set_dates:
			dt_now = datetime.datetime.now()
			dt_expire = UcfUtil.add_days(dt_now, 30)  # 当日を入れて31日（厳密でなくてもよいとは思うが...）
			new_domain_entry.available_start_date = dt_now.strftime('%Y/%m/%d')
			new_domain_entry.charge_start_date = dt_expire.strftime('%Y/%m/%d')
			new_domain_entry.cancel_date = dt_expire.strftime('%Y/%m/%d')
		new_domain_entry.put()

		## SSITE、SSOGadget対応：営業メンバーに通知メール送信…ついでにApps版でも送信してみる 2017.01.25
		# サンキューメールとセットアップ通知の統合対応…申込ページ経由ではない場合（直接Marketplaceからインストール＆有償版）はこれまで通りここでセットアップ通知を送る 2017.09.15
		# sendInstallNotificationMailToSalesMembers(new_domain_entry, contract_entry)
		if not not_send_setup_mail:
			sendThankyouMailAndSetupNotificationMail(new_domain_entry, contract_entry, None, is_send_thankyou_mail=False, is_send_setup_mail=True)

	namespace_manager.set_namespace(old_namespace)
	return new_domain_entry

# SSITE、SSOGadget対応：営業メンバーに通知メール送信 2017.01.25
def sendThankyouMailAndSetupNotificationMail(domain_entry, contract_entry, my_lang, is_send_thankyou_mail=False, is_send_setup_mail=False):
	logging.info('sendThankyouMailAndSetupNotificationMail start...')

	sp_name = ''
	if contract_entry is not None:
		if contract_entry.sp_code == oem_func.SP_CODE_WORKSMOBILE:
			sp_name = u'LINE WORKS 版'
		# Workplace対応 2017.09.13
		elif contract_entry.sp_code == oem_func.SP_CODE_WORKPLACE:
			sp_name = u'Workplace by Facebook 版'
		elif contract_entry.sp_code == oem_func.SP_CODE_SSITE:
			sp_name = u'サテライトポータルサイト版'
		# Google Workspace 版申込ページ対応 2017.06.05
		elif contract_entry.sp_code == oem_func.SP_CODE_GSUITE:
			if sateraito_inc.appspot_domain == 'sateraito-electronic-storage':
				sp_name = u'Google Workspace 有償版'
			elif sateraito_inc.appspot_domain == 'sateraito-electronic-storage2':
				sp_name = u'Google Workspace 無償版'
			elif sateraito_inc.appspot_domain == 'kddi-electronic-storage':
				sp_name = u'Google Workspace KDDI版'
			elif sateraito_inc.appspot_domain == 'test-sateraito-todo':
				sp_name = u'Google Workspace 開発版'
	else:
		sp_name = u''
		if sateraito_inc.appspot_domain == 'sateraito-electronic-storage':
			sp_name += u'Google Workspace 有償版'
		elif sateraito_inc.appspot_domain == 'sateraito-electronic-storage2':
			sp_name += u'Google Workspace 無償版'
		elif sateraito_inc.appspot_domain == 'kddi-electronic-storage':
			sp_name += u'Google Workspace KDDI版'

	subject = u'[セットアップ通知]サテライトオフィス・電子帳簿保存法ファイルサーバー機能（%s）：%s' % (sp_name, domain_entry.google_apps_domain)
	body = u''
	body += u'サービス名：サテライトオフィス・電子帳簿保存法ファイルサーバー機能（%s）\n' % (sp_name)
	if contract_entry is not None:
		body += u'代理店：%s\n' % (noneToZeroStr(contract_entry.oem_company_code) if contract_entry is not None else '')
	body += u'ドメイン：%s\n' % (domain_entry.google_apps_domain)
	body += u'インストール日時：%s\n' % (toShortLocalTime(datetime.datetime.now(), timezone=sateraito_inc.DEFAULT_TIMEZONE))
	body += u'利用開始日：%s\n' % (domain_entry.available_start_date if domain_entry.available_start_date is not None else '')
	body += u'課金開始日：%s\n' % (domain_entry.charge_start_date if domain_entry.charge_start_date is not None else '')
	body += u'解約日：%s\n' % (domain_entry.cancel_date if domain_entry.cancel_date is not None else '')

	if contract_entry is not None and contract_entry.sp_code == oem_func.SP_CODE_WORKSMOBILE:
		body += u'\n'
		body += u'～LINE WORKS の情報～\n'
		# LINE WORKS直接認証対応…ついでに変更 2019.06.13
		#body += u'ドメイン：%s\n' % (noneToZeroStr(contract_entry.worksmobile_domain) if contract_entry is not None else '')
		body += u'ドメイン/グループ名：%s\n' % (noneToZeroStr(contract_entry.worksmobile_domain) if contract_entry is not None else '')
		# LINE WORKS直接認証対応…SSO認証ではなくなったのでコメントアウト 2019.06.13
		# sso_name = ''
		# # 申込簡単化対応（ついでに...）
		# if contract_entry.sso_for_authorize == 'WORKSMOBILE':
		# 	#sso_name = u'専用版SSO'
		# 	sso_name = u'LINE WORKS版SSO'
		# elif contract_entry.sso_for_authorize == 'WORKPLACE':
		# 	sso_name = u'Workplace版SSO'
		# elif contract_entry.sso_for_authorize == 'APPS_PAID':
		# 	sso_name = u'Google Workspace 有償版SSO'
		# elif contract_entry.sso_for_authorize == 'APPS_FREE':
		# 	sso_name = u'Google Workspace 無償版SSO'
		# elif contract_entry.sso_for_authorize == 'APPS_KDDI':
		# 	sso_name = u'Google Workspace KDDI版SSO'
		# body += u'SSOの種類：%s\n' % (noneToZeroStr(sso_name) if contract_entry is not None else '')
		# body += u'SSOテナント：%s\n' % (noneToZeroStr(contract_entry.sso_tenant) if contract_entry is not None else '')
	# Workplace対応 2017.09.13
	elif contract_entry is not None and contract_entry.sp_code == oem_func.SP_CODE_WORKPLACE:
		body += u'\n'
		body += u'～Workplace by Facebook の情報～\n'

		body += u'ドメイン：%s\n' % (noneToZeroStr(contract_entry.workplace_domain) if contract_entry is not None else '')
		sso_name = ''
		if contract_entry.sso_for_authorize == 'WORKPLACE':
			sso_name = u'専用版SSO'
		elif contract_entry.sso_for_authorize == 'APPS_PAID':
			sso_name = u'Google Workspace 有償版SSO'
		elif contract_entry.sso_for_authorize == 'APPS_FREE':
			sso_name = u'Google Workspace 無償版SSO'
		elif contract_entry.sso_for_authorize == 'APPS_KDDI':
			sso_name = u'Google Workspace KDDI版SSO'
		body += u'SSOの種類：%s\n' % (noneToZeroStr(sso_name) if contract_entry is not None else '')
		body += u'SSOテナント：%s\n' % (noneToZeroStr(contract_entry.sso_tenant) if contract_entry is not None else '')
	elif contract_entry is not None and contract_entry.sp_code == oem_func.SP_CODE_SSITE:
		body += u'\n'
		body += u'～サテライトポータルサイトの情報～\n'
		body += u'テナント：%s\n' % (noneToZeroStr(contract_entry.ssite_tenant) if contract_entry is not None else '')

	body += u'\n'
	body += u'～その他の情報～\n'
	body += u'会社名：%s\n' % (noneToZeroStr(contract_entry.company_name) if contract_entry is not None else '')
	body += u'担当者名：%s\n' % (noneToZeroStr(contract_entry.tanto_name) if contract_entry is not None else '')
	body += u'担当者アドレス：%s\n' % (noneToZeroStr(contract_entry.contact_mail_address) if contract_entry is not None else '')
	body += u'担当者電話番号：%s\n' % (noneToZeroStr(contract_entry.contact_tel_no) if contract_entry is not None else '')
	body += u'導入予定アカウント数：%s\n' % (noneToZeroStr(
		contract_entry.contact_prospective_account_num) if contract_entry is not None else '')      # Google Workspace 版申込ページ対応…見込みアカウント数対応 2017.06.05

	# Google Workspace 版申込ページ対応…会社情報サーバーから送る対応 2017.06.05
	#mail.send_mail(
	#			sender=sateraito_inc.MESSAGE_SENDER_EMAIL,
	#			subject=subject,
	#			to=sateraito_inc.SALES_MEMBERS_EMAILS,
	#			body=body,
	#			#reply_to=reply_to,
	#			)

	# ※ここはアドオンごとに変更してください
	addon_id = ''
	if contract_entry is not None:
		if contract_entry.sp_code == oem_func.SP_CODE_WORKSMOBILE:
			addon_id = 'ESTORAGE_EXCLUSIVE'
		# Workplace対応 2017.09.13
		elif contract_entry.sp_code == oem_func.SP_CODE_WORKPLACE:
			addon_id = 'ESTORAGE_EXCLUSIVE'
		elif contract_entry.sp_code == oem_func.SP_CODE_SSITE:
			addon_id = 'ESTORAGE_EXCLUSIVE'
		elif contract_entry.sp_code == oem_func.SP_CODE_GSUITE:
			if sateraito_inc.appspot_domain == 'sateraito-electronic-storage':
				addon_id = 'ESTORAGE_NONFREE'
			elif sateraito_inc.appspot_domain == 'sateraito-electronic-storage2':
				addon_id = 'ESTORAGE_FREE'
			elif sateraito_inc.appspot_domain == 'kddi-electronic-storage':
				addon_id = 'ESTORAGE_KDDI'
			elif sateraito_inc.appspot_domain == 'vn-sateraito-electronic-storage':
				addon_id = 'ESTORAGE_DEV'
	else:
		addon_id = ''
		if sateraito_inc.appspot_domain == 'sateraito-electronic-storage':
			addon_id += 'ESTORAGE_NONFREE'
		elif sateraito_inc.appspot_domain == 'sateraito-electronic-storage2':
			addon_id += 'ESTORAGE_FREE'
		elif sateraito_inc.appspot_domain == 'kddi-electronic-storage':
			addon_id += 'ESTORAGE_KDDI'

	# サンキューメールとセットアップ通知の統合対応 2017.09.15
	# サンキューメールの送信情報を作成
	thankyou_mail_to = ''
	thankyou_mail_subject = ''
	thankyou_mail_body = ''
	thankyou_mail_html_body = ''
	if is_send_thankyou_mail:
		thankyou_mail_to, thankyou_mail_subject, thankyou_mail_body, thankyou_mail_html_body = createInstallNotificationMailInfo(domain_entry, contract_entry, my_lang)

	post_data = {
		'subject': subject,
		'body': body,
		'addon_id': addon_id,
		'sp_code': noneToZeroStr(contract_entry.sp_code) if contract_entry is not None else '',
		'oem_company_code': noneToZeroStr(contract_entry.oem_company_code) if contract_entry is not None else '',
		'tenant_or_domain': domain_entry.google_apps_domain,
		'available_start_date': domain_entry.available_start_date if domain_entry.available_start_date is not None else '',
		'charge_start_date': domain_entry.charge_start_date if domain_entry.charge_start_date is not None else '',
		'cancel_date': domain_entry.cancel_date if domain_entry.cancel_date is not None else '',
		'company_name': noneToZeroStr(contract_entry.company_name) if contract_entry is not None else '',
		'tanto_name': noneToZeroStr(contract_entry.tanto_name) if contract_entry is not None else '',
		'contact_mail_address':noneToZeroStr(contract_entry.contact_mail_address) if contract_entry is not None else '',			# 追加 2018.04.11
		'contact_tel_no': noneToZeroStr(contract_entry.contact_tel_no) if contract_entry is not None else '',
		'contact_prospective_account_num': noneToZeroStr(
			contract_entry.contact_prospective_account_num) if contract_entry is not None else '',
		# サンキューメールとセットアップ通知の統合対応 2017.09.15
		'version':'v2',			# API側での動作分岐のため
		'is_send_setup_mail':'send' if is_send_setup_mail else '',			# セットアップ通知を送るかどうかのフラグ
		'is_send_thankyou_mail':'send' if is_send_thankyou_mail else '',			# サンキューメールを送るかどうかのフラグ
		'thankyou_mail_to':thankyou_mail_to,
		'thankyou_mail_subject':thankyou_mail_subject,
		'thankyou_mail_body':thankyou_mail_body,
		'thankyou_mail_html_body':thankyou_mail_html_body,
		}
	payload = json.JSONEncoder().encode(post_data)
	headers = {'Content-Type': 'application/json'}
	retry_cnt = 0
	while True:
		try:
			now = datetime.datetime.now()
			MD5_SUFFIX_KEY_APPSSUPPORT = '0234b04994db475facdc22e5a0351676'    # 認証APIのMD5SuffixKey（サテライトサポート窓口アプリ）
			check_key = UcfUtil.md5(addon_id + now.strftime('%Y%m%d%H%M') + MD5_SUFFIX_KEY_APPSSUPPORT)
			url = 'https://sateraito-apps-support.appspot.com/api/sendmail_to_salesmembers?addon_id=%s&ck=%s' % (
				UcfUtil.urlEncode(addon_id), UcfUtil.urlEncode(check_key))
			result = urlfetch.fetch(url=url, payload=payload, headers=headers, method=urlfetch.POST, deadline=10,
				follow_redirects=True)
			if result.status_code != 200:
				raise Exception(str(result.status_code))
			break
		except Exception as e:
			if retry_cnt < 3:
				logging.warning('retry' + '(' + str(retry_cnt) + ')... ' + str(e))
				retry_cnt += 1
			else:
				logging.exception(e)
				break

# SSITE、SSOGadget対応：ご担当者にセットアップ完了メール送信 2017.01.25
def createInstallNotificationMailInfo(domain_entry, contract_entry, my_lang):
	logging.info('createInstallNotificationMailInfo start...')

	to = noneToZeroStr(contract_entry.contact_mail_address) if contract_entry is not None else ''

	# サンキューメールとセットアップ通知の統合対応 2017.09.15
	# if to is not None and to != '':
	logging.info('to=' + to)

	message_subject = ''
	message_body = ''
	setup_url = ''  # Google Workspace 版申込ページ対応 2017.06.05
	if contract_entry.sp_code == oem_func.SP_CODE_WORKSMOBILE:
		message_subject = my_lang.getMsg('CONTRACT_NOTIFICATION_MAIL_FOR_WORKSMOBILE_SUBJECT')
		message_body = my_lang.getMsg('CONTRACT_NOTIFICATION_MAIL_FOR_WORKSMOBILE_BODY')
	elif contract_entry.sp_code == oem_func.SP_CODE_SSITE:
		message_subject = my_lang.getMsg('CONTRACT_NOTIFICATION_MAIL_FOR_WORKSMOBILE_BY_SSITE_SUBJECT')
		message_body = my_lang.getMsg('CONTRACT_NOTIFICATION_MAIL_FOR_WORKSMOBILE_BY_SSITE_BODY')
	# Workplace対応 2017.09.13
	elif contract_entry.sp_code == oem_func.SP_CODE_WORKPLACE:
		message_subject = my_lang.getMsg('CONTRACT_NOTIFICATION_MAIL_FOR_WORKPLACE_SUBJECT')
		message_body = my_lang.getMsg('CONTRACT_NOTIFICATION_MAIL_FOR_WORKPLACE_BODY')
	# Google Workspace 版申込ページ対応…無償版 2017.06.05
	# elif contract_entry.sp_code == oem_func.SP_CODE_GSUITE and sateraito_inc.IS_FREE_EDITION:
	elif contract_entry.sp_code == oem_func.SP_CODE_GSUITE:
		message_subject = my_lang.getMsg('CONTRACT_NOTIFICATION_MAIL_FOR_GSUITE_FREE_EDITION_SUBJECT')
		message_body = my_lang.getMsg('CONTRACT_NOTIFICATION_MAIL_FOR_GSUITE_FREE_EDITION_BODY')
		# 無償版MarketplaceアプリセットアップURL
		# setup_url = 'https://admin.google.com/%s/OauthTosCombined?appId=%s&redirectUri=https://admin.google.com/AdminHome' % (
		# 	noneToZeroStr(domain_entry.google_apps_domain), sateraito_inc.WEBAPP_APP_ID)
		setup_url = 'https://workspace.google.com/u/0/marketplace/dwi/%s?redirect_url=./marketplace/adminoauthpromptredirect' % (
			sateraito_inc.WEBAPP_APP_ID)

	dt_now = datetime.datetime.now()
	data = {
		'COMPANY_NAME': noneToZeroStr(contract_entry.company_name) if contract_entry is not None else '',
		'TANTO_NAME': noneToZeroStr(contract_entry.tanto_name) if contract_entry is not None else '',
		'DATETIME': dt_now.strftime('%Y/%m/%d'),
		'WORKFLOW_TENANT': noneToZeroStr(contract_entry.tenant) if contract_entry is not None else '',
		'SSITE_TENANT': noneToZeroStr(contract_entry.ssite_tenant) if contract_entry is not None else '',
		'WORKSMOBILE_DOMAIN': noneToZeroStr(contract_entry.worksmobile_domain) if contract_entry is not None else '',
		# Workplace対応 2017.09.13
		'WORKPLACE_DOMAIN': noneToZeroStr(contract_entry.workplace_domain) if contract_entry is not None else '',
		'SSO_TENANT': noneToZeroStr(contract_entry.sso_tenant) if contract_entry is not None else '',
		# Google Workspace 版申込ページ対応 2017.06.05
		'GOOGLE_APPS_DOMAIN': noneToZeroStr(domain_entry.google_apps_domain),
		'SETUP_URL': createShortURL(setup_url),
	}

	subject = UcfUtil.editInsertTag(message_subject, data, '[$$', '$$]')
	body = UcfUtil.editInsertTag(message_body, data, '[$$', '$$]')

	# # register sending mail queue
	# params = {
	# 	'sender': sateraito_inc.MESSAGE_SENDER_EMAIL,
	# 	'subject': subject,
	# 	'to': to,
	# 	'body': body,
	# 	}
	# mail_q = taskqueue.Queue('mail-send-queue')
	# mail_t = taskqueue.Task(
	# 	url='/' + domain_entry.google_apps_domain + '/tq/sendmail',
	# 	params=params,
	# 	target=getBackEndsModuleNameDeveloper('commonprocess'), # frontend
	# 	countdown=5,
	# )
	# mail_q.add(mail_t)
	thankyou_mail_to = to
	thankyou_mail_subject = subject
	thankyou_mail_body = body
	thankyou_mail_html_body = ''

	return thankyou_mail_to, thankyou_mail_subject, thankyou_mail_body, thankyou_mail_html_body

def getActiveTimeZone(timezone):
	# filter by ACTIVE_TIMEZONES
	return timezone if timezone in ACTIVE_TIMEZONES else sateraito_inc.DEFAULT_TIMEZONE

def getScriptLibVirtualUrl():
	return '/lib/' if not sateraito_inc.debug_mode else '/lib/debug/'

def get_directory_service(viewer_email, google_apps_domain, target_google_apps_domain=None, num_retry=0,
                          do_not_retry=False, do_not_use_impersonate_mail=False, credentials=None):
  # Directory API can be used by only Google Workspace Admin user
  # get admin user email
  try:
    directory_service = _get_directory_service(viewer_email, google_apps_domain,
                                               target_google_apps_domain=target_google_apps_domain,
                                               do_not_use_impersonate_mail=do_not_use_impersonate_mail,
                                               credentials=credentials)
    return directory_service
  # except AccessTokenRefreshError as e:  # g2対応
  except RefreshError as e:
    raise e
  except BaseException as e:
    if do_not_retry:
      raise e
    if num_retry > 10:
      raise e
    else:
      sleep_time = timeToSleep(num_retry)
      time.sleep(sleep_time)
      return get_directory_service(viewer_email, google_apps_domain,
                                   target_google_apps_domain=target_google_apps_domain,
                                   num_retry=num_retry + 1, do_not_use_impersonate_mail=do_not_use_impersonate_mail)

def _get_directory_service(viewer_email, google_apps_domain, target_google_apps_domain=None, do_not_use_impersonate_mail=False, credentials=None):
	# Directory API can be used by only Google Workspace Admin user
	# get admin user email

	logging.info('_get_directory_service')
	old_namespace = namespace_manager.get_namespace()
	namespace_manager.set_namespace('')
	impersonate_email = ""
	if do_not_use_impersonate_mail:
		impersonate_email = viewer_email
	else:
		row_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
		if row_dict is not None:
			impersonate_email = row_dict["impersonate_email"]
		if impersonate_email == "":
			impersonate_email = viewer_email

	logging.info('impersonate_email:' + impersonate_email)
	# memcache_expire_secs = 30 * 60 * 1
	# memcache_key = 'script=getappservice&google_app_domain=' + google_app_domain + '&email_to_check=' + impersonate_email
	if credentials is not None:
		service = build('admin', 'directory_v1', credentials=credentials)
	else:
		credentials = get_authorized_http(impersonate_email, google_apps_domain, sateraito_inc.OAUTH2_SCOPES)
		service = build('admin', 'directory_v1', credentials=credentials)

	# set old namespace
	namespace_manager.set_namespace(old_namespace)
	return service

def getRelatedSateraitoAddressDomain(google_apps_domain=None):
	# for special domain:
	if google_apps_domain is not None:
		if google_apps_domain == 'akindo-sushiro.co.jp':
			return 'https://akindo-sushiro-address.appspot.com'
		if google_apps_domain == 'home.misawa.co.jp':
			return 'https://sateraito-apps-address-misawa.appspot.com'
		if google_apps_domain == 'hokkaido.ccbc.co.jp':
			return 'https://kddi-address.appspot.com'
		if google_apps_domain == 'ranet.co.jp':
			return 'https://kddi-address.appspot.com'
		if google_apps_domain == 'ssi.co.jp':
			return 'https://kddi-address.appspot.com'
		if google_apps_domain == 'okuwa.co.jp':
			return 'https://kddi-address.appspot.com'
		if google_apps_domain == 'housemate.co.jp':
			return 'https://kddi-address.appspot.com'
		if google_apps_domain == 'ma.master-apps.jp':
			return 'https://kddi-address.appspot.com'
		if google_apps_domain == 'housemate.co.jp':
			return 'https://kddi-address.appspot.com'
		if google_apps_domain == 'k17.k-cloud.biz':
			return 'https://kddi-address.appspot.com'
			# for kddi-product
	if sateraito_inc.appspot_domain == 'kddi-electronic-storage':
		return 'https://kddi-address.appspot.com'
		# for noemal domain
	if sateraito_inc.IS_FREE_EDITION:
		return 'https://sateraito-apps-address2.appspot.com'
	return 'https://sateraito-apps-address.appspot.com'

#=====================2022-05-31==========================================
def isWorkflowAdminForSharePoint(user_email, tenant_or_domain, app_id=None, do_not_include_additional_admin=False):
	'''
check if user is workflow admin user
Args:
				user_email ... user to check
Return:
				true ... user_email is GoogleApps admin or member of workflow group
'''

	# memcache entry expires in 10 min
	memcache_expire_secs = 60 * 30
	memcache_key = 'script=isworkflowadmin_for_sharepoint?user_email=' + user_email + '&g=2'
	# check if cached data exists
	cached_data = memcache.get(memcache_key)
	if cached_data is not None:
		logging.info('isWorkflowAdmin: found and respond cached data result = ' + cached_data)
		return strToBool(cached_data)

	is_workflow_admin = False
	user_entry = sateraito_db.GoogleAppsUserEntry.getInstance(tenant_or_domain, user_email)
	if user_entry is not None:
		is_workflow_admin = user_entry.is_apps_admin if user_entry.is_apps_admin is not None else False

	# # # Edit 2021-02-02
	# if is_workflow_admin == False:
	# 	# Check user or group allow access
	# 	if tenant_or_domain is not None:
	# 		is_allow_user_or_groups = checkUserOrGroupAllowAccessForSSite(user_email, tenant_or_domain, None)
	# 		# logging.info(is_allow_user_or_groups)
	# 		is_workflow_admin = is_allow_user_or_groups

	if not is_workflow_admin:
		logging.debug('user is not apps admin, not member of workflow group')
		if not do_not_include_additional_admin:
			if ifUserMemberOfAdditionalWorkflowAdmin(user_email, tenant_or_domain, app_id):
				logging.debug('user is a member of ADDITIONAL admin user')
				is_workflow_admin = True

	if not memcache.set(key=memcache_key, value=boolToStr(is_workflow_admin), time=memcache_expire_secs):
		logging.warning("Memcache set failed.")

	return is_workflow_admin

# SSOGadget対応：ワークフロー管理者判定（とりあえずSSITEと同じロジック）
def isWorkflowAdminForSSOGadget(user_email, tenant_or_domain, app_id=None, do_not_include_additional_admin=False):
	return isWorkflowAdminForSSite(user_email, tenant_or_domain, app_id, do_not_include_additional_admin=do_not_include_additional_admin)

def needToShowUpgradeLink(google_apps_domain):
	""" check if domain is in status to show upgrade link
		Return: True if showing upgrade link is needed
"""
	# Upgrade link is shown ONLY IN FREE edition
	if not sateraito_inc.IS_FREE_EDITION:
		return False
		# check number of users
	row = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain)
	if row is None:
		return False
	available_users = row.available_users
	num_users = row.num_users
	logging.info('available_users=' + str(available_users) + ' num_users=' + str(num_users))
	if available_users is not None and num_users is not None:
		if available_users < num_users:
			return True
	return False

# For SSO
def getUserListSSOGadget(google_apps_domain, app_id, viewer_email):
	users = []
	ssogadget_app_key = sateraito_db.GoogleAppsDomainEntry.getSSOAppKey(google_apps_domain)
	if ssogadget_app_key != '':
		client = ssoclient.SSOClient(google_apps_domain, ssogadget_app_key, viewer_email)
		access_token = client.getAccessToken()
		if access_token != '':
			users = client.getUserInfoList(access_token)

	return users

def getMyJoiningGroupSSOGadget(google_apps_domain, viewer_email):
	groups = []
	ssogadget_app_key = sateraito_db.GoogleAppsDomainEntry.getSSOAppKey(google_apps_domain)
	if ssogadget_app_key != '':
		client = ssoclient.SSOClient(google_apps_domain, ssogadget_app_key, viewer_email)
		access_token = client.getAccessToken()
		if access_token != '':
			groups = client.getGroupListObject(access_token)
			for group in groups:
				if viewer_email in group['members']:
					groups = groups.append(group['email'])

	return groups

def getGroupListSSOGadget(google_apps_domain, viewer_email):
	groups = []
	ssogadget_app_key = sateraito_db.GoogleAppsDomainEntry.getSSOAppKey(google_apps_domain)
	if ssogadget_app_key != '':
		client = ssoclient.SSOClient(google_apps_domain, ssogadget_app_key, viewer_email)
		access_token = client.getAccessToken()
		if access_token != '':
			groups = client.getGroupInfoList(access_token)

	return groups

def getUserInfoSSOGadget(google_apps_domain, viewer_email):
	""" Get user data from SSOGadget
"""
	family_name = ''
	given_name = ''
	user_rec = sateraito_db.UserInfo.getInstance(str(viewer_email).lower())
	if user_rec is not None:
		family_name = user_rec.family_name
		given_name = user_rec.given_name

	user_info = {
		'user_email': viewer_email,
		'family_name': family_name,
		'given_name': given_name,
		'photo_url': '',
		}

	return user_info

def fetch_user_data_SSOGadget(google_apps_domain, app_id, viewer_email, return_by_object=False):
	""" Get user list data from SSOGadget
"""
	old_namespace = namespace_manager.get_namespace()
	setNamespace(google_apps_domain, app_id)
	family_name = ''
	given_name = ''
	user_rec = sateraito_db.UserInfo.getInstance(str(viewer_email).lower())
	if user_rec is not None:
		family_name = user_rec.family_name
		given_name = user_rec.given_name
	user_entry = {
		'user_email': str(viewer_email).lower(),
		'family_name': family_name,
		'given_name': given_name,
	}
	namespace_manager.set_namespace(old_namespace)
	if return_by_object:
		return user_entry
	# return json data
	jsondata = json.JSONEncoder().encode(user_entry)
	return jsondata


# For SSITE
def getAccessTokenSSite(google_apps_domain, viewer_email, uid='', ck=''):

	service = None
	access_token = ''
	check_key_temp = ''

	domain_site = sateraito_db.GoogleAppsDomainEntry.getSSiteTenantID(google_apps_domain)
	if not domain_site:
		domain_site = google_apps_domain

	logging.info('get access token follow domain sateraito-site: ' + str(domain_site))

	# old namespace
	old_namespace = namespace_manager.get_namespace()

	# set namespace
	namespace_manager.set_namespace(google_apps_domain)

	memcache_expire_secs = 30 * 60 * 1
	memcache_key = 'script=get_accesstoken_for_ssite&google_apps_domain=' + google_apps_domain + '&email_to_check=' + viewer_email + '&g=2'

	service = ssiteclient.SSITEClient(domain_site, viewer_email, uid, ck)

	cached_data = memcache.get(memcache_key)
	if cached_data is not None:
		if cached_data['ck'] != ck and ck:
			logging.warn('get access_token new')
			memcache.delete(memcache_key)
			access_token = service.getAccessToken()
			check_key_temp = ck
		else:
			logging.info('get_accesstoken_for_ssite: found and respond cached data')
			access_token = cached_data['access_token']
			ck = cached_data['ck']
	else:
		if uid and ck:
			access_token = service.getAccessToken()
			check_key_temp = ck

	if check_key_temp:
		ck = check_key_temp
		user_entry = sateraito_db.GoogleAppsUserEntry.getInstance(google_apps_domain, viewer_email)
		if user_entry is not None:
			if ck != user_entry.check_key_ssite:
				user_entry.check_key_ssite = ck
				user_entry.put()

	if access_token:
		if not memcache.set(key=memcache_key, value={'access_token':access_token, 'ck': ck}, time=memcache_expire_secs):
			logging.info("Memcache set failed.")
	else:
		user_entry = sateraito_db.GoogleAppsUserEntry.getInstance(google_apps_domain, viewer_email)
		if user_entry is not None and user_entry.check_key_ssite is not None:
			ck = user_entry.check_key_ssite
			uid = user_entry.user_id
			service = ssiteclient.SSITEClient(domain_site, viewer_email, uid, ck)
			access_token = service.getAccessToken()

			if not memcache.set(key=memcache_key, value={'access_token':access_token, 'ck': ck}, time=memcache_expire_secs):
				logging.info("Memcache set failed.")

	namespace_manager.set_namespace(old_namespace)

	logging.info('access_token of ssite=' + str(access_token))

	return service, access_token

def checkUserOrGroupAllowAccessForSSite(user_email, tenant, app_id):
	"""
	check if the user is member of allow_user_or_group
	Args:
		user_email .. email to check user
		checker .... checker object
	"""
	logging.info('checkUserOrGroupAllowAccessForSSite: user_email=' + str(user_email))
	logging.info('tenant=' + str(tenant))
	logging.info('app_id=' + str(app_id))

	old_namespace = namespace_manager.get_namespace()
	setNamespace(tenant, app_id)
	entry = sateraito_db.OtherSetting.getInstance(auto_create=True)
	if entry:
		allow_user_or_groups = ''
		if entry.allow_user_or_groups:
			allow_user_or_groups = entry.allow_user_or_groups
		accessible_user_or_groups = allow_user_or_groups.split()
		accessible_members_set = set(accessible_user_or_groups)
		if user_email in accessible_members_set:
			logging.info('user or group is member')
			return True

	namespace_manager.set_namespace(old_namespace)
	return False

def getNumUsersSSite(google_apps_domain, viewer_email):
	num_users = 0

	service, access_token = getAccessTokenSSite(google_apps_domain, viewer_email)
	if access_token and service is not None:
		user_list = service.getUserInfoList(access_token)
		num_users = len(user_list)

	return num_users

def getGroupMembers(service, access_token, group_id):
	# memcache entry expires in 30 min
	memcache_expire_secs = 60 * 30
	memcache_key = 'script=getgroupmembersssite?group_id=' + group_id + '&g=2'
	# check if cached data exists
	cached_data = memcache.get(memcache_key)
	if cached_data is not None:
		logging.debug('getgroupmembers ' + str(group_id) + ': found and respond cached data')
		logging.debug('group_member=' + str(cached_data))
		return cached_data

	group_member = service.getGroupMembers(group_id, access_token)
	# add data to cache
	if not memcache.set(key=memcache_key, value=group_member, time=memcache_expire_secs):
		logging.debug("Memcache set failed.")

	return group_member

def isWorkflowAdminForSSite(user_email, tenant_or_domain, app_id=None, do_not_include_additional_admin=False):
	'''
check if user is workflow admin user
Args:
				user_email ... user to check
Return:
				true ... user_email is GoogleApps admin or member of workflow group
'''

	logging.info('isWorkflowAdmin user_email=' + str(user_email))

	# memcache entry expires in 10 min
	memcache_expire_secs = 60 * 30
	# LINE WORKS直接認証対応…ついでに対応 2019.06.13
	#memcache_key = 'script=isworkflowadmin_for_ssite?user_email=' + user_email
	memcache_key = 'script=isworkflowadmin_for_ssite?user_email=' + user_email + '&do_not_include_additional_admin=' + str(do_not_include_additional_admin) + '&g=2'
	# check if cached data exists
	cached_data = memcache.get(memcache_key)
	if cached_data is not None:
		logging.info('isWorkflowAdmin: found and respond cached data result = ' + cached_data)
		return strToBool(cached_data)

	is_workflow_admin = False
	user_entry = sateraito_db.GoogleAppsUserEntry.getInstance(tenant_or_domain, user_email)
	if user_entry is not None:
		#is_workflow_admin = user_entry.is_admin_for_ssite if user_entry.is_admin_for_ssite is not None else False
		is_workflow_admin = user_entry.is_apps_admin if user_entry.is_apps_admin is not None else False

	# # # Edit 2021-02-02
	# if is_workflow_admin == False:
	# 	# Check user or group allow access
	# 	if tenant_or_domain is not None:
	# 		is_allow_user_or_groups = checkUserOrGroupAllowAccessForSSite(user_email, tenant_or_domain, app_id)
	# 		# logging.info(is_allow_user_or_groups)
	# 		is_workflow_admin = is_allow_user_or_groups

	if not is_workflow_admin:
		logging.debug('user is not apps admin, not member of workflow group')
		if not do_not_include_additional_admin:
			if ifUserMemberOfAdditionalWorkflowAdmin(user_email, tenant_or_domain, app_id):
				logging.debug('user is a member of ADDITIONAL admin user')
				is_workflow_admin = True

	if not memcache.set(key=memcache_key, value=boolToStr(is_workflow_admin), time=memcache_expire_secs):
		logging.warning("Memcache set failed.")
	return is_workflow_admin

def getUserListSSiteGadget(google_apps_domain, viewer_email):
	return _getUserListSSiteGadget(google_apps_domain, viewer_email)

def _getUserListSSiteGadget(google_apps_domain, viewer_email, target_google_apps_domain=None, return_by_object=False):
	users = []

	service, access_token = getAccessTokenSSite(google_apps_domain, viewer_email)
	if access_token and service is not None:
		user_list = service.getUserInfoList(access_token)
		for each_user in user_list:
			each_user_email = each_user["primaryEmail"]
			family_name = ''
			given_name = ''
			if each_user["name"] is None or (
					each_user["name"]["familyName"] is None and each_user["name"]["givenName"] is None):
				user_rec = sateraito_db.GoogleAppsUserEntry.getInstance(google_apps_domain, str(each_user_email).lower())
				if user_rec is not None:
					family_name = user_rec.user_family_name
					given_name = user_rec.user_given_name
			else:
				family_name = each_user["name"]["familyName"]
				given_name = each_user["name"]["givenName"]

			if not family_name and not given_name:
				family_name = each_user_email.split("@")[0]

			users.append({
				'user_email': str(each_user_email).lower(),
				'family_name': family_name,
				'given_name': given_name,
			})

	return users

def getMyJoiningGroupSSiteGadget(google_apps_domain, email_to_check, viewer_email):
	groups = []
	# memcache entry expires in 30 min
	memcache_expire_secs = 60 * 30
	memcache_key = 'script=getMyJoiningGroupSSiteGadget?google_apps_domain=' + google_apps_domain + '&email_to_check=' + email_to_check + '&g=2'
	# check if cached data exists
	cached_data = memcache.get(memcache_key)
	if cached_data is not None:
		logging.debug('_getMyJoiningGroupSSite: found and respond cached data')
		logging.debug('group_list=' + str(cached_data))
		return cached_data

	groups = _getMyJoiningGroupSSite(google_apps_domain, email_to_check, viewer_email)
	logging.info(groups)

	# add data to cache
	if not memcache.set(key=memcache_key, value=groups, time=memcache_expire_secs):
		logging.debug("Memcache set failed.")

	return groups

def _getMyJoiningGroupSSite(google_apps_domain, email_to_check, viewer_email, service=None, access_token='', processed_group_ids=None):
	logging.info('_getMyJoiningGroupSSite processed_group_emails_id=' + str(processed_group_ids))
	# 処理済みグループ判別用set
	if processed_group_ids is None:
		processed_group_ids = set([])

	groups = []
	if service is None or access_token == '':
		service, access_token = getAccessTokenSSite(google_apps_domain, viewer_email)

	if access_token and service is not None:
		group_list = service.getGroupListObject(access_token, use_key=email_to_check)

		for each_group in group_list:
			group_id = str(each_group['id']).lower()
			if not (group_id in processed_group_ids):
				groups.append(group_id)
				processed_group_ids.add(group_id)
				parent_groups = _getMyJoiningGroupSSite(google_apps_domain, group_id, viewer_email,
																								service=service, access_token=access_token,
																								processed_group_ids=processed_group_ids)
				logging.info('parent_groups=' + str(parent_groups))
				groups.extend(parent_groups)

		# remove duplicate
		groups = list(set(groups))

	return groups

def getGroupMembersSSiteGadget(google_apps_domain, viewer_email, group_id):
	is_group = 0
	group_members = []
	user_members = []

	service, access_token = getAccessTokenSSite(google_apps_domain, viewer_email)
	if access_token and service is not None:
		groups = service.getGroupMembers(group_id, access_token)
		for member in groups:
			if member['type'] == 'USER':
				user_members.append(member['email'])
			elif member['type'] == 'GROUP':
				group_members.append(member['id'])
			is_group = 1

	return is_group, group_members, user_members

def getUserInfoSSiteGadget(google_apps_domain, viewer_email):
	service, access_token = getAccessTokenSSite(google_apps_domain, viewer_email)
	if access_token and service is not None:
		user = service.getUser(access_token, viewer_email)
	else:
		user = sateraito_db.GoogleAppsUserEntry.getInstance(google_apps_domain, str(viewer_email).lower())

	return user

def fetch_user_data_SSiteGadget(google_apps_domain, viewer_email, return_by_object=False):
	""" Get user list data from SSiteGadget
	"""
	family_name = ''
	given_name = ''
	user_entry = None

	service, access_token = getAccessTokenSSite(google_apps_domain, viewer_email)
	if access_token and service is not None:
		user_entry = service.getUser(access_token, viewer_email)

	if user_entry is None or user_entry["name"] is None or (
		user_entry["name"]["familyName"] is None and user_entry["name"]["givenName"] is None):
		user_email = viewer_email
		user_rec = sateraito_db.GoogleAppsUserEntry.getInstance(google_apps_domain, user_email)
		if user_rec is not None:
			family_name = user_rec.user_family_name
			given_name = user_rec.user_given_name
	else:
		family_name = user_entry['name']['familyName']
		given_name = user_entry['name']['givenName']
		user_email = user_entry['primaryEmail']
		is_apps_admin = user_entry['isAdmin']
		user_rec = sateraito_db.GoogleAppsUserEntry.getInstance(google_apps_domain, str(user_email).lower())
		if user_rec is not None:
			user_rec.user_family_name = family_name
			user_rec.user_given_name = given_name
			user_rec.is_apps_admin = is_apps_admin
			user_rec.put()
	if not family_name and not given_name:
		family_name = user_email.split("@")[0]
	user_entry = {
		'user_email': str(viewer_email).lower(),
		'family_name': family_name,
		'given_name': given_name,
	}

	if return_by_object:
		return user_entry
	# return json data
	jsondata = json.JSONEncoder().encode(user_entry)
	return jsondata

def epochTodatetime(epoch):
	return datetime.datetime(*time.localtime(epoch)[:6])

def createNewFileId(name_field):
	""" create new file id string
	"""
	return name_field + '-' + dateString() + randomString()

def createNewId(string_length):
	return dateString() + randomString(string_length=string_length)

def isValidEmail(email):
	if email is None or email == '':
		return False

	regexp = re.compile('([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})|([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]{2,})')
	if regexp.search(email) is None:
		return False

	return True

def boolToNumber(check):
	if check:
		return 1
	else:
		return 0

def createWFUserListSearch(row):
	return sateraito_search.create_wf_user_list_search(row)

def addToTextSearchWFUserListIndex(row):
	return sateraito_search.add_to_text_search_wf_user_list_index(row)

def removeToTextSearchWFUserListIndex(row):
	return sateraito_search.remove_to_text_search_wf_user_list_index(row)

def getFileEncoding(value):
	return value if value is not None and value != '' else 'cp932'

def getFolderNameFullpath(folder_code):
	folder_dict = sateraito_db.DocFolder.getDict(folder_code)
	if folder_dict is None:
		return None
	if folder_dict['parent_folder_code'] == '__root':
		return '/' + folder_dict['folder_name']
	else:
		return getFolderNameFullpath(folder_dict['parent_folder_code']) + '/' + folder_dict['folder_name']

def get_gmail_service(viewer_email, google_apps_domain):
	# http = get_authorized_http(viewer_email, google_apps_domain, sateraito_inc.OAUTH2_SCOPES_GMAIL)
	credentials = get_authorized_http(viewer_email, google_apps_domain, sateraito_inc.OAUTH2_SCOPES_GMAIL)
	return build('gmail', 'v1', credentials=credentials)

def get_http(viewer_email, google_apps_domain):
	return get_authorized_http2(viewer_email, google_apps_domain, sateraito_inc.OAUTH2_SCOPES_GMAIL)

def get_http_google_drive(viewer_email, google_apps_domain):
	return get_authorized_http2(viewer_email, google_apps_domain, sateraito_inc.OAUTH2_SCOPES_DRIVE)

def get_authorized_http2(viewer_email, google_apps_domain, scope=sateraito_inc.OAUTH2_SCOPES):
	old_namespace = namespace_manager.get_namespace()
	namespace_manager.set_namespace(google_apps_domain)

	http = None
	access_token = ''

	try:
		namespace_manager.set_namespace(google_apps_domain)
		memcache_expire_secs = 60 * 60 * 1
		memcache_key = 'script=getauthorizedhttp&v=2&google_apps_domain=' + google_apps_domain + '&email_to_check=' + viewer_email + '&scope=' + str(scope) + '&g=2'

		# （参考）https://developers.google.com/identity/protocols/oauth2/service-account
		credentials = google.oauth2.service_account.Credentials.from_service_account_info(
			sateraito_inc.SERVICE_ACCOUNT_INFO,
			scopes=scope,
		)
		credentials = credentials.with_subject(viewer_email)
		dictTokenInfo = memcache.get(memcache_key)
		# @UndefinedVariable
		boolTokenIsValid = False
		if dictTokenInfo:
			logging.debug('get_authorized_http: cache found.')
			credentials.token = dictTokenInfo.get('token')
			credentials.expiry = dictTokenInfo.get('expiry')
			boolTokenIsValid = credentials.valid

		if (not boolTokenIsValid):
			http = apiclient.http.build_http()
			request = google_auth_httplib2.Request(http)
			credentials.refresh(request)
			if (credentials.valid):
				dictTokenInfo = {
					'token': credentials.token,
					'expiry': credentials.expiry,
				}
				if not memcache.set(key=memcache_key, value=dictTokenInfo, time=memcache_expire_secs):  # @UndefinedVariable
					logging.warning("get_authorized_http: Memcache set failed.")
				else:
					logging.warning('get_authorized_http: credentials.refresh')

			logging.debug('credentials.token	= ' + str(credentials.token))
			logging.debug('credentials.expiry = ' + str(credentials.expiry))

		# return http
		return credentials, credentials.token

	except Exception as e:
		logging.exception(e)

	finally:
		# set old namespace
		namespace_manager.set_namespace(old_namespace)

# 添付ファイル名の正規化
def normalizeFileName(file_name):
	# なぜかDB側にC:\などからフルパスで入っている場合があるのでとりあえずここではじく
	file_name = os.path.basename(os.path.normpath(file_name))
	# Windows用
	ary_file_name = file_name.split('\\')
	file_name = ary_file_name[len(ary_file_name) - 1]
	# Windowsでファイル名として許容されていない記号などを加工
	file_name = file_name.replace('\\', ' ').replace(':', ' ').replace('*', ' ').replace('?', ' ').replace('"', ' ').replace('|', ' ').replace('<', ' ').replace('>', ' ').replace('/', ' ')
	return file_name

#  機種依存文字対策…Unicodeとして無効な文字をカットする
def removeInvalidUnicodeChar(value):
	# return value
	if value is None:
		return value
	dummy_ele = lxml.html.Element('span')
	# dummy_ele = self._dummy_ele
	try:
		dummy_ele.text = value
	except ValueError as e:
		cs = []
		for c in value:
			try:
				dummy_ele.text = c
			except ValueError as e2:
				# logging.exception(e2)
				pass
			else:
				cs.append(c)
		value = ''.join(cs)
	return value

def get_permission_can_upload_folder(folder_id, user_accessible_info_dict=None, viewer_email='', google_apps_domain=None, admin_mode=False):
	if user_accessible_info_dict is None:
		user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(viewer_email, auto_create=True)

	if not admin_mode:
		if not sateraito_db.DocFolder.isAccessibleFolder(folder_id, user_accessible_info_dict, google_apps_domain):
			return False

	# check uploadable
	if admin_mode:
		return True
	else:
		return sateraito_db.DocFolder.isCreatableFolder(folder_id, user_accessible_info_dict, google_apps_domain)

def get_permission_folder(folder_id, user_accessible_info_dict=None, viewer_email='', admin_mode=False):
  if not admin_mode:
    if not sateraito_db.DocFolder.isAccessibleFolder(folder_id, user_accessible_info_dict):
      return False, False, False, False, False

  # check downloadable
  if admin_mode:
    is_downloadable = True
  else:
    is_downloadable = sateraito_db.DocFolder.isDownloadableFolder(folder_id, user_accessible_info_dict)

  logging.info('is_downloadable')
  logging.info(is_downloadable)

  # check uploadable
  if admin_mode:
    is_uploadable = True
  else:
    is_uploadable = sateraito_db.DocFolder.isCreatableFolder(folder_id, user_accessible_info_dict)

  logging.info('is_uploadable')
  logging.info(is_uploadable)

  # check subfolder creatable
  if admin_mode:
    is_subfolder_creatable = True
  else:
    is_subfolder_creatable = sateraito_db.DocFolder.isSubfolderCreatable(folder_id, user_accessible_info_dict)

  logging.info('is_subfolder_creatable')
  logging.info(is_subfolder_creatable)

  # check subfolder delete
  if admin_mode:
    is_deletable = True
  else:
    is_deletable = sateraito_db.DocFolder.isDeletableFolder(folder_id, user_accessible_info_dict)

  logging.info('is_deletable')
  logging.info(is_deletable)

  return True, is_downloadable, is_uploadable, is_subfolder_creatable, is_deletable

def washShiftJISErrorChar(unicode_string):
	"""	Convert character in string which is not in Shift_JIS to '?'
	"""
	if unicode_string is None:
		return unicode_string
	washed_string = unicode_string.encode('cp932', errors='replace').decode('cp932')
	return washed_string

def washJISErrorChar(unicode_string):
	"""  Convert character in string which is not in JIS to '?'
"""
	if unicode_string is None:
		return unicode_string
	washed_string = unicode_string.encode('iso-2022-jp', errors='replace').decode('iso-2022-jp')
	return washed_string

def washUTF8ErrorChar(unicode_string):
	"""  Convert character in string which is not in UTF-8 to '?'
"""
	if unicode_string is None:
		return unicode_string
	washed_string = unicode_string.encode('utf-8', errors='replace').decode('utf-8')
	washed_string = washed_string.replace('\r\n', '\n')
	return washed_string

def washErrorChar(unicode_string, fileencoding):
	if fileencoding == 'utf-8':
		return washUTF8ErrorChar(unicode_string)
	elif fileencoding == 'iso-2022-jp':
		return washJISErrorChar(unicode_string)
	elif fileencoding == 'cp932':
		return washShiftJISErrorChar(unicode_string)
	else:
		return washShiftJISErrorChar(unicode_string)

def encodeString(string, csv_file_encoding=None, type_import=True):
	# logging.info('string:' + str(string))
	if csv_file_encoding is None:
		csv_file_encoding = 'cp932'
		row_dict = sateraito_db.OtherSetting.getDict()
		if 'csv_file_encoding' in row_dict and row_dict['csv_file_encoding'] is not None:
			csv_file_encoding = row_dict['csv_file_encoding']

	try:
		if type_import == True:
			# encode_string = unicode(string, csv_file_encoding).strip().strip('"')  # g2対応
			encode_string = str(string, csv_file_encoding).strip().strip('"')
		else:
			if csv_file_encoding == 'cp932':
				encode_string = washShiftJISErrorChar(string)
			else:
				# encode_string = unicode(string, csv_file_encoding).strip().strip('"')  # g2対応
				encode_string = str(string, csv_file_encoding).strip().strip('"')
	except BaseException as e:
		logging.warning('e:' + str(e))
		encode_string = string.strip().strip('"')

	# logging.info('string2 :' + str(string))
	return encode_string

def createSearchWFUser(email, family_name, given_name, family_name_kana, given_name_kana):
	return sateraito_search.create_search_wf_user(email, family_name, given_name, family_name_kana, given_name_kana)

def addToTextSearchWFUser(obj_data):
	return sateraito_search.add_to_text_search_wf_user(obj_data)

def removeTextSearchFromWFUser(email):
	sateraito_search.remove_text_search_from_wf_user(email)

def removeAllTextSearchFromWFUser():
	sateraito_search.delete_all_in_index(WF_USERLIST_INDEX)

def getAllUsersOAuth2(google_apps_domain, user_email):
	old_namespace = namespace_manager.get_namespace()
	namespace_manager.set_namespace(google_apps_domain)
	user_email_list = []
	q = sateraito_db.GoogleAppsDomainEntry.query()
	for row in q:
		logging.debug('row.google_apps_domain=' + str(row.google_apps_domain))
		target_google_apps_domain = row.google_apps_domain
		apps_service = get_directory_service(user_email, google_apps_domain, target_google_apps_domain)
		page_token = None
		while True:
			try:
				user_list = apps_service.users().list(domain=target_google_apps_domain, pageToken=page_token,
					fields="nextPageToken,users(primaryEmail)").execute()
			except BaseException as instance:
				# entry does not exists
				logging.warn('instance=' + str(instance))
				break
			else:
				# create user list from feed
				if "users" in user_list:
					for user_entry in user_list["users"]:
						member_email = user_entry["primaryEmail"].lower()
						user_email_list.append(member_email)
					if "nextPageToken" in user_list:
						page_token = user_list["nextPageToken"]
					else:
						break
				else:
					break
	namespace_manager.set_namespace(old_namespace)
	return user_email_list

def getAllUsers(google_apps_domain, user_email):
	#SSOGadget対応
	if sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(google_apps_domain):
		return getUserListSSOGadget(google_apps_domain, user_email)
	elif sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(google_apps_domain):
		return getUserListSSiteGadget(google_apps_domain, user_email)
	else:
		return getAllUsersOAuth2(google_apps_domain, user_email)

def isSkipSearchGroup(group):
	for c in group:
		if c == '@':
			return True
		if c not in TEXT_SEARCH_TOKEN_CHARS:
			return False
	return True

def listSearchGroup(groups):
	rtn_groups = []
	for group in groups:
		if not isSkipSearchGroup(group):
			rtn_groups.append(group)
	return rtn_groups

def isEnableAttachFileKeywordSearchFunction(tenant_or_domain, app_id):
	# domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(tenant_or_domain)
	# if domain_dict.get('enable_attach_file_keyword_search_function', False):

	# check other_setting
	other_setting = sateraito_db.OtherSetting.getDict()
	if other_setting.get('enable_attach_file_keyword_search_function', False):
		return True
	return False

def removeDoubleQuota(string_param):
	result = noneToZeroStr(string_param)

	if result is not None and result != '':
		if result[0] == '"':
			result = result.replace('"', '', 1)
		if result[len(result) - 1] == '"':
			result = result.replace('"', '', result.count('"') - 1)

	return result

def escapeForCsv(string_param):
	# multipleのプルダウン対応…カンマ区切りの値に変換 2017.09.06
	if isinstance(string_param, list):
		result = ','.join(string_param)
	else:
		result = none2ZeroStr(string_param)

	# Editorによってはあきらかにカンマ区切りでもタブも区切り文字として識別される場合があるので「\t」も追加 2015.08.11
	#if result.find('\n') >= 0 or result.find(',') >= 0 or result.find('"') >= 0:
	if result.find('\n') >= 0 or result.find('\t') >= 0 or result.find(',') >= 0 or result.find('"') >= 0:
		result = '"' + result.replace('"', '""') + '"'
	else:
		result = '"' + str(result) + '"'
	return result

def getNameScreen(screen_key, lang=sateraito_inc.DEFAULT_LANGUAGE):
	my_lang = MyLang(lang)

	if screen_key == sateraito_db.SCREEN_ADMIN_CONSOLE:
		return my_lang.getMsg('SCREEN_ADMIN_CONSOLE')
	elif screen_key == sateraito_db.SCREEN_USER_CONSOLE:
		return my_lang.getMsg('SCREEN_USER_CONSOLE')
	elif screen_key == sateraito_db.SCREEN_DIRECT_LINK:
		return my_lang.getMsg('SCREEN_DIRECT_LINK')
	elif screen_key == sateraito_db.SCREEN_POPUP_FILE_UPLOAD:
		return my_lang.getMsg('SCREEN_PLUGIN_FILE_UPLOAD')

	return screen_key

def getNameOperation(operation_key, lang=sateraito_inc.DEFAULT_LANGUAGE):
	my_lang = MyLang(lang)

	if operation_key == sateraito_db.OPERATION_DOWNLOAD_FILE:
		return my_lang.getMsg('NAME_OPERATION_DOWNLOAD_FILE')
	elif operation_key == sateraito_db.OPERATION_UPLOAD_FILE:
		return my_lang.getMsg('NAME_OPERATION_UPLOAD_FILE')
	elif operation_key == sateraito_db.OPERATION_DELETE_FILE:
		return my_lang.getMsg('NAME_OPERATION_DELETE_FILE')
	elif operation_key == sateraito_db.OPERATION_CREATE_FOLDER:
		return my_lang.getMsg('NAME_OPERATION_CREATE_FOLDER')
	elif operation_key == sateraito_db.OPERATION_UPDATE_FOLDER:
		return my_lang.getMsg('NAME_OPERATION_UPDATE_FOLDER')
	elif operation_key == sateraito_db.OPERATION_DELETE_FOLDER:
		return my_lang.getMsg('NAME_OPERATION_DELETE_FOLDER')
	elif operation_key == sateraito_db.OPERATION_MOVE_FOLDER:
		return my_lang.getMsg('NAME_OPERATION_MOVE_FOLDER')
	elif operation_key == sateraito_db.OPERATION_COPY_FOLDER:
		return my_lang.getMsg('NAME_OPERATION_COPY_FOLDER')
	elif operation_key == sateraito_db.OPERATION_CREATE_CATEGORIE:
		return my_lang.getMsg('NAME_OPERATION_CREATE_CATEGORIE')
	elif operation_key == sateraito_db.OPERATION_UPDATE_CATEGORIE:
		return my_lang.getMsg('NAME_OPERATION_UPDATE_CATEGORIE')
	elif operation_key == sateraito_db.OPERATION_DELETE_CATEGORIE:
		return my_lang.getMsg('NAME_OPERATION_DELETE_CATEGORIE')
	elif operation_key == sateraito_db.OPERATION_CREATE_WORKFLOW_DOC:
		return my_lang.getMsg('NAME_OPERATION_CREATE_WORKFLOW_DOC')
	elif operation_key == sateraito_db.OPERATION_UPDATE_WORKFLOW_DOC:
		return my_lang.getMsg('NAME_OPERATION_UPDATE_WORKFLOW_DOC')
	elif operation_key == sateraito_db.OPERATION_DELETE_WORKFLOW_DOC:
		return my_lang.getMsg('NAME_OPERATION_DELETE_WORKFLOW_DOC')
	elif operation_key == sateraito_db.OPERATION_IMPORT_CSV:
		return my_lang.getMsg('NAME_OPERATION_IMPORT_CSV')
	elif operation_key == sateraito_db.OPERATION_EXPORT_CSV:
		return my_lang.getMsg('NAME_OPERATION_EXPORT_CSV')

	return operation_key

def compareDatetime(dt_1, dt_2):
	""" returns 1 is dt_1 is Bigger
				returns -1 if dt_1 is smaller
				returns 0 if same
		"""
	tz_utc = tz.tzutc()
	# first patam
	dt_1_native = None
	if dt_1 is not None:
		if dt_1.tzinfo is not None:
			dt_1_native = dt_1.astimezone(tz_utc).replace(tzinfo=None)
		else:
			dt_1_native = dt_1
		# second param
	dt_2_native = None
	if dt_2 is not None:
		if dt_2.tzinfo is not None:
			dt_2_native = dt_2.astimezone(tz_utc).replace(tzinfo=None)
		else:
			dt_2_native = dt_2
		# smaller returns -1
	if dt_1_native < dt_2_native:
		return -1
		# bigger returns 1
	if dt_1_native > dt_2_native:
		return 1
		# same returns 0
	return 0

def isBiggerDate(dt_1, dt_2):
	if compareDatetime(dt_1, dt_2) > 0:
		return True
	return False

def getUserNameSSOGadget(google_apps_domain, app_id, viewer_email, split_name=False):
	""" Get user list data from SSOGadget
				"""
	family_name = ''
	given_name = ''
	old_namespace = namespace_manager.get_namespace()
	setNamespace(google_apps_domain, app_id)
	user_rec = sateraito_db.UserInfo.getInstance(str(viewer_email).lower())
	if user_rec is not None:
		family_name = user_rec.family_name
		given_name = user_rec.given_name

	namespace_manager.set_namespace(old_namespace)
	if split_name:
		return family_name, given_name

	return family_name + given_name

def getUserNameSSiteGadget(google_apps_domain, viewer_email, split_name=False):
	family_name = ''
	given_name = ''

	service, access_token = getAccessTokenSSite(google_apps_domain, viewer_email)
	if access_token and service is not None:
		user = service.getUser(access_token, viewer_email)
		if user is not None:
			family_name = user['name']['familyName']
			given_name = user['name']['givenName']
		else:
			family_name = viewer_email.split('@')[0]
			given_name = ''

	if split_name:
		return family_name, given_name

	return family_name + given_name


def getListFolderCodeChild(folder_code, viewer_email, user_accessible_info=None, admin_mode=False):
	if user_accessible_info is None:
		user_accessible_info = sateraito_db.UserAccessibleInfo.getDict(viewer_email, auto_create=True)
	
	list_folder_code = []
	q = sateraito_db.DocFolder.query()
	q = q.filter(sateraito_db.DocFolder.del_flag == False)
	q = q.filter(sateraito_db.DocFolder.parent_folder_code == str(folder_code))

	for row in q:
		if not admin_mode:
			if not sateraito_db.DocFolder.isAccessibleFolder(row.folder_code, user_accessible_info):
				continue

		child_more = getListFolderCodeChild(row.folder_code, viewer_email=viewer_email, user_accessible_info=user_accessible_info, admin_mode=admin_mode)
		child_more.append(row.folder_code)
		list_folder_code.extend(child_more)

	return list_folder_code

def getListFolderNosChild(folder_code, viewer_email, user_accessible_info=None, admin_mode=False):
	if user_accessible_info is None:
		user_accessible_info = sateraito_db.UserAccessibleInfo.getDict(viewer_email, auto_create=True)

	list_folder_nos = []
	q = sateraito_db.DocFolder.query()
	q = q.filter(sateraito_db.DocFolder.del_flag == False)
	q = q.filter(sateraito_db.DocFolder.parent_folder_code == str(folder_code))

	for row in q:
		if not admin_mode:
			if not sateraito_db.DocFolder.isAccessibleFolder(row.folder_code, user_accessible_info):
				continue

		child_more = getListFolderNosChild(row.folder_code, viewer_email=viewer_email, user_accessible_info=user_accessible_info, admin_mode=admin_mode)
		child_more.append(row.folder_no)
		list_folder_nos.extend(child_more)

	return list_folder_nos

def getSettingAttachViewerType(tenant_or_domain, domain_dict=None):

	attached_file_viewer_type = 'GOOGLEDRIVEVIEWER'
	is_preview = True
	if domain_dict is None:
		domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(tenant_or_domain)

	if 'is_preview' in domain_dict:
		if domain_dict['is_preview'] is not None:
			is_preview = domain_dict['is_preview']
			attached_file_viewer_type = domain_dict['attached_file_viewer_type']

	return is_preview, attached_file_viewer_type

# todo: edited start: tan@vn.sateraito.co.jp (version: 3)
def checkOpenAsGoogleDocViewer(google_apps_domain, mime_type):
	# Supported file types
	# These are the most common file types that you can view in Google Drive.
	# .txt	text/plain
	# .doc	application/msword
	# .docx 	application/vnd.openxmlformats-officedocument.wordprocessingml.document
	# .xls	application/vnd.ms-excel
	# .xlsx	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
	# .ppt	application/vnd.ms-powerpoint
	# .pptx	application/vnd.openxmlformats-officedocument.presentationml.presentation
	# .pdf 	application/pdf
	# .css	text/css
	# .html	text/html
	# .js	application/javascript

	# Officeビューアー対応

	# if other_setting is not None:
	domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
	attached_file_viewer_type = 'GOOGLEDRIVEVIEWER'
	if 'attached_file_viewer_type' in domain_dict:
		attached_file_viewer_type = domain_dict['attached_file_viewer_type']

	if attached_file_viewer_type == 'OFFICEVIEWER':
		# Office系ファイルのみ対応しているのでtxt系、pdfは除外
		# TXT系→ブラウザ自体で表示、PDF→PDFJSで表示（画像系はもともとブラウザで表示）
		arrMimeTypeIsOk = [
			'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
			'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
			'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
		]
	else:
		arrMimeTypeIsOk = [
			'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
			'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
			'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
			'text/plain', 'application/pdf', 'text/css', 'text/html', 'application/javascript',
		]

	if mime_type in arrMimeTypeIsOk:
		return True
	return False

def jsonEncodeToUtf8str(objTarget):
	value = json.JSONEncoder(ensure_ascii=False).encode(objTarget)
	return value

def isOauth2Domain(google_apps_domain):
	return True

def isValidMasterCode(master_code):
	return isValidDocTypeCode(master_code)

def isValidDocTypeCode(doc_type_code):
	# doc_type_code must
	#  contain only alphabet, numeric and _ and - and . character
	logging.info('isValidDocTypeCode doc_type_code=' + str(doc_type_code))
	regexp = re.compile('^[0-9A-Za-z_\-\.]+$')
	if regexp.search(doc_type_code) is None:
		# doc_type_code have prohibited character
		logging.info('not matched')
		return False
	return True

def isUseClientMasterDef(tenant_or_domain, app_id):
	return sateraito_db.MasterDef.loadMasterDefAppId(CLIENT_INFO_MASTER_CODE, tenant_or_domain, app_id) is not None

def createSearchMasterData(master_data_row):
	return sateraito_search.create_search_master_data(master_data_row)

def removeMasterDataFromIndex(master_key):
	sateraito_search.remove_master_data_from_index(master_key)

def addMasterDataToTextSearchIndex(master_data_row, num_retry=0):
	sateraito_search.add_master_data_to_text_search_index(master_data_row, num_retry=0)

def removeAllMasterDataWithMasterCode(master_code):
	return sateraito_search.remove_all_master_data_with_master_code(master_code)

def callTaskUpdateClientForDoc(google_apps_domain, app_id, client_id):
	logging.info('callTaskUpdateClientForDoc')
	# add queue to extract accessible_members
	que = taskqueue.Queue('default')
	task = taskqueue.Task(url='/' + google_apps_domain + '/' + app_id + '/workflowdoc/tq/updateclient',
							params={
								'client_id': client_id
							},
							target=getBackEndsModuleNameDeveloper('default'),
							)
	que.add(task)

def callTaskUpdateClientDataMasterForDoc(google_apps_domain, app_id, client_id):
	# add queue to extract accessible_members
	que = taskqueue.Queue('default')
	task = taskqueue.Task(url='/' + google_apps_domain + '/' + app_id + '/workflowdoc/tq/updateclientdatamaster',
							params={
								'client_id': client_id
							},
							target=getBackEndsModuleNameDeveloper('default')
							)
	que.add(task)

def getCurrencyMasterDef(viewer_email):
	master_datas = []
	master_code = CURRENCY_MASTER_CODE

	md_row = sateraito_db.MasterDef.getInstance(master_code)
	if md_row is not None:
		q = sateraito_db.MasterData.query()
		q = q.filter(sateraito_db.MasterData.master_code == master_code)
		rows = q.fetch()

		for row in rows:
			row_dict = row.to_dict()
			master_datas.append(noneToZeroStr(row.attribute_1))

	if len(master_datas) == 0:
		user_language = sateraito_db.UserInfo.getUserLanguage(viewer_email, hl=sateraito_inc.DEFAULT_LANGUAGE)
		if user_language in ['en', 'en-gb', 'en_GB']:
			master_datas = LIST_CURRENCY_DEFAULT_EN
		else:
			master_datas = LIST_CURRENCY_DEFAULT_JA

	return master_datas

def getCurrencyDoc(doc_dict, viewer_email=None, data_currency=None):

	if data_currency is None:
		data_currency = getCurrencyMasterDef(viewer_email)

	if 'currency' not in doc_dict:
		return data_currency[0]
	elif doc_dict['currency'] is None:
		return data_currency[0]

	return doc_dict['currency']

def getListAppsDomain(google_apps_domain, domain_dict=None):
	list_google_apps_domain = []

	if domain_dict is None:
		domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)

	if domain_dict['multi_domain_setting']:
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)

		q = sateraito_db.GoogleAppsDomainEntry.query()
		for row in q:
			if row.google_apps_domain and row.google_apps_domain != '':
				list_google_apps_domain.append(row.google_apps_domain)

		namespace_manager.set_namespace(old_namespace)
	else:
		list_google_apps_domain.append(domain_dict['google_apps_domain'])

	return list_google_apps_domain

# check without ndb.UserAccessibleInfo
def isAccessibleParentFolder(folder_code_check, joining_groups=None):
	if folder_code_check == '__root':
		return True

	if joining_groups is None:
		joining_groups = []

	folder_dict = sateraito_db.DocFolder.getDict(folder_code_check)

	if folder_dict is None:
		return False

	elif ('*' in folder_dict['accessible_users']):
		if folder_dict['parent_folder_code'] and (folder_dict['parent_folder_code'] != '__root'):
			# call func recursion to check accessible folder parent if folder check
			return isAccessibleParentFolder(folder_dict['parent_folder_code'], joining_groups)
		else:
			return True
	else:
		for email in folder_dict['accessible_users']:
			if email in joining_groups:
				return True

	return False

# check without ndb.UserAccessibleInfo
def isCreatableParentFolder(folder_code_check, joining_groups=None):
	if folder_code_check == '__root':
		return False

	if joining_groups is None:
		joining_groups = []

	folder_dict = sateraito_db.DocFolder.getDict(folder_code_check)

	if folder_dict is None:
		return False

	elif folder_dict['creatable_same_accessible']:
		if isAccessibleParentFolder(folder_code_check, joining_groups):
			# OK!
			return True
		else:
			return False

	elif ('*' in folder_dict['creatable_users']):
		if folder_dict['parent_folder_code'] and (folder_dict['parent_folder_code'] != '__root'):
			# call func recursion to check accessible folder parent if folder check
			return isCreatableParentFolder(folder_dict['parent_folder_code'], joining_groups)
		else:
			return True

	else:
		for email in folder_dict['creatable_users']:
			if email in joining_groups:
				return True

	return False

# check without ndb.UserAccessibleInfo
def isDownloadableParentFolder(folder_code_check, joining_groups=None):
	if folder_code_check == '__root':
		return False

	if joining_groups is None:
		joining_groups = []

	folder_dict = sateraito_db.DocFolder.getDict(folder_code_check)

	if folder_dict is None:
		return False

	elif folder_dict['downloadable_same_accessible']:
		if isAccessibleParentFolder(folder_code_check, joining_groups):
			# OK!
			return True
		else:
			return False

	elif ('*' in folder_dict['downloadable_users']):
		if folder_dict['parent_folder_code'] and (folder_dict['parent_folder_code'] != '__root'):
			# call func recursion to check accessible folder parent if folder check
			return isDownloadableParentFolder(folder_dict['parent_folder_code'], joining_groups)
		else:
			return True

	else:
		for email in folder_dict['downloadable_users']:
			if email in joining_groups:
				return True

	return False

# check without ndb.UserAccessibleInfo
def isDeletableParentFolder(folder_code_check, joining_groups=None):
	if folder_code_check == '__root':
		return False

	if joining_groups is None:
		joining_groups = []

	folder_dict = sateraito_db.DocFolder.getDict(folder_code_check)

	if folder_dict is None:
		return False

	elif folder_dict['deletable_admin_only']:
		return False

	elif ('*' in folder_dict['deletable_users']):
		if folder_dict['parent_folder_code'] and (folder_dict['parent_folder_code'] != '__root'):
			# call func recursion to check accessible folder parent if folder check
			return isDeletableParentFolder(folder_dict['parent_folder_code'], joining_groups)
		else:
			return True

	else:
		for email in folder_dict['deletable_users']:
			if email in joining_groups:
				return True

	return False

# check without ndb.UserAccessibleInfo
def isSubFolderCreatableParentFolder(folder_code_check, joining_groups=None):
	if folder_code_check == '__root':
		return False

	if joining_groups is None:
		joining_groups = []

	folder_dict = sateraito_db.DocFolder.getDict(folder_code_check)

	if folder_dict is None:
		return False

	elif folder_dict['subfolder_creatable_admin_only']:
		return False

	elif ('*' in folder_dict['subfolder_creatable_users']):
		if folder_dict['parent_folder_code'] and (folder_dict['parent_folder_code'] != '__root'):
			# call func recursion to check accessible folder parent if folder check
			return isSubFolderCreatableParentFolder(folder_dict['parent_folder_code'], joining_groups)
		else:
			return True

	else:
		for email in folder_dict['subfolder_creatable_users']:
			if email in joining_groups:
				return True

	return False

# GAEGEN2対応
# ビューメソッド（get, post など）戻り値が None のときに b'' に変換するデコレーター
def convert_result_none_to_empty_str(func):
	@wraps(func)
	def _wrapper(*args, **keywords):
		oResult = func(*args, **keywords)
		if (oResult is None):
			oResult = b''
		return oResult

	return _wrapper

def removeItemFromQueryString(query_string, item):
	if query_string is None or query_string == '':
		return query_string

	# decode if string binary
	if isinstance(query_string, bytes):
		query_string = query_string.decode('ascii')
	splited = str(query_string).split('&')
	while item in splited:
		splited.remove(item)
	return '&'.join(splited)

def removeOEqualKm(query_string):
	return removeItemFromQueryString(query_string, 'o=km')

def removeItemIfValueInList(list_check, value_check=''):
	list_return = []
	for item in list_check:
		item = item.strip()
		if item != value_check:
			list_return.append(item)

	return list_return

def isUserCanDeleteWorkflowDoc(tenant_or_domain, app_id, user_email, doc_id, folder_id, doc_dict=None, folder_dict=None, user_accessible_info_dict=None):

	if doc_dict is None:
		doc_dict = sateraito_db.WorkflowDoc.getDict(doc_id)
	if folder_dict is None:
		folder_dict = sateraito_db.DocFolder.getDict(folder_id)
	if not doc_dict or not folder_dict:
		return False

	# Check if user_email can delete doc with other settings
	old_namspace = namespace_manager.get_namespace()
	setNamespace(tenant_or_domain, app_id)
	other_setting = sateraito_db.OtherSetting.getDict(auto_create=True)
	namespace_manager.set_namespace(old_namspace)

	# check.1 is can edit doc setting on
	if not other_setting['user_can_delete_doc']:
		return False
	if len(other_setting['users_groups_can_delete_doc']) == 0:  # only user create doc can delete doc
		return doc_dict['author_email'] == user_email

	# check.2 is user is member of allowed group member
	set1 = set(other_setting['users_groups_can_delete_doc'])

	deletable_by_other_setting = False
	user_dict = sateraito_db.GoogleAppsUserEntry.getDict(tenant_or_domain, user_email)
	set2 = set(user_dict['google_apps_groups'])
	set2.add(user_email)
	if len(set1 & set2) > 0:
		deletable_by_other_setting = True
	logging.info('deletable_by_other_setting=' + str(deletable_by_other_setting))

	if user_accessible_info_dict is None:
		user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(user_email, auto_create=True)
		if user_accessible_info_dict is None:
			return False

	# Check if user_email can delete doc with folder setting
	deletable_by_folder_setting = sateraito_db.DocFolder.isDeletableFolder(folder_id, user_accessible_info_dict, tenant_or_domain)
	logging.info('deletable_by_folder_setting=' + str(deletable_by_folder_setting))

	return deletable_by_other_setting and deletable_by_folder_setting

def complete_full_url(url):
	'''
	Complete full URL by adding "http://" and "www" if scheme is missing.
	Example:
	- sateraito.jp -> http://www.sateraito.jp
	'''
	if url is None or url == '':
		return url

	if not (url.startswith('http://') or url.startswith('https://')):
		url = 'http://' + url
		if not url.startswith('http://www.') and not url.startswith('https://www.'):
			url = url.replace('http://', 'http://www.', 1)
			url = url.replace('https://', 'https://www.', 1)
	return url

def format_date(date, format_str='%Y/%m/%d'):
	if date is None:
		return ''
	try:
		return date.strftime(format_str)
	except Exception as e:
		logging.warning('e:' + str(e))
		return ''

def is_valid_unique_id(unique_id):
	# unique_id must
	#  contain only alphabet, numeric and _ and - and . character
	logging.info('is_valid_unique_id unique_id=' + str(unique_id))
	regexp = re.compile('^[0-9A-Za-z_\-\.]+$')
	if regexp.search(unique_id) is None:
		# unique_id have prohibited character
		logging.info('not matched')
		return False
	return True

def is_valid_stream_path(stream_path):
	# stream_path must
	#  contain only alphabet, numeric and _ and - and . and / character
	logging.info('is_valid_stream_path stream_path=' + str(stream_path))
	regexp = re.compile('^[0-9A-Za-z_\-\.\/]+$')
	if regexp.search(stream_path) is None:
		# stream_path have prohibited character
		logging.info('not matched')
		return False
	return True

def get_current_timestamp_ms():
	return int(datetime.datetime.now().timestamp() * 1000)

def convert_path_real_time_firebase_database(path):
	# Paths must be non-empty strings and can't contain ".", "#", "$", "[", or "]"
	if not path or not isinstance(path, str):
		return ''

	# "." -> "dot"
	new_path = path.replace('.', '_dot_')
	# "#" -> "hash"
	new_path = new_path.replace('#', '_hash_')
	# "$" -> "dollar"
	new_path = new_path.replace('$', '_dollar_')
	# "[" -> "leftb"
	new_path = new_path.replace('[', '_leftb_')
	# "]" -> "rightb"
	new_path = new_path.replace(']', '_rightb_')

	# Prefix with NAME_PATH_FIREBASE_REALTIME_DATABASE
	if sateraito_inc.NAME_PATH_FIREBASE_REALTIME_DATABASE:
		new_path = f'{sateraito_inc.NAME_PATH_FIREBASE_REALTIME_DATABASE}/{new_path}'

	return new_path

class MyLang:

	root_node = None

	def __init__(self, language):
		file_name = getLangFileName(language)
		folder_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'params'))
		xml_file_name = os.path.normpath(os.path.join(folder_path, 'lang', file_name))
		self.root_node = UcfXml.load(xml_file_name)

	def getMsgs(self):
		if self.root_node is None:
			return {}
		nodes = self.root_node.selectNodes('msg')
		dict = {}
		for node in nodes:
			name = node.getAttribute('name')
			message = node.getInnerText()
			if name is not None and name != '':
				dict[name] = message
		return dict

	def getMsg(self, code):
		if self.root_node is None:
			return ''
		node = self.root_node.selectSingleNode('msg[@name="' + code + '"]')
		message = ''
		if node is not None:
			message = node.getInnerText()
		return message

class ImpersonateMailException(Exception):
	def __init__(self):
		pass

class NotInstalledException(Exception):
	""" exception: this application is not installed to the domain
"""

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return str(self.value)

class Error(Exception):
	def __str__(self):
		return "Error: %s" % self.__doc__

class OAuth2JWTError(Error):
	"""Raised when an OAuth2 error occurs."""
	def __init__(self, error_message):
		self.error_message = error_message

class TransientError(Exception):
	def __init__(self):
		pass

class CheckIpAddressAccess():
	def run(self, request, accept_ip_address_list):
		# accept_ip_address_list = ['2001:DB8:0:0:8:800:200C:417A', '127.0.0.1/32']
		deny_ip_address_list = []
		logging.info('self.getClientIPAddress()')
		logging.info(self.getClientIPAddress(request))
		logging.info(accept_ip_address_list)
		if not self.isCheckIPAddressRange(self.getClientIPAddress(request), accept_ip_address_list, deny_ip_address_list):
			# self.response.out.write('NG')
			# self.response.set_status(403)
			return False

		# self.response.out.write('OK')
		return True

	# クライアントのIPアドレスを取得
	def getClientIPAddress(self, request):
		client_ip = None

		if self.isViaSateraitoReverseProxyServer():
			# 中国アクセス対策：リバースプロキシサーバーからのアクセスの場合はX-Forwarded-Forに本来のクライアントIPが入っているはずなのでそれを通常のクライアントIPアドレスとして扱う 2018/06/12
			xffip = UcfUtil.getHashStr(os.environ, 'HTTP_X_FORWARDED_FOR')
			# 取得できたら
			if xffip != '':
				# 末尾のIPアドレスを使用（末尾がリバースプロキシサーバーの直前のIPアドレスなので）
				if xffip.find(',') >= 0:
					ip_ary = xffip.split(',')
					xffip = ip_ary[len(ip_ary) - 1]
					xffip = xffip.strip()
			if xffip != '':
				client_ip = xffip
		else:
			# normal case forward check
			logging.info('headers=' + str(request.headers))
			if 'X-Forwarded-For' in request.headers:
				x_forwarded_for = request.headers['X-Forwarded-For']
				if x_forwarded_for:
					x_forwarded_for_array = x_forwarded_for.split(',')
					client_ip = x_forwarded_for_array[0]
					# ip v6 correspondence
					if len(client_ip) > 7:
						if client_ip[:7] == '::ffff:' or client_ip[:7] == '::FFFF:':
							client_ip = client_ip[7:]
					logging.info('client_ip=' + client_ip)

		if client_ip is None:
			return os.environ.get('REMOTE_ADDR', '')
		else:
			return client_ip

	def getRemoteAddress(self, request):
		return os.environ.get('REMOTE_ADDR', '')

	def getXForwardedFor(self, request):
		x_forwarded_for = None
		if 'X-Forwarded-For' in request.headers:
			x_forwarded_for = request.headers['X-Forwarded-For']
			if str(x_forwarded_for).strip() == '':
				x_forwarded_for = None
		return x_forwarded_for

	# 中国アクセス対策：リバースプロキシサーバーからのアクセスかどうかを判定 2018/06/12
	def isViaSateraitoReverseProxyServer(self):
		# TODO 本当はREMOTE_ADDR がメールプロキシサーバーのIPかも見て判断すべき... だが、IP増えたり変わったりすると面倒なので...
		return UcfUtil.getHashStr(os.environ, 'HTTP_X_UCF_PROXY') in ['NEXTSETADDONPROXY', 'SATERAITOADDONPROXY']

	def isCheckIPAddressRange(self, ip, checkiplist, denyiplist=None):
		u'''
		TITLE:指定IPアドレスが対象範囲に入っているかを判定
		PARAMETER:
			ip:チェックするIPアドレス…IPv4形式（例：127.0.0.1）
			checkiplist:対象範囲とするIPアドレス一覧…（127.0.0.1、127.0.0.1/32 ）などの一覧
			※checkiplistが空なら判定はFalse
			denyiplist:対象範囲外とするIPアドレス一覧…（127.0.0.1、127.0.0.1/32 ）などの一覧　（denyが優先）

		'''
		is_in_range = False
		is_in_denyrange = False
		ip_cidr = IPy.IP(ip)

		# 拒否IPリストをまずチェック
		if denyiplist is not None:
			if isinstance(denyiplist, str):
				denyiplist = (denyiplist, '')
			ipranges = []
			for checkip in denyiplist:
				if checkip and checkip != '':
					# 0.0.0.0/0 とかだと、IPyがエラーするので、しょうがなく個別対応
					if self.startsWith(checkip, '0.0.0.0/') or checkip == '0.0.0.0' or self.startsWith(checkip,
																																														 '000.000.000.000/') or checkip == '000.000.000.000':
						is_in_denyrange = True
						break
					else:
						try:
							ipranges.append(IPy.IP(checkip))
						except Exception as e:
							logging.error('No use "' + checkip + '" because of invalid iprange!')
							logging.error(str(e))

			if is_in_denyrange == False:
				# CIDRで範囲指定されたIP群の中に含まれているかを判断します
				for iprange in ipranges:
					if ip_cidr in iprange:
						is_in_denyrange = True
						break

		if not is_in_denyrange:  # 拒否リストにいなければ許可リストをチェック
			if checkiplist is not None:
				if isinstance(checkiplist, str):
					checkiplist = (checkiplist, '')
				ipranges = []
				for checkip in checkiplist:
					if checkip and checkip != '':
						# 0.0.0.0/0 とかだと、IPyがエラーするので、しょうがなく個別対応
						if self.startsWith(checkip, '0.0.0.0/') or checkip == '0.0.0.0' or self.startsWith(checkip,
																																															 '000.000.000.000/') or checkip == '000.000.000.000':
							logging.info('is_in_range:' + checkip)
							is_in_range = True
							break
						else:
							try:
								ipranges.append(IPy.IP(checkip))
							except Exception as e:
								logging.error('No use "' + checkip + '" because of invalid iprange!')
								logging.error(str(e))

				if is_in_range == False:
					# CIDRで範囲指定されたIP群の中に含まれているかを判断します
					for iprange in ipranges:
						if ip_cidr in iprange:
							is_in_range = True
							break

		return is_in_range

	# +++++++++++++++++++++++++++++++++++++++++
	# 文字列が指定文字列から始まるかどうか
	# +++++++++++++++++++++++++++++++++++++++++
	def startsWith(self, str_data, check_str):
		is_start = False
		if str_data is not None and str_data != '' and check_str is not None and check_str != '':
			if len(str_data) >= len(check_str):
				start_str = str_data[0:len(check_str)]
				if start_str == check_str:
					is_start = True
		return is_start

class OpenSocialInfo():
	"""  Class to save/load opensocial viewer id and opensocial container information
	The key of db is token
	"""
	container = None
	viewer_id = None

	def loadInfo(self, token):
		""" Load opensocial info by token from memcache
				"""
		strOldNamespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace('')
		try:
			logging.info('loadInfo:token=' + token)
			opensocial_info = memcache.get('checkuserpage?token=' + token)
			# fix google login select_account - edited by tan@vn.sateraito.co.jp 2021-03-12
			if opensocial_info is not None:
				opensocial_info_splited = opensocial_info.split('|')
				self.container = opensocial_info_splited[0]
				self.viewer_id = opensocial_info_splited[1]
			else:
				self.container = None
				self.viewer_id = None
			namespace_manager.set_namespace(strOldNamespace)
			return True
		except Exception as error:
			namespace_manager.set_namespace(strOldNamespace)
			raise error

	def saveInfo(self, token, opensocial_container, opensocial_viewer_id):
		""" Save opensocial information to memcache
				This information expires in an hour
				"""
		strOldNamespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace('')
		try:
			logging.info('saveInfo:token=' + token)
			memcache_set_value = opensocial_container + '|' + opensocial_viewer_id
			if not memcache.set(key='checkuserpage?token=' + token + '&g=2', value=memcache_set_value, time=(60 * 60)):
				logging.warning("Memcache set failed.")
				return False
			namespace_manager.set_namespace(strOldNamespace)
			return True
		except Exception as error:
			namespace_manager.set_namespace(strOldNamespace)
			raise error

class RequestChecker():
	""" Check user request which is sent by gadget container(Signed request)
	"""

	viewer_email = ''
	viewer_user_id = ''
	is_admin = None
	disable_user = None
	google_apps_domain = None
	opensocial_viewer_id = None
	opensocial_container = None
	google_apps_domain_from_gadget_url = None
	timezone_name = None

	def checkContainerSign(self, request, check_user_db=True):
		"""
		check signed request
		Args:
			request: http request object
			chech_user_db: If this is True, check if opensocial id is registered in Datastore.
				If not found in Datastore, returns False.
		Returns:
			True ... Request has no problem
			False .. Request has security issue
		"""
		opensocial_owner_id = request.get('opensocial_owner_id')
		self.opensocial_viewer_id = request.get('opensocial_viewer_id')
		opensocial_app_id = request.get('opensocial_app_id')
		opensocial_app_url = request.get('opensocial_app_url')
		xoauth_signature_publickey = request.get('xoauth_signature_publickey')
		xoauth_public_key = request.get('xoauth_public_key')
		oauth_version = request.get('oauth_version')
		oauth_timestamp = request.get('oauth_timestamp')
		oauth_nonce = request.get('oauth_nonce')
		self.opensocial_container = request.get('opensocial_container')
		oauth_consumer_key = request.get('oauth_consumer_key')
		oauth_signature_method = request.get('oauth_signature_method')
		oauth_signature = request.get('oauth_signature')
#    logging.info('query param opensocial_owner_id=' + opensocial_owner_id
#                  + ' opensocial_viewer_id=' + self.opensocial_viewer_id
#                  + ' opensocial_app_id=' + opensocial_app_id
#                  + ' opensocial_app_url=' + opensocial_app_url
#                  + ' xoauth_signature_publickey=' + xoauth_signature_publickey
#                  + ' xoauth_public_key=' + xoauth_public_key
#                  + ' oauth_version=' + oauth_version
#                  + ' oauth_timestamp=' + oauth_timestamp
#                  + ' oauth_nonce=' + oauth_nonce
#                  + ' opensocial_container=' + self.opensocial_container
#                  + ' oauth_consumer_key=' + oauth_consumer_key
#                  + ' oauth_signature_method=' + oauth_signature_method
#                  + ' oauth_signature=' + oauth_signature)
		logging.info('query param opensocial_owner_id=%s opensocial_viewer_id=%s opensocial_app_id=%s opensocial_app_url=%s xoauth_signature_publickey=%s xoauth_public_key=%s oauth_version=%s oauth_timestamp=%s oauth_nonce=%s opensocial_container=%s oauth_consumer_key=%s oauth_signature_method=%s oauth_signature=%s'
					 % (opensocial_owner_id, self.opensocial_viewer_id, opensocial_app_id, opensocial_app_url, xoauth_signature_publickey, xoauth_public_key, oauth_version, oauth_timestamp, oauth_nonce, self.opensocial_container, oauth_consumer_key, oauth_signature_method, oauth_signature))

		# check opensocial container
		# by checking this, request from other container refused
		#    if not(self.opensocial_container == 'http://www.google.com/ig' or self.opensocial_container == OPENSOCIAL_CONTAINER_GOOGLE_SITE):
		if not (self.opensocial_container == OPENSOCIAL_CONTAINER_GOOGLE_SITE):
			logging.error('Illegal opensocial_container:' + self.opensocial_container)
			return False

		# check oauth consumer key
		if oauth_consumer_key != 'www.google.com':
			logging.error('Illegal oauth_consumer_key:' + oauth_consumer_key)
			return False

		# check sign of this request
		# by checking sign, contents of this request is guaranteed by google
		sign_check_result = self.isValidSignature(request)
		if sign_check_result == False:
			logging.error('Illegal sign check failed')
			return False

		gadget_url_splited = opensocial_app_url.split('/')
		# opensocial_app_url --> starts with http NOT https
		# checking appspot domain
		if 'https://' + gadget_url_splited[2] != sateraito_inc.my_site_url:
			logging.error('Illegal opensocial_app_url:' + opensocial_app_url)
			return False
		self.google_apps_domain_from_gadget_url = gadget_url_splited[4]

		if check_user_db:
			# check opensocial viewer_id
			user_dict = sateraito_db.GoogleAppsUserEntry.getDictByOpensocialId(self.google_apps_domain_from_gadget_url, self.opensocial_viewer_id, self.opensocial_container)

			if user_dict is None:
				logging.error('opensocial_viewer_id:' + self.opensocial_viewer_id + ' not found')
				return False
			# user entry found in datastore
			self.viewer_email = user_dict['user_email']
			self.viewer_user_id = user_dict['user_id']
			logging.info('checked user db viewer email is:%s' % self.viewer_email)
			# set google_apps_domain from viewer_email
			self.google_apps_domain = getDomainPart(self.viewer_email)
			# ckeck opensocial app url
			# by checking this, request from other gadget is refused
			# and gurantee at least google_apps_domain of viewer email is correct
			gadget_names = GetGadgetNames()
			matched = False
			for gadget_name in gadget_names:
				# for multi domain
				#gadget_url = 'http://' + sateraito_inc.appspot_domain + '.appspot.com/gadget/' + self.google_apps_domain + '/' + gadget_name + '.xml'
				gadget_url = 'http://' + sateraito_inc.appspot_domain + '.appspot.com/gadget/' + self.google_apps_domain_from_gadget_url + '/' + gadget_name + '.xml'
				if opensocial_app_url[0:(len(gadget_url))] == gadget_url:
					matched = True
			if not matched:
				logging.error('Illegal opensocial_app_url:' + opensocial_app_url)
				return False
		return True

	def checkAppsAdmin(self, user_email, google_apps_domain):
		try:
			app_service = fetch_google_app_service(user_email, google_apps_domain)
			user_entry = app_service.users().get(userKey=user_email).execute()
			logging.info('user_entry:' + str(user_entry))
			if user_entry["isAdmin"] == 'true' or user_entry["isAdmin"] == 'True' or user_entry["isAdmin"] == True:
				return True
			return False
		except Exception as e:
			logging.error('error: class name:' + e.__class__.__name__ + ' message=' + str(e))
			raise NotInstalledException('not installed to the domain')

	def putNewUserEntry(self, user_email, google_apps_domain, target_google_apps_domain, opensocial_viewer_id,
											opensocial_container, user_id, is_admin=False):
		""" Add new user entry """
		old_namespace = namespace_manager.get_namespace()
		namespace_manager.set_namespace(google_apps_domain)

		# check if same entry already registered
		q = sateraito_db.GoogleAppsUserEntry.query()
		q = q.filter(sateraito_db.GoogleAppsUserEntry.opensocial_viewer_id == opensocial_viewer_id)
		q = q.filter(sateraito_db.GoogleAppsUserEntry.opensocial_container == opensocial_container)
		q = q.filter(sateraito_db.GoogleAppsUserEntry.user_email == str(user_email).lower())
		row = q.get()
		if row is not None:
			# same entry already registered
			# self.is_admin = row.is_apps_admin
			namespace_manager.set_namespace(old_namespace)
			return row

		if not is_admin:
			try:
				# check if current user is google apps admin user
				app_service = fetch_google_app_service(user_email, google_apps_domain)
				user_entry = app_service.users().get(userKey=user_email).execute()
				is_current_user_admin = False
				self.is_admin = False
				if user_entry["isAdmin"] == 'true' or user_entry["isAdmin"] == 'True' or user_entry["isAdmin"] == True:
					is_current_user_admin = True
					self.is_admin = True
			except Exception as e:
				namespace_manager.set_namespace(old_namespace)
				is_current_user_admin = False
				self.is_admin = False
		else:
			is_current_user_admin = is_admin
			self.is_admin = is_admin


		# check if email and opensocial_container and opensocial_id='__not_set'
		query = sateraito_db.GoogleAppsUserEntry.query()
		query = query.filter(sateraito_db.GoogleAppsUserEntry.opensocial_viewer_id == '__not_set')
		query = query.filter(sateraito_db.GoogleAppsUserEntry.user_email == str(user_email).lower())
		query = query.filter(sateraito_db.GoogleAppsUserEntry.opensocial_container == opensocial_container)
		user_entry_by_mail = query.get()

		if user_entry_by_mail is None:
			# Normal pattern: Add new entry to datastore
			# register new user entry to datastore
			user_email_lower = str(user_email).lower()
			new_user_entry = sateraito_db.GoogleAppsUserEntry(id=user_email_lower)
			new_user_entry.user_id = user_id
			new_user_entry.user_email = user_email_lower
			new_user_entry.google_apps_domain = google_apps_domain
			new_user_entry.opensocial_viewer_id = opensocial_viewer_id
			new_user_entry.opensocial_container = opensocial_container
			new_user_entry.disable_user = False
#      new_user_entry.timezone_name = 'Asia/Tokyo'  # default user timezone
			if is_current_user_admin:
				logging.info('curent user is admin')
				new_user_entry.is_apps_admin = True
			else:
				logging.info('curent user is not admin')
				new_user_entry.is_apps_admin = False
			new_user_entry.put()
			namespace_manager.set_namespace(old_namespace)
			return new_user_entry
		else:
			# Exceptional Pattern:
			# user entry (email=user_email, opensocual_viewer_id='__not_set', opensocial_container=opensocial_container) is already registered
			# If system admin want to disable the user which have the email,
			# he puts such datastore entry with disable_user = True
			# so just update opensocial_viewer_id is needed here
			user_entry_by_mail.user_id = user_id
			if is_current_user_admin:
				logging.info('curent user is admin')
				user_entry_by_mail.is_apps_admin = True
			else:
				logging.info('curent user is not admin')
				user_entry_by_mail.is_apps_admin = False
			user_entry_by_mail.opensocial_viewer_id = opensocial_viewer_id
			user_entry_by_mail.put()
			namespace_manager.set_namespace(old_namespace)
			return user_entry_by_mail

	def isValidSignature(self, request):
		# """ Check request signature using Google public key """
		# # Construct a RSA.pubkey object
		# exponent = 65537
		# #
		# # below is iGoogle public key Hex Value
		# #
		# # https://opensocialresources.appspot.com/certificates/#container4
		# #
		# # this is actually Google-wide RSA public key as mentioned at
		# # http://www.google.com/support/forum/p/apps-apis/thread?tid=3a8a43555c719695&hl=en
		# #
		# # Basic opensocial sign checking code for python
		# # http://wiki.opensocial.org/index.php?title=Building_an_OpenSocial_App_with_Google_App_Engine#Sending_and_verifying_signed_requests
		# #
		# public_key_str = """0xd0515eee9087c88b16e890738d18c5bdf9e77413d5f89bdf48f2ea4f429de202da88bd6b3b5c26c06c6ab3407d6a5fd634d21ad0e514508fc388ded46242cfca7f319639dbcba48939a17a5d4f9f2d838165621e5f6e1228568567e06bed4a32a6245b2833c351b442472f569677ef9d5f39108c4b0d7015f042f7c36f46276dL"""
		# public_key_long = long(public_key_str, 16)
		# public_key = RSA.construct((public_key_long, exponent))

		# # Rebuild the message hash locally
		# oauth_request = oauth.OAuthRequest(http_method=request.method,
		# 								http_url=request.url,
		# 								parameters=request.params.mixed())
		# message = '&'.join((oauth.escape(oauth_request.get_normalized_http_method()),
		# 								oauth.escape(oauth_request.get_normalized_http_url()),
		# 								oauth.escape(oauth_request.get_normalized_parameters()),))
		# local_hash = hashlib.sha1(message).digest()

		# # Apply the public key to the signature from the remote host
		# sig = urllib.unquote(request.params.mixed()["oauth_signature"]).decode('base64')
		# remote_hash = public_key.encrypt(sig, '')[0][-20:]

		# # Verify that the locally-built value matches the value from the remote server.
		# return local_hash==remote_hash
		return True

	# SSITE、SSOGadget対応：O365版から流用
	def registOrUpdateUserEntry(self, tenant_or_domain, user_email, target_domain, opensocial_viewer_id,
															opensocial_container, user_id, is_admin, family_name='', given_name=''):
		''' Add new user entry '''

		old_namespace = namespace_manager.get_namespace()
		setNamespace(tenant_or_domain, '')

		self.is_admin = is_admin

		# check if same entry already registered
		q = sateraito_db.GoogleAppsUserEntry.query()
		q = q.filter(sateraito_db.GoogleAppsUserEntry.opensocial_viewer_id == opensocial_viewer_id)
		q = q.filter(sateraito_db.GoogleAppsUserEntry.opensocial_container == opensocial_container)

		user_entry = None
		for key in q.iter(keys_only=True):
			entry = key.get()
			if entry is None:
				continue
			# 別のアドレスのレコードがあれば削除
			if entry.user_email.lower() != user_email.lower():
				entry.delete()
			# 既に該当レコードがある場合はその他のレコードは削除
			elif user_entry is not None:
				entry.delete()
			else:
				user_entry = entry

		# if user_entry is None:
		#  # check if email and opensocial_container and opensocial_id='__not_set'
		#  q = sateraito_db.UserEntry.gql("where opensocial_viewer_id = '__not_set' and user_email = :1 and opensocial_container = :2", user_email, opensocial_container)
		#  user_entry = q.get()

		if user_entry is None:
			memcache_expire_secs = 5
			memcache_key = 'script=regist_or_update_user_entry&opensocial_viewer_id=' + opensocial_viewer_id.lower() + '&opensocial_container=' + opensocial_container.lower() + '&user_email=' + user_email.lower() + '&g=2'
			is_processing = memcache.get(memcache_key)
			if is_processing is not None:
				logging.info('registOrUpdateUserEntry processing...')
				return ''

			if not memcache.set(memcache_key, value=True, time=memcache_expire_secs):
				logging.warning("Memcache set failed.")

			# 重複防止のためキーをuser_idにしてみる...
			# user_entry = sateraito_db.GoogleAppsUserEntry()
			# user_entry = sateraito_db.GoogleAppsUserEntry(key_name=user_id.lower())
			user_entry = sateraito_db.GoogleAppsUserEntry(id=user_id.lower())
			user_entry.user_id = user_id
			user_entry.user_email = user_email
			user_entry.google_apps_domain = target_domain
			user_entry.opensocial_viewer_id = opensocial_viewer_id
			user_entry.opensocial_container = opensocial_container
			user_entry.disable_user = False
			if self.is_admin:
				logging.info('curent user is admin')
				user_entry.is_apps_admin = True
			else:
				logging.info('curent user is not admin')
				user_entry.is_apps_admin = False
		# user_entry.put()

		# Exceptional Pattern:
		# user entry (email=user_email, opensocual_viewer_id='__not_set', opensocial_container=opensocial_container) is already registered
		# If system admin want to disable the user which have the email,
		# he puts such datastore entry with disable_user = True
		# so just update opensocial_viewer_id is needed here
		# user_entry.opensocial_viewer_id = opensocial_viewer_id
		# DocDetailなどのOpenID認証代わりに使うのでガジェット表示時にセット（SSITE版で使うかな？？？）
		if user_entry.token_expire_date is None or user_entry.token_expire_date < datetime.datetime.now():
			user_entry.user_token = createNewUserToken()
			user_entry.token_expire_date = datetime.datetime.now() + datetime.timedelta(hours=24)
		user_entry.is_apps_admin = is_admin

		# ユーザーID変更対応…サテライトサイト側でユーザーIDが変わった場合に自動的にアドオン側のUserEntryを書き換える
		user_entry.user_id = user_id
		user_entry.user_email = user_email
		user_entry.google_apps_domain = target_domain
		user_entry.user_family_name = family_name
		user_entry.user_given_name = given_name

		user_entry.put()

		namespace_manager.set_namespace(old_namespace)
		return user_entry.user_token
