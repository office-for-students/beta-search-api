import logging
import os
import traceback
import json

import azure.functions as func

from . import helper, query, search, validation
from .models import error


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Implements the REST API endpoint for searching for course documents.

    The endpoint implemented is:
        /search/courses

    The API is fully documented in a swagger document in the same repo
    as this module.
    """

    api_key = os.environ['SearchAPIKey']
    api_version = os.environ['AzureSearchAPIVersion']
    default_limit = os.environ["DefaultLimit"]
    max_default_limit = int(os.environ["MaxDefaultLimit"])
    postcode_index_name = os.environ['PostcodeIndexName']
    search_url = os.environ['SearchURL']

    # Only log environment variables which are not security sensitive
    logging.info(f"Starting up azure function with the following configuration\n\
                  max_default_limit: {max_default_limit}\n\
                  default_limit: {default_limit}\n\
                  postcode_index_name: {postcode_index_name}")

    try:
        logging.info(f"Processing course search request\n\
                       url: {req.url}\n\
                       params: {req.params}")

        params = dict(req.route_params)
        limit = req.params.get("limit", default_limit)
        offset = req.params.get("offset", "0")
        course = req.params.get("qc", "")
        institution = req.params.get("qi", "")
        filters = req.params.get("filters", "")
        postcode = req.params.get("postcode", "")
        institutions = req.params.get("institutions", "")
        countries = req.params.get("countries", "")
        length_of_course = req.params.get("length_of_course", "")

        postcode_object = {}
        # Step 1 Lookup postcode if parameter is set
        if postcode != "":
            p = postcode.split(",")
            postcode_object = search.find_postcode(search_url, api_key, api_version, postcode_index_name, p[0])
            postcode_object["distance"] = convert_to_km(p[1])

        # Step 2 - Validate query parameters
        query_params, error_objects = validation.check_query_parameters(countries, filters, length_of_course, limit, max_default_limit, offset)
        logging.info(f"query_params: {query_params}")
        if len(error_objects) > 0:
            logging.error(f"invalid filter options\n filter_options: {params}\n")
            return func.HttpResponse(
                error.get_http_error_response_json(error_objects),
                headers={"Content-Type": "application/json"},
                status_code=400,
            )

        # Step 3 - TODO Instead of hardcoding the version, it should retrieve the
        # latest stable dataset version, dependent on dataset endpoint existing 
        version = "1"
        course_index_name = "courses-" + version

        # Step 4 - Build institution course grouping query
        search_query = query.build_institution_search_query(course, institution, institutions, postcode_object, query_params)

        # Step 5 - Query course search index to get list of institution course groupings
        response_with_facets = search.get_courses(search_url, api_key, api_version, course_index_name, search_query)
        facets = response_with_facets.json()
       
        counts = {}
        # Step 6 - handle facets to build correct limit and offset for next query
        query_params["limit"], query_params["offset"], counts["institutions"], counts["courses"] = helper.get_offset_and_limit(facets["@search.facets"]['course/institution/sort_pub_ukprn_name'], int(limit), int(offset))

        # Step 7 - Build course query
        search_query = query.build_course_search_query(course, institution, institutions, postcode_object, query_params)

        # Step 8 - Query course search index
        response = search.get_courses(search_url, api_key, api_version, course_index_name, search_query)

        # Step 9 - Manipulate response to match swagger spec - add counts (inst. & courses)
        search_results = helper.group_courses_by_institution(response.json(), counts, int(limit), int(offset))

        if response:
            return func.HttpResponse(
                json.dumps(search_results),
                headers={"Content-Type": "application/json"},
                status_code=200
            )

    except Exception as e:
        logging.error(traceback.format_exc())

        # Raise so Azure sends back the HTTP 500
        raise e


def convert_to_km(distance):
  try:
    distance = str(float(distance) * 1.60934)
    logging.info(f"type distance 1: {type(distance)}")

    return distance
  except ValueError:
    return None