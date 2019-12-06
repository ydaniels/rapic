class RapicException(Exception):
    """There was an exception that occurred while handling your
        rapic request.
        """

    def __init__(self, *args, **kwargs):
        """
        Initialize RapicException with `request_data`
        """

        self.request_data = kwargs.pop('request_data', None)
        self.client = kwargs.pop('client', None)


class RapicMissingUrlData(RapicException):
    """Error is generated when user does not supply required url data"""
