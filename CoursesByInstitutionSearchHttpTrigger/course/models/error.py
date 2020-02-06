import json
import os
import inspect
import sys

# TODO investigate setting PATH in Azure so can remove this
CURRENTDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENTDIR = os.path.dirname(CURRENTDIR)
sys.path.insert(0, CURRENTDIR)
sys.path.insert(0, PARENTDIR)

ERR_LIMIT_WRONG_TYPE = "limit value needs to be a number"
ERR_LIMIT_NEGATIVE = "limit needs to be a positive number, limit cannot be lower than 0"
ERR_LIMIT_ABOVE_MAX = "limit cannot exceed maximum value of "
ERR_OFFSET_WRONG_TYPE = "offset value needs to be a number"
ERR_OFFSET_NEGATIVE = (
    "offset needs to be a positive number, offset cannot be lower than 0"
)
ERR_MANDATORY_FIELD_INSTITUTION = "missing value for mandatory field: institution"
ERR_MULTIPLE_MODES = "cannot have both part_time and full_time filters set"
ERR_INVALID_FILTERS = "invalid filters"
ERR_DUPLICATE_FILTERS = "use of the same filter option more than once"
ERR_DUPLICATE_COUNTRIES = "use of the same countries more than once"
ERR_INVALID_COUNTRIES = "invalid countries"
ERR_LENGTH_OF_COURSE_WRONG_TYPE = "length_of_course values needs to be a number"
ERR_LENGTH_OF_COURSE_OUT_OF_RANGE = (
    "length_of_course values needs to be numbers between the range of 1 and 7"
)
ERR_UNKNOWN_LANGUAGE = "value of language is not supported"


def get_error_object(error_title, error_key_value_pairs):
    """Returns an error object"""

    error_values = []
    for ekvp in error_key_value_pairs:
        error_values.append({ekvp["key"]: ekvp["value"]})

    error_object = {"error": error_title, "error_values": error_values}

    return error_object


def get_http_error_response_json(error_objects):
    """Returns a JSON object indicating an Http Error"""
    http_error_resp = {}
    http_error_resp["errors"] = error_objects
    return json.dumps(http_error_resp)
