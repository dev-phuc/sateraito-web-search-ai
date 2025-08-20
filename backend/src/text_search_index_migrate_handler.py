# coding: utf-8
from flask import render_template, request, make_response
# import json
from sateraito_logger import logging
# import datetime

from google.appengine.api import namespace_manager
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

import sateraito_inc
import sateraito_page
# import sateraito_db
import sateraito_func

from search_alt import db_migrate
from search_alt import search_mirage
from search_alt import search_adapt
from search_alt import json_helper



MIGRATE_QUEUE_NAME = 'default'


ES_MIGRATE_KEY = sateraito_inc.ES_MIGRATE_KEY


def queue_background_task_migrate(domain):
  queue_name = MIGRATE_QUEUE_NAME
  # task_name = 'search_migrate_task_process_domain_%s' % domain.replace('.', '-')
  task_url = '/%s/search_migrate/task_process_domain' % domain

  taskqueue.add(
    url=task_url,
    queue_name=queue_name,
    # name=task_name,
    method='GET',
    params={},
    retry_options=taskqueue.TaskRetryOptions(task_retry_limit=1),
  )


def stop_background_task_migrate(domain):
  # queue_name = MIGRATE_QUEUE_NAME
  # task_name = 'search_migrate_task_process_domain_%s' % domain.replace('.', '-')

  # taskqueue.Queue(queue_name).delete_tasks_by_name(task_name)

  memcache.set('stop_search_migrate_task_process_domain_%s&g=2' % domain, True, namespace=domain, time=60*30)


def fetch_status_task_migrate(domain):
  # old_name = namespace_manager.get_namespace()
  # namespace_manager.set_namespace(domain)
  # status = db_migrate.SearchIndexMigrateStatus.get_dict(db_migrate.ID_ALL_DOMAIN_NAMESPACES)
  # namespace_manager.set_namespace(old_name)
  # return status

  return search_mirage.get_db_mirgate_status_domain_namespace(domain, namespace=db_migrate.ID_ALL_DOMAIN_NAMESPACES, as_dict=True)


def fetch_status_task_migrate_all(domain):
  return search_mirage.get_db_mirgate_status_domain_namespace_all(domain, as_dict=True)


def delete_status_migrate_search(domain):
  old_name = namespace_manager.get_namespace()
  namespace_manager.set_namespace(domain)
  db_migrate.SearchIndexMigrateStatus.delete(db_migrate.ID_ALL_DOMAIN_NAMESPACES)
  namespace_manager.set_namespace(old_name)


class TaskProcessDomain(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def get(self, domain):
    result = search_mirage.process_migrate_search_data_domain(domain)
    done = result.get('done')
    if done:
      return make_response('',200)
    
    stop = memcache.get('stop_search_migrate_task_process_domain_%s' % domain, namespace=domain)
    
    if stop:
      memcache.delete('stop_search_migrate_task_process_domain_%s' % domain, namespace=domain)
      logging.info('stop search migrate task process domain %s' % domain)
      return make_response('',200)
    queue_background_task_migrate(domain)
    return make_response('', 200)
    

class RequestMigrateStart(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def post(self, domain):
    return self.process(domain)

  @sateraito_func.convert_result_none_to_empty_str
  def get(self, domain):
    return self.process(domain)

  def process(self, domain):
    app_id = None
    if not self.setNamespace(domain, app_id):
      return

    migrate_key = self.request.get('migrate_key') or self.request.get('key')
    if migrate_key:
      if migrate_key != ES_MIGRATE_KEY:
        return
    else:
      if not self.checkTokenOrOidRequest(domain):
        return
      if not sateraito_func.isWorkflowAdmin(self.viewer_email, domain):
        return
    
    restart = self.request.get('restart')
    if restart:
      delete_status_migrate_search(domain)

    self.setResponseHeader('Content-Type', 'application/json')

    status = fetch_status_task_migrate(domain)
    if status and status.get('status') == db_migrate.MIGRATE_STATUS_RUNNING:
      res = {
      }
      res_json = json_helper.dumps(res, sort_keys=True)
      return res_json
    
    queue_background_task_migrate(domain)

    res = {
      "status": "ok"
    }
    res_json = json_helper.dumps(res, sort_keys=True)
    return res_json


class RequestMigrateStop(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def post(self, domain):
    return self.process(domain)

  @sateraito_func.convert_result_none_to_empty_str
  def get(self, domain):
    return self.process(domain)

  def process(self, domain):
    app_id = None
    if not self.setNamespace(domain, app_id):
      return
    
    migrate_key = self.request.get('migrate_key') or self.request.get('key')
    if migrate_key:
      if migrate_key != ES_MIGRATE_KEY:
        return
    else:
      if not self.checkTokenOrOidRequest(domain):
        return
      if not sateraito_func.isWorkflowAdmin(self.viewer_email, domain):
        return

    self.setResponseHeader('Content-Type', 'application/json')

    status = fetch_status_task_migrate(domain)
    if not status or status.get('status') != db_migrate.MIGRATE_STATUS_RUNNING:
      res = {
      }
      res_json = json_helper.dumps(res, sort_keys=True)
      return res_json
    
    stop_background_task_migrate(domain)

    res = {
      "status": "ok"
    }
    res_json = json_helper.dumps(res, sort_keys=True)
    return res_json


class RequestMigrateRestart(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def post(self, domain):
    return self.process(domain)

  @sateraito_func.convert_result_none_to_empty_str
  def get(self, domain):
    return self.process(domain)

  def process(self, domain):
    app_id = None
    if not self.setNamespace(domain, app_id):
      return
    
    migrate_key = self.request.get('migrate_key') or self.request.get('key')
    if migrate_key:
      if migrate_key != ES_MIGRATE_KEY:
        return
    else:
      if not self.checkTokenOrOidRequest(domain):
        return
      if not sateraito_func.isWorkflowAdmin(self.viewer_email, domain):
        return
    
    delete_status_migrate_search(domain)

    queue_background_task_migrate(domain)

    res = {
      "status": "ok"
    }
    res_json = json_helper.dumps(res, sort_keys=True)
    self.setResponseHeader('Content-Type','application/json')
    return res_json


class RequestMigrateStatus(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def post(self, domain):
    return self.process(domain)

  @sateraito_func.convert_result_none_to_empty_str
  def get(self, domain):
    return self.process(domain)

  def process(self, domain):
    app_id = None
    if not self.setNamespace(domain, app_id):
      return
    
    migrate_key = self.request.get('migrate_key') or self.request.get('key')
    if migrate_key:
      if migrate_key != ES_MIGRATE_KEY:
        return
    else:
      if not self.checkTokenOrOidRequest(domain):
        return
      if not sateraito_func.isWorkflowAdmin(self.viewer_email, domain):
        return

    status = fetch_status_task_migrate(domain)
    res_json = json_helper.dumps(status, sort_keys=True)

    self.setResponseHeader('Content-Type','application/json')
    return res_json


class RequestMigrateStatusAll(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def post(self, domain):
    return self.process(domain)

  @sateraito_func.convert_result_none_to_empty_str
  def get(self, domain):
    return self.process(domain)

  def process(self, domain):
    app_id = None
    if not self.setNamespace(domain, app_id):
      return
    
    migrate_key = self.request.get('migrate_key') or self.request.get('key')
    if migrate_key:
      if migrate_key != ES_MIGRATE_KEY:
        return
    else:
      if not self.checkTokenOrOidRequest(domain):
        return
      if not sateraito_func.isWorkflowAdmin(self.viewer_email, domain):
        return

    status_all = fetch_status_task_migrate_all(domain)
    res_json = json_helper.dumps(status_all, sort_keys=True)

    self.setResponseHeader('Content-Type','application/json')
    return res_json


def queue_background_task_migrate_all_project():
  queue_name = MIGRATE_QUEUE_NAME
  # task_name = 'search_migrate_task_process_all_project'
  task_url = '/search_migrate/task_process_all_project'

  taskqueue.add(
    url=task_url,
    queue_name=queue_name,
    # name=task_name,
    method='GET',
    params={},
    retry_options=taskqueue.TaskRetryOptions(task_retry_limit=1),
  )

class TaskProcessAllProject(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def get(self):
    result = None
    
    try:
      result = search_mirage.process_migrate_search_data_all_project()
    except Exception as ex:
      logging.exception(ex, exc_info=True)
      search_mirage.set_db_mirgate_status_all_project(status=db_migrate.MIGRATE_STATUS_ERROR, info=str(ex))

    if not result:
      return make_response('',200)
    
    done = result.get('done')
    if done:
      return make_response('',200)
    
    stop = memcache.get('stop_search_migrate_task_process_all_project', namespace="")
    
    if stop:
      memcache.delete('stop_search_migrate_task_process_all_project', namespace="")
      logging.info('stop search migrate task process all project')
      return make_response('stop search migrate task process all project',200)
    queue_background_task_migrate_all_project()
    return make_response('',200)


class RequestMigrateAllProjectStart(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def post(self):
    return self.process()

  @sateraito_func.convert_result_none_to_empty_str
  def get(self):
    return self.process()

  def process(self):
    migrate_key = self.request.get('migrate_key') or self.request.get('key')
    if migrate_key != ES_MIGRATE_KEY:
      return
    
    force = self.request.get('force')
    if force:
      db_migrate.SearchIndexMigrateStatus.delete(db_migrate.ID_ALL_FULL_PROJECT)

    restart = self.request.get('restart')
    if restart:
      search_mirage.clean_db_mirgate_status_all_project_full()

    self.setResponseHeader('Content-Type', 'application/json')

    status = search_mirage.get_db_mirgate_status_all_project(as_dict=True)
    if status and status.get('status') == db_migrate.MIGRATE_STATUS_RUNNING:
      res = {
      }
      res_json = json_helper.dumps(res, sort_keys=True)
      return res_json
    
    queue_background_task_migrate_all_project()

    res = {
      "status": "ok"
    }
    res_json = json_helper.dumps(res, sort_keys=True)
    return res_json


class RequestMigrateAllProjectStop(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def post(self):
    return self.process()

  @sateraito_func.convert_result_none_to_empty_str
  def get(self):
    return self.process()

  def process(self):
    migrate_key = self.request.get('migrate_key') or self.request.get('key')
    if migrate_key != ES_MIGRATE_KEY:
      return

    self.setResponseHeader('Content-Type', 'application/json')
    
    status = search_mirage.get_db_mirgate_status_all_project(as_dict=True)
    if not status or status.get('status') != db_migrate.MIGRATE_STATUS_RUNNING:
      res = {
      }
      res_json = json_helper.dumps(res, sort_keys=True)
      return res_json
    
    memcache.set('stop_search_migrate_task_process_all_project&g=2', True, namespace="", time=60*30)

    res = {
      "status": "ok"
    }
    res_json = json_helper.dumps(res, sort_keys=True)
    return res_json


class RequestMigrateAllProjectStatus(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def post(self):
    return self.process()

  @sateraito_func.convert_result_none_to_empty_str
  def get(self):
    return self.process()

  def process(self):
    migrate_key = self.request.get('migrate_key') or self.request.get('key')
    if migrate_key != ES_MIGRATE_KEY:
      return

    status = search_mirage.get_db_mirgate_status_all_project_full(as_dict=True)
    res_json = json_helper.dumps(status, sort_keys=True)

    self.setResponseHeader('Content-Type','application/json')
    return res_json


class RequestMigrateAllProjectStatusDetail(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def post(self):
    return self.process()

  @sateraito_func.convert_result_none_to_empty_str
  def get(self):
    return self.process()

  def process(self):
    migrate_key = self.request.get('migrate_key') or self.request.get('key')
    if migrate_key != ES_MIGRATE_KEY:
      return

    status = search_mirage.get_db_mirgate_status_all_project_full_detail(as_dict=True)
    res_json = json_helper.dumps(status, sort_keys=True)

    self.setResponseHeader('Content-Type', 'application/json')
    return res_json


def queue_background_task_migrate_all_project_parallel():
  queue_name = MIGRATE_QUEUE_NAME
  # task_name = 'search_migrate_task_process_all_project_parallel'
  task_url = '/search_migrate/task_process_all_project_parallel'

  taskqueue.add(
    url=task_url,
    queue_name=queue_name,
    # name=task_name,
    method='GET',
    params={},
    retry_options=taskqueue.TaskRetryOptions(task_retry_limit=1),
  )

class TaskProcessAllProjectParallel(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def get(self):
    old_namespace = namespace_manager.get_namespace()
    if old_namespace != "":
      namespace_manager.set_namespace("")

    # restart = self.request.get('restart')
    # if restart:
    #   search_mirage.clean_db_mirgate_status_all_project_full()

    all_domains = search_adapt.get_all_domain_names()

    for domain in all_domains:
      namespace_manager.set_namespace(domain)
      migrate_status = search_mirage.get_db_mirgate_status_domain_namespace(domain)
      if migrate_status  and (migrate_status.status != db_migrate.MIGRATE_STATUS_RUNNING or migrate_status.status != db_migrate.MIGRATE_STATUS_COMPLETED):
        logging.info('skip domain: %s' % domain)
        continue
      logging.info('queue migrate domain: %s' % domain)
      queue_background_task_migrate(domain)
    namespace_manager.set_namespace("")

    if old_namespace != "":
      namespace_manager.set_namespace(old_namespace)


class RequestMigrateAllProjectParallel(sateraito_page._BasePage):

  @sateraito_func.convert_result_none_to_empty_str
  def post(self):
    return self.process()

  @sateraito_func.convert_result_none_to_empty_str
  def get(self):
    return self.process()

  def process(self):
    migrate_key = self.request.get('migrate_key') or self.request.get('key')
    if migrate_key != ES_MIGRATE_KEY:
      return
    
    force = self.request.get('force')
    if force:
      db_migrate.SearchIndexMigrateStatus.delete(db_migrate.ID_ALL_FULL_PROJECT)

    restart = self.request.get('restart')
    if restart:
      search_mirage.clean_db_mirgate_status_all_project_full()
    
    queue_background_task_migrate_all_project_parallel()

    res = {
      "status": "ok"
    }
    res_json = json_helper.dumps(res, sort_keys=True)
    self.setResponseHeader('Content-Type','application/json')
    return res_json

