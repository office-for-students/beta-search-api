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
        queried_course_title = "marketing"

        mapper = CourseToLabelMapper(course_to_label_mapping)
        courseBySubject = CoursesBySubject(mapper)

        # ACT
        actual = courseBySubject.group(queried_course_title,
                                       courses,
                                       counts, 
                                       int(limit),
                                       int(offset), 
                                       language,
                                       )

        # ASSERT
        # self.assertEqual(actual, expected)

        self.assertEqual(len(actual['single_subject_courses']['Marketing courses']), 250)
        self.assertEqual(len(actual['single_subject_courses']['Business studies courses']), 37)
        self.assertEqual(len(actual['single_subject_courses']['Design studies courses']), 24)
        self.assertEqual(len(actual['single_subject_courses']['Management studies courses']), 19)
        self.assertEqual(len(actual['single_subject_courses']['Tourism, transport and travel courses']), 9)
        self.assertEqual(len(actual['single_subject_courses']['Courses in other subjects']), 20)
        self.assertEqual(len(actual['single_subject_courses'].keys()), 6)
        # TODO check order

        self.assertEqual(len(actual['multiple_subject_courses']['Business and management & Marketing courses']), 13)
        self.assertEqual(len(actual['multiple_subject_courses']['Business studies & Marketing courses']), 59)
        self.assertEqual(len(actual['multiple_subject_courses']['Economics & Marketing courses']), 8)
        self.assertEqual(len(actual['multiple_subject_courses']['Marketing & Design studies courses']), 22)
        self.assertEqual(len(actual['multiple_subject_courses']['Marketing & Journalism courses']), 13)
        self.assertEqual(len(actual['multiple_subject_courses']['Marketing & Management studies courses']), 50)
        self.assertEqual(len(actual['multiple_subject_courses']['Marketing & Media studies courses']), 20)
        self.assertEqual(len(actual['multiple_subject_courses']['Marketing & Publicity studies courses']), 15)
        self.assertEqual(len(actual['multiple_subject_courses']['Marketing & Tourism, transport and travel courses']), 22)
        self.assertEqual(len(actual['multiple_subject_courses']['Psychology & Marketing courses']), 10)
        self.assertEqual(len(actual['multiple_subject_courses']['Other combinations with Marketing']), 111)
        self.assertEqual(len(actual['multiple_subject_courses']['Other combinations']), 14)
        self.assertEqual(len(actual['multiple_subject_courses'].keys()), 12)
        # TODO check order

        self.assertEqual(len(actual.keys()), 2)



