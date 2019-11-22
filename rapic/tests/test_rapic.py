"""Tests for rapic Client."""
import unittest
import os
from rapic.client import APIClient
from rapic.exceptions import RapicException


class TestRapic(unittest.TestCase):

    def setUp(self):
        curr_dir = os.path.dirname(__file__)
        httpbin_file = os.path.join(curr_dir, 'httpbin.json')
        httpbin_file_2 = os.path.join(curr_dir, 'httpbin_2.json')
        httpbin_file_3 = os.path.join(curr_dir, 'httpbin_3.json')
        httpbin_file_4 = os.path.join(curr_dir, 'httpbin_4.json')
        self.httpbin = APIClient('httpbin', httpbin_file)
        self.httpbin_2 = APIClient('httpbin', httpbin_file_2)
        self.httpbin_3 = APIClient('httpbin', httpbin_file_3)
        self.httpbin_4 = APIClient('httpbin', httpbin_file_4)

    def test_client_can_load_client_requests_directly(self):
        """Request can be specified in json file under a client directly
            A rapic client should be able to extract all the request from it
        """

        req = self.httpbin.get_request_data('get_my_ip')
        self.assertEqual(req, self.httpbin.client['get_my_ip'])
        req = self.httpbin.get_request_data('get_my_headers')
        self.assertEqual(req, self.httpbin.client['get_my_headers'])

        req = self.httpbin_2.get_request_data('get_my_ip')
        self.assertEqual(req, self.httpbin_2.client['get_my_ip'])
        req = self.httpbin_2.get_request_data('get_my_headers')
        self.assertEqual(req, self.httpbin_2.client['get_my_headers'])

    def test_client_can_load_client_page_requests_directly(self):
        """Request can be specified in json file  under pages of client
        requests are grouped by pages and does not exist under client direclty
            A rapic client should be able to extract all the request from it
        """

        req = self.httpbin_3.get_request_data('get_my_ip')

        self.assertEqual(req, self.httpbin_3.client["homepage"]['get_my_ip'])
        req = self.httpbin_3.get_request_data('test_requests_patch_method')
        self.assertEqual(req, self.httpbin_3.client["homepage"]['test_requests_patch_method'])
        req = self.httpbin_3.get_request_data('test_requests_delete_method')
        self.assertEqual(req, self.httpbin_3.client["second_page"]['test_requests_delete_method'])

        req = self.httpbin_4.get_request_data('get_my_ip')
        self.assertEqual(req, self.httpbin_4.client['get_my_ip'])
        req = self.httpbin_4.get_request_data('get_user_my_agent')
        self.assertEqual(req, self.httpbin_4.client['get_user_my_agent'])
        req = self.httpbin_4.get_request_data('test_requests_put_method')
        self.assertEqual(req, self.httpbin_4.client['test_requests_put_method'])
        req = self.httpbin_4.get_request_data('test_requests_post_method')
        self.assertEqual(req, self.httpbin_4.client['test_requests_post_method'])

    def test_client_exception_for_invalid_request(self):
        self.assertRaises(RapicException, self.httpbin_3.get_request_data, 'action_not_in_client_json_file')

    def test_run_method_get_ip(self):
        req = self.httpbin.get_my_ip()
        self.assertEqual(req.status_code, 200)

    def tearDown(self):
        self.httpbin.close()
