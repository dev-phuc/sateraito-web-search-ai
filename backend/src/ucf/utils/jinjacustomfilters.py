# coding: utf-8

# GAEGEN2対応:Loggerをカスタマイズ
#import logging
import sateraito_logger as logging
# from jinja2 import contextfilter, Markup
from jinja2 import pass_context
from markupsafe import Markup, escape

#+++++++++++++++++++++++++++++++++++++++
#+++ フィルタを登録
#+++++++++++++++++++++++++++++++++++++++
def registCustomFilters(jinja_environment):
	jinja_environment.filters['escapejs'] = escapejs

#+++++++++++++++++++++++++++++++++++++++
#+++ escapejs:JavaScript用のエスケープ
#+++++++++++++++++++++++++++++++++++++++
#@contextfilter
@pass_context
def escapejs(context, value):
	result = ''
	if type(value) is int:
		result = str(value)
	else:
		if value is not None:
			# 長い文字列の連結パフォーマンス改善対応 2022.05.30
			#for c in value:
			#	result = result + '\\u' + hex(ord(c))[2:].zfill(4)
			result_list = []
			for c in value:
				result_list.append('\\u' + hex(ord(c))[2:].zfill(4))
			result = ''.join(result_list)
			if context.eval_ctx.autoescape:
				result = Markup(result)
	return result


def escapeJavaScriptString(strValue):
	"""
		JINJA2 の JavaScript 用文字列エスケープ関数
	"""

	if (not strValue):
		return ''
	else:
		return strValue.replace("\\", "\\\\").replace(r"'", r"\'").replace(r'"', r'\"').replace(r'/', r'\/').replace(r'&', r'\x26').replace(r'<', r'\x3c').replace(r'>', r'\x3e').replace('\r', r'\r').replace('\n', r'\n')
