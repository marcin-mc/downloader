import os
import tempfile
import unittest
from unittest.mock import (
    patch,
    mock_open,
)

from project.app import (
    app,
    db,
)
from project.database import Task


class TestAPI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        _, cls.database = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(cls.database)
        db.create_all()
        task_text = Task(url='http://www.myurl.org/',
                         type='text',
                         status='ready',
                         location='fs/text/http-myurl-org/')
        db.session.add(task_text)
        task_images = Task(url='http://www.myurl.org/',
                           type='images',
                           status='ready',
                           location='fs/images/http-myurl-org/')
        db.session.add(task_text)
        db.session.add(task_images)
        db.session.commit()
    
    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.database)

    @patch('project.downloader.download_text')
    @patch('project.downloader.check_url', return_value=True)
    @patch('project.views.Thread')
    def test_download_text(self, thread, check_url, download_text):
        response = self.client.post('/download/text/http://www.myurl.org/')
        thread.assert_called_with(target=download_text, args=('http://www.myurl.org/', check_url()))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'fetching': 'text', 'URL': 'http://www.myurl.org/'})
    
    @patch('project.downloader.download_images')
    @patch('project.downloader.check_url', return_value=True)
    @patch('project.views.Thread')
    def test_download_images(self, thread, check_url, download_images):
        response = self.client.post('/download/images/http://www.myurl.org/')
        thread.assert_called_with(target=download_images, args=('http://www.myurl.org/', check_url()))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'fetching': 'images', 'URL': 'http://www.myurl.org/'})
    
    def test_status_missing(self):
        response = self.client.get('/status/text/http://missingurl.org/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'URL has not been found in the database.'})
    
    def test_status_present(self):
        response = self.client.get('/status/text/http://www.myurl.org/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'URL': 'http://www.myurl.org/', 'status': 'ready'})
    
    def test_get_text_missing_url(self):
        response = self.client.get('/get/text/http://www.missingurl.org/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'URL has not been found in the database.'})
    
    @patch('builtins.open', mock_open(read_data='Text content from http://www.myurl.org'))
    def test_get_text(self):
        response = self.client.get('/get/text/http://www.myurl.org/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'text': 'Text content from http://www.myurl.org'})
    
    @patch('project.views.os.listdir')
    @patch('project.views.os.path.join')
    def test_get_images(self, join, listdir):
        """
        As we aren't testing writing to disk here,
        both directory listing and joining
        images' paths must be mocked.
        """
        
        def _join(path, filename):
            return path + filename
        
        join.side_effect = _join
        listdir.return_value = [
            'image1.jpg', 'image2.jpg',
        ]
        response = self.client.get('/get/images/http://www.myurl.org/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'images': [
            'fs/images/http-myurl-org/image1.jpg',
            'fs/images/http-myurl-org/image2.jpg'
        ]})


if __name__ == '__main__':
    unittest.main()
