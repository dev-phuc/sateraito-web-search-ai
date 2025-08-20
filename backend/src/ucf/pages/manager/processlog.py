# coding: utf-8

# XML関連
#import xml.dom.minidom as dom
#import xml.xpath as xpath
from xml.etree import ElementTree

# import os,sys,math
# from google.appengine.api import users
# from google.appengine.ext import webapp
# from google.appengine.ext.webapp import template
from ucf.utils.helpers import Helper, ViewHelper
from ucf.utils.validates import BaseValidator
from ucf.config.ucfconfig import *
from ucf.config.ucfmessage import *
from ucf.utils.ucfutil import *
from ucf.utils.models  import *


############################################################
## バリデーションチェッククラス 
############################################################
class ProcessLogValidator(BaseValidator):
	u'''入力チェッククラス'''
		
	def validate(self, helper, vo):
		
		# 初期化
		self.init()

		unique_id = UcfUtil.getHashStr(vo, 'unique_id')

		check_name = ''
		check_key = ''
		check_value = ''


############################################################
## ビューヘルパー
############################################################
class ProcessLogViewHelper(ViewHelper):

	def applicate(self, vo, helper):
		voVH = {}

		# ここで表示用変換を必要に応じて行うが、原則Djangoテンプレートのフィルタ機能を使う
		for k,v in vo.iteritems():
			if k == 'del_flag':
				if v == 'DEL':
					voVH[k] = u'削除する'
				elif v == '':
					voVH[k] = u'削除しない'
				else:
					voVH[k] = v
			elif k == 'log_type':
				if v == 'MANAGE_ERROR':
					voVH[k] = u'管理エラー'
				elif v == 'FRONT_ERROR':
					voVH[k] = u'フロントエラー'
				else:
					voVH[k] = v
			# exchangeVoの時点で行うのでここでは不要
#			elif k == 'date_created':
#				voVH[k] = self.formatDateTime(v)
#			elif k == 'date_changed':
#				voVH[k] = self.formatDateTime(v)
			else:
				voVH[k] = v	
		
		return voVH
