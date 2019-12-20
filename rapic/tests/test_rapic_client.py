"""Tests for rapic Client."""
import unittest
import json
import os
import requests
from urllib.parse import urlencode, urlparse, quote
from rapic.client import APIClient
from rapic.exceptions import RapicException, RapicMissingUrlData


class TestRapicClient(unittest.TestCase):

    def setUp(self):
        curr_dir = os.path.dirname(__file__)

        httpbin_file = os.path.join(curr_dir, 'httpbin.json')
        httpbin_file_2 = os.path.join(curr_dir, 'httpbin_2.json')
        httpbin_file_3 = os.path.join(curr_dir, 'httpbin_3.json')
        httpbin_file_4 = os.path.join(curr_dir, 'httpbin_4.json')

        self.bad_proxies = {'http':'http://10.10.1.11:1080',  'https':'https://10.10.1.11:1080'}

        self.httpbin = APIClient('httpbin', httpbin_file)
        self.httpbin_2 = APIClient('httpbin', httpbin_file_2, loads_nested=True)
        self.httpbin_3 = APIClient('httpbin', httpbin_file_3)
        self.httpbin_4 = APIClient('httpbin', httpbin_file_4, loads_nested=True)
        self.httpbin_5 = APIClient('httpbin', httpbin_file_4, loads_nested=True, proxies = self.bad_proxies, timeout=3)

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
        """A request not present in json file should generate a RapicException on access"""
        self.assertRaises(RapicException, self.httpbin_3.get_request_data, 'request_not_in_client_json_file')

    def test_default_headers_sent_with_request(self):
        """All request must send client default headers unless the particular header has been
            overide by the request
        """
        req = self.httpbin.get_my_ip(dry_run=True)
        self.assertIn('All-Request-Headers', req.prepared_request.headers)
        self.assertEqual(req.prepared_request.headers['All-Request-Headers'],
                         self.httpbin.client["default_headers"]['All-Request-Headers'])

    def test_default_default_url_query_sent_with_request(self):
        """All request must send client default url query unless the particular url query has been
                    override by the request
                """
        req = self.httpbin.get_my_ip(dry_run=True)

        def_url_query = self.httpbin.client["default_url_query"]
        self.assertIn(urlencode(def_url_query), req.prepared_request.url)

    def test_default_default_body_sent_with_request(self):
        """All request must send client default body unless the particular body data has been
                            override by the request
                        """
        req = self.httpbin.get_my_ip(dry_run=True)
        def_body = self.httpbin.client["default_data"]
        self.assertIn(urlencode(def_body), req.prepared_request.body)

    def test_correct_sheme_host_sent_with_request(self):
        """The scheme and host should be taken directly from the main client file
            unless present in the request section directly in the json file
        """
        req = self.httpbin.get_my_ip(dry_run=True)
        self.assertIn(self.httpbin.client['host'], urlparse(req.prepared_request.url).netloc)
        self.assertIn(self.httpbin.client['scheme'], urlparse(req.prepared_request.url).scheme)
        self.assertIn(self.httpbin.client['get_my_ip']['path'], urlparse(req.prepared_request.url).path)

    def test_specific_headers_sent_with_request(self):
        """All request must send it own headers unless the particular if any is provided
                """
        req = self.httpbin.get_my_headers(dry_run=True)
        self.assertIn('All-Request-Headers', req.prepared_request.headers)
        request_data_headers = self.httpbin.client['get_my_headers']['headers']['All-Request-Headers']
        self.assertEqual(req.prepared_request.headers['All-Request-Headers'], request_data_headers)

    def test_user_headers_sent_with_request(self):
        """Headers can also bet set directly on a request during an api call """
        user_header = {'All-Request-Headers': 'Headers from user code'}
        req = self.httpbin.get_my_headers(headers=user_header, dry_run=True)
        self.assertIn('All-Request-Headers', req.prepared_request.headers)
        self.assertEqual(req.prepared_request.headers['All-Request-Headers'], user_header['All-Request-Headers'])

    def test_specific_url_is_used_for_request(self):
        """The url to use for a request can be set directly in the request part in the json file
            This will over ride any url or url parts in the request and client part
        """
        req = self.httpbin.get_my_headers(dry_run=True)

        url = self.httpbin.client["get_my_headers"]["url"]
        self.assertIn(url, req.prepared_request.url)

    def test_specific_default_body_sent_with_request(self):
        """The body of a request can be set directly in the request part in the json file
                    This will over ride any   client part
                """
        req = self.httpbin.get_my_headers(dry_run=True)
        def_body = self.httpbin.client["get_my_headers"]["data"]
        self.assertIn(urlencode(def_body), req.prepared_request.body)

    def test_specific_url_query_sent_with_request(self):
        """The url query of a request can be set directly in the request part of the json file
                    This will over ride any   client part
                """
        req = self.httpbin_2.get_my_headers(dry_run=True)
        def_url_query = self.httpbin_2.client["get_my_headers"]["url_query"]
        self.assertIn(urlencode(def_url_query), req.prepared_request.url)

    def test_client_load_pages_request(self):
        """A client should be able to make request under pages section in the json file
        """
        is_present = hasattr(self.httpbin_3, 'test_requests_patch_method')

        self.assertTrue(is_present)

    def test_url_data_present_in_url(self):
        """A dynamic value can be set directly in the url path of a request"""
        url_data = {'anything': 'my username'}
        req = self.httpbin_3.test_requests_patch_method(url_data=url_data, dry_run=True)
        path = self.httpbin_3.client['homepage']['test_requests_patch_method']['path']
        self.assertEqual(urlparse(req.prepared_request.url).path, quote(path.format(**url_data)))

    def test_client_except_missing_url_data(self):
        """Raise exception if a value is not provided by the user in the path"""
        self.assertRaises(RapicMissingUrlData, self.httpbin_3.test_requests_patch_method, dry_run=True)

    def test_body_data_is_sent(self):
        """Body should be sent by all request"""
        data = {'delete': 'Immediately'}
        url_data = {'user_id': 3435455}
        req = self.httpbin_3.test_requests_delete_method(data=data, url_data=url_data, dry_run=True)
        req_data = self.httpbin_3.client['second_page']['test_requests_delete_method']
        self.assertIn(urlencode(data), req.prepared_request.body)
        self.assertIn(urlencode(req_data['data']), req.prepared_request.body)

    def test_user_can_overide_body_data_sent(self):
        """Body of a request can be set directly by end user this would override
            anyother body set before
        """
        data = {'user_name': 3435455}
        req = self.httpbin_4.test_requests_put_method(data=data, dry_run=True)

        self.assertEqual(urlencode(data), req.prepared_request.body)

    def test_user_can_send_json_body_data(self):
        """A client can send request in json format to a server automatically by
            specifying the data as json on the method call
        """
        data = {'user_name': 3435455}
        req = self.httpbin_4.test_requests_put_method(json=data, dry_run=True)
        self.assertEqual(bytes(json.dumps(data), encoding='utf8'), req.prepared_request.body)

    def test_client_can_send_default_json_body_data(self):
        """A client can send request in json format to a server automatically by
                    specifying the data as json in the request file
                """
        req = self.httpbin_4.test_requests_post_method(dry_run=True)
        req_data = self.httpbin_4.client['test_requests_post_method']['data']
        self.assertEqual(bytes(json.dumps(req_data), encoding='utf8'), req.prepared_request.body)

    def test_client_can_send_url_params_fragment(self):
        """A client can send ulr fragment and params of a url directly"""
        req = self.httpbin_4.get_user_my_agent(dry_run=True)
        url_fragment = self.httpbin_4.client['get_user_my_agent']['url_fragment']
        url_params = self.httpbin_4.client['get_user_my_agent']['url_params']
        self.assertEqual(urlparse(req.prepared_request.url).fragment, url_fragment)
        self.assertEqual(urlparse(req.prepared_request.url).params, urlencode(url_params))

    def test_client_can_do_get_request(self):
        """A client can do get request successfully"""
        response = self.httpbin.get_my_headers(headers={'User-agent': 'Fake user agent'})
        self.assertEqual(response.request.method, 'GET')
        self.assertEqual(response.status_code, 200)

    def test_client_can_do_post_request(self):
        """A client can do post request successfully"""
        response = self.httpbin_4.test_requests_post_method()
        self.assertEqual(response.request.method, 'POST')
        self.assertEqual(response.status_code, 200)

    def test_client_can_do_patch_request(self):
        """A client can do patch request successfully"""
        response = self.httpbin_4.test_requests_patch_method()
        self.assertEqual(response.request.method, 'PATCH')
        self.assertEqual(response.status_code, 200)

    def test_client_can_do_put_request(self):
        """A client can do put request successfully"""
        response = self.httpbin_4.test_requests_put_method()
        self.assertEqual(response.request.method, 'PUT')
        self.assertEqual(response.status_code, 200)

    def test_client_can_do_delete_request(self):
        """A client can do delete request successfully"""
        response = self.httpbin_4.test_requests_delete_method()
        self.assertEqual(response.request.method, 'DELETE')
        self.assertEqual(response.status_code, 200)

    def test_client_request_can_take_proxies_directly(self):
        """A client can make a request by overiding successfully"""
        bad_proxies = {'http': 'http://20.10.1.11:1080', 'https': 'https://20.10.1.11:1080'}
        self.assertRaises(requests.exceptions.ConnectTimeout, self.httpbin_5.test_requests_delete_method, proxies=bad_proxies )

    def test_client_can_take_proxies_directly(self):
        """A client can make a request by overiding successfully"""

        self.assertRaises(requests.exceptions.ConnectTimeout, self.httpbin_5.test_requests_delete_method,
                         )

    def tearDown(self):
        self.httpbin.close()
        self.httpbin_4.close()
