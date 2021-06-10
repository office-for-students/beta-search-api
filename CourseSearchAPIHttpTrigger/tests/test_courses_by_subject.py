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
        # self.assertEqual(actual, expected)

        self.assertEqual(len(actual['Marketing']), 250)
        self.assertEqual(len(actual['Business studies']), 37)
        self.assertEqual(len(actual['Design studies']), 24)
        self.assertEqual(len(actual['Management studies']), 19)
        self.assertEqual(len(actual['Tourism, transport and travel']), 9)
        self.assertEqual(len(actual['Courses in other subjects']), 20)
        self.assertEqual(actual.get('Agriculture'), None) 
        self.assertEqual(actual.get('Business and management (non-specific)'), None) 
        self.assertEqual(actual.get('Economics'), None) 
        self.assertEqual(actual.get('Food and beverage production'), None) 
        self.assertEqual(actual.get('Human resource management'), None) 
        self.assertEqual(actual.get('Nutrition and dietetics'), None) 
        self.assertEqual(actual.get('Others in business and management'), None) 
        self.assertEqual(actual.get('Others in creative arts and design'), None) 

        # self.assertEqual(len(actual['Business and management & Marketing']), 13)
        self.assertEqual(len(actual['Business studies & Marketing']), 59)
        self.assertEqual(len(actual['Economics & Marketing']), 8)
        self.assertEqual(len(actual['Marketing & Design studies']), 22)
        self.assertEqual(len(actual['Marketing & Journalism']), 13)
        self.assertEqual(len(actual['Marketing & Management studies']), 50)
        self.assertEqual(len(actual['Marketing & Media studies']), 20)
        self.assertEqual(len(actual['Marketing & Publicity studies']), 15)
        self.assertEqual(len(actual['Marketing & Tourism, transport and travel']), 22)
        # self.assertEqual(len(actual['Psychology & Marketing']), 10)
        # self.assertEqual(len(actual['Other combinations with Marketing']), 111)
        # self.assertEqual(len(actual['Other combinations']), 14)


