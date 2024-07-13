# Package Imports
from flask import Flask, request, jsonify

# File Imports
from services import Services

app = Flask(__name__)
services = Services()

@app.get('/health')
def health_check():
  return jsonify({"status": 200, "message": "Ok"})

@app.post('/upload_and_transcribe')
def upload_and_transcribe():
  return services.upload_and_transcribe(request)

if __name__ == "__main__":
    app.run(debug=True)