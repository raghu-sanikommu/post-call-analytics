# Download a file from the container
def download_blob_from_container(blob_name, download_file_path):
  blob_client = container_client.get_blob_client(blob_name)
  with open(download_file_path, "wb") as download_file:
    download_file.write(blob_client.download_blob().readall())
  print(f"Downloaded {blob_name} to {download_file_path}")
  
# download_blob_from_container("remote_file_name.txt", "path/to/download/file.txt")