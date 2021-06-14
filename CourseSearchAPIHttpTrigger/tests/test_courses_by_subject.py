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
        courses = self.load_fixture('input.json')
        expected = self.load_fixture('output.json')
        queried_course_title = "marketing"
        language = "en"

        # ACT
        actual = self.courseBySubject.group(queried_course_title,
                                       courses,
                                       self.counts, 
                                       int(self.limit),
                                       int(self.offset), 
                                       language,
                                       )

        # ASSERT
        items = actual["items"]
        self.assertEqual(len(items.keys()), 2)

        # single_subject_courses
        self.assertEqual(len(items['single_subject_courses']['Marketing courses']), 250)
        self.assertEqual(len(items['single_subject_courses']['Business studies courses']), 37)
        self.assertEqual(len(items['single_subject_courses']['Design studies courses']), 24)
        self.assertEqual(len(items['single_subject_courses']['Management studies courses']), 19)
        self.assertEqual(len(items['single_subject_courses']['Tourism, transport and travel courses']), 9)
        self.assertEqual(len(items['single_subject_courses']['Courses in other subjects']), 20)
        self.assertEqual(list(items['single_subject_courses'].keys()), [
            'Marketing courses',
            'Business studies courses',
            'Design studies courses',
            'Management studies courses',
            'Tourism, transport and travel courses',
            'Courses in other subjects',
            ]
        )

        # multiple_subject_courses
        self.assertEqual(len(items['multiple_subject_courses']['Business and management & Marketing courses']), 13)
        self.assertEqual(len(items['multiple_subject_courses']['Business studies & Marketing courses']), 59)
        self.assertEqual(len(items['multiple_subject_courses']['Economics & Marketing courses']), 8)
        self.assertEqual(len(items['multiple_subject_courses']['Marketing & Design studies courses']), 22)
        self.assertEqual(len(items['multiple_subject_courses']['Marketing & Journalism courses']), 13)
        self.assertEqual(len(items['multiple_subject_courses']['Marketing & Management studies courses']), 50)
        self.assertEqual(len(items['multiple_subject_courses']['Marketing & Media studies courses']), 20)
        self.assertEqual(len(items['multiple_subject_courses']['Marketing & Publicity studies courses']), 15)
        self.assertEqual(len(items['multiple_subject_courses']['Marketing & Tourism, transport and travel courses']), 22)
        self.assertEqual(len(items['multiple_subject_courses']['Psychology & Marketing courses']), 10)
        self.assertEqual(len(items['multiple_subject_courses']['Other combinations with Marketing']), 111)
        self.assertEqual(len(items['multiple_subject_courses']['Other combinations']), 14)
        self.assertEqual(list(items['multiple_subject_courses'].keys()), [
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


    # TODO do the same for law
    def test_when_welsh_course_queried(self):
        # ARRANGE
        courses = self.load_fixture('input.json')
        queried_course_title = "welsh"
        language = "en"

        # ACT
        actual = self.courseBySubject.group(queried_course_title,
                                       courses,
                                       self.counts, 
                                       int(self.limit),
                                       int(self.offset), 
                                       language,
                                       )

        # ASSERT
        items = actual["items"]
        self.assertEqual(len(items.keys()), 2)


    def test_build_course_using_english_language(self):
        self.buld_course('build_course_en_input.json', 'build_course_en_output.json')


    def test_build_course_using_welsh_language(self):
        self.buld_course('build_course_cy_input.json', 'build_course_cy_output.json')


    def buld_course(self, filename_input, filename_expected):
        # ARRANGE
        input = self.load_fixture(filename_input)
        expected = self.load_fixture(filename_expected)
        
        # ACT
        actual = build_course(input["course"], input["institution"], input["language"])

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


    def setUp(self):
        self.counts = {'institutions': 131, 'courses': 716}
        self.limit = "5000"
        self.offset = "0"
        mappings = self.load_mappings()
        mapper = CourseToLabelMapper(mappings)
        self.courseBySubject = CoursesBySubject(mapper)
