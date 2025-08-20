# coding: utf-8

import os,sys,math,datetime,time,hashlib
from google.appengine.ext import webapp
from google.appengine.api import mail

from ucf.config.ucfconfig import UcfConfig
from ucf.utils.ucfutil import *

class UcfMailUtil():
	#+++++++++++++++++++++++++++++++++++++++
	#+++ メールを1件送信
	#+++++++++++++++++++++++++++++++++++++++
	def sendOneMail(to='', sender='', subject='', body='', cc='', bcc='', reply_to='', body_html='', data=None, start_tag='[$$', end_tag='$$]'):
		u''' メールを1件送信 

		～パラメータ～
		[基本]
		to:Toアドレス
		sender:Sender
		subject:件名
		body:本文（TEXT）
		[オプション]
		reply_to:ReplyTo
		cc:Ccアドレス
		bcc:Bccアドレス
		body_html:本文（HTML)

		data:差込データ用ハッシュ
		start_tag:差込タグ（開始）
		end_tag:差込タグ（閉じ）

		'''

		# body, body_html, subject の差込対応
		subject = UcfUtil.editInsertTag(subject, data, start_tag, end_tag)
		body = UcfUtil.editInsertTag(body, data, start_tag, end_tag)
		body_html = UcfUtil.editInsertTag(body_html, data, start_tag, end_tag)


		#キーワード辞書
		kw = {}
		kw['to'] = UcfUtil.nvl(to).encode('utf-8')
		kw['sender'] = UcfUtil.nvl(sender).encode('utf-8')
		kw['subject'] = UcfUtil.nvl(subject).encode('utf-8')
		kw['body'] = UcfUtil.nvl(body).encode('utf-8')

		#オプションキーワード辞書
		if reply_to and reply_to != '':
			kw['reply_to'] = reply_to.encode('utf-8')
		if cc and cc != '':
			kw['cc'] = cc.encode('utf-8')
		if bcc and bcc != '':
			kw['bcc'] = bcc.encode('utf-8')
		if body_html and body_html != '':
			kw['html'] = body_html.encode('utf-8')

		#メール送信
		message = mail.EmailMessage(**kw)
		message.send()

	sendOneMail = staticmethod(sendOneMail)
