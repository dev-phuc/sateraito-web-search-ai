import os
import uuid
import json
import numpy as np
import redis
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
# sateraito_inc.py から設定取得するように変更
#from dotenv import load_dotenv
import sateraito_inc
from ..utils.constant import REDIS_REQUIRED_MODULES
# メモリ使用量が大きいライブラリを使用している。現状未使用なのでいったんコメントアウト
#from ..document_loaders.document import Document
from enum import Enum

def check_redis_module_exist(client, modules):
    installed_modules = client.module_list()
    installed_modules = {
        module[b"name"].decode("utf-8"): module for module in installed_modules
    }
    for module in modules:
        if module["name"] not in installed_modules or int(
            installed_modules[module["name"]][b"ver"]
        ) < int(module["ver"]):
            error_message = (
                "You must add the RediSearch (>= 2.4) module from Redis Stack. "
                "Please refer to Redis Stack docs: https://redis.io/docs/stack/"
            )
            raise ValueError(error_message)
        
def redis_prefix(index_name):
    return f'doc:{index_name}'

def redis_key(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"

def check_index_exists(client, index_name) -> bool:
    try:
        client.ft(index_name).info()
    except:
        print("Index does not exist")
        return False
    print("Index already exists")
    return True

class RedisSearchType(Enum):
    FLAT = 'FLAT'
    HNSW = 'HNSW'

class Redis():
    def __init__(
            self, 
            redis_url, 
            index_name, 
            embedding_function, 
            id_key = 'chunk_id',
            vector_key = 'embedding'):
        self.index_name = index_name
        self.embedding_function = embedding_function
        self.id_key = id_key
        self.vector_key = vector_key

        try:
            redis_client = redis.from_url(redis_url)
            check_redis_module_exist(redis_client, REDIS_REQUIRED_MODULES)
        except ValueError as e:
            raise ValueError(f"Redis failed to connect: {e}")
        
        self.client = redis_client
    
    def similarity_search(self, query, k=5):
        chunk_id_scores = self.similarity_search_with_score(query, k=k)
        return [chunk_id for chunk_id, _ in chunk_id_scores]

    def similarity_search_limit_score(self, query, k=5, score_threshold=0.2):
        chunk_id_scores = self.similarity_search_with_score(query, k=k)
        return [chunk_id for chunk_id, score in chunk_id_scores if score < score_threshold]

    def similarity_search_with_score(self, query, k=5):
        # Creates embedding vector from user query
        embedding = self.embedding_function(query)
        # Prepare the Query
        return_fields = [self.id_key, "vector_score"]
        vector_field = self.vector_key
        hybrid_fields = "*"
        base_query = (
            f"{hybrid_fields}=>[KNN {k} @{vector_field} $vector AS vector_score]"
        )
        redis_query = (
            Query(base_query)
            .return_fields(*return_fields)
            .sort_by("vector_score")
            .paging(0, k)
            .dialect(2)
        )
        params_dict = {
            "vector": np.array(embedding)
            .astype(dtype=np.float32)
            .tobytes()
        }
        # perform vector search
        results = self.client.ft(self.index_name).search(redis_query, params_dict)
        chunk_id_scores = [
            (
                result.chunk_id,
                float(result.vector_score),
            )
            for result in results.docs
        ]
        return chunk_id_scores
    
    def get_keys_of_index(self, index_name):
        prefix = redis_prefix(index_name)
        return self.client.keys(f'{prefix}*')
    
    def set_expire_of_index(self, index_name, time):
        keys = self.get_keys_of_index(index_name)
        for key in keys:
            self.client.expire(key, time)

    def set_expire_of_index(self, index_name, time):
        keys = self.get_keys_of_index(index_name)
        for key in keys:
            self.client.expire(key, time)
    
    @classmethod
    def from_embeddings_info(
        cls,
        embedding_model,
        embeddings_info,
        index_name=None,
        id_key='chunk_id', 
        vector_key='embedding',
        search_type=RedisSearchType.HNSW):

        # sateraito_inc.py から設定取得するように変更
        #if os.getenv('REDIS_URL') is None:
        #    load_dotenv()
        
        # sateraito_inc.py から設定取得するように変更
        #redis_url = os.getenv('REDIS_URL')
        redis_url = sateraito_inc.REDIS_URL
        try:
            client = redis.from_url(url=redis_url)
            check_redis_module_exist(client, REDIS_REQUIRED_MODULES)
        except ValueError as e:
            raise ValueError(f'Redis failed to connect {e}')
        
        if not index_name:
            raise ValueError(f'Index name must be not none.')
        prefix = redis_prefix(index_name)
        embeddings = [info['embedding'] for info in embeddings_info]
        chunk_ids = [info['id'] for info in embeddings_info]
        if not check_index_exists(client, index_name):
            embedding_dimension = len(embeddings[0])
            distance_metric = (
                "COSINE"
            )
            schema = (
                TextField(name=id_key),
                VectorField(
                    vector_key,
                    search_type.value,
                    {
                        "TYPE": "FLOAT32",
                        "DIM": embedding_dimension,
                        "DISTANCE_METRIC": distance_metric,
                    },
                ),
            )
            # Create Redis Index
            client.ft(index_name).create_index(
                fields=schema,
                definition=IndexDefinition(prefix=[prefix], index_type=IndexType.HASH),
            )
        
        # Write data to Redis
        pipeline = client.pipeline(transaction=False)
        for i, chunk_id in enumerate(chunk_ids):
            key = redis_key(prefix)
            pipeline.hset(
                key,
                mapping={
                    id_key: chunk_id,
                    vector_key: np.array(embeddings[i], dtype=np.float32).tobytes(),
                },
            )
        pipeline.execute()
        return cls(
            redis_url,
            index_name,
            embedding_model.embed_text,
            id_key=id_key,
            vector_key=vector_key
        )
    
    @staticmethod
    def drop_index(index_name, delete_documents):
        # sateraito_inc.py から設定取得するように変更
        #if os.getenv('REDIS_URL') is None:
        #    load_dotenv()
        #redis_url = os.getenv('REDIS_URL')
        redis_url = sateraito_inc.REDIS_URL
        try:
            client = redis.from_url(url=redis_url)
        except ValueError as e:
            raise ValueError(f"Your redis connected error: {e}")
        # Check if index exists
        try:
            client.ft(index_name).dropindex(delete_documents)
            print("Drop index")
            return True
        except:
            # Index not exist
            return False
        
    @classmethod
    def check_index_exists(cls, index_name):
        # sateraito_inc.py から設定取得するように変更
        #if os.getenv('REDIS_URL') is None:
        #    load_dotenv()
        #redis_url = os.getenv('REDIS_URL')
        redis_url = sateraito_inc.REDIS_URL
        try:
            client = redis.from_url(url=redis_url)
            return check_index_exists(client, index_name)
        except Exception as e:
            raise ValueError(f"Redis failed to connect: {e}")

    @classmethod
    def from_existing_index(cls, embedding, index_name):
        # sateraito_inc.py から設定取得するように変更
        #if os.getenv('REDIS_URL') is None:
        #    load_dotenv()
        #redis_url = os.getenv('REDIS_URL')
        redis_url = sateraito_inc.REDIS_URL
        try:
            client = redis.from_url(url=redis_url)
            # check if redis has redisearch module installed
            check_redis_module_exist(client, REDIS_REQUIRED_MODULES)
            # ensure that the index already exists
            assert check_index_exists(client, index_name), f"Index {index_name} does not exist"
        except Exception as e:
            raise ValueError(f"Redis failed to connect: {e}")
        return cls(redis_url, index_name, embedding.embed_text)
