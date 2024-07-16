# Package Imports
from azure.storage.queue import QueueClient, TextBase64EncodePolicy, TextBase64DecodePolicy
import json

# File Imports
import config


class Queue:
  def __init__(self) -> None:
    self.client = QueueClient.from_connection_string(
      conn_str=config.BLOB_CONNECTION_STRING, queue_name=config.QUEUE_NAME)
    self.client._message_encode_policy = TextBase64EncodePolicy()
    self.client._message_decode_policy = TextBase64DecodePolicy()

  def push(self, message):
    message_string = json.dumps(message)
    self.client.send_message(
      self.client._message_encode_policy.encode(content=message_string)
    )
    
    return True
