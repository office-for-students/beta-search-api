import json
import os
import inspect

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


class CourseToLabelMapper:
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
