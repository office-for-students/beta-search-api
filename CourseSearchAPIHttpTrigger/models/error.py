import json

err_limit_wrong_type = "limit value needs to be a number"
err_limit_negative = "limit needs to be a positive number, limit cannot be lower than 0"
err_limit_above_max = "limit cannot exceed maximum value of "
err_offset_wrong_type = "offset value needs to be a number"
err_offset_negative = "offset needs to be a positive number, offset cannot be lower than 0"
err_multiple_modes = "cannot have both part_time and full_time filters set"
err_invalid_filters = "invalid filters"
err_duplicate_filters = "use of the same filter option more than once"
err_duplicate_countries = "use of the same countries more than once"
err_invalid_countries = "invalid countries"
err_length_of_course_wrong_type  = "length_of_course values needs to be a number"
err_length_of_course_out_of_range = "length_of_course values needs to be numbers between the range of 1 and 7"
	

def get_error_object(error_title, error_key_value_pairs):
    """Returns an error object"""

    error_values = []
    for ekvp in error_key_value_pairs:
        error_values.append(
            {
                ekvp["key"]: ekvp["value"]
            }
        )
    
    error_object = {
        'error': error_title,
        'error_values': error_values
    }

    return error_object


def get_http_error_response_json(error_objects):
    """Returns a JSON object indicating an Http Error"""
    http_error_resp = {}
    http_error_resp["errors"] = error_objects
    return json.dumps(http_error_resp)