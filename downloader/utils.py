import sys
from time import sleep
from urllib.parse import urlencode

import requests


def _http_get(url, params=None):
    encoded = urlencode(params if params else {})
    params['extraParams'] = 'CAPS'
    try:
        response = requests.get(url, encoded, timeout=10)
    except BaseException as e:
        sys.stderr.write("Error while sending request: {}\n".format(e))
        return None
    if response.status_code == 200:
        return response.json()
    sys.stderr.write("Request failed with code {}, detail: {}\n".format(response.status_code, response.text))
    return None

def http_get(url, params=None, retry_lim=-1):
    """Send HTTP GET request repeatedly until it gets responses or the maximum number of retries exceeded

    :param url: the URL to request
    :param params: extra query parameters, will be URL encoded and multiple params will be concatenated with '&'
    :param retry_lim: the maximum number of retry attempts
    :return: response
    """
    trial = 0
    response = None
    while trial != retry_lim:
        response = _http_get(url, params)
        if response is not None:
            break
        trial += 1
        sleep(1)
        sys.stderr.write("Retrying...\n")
    return response