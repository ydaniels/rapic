class APIClientHook:
    """Allow access to necessary requests data by giving a client the ability to hook
        request and response data before it is sent to or returned from a server.
        There are 6 different hook type which determines what data is sent to the client for hooking
         REQUEST_HOOK_TYPE : A dictionary that contains parsed api client req dict
         HEADER_HOOK_TYPE :  Header dict
         URL_HOOK_TYPE : Final  Url as value
         URL_QUERY_HOOK_TYPE : Url query dict as value
         POST_DATA_HOOK_TYPE : Body data as dict
         REQUESTS_OBJ_HOOK_TYPE : Python-Requests prepared request obj
         RESPONSE_OBJ_HOOK_TYPE : Python-Requests response obj
    """
    HOOK_STORE = {}

    REQUEST_HOOK_TYPE = 1
    HEADER_HOOK_TYPE = 2
    URL_HOOK_TYPE = 3
    POST_DATA_HOOK_TYPE = 4
    REQUESTS_OBJ_HOOK_TYPE = 5
    RESPONSE_OBJ_HOOK_TYPE = 6
    URL_QUERY_HOOK_TYPE = 7

    def __init__(self, name, **kwargs):

        self.name = name

    @classmethod
    def create_type_hooks_store(cls, hook_type):

        cls.HOOK_STORE[hook_type] = dict()

    @classmethod
    def create_client_hooks_store(cls, hook_type, client_name):
        """
        Create an empty dict to hold hooks per client per hook type

        :param client_name: The api client that hook belongs to
        :param hook_type: The hook type store
        :return:
        """

        cls.HOOK_STORE[hook_type][client_name] = dict()

    @classmethod
    def register_client_hooks(cls, hook_type, requests, client_name, func, exclude_requests=None):
        """
            Save all hooks and functions per client per hook type that are going
            to be called for a client before a request is made

        :param hook_type: The hook_type that is being performed
        :param requests: List of requests name that the hook is registered for, this can also be ['*'] to register
                        for all requests made by the client
        :param client_name: The api client this hook is registered for
        :param func: The function to call for the hook
        :param exclude_requests: List of requests name to exclude this hook from running for
        :return: decorated func
        """
        if not requests:
            return
        if exclude_requests is None:
            exclude_requests = []
        if hook_type not in cls.HOOK_STORE:
            cls.create_type_hooks_store(hook_type)
        if client_name not in cls.HOOK_STORE[hook_type]:
            cls.create_client_hooks_store(hook_type, client_name)

        if not isinstance(requests, list):
            requests = [requests]

        for request in requests:

            if request not in cls.HOOK_STORE[hook_type][client_name]:
                cls.HOOK_STORE[hook_type][client_name][request] = [(func, exclude_requests)]
            else:
                cls.HOOK_STORE[hook_type][client_name][request].append((func, exclude_requests))

        def action_arg(*args, **kwargs):
            func(*args, **kwargs)

        return action_arg

    @classmethod
    def hook_client_prepared_request(cls, client, requests, exclude_requests=None):
        """
        This gives the ability to hook a python-requests obj before its sent.
         the registered callback function will recieve the prepared request object before sending it to the server.
        more at https://requests.kennethreitz.org/en/master/user/advanced/#prepared-requests
        :param client: the client to perform the hook for
        :param requests: list of request
        :return: decorated func
        """

        def request_func(func):
            cls.register_client_hooks(hook_type=cls.REQUESTS_OBJ_HOOK_TYPE, requests=requests, client_name=client,
                                      func=func, exclude_requests=exclude_requests)

        return request_func

    @classmethod
    def hook_client_response(cls, client, requests, exclude_requests=None):
        """
        This gives the ability to hook the return python-requests response obj
        :param client: the client to perform the hook for
        :param requests: list of request
        :return: decorated func
        """

        def request_func(func):
            cls.register_client_hooks(hook_type=cls.RESPONSE_OBJ_HOOK_TYPE, requests=requests, client_name=client,
                                      func=func, exclude_requests=exclude_requests)

        return request_func

    @classmethod
    def hook_client_request_data(cls, client, requests, exclude_requests=None):
        """
        This gives the ability to hook a full request in internal api client before its transformed
        to python-requests prepared requests
         the registered callback function will recieve all the datas before performing actual request.

        :param client: the client to perform the hook for
        :param requests: list of request
        :return:
        """

        def request_func(func):
            cls.register_client_hooks(hook_type=cls.REQUEST_HOOK_TYPE, requests=requests, client_name=client, func=func, exclude_requests=exclude_requests)

        return request_func

    @classmethod
    def hook_client_url(cls, client, requests, exclude_requests=None):
        """
        Run user hooks on  generated url
        :param client: the client to perform the hook for
        :param requests: List of requests to run for
        :return:
        """

        def request_func(func):
            cls.register_client_hooks(hook_type=cls.URL_HOOK_TYPE, requests=requests, client_name=client,
                                      func=func, exclude_requests=exclude_requests)

        return request_func

    @classmethod
    def hook_client_url_query(cls, client, requests, exclude_requests=None):
        """
        Run user hooks when generating url query data
        :param client: the client to perform the hook for
        :param requests: List of requests to run for
        :return:
        """

        def request_func(func):
            cls.register_client_hooks(hook_type=cls.URL_QUERY_HOOK_TYPE, requests=requests, client_name=client,
                                      func=func, exclude_requests=exclude_requests)

        return request_func

    @classmethod
    def hook_client_body_data(cls, client, requests, exclude_requests=None):
        """
        Run user hooks on request body when posting, deleting or putting data to a server
        :param client:
        :param requests:
        :return:
        """

        def action_function(request_func):
            cls.register_client_hooks(hook_type=cls.POST_DATA_HOOK_TYPE, requests=requests, client_name=client,
                                      func=request_func, exclude_requests=exclude_requests)

        return action_function

    @classmethod
    def hook_client_header(cls, client, requests, exclude_requests=None):
        """
         Register client func to run and process request header before making actual request to the server
         Good for including timestamp or signature that must be present in headers along with a particular requests

         @cls.hook_header(client='instagram', requests=['get_followers'])
         def set_time_stamp(data, **kwargs):
            data['timestamp'] = time.time()
            return data
        The current time stamp will be set in headers when get_followers request is made
        :param client: client to register this header
        :param requests: list of request name to to run this hook for e.g ['get_user_info']
        :return:
        """

        def req_func(func):
            cls.register_client_hooks(hook_type=cls.HEADER_HOOK_TYPE, requests=requests, client_name=client, func=func, exclude_requests=exclude_requests)

        return req_func

    def _run_hook_func(self, request_name, data, hook_type):
        """
        All hooks are registered from child  api client in format
        cls.hook_<hook_type>(client_name='instagram', requests_name=['get_user']) :
        The registered function will be called here with the necessary data
        :param request_name:  the current request_name hook is running for
        :param data: data that will be sent for hooking [headers,post data, url data, req obj, resp obj]
        :return: reformed data sent back
        """

        if hook_type not in self.HOOK_STORE or self.name not in self.HOOK_STORE[hook_type]:
            return data
        hook_type_store = self.HOOK_STORE[hook_type][self.name]

        if request_name not in hook_type_store and '*' not in hook_type_store:
            return data
        hook_funcs = hook_type_store.get(request_name, None) or hook_type_store.get('*')
        for func, excluded_requests in hook_funcs:
            if request_name in excluded_requests:
                continue
            elif '*' in excluded_requests and request_name not in hook_type_store:
                continue
            data = func(self,  data, request_name=request_name, client_name=self.name, hook_type=hook_type)
        return data
