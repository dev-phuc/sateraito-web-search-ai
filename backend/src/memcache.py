#!/usr/bin/python
# coding: utf-8

__author__ = 'Tran Minh Phuc <phuc@vnd.sateraito.co.jp>'
'''
sateraito_db.py

@since: 2025-08-20
@version: 1.0.0
@author: Tran Minh Phuc
'''

import redis
import json
from typing import Any, Optional, Union
from datetime import timedelta, datetime
import os
from decimal import Decimal

import sateraito_logger as logging  # GAEGEN2対応:独自ロガー

MAX_VALUE_SIZE = (1024 * 1024) * 10  # 10MB limit for Redis values

class CustomJSONEncoder(json.JSONEncoder):
  """Custom JSON encoder để xử lý các kiểu dữ liệu đặc biệt"""
  
  def default(self, obj):
    # Xử lý DatetimeWithNanoseconds từ Google Cloud Firestore
    if hasattr(obj, 'timestamp') and hasattr(obj, 'nanosecond'):
      # DatetimeWithNanoseconds object
      return {
        '__type__': 'DatetimeWithNanoseconds',
        'timestamp': obj.timestamp(),
        'nanosecond': getattr(obj, 'nanosecond', 0)
      }
    
    # Xử lý datetime objects
    elif isinstance(obj, datetime):
      return {
        '__type__': 'datetime',
        'isoformat': obj.isoformat()
      }
    
    # Xử lý Decimal
    elif isinstance(obj, Decimal):
      return {
        '__type__': 'Decimal',
        'value': str(obj)
      }
    
    # Xử lý bytes
    elif isinstance(obj, bytes):
      return {
        '__type__': 'bytes',
        'value': obj.decode('utf-8', errors='ignore')
      }
    
    # Xử lý set
    elif isinstance(obj, set):
      return {
        '__type__': 'set',
        'value': list(obj)
      }
    
    # Xử lý các object có __dict__
    elif hasattr(obj, '__dict__'):
      return {
        '__type__': 'object',
        '__class__': obj.__class__.__name__,
        '__dict__': obj.__dict__
      }
    
    # Fallback cho các kiểu không xử lý được
    try:
      return str(obj)
    except:
      return f"<Unserializable: {type(obj).__name__}>"

def custom_json_decoder(dct):
  """Custom JSON decoder để restore các object đặc biệt"""
  if '__type__' not in dct:
    return dct
  
  obj_type = dct['__type__']
  
  if obj_type == 'DatetimeWithNanoseconds':
    # Recreate DatetimeWithNanoseconds (simplified as datetime)
    from datetime import datetime
    return datetime.fromtimestamp(dct['timestamp'])
  
  elif obj_type == 'datetime':
    from datetime import datetime
    return datetime.fromisoformat(dct['isoformat'])
  
  elif obj_type == 'Decimal':
    return Decimal(dct['value'])
  
  elif obj_type == 'bytes':
    return dct['value'].encode('utf-8')
  
  elif obj_type == 'set':
    return set(dct['value'])
  
  elif obj_type == 'object':
    # Return as dict, không recreate object
    return dct['__dict__']
  
  return dct

class RedisMemcache:
  def __init__(self):
    """Initialize Redis connection với cấu hình cho GCP"""
    self.redis_host = os.getenv('REDIS_HOST', 'redis')
    self.redis_port = int(os.getenv('REDIS_PORT', 6379))
    self.redis_password = os.getenv('REDIS_PASSWORD', None)
    self.redis_db = int(os.getenv('REDIS_DB', 0))
    
    # Cấu hình connection pool cho hiệu suất tốt hơn
    self.pool = redis.ConnectionPool(
      host=self.redis_host,
      port=self.redis_port,
      password=self.redis_password,
      db=self.redis_db,
      decode_responses=True,
      max_connections=20,
      retry_on_timeout=True,
      socket_connect_timeout=5,
      socket_timeout=5
    )
    
    self.redis_client = redis.Redis(connection_pool=self.pool)
    
    # Test connection
    try:
      self.redis_client.ping()
      logging.info("Redis connection established successfully")
    except redis.ConnectionError as e:
      logging.error(f"Redis connection failed: {e}")
      raise

  def _get_key(self, key: str, namespace: Optional[str] = None) -> str:
    """Tạo key với namespace"""
    if namespace:
      return f"{namespace}:{key}"
    return key

  def _serialize_value(self, value: Any) -> str:
    """Serialize value thành JSON string với custom encoder"""
    try:
      return json.dumps(value, ensure_ascii=False, cls=CustomJSONEncoder)
    except (TypeError, ValueError) as e:
      logging.error(f"Serialization error for value {value}: {e}")
      raise

  def _deserialize_value(self, data: str) -> Any:
    """Deserialize JSON string thành value với custom decoder"""
    try:
      return json.loads(data, object_hook=custom_json_decoder)
    except (json.JSONDecodeError, TypeError) as e:
      logging.error(f"Deserialization error for data {data}: {e}")
      return None

  def set(self, key: str, value: Any, namespace: Optional[str] = None, 
          ttl: Optional[Union[int, timedelta]] = None) -> bool:
    """
    Set a value in Redis cache
    
    Args:
      key: Cache key
      value: Value to cache (will be JSON serialized)
      namespace: Optional namespace for key grouping
      ttl: Time to live in seconds (int) or timedelta object
    
    Returns:
      bool: True if successful, False otherwise
    """
    try:
      cache_key = self._get_key(key, namespace)
      serialized_value = self._serialize_value(value)
      
      if isinstance(ttl, timedelta):
        ttl = int(ttl.total_seconds())
      
      result = self.redis_client.set(cache_key, serialized_value, ex=ttl)
      
      if result:
        logging.debug(f"Successfully cached key: {cache_key}")
      return result
      
    except Exception as e:
      logging.error(f"Error setting cache for key {key}: {e}")
      return False

  def get(self, key: str, namespace: Optional[str] = None, 
          default: Any = None) -> Any:
    """
    Get a value from Redis cache
    
    Args:
      key: Cache key
      namespace: Optional namespace
      default: Default value if key not found
    
    Returns:
      Cached value or default
    """
    try:
      cache_key = self._get_key(key, namespace)
      data = self.redis_client.get(cache_key)
      
      if data is not None:
        deserialized = self._deserialize_value(data)
        logging.debug(f"Cache hit for key: {cache_key}")
        return deserialized
      else:
        logging.debug(f"Cache miss for key: {cache_key}")
        return default
        
    except Exception as e:
      logging.error(f"Error getting cache for key {key}: {e}")
      return default

  def delete(self, key: str, namespace: Optional[str] = None) -> bool:
    """
    Delete a value from Redis cache
    
    Args:
      key: Cache key to delete
      namespace: Optional namespace
    
    Returns:
      bool: True if key was deleted, False otherwise
    """
    try:
      cache_key = self._get_key(key, namespace)
      result = self.redis_client.delete(cache_key)
      
      if result:
        logging.debug(f"Successfully deleted key: {cache_key}")
      return bool(result)
      
    except Exception as e:
      logging.error(f"Error deleting cache for key {key}: {e}")
      return False

  def exists(self, key: str, namespace: Optional[str] = None) -> bool:
    """Check if key exists in cache"""
    try:
      cache_key = self._get_key(key, namespace)
      return bool(self.redis_client.exists(cache_key))
    except Exception as e:
      logging.error(f"Error checking existence for key {key}: {e}")
      return False

  def clear_namespace(self, namespace: str) -> int:
    """
    Clear all keys in a namespace
    
    Args:
      namespace: Namespace to clear
    
    Returns:
      int: Number of keys deleted
    """
    try:
      pattern = f"{namespace}:*"
      keys = self.redis_client.keys(pattern)
      if keys:
        deleted = self.redis_client.delete(*keys)
        logging.info(f"Cleared {deleted} keys from namespace: {namespace}")
        return deleted
      return 0
    except Exception as e:
      logging.error(f"Error clearing namespace {namespace}: {e}")
      return 0

  def increment(self, key: str, namespace: Optional[str] = None, 
                amount: int = 1, ttl: Optional[int] = None) -> Optional[int]:
    """
    Increment a numeric value
    
    Args:
      key: Cache key
      namespace: Optional namespace
      amount: Amount to increment by
      ttl: TTL for the key if it doesn't exist
    
    Returns:
      New value after increment or None if error
    """
    try:
      cache_key = self._get_key(key, namespace)
      
      # Use pipeline for atomic operation
      pipe = self.redis_client.pipeline()
      pipe.incr(cache_key, amount)
      if ttl and not self.redis_client.exists(cache_key):
        pipe.expire(cache_key, ttl)
      
      results = pipe.execute()
      return results[0]
      
    except Exception as e:
      logging.error(f"Error incrementing key {key}: {e}")
      return None

  def get_stats(self) -> dict:
    """Get Redis connection and memory stats"""
    try:
      info = self.redis_client.info()
      return {
        'connected_clients': info.get('connected_clients'),
        'used_memory_human': info.get('used_memory_human'),
        'keyspace_hits': info.get('keyspace_hits', 0),
        'keyspace_misses': info.get('keyspace_misses', 0),
        'total_commands_processed': info.get('total_commands_processed', 0)
      }
    except Exception as e:
      logging.error(f"Error getting Redis stats: {e}")
      return {}

  def health_check(self) -> bool:
    """Kiểm tra trạng thái kết nối Redis"""
    try:
      return self.redis_client.ping()
    except Exception as e:
      logging.error(f"Redis health check failed: {e}")
      return False

  def clear_all(self) -> bool:
    """
    Clear tất cả cache trong database hiện tại
    
    Returns:
      bool: True if successful, False otherwise
    """
    try:
      result = self.redis_client.flushdb()
      if result:
        logging.info("Successfully cleared all cache")
      return result
    except Exception as e:
      logging.error(f"Error clearing all cache: {e}")
      return False

  def clear_all_redis(self) -> bool:
    """
    Clear tất cả cache trong tất cả Redis databases (NGUY HIỂM!)
    Chỉ sử dụng trong development/testing
    
    Returns:
      bool: True if successful, False otherwise
    """
    try:
      result = self.redis_client.flushall()
      if result:
        logging.warning("Successfully cleared ALL Redis data across all databases")
      return result
    except Exception as e:
      logging.error(f"Error clearing all Redis data: {e}")
      return False

  def get_all_keys(self, pattern: str = "*") -> list:
    """
    Lấy tất cả keys theo pattern
    
    Args:
      pattern: Pattern để search keys (default: "*" = tất cả)
    
    Returns:
      list: Danh sách keys
    """
    try:
      keys = self.redis_client.keys(pattern)
      logging.debug(f"Found {len(keys)} keys matching pattern: {pattern}")
      return keys
    except Exception as e:
      logging.error(f"Error getting keys with pattern {pattern}: {e}")
      return []

  def delete_by_pattern(self, pattern: str) -> int:
    """
    Xóa tất cả keys theo pattern
    
    Args:
      pattern: Pattern để xóa keys (vd: "user:*", "session:*")
    
    Returns:
      int: Số lượng keys đã xóa
    """
    try:
      keys = self.redis_client.keys(pattern)
      if keys:
        deleted = self.redis_client.delete(*keys)
        logging.info(f"Deleted {deleted} keys matching pattern: {pattern}")
        return deleted
      return 0
    except Exception as e:
      logging.error(f"Error deleting keys with pattern {pattern}: {e}")
      return 0

  def get_cache_size(self) -> dict:
    """
    Lấy thông tin về số lượng keys và memory usage
    
    Returns:
      dict: Cache size information
    """
    try:
      info = self.redis_client.info()
      dbsize = self.redis_client.dbsize()
      
      return {
        'total_keys': dbsize,
        'used_memory': info.get('used_memory', 0),
        'used_memory_human': info.get('used_memory_human', '0B'),
        'used_memory_peak_human': info.get('used_memory_peak_human', '0B'),
        'keyspace_hits': info.get('keyspace_hits', 0),
        'keyspace_misses': info.get('keyspace_misses', 0)
      }
    except Exception as e:
      logging.error(f"Error getting cache size info: {e}")
      return {}

  def close(self):
    """Đóng connection pool"""
    try:
      self.redis_client.close()
      logging.info("Redis connections closed")
    except Exception as e:
      logging.error(f"Error closing Redis connections: {e}")
      
_cache_instance = None
def get_cache() -> RedisMemcache:
  """Get singleton cache instance"""
  global _cache_instance
  if _cache_instance is None:
    _cache_instance = RedisMemcache()
  return _cache_instance

def set(key: str, value: Any, namespace: Optional[str] = None, time: Optional[Union[int, timedelta]] = None) -> bool:
	"""Set a value in Redis cache"""
	cache = get_cache()
	return cache.set(key, value, namespace, time)

def get(key: str, namespace: Optional[str] = None, default: Any = None) -> Any:
	"""Get a value from Redis cache"""
	cache = get_cache()
	return cache.get(key, namespace, default)

def delete(key: str, namespace: Optional[str] = None) -> bool:
	"""Delete a value from Redis cache"""
	cache = get_cache()
	return cache.delete(key, namespace)

def clear_all_cache():
  """Utility function để clear tất cả cache"""
  cache = get_cache()
  return cache.clear_all()

def clear_cache_by_pattern(pattern: str):
  """Utility function để clear cache theo pattern"""
  cache = get_cache()
  return cache.delete_by_pattern(pattern)

def get_cache_info():
  """Utility function để lấy thông tin cache"""
  cache = get_cache()
  return {
    'size_info': cache.get_cache_size(),
    'stats': cache.get_stats(),
    'health': cache.health_check()
  }