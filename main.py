import argparse
import logging

from flask import Flask
from google.cloud import storage

import jinja2 

import noaa
import nwac

app = Flask(__name__)

def fetch():
	client = storage.Client()
	bucket = client.get_bucket('bakercrew')
	index_html = bucket.get_blob('index.html').download_as_string()
	index_html = index_html.decode('UTF-8')

	nwac_data = eval(nwac.fetch())

	template = jinja2.Template(index_html)
	return template.render(nwac_data)

def upload_html():
	client = storage.Client()
	bucket = client.get_bucket('bakercrew')
	bucket.blob('index.html').upload_from_filename(filename='index.html')

@app.route('/')
def home():
    return fetch()

@app.route('/noaa')
def noaa_debug():
	return str(noaa.fetch())

@app.route('/nwac')
def nwac_debug():
	return nwac.fetch()
	

# This is used when running locally. Gunicorn is used to run the
# application on Google App Engine. See entrypoint in app.yaml.
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-u', '--upload', help='Upload local html files to Cloud Storage', action='store_true')
	args = parser.parse_args()
	if args.upload:
		upload_html()
	app.run(host='127.0.0.1', port=8080, debug=True)



