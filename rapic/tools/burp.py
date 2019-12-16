import re
from urllib.parse import urlparse
from urllib.parse import unquote


def get_body_data(body_str_data):
    body_data = {}

    def body_part_to_dict(body_part):
        data = {}
        if '=' in body_part:
            d = body_part.split('=')
            data[d[0]] = unquote(d[1])
        else:
            data[body_part] = ''
        return data

    if body_str_data:
        if '&' in body_str_data:  # if its more than one value in body linked with and
            body_parts = body_str_data.split('&')
            for parts in body_parts:
                body_data.update(body_part_to_dict(parts))
        elif '=' not in body_str_data:
            return unquote(body_str_data)
        else:
            body_data.update(body_part_to_dict(body_str_data))
    return body_data


def get_url_data(url):
    data = {}
    if '{{' in url and '}}' in url:
        se = re.findall("\{\{[A-Za-z0-9_]+\}\}", url)
        for s in se:
            s = s.replace('{{', '')
            s = s.replace('}}', '')
            data[s] = None
    parsed = urlparse(url)
    data.update(get_body_data(parsed.query))
    return data


def get_header(header):
    header_l = header.split('\n')

    head = {}
    for h in header_l:
        if 'Content-Length' in h:
            continue
        if ':' in h:
            header_key, header_value = h.split(':', 1)
            head[header_key.lstrip().rstrip()] = unquote(header_value.lstrip().rstrip())
    return head


def create_endpoint(request_item):
    endpoint = {}
    if not isinstance(request_item, list):
        request_item = [request_item]
    request_num = 1
    for item in request_item:

        url = item['url']
        location = urlparse(url).netloc
        scheme = urlparse(url).scheme
        path = urlparse(url).path
        url_data = get_url_data(url)
        method = item['method']
        request_body = item['request']['#text']  # get request body
        request_body_lst = request_body.split("\n\n")
        header_text = request_body_lst[0]
        body_data_text = request_body_lst[1:]
        head = get_header(header_text)
        post_data = {}
        if body_data_text and len(body_data_text) > 0:
            post_data = get_body_data(body_data_text[0])
        d = dict()
        d['path'] = path
        d['host'] = location
        d['scheme'] = scheme
        d['method'] = method
        d['data'] = post_data
        d['is_json'] = False
        if isinstance(post_data, str):
            d['is_json'] = True
        #d['url'] = unquote(url)
        d['url_query'] = url_data
        d['url_params'] = urlparse(url).params
        d['url_fragment'] = urlparse(url).fragment
        d['headers'] = head
        d['do_extra_requests'] = False
        d['do_implicit_requests'] = False
        d['extra_request_names'] = []
        endpoint['request_%s' % request_num] = d
        request_num += 1

    endpoint['total_requests'] = request_num - 1
    endpoint['implicit_requests'] = []
    return endpoint
