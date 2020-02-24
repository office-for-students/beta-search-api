import unittest
import os
import sys
import inspect

CURRENTDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENTDIR = os.path.dirname(CURRENTDIR)
sys.path.insert(0, PARENTDIR)

from course.validation import (
    check_query_parameters,
    check_country_is_valid,
    Validator,
    validate_filter_options,
    is_int,
)


class TestValidateLimit(unittest.TestCase):
    def test_when_institution_param_is_empty(self):
        limit = "10"
        max_limit = 100
        validator = Validator("", "", "", "", "", limit, max_limit, "0", "en")

        expected_result = []
        expected_error_object = [
            {
                'error': 'missing value for mandatory field: institution',
                'error_values': [{'institution': ''}],
            }
        ]
        output_result, output_error_object = validator.validate_institution()

        self.assertEqual(expected_result, output_result)
        self.assertEqual(expected_error_object, output_error_object)

    def test_when_limit_is_within_max_limit(self):
        limit = "10"
        max_limit = 100
        validator = Validator("", "", "Coventry University", "", "", limit, max_limit, "0", "en")

        expected_result = 10
        output_result, output_error_object = validator.validate_limit()
        self.assertEqual(expected_result, output_result)
        self.assertEqual([], output_error_object)

    def test_when_limit_is_outside_max_limit(self):
        limit = "200"
        max_limit = 100
        validator = Validator("", "", "Coventry University", "", "", limit, max_limit, "0", "en")

        expected_result = 200
        expected_error_object = [
            {
                "error": "limit cannot exceed maximum value of 100",
                "error_values": [{"limit": "200"}],
            }
        ]
        output_result, output_error_object = validator.validate_limit()

        self.assertEqual(expected_result, output_result)
        self.assertEqual(expected_error_object, output_error_object)

    def test_when_limit_is_a_negative_number(self):
        limit = "-20"
        max_limit = 100
        validator = Validator("", "", "Coventry University", "", "", limit, max_limit, "0", "en")

        expected_result = -20
        expected_error_object = [
            {
                "error": "limit needs to be a positive number, limit cannot be lower than 0",
                "error_values": [{"limit": "-20"}],
            }
        ]
        output_result, output_error_object = validator.validate_limit()

        self.assertEqual(expected_result, output_result)
        self.assertEqual(expected_error_object, output_error_object)

    def test_when_limit_is_not_a_number(self):
        limit = "twenty"
        max_limit = 100
        validator = Validator("", "", "Coventry University", "", "", limit, max_limit, "0", "en")

        expected_result = 0
        expected_error_object = [
            {
                "error": "limit value needs to be a number",
                "error_values": [{"limit": limit}],
            }
        ]
        output_result, output_error_object = validator.validate_limit()

        self.assertEqual(expected_result, output_result)
        self.assertEqual(expected_error_object, output_error_object)


class TestValidateOffset(unittest.TestCase):
    def test_when_offset_is_a_positive_number(self):
        offset = "20"
        validator = Validator("", "", "Coventry University", "", "", "0", 100, offset, "en")

        expected_result = 20
        output_result, output_error_object = validator.validate_offset()

        self.assertEqual(expected_result, output_result)
        self.assertEqual([], output_error_object)

    def test_when_offset_is_a_negative_number(self):
        offset = "-20"
        validator = Validator("", "", "Coventry University", "", "", "0", 100, offset, "en")

        expected_result = -20
        expected_error_object = [
            {
                "error": "offset needs to be a positive number, offset cannot be lower than 0",
                "error_values": [{"offset": offset}],
            }
        ]
        output_result, output_error_object = validator.validate_offset()

        self.assertEqual(expected_result, output_result)
        self.assertEqual(expected_error_object, output_error_object)

    def test_when_offset_is_not_a_number(self):
        offset = "twenty"
        validator = Validator("", "", "Coventry University", "", "", "0", 100, offset, "en")

        expected_result = 0
        expected_error_object = [
            {
                "error": "offset value needs to be a number",
                "error_values": [{"offset": offset}],
            }
        ]
        output_result, output_error_object = validator.validate_offset()

        self.assertEqual(expected_result, output_result)
        self.assertEqual(expected_error_object, output_error_object)


class TestValidateFilters(unittest.TestCase):
    def test_when_empty_filters_returns_no_error(self):
        filters = ""
        validator = Validator("", filters, "", "Coventry University", "", "0", 100, "0", "en")

        output_filters, output_error_object = validator.validate_filters()

        self.assertEqual({}, output_filters)
        self.assertEqual([], output_error_object)

    def test_when_a_filter_is_selected_returns_no_error(self):
        filters = "distance_learning"
        validator = Validator("", filters, "Coventry University", "", "", "0", 100, "0", "en")

        output_filters, output_error_object = validator.validate_filters()
        expected_filters = {"distance_learning": True}

        self.assertEqual(expected_filters, output_filters)
        self.assertEqual([], output_error_object)

    def test_when_a_filter_is_selected_prefixed_with_hyphen_returns_no_error(self):
        filters = "-sandwich_year"
        validator = Validator("", filters, "Coventry University", "", "", "0", 100, "0", "en")

        output_filters, output_error_object = validator.validate_filters()
        expected_filters = {"sandwich_year": False}

        self.assertEqual(expected_filters, output_filters)
        self.assertEqual([], output_error_object)

    def test_when_all_filters_are_selected_returns_no_error(self):
        filters = "-distance_learning,honours_award,foundation_year,sandwich_year,year_abroad,-full_time"
        validator = Validator("", filters, "Coventry University", "", "", "0", 100, "0", "en")

        output_filters, output_error_object = validator.validate_filters()
        expected_filters = {
            "distance_learning": False,
            "foundation_year": True,
            "full_time": False,
            "honours_award": True,
            "sandwich_year": True,
            "year_abroad": True,
        }

        self.assertEqual(expected_filters, output_filters)
        self.assertEqual([], output_error_object)

    def test_when_there_are_duplicate_filters_returns_error(self):
        filters = "-distance_learning,distance_learning"
        validator = Validator("", filters, "", "Coventry University", "", "0", 100, "0", "en")

        output_filters, output_error_object = validator.validate_filters()
        expected_error_object = [
            {
                "error": "use of the same filter option more than once",
                "error_values": [{"filters": "distance_learning"}],
            }
        ]

        self.assertEqual({}, output_filters)
        self.assertEqual(expected_error_object, output_error_object)

    def test_when_there_are_invalid_filters_returns_error(self):
        filters = "salary,distance_learning,PaRt-Time"
        validator = Validator("", filters, "Coventry University", "", "", "0", 100, "0", "en")

        output_filters, output_error_object = validator.validate_filters()
        expected_error_object = [
            {
                "error": "invalid filters",
                "error_values": [{"filters": "salary,PaRt-Time"}],
            }
        ]

        self.assertEqual({}, output_filters)
        self.assertEqual(expected_error_object, output_error_object)

    def test_when_there_both_part_time_and_full_time_filters_set_returns_error(self):
        filters = "full_time,-part_time"
        validator = Validator("", filters, "Coventry University", "", "", "0", 100, "0", "en")

        output_filters, output_error_object = validator.validate_filters()
        expected_error_object = [
            {
                "error": "cannot have both part_time and full_time filters set",
                "error_values": [{"filters": "part_time,full_time"}],
            }
        ]

        self.assertEqual({}, output_filters)
        self.assertEqual(expected_error_object, output_error_object)


class TestValidateFilterOptions(unittest.TestCase):
    def test_distance_learning_is_true(self):
        expected_result = True
        filter = "distance_learning"

        output_result = validate_filter_options(filter)
        self.assertEqual(expected_result, output_result)

    def test_honours_award_is_true(self):
        expected_result = True
        filter = "honours_award"

        output_result = validate_filter_options(filter)
        self.assertEqual(expected_result, output_result)

    def test_foundation_year_is_true(self):
        expected_result = True
        filter = "foundation_year"

        output_result = validate_filter_options(filter)
        self.assertEqual(expected_result, output_result)

    def test_sandwich_year_is_true(self):
        expected_result = True
        filter = "sandwich_year"

        output_result = validate_filter_options(filter)
        self.assertEqual(expected_result, output_result)

    def test_year_abroad_is_true(self):
        expected_result = True
        filter = "year_abroad"

        output_result = validate_filter_options(filter)
        self.assertEqual(expected_result, output_result)

    def test_full_time_is_true(self):
        expected_result = True
        filter = "full_time"

        output_result = validate_filter_options(filter)
        self.assertEqual(expected_result, output_result)

    def test_part_time_is_true(self):
        expected_result = True
        filter = "part_time"

        output_result = validate_filter_options(filter)
        self.assertEqual(expected_result, output_result)

    def test_upper_case_part_time_is_false(self):
        expected_result = False
        filter = "PART_TIME"

        output_result = validate_filter_options(filter)
        self.assertEqual(expected_result, output_result)

    def test_hyphen_in_part_time_is_false(self):
        expected_result = False
        filter = "part-time"

        output_result = validate_filter_options(filter)
        self.assertEqual(expected_result, output_result)


class TestValidateCountries(unittest.TestCase):
    def test_when_empty_countries_returns_no_error(self):
        countries = ""
        validator = Validator(countries, "", "", "Coventry University", "", "0", 100, "0", "en")

        output_countries, output_error_object = validator.validate_countries()

        self.assertEqual([], output_countries)
        self.assertEqual([], output_error_object)

    def test_when_england_is_selected_returns_no_error(self):
        countries = "england"
        validator = Validator(countries, "", "", "Coventry University", "", "0", 100, "0", "en")

        output_countries, output_error_object = validator.validate_countries()

        self.assertEqual(["XF"], output_countries)
        self.assertEqual([], output_error_object)

    def test_when_northern_ireland_is_selected_returns_no_error(self):
        countries = "northern_ireland"
        validator = Validator(countries, "", "", "Coventry University", "", "0", 100, "0", "en")

        output_countries, output_error_object = validator.validate_countries()

        self.assertEqual(["XG"], output_countries)
        self.assertEqual([], output_error_object)

    def test_when_scotland_is_selected_returns_no_error(self):
        countries = "scotland"
        validator = Validator(countries, "", "", "Coventry University", "", "0", 100, "0", "en")

        output_countries, output_error_object = validator.validate_countries()

        self.assertEqual(["XH"], output_countries)
        self.assertEqual([], output_error_object)

    def test_when_wales_is_selected_returns_no_error(self):
        countries = "wales"
        validator = Validator(countries, "", "", "Coventry University", "", "0", 100, "0", "en")

        output_countries, output_error_object = validator.validate_countries()

        self.assertEqual(["XI"], output_countries)
        self.assertEqual([], output_error_object)

    def test_when_multiple_countries_are_selected_returns_no_error(self):
        countries = "england,wales"
        validator = Validator(countries, "", "", "Coventry University", "", "0", 100, "0", "en")

        output_countries, output_error_object = validator.validate_countries()

        self.assertEqual(["XF", "XI"], output_countries)
        self.assertEqual([], output_error_object)

    def test_when_a_country_is_selected_prefixed_with_hyphen_returns_no_error(self):
        countries = "-england"
        validator = Validator(countries, "", "", "Coventry University", "", "0", 100, "0", "en")

        output_countries, output_error_object = validator.validate_countries()

        self.assertEqual(["XG", "XH", "XI"], output_countries)
        self.assertEqual([], output_error_object)

    def test_when_there_are_duplicate_countries_returns_error(self):
        countries = "england,-england"
        validator = Validator(countries, "", "", "Coventry University", "", "0", 100, "0", "en")

        output_countries, output_error_object = validator.validate_countries()
        expected_error_object = [
            {
                "error": "use of the same countries more than once",
                "error_values": [{"countries": "england"}],
            }
        ]

        self.assertEqual([], output_countries)
        self.assertEqual(expected_error_object, output_error_object)

    def test_when_there_are_invalid_uk_countries_returns_error(self):
        countries = "bosnia,photosynthesis,england"
        validator = Validator(countries, "", "", "Coventry University", "", "0", 100, "0", "en")

        output_countries, output_error_object = validator.validate_countries()
        expected_error_object = [
            {
                "error": "invalid countries",
                "error_values": [{"countries": "bosnia,photosynthesis"}],
            }
        ]

        self.assertEqual([], output_countries)
        self.assertEqual(expected_error_object, output_error_object)


class TestCheckCountryIsValid(unittest.TestCase):
    def test_england_returns_country_code(self):
        expected_result = "XF"
        country = "england"

        output_result = check_country_is_valid(country)
        self.assertEqual(expected_result, output_result)

    def test_northern_ireland_returns_country_code(self):
        expected_result = "XG"
        country = "northern_ireland"

        output_result = check_country_is_valid(country)
        self.assertEqual(expected_result, output_result)

    def test_scotland_returns_country_code(self):
        expected_result = "XH"
        country = "scotland"

        output_result = check_country_is_valid(country)
        self.assertEqual(expected_result, output_result)

    def test_wales_returns_country_code(self):
        expected_result = "XI"
        country = "wales"

        output_result = check_country_is_valid(country)
        self.assertEqual(expected_result, output_result)

    def test_upper_case_country_returns_empty_string(self):
        expected_result = ""
        country = "SCOTLAND"

        output_result = check_country_is_valid(country)
        self.assertEqual(expected_result, output_result)

    def test_invalid_uk_country_returns_empty_string(self):
        expected_result = ""
        country = "france"

        output_result = check_country_is_valid(country)
        self.assertEqual(expected_result, output_result)


class TestIsInt(unittest.TestCase):
    def test_when_string_contains_an_integer(self):
        expected_is_int = True
        expected_new_value = 1
        value = "1"

        output_is_int, output_new_value = is_int(value)
        self.assertEqual(expected_is_int, output_is_int)
        self.assertEqual(expected_new_value, output_new_value)

    def test_when_string_contains_a_negative_number(self):
        expected_is_int = True
        expected_new_value = -1
        value = "-1"

        output_is_int, output_new_value = is_int(value)
        self.assertEqual(expected_is_int, output_is_int)
        self.assertEqual(expected_new_value, output_new_value)

    def test_when_string_does_not_contain_an_integer(self):
        expected_is_int = False
        expected_new_value = None
        value = "one"

        output_is_int, output_new_value = is_int(value)
        self.assertEqual(expected_is_int, output_is_int)
        self.assertEqual(expected_new_value, output_new_value)


class TestValidateLengthOfCourse(unittest.TestCase):
    def test_when_empty_length_of_course_returns_no_error(self):
        length_of_course = ""
        validator = Validator("", "", "Coventry University", length_of_course, "", "0", 100, "0", "en")

        output_lengths, output_error_object = validator.validate_length_of_course()

        self.assertEqual([], output_lengths)
        self.assertEqual([], output_error_object)

    def test_when_a_valid_length_of_course_returns_no_error(self):
        length_of_course = "4"
        validator = Validator("", "", "Coventry University", length_of_course, "", "0", 100, "0", "en")

        output_lengths, output_error_object = validator.validate_length_of_course()

        self.assertEqual(["4"], output_lengths)
        self.assertEqual([], output_error_object)

    def test_when_multiple_valid_length_of_course_returns_no_error(self):
        length_of_course = "1,7"
        validator = Validator("", "", "Coventry University", length_of_course, "", "0", 100, "0", "en")

        output_lengths, output_error_object = validator.validate_length_of_course()

        self.assertEqual(["1", "7"], output_lengths)
        self.assertEqual([], output_error_object)

    def test_when_length_of_course_is_not_a_number_returns_error(self):
        length_of_course = "four,3"
        validator = Validator("", "", "Coventry University", length_of_course, "", "0", 100, "0", "en")

        output_lengths, output_error_object = validator.validate_length_of_course()
        expected_error_object = [
            {
                "error": "length_of_course values needs to be a number",
                "error_values": [{"length_of_course": "four"}],
            }
        ]

        self.assertEqual([], output_lengths)
        self.assertEqual(expected_error_object, output_error_object)

    def test_when_length_of_course_is_above_maximum_number_of_years_returns_error(self):
        length_of_course = "8"
        validator = Validator("", "", "Coventry University", length_of_course, "", "0", 100, "0", "en")

        output_lengths, output_error_object = validator.validate_length_of_course()
        expected_error_object = [
            {
                "error": "length_of_course values needs to be numbers between the range of 1 and 7",
                "error_values": [{"length_of_course": "8"}],
            }
        ]

        self.assertEqual([], output_lengths)
        self.assertEqual(expected_error_object, output_error_object)

    def test_when_length_of_course_is_above_minimum_number_of_years_returns_error(self):
        length_of_course = "0"
        validator = Validator("", "", "Coventry University", length_of_course, "", "0", 100, "0", "en")

        output_lengths, output_error_object = validator.validate_length_of_course()
        expected_error_object = [
            {
                "error": "length_of_course values needs to be numbers between the range of 1 and 7",
                "error_values": [{"length_of_course": "0"}],
            }
        ]

        self.assertEqual([], output_lengths)
        self.assertEqual(expected_error_object, output_error_object)


class TestValidate(unittest.TestCase):
    def test_when_all_query_params_are_set(self):
        limit = 5
        offset = "30"
        filters = "distance_learning,honours_award,-foundation_year,sandwich_year,-year_abroad,full_time"
        institution = "Coventry University"
        length_of_course = "3,4"
        countries = "england,wales"
        subjects = "CAH09-01-01,CAH09-01-02"
        language = "en"

        validator = Validator(
            countries, filters, institution, length_of_course, subjects, limit, 100, offset, language
        )

        expected_result = {
            "countries": ["XF", "XI"],
            "distance_learning": True,
            "foundation_year": False,
            "full_time": True,
            "honours_award": True,
            "language": "en",
            "length_of_course": ["3", "4"],
            "limit": 5,
            "offset": 30,
            "sandwich_year": True,
            "subjects": ["CAH09-01-01", "CAH09-01-02"],
            "year_abroad": False,
        }
        output_result, output_error_object = validator.validate()

        self.assertEqual(expected_result, output_result)
        self.assertEqual([], output_error_object)

    def test_when_all_query_params_are_bad(self):
        limit = 200
        offset = "-30"
        filters = "illusion,Part_Time,full_time,-full_time"
        institution = ""
        length_of_course = "-2,8,twenty"
        countries = "bolivia,-england,england"
        subjects = 32
        language = 'bad'

        validator = Validator(
            countries, filters, institution, length_of_course, subjects, limit, 100, offset, language
        )

        expected_result = {}
        output_result, output_error_object = validator.validate()
        expected_error_object = [
            {
                "error": "limit cannot exceed maximum value of 100",
                "error_values": [{"limit": 200}],
            },
            {
                "error": "offset needs to be a positive number, offset cannot be lower than 0",
                "error_values": [{"offset": "-30"}],
            },
            {
                "error": "use of the same filter option more than once",
                "error_values": [{"filters": "full_time"}],
            },
            {
                "error": "invalid filters",
                "error_values": [{"filters": "illusion,Part_Time"}],
            },
            {
                "error": "use of the same countries more than once",
                "error_values": [{"countries": "england"}],
            },
            {"error": "invalid countries", "error_values": [{"countries": "bolivia"}]},
            {
                "error": "length_of_course values needs to be a number",
                "error_values": [{"length_of_course": "twenty"}],
            },
            {
                "error": "length_of_course values needs to be numbers between the range of 1 and 7",
                "error_values": [{"length_of_course": "-2,8"}],
            },
            {
                'error': 'missing value for mandatory field: institution',
                'error_values': [{'institution': ''}],
            },
            {
                'error': 'value of language is not supported',
                'error_values': [{'language': 'bad'}],
            }
        ]

        print(f"output: {output_error_object}")

        self.assertEqual(expected_result, output_result)
        self.assertEqual(expected_error_object, output_error_object)
