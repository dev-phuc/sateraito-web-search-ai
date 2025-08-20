#!/usr/bin/python
# coding: utf-8

__author__ = 'T.ASAO <asao@sateraito.co.jp>'

import logging
import sateraito_inc

OEM_COMPANY_CODE_DEFAULT = 'sateraito'

SP_CODE_SSITE = 'ssite'										# サテライトポータルサイト
SP_CODE_WORKSMOBILE = 'worksmobile'			# ワークスモバイル
SP_CODE_GSUITE = 'apps'	# G Suite版	# G Suite 版申込ページ対応 2017.06.05
SP_CODE_WORKPLACE = 'workplace'			# Workplace対応 2017.09.13

def isValidSPCodeByContractPlatform(contract_platform, sp_code):
	if contract_platform == 'APPS':
		# G Suite 版申込ページ対応 2017.06.05
		#return sp_code is None or sp_code == ''
		return sp_code is None or sp_code == '' or sp_code == SP_CODE_GSUITE
	elif contract_platform == 'EXCLUSIVE':
		# Workplace対応 2017.09.13
		#return sp_code in [SP_CODE_SSITE, SP_CODE_WORKSMOBILE]
		return sp_code in [SP_CODE_SSITE, SP_CODE_WORKSMOBILE, SP_CODE_WORKPLACE]
	else:
		return False

def getMailMagazineTargetOEMCompanyCodes():
	return [OEM_COMPANY_CODE_DEFAULT, '']

def getBlackListTargetOEMCompanyCodes():
	return [OEM_COMPANY_CODE_DEFAULT, '']

def isValidSPCode(oem_company_code, sp_code):
	sp_code = sp_code.lower()
	if oem_company_code.lower() in [OEM_COMPANY_CODE_DEFAULT]:
		# Google Workspace 版申込ページ対応…現状、Google Workspace版は無償版のみ対応 2017.06.05
		#return sp_code in [SP_CODE_WORKSMOBILE, SP_CODE_SSITE]
		# if sp_code == SP_CODE_GSUITE and not sateraito_inc.IS_FREE_EDITION:
		# 	return False
		# Workplace対応 2017.09.13
#		return sp_code in [SP_CODE_WORKSMOBILE, SP_CODE_SSITE, SP_CODE_GSUITE]
		return sp_code in [SP_CODE_WORKSMOBILE, SP_CODE_WORKPLACE, SP_CODE_SSITE, SP_CODE_GSUITE]
	return False

def isValidOEMCompanyCode(oem_company_code):
	oem_company_code = oem_company_code.lower()
	return oem_company_code in [OEM_COMPANY_CODE_DEFAULT]

def getValidOEMCompanyCode(oem_company_code):
	if isValidOEMCompanyCode(oem_company_code):
		return oem_company_code.lower()
	else:
		return OEM_COMPANY_CODE_DEFAULT

# G Suite版以外は解約者リストを見ない対応 2017.08.28
def getBlackListTargetSPCodes():
	return [SP_CODE_GSUITE, '']

	#def getMySiteUrl(oem_company_code):
#	if oem_company_code == OEM_COMPANY_CODE_CONEXIO:
#		return sateraito_inc.for_salesforce_my_site_url
#	else:
#		return sateraito_inc.my_site_url
#
#def exchangeMessageID(msgid, oem_company_code):
#	logging.info('oem_company_code=' + oem_company_code)
#	logging.info('from msgid=' + msgid)
#	if oem_company_code == 'conexio':
#		target_msgids = [
#						'MAILSUBJECT_CONTRACT_NOTIFICATION',
#						'MAILBODY_CONTRACT_NOTIFICATION',
#						'MAILSUBJECT_APPROVAL_ACCESS_APPLY',
#						'MAILBODY_APPROVAL_ACCESS_APPLY',
#						'MAILSUBJECT_DENY_ACCESS_APPLY',
#						'MAILBODY_DENY_ACCESS_APPLY',
#						'MAILSUBJECT_ENTRY_ACCESS_APPLY_TO_MANAGER',
#						'MAILBODY_ENTRY_ACCESS_APPLY_TO_MANAGER',
#						'MAILSUBJECT_SUB_MAIL_ADDRESS_REGIST_NOTIFICATION',
#						'MAILBODY_SUB_MAIL_ADDRESS_REGIST_NOTIFICATION',
#						'MAILSUBJECT_TWO_FACTOR_AUTH_CODE_NOTIFICATION',
#						'MAILBODY_TWO_FACTOR_AUTH_CODE_NOTIFICATION',
#						'MAILSUBJECT_REMINDER_AUTH_CODE_NOTIFICATION',
#						'MAILBODY_REMINDER_AUTH_CODE_NOTIFICATION',
#						'MAILSUBJECT_PASSWORD_EXPIRE_NOTIFICATION',
#						'MAILBODY_PASSWORD_EXPIRE_NOTIFICATION',
#						'HTML_TITLE',
#						'MSG_THIS_APPRICATION_IS_STOPPED_FOR_YOUR_TENANT',
#						'MSG_NOT_INSTALLED',
#						'MSG_NOT_INSTALLED2',
#						'EXPLAIN_LOGINPAGE_DEFAULT',
#						'EXPLAIN_DASHBOARD_HEADER',
#						'EXPLAIN_COMMON_FOOTER',
#						'EXP_CONTRACT_REQUEST',
#						'EXP_CONTRACT_REQUEST2',
#			]
#		if msgid in target_msgids:
#			msgid = msgid + '_CONEXIO'
#	logging.info('exchange msgid into "' + msgid + '"')
#	return msgid