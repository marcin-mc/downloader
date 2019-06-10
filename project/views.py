"""
Standard Flask views with routing
"""


import os
from threading import Thread

from flask import jsonify

from project import (
    database,
    downloader,
)
from project.app import app


@app.route('/download/<data_type>/<path:url>', methods=['POST'])
def download(data_type, url):
    if data_type == 'text':
        target = downloader.download_text
    elif data_type == 'images':
        target = downloader.download_images
    else:
        return jsonify({'error': 'Use "download/text/<url>" or "download/images/<url>"'}), 400
    response = downloader.check_url(url)
    if not response:
        return jsonify({'error': 'Invalid URL or page cannot be accessed.'}), 400
    fetch_url = Thread(target=target, args=(url, response))
    fetch_url.start()
    context = {
        'URL': url,
        'fetching': data_type,
    }
    return jsonify(context), 201


@app.route('/status/<data_type>/<path:url>', methods=['GET'])
def status(url, data_type):
    if not data_type in ['images', 'text']:
        return jsonify({'error': 'Use "status/text/<url>" or "status/images/<url>"'})
    task = database.get_task(url, data_type)
    if not task:
        return jsonify({'error': 'URL has not been found in the database.'}), 400
    context = {
        'status': str(task.status),
        'URL': url,
    }
    return jsonify(context), 200


@app.route('/get/text/<path:url>', methods=['GET'])
def get_text(url):
    task = database.get_task(url, 'text')
    if not task:
        return jsonify({'error': 'URL has not been found in the database.'}), 400
    if task.status != 'ready':
        return jsonify(
            {'error': 'Downloading text from this URL has not been completed yet.'}), 400
    with open(task.location, 'rt', encoding='utf8') as file:
        text = file.read()
    return jsonify({'text': text})


@app.route('/get/images/<path:url>', methods=['GET'])
def get_images(url):
    task = database.get_task(url, 'images')
    if not task:
        return jsonify({'error': 'URL has not been found in the database.'}), 400
    if task.status != 'ready':
        return jsonify(
            {'error': 'Downloading images from this URL has not been completed yet.'}), 400
    location = task.location
    filepaths = [os.path.join(location, filename) for filename in os.listdir(location)]
    return jsonify({'images': filepaths})
