import unittest

from query import Query

class TestBuildDistanceLearningFilter(unittest.TestCase):

    def setUp(self):
        self.query_params = {}

    def test_when_filter_present(self):
        self.query_params['distance_learning'] = True
        expected = 'course/distance_learning/code ne 0'
        self.execute(expected)

    def test_when_filter_absent(self):
        self.query_params['distance_learning'] = False
        expected = 'course/distance_learning/code ne 1'
        self.execute(expected)

    def execute(self, expected):
        actual = Query.build_distance_learning_filter(self.query_params)
        self.assertEqual(actual, expected)
