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
from courses_by_subject import build_course

MAPPING_DIR = f'{PARENT_DIR}/fixtures'
FIXTURES_DIR = f'{CURRENT_DIR}/fixtures/courses_by_subject'


class TestCoursesBySubject(unittest.TestCase):

    def test_when_marketing_course_queried(self):
        # ARRANGE
        mappings = self.load_mappings()
        mapper = CourseToLabelMapper(mappings)
        courseBySubject = CoursesBySubject(mapper)

        courses = self.load_fixture('input.json')
        expected = self.load_fixture('output.json')

        queried_course_title = 'marketing'
        counts = {'institutions': 131, 'courses': 716}
        limit = 5000
        offset = 0
        language = 'en'


        # ACT
        actual = courseBySubject.group(queried_course_title,
                                        courses,
                                        counts, 
                                        limit,
                                        offset, 
                                        language,
                                        )

        # ASSERT
        items = actual['items']
        self.assertEqual(len(items.keys()), 2)

        # single_subject_courses
        courses = items['single_subject_courses']
        self.assertEqual(courses['Marketing courses']['number_of_courses'], 250)
        self.assertEqual(courses['Business studies courses']['number_of_courses'], 37)
        self.assertEqual(courses['Design studies courses']['number_of_courses'], 24)
        self.assertEqual(courses['Management studies courses']['number_of_courses'], 19)
        self.assertEqual(courses['Tourism, transport and travel courses']['number_of_courses'], 9)
        self.assertEqual(courses['Courses in other subjects']['number_of_courses'], 20)
        self.assertEqual(list(courses.keys()), [
            'Marketing courses',
            'Business studies courses',
            'Design studies courses',
            'Management studies courses',
            'Tourism, transport and travel courses',
            'Courses in other subjects',
            ]
        )

        # multiple_subject_courses
        courses = items['multiple_subject_courses']
        self.assertEqual(courses['Business and management & Marketing courses']['number_of_courses'], 13)
        self.assertEqual(courses['Business studies & Marketing courses']['number_of_courses'], 59)
        self.assertEqual(courses['Economics & Marketing courses']['number_of_courses'], 8)
        self.assertEqual(courses['Marketing & Design studies courses']['number_of_courses'], 22)
        self.assertEqual(courses['Marketing & Journalism courses']['number_of_courses'], 13)
        self.assertEqual(courses['Marketing & Management studies courses']['number_of_courses'], 50)
        self.assertEqual(courses['Marketing & Media studies courses']['number_of_courses'], 20)
        self.assertEqual(courses['Marketing & Publicity studies courses']['number_of_courses'], 15)
        self.assertEqual(courses['Marketing & Tourism, transport and travel courses']['number_of_courses'], 22)
        self.assertEqual(courses['Psychology & Marketing courses']['number_of_courses'], 10)
        self.assertEqual(courses['Other combinations with Marketing']['number_of_courses'], 111)
        self.assertEqual(courses['Other combinations']['number_of_courses'], 14)
        self.assertEqual(list(courses.keys()), [
            'Business and management & Marketing courses',
            'Business studies & Marketing courses',
            'Economics & Marketing courses',
            'Marketing & Design studies courses',
            'Marketing & Journalism courses',
            'Marketing & Management studies courses',
            'Marketing & Media studies courses',
            'Marketing & Publicity studies courses',
            'Marketing & Tourism, transport and travel courses',
            'Psychology & Marketing courses',
            'Other combinations with Marketing',
            'Other combinations',
            ]
        )

        self.assertEqual(actual, expected)


    def test_build_course_using_english_language(self):
        self.assert_buld_course('build_course_en_input.json', 'build_course_en_output.json')


    def test_build_course_using_welsh_language(self):
        self.assert_buld_course('build_course_cy_input.json', 'build_course_cy_output.json')


    def assert_buld_course(self, filename_input, filename_expected):
        # ARRANGE
        input = self.load_fixture(filename_input)
        expected = self.load_fixture(filename_expected)
        
        # ACT
        actual = build_course(input['course'], input['institution'], input['language'])

        # ASSERT
        self.assertEqual(actual, expected)


    def load_fixture(self, filename):
        return self.load_file(FIXTURES_DIR, filename)


    def load_mappings(self):
        return self.load_file(f'{MAPPING_DIR}', 'subjects-sort-by.json')


    def load_file(self, dir, filename):
        with open(f'{dir}/{filename}', 'r') as file:
            input = file.read()
        return json.loads(input)
