from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from musixfy.utils.ApiClient import ApiClient

# Load Env Variables
load_dotenv()

app = Flask(__name__)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Define All Dependencies

apiClient = ApiClient()


# Global Functions

@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response


def iterate_data(resp, chunk=2048):
    for data_chunk in resp.iter_content(chunk_size=chunk):
        yield data_chunk

