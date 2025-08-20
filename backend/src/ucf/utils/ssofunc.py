# coding: utf-8

# ログイン連携対応

import re,os
import sateraito_logger as logging
import base64,datetime,random
from hashlib import sha1, sha256, sha384, sha512
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256, SHA1
import calendar
from xml.etree import ElementTree
from xml.dom import minidom
from xml.dom.minidom import Document, Element
from lxml import etree
import io
from ucf.utils.ucfutil import UcfUtil
from ucf.utils.ucfxml import UcfXml
#from ucf.utils import ucffunc
import utilities.xmldsig
import utilities.rsa_x509_pem
import sateraito_inc
import sateraito_func
from copy import deepcopy
import root
# 申込簡単化対応
from google.appengine.api import urlfetch
import urllib,json

# 申込簡単化対応
MD5_SUFFIX_KEY_FOR_SSO = 'ce2b06c1bc3b43ff9fde0ea5e2738ade'

# SSO側に指定テナントが存在するかをチェック
def checkSSOTenantExist(sso_fqdn, sso_tenant):
	sso_api_results = None
	num_retry = 0
	while True:
		try:
			now = datetime.datetime.now()
			check_key = UcfUtil.md5(sso_tenant.lower() + now.strftime('%Y%m%d%H%M') + MD5_SUFFIX_KEY_FOR_SSO)
			if sateraito_inc.developer_mode:
				url = 'http://' + sso_fqdn + '/api/setup/checktenant'
			else:
				url = 'https://' + sso_fqdn + '/api/setup/checktenant'
			payload = {
				'ck':check_key,
				'tenant':sso_tenant,
			}
			headers={}
			logging.info(url)
			result = urlfetch.fetch(url=url, payload=urllib.parse.urlencode(payload), headers=headers, method='post', deadline=30, follow_redirects=True)
			sso_api_results = json.JSONDecoder().decode(result.content.decode())
			break
		except BaseException as e:
			if num_retry > 3:
				raise e
			else:
				logging.warning(e)
				num_retry += 1
	return sso_api_results

# SSO側のテナント情報を取得
def getSSOTenantInfo(sso_fqdn, sso_tenant):
	sso_api_results = None
	num_retry = 0
	while True:
		try:
			now = datetime.datetime.now()
			check_key = UcfUtil.md5(sso_tenant.lower() + now.strftime('%Y%m%d%H%M') + MD5_SUFFIX_KEY_FOR_SSO)
			if sateraito_inc.developer_mode:
				url = 'http://' + sso_fqdn + '/api/setup/gettenantinfo'
			else:
				url = 'https://' + sso_fqdn + '/api/setup/gettenantinfo'
			payload = {
				'ck':check_key,
				'tenant':sso_tenant,
			}
			headers={}
			logging.info(url)
			result = urlfetch.fetch(url=url, payload=urllib.parse.urlencode(payload), headers=headers, method='post', deadline=30, follow_redirects=True)
			sso_api_results = json.JSONDecoder().decode(result.content.decode())
			break
		except BaseException as e:
			if num_retry > 3:
				raise e
			else:
				logging.warning(e)
				num_retry += 1
	return sso_api_results

# SSO側にテナントを新規追加
def createSSONewTenant(sso_fqdn, sso_tenant, sso_operator_id, sso_operator_pwd, oem_company_code, sp_code, hl, user_language, company_name, tanto_name, contact_mail_address, contact_tel_no, contact_prospective_account_num):

	federated_domain = sso_tenant
	sso_operator_id_ary = sso_operator_id.strip().split('@')
	if len(sso_operator_id_ary) == 2:
		federated_domain = sso_operator_id_ary[1]
		sso_operator_id = sso_operator_id_ary[0]

	sso_api_results = None
	num_retry = 0
	while True:
		try:
			now = datetime.datetime.now()
			check_key = UcfUtil.md5(sso_tenant.lower() + now.strftime('%Y%m%d%H%M') + MD5_SUFFIX_KEY_FOR_SSO)
			if sateraito_inc.developer_mode:
				url = 'http://' + sso_fqdn + '/api/setup/createnewtenant'
			else:
				url = 'https://' + sso_fqdn + '/api/setup/createnewtenant'
			payload = {
				'ck':check_key,
				'tenant':sso_tenant,
				'federated_domain':federated_domain,
				'sso_default_operator_id':sso_operator_id.strip(),
				'sso_default_operator_pwd':sso_operator_pwd.strip(),
				'oem_company_code':oem_company_code,
				'sp_code':sp_code,
				'hl':hl,
				'user_language':user_language,
				'company_name':company_name.strip(),
				'tanto_name':tanto_name.strip(),
				'contact_mail_address':contact_mail_address.strip(),
				'contact_tel_no':contact_tel_no.strip(),
				'contact_prospective_account_num':contact_prospective_account_num.strip(),
			}
			headers={}
			logging.info(url)
			result = urlfetch.fetch(url=url, payload=urllib.parse.urlencode(payload), headers=headers, method='post', deadline=30, follow_redirects=True)
			sso_api_results = json.JSONDecoder().decode(result.content.decode())
			break
		except BaseException as e:
			if num_retry > 3:
				raise e
			else:
				logging.warning(e)
				num_retry += 1
	return sso_api_results


class SAMLConstants():

		# Value added to the current time in time condition validations
		ALLOWED_CLOCK_DRIFT = 300

		XML = 'http://www.w3.org/XML/1998/namespace'
		XSI = 'http://www.w3.org/2001/XMLSchema-instance'

		# NameID Formats
		NAMEID_EMAIL_ADDRESS = 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress'
		NAMEID_X509_SUBJECT_NAME = 'urn:oasis:names:tc:SAML:1.1:nameid-format:X509SubjectName'
		NAMEID_WINDOWS_DOMAIN_QUALIFIED_NAME = 'urn:oasis:names:tc:SAML:1.1:nameid-format:WindowsDomainQualifiedName'
		NAMEID_UNSPECIFIED = 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified'
		NAMEID_KERBEROS = 'urn:oasis:names:tc:SAML:2.0:nameid-format:kerberos'
		NAMEID_ENTITY = 'urn:oasis:names:tc:SAML:2.0:nameid-format:entity'
		NAMEID_TRANSIENT = 'urn:oasis:names:tc:SAML:2.0:nameid-format:transient'
		NAMEID_PERSISTENT = 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent'
		NAMEID_ENCRYPTED = 'urn:oasis:names:tc:SAML:2.0:nameid-format:encrypted'

		# Attribute Name Formats
		ATTRNAME_FORMAT_UNSPECIFIED = 'urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified'
		ATTRNAME_FORMAT_URI = 'urn:oasis:names:tc:SAML:2.0:attrname-format:uri'
		ATTRNAME_FORMAT_BASIC = 'urn:oasis:names:tc:SAML:2.0:attrname-format:basic'

		# Namespaces
		NS_SAML = 'urn:oasis:names:tc:SAML:2.0:assertion'
		NS_SAMLP = 'urn:oasis:names:tc:SAML:2.0:protocol'
		NS_SOAP = 'http://schemas.xmlsoap.org/soap/envelope/'
		NS_MD = 'urn:oasis:names:tc:SAML:2.0:metadata'
		NS_XS = 'http://www.w3.org/2001/XMLSchema'
		NS_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
		NS_XENC = 'http://www.w3.org/2001/04/xmlenc#'
		NS_DS = 'http://www.w3.org/2000/09/xmldsig#'

		# Bindings
		BINDING_HTTP_POST = 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
		BINDING_HTTP_REDIRECT = 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
		BINDING_HTTP_ARTIFACT = 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact'
		BINDING_SOAP = 'urn:oasis:names:tc:SAML:2.0:bindings:SOAP'
		BINDING_DEFLATE = 'urn:oasis:names:tc:SAML:2.0:bindings:URL-Encoding:DEFLATE'

		# Auth Context Class
		AC_UNSPECIFIED = 'urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified'
		AC_PASSWORD = 'urn:oasis:names:tc:SAML:2.0:ac:classes:Password'
		AC_PASSWORD_PROTECTED = 'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport'
		AC_X509 = 'urn:oasis:names:tc:SAML:2.0:ac:classes:X509'
		AC_SMARTCARD = 'urn:oasis:names:tc:SAML:2.0:ac:classes:Smartcard'
		AC_KERBEROS = 'urn:oasis:names:tc:SAML:2.0:ac:classes:Kerberos'

		# Subject Confirmation
		CM_BEARER = 'urn:oasis:names:tc:SAML:2.0:cm:bearer'
		CM_HOLDER_KEY = 'urn:oasis:names:tc:SAML:2.0:cm:holder-of-key'
		CM_SENDER_VOUCHES = 'urn:oasis:names:tc:SAML:2.0:cm:sender-vouches'

		# Status Codes
		STATUS_SUCCESS = 'urn:oasis:names:tc:SAML:2.0:status:Success'
		STATUS_REQUESTER = 'urn:oasis:names:tc:SAML:2.0:status:Requester'
		STATUS_RESPONDER = 'urn:oasis:names:tc:SAML:2.0:status:Responder'
		STATUS_VERSION_MISMATCH = 'urn:oasis:names:tc:SAML:2.0:status:VersionMismatch'
		STATUS_NO_PASSIVE = 'urn:oasis:names:tc:SAML:2.0:status:NoPassive'
		STATUS_PARTIAL_LOGOUT = 'urn:oasis:names:tc:SAML:2.0:status:PartialLogout'
		STATUS_PROXY_COUNT_EXCEEDED = 'urn:oasis:names:tc:SAML:2.0:status:ProxyCountExceeded'

		# Namespaces
		NSMAP = {
				'samlp': NS_SAMLP,
				'saml': NS_SAML,
				'md': NS_MD,
				'ds': NS_DS,
				'xenc': NS_XENC
		}

		# Sign & Crypto
		SHA1 = 'http://www.w3.org/2000/09/xmldsig#sha1'
		SHA256 = 'http://www.w3.org/2001/04/xmlenc#sha256'
		SHA384 = 'http://www.w3.org/2001/04/xmldsig-more#sha384'
		SHA512 = 'http://www.w3.org/2001/04/xmlenc#sha512'

		DSA_SHA1 = 'http://www.w3.org/2000/09/xmld/sig#dsa-sha1'
		RSA_SHA1 = 'http://www.w3.org/2000/09/xmldsig#rsa-sha1'
		RSA_SHA256 = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
		RSA_SHA384 = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha384'
		RSA_SHA512 = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha512'

		# Enc
		TRIPLEDES_CBC = 'http://www.w3.org/2001/04/xmlenc#tripledes-cbc'
		AES128_CBC = 'http://www.w3.org/2001/04/xmlenc#aes128-cbc'
		AES192_CBC = 'http://www.w3.org/2001/04/xmlenc#aes192-cbc'
		AES256_CBC = 'http://www.w3.org/2001/04/xmlenc#aes256-cbc'
		RSA_1_5 = 'http://www.w3.org/2001/04/xmlenc#rsa-1_5'
		RSA_OAEP_MGF1P = 'http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p'


############################################################
## SSO関連クラス
############################################################
class SSOFunc():
	u'''SSO関連クラス'''

	#+++++++++++++++++++++++++++++++++++++++
	#+++ コンストラクタ
	#+++++++++++++++++++++++++++++++++++++++
	def __init__(self):
		u'''
		TITLE:コンストラクタ
		'''

	# ID文字列をランダムに作成して返す（半角英字.小文字.40文字）
	@classmethod
	def _createID2(cls):
		char_ary = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z')
		new_id = ''
		for i in range(40):
			idx = random.randint(1, len(char_ary))
			new_id += char_ary[idx - 1]
		return new_id

	# ID文字列をランダムに作成して返す（_ + GUID32桁）
	@classmethod
	def _createID(cls):
		return '_' + UcfUtil.guid()

	@classmethod
	def parse_time_to_SAML(cls, dt):
		"""
		Converts a UNIX timestamp to SAML2 timestamp on the form
		yyyy-mm-ddThh:mm:ss(\.s+)?Z.

		:param time: The time we should convert (DateTime).
		:type: string

		:return: SAML2 timestamp.
		:rtype: string
		"""
		return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

	@staticmethod
	def parse_SAML_to_time(timestr):
			"""
			Converts a SAML2 timestamp on the form yyyy-mm-ddThh:mm:ss(\.s+)?Z
			to a UNIX timestamp. The sub-second part is ignored.

			:param time: The time we should convert (SAML Timestamp).
			:type: string

			:return: Converted to a unix timestamp.
			:rtype: int
			"""
			try:
					data = datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%SZ')
			except ValueError:
					data = datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%S.%fZ')
			return calendar.timegm(data.utctimetuple())

	@staticmethod
	def now():
			"""
			:return: unix timestamp of actual time.
			:rtype: int
			"""
			return calendar.timegm(datetime.utcnow().utctimetuple())

	@staticmethod
	def parse_duration(duration, timestamp=None):
			"""
			Interprets a ISO8601 duration value relative to a given timestamp.

			:param duration: The duration, as a string.
			:type: string

			:param timestamp: The unix timestamp we should apply the duration to.
												Optional, default to the current time.
			:type: string

			:return: The new timestamp, after the duration is applied.
			:rtype: int
			"""
			assert isinstance(duration, basestring)
			assert timestamp is None or isinstance(timestamp, int)

			timedelta = duration_parser(duration)
			if timestamp is None:
					data = datetime.utcnow() + timedelta
			else:
					data = datetime.utcfromtimestamp(timestamp) + timedelta
			return calendar.timegm(data.utctimetuple())

	@staticmethod
	def get_expire_time(cache_duration=None, valid_until=None):
			"""
			Compares 2 dates and returns the earliest.

			:param cache_duration: The duration, as a string.
			:type: string

			:param valid_until: The valid until date, as a string or as a timestamp
			:type: string

			:return: The expiration time.
			:rtype: int
			"""
			expire_time = None

			if cache_duration is not None:
					expire_time = SSOFunc.parse_duration(cache_duration)

			if valid_until is not None:
					if isinstance(valid_until, int):
							valid_until_time = valid_until
					else:
							valid_until_time = SSOFunc.parse_SAML_to_time(valid_until)
					if expire_time is None or expire_time > valid_until_time:
							expire_time = valid_until_time

			if expire_time is not None:
					return '%d' % expire_time
			return None

	@staticmethod
	def query(dom, query, context=None):
			"""
			Extracts nodes that match the query from the Element

			:param dom: The root of the lxml objet
			:type: Element

			:param query: Xpath Expresion
			:type: string

			:param context: Context Node
			:type: DOMElement

			:returns: The queried nodes
			:rtype: list
			"""
			if context is None:
					return dom.xpath(query, namespaces=SAMLConstants.NSMAP)
			else:
					return context.xpath(query, namespaces=SAMLConstants.NSMAP)


	@staticmethod
	def calculate_x509_fingerprint(x509_cert, alg='sha1'):
			"""
			Calculates the fingerprint of a x509cert.

			:param x509_cert: x509 cert
			:type: string

			:param alg: The algorithm to build the fingerprint
			:type: string

			:returns: fingerprint
			:rtype: string
			"""
			assert isinstance(x509_cert, basestring)

			lines = x509_cert.split('\n')
			data = ''

			for line in lines:
					# Remove '\r' from end of line if present.
					line = line.rstrip()
					if line == '-----BEGIN CERTIFICATE-----':
							# Delete junk from before the certificate.
							data = ''
					elif line == '-----END CERTIFICATE-----':
							# Ignore data after the certificate.
							break
					elif line == '-----BEGIN PUBLIC KEY-----' or line == '-----BEGIN RSA PRIVATE KEY-----':
							# This isn't an X509 certificate.
							return None
					else:
							# Append the current line to the certificate data.
							data += line

			decoded_data = base64.b64decode(data)

			if alg == 'sha512':
					fingerprint = sha512(decoded_data)
			elif alg == 'sha384':
					fingerprint = sha384(decoded_data)
			elif alg == 'sha256':
					fingerprint = sha256(decoded_data)
			else:
					fingerprint = sha1(decoded_data)

			return fingerprint.hexdigest().lower()

	@staticmethod
	def format_finger_print(fingerprint):
			"""
			Formats a fingerprint.

			:param fingerprint: fingerprint
			:type: string

			:returns: Formatted fingerprint
			:rtype: string
			"""
			formated_fingerprint = fingerprint.replace(':', '')
			return formated_fingerprint.lower()


	@staticmethod
	def get_status(dom):
			"""
			Gets Status from a Response.

			:param dom: The Response as XML
			:type: Document

			:returns: The Status, an array with the code and a message.
			:rtype: dict
			"""
			status = {}

			status_entry = SSOFunc.query(dom, '/samlp:Response/samlp:Status')
			if len(status_entry) == 0:
					raise Exception('Missing Status on response')

			code_entry = SSOFunc.query(dom, '/samlp:Response/samlp:Status/samlp:StatusCode', status_entry[0])
			if len(code_entry) == 0:
					raise Exception('Missing Status Code on response')
			code = code_entry[0].values()[0]
			status['code'] = code

			message_entry = SSOFunc.query(dom, '/samlp:Response/samlp:Status/samlp:StatusMessage', status_entry[0])
			if len(message_entry) == 0:
					subcode_entry = SSOFunc.query(dom, '/samlp:Response/samlp:Status/samlp:StatusCode/samlp:StatusCode', status_entry[0])
					if len(subcode_entry) > 0:
							status['msg'] = subcode_entry[0].values()[0]
					else:
							status['msg'] = ''
			else:
					status['msg'] = message_entry[0].text

			return status


	@staticmethod
	def decrypt_element(encrypted_data, key, debug=False):
			"""
			Decrypts an encrypted element.

			:param encrypted_data: The encrypted data.
			:type: lxml.etree.Element | DOMElement | basestring

			:param key: The key.
			:type: string

			:param debug: Activate the xmlsec debug
			:type: bool

			:returns: The decrypted element.
			:rtype: lxml.etree.Element
			"""
			if isinstance(encrypted_data, Element):
					encrypted_data = etree.fromstring(str(encrypted_data.toxml()))
			elif isinstance(encrypted_data, basestring):
					encrypted_data = etree.fromstring(str(encrypted_data))

			#if debug:
			#		xmlsec.set_error_callback(print_xmlsec_errors)

			mngr = xmlsec.KeysMngr()

			key = xmlsec.Key.loadMemory(key, xmlsec.KeyDataFormatPem, None)
			mngr.addKey(key)
			enc_ctx = xmlsec.EncCtx(mngr)

			return enc_ctx.decrypt(encrypted_data)



	@staticmethod
	def validate_xml(xml, schema):
			"""
			Validates a xml against a schema
			:param xml: The xml that will be validated
			:type: string|DomDocument
			:param schema: The schema
			:type: string
			:type: bool
			:returns: Error code or the DomDocument of the xml
			:rtype: string
			"""
			assert isinstance(xml, basestring) or isinstance(xml, Document) or isinstance(xml, etree._Element)
			assert isinstance(schema, basestring)

			if isinstance(xml, Document):
					#xml = xml.toxml()
					xml = etree.tostring(xml)
			elif isinstance(xml, etree._Element):
					#xml = tostring(xml)
					xml = etree.tostring(xml)

			# Switch to lxml for schema validation
			try:
					dom = etree.fromstring(str(xml))
			except Exception:
					return 'unloaded_xml'

			schema_file = join(os.path.dirname(root.__file__), 'params', 'schemas', schema)
			f_schema = open(schema_file, 'r')
			schema_doc = etree.parse(f_schema)
			f_schema.close()
			xmlschema = etree.XMLSchema(schema_doc)

			if not xmlschema.validate(dom):
				logging.debug('Errors validating the metadata:')
				for error in xmlschema.error_log:
						logging.debug('%s\n' % error.message)
				return 'invalid_xml'

			return minidom.parseString(etree.tostring(dom))

	@staticmethod
	def format_cert(cert, heads=True):
			"""
			Returns a x509 cert (adding header & footer if required).

			:param cert: A x509 unformatted cert
			:type: string

			:param heads: True if we want to include head and footer
			:type: boolean

			:returns: Formatted cert
			:rtype: string
			"""
			x509_cert = cert.replace('\x0D', '')
			x509_cert = x509_cert.replace('\r', '')
			x509_cert = x509_cert.replace('\n', '')
			if len(x509_cert) > 0:
					x509_cert = x509_cert.replace('-----BEGIN CERTIFICATE-----', '')
					x509_cert = x509_cert.replace('-----END CERTIFICATE-----', '')
					x509_cert = x509_cert.replace(' ', '')

					if heads:
							x509_cert = "-----BEGIN CERTIFICATE-----\n" + "\n".join(wrap(x509_cert, 64)) + "\n-----END CERTIFICATE-----\n"

			return x509_cert



	@staticmethod
	def get_self_url_host(request_data):
			"""
			Returns the protocol + the current host + the port (if different than
			common ports).

			:param request_data: The request as a dict
			:type: dict

			:return: Url
			:rtype: string
			"""
			current_host = SSOFunc.get_self_host(request_data)
			port = ''
			if SSOFunc.is_https(request_data):
					protocol = 'https'
			else:
					protocol = 'http'

			if 'server_port' in request_data and request_data['server_port'] is not None:
					port_number = str(request_data['server_port'])
					port = ':' + port_number

					if protocol == 'http' and port_number == '80':
							port = ''
					elif protocol == 'https' and port_number == '443':
							port = ''

			return '%s://%s%s' % (protocol, current_host, port)

	@staticmethod
	def get_self_host(request_data):
			"""
			Returns the current host.

			:param request_data: The request as a dict
			:type: dict

			:return: The current host
			:rtype: string
			"""
			if 'http_host' in request_data:
					current_host = request_data['http_host']
			elif 'server_name' in request_data:
					current_host = request_data['server_name']
			else:
					raise Exception('No hostname defined')

			if ':' in current_host:
					current_host_data = current_host.split(':')
					possible_port = current_host_data[-1]
					try:
							possible_port = float(possible_port)
							current_host = current_host_data[0]
					except ValueError:
							current_host = ':'.join(current_host_data)

			return current_host

	@staticmethod
	def is_https(request_data):
			"""
			Checks if https or http.

			:param request_data: The request as a dict
			:type: dict

			:return: False if https is not active
			:rtype: boolean
			"""
			is_https = 'https' in request_data and request_data['https'] != 'off'
			is_https = is_https or ('server_port' in request_data and str(request_data['server_port']) == '443')
			return is_https

	@staticmethod
	def get_self_url_no_query(page):
			"""
			Returns the URL of the current host + current view.

			:param request_data: The request as a dict
			:type: dict

			:return: The url of current host + current view
			:rtype: string
			"""
			self_url_host = SSOFunc.get_self_url_host(request_data)
			script_name = request_data['script_name']
			if script_name:
					if script_name[0] != '/':
							script_name = '/' + script_name
			else:
					script_name = ''
			self_url_no_query = self_url_host + script_name
			if 'path_info' in request_data:
					self_url_no_query += request_data['path_info']

			return self_url_no_query

	@staticmethod
	def get_self_routed_url_no_query(request_data):
			"""
			Returns the routed URL of the current host + current view.

			:param request_data: The request as a dict
			:type: dict

			:return: The url of current host + current view
			:rtype: string
			"""
			self_url_host = SSOFunc.get_self_url_host(request_data)
			route = ''
			if 'request_uri' in request_data.keys() and request_data['request_uri']:
					route = request_data['request_uri']
					if 'query_string' in request_data.keys() and request_data['query_string']:
							route = route.replace(request_data['query_string'], '')

			return self_url_host + route

	@staticmethod
	def get_self_url(request_data):
			"""
			Returns the URL of the current host + current view + query.

			:param request_data: The request as a dict
			:type: dict

			:return: The url of current host + current view + query
			:rtype: string
			"""
			self_url_host = SSOFunc.get_self_url_host(request_data)

			request_uri = ''
			if 'request_uri' in request_data:
					request_uri = request_data['request_uri']
					if not request_uri.startswith('/'):
							match = re.search('^https?://[^/]*(/.*)', request_uri)
							if match is not None:
									request_uri = match.groups()[0]

			return self_url_host + request_uri

	@staticmethod
	def validate_sign(xml, cert=None, fingerprint=None, fingerprintalg='sha1', validatecert=False, debug=False):
			"""
			Validates a signature (Message or Assertion).

			:param xml: The element we should validate
			:type: string | Document

			:param cert: The pubic cert
			:type: string

			:param fingerprint: The fingerprint of the public cert
			:type: string

			:param fingerprintalg: The algorithm used to build the fingerprint
			:type: string

			:param validatecert: If true, will verify the signature and if the cert is valid.
			:type: bool

			:param debug: Activate the xmlsec debug
			:type: bool
			"""

			try:
					if xml is None or xml == '':
							raise Exception('Empty string supplied as input')
					elif isinstance(xml, etree._Element):
							elem = xml
					elif isinstance(xml, Document):
							#xml = xml.toxml()
							xml = etree.tostring(xml)
							elem = etree.fromstring(str(xml))
					elif isinstance(xml, Element):
							xml.setAttributeNS(SAMLConstants.NS_SAMLP, 'xmlns:samlp', SAMLConstants.NS_SAMLP)
							xml.setAttributeNS(SAMLConstants.NS_SAML, 'xmlns:saml', SAMLConstants.NS_SAML)
							xml.setAttributeNS(SAMLConstants.NS_SAML, 'xmlns:saml2',SAMLConstants.NS_SAML)
							#xml = xml.toxml()
							xml = etree.tostring(xml)
							elem = etree.fromstring(str(xml))
					elif isinstance(xml, basestring):
							elem = etree.fromstring(str(xml))
					else:
							raise Exception('Error parsing xml string')

					#if debug:
					#		xmlsec.set_error_callback(print_xmlsec_errors)

					#xmlsec.addIDs(elem, ["ID"])

					parent_elems_dict = {}			# Signatureノードを削除するために親ノードを取得しておく lxml etree で親ノードを取得できないようなので
					signature_nodes = []
					signature_nodes_res = SSOFunc.query(elem, '/samlp:Response/ds:Signature')
					signature_nodes_asr = SSOFunc.query(elem, '/samlp:Response/saml:Assertion/ds:Signature')
					if len(signature_nodes_res) > 0:
						parent_elems_dict[signature_nodes_res[0]] = SSOFunc.query(elem, '/samlp:Response')[0]
						signature_nodes.extend(signature_nodes_res)
					if len(signature_nodes_asr) > 0:
						parent_elems_dict[signature_nodes_asr[0]] = SSOFunc.query(elem, '/samlp:Response/saml:Assertion')[0]
						signature_nodes.extend(signature_nodes_asr)				

					signature_node = None
					if len(signature_nodes_res) > 0:
						signature_node = signature_nodes_res[0]
					elif len(signature_nodes_asr) > 0:
						signature_node = signature_nodes_asr[0]

					if signature_node is not None:
						return SSOFunc.validate_node_sign(signature_node, signature_nodes, parent_elems_dict, elem, cert, fingerprint, fingerprintalg, validatecert, debug)
					else:
						logging.warning('signature_node is not found.')
						return False
			except Exception as e:
					logging.exception(e)
					return False


	@staticmethod
	def validate_node_sign(signature_node, signature_nodes, parent_elems_dict, elem, cert=None, fingerprint=None, fingerprintalg='sha1', validatecert=False, debug=False):
			"""
			Validates a signature node.

			:param signature_node: The signature node
			:type: Node

			:param xml: The element we should validate
			:type: Document

			:param cert: The public cert
			:type: string

			:param fingerprint: The fingerprint of the public cert
			:type: string

			:param fingerprintalg: The algorithm used to build the fingerprint
			:type: string

			:param validatecert: If true, will verify the signature and if the cert is valid.
			:type: bool

			:param debug: Activate the xmlsec debug
			:type: bool
			"""
			try:
					#if debug:
					#		xmlsec.set_error_callback(print_xmlsec_errors)

					#xmlsec.addIDs(elem, ["ID"])

					if (cert is None or cert == '') and fingerprint:
							x509_certificate_nodes = SSOFunc.query(signature_node, '//ds:Signature/ds:KeyInfo/ds:X509Data/ds:X509Certificate')
							if len(x509_certificate_nodes) > 0:
									x509_certificate_node = x509_certificate_nodes[0]
									x509_cert_value = x509_certificate_node.text
									x509_fingerprint_value = SSOFunc.calculate_x509_fingerprint(x509_cert_value, fingerprintalg)
									if fingerprint == x509_fingerprint_value:
											cert = SSOFunc.format_cert(x509_cert_value)

					# Check if Reference URI is empty
					# reference_elem = SSOFunc.query(signature_node, '//ds:Reference')
					# if len(reference_elem) > 0:
					#		if reference_elem[0].get('URI') == '':
					#				reference_elem[0].set('URI', '#%s' % signature_node.getparent().get('ID'))

					if cert is None or cert == '':
							return False

					# 署名の検証

					#file_cert = OneLogin_Saml2_Utils.write_temp_file(cert)
					#if validatecert:
					#		mngr = xmlsec.KeysMngr()
					#		mngr.loadCert(file_cert.name, xmlsec.KeyDataFormatCertPem, xmlsec.KeyDataTypeTrusted)
					#		dsig_ctx = xmlsec.DSigCtx(mngr)
					#else:
					#		dsig_ctx = xmlsec.DSigCtx()
					#		dsig_ctx.signKey = xmlsec.Key.load(file_cert.name, xmlsec.KeyDataFormatCertPem, None)
					#file_cert.close()
					#dsig_ctx.setEnabledKeyData([xmlsec.KeyDataX509])
					#dsig_ctx.verify(signature_node)
					#return True

					public_key_dict = utilities.rsa_x509_pem.parse(cert)
					logging.debug(public_key_dict)
					public_key_obj = utilities.rsa_x509_pem.get_key(public_key_dict)
					f_public = utilities.rsa_x509_pem.f_public(public_key_obj)
					key = utilities.rsa_x509_pem.get_key(public_key_dict)
				   ## GAEGEN2対応:SAML、SSO連携対応. TODO 本来はPyCrypto→pycryptodome対応したい
					key_size = key.size() + 1
					#key_size = key.size_in_bits()
					logging.info('key_size=%s' % (key_size))


					## PEM形式の証明書から公開鍵を取り出す
					#cert_obj = x509.load_pem_x509_certificate(cert.encode(), default_backend())
					#public_key = cert_obj.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
					## 公開鍵をRSA.import_keyに渡す
					#rsa_key = RSA.import_key(public_key)

					# unsigned_xml と signature_value の取り出し方法の変更（正規表現の廃止） 2023/10/27
					unsigned_xml = ''			# 署名対象のノード.Response or Assertionノード（署名部分はカットしたもの）
					signature_value = ''	
					# SignatureValue値を抽出
					signatureValueNode = SSOFunc.query(signature_node, '//ds:Signature/ds:SignatureValue')
					if signatureValueNode and len(signatureValueNode) > 0:
						signature_value = signatureValueNode[0].text.replace('\n', '')
						#signature_value = signatureValueNode[0].text
					logging.debug('signature_value=%s' % (signature_value))

					canonicalization_method = ''
					canonicalization_method_elem = SSOFunc.query(signature_node, '//ds:SignedInfo/ds:CanonicalizationMethod')
					if len(canonicalization_method_elem) > 0:
						canonicalization_method = canonicalization_method_elem[0].get('Algorithm')
					logging.info('canonicalization_method=%s' % (canonicalization_method))
					# SignatureMethod「sha256」対応 2023/10/27
					signature_method = ''
					signature_method_elem = SSOFunc.query(signature_node, '//ds:SignatureMethod')
					if len(signature_method_elem) > 0:
						signature_method = signature_method_elem[0].get('Algorithm')
					logging.info('signature_method=%s' % (signature_method))
					digest_method = ''
					digest_method_elem = SSOFunc.query(signature_node, '//ds:DigestMethod')
					if len(digest_method_elem) > 0:
						digest_method = digest_method_elem[0].get('Algorithm')
					logging.info('digest_method=%s' % (digest_method))
					#digest_value = ''
					#digest_value_elem = SSOFunc.query(signature_node, '//ds:DigestValue')
					#if len(digest_value_elem) > 0:
					#	digest_value = digest_value_elem[0].text
					#logging.info('digest_value=%s' % (digest_value))
					reference_uri = ''
					reference_elem = SSOFunc.query(signature_node, '//ds:Signature/ds:SignedInfo/ds:Reference')
					if reference_elem and len(reference_elem) > 0:
						logging.debug('reference_uri is exists')
						reference_uri = reference_elem[0].get('URI')
					logging.debug('reference_uri=%s' % (reference_uri))

					with_exclusive_c14n = canonicalization_method.find('xml-exc-c14n') >= 0
					with_comments = canonicalization_method.find('#WithComments') >= 0
					logging.debug('with_exclusive_c14n=%s with_comments=%s' % (with_exclusive_c14n, with_comments))

					signed_info_xml = ''
					signed_info_elem = SSOFunc.query(signature_node, '//ds:SignedInfo')
					if len(signed_info_elem) > 0:
						output = io.BytesIO()
						etree.ElementTree(signed_info_elem[0]).write_c14n(output, exclusive=1 if with_exclusive_c14n else 0, with_comments=1 if with_comments else 0)
						signed_info_xml = output.getvalue().decode()
					logging.debug('signed_info_xml=%s' % (signed_info_xml))

					# Signatureノードを削除（正規化より前に削除）
					for remove_node in signature_nodes:
						parent_elems_dict[remove_node].remove(remove_node)
					#logging.debug(etree.tostring(elem))

					# 署名が付いているXMLノードを取得
					reference_id = ''
					if reference_uri.startswith('#'):
						reference_id = reference_uri.lstrip('#')
					logging.debug('reference_id=' + reference_id)
					if reference_id != '':
						nodelist = SSOFunc.query(elem, '//*[@ID=\'' + reference_id + '\']')
						if nodelist is not None and len(nodelist) > 0:
							#unsigned_xml = etree.tostring(nodelist[0])	
							# GAEGEN2対応：SAML、SSO連携対応. XML正規化ライブラリを変更
							#unsigned_xml = minidom.parseString(unsigned_xml)
							#unsigned_xml = c14n.Canonicalize(unsigned_xml)
							output = io.BytesIO()
							etree.ElementTree(nodelist[0]).write_c14n(output, exclusive=1 if with_exclusive_c14n else 0, with_comments=1 if with_comments else 0)
							unsigned_xml = output.getvalue().decode()
						else:
							logging.warning('target node is not found. the reference_id=' + reference_id)
							return False

					else:
						# GAEGEN2対応：SAML、SSO連携対応. XML正規化ライブラリを変更
						#unsigned_xml = etree.tostring(elem)
						#unsigned_xml = minidom.parseString(unsigned_xml)
						#unsigned_xml = c14n.Canonicalize(unsigned_xml)
						output = io.BytesIO()
						etree.ElementTree(elem).write_c14n(output, exclusive=1 if with_exclusive_c14n else 0, with_comments=1 if with_comments else 0)
						unsigned_xml = output.getvalue().decode()
					

					# 雑だが正規化方式をSAMLResponseを見て判断する 2019.06.13
					# unsigned_xml と signature_value の取り出し方法の変更（正規表現の廃止） 2023/10/27
					#with_comments = unsigned_xml.find('#WithComments') >= 0
					#with_c14n = unsigned_xml.find('xml-exc-c14n') >= 0
					# 文字列処理ではなく各方式を取得して処理（同時に↑に移動）
					#signature_xml = etree.tostring(signature_node).decode()
					#with_comments = signature_xml.find('#WithComments') >= 0
					#with_c14n = signature_xml.find('xml-exc-c14n') >= 0

					# unsigned_xml と signature_value の取り出し方法の変更（正規表現の廃止） 2023/10/27
					#return utilities.xmldsig.verify(unsigned_xml, f_public, key_size, with_c14n=with_c14n, with_comments=with_comments, reference_uri=reference_uri)
					# SignatureMethod「sha256」対応 2023/10/27
					#return utilities.xmldsig.verify(unsigned_xml, signature_value, f_public, key_size, with_c14n=with_c14n, with_comments=with_comments, reference_uri=reference_uri)
					# 文字列処理ではなく各方式を取得して処理
					#return utilities.xmldsig.verify(unsigned_xml, signature_value, f_public, key_size, with_c14n=with_c14n, with_comments=with_comments, signature_method=signature_method, reference_uri=reference_uri)
					#return utilities.xmldsig.verify(unsigned_xml, signature_value, rsa_key, key_size, digest_value, canonicalization_method, signature_method=signature_method, digest_method=digest_method, reference_uri=reference_uri)
					# SHA256対応
					if signature_method.find('#rsa-sha256') >= 0:
						# PEM形式の証明書から公開鍵を取り出す
						cert_obj = x509.load_pem_x509_certificate(cert.encode(), default_backend())
						public_key = cert_obj.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
						# 公開鍵をRSA.import_keyに渡す
						rsa_key = RSA.import_key(public_key)
						if isinstance(signed_info_xml, str):
							signed_info_xml = signed_info_xml.encode()
						digest = SHA256.new(signed_info_xml)
						signature = base64.decodebytes(signature_value.encode())
						return PKCS1_v1_5.new(rsa_key).verify(digest, signature)

					else:
						return utilities.xmldsig.verify(unsigned_xml, signature_value, f_public, key_size, canonicalization_method, signature_method=signature_method, digest_method=digest_method, reference_uri=reference_uri)

			except Exception as e:
					logging.exception(e)
					return False


############################################################
## SAMLRequest関連のクラス
############################################################
class SamlAuthnRequest():

	def __init__(self, samlsettings, force_authn=False, is_passive=False, set_nameid_policy=True):

			"""
			Constructs the AuthnRequest object.

			:param settings: OSetting data
			:type return_to: OneLogin_Saml2_Settings

			:param force_authn: Optional argument. When true the AuthNRequest will set the ForceAuthn='true'.
			:type force_authn: bool

			:param is_passive: Optional argument. When true the AuthNRequest will set the Ispassive='true'.
			:type is_passive: bool

			:param set_nameid_policy: Optional argument. When true the AuthNRequest will set a nameIdPolicy element.
			:type set_nameid_policy: bool
			"""

			self._samlsettings = samlsettings
			idp_data = self._samlsettings['idp_data']
			sp_data = self._samlsettings['sp_data']
			security = self._samlsettings['security']

			uid = SSOFunc._createID()
			self.__id = uid
			issue_instant = SSOFunc.parse_time_to_SAML(datetime.datetime.utcnow())

			destination = idp_data['singleSignOnService']['url']

			provider_name_str = ' ProviderName="%s"' % 'SateraitoAddOn'

			force_authn_str = ''
			if force_authn is True:
					force_authn_str = ' ForceAuthn="true"'

			is_passive_str = ''
			if is_passive is True:
					is_passive_str = ' IsPassive="true"'

			nameid_policy_str = ''
			if set_nameid_policy:
					name_id_policy_format = sp_data['NameIDFormat']
					if 'wantNameIdEncrypted' in security and security['wantNameIdEncrypted']:
							name_id_policy_format = SAMLConstants.NAMEID_ENCRYPTED

					nameid_policy_str = """
	<samlp:NameIDPolicy
			Format="%s"
			AllowCreate="true" />""" % name_id_policy_format

			requested_authn_context_str = ''
			if 'requestedAuthnContext' in security.keys() and security['requestedAuthnContext'] is not False:
					authn_comparison = 'exact'
					if 'requestedAuthnContextComparison' in security.keys():
							authn_comparison = security['requestedAuthnContextComparison']

					if security['requestedAuthnContext'] is True:
							requested_authn_context_str = "\n" + """		<samlp:RequestedAuthnContext Comparison="%s">
			<saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</saml:AuthnContextClassRef>
	</samlp:RequestedAuthnContext>""" % authn_comparison
					else:
							requested_authn_context_str = "\n" + '		<samlp:RequestedAuthnContext Comparison="%s">' % authn_comparison
							for authn_context in security['requestedAuthnContext']:
									requested_authn_context_str += '<saml:AuthnContextClassRef>%s</saml:AuthnContextClassRef>' % authn_context
							requested_authn_context_str += '		</samlp:RequestedAuthnContext>'

			attr_consuming_service_str = ''
			if 'attributeConsumingService' in sp_data and sp_data['attributeConsumingService']:
					attr_consuming_service_str = 'AttributeConsumingServiceIndex="1"'

			request = """<samlp:AuthnRequest
	xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
	xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
	ID="%(id)s"
	Version="2.0"%(provider_name)s%(force_authn_str)s%(is_passive_str)s
	IssueInstant="%(issue_instant)s"
	Destination="%(destination)s"
	ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
	AssertionConsumerServiceURL="%(assertion_url)s"
	%(attr_consuming_service_str)s>
	<saml:Issuer>%(entity_id)s</saml:Issuer>%(nameid_policy_str)s%(requested_authn_context_str)s
</samlp:AuthnRequest>""" % \
					{
							'id': uid,
							'provider_name': provider_name_str,
							'force_authn_str': force_authn_str,
							'is_passive_str': is_passive_str,
							'issue_instant': issue_instant,
							'destination': destination,
							'assertion_url': sp_data['assertionConsumerService']['url'],
							'entity_id': sp_data['entityId'],
							'nameid_policy_str': nameid_policy_str,
							'requested_authn_context_str': requested_authn_context_str,
							'attr_consuming_service_str': attr_consuming_service_str
					}

			self.__authn_request = request

	def get_request(self, deflate=True):
			"""
			Returns unsigned AuthnRequest.
			:param deflate: It makes the deflate process optional
			:type: bool
			:return: AuthnRequest maybe deflated and base64 encoded
			:rtype: str object
			"""
			if deflate:
					request = UcfUtil.deflateCompress(self.__authn_request)
			else:
					request = base64.b64encode(self.__authn_request)
			return request

	def get_id(self):
			"""
			Returns the AuthNRequest ID.
			:return: AuthNRequest ID
			:rtype: string
			"""
			return self.__id


	def redirect_to_idp(self, page, relay_state=None):
		query_saml_request = self.get_request(deflate=True)		# deflateはどちらでもOK（→LINE WORKSはDeflate必要）
		logging.debug(query_saml_request)
		query_relay_state = relay_state if relay_state is not None else page.request.url

		idp_data = self._samlsettings['idp_data']
		security = self._samlsettings['security']

		url = idp_data['singleSignOnService']['url']
		url = UcfUtil.appendQueryString(url, 'SAMLRequest', query_saml_request)
		url = UcfUtil.appendQueryString(url, 'RelayState', query_relay_state)
		logging.info('redirect to:' + url)
		page.redirect(url)
		return


############################################################
## SAMLResponse関連のクラス
############################################################
class SamlResponse():

	def __init__(self, samlsettings, response):

			"""
			Constructs the response object.

			:param settings: The setting info
			:type settings: OneLogin_Saml2_Setting object

			:param response: The base64 encoded, XML string containing the samlp:Response
			:type response: string
			"""

			self._samlsettings = samlsettings
			idp_data = self._samlsettings['idp_data']
			sp_data = self._samlsettings['sp_data']
			security = self._samlsettings['security']

			self.__error = None
			# Deflate圧縮パターンに対応 2019.06.13
			try:
				self.response = base64.b64decode(response)
				self.document = etree.fromstring(self.response)
			except Exception as e:
				logging.exception(e)
				self.response = UcfUtil.deflateDecompress(base64.b64decode(response))
				self.document = etree.fromstring(self.response)
			self.decrypted_document = None
			self.encrypted = None

			# Quick check for the presence of EncryptedAssertion
			encrypted_assertion_nodes = self.__query('/samlp:Response/saml:EncryptedAssertion')
			if encrypted_assertion_nodes:
					decrypted_document = deepcopy(self.document)
					self.encrypted = True
					self.decrypted_document = self.__decrypt_assertion(decrypted_document)

	def get_error(self):
		return self.__error

	# LINE WORKSのSAML設定画面の「TEST」ボタンクリック時の対応 2019.06.13
	#def is_valid(self, page, request_id=None):
	def is_valid(self, page, request_id=None, use_cert_in_samlresponse=False):
			"""
			Validates the response object.

			:param page: Request Data
			:type request_data: dict

			:param request_id: Optional argument. The ID of the AuthNRequest sent by this SP to the IdP
			:type request_id: string

			:returns: True if the SAML Response is valid, False if not
			:rtype: bool
			"""
			self.__error = None
			try:
					# Checks SAML version
					if self.document.get('Version', None) != '2.0':
							raise Exception('Unsupported SAML version')

					# Checks that ID exists
					if self.document.get('ID', None) is None:
							raise Exception('Missing ID attribute on SAML Response')

					# Checks that the response only has one assertion
					if not self.validate_num_assertions():
							raise Exception('SAML Response must contain 1 assertion')

					# Checks that the response has the SUCCESS status
					self.check_status()

					idp_data = self._samlsettings['idp_data']
					sp_data = self._samlsettings['sp_data']
					security = self._samlsettings['security']
					#idp_data = self.__settings.get_idp_data()
					idp_entity_id = idp_data.get('entityId', '')
					#sp_data = self.__settings.get_sp_data()
					sp_entity_id = sp_data.get('entityId', '')

					signed_elements = self.process_signed_elements()

					# SAMLResponseの署名からX.509公開証明書を取得 2019.06.13
					cert_from_samlresponse = ''
					if use_cert_in_samlresponse:
						cert_from_samlresponse = self.get_certificate_from_signature()
						logging.info('cert_from_samlresponse=%s' % (cert_from_samlresponse))

					if self._samlsettings.get('strict', False):
							no_valid_xml_msg = 'Invalid SAML Response. Not match the saml-schema-protocol-2.0.xsd'
							res = SSOFunc.validate_xml(etree.tostring(self.document), 'saml-schema-protocol-2.0.xsd')
							if not isinstance(res, Document):
									raise Exception(no_valid_xml_msg)

							if self.encrypted:
									res = SSOFunc.validate_xml(etree.tostring(self.decrypted_document), 'saml-schema-protocol-2.0.xsd')
									if not isinstance(res, Document):
											raise Exception(no_valid_xml_msg)

							current_url = page.request.url.split('?')[0]

							# Check if the InResponseTo of the Response matchs the ID of the AuthNRequest (requestId) if provided
							in_response_to = self.document.get('InResponseTo', None)
							if in_response_to and request_id:
									if in_response_to != request_id:
											raise Exception('The InResponseTo of the Response: %s, does not match the ID of the AuthNRequest sent by the SP: %s' % (in_response_to, request_id))

							if not self.encrypted and security.get('wantAssertionsEncrypted', False):
									raise Exception('The assertion of the Response is not encrypted and the SP require it')

							if security.get('wantNameIdEncrypted', False):
									encrypted_nameid_nodes = self.__query_assertion('/saml:Subject/saml:EncryptedID/xenc:EncryptedData')
									if len(encrypted_nameid_nodes) == 0:
											raise Exception('The NameID of the Response is not encrypted and the SP require it')

							# Checks that there is at least one AttributeStatement if required
							attribute_statement_nodes = self.__query_assertion('/saml:AttributeStatement')
							if security.get('wantAttributeStatement', True) and not attribute_statement_nodes:
									raise Exception('There is no AttributeStatement on the Response')

							# Validates Assertion timestamps
							if not self.validate_timestamps():
									raise Exception('Timing issues (please check your clock settings)')

							encrypted_attributes_nodes = self.__query_assertion('/saml:AttributeStatement/saml:EncryptedAttribute')
							if encrypted_attributes_nodes:
									raise Exception('There is an EncryptedAttribute in the Response and this SP not support them')

							# Checks destination
							destination = self.document.get('Destination', '')
							if destination:
									if not destination.startswith(current_url):
											# TODO: Review if following lines are required, since we can control the
											# request_data
											#	current_url_routed = OneLogin_Saml2_Utils.get_self_routed_url_no_query(request_data)
											#	if not destination.startswith(current_url_routed):
											raise Exception('The response was received at %s instead of %s' % (current_url, destination))

							# Checks audience
							valid_audiences = self.get_audiences()
							if valid_audiences and sp_entity_id not in valid_audiences:
									raise Exception('%s is not a valid audience for this Response' % sp_entity_id)

							# Checks the issuers
							issuers = self.get_issuers()
							for issuer in issuers:
									if issuer is None or issuer != idp_entity_id:
											raise Exception('Invalid issuer in the Assertion/Response')

							# Checks the session Expiration
							session_expiration = self.get_session_not_on_or_after()
							if session_expiration and session_expiration <= SSOFunc.now():
									raise Exception('The attributes have expired, based on the SessionNotOnOrAfter of the AttributeStatement of this Response')

							# Checks the SubjectConfirmation, at least one SubjectConfirmation must be valid
							any_subject_confirmation = False
							subject_confirmation_nodes = self.__query_assertion('/saml:Subject/saml:SubjectConfirmation')

							for scn in subject_confirmation_nodes:
									method = scn.get('Method', None)
									if method and method != SAMLConstants.CM_BEARER:
											continue
									sc_data = scn.find('saml:SubjectConfirmationData', namespaces=SAMLConstants.NSMAP)
									if sc_data is None:
											continue
									else:
											irt = sc_data.get('InResponseTo', None)
											if in_response_to and irt and irt != in_response_to:
													continue
											recipient = sc_data.get('Recipient', None)
											if recipient and current_url not in recipient:
													continue
											nooa = sc_data.get('NotOnOrAfter', None)
											if nooa:
													parsed_nooa = SSOFunc.parse_SAML_to_time(nooa)
													if parsed_nooa <= SSOFunc.now():
															continue
											nb = sc_data.get('NotBefore', None)
											if nb:
													parsed_nb = SSOFunc.parse_SAML_to_time(nb)
													if parsed_nb > SSOFunc.now():
															continue
											any_subject_confirmation = True
											break

							if not any_subject_confirmation:
									raise Exception('A valid SubjectConfirmation was not found on this Response')

							if security.get('wantAssertionsSigned', False) and ('{%s}Assertion' % SAMLConstants.NS_SAML) not in signed_elements:
									raise Exception('The Assertion of the Response is not signed and the SP require it')

							if security.get('wantMessagesSigned', False) and ('{%s}Response' % SAMLConstants.NS_SAMLP) not in signed_elements:
									raise Exception('The Message of the Response is not signed and the SP require it')

					if len(signed_elements) > 0:
							if len(signed_elements) > 2:
									raise Exception('Too many Signatures found. SAML Response rejected')

							# LINE WORKSのSAML設定画面の「TEST」ボタンクリック時の対応 2019.06.13
							#cert = idp_data.get('x509cert', None)
							if use_cert_in_samlresponse:
								cert = cert_from_samlresponse
							else:
								cert = idp_data.get('x509cert', None)
							fingerprint = idp_data.get('certFingerprint', None)
							fingerprintalg = idp_data.get('certFingerprintAlgorithm', None)

							# If find a Signature on the Response, validates it checking the original response
							if '{%s}Response' % SAMLConstants.NS_SAMLP in signed_elements:
									document_to_validate = self.document
							# Otherwise validates the assertion (decrypted assertion if was encrypted)
							else:
									if self.encrypted:
											document_to_validate = self.decrypted_document
									else:
											document_to_validate = self.document

							if not SSOFunc.validate_sign(document_to_validate, cert, fingerprint, fingerprintalg):
									raise Exception('Signature validation failed. SAML Response rejected')
					else:
							raise Exception('No Signature found. SAML Response rejected')

					return True
			except Exception as err:
					self.__error = err.__str__()
					logging.exception(err)
					return False


	def validate_num_assertions(self):
			"""
			Verifies that the document only contains a single Assertion (encrypted or not)

			:returns: True if only 1 assertion encrypted or not
			:rtype: bool
			"""
			encrypted_assertion_nodes = SSOFunc.query(self.document, '//saml:EncryptedAssertion')
			assertion_nodes = SSOFunc.query(self.document, '//saml:Assertion')
			return (len(encrypted_assertion_nodes) + len(assertion_nodes)) == 1


	def process_signed_elements(self):
			"""
			Verifies the signature nodes:
			 - Checks that are Response or Assertion
			 - Check that IDs and reference URI are unique and consistent.

			:returns: The signed elements tag names
			:rtype: list
			"""
			sign_nodes = self.__query('//ds:Signature')

			signed_elements = []
			verified_seis = []
			verified_ids = []
			response_tag = '{%s}Response' % SAMLConstants.NS_SAMLP
			assertion_tag = '{%s}Assertion' % SAMLConstants.NS_SAML

			for sign_node in sign_nodes:
					signed_element = sign_node.getparent().tag
					if signed_element != response_tag and signed_element != assertion_tag:
							raise Exception('Invalid Signature Element %s SAML Response rejected' % signed_element)

					if not sign_node.getparent().get('ID'):
							raise Exception('Signed Element must contain an ID. SAML Response rejected')

					id_value = sign_node.getparent().get('ID')
					if id_value in verified_ids:
							raise Exception('Duplicated ID. SAML Response rejected')
					verified_ids.append(id_value)

					# Check that reference URI matches the parent ID and no duplicate References or IDs
					ref = SSOFunc.query(sign_node, './/ds:Reference')
					if ref:
							ref = ref[0]
							if ref.get('URI'):
									sei = ref.get('URI')[1:]

									if sei != id_value:
											raise Exception('Found an invalid Signed Element. SAML Response rejected')

									if sei in verified_seis:
											raise Exception('Duplicated Reference URI. SAML Response rejected')
									verified_seis.append(sei)

					signed_elements.append(signed_element)
			return signed_elements


	# SAMLResponseの署名からX.509公開証明書を取得 2019.06.13
	def get_certificate_from_signature(self):
			cert = ''
			x509certificate_nodes = self.__query('//ds:Signature/ds:KeyInfo/ds:X509Data/ds:X509Certificate')
			for x509certificate_node in x509certificate_nodes:
					cert = x509certificate_node.text
			cert = cert.strip()
			if cert != '' and cert.find('-----BEGIN CERTIFICATE-----') < 0:
				cert = '-----BEGIN CERTIFICATE-----\n' + cert + '\n-----END CERTIFICATE-----'
			return cert

	def check_status(self):
			"""
			Check if the status of the response is success or not

			:raises: Exception. If the status is not success
			"""
			status = SSOFunc.get_status(self.document)
			logging.debug(status)
			code = status.get('code', None)
			if code and code != SAMLConstants.STATUS_SUCCESS:
					splited_code = code.split(':')
					printable_code = splited_code.pop()
					status_exception_msg = 'The status code of the Response was not Success, was %s' % printable_code
					status_msg = status.get('msg', None)
					if status_msg:
							status_exception_msg += ' -> ' + status_msg
					raise Exception(status_exception_msg)



	def get_audiences(self):
			"""
			Gets the audiences

			:returns: The valid audiences for the SAML Response
			:rtype: list
			"""
			audience_nodes = self.__query_assertion('/saml:Conditions/saml:AudienceRestriction/saml:Audience')
			return [node.text for node in audience_nodes if node.text is not None]

	def get_issuers(self):
			"""
			Gets the issuers (from message and from assertion)

			:returns: The issuers
			:rtype: list
			"""
			issuers = []

			message_issuer_nodes = self.__query('/samlp:Response/saml:Issuer')
			if message_issuer_nodes:
					issuers.append(message_issuer_nodes[0].text)

			assertion_issuer_nodes = self.__query_assertion('/saml:Issuer')
			if assertion_issuer_nodes:
					issuers.append(assertion_issuer_nodes[0].text)

			return list(set(issuers))

#	def get_nameid_data(self):
#			"""
#			Gets the NameID Data provided by the SAML Response from the IdP
#
#			:returns: Name ID Data (Value, Format, NameQualifier, SPNameQualifier)
#			:rtype: dict
#			"""
#			nameid = None
#			nameid_data = {}
#
#			encrypted_id_data_nodes = self.__query_assertion('/saml:Subject/saml:EncryptedID/xenc:EncryptedData')
#			if encrypted_id_data_nodes:
#					encrypted_data = encrypted_id_data_nodes[0]
#					key = self.__settings.get_sp_key()
#					nameid = SSOFunc.decrypt_element(encrypted_data, key)
#			else:
#					nameid_nodes = self.__query_assertion('/saml:Subject/saml:NameID')
#					if nameid_nodes:
#							nameid = nameid_nodes[0]
#			if nameid is None:
#					security = self.__settings.get_security_data()
#
#					if security.get('wantNameId', True):
#							raise Exception('Not NameID found in the assertion of the Response')
#			else:
#					nameid_data = {'Value': nameid.text}
#					for attr in ['Format', 'SPNameQualifier', 'NameQualifier']:
#							value = nameid.get(attr, None)
#							if value:
#									nameid_data[attr] = value
#			return nameid_data
#
#	def get_nameid(self):
#			"""
#			Gets the NameID provided by the SAML Response from the IdP
#
#			:returns: NameID (value)
#			:rtype: string|None
#			"""
#			nameid_value = None
#			nameid_data = self.get_nameid_data()
#			if nameid_data and 'Value' in nameid_data.keys():
#					nameid_value = nameid_data['Value']
#			return nameid_value

	def get_nameid(self):
			nameid = ''
			# 本当はもっとスマートに対応できるはずだが取り急ぎ... 2019.06.13
			#nameid_nodes = self.__query_assertion('/saml:Subject/saml:NameID')
			#nameid_nodes = self.__query_assertion('/{urn:oasis:names:tc:SAML:2.0:assertion}Subject/{urn:oasis:names:tc:SAML:2.0:assertion}NameID')
			nameid_nodes = SSOFunc.query(self.document, '//saml:Subject/saml:NameID')

			if nameid_nodes is not None and len(nameid_nodes) > 0:
				nameid = nameid_nodes[0].text

			## 本当はもっとスマートに対応できるはずだが取り急ぎ個別対応 2019.06.13
			#if nameid is None or nameid == '':
			#	nameid_nodes = self.__query_assertion('/saml2:Subject/saml2:NameID')
			#	if nameid_nodes is not None and len(nameid_nodes) > 0:
			#		nameid = nameid_nodes[0].text

			if nameid is None:
				nameid = ''
			logging.info('nameid=' + nameid)
			return nameid

	def get_uid(self):
			attributes = self.get_attributes()
			values = None
			if 'uid' in attributes:
				values = attributes['uid']
			logging.debug(values)
			uid = ''
			if values is not None and len(values) > 0:
				uid = values[0]
			if uid is None:
				uid = ''
			logging.info('uid=' + uid)
			return uid

	def get_isadmin(self):
			attributes = self.get_attributes()
			values = None
			if 'isadmin' in attributes:
				values = attributes['isadmin']
			logging.debug(values)
			isadmin = ''
			if values is not None and len(values) > 0:
				isadmin = values[0]
			if isadmin is None:
				isadmin = ''
			logging.info('isadmin=' + isadmin)
			return isadmin

	def get_familyname(self):
			attributes = self.get_attributes()
			values = None
			if 'familyname' in attributes:
				values = attributes['familyname']
			logging.debug(values)
			familyname = ''
			if values is not None and len(values) > 0:
				familyname = values[0]
			if familyname is None:
				familyname = ''
			if familyname != '':
				# GAEGEN2対応：SAML、SSO連携対応. ついでに IdP側がBase64エンコードしない場合に対応 2023/11/27
				#familyname = base64.decodestring(familyname).decode('utf-8')
				try:
					familyname_temp = base64.decodebytes(familyname.encode()).decode()
					# BASE64文字列ではない場合はdecodebytesの結果が空なので空の場合は元の文字列を使う
					if familyname_temp != '':
						familyname = familyname_temp
				except:
					pass
			logging.info('familyname=' + familyname)
			return familyname

	def get_givenname(self):
			attributes = self.get_attributes()
			values = None
			if 'givenname' in attributes:
				values = attributes['givenname']
			logging.debug(values)
			givenname = ''
			if values is not None and len(values) > 0:
				givenname = values[0]
			if givenname is None:
				givenname = ''
			if givenname != '':
				# GAEGEN2対応：SAML、SSO連携対応. ついでに IdP側がBase64エンコードしない場合に対応 2023/11/27
				#givenname = base64.decodestring(givenname).decode('utf-8')
				try:
					givenname_temp = base64.decodebytes(givenname.encode()).decode()
					# BASE64文字列ではない場合はdecodebytesの結果が空なので空の場合は元の文字列を使う
					if givenname_temp != '':
						givenname = givenname_temp
				except:
					pass
		
			logging.info('givenname=' + givenname)
			return givenname

	def get_target_domains(self):
			attributes = self.get_attributes()
			values = None
			if 'target_domains' in attributes:
				values = attributes['target_domains']
			logging.debug(values)
			target_domains = ''
			if values is not None and len(values) > 0:
				target_domains = values[0]
			if target_domains is None:
				target_domains = ''
			logging.info('target_domains=' + target_domains)
			return target_domains

	def get_session_not_on_or_after(self):
			"""
			Gets the SessionNotOnOrAfter from the AuthnStatement
			Could be used to set the local session expiration

			:returns: The SessionNotOnOrAfter value
			:rtype: time|None
			"""
			not_on_or_after = None
			authn_statement_nodes = self.__query_assertion('/saml:AuthnStatement[@SessionNotOnOrAfter]')
			if authn_statement_nodes:
					not_on_or_after = OneLogin_Saml2_Utils.parse_SAML_to_time(authn_statement_nodes[0].get('SessionNotOnOrAfter'))
			return not_on_or_after

	def get_session_index(self):
			"""
			Gets the SessionIndex from the AuthnStatement
			Could be used to be stored in the local session in order
			to be used in a future Logout Request that the SP could
			send to the SP, to set what specific session must be deleted

			:returns: The SessionIndex value
			:rtype: string|None
			"""
			session_index = None
			authn_statement_nodes = self.__query_assertion('/saml:AuthnStatement[@SessionIndex]')
			if authn_statement_nodes:
					session_index = authn_statement_nodes[0].get('SessionIndex')
			return session_index

	def get_attributes(self):
			"""
			Gets the Attributes from the AttributeStatement element.
			EncryptedAttributes are not supported
			"""
			attributes = {}
			attribute_nodes = self.__query_assertion('/saml:AttributeStatement/saml:Attribute')
			for attribute_node in attribute_nodes:
					attr_name = attribute_node.get('Name')
					values = []
					for attr in attribute_node.iterchildren('{%s}AttributeValue' % SAMLConstants.NSMAP['saml']):
							# Remove any whitespace (which may be present where attributes are
							# nested inside NameID children).
							if attr.text:
									text = attr.text.strip()
									if text:
											values.append(text)

							# Parse any nested NameID children
							for nameid in attr.iterchildren('{%s}NameID' % SAMLConstants.NSMAP['saml']):
									values.append({
											'NameID': {
													'Format': nameid.get('Format'),
													'NameQualifier': nameid.get('NameQualifier'),
													'value': nameid.text
											}
									})

					attributes[attr_name] = values
			return attributes


	def validate_timestamps(self):
			"""
			Verifies that the document is valid according to Conditions Element

			:returns: True if the condition is valid, False otherwise
			:rtype: bool
			"""
			conditions_nodes = self.__query_assertion('/saml:Conditions')

			for conditions_node in conditions_nodes:
					nb_attr = conditions_node.get('NotBefore')
					nooa_attr = conditions_node.get('NotOnOrAfter')
					if nb_attr and SSOFunc.parse_SAML_to_time(nb_attr) > SSOFunc.now() + SAMLConstants.ALLOWED_CLOCK_DRIFT:
							return False
					if nooa_attr and SSOFunc.parse_SAML_to_time(nooa_attr) + SAMLConstants.ALLOWED_CLOCK_DRIFT <= SSOFunc.now():
							return False
			return True

	def __query(self, query):
			"""
			Extracts nodes that match the query from the Response

			:param query: Xpath Expresion
			:type query: String

			:returns: The queried nodes
			:rtype: list
			"""
			if self.encrypted:
					document = self.decrypted_document
			else:
					document = self.document
			return SSOFunc.query(document, query)



	def __query_assertion(self, xpath_expr):
			"""
			Extracts nodes that match the query from the Assertion

			:param query: Xpath Expresion
			:type query: String

			:returns: The queried nodes
			:rtype: list
			"""
			assertion_expr = '/saml:Assertion'
			signature_expr = '/ds:Signature/ds:SignedInfo/ds:Reference'
			signed_assertion_query = '/samlp:Response' + assertion_expr + signature_expr
			assertion_reference_nodes = self.__query(signed_assertion_query)

			if not assertion_reference_nodes:
					# Check if the message is signed
					signed_message_query = '/samlp:Response' + signature_expr
					message_reference_nodes = self.__query(signed_message_query)
					if message_reference_nodes:
							message_id = message_reference_nodes[0].get('URI')
							final_query = "/samlp:Response[@ID='%s']/" % message_id[1:]
					else:
							final_query = "/samlp:Response"
					final_query += assertion_expr
			else:
					assertion_id = assertion_reference_nodes[0].get('URI')
					final_query = '/samlp:Response' + assertion_expr + "[@ID='%s']" % assertion_id[1:]
			final_query += xpath_expr
			return self.__query(final_query)
