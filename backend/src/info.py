#!/usr/bin/python
# coding: utf-8
#######################################
# LINE WORKS直接認証対応…汎用的なメッセージ表示用ページ
#######################################

import os
import jinja2
# import webapp2

# GAEGEN2対応:独自ロガー
# import logging
import sateraito_logger as logging

import datetime
from ucf.utils.ucfutil import UcfUtil
from ucf.utils import jinjacustomfilters
import sateraito_inc
import sateraito_func
import sateraito_page
import oem_func

from google.appengine.api import memcache

cwd = os.path.dirname(__file__)
path = os.path.join(cwd, 'templates')
bcc = jinja2.MemcachedBytecodeCache(client=memcache.Client(), prefix='jinja2/bytecode/', timeout=None)
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path), auto_reload=False, bytecode_cache=bcc)
jinjacustomfilters.registCustomFilters(jinja_environment)

class Page(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	#def get(self, oem_company_code, sp_code):
	def doAction(self):
		logging.debug('**** requests *********************')
		logging.debug(self.request)
		hl = self.request.get('hl')
		if hl == '':
			hl = sateraito_inc.DEFAULT_LANGUAGE
		user_language = sateraito_func.getActiveLanguage('', hl=hl)
		logging.debug('user_language=' + user_language)
		my_lang = sateraito_func.MyLang(user_language)
		lang = my_lang.getMsgs()

		msg = self.session.get('msg')
		template_filename = 'info.html'
		template = jinja_environment.get_template(template_filename)
		values = {
				'lang': lang,
				'hl': hl,
				'user_lang': user_language,
				#'oem_company_code':oem_company_code,
				#'sp_code':sp_code,
				'msg':msg,
				}
		# self.response.out.write(template.render(values))
		return template.render(values)


# app = webapp2.WSGIApplication([
# 	(r'/info', Page),
# ], debug=sateraito_inc.debug_mode, config=sateraito_page.config)


def add_url_rules(app):
	app.add_url_rule('/info', view_func=Page.as_view('InfoPage'))
