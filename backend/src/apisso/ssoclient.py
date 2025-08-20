import time
# import urllib2
# import urlparse
import urllib
import logging
import json

# from google.appengine.api import memcache

URL_SSO_API = "https://sso.sateraito.jp/a/{0}/api/public/{1}"
MEMCACHE_EXPIRE_SECS = 60 * 60

class SSOClient():
	_domain_name = ''
	_app_key = ''
	_user_email = ''

	def __init__(self, app_domain_name, app_key, user_email):
		self._domain_name = app_domain_name
		self._app_key = app_key
		self._user_email = user_email

	def _memcache_key(self, function_name):
		return 'script=' + function_name + '?app_domain_name=' + self._domain_name + '&app_key=' + self._app_key

	def getAccessToken(self):
		result = ''
		url_authen_token = URL_SSO_API.format(self._domain_name, 'auth')
		data_post = {
			'api_key': self._app_key,
			'impersonate_email': self._user_email
		}

		count_loop = 3
		index_loop = 1
		while index_loop <= count_loop:
			try:
				data = urllib.parse.urlencode(data_post)
				response = urllib.request.urlopen(url_authen_token, data)

				status_code = response.getcode()
				if status_code == 200:
					contents = response.read()
					response_json = json.loads(contents)
					if 'access_token' in response_json:
						result = response_json['access_token']
					break
			except ValueError:
				index_loop = index_loop + 1

		return result


	def executeQuery(self, url_query, data_post):
		result = None
		data = urllib.parse.urlencode(data_post)
		request = urllib.request.Request(url_query, data)
		count_loop = 3
		index_loop = 1
		while index_loop <= count_loop:
			try:
				response = urllib.request.urlopen(request)
				status_code = response.getcode()
				#logging.debug(status_code)
				if status_code == 200:
					contents = response.read()
					result = json.loads(contents)
					#logging.debug(contents)
					break
			except ValueError:
				index_loop = index_loop + 1

		return result

	def getUserInfoList(self, access_token, max_len=50):
		result = []
		if access_token == '': return result

		next_cursor = ''
		while(True):
			url_query = URL_SSO_API.format(self._domain_name, 'users/list')
			data_post = {
				'max_results': max_len,
				'access_token': access_token,
				'impersonate_email': self._user_email,
				'start_cursor': next_cursor
			}
			contents = self.executeQuery(url_query, data_post)
			if contents is None: break
			if 'datas' in contents:
				for row in contents['datas']:
					result.append({
						'user_email': row['email'],
						'family_name': row['first_name'],
						'given_name': row['last_name'],
						'photo_url': '',
						})
			next_cursor = contents['next_cursor'] if 'next_cursor' in contents else ''
			if next_cursor == '': break

		return  result


	def getUserList(self, access_token, max_len=50):
		result = []
		if access_token == '': return result

		next_cursor = ''
		while(True):
			url_query = URL_SSO_API.format(self._domain_name, 'users/list')
			data_post = {
				'max_results': max_len,
				'access_token': access_token,
				'impersonate_email': self._user_email,
				'start_cursor': next_cursor
			}
			contents = self.executeQuery(url_query, data_post)
			if contents is None: break
			if 'datas' in contents:
				for row in contents['datas']:
					result.append(row['email'])
			next_cursor = contents['next_cursor'] if 'next_cursor' in contents else ''
			if next_cursor == '': break

		return  result


	def getUserListObject(self, access_token, max_len=50):
		result = []
		if access_token == '': return result

		next_cursor = ''
		while(True):
			url_query = URL_SSO_API.format(self._domain_name, 'users/list')
			data_post = {
				'max_results': max_len,
				'access_token': access_token,
				'impersonate_email': self._user_email,
				'start_cursor': next_cursor
			}
			contents = self.executeQuery(url_query, data_post)
			if contents is None: break
			if 'datas' in contents:
				result = result + contents['datas']
			next_cursor = contents['next_cursor'] if 'next_cursor' in contents else ''
			if next_cursor == '': break

		return  result


	def getGroupInfoList(self, access_token, max_len=50):
		result = []
		if access_token == '': return result

		next_cursor = ''
		while(True):
			url_query = URL_SSO_API.format(self._domain_name, 'groups/list')
			data_post = {
				'max_results': max_len,
				'access_token': access_token,
				'impersonate_email': self._user_email,
				'start_cursor': next_cursor
			}
			contents = self.executeQuery(url_query, data_post)
			if contents is None: break
			if 'datas' in contents:
				for row in contents['datas']:
					result.append({
						'group_id': row['email'],
						'group_name': row['group_name']
					})
			next_cursor = contents['next_cursor'] if 'next_cursor' in contents else ''
			if next_cursor == '': break

		return  result


	def getGroupList(self, access_token, max_len=50):
		result = []
		if access_token == '': return result

		next_cursor = ''
		while(True):
			url_query = URL_SSO_API.format(self._domain_name, 'groups/list')
			data_post = {
				'max_results': max_len,
				'access_token': access_token,
				'impersonate_email': self._user_email,
				'start_cursor': next_cursor
			}
			contents = self.executeQuery(url_query, data_post)
			if contents is None: break
			if 'datas' in contents:
				for row in contents['datas']:
					result.append(row['email'])
			next_cursor = contents['next_cursor'] if 'next_cursor' in contents else ''
			if next_cursor == '': break

		return  result

	def getGroupListObject(self, access_token, max_len=50):
		result = []
		if access_token == '': return result

		next_cursor = ''
		while(True):
			url_query = URL_SSO_API.format(self._domain_name, 'groups/list')
			data_post = {
				'max_results': max_len,
				'access_token': access_token,
				'impersonate_email': self._user_email,
				'start_cursor': next_cursor
			}
			contents = self.executeQuery(url_query, data_post)
			if contents is None: break
			if 'datas' in contents:
				result = result + contents['datas']
			next_cursor = contents['next_cursor'] if 'next_cursor' in contents else ''
			if next_cursor == '': break

		return  result

