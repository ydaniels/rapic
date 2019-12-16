"""Tests for rapic Client."""
import unittest
import os
import time
import hashlib
from urllib.parse import urlencode
from rapic.client import APIClient
from rapic.hook import APIClientHook


class UserAgentObject:

    def __init__(self, data):
        self.data = data


class TestRapicClientHook(unittest.TestCase):

    def setUp(self):
        curr_dir = os.path.dirname(__file__)
        self.httpbin_file = os.path.join(curr_dir, 'httpbin.json')
        self.httpbin_file_2 = os.path.join(curr_dir, 'httpbin_2.json')
        self.httpbin_file_3 = os.path.join(curr_dir, 'httpbin_3.json')
        self.httpbin_file_5 = os.path.join(curr_dir, 'httpbin_5.json')

    def test_hook_can_exclude_requests(self):
        """Requests can excluded from running a hook even when it has been set"""
        time_st = str(time.time())

        class MyApiClient(APIClient):

            @APIClientHook.hook_client_header(client='httpbin_6',
                                              requests=['get_my_headers',
                                                        'get_my_ip'], exclude_requests=['get_my_ip'])
            def set_dynamic_data_on_header(self, data, **kwargs):
                data['timestamp'] = time_st + data['All-Request-Headers']
                return data

        httpbin = MyApiClient('httpbin_6', self.httpbin_file_5)
        req = httpbin.get_my_ip(dry_run=True)
        self.assertNotIn('timestamp', req.prepared_request.headers)

    def test_hook_can_run_explicit_excluded_requests(self):
        """Requests should run if its specified expicitly even if it is
         excluded from running"""
        time_st = str(time.time())

        class MyApiClient(APIClient):

            @APIClientHook.hook_client_header(client='httpbin_7',
                                              requests=['get_my_headers'], exclude_requests=['*'])
            def set_dynamic_data_on_header(self, data, **kwargs):
                data['timestamp'] = time_st
                return data

        httpbin = MyApiClient('httpbin_7', self.httpbin_file_5)
        req = httpbin.get_my_headers(dry_run=True)
        self.assertIn('timestamp', req.prepared_request.headers)



    def test_can_hook_request_data_header(self):
        """Headers can be accessed and updated with
         custom parameters before being sent to the server"""
        time_st = str(time.time())

        class MyApiClient(APIClient):

            @APIClientHook.hook_client_header(client='httpbin',
                                              requests=['get_my_headers',
                                                        'get_my_ip'])
            def set_dynamic_data_on_header(self, data, **kwargs):
                data['timestamp'] = time_st + data['All-Request-Headers']
                return data

        httpbin = MyApiClient('httpbin', self.httpbin_file)
        new_header = time_st + httpbin.client["get_my_headers"]['headers']['All-Request-Headers']
        req = httpbin.get_my_headers(dry_run=True)
        self.assertIn('timestamp', req.prepared_request.headers)
        self.assertEqual(req.prepared_request.headers['timestamp'], new_header)

    def test_can_hook_body_data(self):
        """The body of a request can be hooked to perform any necessary processing"""
        new_body_data = {'new_body_data': 'set_in_hook'}

        class MyApiClient(APIClient):
            @APIClientHook.hook_client_body_data(client='httpbin_2',
                                                 requests=['*'])
            def overide_body_data(self, data, **kwargs):
                return new_body_data

        httpbin = MyApiClient('httpbin_2', self.httpbin_file_5)
        req = httpbin.get_my_headers(dry_run=True)
        self.assertEqual(req.prepared_request.body, urlencode(new_body_data))

    def test_can_hook_url(self):
        """The finally url of a client can be changed just before being sent to the server"""
        new_url = 'http://httpbin.org/new_url'

        class MyApiClient(APIClient):

            @APIClientHook.hook_client_url(client='httpbin_3',
                                           requests=['*'])  # register this for all the hooks in client 3
            def overide_url_query(self, url, **kwargs):
                return new_url

        httpbin = MyApiClient('httpbin_3', self.httpbin_file_5)
        req = httpbin.get_my_headers(dry_run=True)
        self.assertEqual(new_url, req.prepared_request.url)

    def test_can_hook_url_query(self):
        """The query part of a url of a client can be changed just before being sent to the server"""
        new_query_value = 'new_query_value'
        this = self
        class MyApiClient(APIClient):

            @APIClientHook.hook_client_url_query(client='httpbin',
                                           requests=['*'])  # register this for all the requests in client 3
            def overide_url_query(self, data, **kwargs):
                this.assertIn('second_key', data)
                data['query'] = new_query_value
                return data

        httpbin = MyApiClient('httpbin', self.httpbin_file_3)
        req = httpbin.test_requests_patch_method(url_data={'anything': "1"}, url_query = {'second_key': 'second_value'}, dry_run=True)
        self.assertIn(new_query_value, req.prepared_request.url)

    def test_can_hook_request_data(self):
        """The full request data can be hooked in case there is any compulsory
        processing that utilizes all the part of a request e.g signature signing of a request
        can be appended in the header
        """

        class MyApiClient(APIClient):

            @APIClientHook.hook_client_request_data(client='httpbin',
                                                    requests=['get_my_headers',
                                                              'get_my_ip'])
            def set_http_signature_on_header(self, data, **kwargs):
                sign_request = data['url'] + data['method'] + urlencode(data['data'])
                m = hashlib.sha256()
                m.update(bytes(sign_request, encoding='utf8'))
                signature = m.hexdigest()
                data['headers']['signature'] = signature
                self.http_signature = signature
                return data

        httpbin = MyApiClient('httpbin', self.httpbin_file)
        req = httpbin.get_my_headers(dry_run=True)
        self.assertIn('signature', req.prepared_request.headers)

    def test_can_hook_prepared_req(self):
        """Exactly above a rapic client is returned where the python prepared requests
            can be accessed before being sent
        """

        class MyApiClient(APIClient):

            @APIClientHook.hook_client_prepared_request(client='httpbin',
                                                        requests=['get_my_ip'])
            def set_http_signature_on_header(self, req, **kwargs):
                req.method = 'POST'
                return req

        httpbin = MyApiClient('httpbin', self.httpbin_file)
        req = httpbin.get_my_ip(dry_run=True)
        self.assertIn('POST', req.prepared_request.method)
        response = req.run()
        self.assertEqual(response.status_code, 405)
        req.close()

    def test_can_hook_response(self):
        """The response can be changed or go through data change before
            being sent back.
        """

        class MyApiClient(APIClient):

            @APIClientHook.hook_client_response(client='httpbin',
                                                requests=['*'])  # register this for all the hooks
            def return_custom_api_obj(self, response, **kwargs):
                if kwargs.get('request_name') == 'get_my_headers':
                    user_agent = UserAgentObject(response.content)
                    return user_agent
                return response

        httpbin = MyApiClient('httpbin', self.httpbin_file)
        resp = httpbin.get_my_headers()
        httpbin.close()
        self.assertIsInstance(resp, UserAgentObject)
