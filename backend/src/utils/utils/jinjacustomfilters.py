# coding: utf-8

import logging
from jinja2 import contextfilter, Markup

#+++++++++++++++++++++++++++++++++++++++
#+++ フィルタを登録
#+++++++++++++++++++++++++++++++++++++++
def registCustomFilters(jinja_environment):
	jinja_environment.filters['escapejs'] = escapejs

#+++++++++++++++++++++++++++++++++++++++
#+++ escapejs:JavaScript用のエスケープ
#+++++++++++++++++++++++++++++++++++++++
@contextfilter
def escapejs(context, value):
	result = ''
	for c in value:
		result = result + '\\u' + hex(ord(c))[2:].zfill(4)
	if context.eval_ctx.autoescape:
		result = Markup(result)
	return result
