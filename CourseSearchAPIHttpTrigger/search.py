import logging
import requests
import os

from . import exceptions


def find_postcode(url, api_key, api_version, index_name, postcode):

    try:
        index = PostcodeIndex(url, api_key, api_version, index_name, postcode)

        return index.get()
    except Exception:
        raise

class PostcodeIndex():
    def __init__(self, url, api_key, api_version, index_name, postcode):
        self.url = url
        self.headers = {
            'Content-Type': 'application/json',
            'api-key': api_key,
            'odata': 'verbose'
        }

        # lowercase postcode and remove whitespace
        self.p = postcode.lower().replace(' ', '')
        self.query_string = '?api-version=' + api_version + '&search=' + self.p
        self.index_name = index_name

    def get(self):
        try:
            url = self.url + "/indexes/" + self.index_name + \
                "/docs" + self.query_string

            response = requests.get(url, headers=self.headers)

        except requests.exceptions.RequestException as e:
            logging.exception('unexpected error calling postcode search index', exc_info=True)
            raise exceptions.UnexpectedErrorExceptionFromSearchIndex(e)

        if response.status_code != 200:
            logging.error(f'failed to find postcode in search documents\n\
                            index-name: {self.index_name}\n\
                            status: {response.status_code}\n\
                            postcode: {self.p}')
            return {}
        
        return response
