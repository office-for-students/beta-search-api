import inspect
import json
import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

# from helper import group_courses_by_subject
from sort_by_subject import SortBySubject

TEST_DATA_DIR=f'{CURRENT_DIR}/fixtures/group_courses_by_subject'

class TestGroupCoursesBySubject(unittest.TestCase):
    
    def test_existing_logic(self):
        with open(f'{CURRENT_DIR}/../fixtures/subjects-sort-by.json', 'r') as myfile:
            mapping=myfile.read()
        course_to_label_mapping = json.loads(mapping)

        # ARRANGE
        with open(f'{TEST_DATA_DIR}/input.json', 'r') as myfile:
            input=myfile.read()
        courses = json.loads(input)

        with open(f'{TEST_DATA_DIR}/input.json', 'r') as myfile:
            input=myfile.read()
        courses = json.loads(input)
        
        with open(f'{TEST_DATA_DIR}/output.json', 'r') as myfile:
            output=myfile.read()
        expected = json.loads(output)

        counts = {'institutions': 432, 'courses': 29167}
        limit = "20" 
        offset = "0"
        language = "en"

        # ACT
        actual = SortBySubject(course_to_label_mapping).sort(
            courses, 
            counts, 
            int(limit), 
            int(offset), 
            language
        )

        # ASSERT
        self.assertEqual(actual, expected)

