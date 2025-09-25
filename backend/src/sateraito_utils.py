#!/usr/bin/python
# coding: utf-8

__author__ = 'PhucLeo <phuc@vnd.sateraito.co.jp>'
'''
sateraito_utils.py

@since: 2025-09-03
@version: 1.0.0
@author: PhucLeo
'''

import requests
import json

from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import sateraito_func
from sateraito_page import Handler_Basic_Request, _BasePage
from sateraito_logger import logging

from sateraito_inc import my_site_url, flask_docker
if flask_docker:
	import memcache
else:
	from google.appengine.api import memcache

FILE_FAVICON_LIST = {
	'application/pdf': f'{my_site_url}/images/file_icon/64/pdf.png',
	'application/msword': f'{my_site_url}/images/file_icon/64/word.png',
	'application/vnd.openxmlformats-officedocument.wordprocessingml.document': f'{my_site_url}/images/file_icon/64/word-doc.png',
	'application/vnd.ms-excel': f'{my_site_url}/images/file_icon/64/excel.png',
	'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': f'{my_site_url}/images/file_icon/64/excel.png',
	'application/vnd.ms-powerpoint': f'{my_site_url}/images/file_icon/64/ppt.png',
	'application/vnd.openxmlformats-officedocument.presentationml.presentation': f'{my_site_url}/images/file_icon/64/ppt.png',
	'application/zip': f'{my_site_url}/images/file_icon/64/zip.png',
	'application/x-rar-compressed': f'{my_site_url}/images/file_icon/64/zip.png',
	'text/plain': f'{my_site_url}/images/file_icon/64/txt.png',
	'audio/mpeg': f'{my_site_url}/images/file_icon/64/mp3.png',
	'video/mp4': f'{my_site_url}/images/file_icon/64/mp4.png',
	'image/jpeg': f'{my_site_url}/images/file_icon/64/jpg.png',
	'image/png': f'{my_site_url}/images/file_icon/64/jpg.png',
	'image/gif': f'{my_site_url}/images/file_icon/64/jpg.png',
}

# Utils for ClientWebsites
class GetPageInfoByURL(Handler_Basic_Request, _BasePage):

	def doAction(self):
		try:
			# Get params
			page_url = self.request.args.get('page_url')

			if not page_url or page_url == '':
				return self.json_response({'message': 'page_url_is_required'}, status=400)
			
			page_url = sateraito_func.complete_full_url(page_url)

			session = requests.session()
			session.headers.update({
				'User-Agent': UserAgent().random 
			})

			# First, make a HEAD request to check content type
			try:
				head_response = session.head(page_url, timeout=10)
				content_type = head_response.headers.get('content-type', '').lower()
				logging.info('HEAD request content type for %s: %s', page_url, content_type)
				if 'text/html' not in content_type:
					logging.warning('Content type is not HTML: %s, content type: %s', page_url, content_type)
					return self.json_response({'message': 'invalid_content_type'}, status=400)
			except requests.exceptions.RequestException as e:
				# If HEAD request fails, proceed with GET request
				logging.warning('HEAD request failed for %s: %s', page_url, str(e))

			response = session.get(page_url, timeout=10)
			response.encoding = response.apparent_encoding

			if response.status_code != 200:
				logging.warning('Failed to fetch page: %s, status code: %d', page_url, response.status_code)
				return self.json_response({'message': 'failed_to_fetch_page'}, status=400)
			
			favicon_url = None
			site_name = None
			description = None

			soup = BeautifulSoup(response.text, 'html.parser')
			icon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
			if icon_link and icon_link.get('href'):
				favicon_url = icon_link['href']
				if not favicon_url.startswith('http'):
					favicon_url = urljoin(page_url, favicon_url)

			# Get site name
			if soup.title and soup.title.string:
				site_name = soup.title.string.strip()

			# Get description
			description_meta = soup.find('meta', attrs={'name': 'description'})
			if description_meta and description_meta.get('content'):
				description = description_meta['content'].strip()
			else:
				og_description = soup.find('meta', attrs={'property': 'og:description'})
				if og_description and og_description.get('content'):
					description = og_description['content'].strip()

			return {
			'favicon_url': favicon_url,
			'site_name': site_name,
			'description': description
		}

		except requests.exceptions.RequestException as e:
			return self.json_response({'message': 'failed_to_fetch_page'}, status=400)
		except Exception as e:
			logging.exception('Error in GetPageInfoByURL.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)


class GetFaviconByURL(Handler_Basic_Request, _BasePage):
	def get_cache_key(self, page_url):
		return f'favicon_url_{page_url}'
	
	def get_cached_favicon(self, page_url):
		cache_key = self.get_cache_key(page_url)
		return memcache.get(cache_key)
	
	def set_cached_favicon(self, page_url, favicon_url):
		cache_key = self.get_cache_key(page_url)
		memcache.set(cache_key, favicon_url, time=86400)  # Cache for 1 day

	def doAction(self):
		try:
			# Get params
			page_url = self.request.args.get('page_url')
			if not page_url or page_url == '':
				return self.json_response({'message': 'page_url_is_required'}, status=400)
			
			page_url = sateraito_func.complete_full_url(page_url)
			cached_favicon = self.get_cached_favicon(page_url)
			if cached_favicon:
				return {'favicon_url': cached_favicon}
			
			session = requests.session()
			session.headers.update({
				'User-Agent': UserAgent().random,
			})

			# First, make a HEAD request to check content type
			try:
				head_response = session.head(page_url, timeout=3)
				content_type = head_response.headers.get('content-type', '').lower()
				logging.info('HEAD request content type for %s: %s', page_url, content_type)
				if content_type in FILE_FAVICON_LIST:
					favicon_url = FILE_FAVICON_LIST[content_type]
					self.set_cached_favicon(page_url, favicon_url)
					return {'favicon_url': favicon_url}
				
				if 'text/html' not in content_type:
					logging.warning('Content type is not HTML: %s, content type: %s', page_url, content_type)
					return self.json_response({'message': 'invalid_content_type'}, status=400)
				
			except requests.exceptions.RequestException as e:
				# If HEAD request fails, proceed with GET request
				logging.warning('HEAD request failed for %s: %s', page_url, str(e))

			response = session.get(page_url, timeout=3)
			response.encoding = response.apparent_encoding
			
			content_type = response.headers.get('content-type', '').lower()
			if 'text/html' not in content_type:
				logging.warning('Content type is not HTML: %s, content type: %s', page_url, content_type)
				return self.json_response({'message': 'invalid_content_type'}, status=400)
			if response.status_code != 200:
				logging.warning('Failed to fetch page: %s, status code: %d', page_url, response.status_code)
				return self.json_response({'message': 'failed_to_fetch_page'}, status=400)
	
			favicon_url = None
			soup = BeautifulSoup(response.text, 'html.parser')
			icon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
			if icon_link and icon_link.get('href'):
				favicon_url = icon_link['href']
				if not favicon_url.startswith('http'):
					favicon_url = urljoin(page_url, favicon_url)

			if favicon_url:
				self.set_cached_favicon(page_url, favicon_url)

			return {'favicon_url': favicon_url}
		
		except requests.exceptions.RequestException as e:
			return self.json_response({'message': 'failed_to_fetch_page'}, status=400)
		
		except Exception as e:
			logging.exception('Error in GetFaviconByURL.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)
		

def add_url_rules(app):
	app.add_url_rule('/utils/page-info-by-url', view_func=GetPageInfoByURL.as_view('GetPageInfoByURL'), methods=['GET'])
	app.add_url_rule('/utils/favicon-by-url', view_func=GetFaviconByURL.as_view('GetFaviconByURL'), methods=['GET'])
