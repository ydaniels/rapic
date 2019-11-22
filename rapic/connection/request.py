import requests


class RequestClient:
    """ This is a very straight-forward using Python-Requests to make actual requests """

    def __init__(self, name, **kwargs):
        self.name = name
        self.session = kwargs.pop('session', None) or requests.Session()
        self.request_kwargs = kwargs

    def prepare_requests_request(self, request):
        """
        Prepare request  called by an api client in case it needs to
        change anything in the prepared request first before sending it over
        :param request: crafted api request
        :return: <PreparedRequest>
        """
        method = request['method']
        url = request['url']
        headers = self.clean_headers(request['headers'])
        data = request['body_data']
        req = requests.Request(method, url, data=data, headers=headers)
        prepped = self.session.prepare_request(req)
        return prepped

    def execute(self, prepped_req):
        """
        Take prepared request from client do actual sending by request session
        :param prepped_req: Hooked  <PreparedRequest>
        :return:  <Response>
        """
        resp = self.session.send(prepped_req,
                                 **self.request_kwargs
                                 )
        return resp

    @staticmethod
    def clean_headers(headers):
        return {x.strip(): y.strip() for x, y in headers.items()}

    def close(self):
        self.session.close()
