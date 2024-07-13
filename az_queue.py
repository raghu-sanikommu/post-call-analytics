# Package Imports
from azure.storage.queue import QueueClient
import json

# File Imports
import config


class Queue:
  def __init__(self) -> None:
    self.client = QueueClient.from_connection_string(
      conn_str=config.BLOB_CONNECTION_STRING, queue_name=config.QUEUE_NAME)

  def push(self, message):
    json_message = json.dumps(message)
    self.client.send_message(
      json_message
    )
    
    return True
