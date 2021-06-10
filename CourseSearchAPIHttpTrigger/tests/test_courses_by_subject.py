import inspect
import json
import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

from course_to_label_mapper import CourseToLabelMapper
from courses_by_subject import CoursesBySubject

MAPPING_FILE = f'{PARENT_DIR}/fixtures/subjects-sort-by.json'
FIXTURES_DIR = f'{CURRENT_DIR}/fixtures/courses_by_subject'


class TestCoursesBySubject(unittest.TestCase):
    def test_blah(self):
        # ARRANGE
        with open(f'{MAPPING_FILE}', 'r') as file:
            mapping = file.read()
        course_to_label_mapping = json.loads(mapping)

        with open(f'{FIXTURES_DIR}/input.json', 'r') as file:
            input = file.read()
        courses = json.loads(input)

        with open(f'{FIXTURES_DIR}/output.json', 'r') as file:
            output = file.read()
        expected = json.loads(output)

        counts = {'institutions': 432, 'courses': 29167}
        limit = "20"
        offset = "0"
        language = "en"

        mapper = CourseToLabelMapper(course_to_label_mapping)
        courseBySubject = CoursesBySubject(mapper)

        # ACT
        actual = courseBySubject.group(courses,
                                       counts, 
                                       int(limit),
                                       int(offset), 
                                       language)

        # ASSERT
        self.assertEqual(actual, expected)
