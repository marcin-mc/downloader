"""
Downloader module is responsible for:
creating tasks (through 'database' module),
downloading page contents,
parsing page contents,
writing text and images to proper locations on disk,
updating tasks when downloading data is finished (through 'database' module),
"""

import os
import re
from urllib.parse import (
    urlparse,
    urlunparse,
)

import requests
from bs4 import BeautifulSoup

from project import database

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_PATH = os.path.join(BASE_PATH, 'images')
TEXT_PATH = os.path.join(BASE_PATH, 'text')


def check_url(url):
    """
    Quickly check if the URL is valid
    and give feedback to client if
    there is any problem with the URL.
    :returns response or None
    """
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
    except requests.exceptions.ConnectionError:
        return None
    return response


def make_soup(response):
    content = response.content
    return BeautifulSoup(content, features="lxml")


def slugify(text, delim='-'):
    """Generates an ASCII-only slug."""
    punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')
    result = []
    for word in punct_re.split(text.lower()):
        result.extend(word.split())
    return delim.join(result)


def download_text(url, response):
    soup = make_soup(response)
    task_id = database.create_task(url, 'text')
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()
    if text:
        filename = slugify(url)
        filename = '{}.txt'.format(filename)
        full_path = os.path.join(TEXT_PATH, filename)
        with open(full_path, 'wt', encoding='utf8') as file:
            file.write(text)
        database.update_task_ready(task_id, full_path)


def download_images(url, response):
    soup = make_soup(response)
    task_id = database.create_task(url, 'images')
    images = [img for img in soup.findAll('img')]
    if images:
        dir_name = slugify(url)
        dir_full_path = os.path.join(IMAGE_PATH, dir_name)
        os.makedirs(dir_full_path, exist_ok=True)
        images_url = urlunparse(urlparse(url)._replace(path='/'))
        for image in images:
            link = image.get('src')
            if not link.startswith("http"):
                link = images_url + link
            filename = link.split('/')[-1]
            filename = re.sub('\?.*', '', filename)
            full_path = os.path.join(dir_full_path, filename)
            data = requests.get(link)
            with open(full_path, 'wb') as file:
                file.write(data.content)
        database.update_task_ready(task_id, dir_full_path)
