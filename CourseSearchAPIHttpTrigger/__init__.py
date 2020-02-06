import logging
import os
import sys
import inspect
import traceback
import json
import re

import azure.functions as func


# TODO investigate setting PATH in Azure so can remove this
CURRENTDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENTDIR = os.path.dirname(CURRENTDIR)
sys.path.insert(0, CURRENTDIR)
sys.path.insert(0, PARENTDIR)

from .helper import (
    handle_search_terms,
    remove_conjunctions_from_searchable_fields,
    handle_apostrophes_in_search,
    get_offset_and_limit,
    group_courses_by_institution,
)

from .query import (
    build_institution_search_query,
    build_course_search_query,
)

from .search import (
    find_postcode,
    get_courses,
    get_results,
)

from .validation import check_query_parameters

from .dataset_helper import (
    DataSetHelper,
    get_cosmos_client,
    get_collection_link,
)

from .models import error

api_key = os.environ["SearchAPIKey"]
api_version = os.environ["AzureSearchAPIVersion"]
default_limit = os.environ["DefaultLimit"]
max_default_limit = int(os.environ["MaxDefaultLimit"])
postcode_index_name = os.environ["PostcodeIndexName"]
search_url = os.environ["SearchURL"]
cosmosdb_uri = os.environ["AzureCosmosDbUri"]
cosmosdb_key = os.environ["AzureCosmosDbKey"]
cosmosdb_database_id = os.environ["AzureCosmosDbDatabaseId"]
cosmosdb_dataset_collection_id = os.environ["AzureCosmosDbDataSetCollectionId"]

# Intialise cosmos db client
client = get_cosmos_client(cosmosdb_uri, cosmosdb_key)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Implements the REST API endpoint for searching for course documents.

    The endpoint implemented is:
        /search/courses

    The API is fully documented in a swagger document in the same repo
    as this module.
    """

    # Only log environment variables which are not security sensitive
    logging.info(
        f"Starting up azure function with the following configuration\n\
                  max_default_limit: {max_default_limit}\n\
                  default_limit: {default_limit}\n\
                  postcode_index_name: {postcode_index_name}"
    )

    try:

        logging.info(
            f"Processing course search request\n\
                       url: {req.url}\n\
                       params: {req.params}"
        )

        params = dict(req.route_params)
        limit = req.params.get("limit", default_limit)
        offset = req.params.get("offset", "0")
        course = req.params.get("qc", "")
        institution = req.params.get("qi", "")
        filters = req.params.get("filters", "")
        postcode_and_distance = req.params.get("postcode", "")
        institutions = req.params.get("institutions", "")
        countries = req.params.get("countries", "")
        length_of_course = req.params.get("length_of_course", "")
        subjects = req.params.get("subjects", "")
        language = req.params.get("language", "en")

        # Step 1 - Validate query parameters
        query_params, error_objects = check_query_parameters(
            countries,
            filters,
            length_of_course,
            subjects,
            limit,
            max_default_limit,
            offset,
            language,
        )

        if error_objects:
            logging.error(
                f"invalid filter options\n filter_options:\
                           {params}\n"
            )
            return func.HttpResponse(
                error.get_http_error_response_json(error_objects),
                headers={"Content-Type": "application/json"},
                status_code=400,
            )

        postcode_object = {}
        # Step 2 Lookup postcode if parameter is set
        if postcode_and_distance:
            postcode_params = postcode_and_distance.split(",")
            postcode_object = find_postcode(
                search_url,
                api_key,
                api_version,
                postcode_index_name,
                postcode_params[0],
            )

            postcode_object["distance"] = convert_miles_to_km(postcode_params[1])

        # Step 3 handle unsafe and reserved characters in search terms
        course, institution = handle_search_terms(course, institution)

        # Step 4 - Remove conjunctions from course and institution search
        course, institution = remove_conjunctions_from_searchable_fields(
            course, institution
        )

        # Gracefully handle apostrophes for search
        institution = handle_apostrophes_in_search(institution)
        institutions = handle_apostrophes_in_search(institutions)

        # Step 5 - Retrieve the latest stable dataset version, dependent on
        dataset_collection_link = get_collection_link(cosmosdb_database_id, cosmosdb_dataset_collection_id)

        dsh = DataSetHelper(client, dataset_collection_link)
        version = dsh.get_highest_successful_version_number()
        
        course_index_name = f"courses-{version}"
        logging.info(f"course_index_name:{course_index_name}")

        # Step 6 - Build institution course grouping query
        search_query = build_institution_search_query(
            course, institution, institutions, postcode_object, query_params
        )

        # Step 7 - Query course search index to get list of
        # institution course groupings
        response_with_facets = get_courses(
            search_url, api_key, api_version, course_index_name, search_query
        )

        facets = response_with_facets.json()

        counts = {}
        # Step 8 - handle facets to build correct
        # limit and offset for next query
        query_params["limit"], query_params["offset"], counts["institutions"], counts[
            "courses"
        ], institution_course_counts = get_offset_and_limit(
            facets["@search.facets"]["course/institution/sort_pub_ukprn_name"],
            int(limit),
            int(offset),
        )

        # Step 9 - TODO Refactor so caller does not have to know about the number of courses and handling more than 1000
        # Get courses by institution based on query paramaeters
        # Azure search can only return a maximum of 1000 docs in one call, so page through results
        if query_params["limit"] > 1000:
            courses = get_results(
                search_url,
                api_key,
                api_version,
                course_index_name,
                course,
                institution,
                institutions,
                postcode_object,
                query_params,
            )
        else:
            # Step a - Build course query
            search_query = build_course_search_query(
                course, institution, institutions, postcode_object, query_params
            )

            # Step b - Query course search index
            response = get_courses(
                search_url, api_key, api_version, course_index_name, search_query
            )
            json_response = response.json()
            courses = json_response["value"]

        # Step 10 - Manipulate response to match swagger spec - add counts (inst. & courses)
        search_results = group_courses_by_institution(
            courses, counts, int(limit), int(offset), language
        )

        return func.HttpResponse(
            json.dumps(search_results),
            headers={"Content-Type": "application/json"},
            status_code=200,
        )

    except Exception as e:
        logging.error(traceback.format_exc())

        # Raise so Azure sends back the HTTP 500
        raise e


def convert_miles_to_km(distance_in_miles):
    try:
        distance = str(float(distance_in_miles) * 1.60934)

        return distance
    except ValueError:
        return None