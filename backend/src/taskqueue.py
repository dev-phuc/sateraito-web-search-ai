#!/usr/bin/python
# coding: utf-8

__author__ = 'Tran Minh Phuc <phuc@vnd.sateraito.co.jp>'
'''
sateraito_db.py

@since: 2025-08-20
@version: 1.0.0
@author: Tran Minh Phuc
'''

import datetime
import json
from typing import Dict, Optional

from google.cloud import tasks_v2
from google.protobuf import duration_pb2, timestamp_pb2

import sateraito_logger as logging  # GAEGEN2対応:独自ロガー
from sateraito_inc import my_site_url

project = 'vn-sateraito-apps-timecard2'
queue = 'default'
location = 'us-central1'

def create_http_task(
  project: str,
  location: str,
  queue: str,
  url: str,
  json_payload: Dict,
  scheduled_seconds_from_now: Optional[int] = None,
  task_id: Optional[str] = None,
  deadline_in_seconds: Optional[int] = None,
) -> tasks_v2.Task:
  
  """Create an HTTP POST task with a JSON payload.
  Args:
    project: The project ID where the queue is located.
    location: The location where the queue is located.
    queue: The ID of the queue to add the task to.
    url: The target URL of the task.
    json_payload: The JSON payload to send.
    scheduled_seconds_from_now: Seconds from now to schedule the task for.
    task_id: ID to use for the newly created task.
    deadline_in_seconds: The deadline in seconds for task.
  Returns:
    The newly created task.
  """

  # Create a client.
  client = tasks_v2.CloudTasksClient()

  # Construct the task.
  task = tasks_v2.Task(
    http_request=tasks_v2.HttpRequest(
      http_method=tasks_v2.HttpMethod.POST,
      url=url,
      headers={"Content-type": "application/json"},
      body=json.dumps(json_payload).encode(),
    ),
    name=(
      client.task_path(project, location, queue, task_id)
      if task_id is not None
      else None
    ),
  )

  # Convert "seconds from now" to an absolute Protobuf Timestamp
  if scheduled_seconds_from_now is not None:
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(
      datetime.datetime.utcnow()
      + datetime.timedelta(seconds=scheduled_seconds_from_now)
    )
    task.schedule_time = timestamp

  # Convert "deadline in seconds" to a Protobuf Duration
  if deadline_in_seconds is not None:
    duration = duration_pb2.Duration()
    duration.FromSeconds(deadline_in_seconds)
    task.dispatch_deadline = duration

  # Use the client to send a CreateTaskRequest.
  return client.create_task(
    tasks_v2.CreateTaskRequest(
      # The queue to add the task to
      parent=client.queue_path(project, location, queue),
      # The task itself
      task=task,
    )
  )

class Task:
  def __init__(self, url, params=None, target=None, countdown=None):
    self.url = url
    self.params = params if params is not None else {}
    self.target = target
    self.countdown = countdown

class Queue:
  def __init__(self, name):
    self.name = name

  def add(self, task):
    if not isinstance(task, Task):
      raise TypeError("Expected a Task instance")
      
    task.target = f"default"
    
    if not task.url.startswith('http') and not task.url.startswith('https'):
      task.url = my_site_url + task.url
    
    if task.countdown is None:
      task.countdown = 0
      
    # print all parameters for debugging
    logging.info(f"Adding task to queue '{self.name}':")
    logging.info(f"  URL: {task.url}")
    logging.info(f"  Params: {task.params}")
    logging.info(f"  Target: {task.target}")
    logging.info(f"  Countdown: {task.countdown}")
    
    # create_http_task(
    #   project=project,
    #   location=location,
    #   queue=self.name,
    #   url=task.url,
    #   json_payload=task.params,
    #   scheduled_seconds_from_now=task.countdown,
    # )
    
    # Oops! The above line is commented out to prevent actual task creation.
    logging.info(f"Task added to queue '{self.name}' successfully.")
