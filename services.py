# Package Imports
from flask import jsonify
import os
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import subprocess

# File Imports
import config
from db import MongoDB
from az_queue import Queue

class Services:
  def __init__(self) -> None:
    self.mongodb = MongoDB()
    self.queue = Queue()
    self.local_audio_path_generic = ""
    #? Audio Formatter Configs
    # self.local_audio_path_converted = "audios/audio.wav"
    self.local_audio_path_converted = "audios/audio.opus"
  
  """
  - Connect to blob storage
  - Save the incoming file in fs
  - Convert it to .wav/.opus format
  - Upload it into blob
  - Remove files from fs
  - Generate shareable blob url
  - Push {blob_url, project_id, txion_status, uuid} to DB
  - Push {blob_url, uuid} to queue
  """
  def upload_and_transcribe(self, request):
    # - Connect to blob storage
    container_name = config.BLOB_CONTAINER_NAME
    connection_string = config.BLOB_CONNECTION_STRING

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    print('Connected to blob storage ...')

    form_data = request.form
    file = request.files.get('file')
    project_id = form_data.get('projectId')
    
    if ((not file) or (not file.filename)):
      return jsonify({"status": 500, "message": "No file is found"})
    
    # - Save the file in fs
    self.local_audio_path_generic = file.filename.replace(" ", "_").replace("/", "_")
    splitted_filename = file.filename.split(".")
    splitted_filename = splitted_filename[0:-1]
    #? Audio Formatter Configs
    # formatted_filename_for_blob = project_id + "/" + "".join(splitted_filename) + ".wav"
    formatted_filename_for_blob = project_id + "/" + "".join(splitted_filename) + ".opus"
    
    file.save(self.local_audio_path_generic)
    
    # - Convert it into wav/opus
    #? Audio Formatter Configs
    def convert_audio_to_wav():
      command = ["ffmpeg", "-i", self.local_audio_path_generic, self.local_audio_path_converted]
      subprocess.run(command, check=True)
    
    def convert_audio_to_opus():
      command = ["ffmpeg", "-i", self.local_audio_path_generic, self.local_audio_path_converted]
      subprocess.run(command, check=True)
      
    # convert_audio_to_wav()
    convert_audio_to_opus()
    
    # - Upload it into blob
    def upload_file_to_container(file_path, blob_name):
      with open(file_path, "rb") as data:
        print("Uploading audio file ...")
        container_client.upload_blob(name=blob_name, data=data)
      print(f"Uploaded {file_path} to {blob_name} in the container {container_name}")
    
    upload_file_to_container(self.local_audio_path_converted, formatted_filename_for_blob)
    
    # - Remove files from fs
    os.remove(self.local_audio_path_generic)
    os.remove(self.local_audio_path_converted)
    
    # - Generate shareable blob url
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=formatted_filename_for_blob,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )

    blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{formatted_filename_for_blob}?{sas_token}"
    
    # - Push {blob_url, project_id, txion_status} to DB
    db_record_inserted = self.mongodb.insert_one(record={
      "projectId": project_id,
      "blobUrl": blob_url,
      "status": "UPLOADED",
    })
    print(f"Record inserted in DB :: {db_record_inserted.inserted_id}")
    
    # - Push {blob_url, id} to queue
    self.queue.push({"blobUrl": blob_url, "id": str(db_record_inserted.inserted_id)})
    print('Pushed message to queue.')

    return jsonify({"projectId": project_id, "blob_url": blob_url})