# coding: utf-8

import os, sys

#GoogleDataApi
try:
	from xml.etree import ElementTree
except ImportError:
	from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import gdata.alt.appengine
#import gdata.urlfetch
import atom.service
import gdata.spreadsheet
#import gdata.spreadsheet.text_db
import atom
import string
import logging
############################################
## gdata.spreadsheet.serviceアクセスクラス
############################################
def getSpreadsheetsService(email, password, app_name=None):
	u'''SpreadsheetsServiceを取得する'''

	service = gdata.spreadsheet.service.SpreadsheetsService()
	gdata.alt.appengine.run_on_appengine(service, store_tokens=True, single_user_mode=True)
	#	gdata.urlfetch.run_on_appengine(service)
	#service.account_type = 'HOSTED'
	service.email = email
	service.password = password
	service.source = app_name
	#service.service = 'spreadsheet'
	service.ProgrammaticLogin()
	return service


def getGDataEntryId(entry):
	u'''GDataEntryのID(ワークシートならワークシートID)を取得'''

	if entry:
		id_parts = entry.id.text.split('/')
		return id_parts[-1]
	else:
		return None


def getWorksheetByName(service, spreadsheet_key, worksheet_name):
	u'''ワークシート名でワークシートを取得'''

	#WorksheetsFeed取得
	feed = service.GetWorksheetsFeed(spreadsheet_key)

	#WorksheetsFeedが取得できなかったらNoneを返す
	if not feed:
		return None
	for entry in feed.entry:
		if (entry.title.text == worksheet_name):
			return entry

	#ワークシートが見つかれなかったらNoneを返す
	return None

def getLinkWorksheet(service, spreadsheet_key, worksheet_name):
	feed = service.GetWorksheetsFeed(spreadsheet_key)
	if not feed:
		return None
	i = 0
	for entry in feed.entry:
		if (entry.title.text == worksheet_name):
			return 'https://docs.google.com/spreadsheet/ccc?key=' + spreadsheet_key + '&usp=drive_web#gid=' + str(i)
		i += 1
	return None

def getWorksheetIdByName(service, spreadsheet_key, worksheet_name):
	u'''ワークシート名でワークシートIDを取得'''

	#WorksheetsFeed取得
	worksheet = getWorksheetByName(service, spreadsheet_key, worksheet_name)

	return getGDataEntryId(worksheet)

#	#Worksheetが取得できていたらIDを返す
#	if worksheet:
#		return getGDataEntryId(worksheet)
#	else:
#		return None

def getListFeedByCond(gd_client, spreadsheet_key, worksheet_id, query=None, start_index=None, max_results=None,
                      orderby=None):
	u'''
	ワークシートから条件指定で検索

	参考：http://code.google.com/intl/ja/apis/spreadsheets/docs/1.0/reference.html#list_Parameters
	'''

	row_query = None
	if query != None and query != '':
		row_query = gdata.spreadsheet.service.ListQuery()
		row_query.sq = query
	if orderby is not None and orderby != '':
		if row_query is None:
			row_query = gdata.spreadsheet.service.ListQuery()
		row_query.orderby = 'column:' + orderby
	if start_index is not None:
		if row_query is None:
			row_query = gdata.spreadsheet.service.ListQuery()
		row_query.start_index = str(start_index)
	if max_results is not None:
		if row_query is None:
			row_query = gdata.spreadsheet.service.ListQuery()
		row_query.max_results = str(max_results)
	feed = gd_client.GetListFeed(str(spreadsheet_key), str(worksheet_id), query=row_query)
	return feed


def getListFeedByFullText(gd_client, spreadsheet_key, worksheet_id, fulltext_values=None, start_index=None,
                          max_results=None, orderby=None):
	u'''
	ワークシートからフルテキスト検索（取得後に整合性チェックは行うこと）

	参考：http://code.google.com/intl/ja/apis/spreadsheets/docs/1.0/reference.html#list_Parameters
	'''

	row_query = None
	#	if query is not None and query != '':
	#		row_query = gdata.spreadsheet.service.ListQuery()
	#		row_query.sq = query
	if fulltext_values is not None and fulltext_values != '':
		if row_query is None:
			row_query = gdata.spreadsheet.service.ListQuery()
			query = ''
			for v in fulltext_values:
				query = query + ' ' + v
		row_query.q = query.encode('utf-8')
	if orderby is not None and orderby != '':
		if row_query is None:
			row_query = gdata.spreadsheet.service.ListQuery()
		row_query.orderby = 'column:' + orderby
	if start_index is not None:
		if row_query is None:
			row_query = gdata.spreadsheet.service.ListQuery()
		row_query.start_index = str(start_index)
	if max_results is not None:
		if row_query is None:
			row_query = gdata.spreadsheet.service.ListQuery()
		row_query.max_results = str(max_results)

	feed = gd_client.GetListFeed(str(spreadsheet_key), str(worksheet_id), query=row_query)
	return feed


def getNextListFeed(service, feed):
	u''' ListFeedから次のListFeedを取得して返す（次のリストがある場合のみ） '''
	new_feed = None
	next_link = feed.GetNextLink()
	if next_link and next_link.href:
		new_feed = service.Get(next_link.href, converter=gdata.spreadsheet.SpreadsheetsListFeedFromString)

	return new_feed

def addWorksheetRecord(service, spreadsheet_key, worksheet_id, values, header):
	u'''ワークシートに１レコード追加'''
	try:
		data = {}
		for i, value in enumerate(values):
			if i < len(header):
				key = header[i]
				data[key] = value
			else:
				break

		return service.InsertRow(data, spreadsheet_key, worksheet_id)
	except Exception as e:
		raise Exception(['failed add record to worksheet(' + spreadsheet_key + ' , ' + worksheet_id + ')', str(values), str(e)])

def addWorksheetHeader(service, spreadsheet_key, worksheet_id, values):
	try:
		#titles = getWorksheetTitleList(service, spreadsheet_key, worksheet_id)
		#if len(titles) > 0 and len(titles) >= len(values):
		#	return
		for i, value in enumerate(values):
			service.UpdateCell(1, i + 1, value, spreadsheet_key, worksheet_id)
			logging.info(value)
	except Exception as e:
		raise Exception(['failed add header to worksheet(' + spreadsheet_key + ' , ' + worksheet_id + ')', str(values), str(e)])

def updateWorksheetRecord(service,spreadsheet_key, worksheet_id, entry, values,header):
	u'''ワークシートの１レコードを更新'''
	try:

		#for label, custom in entry.custom.iteritems():
		#	if not data.has_key(label):
		#		data[label] = custom.text

		#logging.info(data)
		data = {}
		for i,value in enumerate(values):
			if i < len(header):
				key = header[i]
				data[key] = value
			else:
				break
		logging.info(data)
		service.UpdateRow(entry, data)

	except Exception as e:
		raise Exception (['failed update record to worksheet.', str(data), str(e)])
	#raise e


def deleteWorksheetRecord(service, entry):
	u'''ワークシートの１レコードを物理削除'''
	try:
		service.DeleteRow(entry)

	except Exception as e:
		raise Exception(['failed delete record to worksheet.', str(e)])
	#raise e


def getWorksheetTitleList(service, spreadsheet_key, worksheet_id, no_title_exchange=False):
	u'''ワークシートのタイトル一覧を取得'''

	first_row_contents = []
	query = gdata.spreadsheet.service.CellQuery()
	query.max_row = '1'
	query.min_row = '1'
	feed = service.GetCellsFeed(spreadsheet_key, worksheet_id, query=query)

	for entry in feed.entry:
		first_row_contents.append(entry.content.text)
	# Get the next set of cells if needed.

	#return first_row_contents
	if no_title_exchange:
		return first_row_contents
	else:
		return convertStringsToWorksheetTitleList(first_row_contents)


def convertStringsToWorksheetTitleList(proposed_headers):
	"""Converts a list of strings to column names which spreadsheets accepts.

	When setting values in a record, the keys which represent column names must
	fit certain rules. They are all lower case, contain no spaces or special
	characters. If two columns have the same name after being sanitized, the 
	columns further to the right have _2, _3 _4, etc. appended to them.

	If there are column names which consist of all special characters, or if
	the column header is blank, an obfuscated value will be used for a column
	name. This method does not handle blank column names or column names with
	only special characters.
	"""
	headers = []

	for input_string in proposed_headers:
		# TODO: probably a more efficient way to do this. Perhaps regex.
		sanitized = input_string.lower().replace('_', '').replace(
			':', '').replace(' ', '')
		# When the same sanitized header appears multiple times in the first row
		# of a spreadsheet, _n is appended to the name to make it unique.
		header_count = headers.count(sanitized)

		if header_count > 0:
			headers.append('%s_%i' % (sanitized, header_count + 1))
		else:
			headers.append(sanitized)
	return headers


def createListQuery(wheres):
	where_query = ''
	u'''リストからListQuery文字列を作成'''
	if len(wheres) > 0:
		idx = 0
		for where in wheres:
			if idx > 0:
				where_query += " and "
			where_query += where
			idx += 1
	return where_query


