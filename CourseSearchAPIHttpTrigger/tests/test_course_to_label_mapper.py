import os
import inspect
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

import course_to_label_mapper
from course_to_label_mapper import CourseToLabelMapper

language_english = 'en'
language_welsh = 'cy'

class TestCourseToLabelMapper(unittest.TestCase):
    def test_convert_to_dictionary(self):
        actual = CourseToLabelMapper.convert_to_dictionary(self, data)
        self.assertEqual(actual, expected)
        self.assertEqual(actual['CAH17-01-08']['english_name'], 'Accounting')
        self.assertEqual(actual['CAH02-04-02']['welsh_name'], 'Nyrsio oedolion')

    def test_when_no_subject_found_return_None(self):
        subject = 'something-that-does-not-exist'
        actual = CourseToLabelMapper(data, language_english).get_label(subject)
        expected = None
        self.assertEqual(actual, expected)

    def test_when_subject_found_return_english_label(self):
        subject = 'CAH17-01-08'
        actual = CourseToLabelMapper(data, language_english).get_label(subject)
        self.assertEqual(actual, 'Accounting')

    def test_when_subject_found_return_welsh_label(self):
        subject = 'CAH17-01-08'
        actual = CourseToLabelMapper(data, language_welsh).get_label(subject)
        self.assertEqual(actual, 'Cyfrifeg')


data = [{
    "code": "CAH17-01-08",
    "english_name": "Accounting",
    "welsh_name": "Cyfrifeg",
    "level": "3"
}, {
    "code": "CAH02-04-02",
    "english_name": "Adult nursing",
    "welsh_name": "Nyrsio oedolion",
    "level": "3"
}]

expected = {
    "CAH17-01-08": {
        "english_name": "Accounting",
        "welsh_name": "Cyfrifeg",
    },
    "CAH02-04-02": {
        "english_name": "Adult nursing",
        "welsh_name": "Nyrsio oedolion",
    }
}
