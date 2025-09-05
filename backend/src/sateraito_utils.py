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

from google.appengine.api import namespace_manager

import sateraito_inc
import sateraito_func
import sateraito_page

from sateraito_logger import logging

from sateraito_inc import flask_docker
if flask_docker:
	# import memcache, taskqueue
	pass
else:
	# from google.appengine.api import memcache, taskqueue
	pass

# Utils for ClientWebsites
class GetPageInfoByURL(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		try:
			# Get params
			page_url = self.request.args.get('page_url')

			if not page_url or page_url == '':
				return self.json_response({'message': 'page_url_is_required'}, status=400)
			
			page_url = sateraito_func.complete_full_url(page_url)

			logging.info('Fetching page info for URL: %s', page_url)

			session = requests.session()
			session.headers.update({
				'User-Agent': UserAgent().random 
			})
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
					from urllib.parse import urljoin
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


def add_url_rules(app):
	app.add_url_rule('/utils/page-info-by-url', view_func=GetPageInfoByURL.as_view('GetPageInfoByURL'), methods=['GET'])
