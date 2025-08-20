#!/usr/bin/python
# coding: utf-8

'''
health.py

@since: 2013-10-10
@version: 2023-08-23
@author: T.ASAO
'''
__author__ = 'asao@sateraito.co.jp'

import os
import datetime

from flask import Response

# GAEGEN2対応:独自ロガー
import sateraito_logger as logging

import sateraito_inc
import sateraito_page

class Page(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

  def doAction(self):
    logging.info(self.request)
    self.setCookie('TEST_COOKIE', str(datetime.datetime.now()), living_sec=3600, domain=sateraito_inc.site_fqdn, httpOnly=True)
    response_body = 'CHECK OK' + '<br/>' + self.request.headers.get('COOKIE', '')
    return response_body

def add_url_rules(app):
  app.add_url_rule('/health', view_func=Page.as_view('HealthPage'))
