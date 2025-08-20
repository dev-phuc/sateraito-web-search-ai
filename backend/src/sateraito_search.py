#!/usr/bin/python
# coding: utf-8
import json
import datetime
import time

from sateraito_logger import logging
import sateraito_db
import sateraito_func
import sateraito_inc

if sateraito_inc.ES_SEARCH_MODE:
  from search_alt import search_replace as search
else:
  from google.appengine.api import search

from google.appengine.ext import ndb
from google.appengine.runtime import DeadlineExceededError

from ucf.utils.ucfutil import *

COMPACT_TRANSACTION_AMOUNT = 1000000

INDEX_SEARCH_FILE = 'INDEX_FILE'
INDEX_SEARCH_WORKFLOW_DOC = 'INDEX_WORKFLOW_DOC'
INDEX_SEARCH_MASTER_DATA = 'INDEX_MASTER_DATA'
WF_USERLIST_INDEX = 'WF_USERLIST_INDEX'


class TransientError(Exception):
  def __init__(self):
    pass

def delete_all_in_index(index_name):
  """Delete all the docs in the given index."""

  logging.warn("delete_all_in_index: index_name='%s'" % index_name)
  doc_index = search.Index(name=index_name)

  while True:
    # looping because get_range by default returns up to 100 documents at a time
    # Get a list of documents populating only the doc_id field and extract the ids.
    document_ids = [document.doc_id for document in doc_index.get_range(ids_only=True)]
    if not document_ids:
      break
    # Delete the documents for the given ids from the Index.
    doc_index.delete(document_ids)

# >>>>>>>> For Workflow Doc <<<<<<<< #
def create_search_doc(row):
  """ create index document for textsearch
    """
  created_date_unixtime = sateraito_func.datetimeToUnixtime(row.created_date)
  if row.updated_date is None:
    row.updated_date = row.created_date
  updated_date_unixtime = sateraito_func.datetimeToUnixtime(row.updated_date)

  html_doc_values = u''
  text_doc_values = u''

  tag_name_list = []
  for tag_item in row.tag_list:
    tag_dict = sateraito_db.Categories.getDict(tag_item)
    if tag_dict is not None:
      tag_name_list.append("#" + tag_dict['name'] + "#")

  tag_name_list_str = ' '.join(tag_name_list)
  tag_list_str = ' '.join(row.tag_list)

  fields = []
  fields.append(search.TextField(name='text', value=text_doc_values))
  fields.append(search.HtmlField(name='html', value=html_doc_values))
  fields.append(search.NumberField(name='created_date', value=created_date_unixtime))
  fields.append(search.NumberField(name='updated_date', value=updated_date_unixtime))

  fields.append(search.TextField(name='workflow_doc_id', value=row.workflow_doc_id))
  fields.append(search.TextField(name='author_email', value=row.author_email))
  fields.append(search.TextField(name='author_name', value=row.author_name))
  fields.append(search.NumberField(name='del_flag', value=sateraito_func.boolToNumber(row.del_flag)))

  folder_dict = sateraito_db.DocFolder.getDict(row.folder_code)
  fields.append(search.NumberField(name='fn', value=folder_dict['folder_no']))
  fields.append(search.TextField(name='folder_code', value=folder_dict['folder_code']))
  fields.append(search.TextField(name='folder_name', value=folder_dict['folder_name']))

  q = sateraito_db.FileflowDoc.query()
  q = q.filter(sateraito_db.FileflowDoc.workflow_doc_id == row.workflow_doc_id)
  q = q.filter(sateraito_db.FileflowDoc.del_flag == False)
  q = q.order(-sateraito_db.FileflowDoc.created_date)

  str_list_file_name = ''
  converted_text_of_file = u''

  for file_item in q:
    str_list_file_name += ' ' + file_item.file_name
    # update convert text search
    converted_text = file_item.getConvertedText()
    if converted_text is not None and converted_text != '':
      converted_text_of_file += u' ' + converted_text

  fields.append(search.TextField(name='files_name', value=str_list_file_name))
  fields.append(search.TextField(name='ctf', value=converted_text_of_file))  # converted_text_of_file

  fields.append(search.TextField(name='title', value=row.title))
  fields.append(search.TextField(name='categorie_id', value=row.categorie_id))
  fields.append(search.TextField(name='tag_list', value=tag_list_str))
  fields.append(search.TextField(name='tag_name_list', value=tag_name_list_str))
  fields.append(search.TextField(name='description', value=row.description))

  if row.need_preservation_doc:
    transaction_date_unixtime = sateraito_func.datetimeToUnixtime(row.transaction_date)
    fields.append(search.NumberField(name='need_preservation_doc', value=sateraito_func.boolToNumber(row.need_preservation_doc)))
    fields.append(search.TextField(name='document_code', value=row.document_code))
    fields.append(search.NumberField(name='transaction_date', value=transaction_date_unixtime))
    fields.append(search.NumberField(name='transaction_amount', value=row.transaction_amount / COMPACT_TRANSACTION_AMOUNT))

    if not row.is_client_master_data:
      client_dict = sateraito_db.ClientInfo.getDict(row.client_id)
      fields.append(search.TextField(name='client_id', value=client_dict['client_id']))
    fields.append(search.TextField(name='client_name', value=row.client_name))

  fields.append(search.TextField(name='an', value=row.author_name))

  return search.Document(doc_id=row.workflow_doc_id, fields=fields)

def remove_doc_from_index(workflow_doc_id, num_retry=0):
  logging.info('remove_doc_from_index doc_id=' + str(workflow_doc_id))

  try:
    index = search.Index(name=INDEX_SEARCH_WORKFLOW_DOC)
    index.delete(workflow_doc_id)

  except TransientError as e:
    if num_retry >= sateraito_inc.MAX_RETRY_CNT:
      raise e

    sleep_time = sateraito_func.timeToSleep(num_retry)
    logging.info('sleep_time ' + str(sleep_time))
    time.sleep(sleep_time)

    logging.info('caught TransientError, sleeping and retry...')
    remove_doc_from_index(workflow_doc_id, (num_retry + 1))

  except DeadlineExceededError as e:
    if num_retry >= sateraito_inc.MAX_RETRY_CNT:
      raise e

    sleep_time = sateraito_func.timeToSleep(num_retry)
    logging.info('sleep_time ' + str(sleep_time))
    time.sleep(sleep_time)

    logging.info('caught DeadlineExceededError, sleeping and retry...')
    remove_doc_from_index(workflow_doc_id, (num_retry + 1))

def add_doc_to_text_search_index(row_doc, is_update=False):
  """ add doc to textsearch index
    Args: row_doc ... WorkflowDoc object
    Args: is_update ... is update
  """
  logging.info('add_doc_to_text_search_index doc_id=' + str(row_doc.workflow_doc_id))

  index = search.Index(name=INDEX_SEARCH_WORKFLOW_DOC)
  remove_doc_from_index(row_doc.workflow_doc_id)
  doc_search = create_search_doc(row_doc)
  index.put(doc_search)


# >>>>>>>> For Attach Files <<<<<<<< #
def create_search_file(row):
  """ create index document for textsearch
  """
  uploaded_date_unixtime = sateraito_func.datetimeToUnixtime(row.uploaded_date)
  created_date_unixtime = sateraito_func.datetimeToUnixtime(row.created_date)

  return search.Document(
    doc_id=row.file_id,
    fields=[
      search.TextField(name='file_id', value=row.file_id),
      search.TextField(name='folder_code', value=row.folder_code),
      search.TextField(name='workflow_doc_id', value=row.workflow_doc_id),
      search.TextField(name='author_email', value=row.author_email),
      search.TextField(name='author_name', value=row.author_name),
      search.NumberField(name='del_flag', value=sateraito_func.boolToNumber(row.del_flag)),
      search.TextField(name='file_name', value=row.file_name),
      search.NumberField(name='file_size', value=row.file_size),
      search.NumberField(name='created_date', value=created_date_unixtime),
      search.TextField(name='blob_key_cloud', value=row.blob_key_cloud),
      search.NumberField(name='uploaded_date', value=uploaded_date_unixtime),
    ]
  )

def add_file_to_text_search_index(row_doc):
  """ add file to textsearch index
    Args: row_doc ... FileflowDoc object
  """
  logging.info('add_file_to_text_search_index file_id=' + str(row_doc.file_id))
  if row_doc.del_flag:
    logging.info('deleted doc: not create index')
    return

  index = search.Index(name=INDEX_SEARCH_FILE)
  doc_search = create_search_file(row_doc)
  index.put(doc_search)

def remove_file_from_index(file_id, num_retry=0):
  logging.info('remove_file_from_index file_id=' + str(file_id))

  try:
    index = search.Index(name=INDEX_SEARCH_FILE)
    index.delete(file_id)
  except TransientError as e:
    if num_retry >= sateraito_inc.MAX_RETRY_CNT:
      raise e

    sleep_time = sateraito_func.timeToSleep(num_retry)
    logging.info('sleep_time ' + str(sleep_time))
    time.sleep(sleep_time)

    logging.info('caught TransientError, sleeping and retry...')
    remove_file_from_index(file_id, (num_retry + 1))

  except DeadlineExceededError as e:
    if num_retry >= sateraito_inc.MAX_RETRY_CNT:
      raise e

    sleep_time = sateraito_func.timeToSleep(num_retry)
    logging.info('sleep_time ' + str(sleep_time))
    time.sleep(sleep_time)

    logging.info('caught DeadlineExceededError, sleeping and retry...')
    remove_file_from_index(file_id, (num_retry + 1))


# >>>>>>>> For WF User <<<<<<<< #
def create_wf_user_list_search(row):
  return search.Document(
    doc_id=row.email,
    fields=[
      search.TextField(name='email', value=row.email),
      search.TextField(name='family_name', value=row.family_name),
      search.TextField(name='given_name', value=row.given_name),
    ])

def remove_to_text_search_wf_user_list_index(row):
  email = str(row.email).replace(' ', '')
  index = search.Index(name=WF_USERLIST_INDEX)
  index.delete(email)

def add_to_text_search_wf_user_list_index(row):
  if row is not None:
    index = search.Index(name=WF_USERLIST_INDEX)

    remove_to_text_search_wf_user_list_index(row)

    index.put(create_wf_user_list_search(row))
  else:
    pass

def create_search_wf_user(email, family_name, given_name, family_name_kana, given_name_kana):
  return search.Document(
    doc_id=email,
    fields=[
      search.TextField(name='email', value=email),
      search.TextField(name='family_name', value=family_name),
      search.TextField(name='given_name', value=given_name),
      search.TextField(name='family_name_kana', value=family_name_kana),
      search.TextField(name='given_name_kana', value=given_name_kana),
    ])

def remove_text_search_from_wf_user(email):
  email = str(email).replace(' ', '')
  if sateraito_inc.debug_mode:
    logging.info('removeTextSearchFromWFUser doc_id=' + str(email))

  index = search.Index(name=WF_USERLIST_INDEX)
  index.delete(email)

def add_to_text_search_wf_user(obj_data):
  if obj_data is not None:
    email = str(obj_data["email"]).replace(' ', '')
    family_name = obj_data["family_name"]
    given_name = obj_data["given_name"]
    family_name_kana = obj_data["family_name_kana"]
    given_name_kana = obj_data["given_name_kana"]

    if sateraito_inc.debug_mode:
      logging.info('addCheckStatusToTextSearchIndex3')
    index = search.Index(name=WF_USERLIST_INDEX)
    if sateraito_inc.debug_mode:
      logging.info('doc.doc_id=' + str(email))

    # remove_text_search_from_wf_user
    remove_text_search_from_wf_user(email)

    # create_search_wf_user
    index.put(create_search_wf_user(email, family_name, given_name, family_name_kana, given_name_kana))
  else:
    pass


# >>>>>>>> For Master Data <<<<<<<< #

def create_search_master_data(master_data_row):
  fields = []
  fields.append(search.TextField(name='master_code', value=master_data_row.master_code))
  fields.append(search.TextField(name='data_key', value=master_data_row.data_key))

  master_dict = master_data_row.to_dict()
  for col_name in sateraito_db.MasterData.updatable_cols:
    if master_dict[col_name] != '' and master_dict[col_name] is not None:
      fields.append(search.TextField(name=col_name, value=master_dict[col_name]))

  return search.Document(doc_id=master_data_row.key.id(), fields=fields)

def remove_master_data_from_index(master_key):
  logging.info('remove_master_data_from_index master_key=' + str(master_key))
  index = search.Index(name=INDEX_SEARCH_MASTER_DATA)
  index.delete(master_key)

def add_master_data_to_text_search_index(master_data_row, num_retry=0):
  logging.info('add MasterData To TextSearch Index')
  logging.info('MasterData=' + str(master_data_row))

  index = search.Index(name=INDEX_SEARCH_MASTER_DATA)

  try:
    index.put(create_search_master_data(master_data_row))

  except TransientError as e:
    logging.info('error:' + str(e))
    if num_retry > sateraito_inc.MAX_RETRY_CNT:
      raise e

    sleep_time = sateraito_func.timeToSleep(num_retry)
    logging.info('sleep_time ' + str(sleep_time))
    time.sleep(sleep_time)

    logging.info('caught TransientError, sleeping and retry...')
    add_master_data_to_text_search_index(master_data_row, (num_retry + 1))

  except DeadlineExceededError as e:
    logging.info('error:' + str(e))
    if num_retry > sateraito_inc.MAX_RETRY_CNT:
      raise e

    sleep_time = sateraito_func.timeToSleep(num_retry)
    logging.info('sleep_time ' + str(sleep_time))
    time.sleep(sleep_time)

    logging.info('caught DeadlineExceededError, sleeping and retry...')
    add_master_data_to_text_search_index(master_data_row, (num_retry + 1))

def remove_all_master_data_with_master_code(master_code):
  logging.info('remove_all_master_data_with_master_code master_code=' + str(master_code))
  name_index = INDEX_SEARCH_MASTER_DATA
  index = search.Index(name=name_index)
  query_string = 'master_code=' + str(master_code)

  query_options = search.QueryOptions(
    limit=100,
    ids_only=True
  )
  q = search.Query(query_string=query_string, options=query_options)
  while True:
    results = index.search(q)
    logging.info('results=' + str(results))
    # the overhead of getting the entire document.
    document_ids = [document.doc_id for document in results]
    logging.info('document_ids=' + str(document_ids))

    # If no IDs were returned, we've deleted everything.
    if not document_ids:
      logging.info('END')
      break

    # Delete the documents for the given IDs
    index.delete(document_ids)
