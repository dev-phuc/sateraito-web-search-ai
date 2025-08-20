#!/usr/bin/python
# coding: utf-8

# set default encodeing to utf-8

from dateutil import zoneinfo, tz
from utilities import define_values

def toLocalTime(date_utc, timezone=define_values.DEFAULT_TIMEZONE):
	"""
		 Args: data_utc ... datetime
		 Returns: datetime
		 """
	if date_utc is None:
		return None
	tz_user_local = zoneinfo.gettz(timezone)
	return date_utc.replace(tzinfo=tz.tzutc()).astimezone(tz_user_local)


def getDateFromDatetime(TimeDefine):
	index_T = TimeDefine.find('T')
	if index_T >= 0:
		sub_date = TimeDefine[:index_T]
		return sub_date
	return ''


def getAreaByStationCode(station_code):
	area_code = ''
	station_relation_area = define_values.STATION_RELATION_AREA
	for row in station_relation_area:
		if row['station_code'] == station_code:
			area_code = row['area_code']
			break
	return area_code


def getAreaCodeFromSubArea(area_code_sub):
	area_code = area_code_sub
	sub_area_list = define_values.SUB_AREA_LIST
	for row in sub_area_list:
		if row['sub_area_code'] == area_code_sub:
			area_code = row['area_code']
			break
	return area_code


def getAreaItemFromSubArea(area_code_sub, area_name_sub):
	area_code = area_code_sub
	area_name = area_name_sub
	sub_area_list = define_values.SUB_AREA_LIST
	for row in sub_area_list:
		if row['sub_area_code'] == area_code_sub:
			area_code = row['area_code']
			area_name = row['area_name']
			break
	return area_code, area_name


def AddDataPrecipitationPart(precipitation_list, area_code, datetime_set, value_type):
	is_exist = 0
	input_parse_date = getDateFromDatetime(datetime_set)
	for row in precipitation_list:
		if row['area_code'] == area_code and row['input_parse_date'] == input_parse_date:
			is_exist = 1
			if value_type in row['type_list']:
				break
			else:
				row['type_list'].append(value_type)

	if is_exist == 0:
		precipitation_list.append({
			'area_code': area_code,
			'input_parse_date': input_parse_date,
			'type_list': [value_type]})

	return precipitation_list


def getStringLen2(str):
	sub_str = str
	if len(str) >= 2:
		sub_str = str[:2]

	return sub_str


def convertStr2Int(str):
	if str is None:
		return ''
	number_str = ''
	for x in str:
		if x.isdigit():
			number_str += x
	return int(number_str)
