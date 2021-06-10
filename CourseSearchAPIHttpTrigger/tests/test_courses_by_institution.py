import inspect
import json
import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

from courses_by_institution import CoursesByInstitution

TEST_DATA_DIR=f'{CURRENT_DIR}/fixtures/courses_by_institution'

class TestCoursesByInstitution(unittest.TestCase):
    
    def test_existing_logic(self):
        # ARRANGE
        with open(f'{TEST_DATA_DIR}/input.json', 'r') as myfile:
            input=myfile.read()
        courses = json.loads(input)
        
        with open(f'{TEST_DATA_DIR}/output.json', 'r') as myfile:
            output=myfile.read()
        expected = json.loads(output)

        counts = {'institutions': 442, 'courses': 35169}
        limit = "20" 
        offset = "0"
        language = "en"

        coursesByInstitution = CoursesByInstitution()

        # ACT
        actual = coursesByInstitution.group(courses,
                                            counts, 
                                            int(limit),
                                            int(offset), 
                                            language)        

        # ASSERT
        self.assertEqual(actual, expected)

