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

from institution.helper import (
    handle_search_terms,
    remove_conjunctions_from_searchable_fields,
    handle_apostrophes_in_search,
    get_offset_and_limit,
    group_courses_by_institution,
)

from institution.query import build_institution_search_query

from institution.search import (
    find_postcode,
    get_courses,
    get_results,
)

from institution.validation import check_query_parameters

from institution.dataset_helper import (
    DataSetHelper,
    get_cosmos_client,
    get_collection_link,
)

from institution.models import error

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

        # Step 1 - Validate query parameters
        query_params, error_objects = check_query_parameters(
            countries,
            filters,
            length_of_course,
            subjects,
            limit,
            max_default_limit,
            offset,
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
            postcode_object = search.find_postcode(
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
        
        new_facets = add_sortable_name(facets["@search.facets"]["course/institution/pub_ukprn_name"])
        sorted_facets = sort_facets(new_facets)

        # handle facets to build list of institutions for page
        search_results = build_search_response(
            sorted_facets,
            int(limit),
            int(offset),
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


def add_sortable_name(facets):
    facet_with_sortable_name = []
    for facet in facets:
        facet["sort_name"] = create_sortable_name(facet["value"])
        
        facet_with_sortable_name.append(facet)

    return facet_with_sortable_name


def create_sortable_name(name):

    # lowercase institution name
    sortable_name = name.lower()

    # remove unwanted prefixes
    sortable_name = sortable_name.replace("the university of ", "")
    sortable_name = sortable_name.replace("university of ", "")

    # remove unwanted commas
    sortable_name = sortable_name.replace(",", "")

    return sortable_name


def sort_facets(facets):
    return sorted(facets, key=lambda k: k['sort_name'])
    

def build_search_response(facets, requested_limit, requested_offset):
    total_courses = 0
    total_institutions = 0
    institutions = []

    lower_range = requested_offset
    upper_range = requested_limit + requested_offset

    institution_course_counts = {}
    for facet in facets:
        total_courses += facet["count"]

        if lower_range <= total_institutions < upper_range:
            facet["pub_ukprn_name"] = facet["value"]
            facet["number_of_courses"] = facet["count"]
            del facet["sort_name"]
            del facet["value"]
            del facet["count"]
            institutions.append(facet)

        total_institutions += 1
        

    return {
        "limit": requested_limit,
        "number_of_items": len(institutions),
        "offset": requested_offset,
        "total_number_of_courses": total_courses,
        "total_results": total_institutions,
        "items": institutions
    }
