import logging

from models import error

def check_query_parameters(countries, filters, length_of_course, limit, max_default_limit, offset):

    try:
        validator = Validator(countries, filters, length_of_course, limit, max_default_limit, offset)

        return validator.validate()
    except Exception:
        raise

class Validator():
    def __init__(self, countries, filters, length_of_course, limit, max_default_limit, offset):
        self.max_default_limit = max_default_limit
        self.limit = limit
        self.offset = offset
        self.filters = filters
        self.length_of_course = length_of_course
        self.countries = countries


    def validate(self):
        error_objects = []
        self.new_limit, l_error_objects = self.validate_limit()
        self.new_offset, o_error_objects = self.validate_offset()
        self.new_filters, f_error_objects = self.validate_filters()
        self.new_countries, c_error_objects = self.validate_countries()
        self.new_length_of_courses, loc_error_objects = self.validate_length_of_courses()

        # Combine error objects
        error_objects.extend(
            l_error_objects +
            o_error_objects +
            f_error_objects +
            c_error_objects +
            loc_error_objects
        )

        self.query_params = {}
        if len(error_objects) == 0:
            self.build_query_params()

        return self.query_params, error_objects

    def validate_limit(self):
        error_objects = []
        is_integer, limit = is_int(self.limit)
        if not is_integer:
            error_values = [{"key": "limit", "value": self.limit}]
            error_object = error.get_error_object(error.err_limit_wrong_type, error_values)
            error_objects.append(error_object)

            return 0, error_objects

        if limit > self.max_default_limit:
            error_values = [{"key": "limit", "value": self.limit}]
            error_object = error.get_error_object(error.err_limit_above_max + f"{self.max_default_limit}", error_values)
            error_objects.append(error_object)

            return limit, error_objects

        if limit < 0:
            error_values = [{"key": "limit", "value": self.limit}]
            error_object = error.get_error_object(error.err_limit_negative, error_values)
            error_objects.append(error_object)

            return limit, error_objects

        return limit, error_objects


    def validate_offset(self):
        error_objects = []
        is_integer, offset = is_int(self.offset)
        if not is_integer:
            error_values = [{"key": "offset", "value": self.offset}]
            error_object = error.get_error_object(error.err_offset_wrong_type, error_values)
            error_objects.append(error_object)

            return 0, error_objects

        if offset < 0:
            error_values = [{"key": "offset", "value": self.offset}]
            error_object = error.get_error_object(error.err_offset_negative, error_values)
            error_objects.append(error_object)

            return offset, error_objects

        return offset, error_objects


    def validate_filters(self):
        error_objects, new_filters = [], {}
        if self.filters == "":
            return new_filters, error_objects

        filters = self.filters.split(",")

        count_filters, duplicate_filters, invalid_filters = {}, [], []
        for filter in filters:

            if filter.startswith("-"):
                filter_without_prefix = filter[1:]
                new_filters[filter_without_prefix] = False
            else:
                filter_without_prefix = filter
                new_filters[filter] = True

            if not filter_without_prefix in count_filters:
                count_filters[filter_without_prefix] = 1
            else:
                count_filters[filter_without_prefix] += 1

            # Check filter exists in whitelist
            if not validate_filter_options(filter_without_prefix):
                invalid_filters.append(filter)

            # Find duplicate filters
            if count_filters[filter_without_prefix] > 1:
                duplicate_filters.append(filter_without_prefix)

        if len(duplicate_filters) > 0:
            value = ",".join(duplicate_filters)
            error_values = [{"key": "filters", "value": value}]

            error_object = error.get_error_object(error.err_duplicate_filters, error_values)
            error_objects.append(error_object)

        if len(invalid_filters) > 0:
            value = ",".join(invalid_filters)
            error_values = [{"key": "filters", "value": value}]

            error_object = error.get_error_object(error.err_invalid_filters, error_values)
            error_objects.append(error_object)

        # Check use of part_time and full_time filters
        if "part_time" in count_filters and "full_time" in count_filters:
            error_values = [{"key": "filters", "value": "part_time,full_time"}]
            error_object = error.get_error_object(error.err_multiple_modes, error_values)
            error_objects.append(error_object)

        # Return error objects if array is not empty
        if len(error_objects) > 0:
            return {}, error_objects

        return new_filters, error_objects

    def validate_countries(self):
        error_objects = []
        if self.countries == "":
            return [], error_objects

        countries = self.countries.split(",")


        country_list = {}
        invalid_countries, duplicate_countries, must_have_countries, must_not_have_countries = [], [], [], []
        for country in countries:
            country_code = check_country_is_valid(country)
            if country_code == "":
                invalid_countries.append(country)

            if country.startswith("-"):
                country_without_prefix = country[1:]
                must_not_have_countries.append(country_code)
            else:
                country_without_prefix = country
                must_have_countries.append(country_code)

            # Find duplicate countries
            if not country_without_prefix in country_list:
                country_list[country_without_prefix] = 1
            else:
                country_list[country_without_prefix] += 1

            if country_list[country_without_prefix] > 1:
                duplicate_countries.append(country_without_prefix)

        if len(duplicate_countries) > 0:
            value = ",".join(duplicate_countries)
            error_values = [{"key": "countries", "value": value}]

            error_object = error.get_error_object(error.err_duplicate_countries, error_values)
            error_objects.append(error_object)

        if len(invalid_countries) > 0:
            value = ",".join(invalid_countries)
            error_values = [{"key": "countries", "value": value}]

            error_object = error.get_error_object(error.err_invalid_countries, error_values)
            error_objects.append(error_object)

        # Return error objects if array is not empty
        if len(error_objects) > 0:
            return [], error_objects

        # Logical reasoning would result in countries that must exist will
        # supercede those countries that must not exist
        if len(must_have_countries) > 0:
            return must_have_countries, []

        # To successfully query search index invert countries filter to must have
        must_have_countries = convert(must_not_have_countries)

        return must_have_countries, []

    def validate_length_of_courses(self):
        error_objects = []
        if self.length_of_course == "":
            return [], []

        loc = self.length_of_course.split(",")

        length_of_courses, invalid_type, out_of_range = [], [], []
        for length in loc:
            length_is_int, l = is_int(length)
            if not length_is_int:
                invalid_type.append(length)
                continue

            if l < 1 or l > 7:
                out_of_range.append(length)

            length_of_courses.append(l)

        if len(invalid_type) > 0:
            value = ",".join(invalid_type)
            error_values = [{"key": "length_of_courses", "value": value}]

            error_object = error.get_error_object(error.err_length_of_course_wrong_type, error_values)
            error_objects.append(error_object)

        if len(out_of_range) > 0:
            value = ",".join(out_of_range)
            error_values = [{"key": "length_of_courses", "value": value}]

            error_object = error.get_error_object(error.err_length_of_course_out_of_range, error_values)
            error_objects.append(error_object)

        # Return error objects if array is not empty
        if len(error_objects) > 0:
            return [], error_objects

        return length_of_courses, []

    def build_query_params(self):
        query_params = {}
        if self.new_offset > 0:
            query_params['offset'] = self.new_offset

        if self.new_limit > 0:
            query_params['limit'] = self.new_limit

        query_params.update(self.new_filters)

        if len(self.new_countries) > 0:
            query_params["countries"] = self.new_countries

        if len(self.new_length_of_courses) > 0:
            query_params["length_of_courses"] = self.new_length_of_courses

        self.query_params = query_params

def validate_filter_options(filter):
    switcher = {
        "distance_learning": True,
        "honours_award": True,
        "foundation_year": True,
        "sandwich_year": True,
        "year_abroad": True,
        "full_time": True,
        "part_time": True
    }

    return switcher.get(filter, False)


def check_country_is_valid(country):
    if country.startswith("-"):
        country = country[1:]

    switcher = {
        "england": "XF",
        "northern_ireland": "XG",
        "scotland": "XH",
        "wales": "XI"
    }

    return switcher.get(country, "")


def convert(codes):
    countries = [ "XF", "XG", "XH", "XI" ]

    for code in codes:
        try:
            countries.remove(code)
        except KeyError:
            logging.warning(f"The expected country code was not found: {code}")

    return countries


def is_int(value):
  try:
    new_value = int(value)
    return True, new_value
  except ValueError:
    return False, None
