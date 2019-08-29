import logging
import requests
import os
import sys
import inspect


# TODO investigate setting PATH in Azure so can remove this
CURRENTDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENTDIR = os.path.dirname(CURRENTDIR)
sys.path.insert(0, CURRENTDIR)
sys.path.insert(0, PARENTDIR)

import exceptions


def find_postcode(url, api_key, api_version, index_name, postcode):

    index = PostcodeIndex(url, api_key, api_version, index_name, postcode)

    return index.get_lat_long_for_postcode()


class PostcodeIndex:
    def __init__(self, url, api_key, api_version, index_name, postcode):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "api-key": api_key,
            "odata": "verbose",
        }

        # lowercase postcode and remove whitespace
        self.postcode = postcode.lower().replace(" ", "")
        self.query_string = "?api-version=" + api_version + "&search=" + self.postcode
        self.index_name = index_name

    def get_lat_long_for_postcode(self):
        try:
            url = self.url + "/indexes/" + self.index_name + "/docs" + self.query_string

            response = requests.get(url, headers=self.headers)
            response_body = response.json()

            postcode_lat_long = {
                "latitude": response_body["value"][0]["latitude"],
                "longitude": response_body["value"][0]["longitude"],
            }

        except requests.exceptions.RequestException as e:
            logging.exception(
                "unexpected error calling postcode search index", exc_info=True
            )
            raise exceptions.UnexpectedErrorExceptionFromSearchIndex(e)

        if response.status_code != 200:
            logging.error(
                f"failed to find postcode in search documents\n\
                            index-name: {self.index_name}\n\
                            status: {response.status_code}\n\
                            postcode: {self.postcode}"
            )
            return {}

        return postcode_lat_long


def get_courses(url, api_key, api_version, index_name, search_query):
    index = CourseIndex(url, api_key, api_version, index_name, search_query)

    return index.get()


class CourseIndex:
    def __init__(self, url, api_key, api_version, index_name, search_query):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "api-key": api_key,
            "odata": "verbose",
        }

        # lowercase postcode and remove whitespace
        self.query_string = "?api-version=" + api_version + search_query
        self.index_name = index_name

    def get(self):
        try:
            url = self.url + "/indexes/" + self.index_name + "/docs" + self.query_string

            logging.info(f"Querying search service with the following url: {url}")
            response = requests.get(url, headers=self.headers)

        except requests.exceptions.RequestException as e:
            logging.exception(
                "unexpected error calling course search index", exc_info=True
            )
            raise exceptions.UnexpectedErrorExceptionFromSearchIndex(e)

        if response.status_code != 200:
            logging.error(
                f"failed to find courses in search index\n\
                            index-name: {self.index_name}\n\
                            status: {response.status_code}\n\
                            url: {self.query_string}"
            )
            return {}

        return response
