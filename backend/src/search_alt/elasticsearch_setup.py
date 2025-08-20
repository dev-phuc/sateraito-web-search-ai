# encoding: utf-8
# WARN: this file only need run in local 1 time when setup new elasticsearch cluster server

import json
from sateraito_logger import logging
# logging.basicConfig(level=logging.INFO)
# import sateraito_logger as logging

# from . import utilities
# IS_GAE = utilities.check_is_running_gae()
# IS_PYTHON_3 = utilities.IS_PYTHON_3
# 
# if IS_GAE and IS_PYTHON_3:
#   import sateraito_logger as logging
# else:
#   import logging

# import elasticsearch_inc
# import elasticsearch_func
# import utilities
from . import elasticsearch_inc
from . import elasticsearch_func
from . import utilities


DOCUMENT_KEY_INTERNAL_TIMESTAMP = elasticsearch_inc.DOCUMENT_KEY_INTERNAL_TIMESTAMP

ID_PIPELINE_AUTOMATIC_TIMESTAMP = "automatic_timestamp"

# default elasticsearch limit is 1000 or 2000 for performance reason
# just to increase this limit to 100000 for make sure that elastic search don't throw error when we create new index that need more sharps than default
# increase this limit not make elasticsearch do slower, but create more sharps when create index will make elasticsearch slower
LIMIT_NUMBER_OF_SHARDS_IN_CLUSTER = 100000


def setup_number_of_sharps_in_cluster():
  es = elasticsearch_func.get_client()
  cluster_settings = es.cluster.get_settings()
  # utilities.print_yaml(cluster_settings)
  current_number_of_shards = None
  try:
    current_number_of_shards = cluster_settings["persistent"]["cluster"]["routing"]["allocation"]["total_shards_per_node"]
  except KeyError:
    pass
  if current_number_of_shards != LIMIT_NUMBER_OF_SHARDS_IN_CLUSTER:
    result = es.cluster.put_settings(body={
      "persistent": {
        "cluster.routing.allocation.total_shards_per_node": LIMIT_NUMBER_OF_SHARDS_IN_CLUSTER,
        # "cluster.max_shards_per_node": 1000,
      }
    })
    utilities.print_yaml(result)


def setup_pipeline_automatic_timestamp():
  es = elasticsearch_func.get_client()
  pipeline = {
    "description": "Add automatic timestamp when index a document",
    "processors": [
      {
        "set": {
          "field": DOCUMENT_KEY_INTERNAL_TIMESTAMP,
          "value": "{{_ingest.timestamp}}"
        }
      }
    ]
  }

  result = es.ingest.get_pipeline(id=ID_PIPELINE_AUTOMATIC_TIMESTAMP, ignore=404)
  if result and not result.get("error"):
    # utilities.print_yaml(result)
    pipeline_current = result.get(ID_PIPELINE_AUTOMATIC_TIMESTAMP)
    if pipeline_current:
      pipeline_current_val = json.dumps(pipeline_current, sort_keys=True)
      pipeline_val = json.dumps(pipeline, sort_keys=True)
      if pipeline_current_val != pipeline_val:
        result = es.ingest.delete_pipeline(id=ID_PIPELINE_AUTOMATIC_TIMESTAMP)
        utilities.print_yaml(result)

  result = None
  result = es.ingest.put_pipeline(id=ID_PIPELINE_AUTOMATIC_TIMESTAMP, body=pipeline)

  utilities.print_yaml(result)


def setup_enable_id_field_data():
  es = elasticsearch_func.get_client()
  
  result = es.cluster.put_settings(
    body={
        "transient": {
            "indices.id_field_data.enabled": True
        }
    }
  )
  utilities.print_yaml(result)


def process_setup():
  setup_number_of_sharps_in_cluster()

  setup_pipeline_automatic_timestamp()

  # setup_enable_id_field_data()


def main():
  process_setup()

if __name__ == "__main__":
  main()
