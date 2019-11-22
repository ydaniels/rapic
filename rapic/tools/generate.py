import os
import xmltodict
from .burp import create_endpoint


def burp_request_files(client_name, burp_xml_files_loc):
    total_page_reqs = 0
    request_load = {}
    pages = []
    for file in burp_xml_files_loc:
        with open(file) as e:
            page = os.path.splitext(os.path.basename(file))[0]
            pages.append(page)
            request_items = xmltodict.parse(e.read())['items']
            if 'item' not in request_items:
                continue
            if not isinstance(request_items, list):
                request_items = request_items['item']
            endpoint = create_endpoint(request_items)
            total_page_reqs = total_page_reqs + endpoint['total_requests']
            request_load[page] = endpoint
    request_load['total_client_requests'] =  total_page_reqs
    request_load['pages'] =  pages
    return {client_name: request_load}
