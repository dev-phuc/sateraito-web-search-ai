#!/usr/bin/python
# coding: utf-8

import datetime

'''
sateraito_mini_pr.py

@since: 2012-11-22
@version: 2013-06-06

@author: Akitoshi Abe
'''

# list MUST have 10 items
MINI_PR_LIST = [
	[u'[PR]Google Apps Scriptで社内システム作ろう！', 'http://goo.gl/nRCkl', 'orange'],
	[u'[PR]Google Apps Scriptで社内システム作ろう！', 'http://goo.gl/nRCkl', 'orange'],
	[u'[PR]Google Apps Scriptで社内システム作ろう！', 'http://goo.gl/nRCkl', 'orange'],
	[u'[PR]Google Apps Scriptで社内システム作ろう！', 'http://goo.gl/nRCkl', 'orange'],
	[u'[PR]Google Apps Scriptで社内システム作ろう！', 'http://goo.gl/nRCkl', 'orange'],
	[u'[PR]クラウド型社内電話システムはこちら', 'http://www.sateraito.jp/sateraito_cloud_tel.html', 'orange'],
	[u'[PR]クラウド型社内電話システムはこちら', 'http://www.sateraito.jp/sateraito_cloud_tel.html', 'orange'],
	[u'[PR]クラウド型社内電話システムはこちら', 'http://www.sateraito.jp/sateraito_cloud_tel.html', 'orange'],
	[u'[PR]Google Apps Marketplace アドオン一覧', 'http://www.sateraito.jp/Google_Apps_Marketplace.html', 'orange'],
	[u'[PR]Google Apps 管理者向け書籍発売！', 'http://goo.gl/H0WdL', 'orange'],
]

def getMiniPrDict():
	random_num = datetime.datetime.now().second % 10
	mini_pr_text = MINI_PR_LIST[random_num][0]
	mini_pr_url = MINI_PR_LIST[random_num][1]
	mini_pr_color = MINI_PR_LIST[random_num][2]
	return {
		'mini_pr_text': mini_pr_text,
		'mini_pr_url': mini_pr_url,
		'mini_pr_color': mini_pr_color,
		}


def getMiniPr():
	mini_pr_dict = getMiniPrDict()
	return u'<a href="' + mini_pr_dict['mini_pr_url'] + '" style="color:' + mini_pr_dict['mini_pr_color'] + ';font-size:12px;" target="_blank">' + mini_pr_dict['mini_pr_text'] + '</a>'
	