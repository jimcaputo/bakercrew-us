import argparse
import logging

from flask import Flask
from google.cloud import storage

import jinja2

import noaa
import nwac

app = Flask(__name__)
run_local = False


def fetch():
    if run_local:
        charts_html = open('charts.html', 'r').read()
        noaa_html = open('noaa.html', 'r').read()
        nwac_html = open('nwac.html', 'r').read()
        index_html = open('index.html', 'r').read()
    else:
        client = storage.Client()
        bucket = client.get_bucket('bakercrew')
        charts_html = bucket.get_blob('charts.html').download_as_string().decode('UTF-8')
        noaa_html = bucket.get_blob('noaa.html').download_as_string().decode('UTF-8')
        nwac_html = bucket.get_blob('nwac.html').download_as_string().decode('UTF-8')
        index_html = bucket.get_blob('index.html').download_as_string().decode('UTF-8')

    noaa_results = noaa.fetch()
    nwac_results = nwac.fetch()

    charts_render = jinja2.Template(charts_html).render({'noaa_data': noaa_results, 'nwac_data': nwac_results})
    noaa_render = jinja2.Template(noaa_html).render({'noaa_data': noaa_results})
    nwac_render = jinja2.Template(nwac_html).render({'nwac_data': nwac_results})
    return jinja2.Template(index_html).render({'charts': charts_render, 'noaa': noaa_render, 'nwac': nwac_render})


def upload_html():
    client = storage.Client()
    bucket = client.get_bucket('bakercrew')
    bucket.blob('charts.html').upload_from_filename(filename='charts.html')
    bucket.blob('noaa.html').upload_from_filename(filename='noaa.html')
    bucket.blob('nwac.html').upload_from_filename(filename='nwac.html')
    bucket.blob('index.html').upload_from_filename(filename='index.html')


@app.route('/')
def home():
    return fetch()

@app.route('/noaa')
def noaa_debug():
    return noaa.fetch()

@app.route('/nwac')
def nwac_debug():
    return nwac.fetch()


# This is used when running locally. Gunicorn is used to run the
# application on Google App Engine. See entrypoint in app.yaml.
if __name__ == '__main__':
    run_local = True

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--upload', help='Upload local html files to Cloud Storage', action='store_true')
    args = parser.parse_args()
    if args.upload:
        upload_html()
        print('All files uploaded to Cloud Storage')
    else:
        app.run(host='127.0.0.1', port=8080, debug=True)



