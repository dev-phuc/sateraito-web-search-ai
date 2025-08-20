import time
# import urllib2
# import urlparse
import urllib
import logging
import json

import sateraito_inc

from google.appengine.api import memcache
from google.appengine.api import urlfetch

URL_SSITE_API = sateraito_inc.SSITE_ROOT_URL + '/{0}/api_center/'
URL_SSITE_API_AUTH = URL_SSITE_API + 'auth'
API_V1 = 'v1'
URL_SSITE_API_V1 = URL_SSITE_API + API_V1 + '/{1}'
MEMCACHE_EXPIRE_SECS = 60 * 60

class SSITEClient():
	_domain_name = ''
	check_key = ''
	uid = ''
	_user_email = ''

	def __init__(self, app_domain_name, user_email, uid, check_key):
		self._domain_name = app_domain_name
		self.check_key = check_key
		self.uid = uid
		self._user_email = user_email

	def _memcache_key(self, function_name):
		return 'script=' + function_name + '?app_domain_name=' + self._domain_name + '&check_key=' + self.check_key

	def getAccessToken(self):
		result = ''
		query_params = {}
		query_params['ck'] = str(self.check_key)
		query_params['uid'] = str(self.uid)
		url_authen_token = URL_SSITE_API_AUTH.format(self._domain_name) + '?' + urllib.parse.urlencode(query_params)
		logging.debug('url_authen_token=' + str(url_authen_token))
		# url_authen_token = URL_SSITE_API_AUTH.format(self._domain_name)
		# data = {
		# 	'ck': self.check_key,
		# 	'uid': self.uid
		# }
		# payload = json.JSONEncoder().encode(data)
		# headers={'Content-Type': 'application/json'}

		deadline = 5

		# response_json = urlfetch.fetch(url=url_authen_token, payload=payload, method=urlfetch.GET, headers=headers, follow_redirects=True, deadline=deadline)
		response_json = urlfetch.fetch(url=url_authen_token, method=urlfetch.GET, follow_redirects=True, deadline=deadline)

		if response_json.status_code != 200:
			logging.error(response_json.status_code)
			logging.error(response_json.content)
			return
		
		results = json.loads(response_json.content)
		if results['code'] != 0:
			logging.error('code: ' + str(results['code']))
			logging.error('error_code: ' + str(results['error_code']))
			return result

		if 'access_token' in results:
			result = results['access_token']

		return result


	def executeQuery(self, url_query, data_post):
		result = None

		# payload = json.JSONEncoder().encode(data_post)
		# headers={'Content-Type': 'application/json'}

		for key, value in iter(data_post.items()):
			if '?' not in url_query:
				url_query = url_query + '?' + str(key) + '=' + str(value)
			else:
				url_query = url_query + '&' + str(key) + '=' + str(value)

		# logging.info(url_query)

		deadline = 5

		# response_json = urlfetch.fetch(url=url_query, payload=payload, method=urlfetch.GET, headers=headers, follow_redirects=True, deadline=deadline)
		response_json = urlfetch.fetch(url=url_query, method=urlfetch.GET, follow_redirects=True, deadline=deadline)

		if response_json.status_code != 200:
			logging.error(response_json.status_code)
			logging.error(response_json.content)
			return None

		results = json.loads(response_json.content)
		if results['code'] != 0:
			logging.error('code: ' + str(results['code']))
			logging.error('error_code: ' + str(results['error_code']))
			return result

		if 'data' in results:
			result = results['data']

		return result

	def getUser(self, access_token, user_email):
		result = None
		if access_token == '': return result

		while(True):
			url_query = URL_SSITE_API_V1.format(self._domain_name, 'user/get')
			data_post = {
				'access_token': access_token,
				'userKey': user_email,
			}
			contents = self.executeQuery(url_query, data_post)
			if contents is not None:
				result = contents

			break
		return result

	def getUserInfoList(self, access_token, page_token='', max_result=10):
		result = []
		if access_token == '': return result

		while(True):
			url_query = URL_SSITE_API_V1.format(self._domain_name, 'user/list')
			data_post = {
				'maxResults': max_result,
				'access_token': access_token,
				'pageToken': page_token,
			}
			contents = self.executeQuery(url_query, data_post)
			if contents is None: break
			for row in contents['users']:
				result.append({
					'primaryEmail': row['primaryEmail'],
					'familyName': row['name']['familyName'],
					'givenName': row['name']['givenName'],
					'name': row['name']
					})

			page_token = contents.get('nextPageToken')
			if page_token is None:
				break

		return  result

	def getGroup(self, access_token, group_key):
		result = None
		if access_token == '': return result

		while(True):
			url_query = URL_SSITE_API_V1.format(self._domain_name, 'group/get')
			data_post = {
				'groupKey': group_key,
				'access_token': access_token,
			}
			contents = self.executeQuery(url_query, data_post)
			if contents is not None:
				result = contents

			break

		return result

	def getGroupListInfo(self, access_token, page_token='', max_result=10):
		result = []
		if access_token == '': return result

		while(True):
			url_query = URL_SSITE_API_V1.format(self._domain_name, 'group/list')
			data_post = {
				'maxResults': max_result,
				'access_token': access_token,
				'pageToken': page_token
			}
			contents = self.executeQuery(url_query, data_post)
			if contents is None: break
			for row in contents['groups']:
				result.append({
					'group_id': row['id'],
					# 'email': row['email'],
					'group_name': row['name'],
					'description': row['description']
					})

			page_token = contents.get('nextPageToken')
			if page_token is None:
				break

		return  result

	def getGroupListObject(self, access_token, page_token='', max_result=10, use_key=None):
		result = []
		if access_token == '': return result

		while(True):
			url_query = URL_SSITE_API_V1.format(self._domain_name, 'group/list')
			data_post = {
				'maxResults': max_result,
				'access_token': access_token,
				'pageToken': page_token,
				'userKey': use_key
			}
			contents = self.executeQuery(url_query, data_post)
			# logging.info(contents)
			if contents is None: break
			for member in contents['groups']:
				result.append(member)

			page_token = contents.get('nextPageToken')
			if page_token is None:
				break

		return  result

	def getGroupMembers(self, group_id, access_token, page=0, max_result=10):
		result = []
		if access_token == '': return result

		while(True):
			url_query = URL_SSITE_API_V1.format(self._domain_name, 'group/members')
			data_post = {
				'size': max_result,
				'access_token': access_token,
				'page': page,
				'group_id': group_id
			}
			contents = self.executeQuery(url_query, data_post)

			if contents is None: break
			for row in contents['members']:
				result.append(row)

			page_token = contents.get('nextPageToken')
			if page_token is None:
				break

		return  result