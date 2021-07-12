import unittest
from unittest import mock
import os

from query import Query

#  --------------------------------------------------------------------------------------------------------------------
# | On campus | Distance learning | KISCOURSE/DISTANCE value | Alternative | Expected no of courses returned (approx.) |
# |   :---:   |      :---:        |           :---:          |     :---:   |                 ---                       |
# |     -     |        -          |         0 or 1 or 2      |             | 1814 courses from 115 providers           |
# |     X     |        -          |         0 or 2           |     ne 1    | 1804 courses from 115 providers           |
# |     -     |        X          |         1 or 2           |     ne 0    | 10 courses from 2 providers               |
# |     X     |        X          |         0 or 1 or 2      |             | 1814 courses from 115 providers           |
#  --------------------------------------------------------------------------------------------------------------------
class TestBuildDistanceLearningFilter(unittest.TestCase):
    doc = 'course/distance_learning/code'

    def setUp(self):
        self.query_params = {}

    def execute(self, expected):
        actual = Query.build_distance_learning_filter(self.query_params)
        self.assertEqual(actual, expected)

    def test_when_no_options_selected(self):
        self.query_params['on_campus'] = False
        self.query_params['distance_learning'] = False
        expected = f'({self.doc} eq 0 or {self.doc} eq 1 or {self.doc} eq 2)'
        self.execute(expected)

    def test_when_on_campus_only(self):
        self.query_params['on_campus'] = True
        self.query_params['distance_learning'] = False
        expected = f'{self.doc} ne 1'
        self.execute(expected)

    def test_when_distance_learning_only(self):
        self.query_params['on_campus'] = False
        self.query_params['distance_learning'] = True
        expected = f'{self.doc} ne 0'
        self.execute(expected)

    def test_when_both_options_selected(self):
        self.query_params['on_campus'] = True
        self.query_params['distance_learning'] = True
        expected = f'({self.doc} eq 0 or {self.doc} eq 1 or {self.doc} eq 2)'
        self.execute(expected)


class TestCampusDistanceWithCountry(unittest.TestCase):

#  -----------------------------------------------------------------------------------------------------------------------------------------------------------
# | On campus | Distance learning |   Wales   |   Scotland   |    N.I.   | KISCOURSE/DISTANCE value | Alternative | Expected no of courses returned (approx.) |
# |   :---:   |      :---:        |   :---:   |    :---:     |   :---:   |           :---:          |     :---:   |                 ---                       |
# |     O     |        X          |     O     |      -       |     -     |         1 or 2           |     ne 0    | 149 courses from 9 providers              |
# |     -     |        -          |     -     |      O       |     O     |         1 or 2           |     ne 0    | 546 courses from 12 providers             |
# |     O     |        X          |     -     |      O       |     O     |         1 or 2           |     ne 0    | 546 courses from 12 providers             |
#  -----------------------------------------------------------------------------------------------------------------------------------------------------------

    doc = 'course/distance_learning/code'

    def setUp(self):
        self.query_params = {}
        self.filters = []
    
    def execute(self, expected):
        actual = Query.build_or_distance_filter(self.query_params, self.filters)
        self.assertEqual(actual, expected)


    def test_campus_removed_when_both_selected(self):
        self.query_params['on_campus'] = True
        self.query_params['distance_learning'] = True
        build_array = Query.build_distance_learning_filter(self.query_params)
        self.filters.append(build_array)
        expected = [f'{self.doc} ne 0']
        self.execute(expected)


    def test_country_removed_when_only_distance_selected(self):
        self.query_params['on_campus'] = False
        self.query_params['distance_learning'] = True
        self.query_params['countries'] = ['Wales']
        build_array = Query.build_distance_learning_filter(self.query_params)
        build_country_array = Query.build_country_filter(self.query_params)
        self.filters.append(build_array)
        self.filters.append(build_country_array)
        expected = [f'{self.doc} ne 0']
        self.execute(expected)

        
    def test_country_and_campus_removed_when_both_selected(self):
        self.query_params['on_campus'] = True
        self.query_params['distance_learning'] = True
        self.query_params['countries'] = ['Wales']
        build_array = Query.build_distance_learning_filter(self.query_params)
        build_country_array = Query.build_country_filter(self.query_params)
        self.filters.append(build_array)
        self.filters.append(build_country_array)
        expected = [f'{self.doc} ne 0']
        self.execute(expected)


    def test_countries_and_campus_removed_when_both_selected(self):
        self.query_params['on_campus'] = True
        self.query_params['distance_learning'] = True
        self.query_params['countries'] = ['Wales', 'Scotland', 'England']
        build_array = Query.build_distance_learning_filter(self.query_params)
        build_country_array = Query.build_country_filter(self.query_params)
        self.filters.append(build_array)
        self.filters.append(build_country_array)
        expected = [f'{self.doc} ne 0']
        self.execute(expected)



class TestInsitituionFilter(unittest.TestCase):
    doc_cy = "course/institution/pub_ukprn_welsh_name eq"
    doc = "course/institution/pub_ukprn_name eq"
    doc_ukprn = "course/institution/pub_ukprn eq"

    def setUp(self):
        self.institutions = ""
        self.query_params = {}
    
    def execute(self, expected):
        actual = Query.build_institution_filter(self.institutions, self.query_params)
        self.assertEqual(actual, expected)

    @mock.patch.dict(os.environ, {"SearchPubUKPRN": "False"})
    def test_with_one_institution_selected(self):
        self.institutions = 'University of Southampton'
        self.query_params["language"] = {}
        build_array = Query.build_institution_filter(self.institutions, self.query_params)
        expected = [f"{self.doc} 'University of Southampton'"]
        self.execute(expected)

    @mock.patch.dict(os.environ, {"SearchPubUKPRN": "False"})
    def test_with_multiple_institutions_selected(self):
        self.institutions = 'University of Southampton@University Two@University Three'
        self.query_params["language"] = {}
        build_array = Query.build_institution_filter(self.institutions, self.query_params)
        expected = [f"({self.doc} 'University of Southampton' or {self.doc} 'University Two' or {self.doc} 'University Three')"]
        self.execute(expected)

    @mock.patch.dict(os.environ, {"SearchPubUKPRN": "False"})
    def test_with_multiple_institutions_welsh(self):
        self.institutions = 'University of Southampton@University Two@University Three'
        self.query_params["language"] = 'cy'
        build_array = Query.build_institution_filter(self.institutions, self.query_params)
        expected = [f"({self.doc_cy} 'University of Southampton' or {self.doc_cy} 'University Two' or {self.doc_cy} 'University Three')"]
        self.execute(expected)

    @mock.patch.dict(os.environ, {"SearchPubUKPRN": "True"})
    def test_multiple_with_SearchPubUKPRN_set_true(self):
        self.institutions = 'University of Southampton@University Two@University Three'
        self.query_params["language"] = 'cy'
        build_array = Query.build_institution_filter(self.institutions, self.query_params)
        expected = [f"({self.doc_ukprn} 'University of Southampton' or {self.doc_ukprn} 'University Two' or {self.doc_ukprn} 'University Three')"]
        self.execute(expected)