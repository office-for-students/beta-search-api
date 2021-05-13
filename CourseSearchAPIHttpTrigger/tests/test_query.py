import unittest

from query import Query

#  ------------------------------------------------------------------------------------------------------
# | On campus | Distance learning | KISCOURSE/DISTANCE value | Expected no of courses returned (approx.) |
# | ----------|-------------------|--------------------------|-------------------------------------------|
# |     -     |        -          |          0, 1, 2         | 1814 courses from 115 providers           |
# |     X     |        -          |          0, 2            | 1804 courses from 115 providers           |
# |     -     |        X          |          1, 2            | 10 courses from 2 providers               |
# |     X     |        X          |          0, 1, 2         | 1814 courses from 115 providers           |
#  ------------------------------------------------------------------------------------------------------
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
        expected = f'({self.doc} eq 0 or {self.doc} eq 2)'
        self.execute(expected)

    def test_when_distance_learning_only(self):
        self.query_params['on_campus'] = False
        self.query_params['distance_learning'] = True
        expected = f'({self.doc} eq 1 or {self.doc} eq 2)'
        self.execute(expected)

    def test_when_both_options_selected(self):
        self.query_params['on_campus'] = True
        self.query_params['distance_learning'] = True
        expected = f'({self.doc} eq 0 or {self.doc} eq 1 or {self.doc} eq 2)'
        self.execute(expected)
