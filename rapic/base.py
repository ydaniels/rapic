from abc import ABCMeta, abstractmethod


class BaseClient:
    """This is the entry point for creating a client, every client must inherit from this class.
        Note this is an abstract class, it cannot be used directly and every child class must implement
        all abstract methods specified below.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def perform_request(self, request_name, do_extra_actions=False, do_implicit=False, **kwargs):
        """Perform the actual http request by calling the name of the request (specified when saving it in burp)
            with the needed data passed in kwargs
        : request_name : The name of the http request you want to perform by this client
        :kwargs : e.g {'data': {'name': 'Ben'}, 'url_data' : {'return_all_info' : True }
        """
        pass

    @abstractmethod
    def get_request_data(self, request_name):
        """
        Get the request with all the  informations (headers, url args) that was saved in burpsuite
        :param request_name:
        :return:
        """

    @abstractmethod
    def get_requests(self):
        """Get all requests or api calls that can be performed """

    @abstractmethod
    def get_total_requests_number(self):
        """
        Get the total number of requests or api calls that can be performed by the client
         this is the number of requests that was saved in burp
        e.g the number of resource endpoint that was saved in burpsuite for a REST API
        :return:
        """

    @abstractmethod
    def get_pages_number(self):
        """
        If request is grouped get the number of groupings
        :return:
        """

    @abstractmethod
    def get_pages(self):
        """
        Get the number of groupings if request is grouped
        :return:
        """

    @abstractmethod
    def info(self):
        """Get different information  about a particular client"""
        pass

    def __getattr__(self, attr):
        def intercept_attr(*args, **kwargs):
            return self.perform_request(attr, *args, **kwargs)

        return intercept_attr
