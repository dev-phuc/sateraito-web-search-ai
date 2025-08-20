#!/usr/bin/python
# coding: utf-8

__author__ = 'Tran Minh Phuc <phuc@vnd.sateraito.co.jp>'
'''
sateraito_db.py

@since: 2025-08-20
@version: 1.0.0
@author: Tran Minh Phuc
'''

import json

import redis
redis_host = 'redis'
redis_port = 6379
redis_client = redis.Redis(host=redis_host, port=redis_port)

def set(key, value, namespace=None, time=None):
		"""Set a value in memcache."""
		if namespace:
				key = f"{namespace}:{key}"
    
		# redis_client.set(key, json.dumps(value))
  
def get(key, namespace=None):
		"""Get a value from memcache."""
		if namespace:
				key = f"{namespace}:{key}"
		
		data = redis_client.get(key)
		if data is not None:
				return json.loads(data)
  
		return None