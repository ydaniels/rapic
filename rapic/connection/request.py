import requests


class RapicRequestClient:
    """ This is very straight-forward using Python-Requests to make actual requests """

    def __init__(self, name, **kwargs):
        self.name = name
        self.session = kwargs.pop('session', None) or requests.Session()
        self.request_kwargs = kwargs
        self.prepared_request = None

    def prepare_requests_request(self, request_data, is_json=False):
        """
        Prepares a request from an api client before sending it.
        A client can change anything in the prepared request before sending it
        :param request_data: crafted api request data from json file
        :param is_json : decide if request is going to be sent in json format
        :return: <PreparedRequest>
        """
        method = request_data['method']
        url = request_data['url']
        headers = self.clean_headers(request_data['headers'])
        data = request_data['data']
        if is_json:
            req = requests.Request(method, url, json=data, headers=headers)
        else:
            req = requests.Request(method, url, data=data, headers=headers)

        prepped = self.session.prepare_request(req)
        return prepped

    def set_prepared_request(self, prepped_req, **kwargs):
        if kwargs:
            self.request_kwargs.update(kwargs)
        self.prepared_request = prepped_req

    def run(self, prepped_req=None, **kwargs):
        """
        Take prepared request from client and do actual sending by  using request session
        :param prepped_req:   <PreparedRequest>
        :return:  <Response>
        """
        sending_data = self.request_kwargs.copy()
        if kwargs:
            sending_data.update(kwargs)
        resp = self.session.send(prepped_req or self.prepared_request,
                                 **sending_data
                                 )
        return resp

    @staticmethod
    def clean_headers(headers):
        return {x.strip(): str(y).strip() for x, y in headers.items()}

    def close(self):
        self.session.close()
