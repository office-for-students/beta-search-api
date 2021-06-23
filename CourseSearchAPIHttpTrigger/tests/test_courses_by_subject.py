import inspect
import json
import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
MAPPING_DIR = f'{PARENT_DIR}/fixtures'
FIXTURES_DIR = f'{CURRENT_DIR}/fixtures/courses_by_subject'
sys.path.insert(0, PARENT_DIR)

from course_to_label_mapper import CourseToLabelMapper
from courses_by_subject import CoursesBySubject
from courses_by_subject import build_course


# To invoke function directly, open the following in a browser
# http://localhost:7071/api/CourseSearchAPIHttpTrigger?qc=marketing&sortBySubject=true&sortBySubjectLimit=5000&limit=5000
class TestCoursesBySubject(unittest.TestCase):

    def test_when_marketing_course_queried(self):
        # ARRANGE
        mappings = self.load_mappings()
        mapper = CourseToLabelMapper(mappings)
        courseBySubject = CoursesBySubject(mapper)

        courses = self.load_fixture('input_marketing.json')
        expected = self.load_fixture('output_marketing.json')

        counts = {'institutions': 131, 'courses': 716}
        limit = 5000
        offset = 0
        language = 'en'

        # ACT
        actual = courseBySubject.group(courses,
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
    

    def test_when_bioengineering_course_queried(self):
        # ARRANGE
        mappings = self.load_mappings()
        mapper = CourseToLabelMapper(mappings)
        courseBySubject = CoursesBySubject(mapper)

        courses = self.load_fixture('input_bioengineering.json')

        counts = {'institutions': 131, 'courses': 716}
        limit = 5000
        offset = 0
        language = 'en'

        # ACT
        actual = courseBySubject.group(courses,
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
        self.assertEqual(courses['Bioengineering, medical and biomedical engineering courses']['number_of_courses'], 10)
        self.assertEqual(courses['Engineering courses']['number_of_courses'], 2)
        self.assertEqual(courses['Mechanical engineering courses']['number_of_courses'], 1)
        self.assertEqual(list(courses.keys()), [
            'Bioengineering, medical and biomedical engineering courses',
            'Engineering courses',
            'Mechanical engineering courses',
            ]
        )
    
    
    def test_when_food_course_queried(self):
        # ARRANGE
        mappings = self.load_mappings()
        mapper = CourseToLabelMapper(mappings)
        courseBySubject = CoursesBySubject(mapper)

        courses = self.load_fixture('input_food.json')

        counts = {'institutions': 131, 'courses': 716}
        limit = 5000
        offset = 0
        language = 'en'

        # ACT
        actual = courseBySubject.group(courses,
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
        self.assertEqual(courses['Food sciences courses']['number_of_courses'], 31)
        self.assertEqual(courses['Nutrition and dietetics courses']['number_of_courses'], 16)
        self.assertEqual(courses['Food and beverage studies courses']['number_of_courses'], 8)
        self.assertEqual(courses['Food and beverage production courses']['number_of_courses'], 7)
        self.assertEqual(courses['Tourism, transport and travel courses']['number_of_courses'], 4)
        self.assertEqual(courses['Agriculture courses']['number_of_courses'], 3)
        self.assertEqual(courses['Teacher training courses']['number_of_courses'], 2)
        self.assertEqual(courses['Biosciences courses']['number_of_courses'], 2)
        self.assertEqual(courses['Courses in other subjects']['number_of_courses'], 1)
        self.assertEqual(list(courses.keys()), [
            'Food sciences courses',
            'Nutrition and dietetics courses',
            'Food and beverage studies courses',
            'Food and beverage production courses',
            'Tourism, transport and travel courses',
            'Agriculture courses',
            'Biosciences courses', 
            'Teacher training courses',
            'Courses in other subjects',
            ]
        )

        # multiple_subject_courses
        courses = items['multiple_subject_courses']
        self.assertEqual(courses['Agriculture & Business and management courses']['number_of_courses'], 2)
        self.assertEqual(courses['Ecology and environmental biology & Agricultural sciences courses']['number_of_courses'], 3)
        self.assertEqual(courses['Food and beverage production & Marketing courses']['number_of_courses'], 3)
        self.assertEqual(courses['Nutrition and dietetics & Food and beverage production courses']['number_of_courses'], 3)
        self.assertEqual(courses['Nutrition and dietetics & Food sciences courses']['number_of_courses'], 12)
        self.assertEqual(courses['Other combinations with Food sciences']['number_of_courses'], 3)
        self.assertEqual(courses['Other combinations']['number_of_courses'], 1)

        self.assertEqual(list(courses.keys()), [
            'Agriculture & Business and management courses',
            'Ecology and environmental biology & Agricultural sciences courses',
            'Food and beverage production & Marketing courses',
            'Nutrition and dietetics & Food and beverage production courses',
            'Nutrition and dietetics & Food sciences courses',
            'Other combinations with Food sciences',
            'Other combinations',
            ]
        )        


    def test_when_history_course_queried(self):
        # ARRANGE
        mappings = self.load_mappings()
        mapper = CourseToLabelMapper(mappings)
        courseBySubject = CoursesBySubject(mapper)

        courses = self.load_fixture('input_history.json')

        counts = {'institutions': 131, 'courses': 716}
        limit = 5000
        offset = 0
        language = 'en'

        # ACT
        actual = courseBySubject.group(courses,
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
        self.assertEqual(courses['History courses']['number_of_courses'], 325)
        self.assertEqual(courses['History of art, architecture and design courses']['number_of_courses'], 91)
        self.assertEqual(courses['Courses in other subjects']['number_of_courses'], 61)
        self.assertEqual(list(courses.keys()), [
            'History courses',
            'History of art, architecture and design courses',
            'Courses in other subjects',
            ]
        )

        # multiple_subject_courses
        courses = items['multiple_subject_courses']
        self.assertEqual(courses['Economics & History courses']['number_of_courses'], 38)
        self.assertEqual(courses['English studies & History courses']['number_of_courses'], 62)
        self.assertEqual(courses['French studies & History courses']['number_of_courses'], 35)
        self.assertEqual(courses['German and Scandinavian studies & History courses']['number_of_courses'], 27)
        self.assertEqual(courses['History & Archaeology courses']['number_of_courses'], 63)
        self.assertEqual(courses['History & Classics courses']['number_of_courses'], 28)
        self.assertEqual(courses['History & Combined, general or negotiated studies courses']['number_of_courses'], 24)
        self.assertEqual(courses['History & Education courses']['number_of_courses'], 24)
        self.assertEqual(courses['History & History of art, architecture and design courses']['number_of_courses'], 26)
        self.assertEqual(courses['History & Media studies courses']['number_of_courses'], 30)
        self.assertEqual(courses['History & Philosophy courses']['number_of_courses'], 57)
        self.assertEqual(courses['History & Theology and religious studies courses']['number_of_courses'], 27)
        self.assertEqual(courses['Iberian studies & History courses']['number_of_courses'], 39)
        self.assertEqual(courses['Italian studies & History courses']['number_of_courses'], 21)
        self.assertEqual(courses['Languages and area studies & History courses']['number_of_courses'], 20)
        self.assertEqual(courses['Literature in English & History courses']['number_of_courses'], 56)
        self.assertEqual(courses['Politics & History courses']['number_of_courses'], 163)
        self.assertEqual(courses['Slavic studies & History courses']['number_of_courses'], 23)
        self.assertEqual(courses['Sociology & History courses']['number_of_courses'], 44)
        self.assertEqual(courses['Other combinations with History']['number_of_courses'], 338)
        self.assertEqual(courses['Other combinations']['number_of_courses'], 228)

        self.assertEqual(list(courses.keys()), [
            'Economics & History courses',
            'English studies & History courses',
            'French studies & History courses',
            'German and Scandinavian studies & History courses',
            'History & Archaeology courses',
            'History & Classics courses',
            'History & Combined, general or negotiated studies courses',
            'History & Education courses',
            'History & History of art, architecture and design courses',
            'History & Media studies courses',
            'History & Philosophy courses',
            'History & Theology and religious studies courses',
            'Iberian studies & History courses',
            'Italian studies & History courses',
            'Languages and area studies & History courses',
            'Literature in English & History courses',
            'Politics & History courses',
            'Slavic studies & History courses',
            'Sociology & History courses',
            'Other combinations with History',
            'Other combinations',
            ]
        )        


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
