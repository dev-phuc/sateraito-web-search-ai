#!/usr/bin/python
# coding: utf-8

__author__ = 'PhucLeo <phuc@vnd.sateraito.co.jp>'
'''
@file: llm_actions.py
@brief: LLM Actions API

@since: 2025-09-03
@version: 1.0.0
@author: PhucLeo
'''

from flask import Response, stream_with_context
import requests
import json
import random

from google.appengine.api import namespace_manager

# Realtime Database
from firebase_admin import db

import sateraito_inc
import sateraito_func
import sateraito_page
from sateraito_page import Handler_Basic_Request, _BasePage
from sateraito_ai.perplexity import PerplexityAI

from sateraito_logger import logging
from sateraito_db import LLMConfiguration

from sateraito_inc import flask_docker
if flask_docker:
	# import memcache, taskqueue
	pass
else:
	# from google.appengine.api import memcache, taskqueue
	pass

class LLMActionAPI(Handler_Basic_Request, _BasePage):
	def process_stream(self, unique_id, stream_path, question, generated_content_func):
		"""
		Stream the generated content to the client.
		Use firebase Realtime Database to store the stream data.
		Args:
			unique_id (str): Unique ID for the stream.
			stream_path (str): Path in Realtime Database to store the stream data.
			generated_content_func (function): Function that generates the content to be streamed.
		"""
		
		try:
			# Create a reference to the stream path in Realtime Database
			stream_ref = db.reference(stream_path)

			# Initialize the stream data
			if not stream_ref.get():
				# Initialize the stream data
				stream_ref.set({
					'id': unique_id,
					'question': question,
					'answer': '',
					'created_at': sateraito_func.get_current_timestamp_ms(),
					'status': 'started'
				})

			# Stream the generated content
			full_answer = ''
			metadata = {}

			max_chunk_size_wait_to_save_opt = [10, 15, 20]
			max_chunk_size_wait_to_save = max_chunk_size_wait_to_save_opt[1]
			chunk_count = 0

			for chunk in generated_content_func():
				if chunk:
					_id = chunk.get('id')
					_data = chunk.get('data')
					_event = chunk.get('event', 'message')
					
					if _event == 'message':
						chunk_count += 1

						full_answer += _data

						if chunk_count >= max_chunk_size_wait_to_save:
							# Update the answer in Realtime Database
							stream_ref.update({
								'answer': full_answer,
								'status': 'in_progress'
							})
							chunk_count = 0
							max_chunk_size_wait_to_save = max_chunk_size_wait_to_save_opt[random.randint(0, len(max_chunk_size_wait_to_save_opt)-1)]

					elif _event == 'metadata':
						# Handle metadata if needed
						metadata = _data
						stream_ref.update({
							'metadata': _data
						})

			# Finalize the stream data
			stream_ref.update({
				'status': 'completed',
				'completed_at': sateraito_func.get_current_timestamp_ms()
			})

			return self.json_response({
				'message': 'stream_completed',
				'answer': full_answer,
				'metadata': metadata
			}, status=200)

		except Exception as e:
			logging.exception('Error in process_stream: %s', str(e))
			# Update the stream data with error status
			stream_ref.update({
				'status': 'error',
				'error': str(e),
				'completed_at': sateraito_func.get_current_timestamp_ms()
			})
			return self.json_response({'message': 'internal_server_error'}, status=500)

# Get method
class _ActionLLMSearchWeb(LLMActionAPI):

	def process(self, tenant, app_id):
		try:
			# Get headers
			unique_id = self.request.headers.get('X-Stream-ID')
			stream_path = self.request.headers.get('X-Stream-Path')
			# Get params
			query = self.request.json.get('query')

			if not sateraito_func.is_valid_unique_id(unique_id):
				return self.json_response({'message': 'bad_request'}, status=400)
			if not sateraito_func.is_valid_stream_path(stream_path):
				return self.json_response({'message': 'bad_request'}, status=400)
			if not query:
				return self.json_response({'message': 'bad_request'}, status=400)
			
			llm_config_dict = LLMConfiguration.getDict()
			if not llm_config_dict:
				return self.json_response({'message': 'response_length_level'}, status=404)
			
			model_name = llm_config_dict.get('model_name')
			system_prompt = llm_config_dict.get('system_prompt')
			search_context_size = llm_config_dict.get('response_length_level', 'medium')

			user_location = {
				"country": "JP",
			}
			
			perplexity_ai = PerplexityAI()
			generate, citations = perplexity_ai.chat_completion(query, stream=True,
																		model_name=model_name,
																		system_prompt=system_prompt,
																		user_location=user_location,
																		search_context_size=search_context_size,
																	)
			
			return self.process_stream(unique_id, stream_path, query, generate)
		
		except Exception as e:
			logging.exception('Error in GetLLMConfiguration.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class ClientActionLLMSearchWeb(_ActionLLMSearchWeb):

	def post(self, tenant, app_id):
		# set namespace
		namespace_manager.set_namespace(tenant)

		if not self.verifyBearerToken(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)
		
		return self.process(tenant, app_id)


def add_url_rules(app):
	app.add_url_rule('/<string:tenant>/<string:app_id>/client/llm-actions/search-web', methods=['POST'],
									view_func=ClientActionLLMSearchWeb.as_view('ClientActionLLMSearchWeb'))
