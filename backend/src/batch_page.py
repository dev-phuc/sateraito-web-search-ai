#!/usr/bin/python
# coding: utf-8

__author__ = 'Tran Minh Phuc <phuc@vnd.sateraito.co.jp>'
'''
workflowdoc.py

@since: 2022-06-22
@version: 1.0.0
@author: Tran Minh Phuc
'''

# set default encodeing to utf-8
from flask import Flask, Response, render_template, request, make_response
import json
import datetime

from google.appengine.api import taskqueue

import sateraito_inc
import sateraito_func
import sateraito_page

from sateraito_logger import logging

class StartUpdateWorkflowDoc(sateraito_page._OidBasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def get(self):
    logging.info('start update doc and client')
    # kick start
    que = taskqueue.Queue('default')
    params = {
      'namespace_name_bigger_than': ''
    }
    task = taskqueue.Task(
      url='/batch/tq/startupdateworkflowdoc',
      params=params,
      target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
      countdown=1
    )
    que.add(task)

    # export json data
    return json.JSONEncoder().encode({
      'status': 'success',
    })


# app = webapp2.WSGIApplication([

#   ('/batch/startupdateworkflowdoc$', StartUpdateWorkflowDoc),

# ], debug=sateraito_inc.debug_mode, config=sateraito_page.config)
