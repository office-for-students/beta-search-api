import json
import os
import inspect

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


class CourseToLabelMapper:

    def __init__(self, json_array, language):
        self.dict = self.convert_to_dictionary(json_array)
        self.language = language

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

    def get_label(self, subject):
        if self.dict.get(subject):
            return self.dict[subject]['welsh_name'] if self.language == 'cy' else self.dict[subject]['english_name']
        else:
            return None

