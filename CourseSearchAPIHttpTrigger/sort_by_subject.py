import json
import os
import sys
import inspect
import re
import logging

# CURRENTDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
class SortBySubject:
    def __init__(self, json_array):
        self.dict = self.convert_to_dictionary(json_array)

    def convert_to_dictionary(self, json_array):
        dict = {}
        for item in json_array:
            key = item['code']
            value = {
                'english_name': item['english_name'],
                'welsh_name': item['welsh_name'],
            }
            dict[key] = value
        return dict

    def get_labels(self, subject):
        return self.dict.get(subject)

    def get_label(self, subject):
        return self.dict[subject]['english_name']

    def get_label_welsh(self, subject):
        return self.dict[subject]['welsh_name']


    def sort(self, courses, counts, limit, offset, language):
        # with open(f'{CURRENTDIR}/fixtures/subjects-sort-by.json', 'r') as myfile:
        #     input = myfile.read()
        # course_to_label_mapping = json.loads(input)

        # sortBySubject = SortBySubject(course_to_label_mapping)
        subject = 'CAH11-01-01'

        # assert sortBySubject.get_label(subject) == 'Computer science'
        # assert sortBySubject.get_label_welsh(
        #     subject) == 'Gwyddoniaeth gyfrifiadurol'

        assert self.get_label(subject) == 'Computer science'
        assert self.get_label_welsh(subject) == 'Gwyddoniaeth gyfrifiadurol'

        print(self.get_labels(subject))

        return 'TO BE IMPLEMENTED'

