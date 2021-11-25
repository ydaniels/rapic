import json as lib_json
import copy
from urllib.parse import urlencode, urlunparse, ParseResult
from rapic.hook import APIClientHook
from rapic.base import BaseClient
from rapic.connection.request import RapicRequestClient
from rapic.tools import dict_merge, json_loads_nested
from rapic.exceptions import RapicException, RapicMissingUrlData


class APIClient(APIClientHook, BaseClient):
    """
        This is used directly by end user to perform actual request
        api = APICLient(client_name = 'instagram',burp_req_file_loc='burp_saved_requests.json')

        api.get_my_followers()
        or
        api.get_user_followers(data ={ 'user_id' : '2343434' })
        or
        api.perform_requests('get_my_followers')
        or
         )

        Client must inherit from this class and supply at least the client name and manually crafted json file
        or json file automatically generated by rapic from a saved xml
        requests file using a reverse engineering software.
        It also exposes hooks from parent class you can use to perform extra cleaning or processing of request such as
         request signing, authentication, timestamp generation before making the actual request.

     """

    CLIENT_REQUESTS = {}

    def __init__(self, client_name, request_file, **kwargs):
        self.file_location = request_file
        self.name = client_name
        load_nested = kwargs.pop('loads_nested', None)
        self.request = RapicRequestClient(client_name, **kwargs)
        with open(request_file, 'r') as j:
            if load_nested:
                client_file = json_loads_nested(j.read())
            else:
                client_file = lib_json.loads(j.read())
            self.client = client_file.get(client_name) or client_file
            self.request_data_list = {}
            APIClient.CLIENT_REQUESTS[client_name] = self.request_data_list
            super(APIClient, self).__init__(client_name, **kwargs)

    def perform_request(self, request_name, do_extra_requests=False, do_implicit_requests=False, **kwargs):
        """
        Perform the actual http request specified by request_name in rapic json file
        :param request_name:
        :param do_extra_requests: Todo
        :param do_implicit_requests: Todo
        :param kwargs:
        :return:
        """
        request_data = self.get_request_data(request_name)

        request_data['request_name'] = request_name

        return self.execute_request(request_data, **kwargs)

    def get_headers(self, user_headers, request):
        headers = {}
        headers = dict_merge(headers, self.client.get("default_headers", {}))
        headers = dict_merge(headers, request.get("headers", {}))
        headers = dict_merge(headers, user_headers or {})
        return headers

    def get_url_query(self, user_url_query, request):
        url_query_data = {}
        url_query_data = dict_merge(url_query_data, self.client.get("default_url_query", {}))
        url_query_data = dict_merge(url_query_data, request.get("url_query", {}))
        url_query_data = dict_merge(url_query_data, user_url_query or {})
        return url_query_data

    def get_body_data(self, user_body_data, request):
        if user_body_data and not isinstance(user_body_data, dict):
            #If user passed data and its not a dict it means user wants to replace all data totally
            return user_body_data or {}
        body_data = {}
        body_data = dict_merge(body_data, self.client.get("default_data", {}))
        body_data = dict_merge(body_data, request.get("data", {}))
        body_data = dict_merge(body_data, user_body_data or {})
        return body_data

    def build_url(self, request_data, url_query, url_data):
        url_data = url_data or {}
        url = request_data.get('url')
        if not url:
            host = request_data.get('host') or self.client.get('host')
            scheme = request_data.get('scheme') or self.client.get('scheme')
            path = request_data['path']
            params = request_data.get('url_params') or self.client.get('default_url_params', '')
            fragment = request_data.get('url_fragment') or self.client.get('default_url_fragment', '')
            if not scheme or not host:
                raise RapicException('Missing host or scheme value for request ', request_data=request_data)
            url = urlunparse(
                ParseResult(netloc=host, scheme=scheme, path=path, query=urlencode(url_query), params=urlencode(params),
                            fragment=fragment))
        try:
            url = url.format(**url_data)
        except KeyError as e:
            raise RapicMissingUrlData(e, request_data=request_data)
        return url

    def execute_request(self, request_data, headers=None, url_data=None, data=None, files=None, auth=None, json=None, url_query=None,
                        dry_run=False, **kwargs):
        """
         Takes a request and execute the request using created session from RequestClient
         you can also pass headers, url data,  post data directly to override headers saved in the rapic json file.
         Hooks registered by API Client will be called here with the appropriate data

        :param request_data: The saved rapic request that should be performed
        :param headers: Headers to over-ride saved headers in json file
        :param url_data: Url data format and over-ride saved default url data
        :param data: Post data to over-ride saved body data
        :param json: Post data to over-ride saved body data in json format
        :param url_query: you can update external field not recorded in the json file url part using append_url dict
                           E.G append_url = {'load_false':1} -> url   = url + ?load_false=1
        :param dry_run : Do not perform actual requests and returns the prepared request to be sent to server
        :return: Response Object
        """

        request_data = self.build_request_data(request_data, data or json, url_data, headers, url_query)
        is_json = bool(json)
        new_req_obj = self._prepare_request(request_data, is_json, files, auth=auth)
        if dry_run:
            req = copy.deepcopy(self.request)
            req.set_prepared_request(new_req_obj, **kwargs)
            return req

        response = self.run(request_data, new_req_obj, **kwargs)
        return response

    def run(self, request_data, req_ob, **kwargs):
        request_name = request_data['request_name']
        response = self.request.run(req_ob, **kwargs)
        response = self._run_hook_func(request_name, response, self.RESPONSE_OBJ_HOOK_TYPE)
        return response

    def _prepare_request(self, request_data, is_json, files=None, auth=None):
        is_json = is_json or request_data.get('is_json')
        request_name = request_data['request_name']
        prep_req_obj = self.request.prepare_requests_request(request_data, is_json, files=files, auth=auth)

        new_req_obj = self._run_hook_func(request_name, prep_req_obj, self.REQUESTS_OBJ_HOOK_TYPE)
        return new_req_obj

    def build_request_data(self, request_data, data, url_data, headers, user_url_query):

        # Run client registered function before a request is performed
        # function registered as header,url, post hooks will recieve headers, url data, post data as an arguement
        # while the ones register as request  hook will recieve the full request before it is sent
        # They can do whatever they want with it and must return it back as this will be set as the new
        # data for each of them respectively before the request is being done
        request_name = request_data['request_name']
        built_headers = self.get_headers(headers, request_data)
        new_header = self._run_hook_func(request_name, built_headers, self.HEADER_HOOK_TYPE)

        url_query = self.get_url_query(user_url_query, request_data)
        new_url_query = self._run_hook_func(request_name, url_query, self.URL_QUERY_HOOK_TYPE)

        url = self.build_url(request_data, new_url_query, url_data)
        new_url = self._run_hook_func(request_name, url, self.URL_HOOK_TYPE)

        body_data = self.get_body_data(data, request_data)
        new_post_data = self._run_hook_func(request_name, body_data, self.POST_DATA_HOOK_TYPE)

        request_data['url'] = new_url
        request_data['headers'] = new_header
        request_data['url_query'] = url_query
        request_data['data'] = new_post_data

        request_data = self._run_hook_func(request_name, request_data, self.REQUEST_HOOK_TYPE)

        return request_data

    def get_request_data(self, request_name):
        """Get a particular request data copy by name from all requests this api client can perform"""
        request_data = self.request_data_list.get(request_name) or self.client.get(request_name)
        if not request_data:
            pages = self.client.get('pages', [])
            for page_name in pages:
                page = self.client[page_name]
                if request_name in page:
                    request_data = page[request_name]
                    break
            if not request_data:
                raise RapicException(
                    'Are you sure request %s exist in json file. Sorry cannot execute request' % request_name)
            self.request_data_list[request_name] = request_data
        return copy.deepcopy(request_data)

    def get_total_requests_number(self):
        return len(self.request_data_list)

    def get_pages_number(self):
        return len(self.client.get('pages', 0))

    def get_pages(self):
        if not self.client.get('pages', 0):
            raise RapicException('This api client does not have pages implemented')
        return self.client['pages']

    def get_requests(self):
        return self.request_data_list

    def info(self):
        req_data = dict()
        req_data['client_name'] = self.name.title()
        req_data['total_pages'] = self.get_pages_number()
        req_data['total_requests'] = self.get_total_requests_number()
        req_data['requests'] = self.get_requests()
        return req_data

    def close(self):
        self.request.close()
