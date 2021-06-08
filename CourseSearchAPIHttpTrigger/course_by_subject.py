import logging

from course_to_label_mapper import CourseToLabelMapper
from helper import group_courses_by_institution


class CourseBySubject:
    def __init__(self, mapper):
        self.mapper = mapper

    def group(self, courses, counts, limit, offset, language):
        logging.info('sort')

        # TODO THIS IS WHERE ALL THE WORK IS DONE
        subject = 'CAH11-01-01'

        assert self.mapper.get_label(subject) == 'Computer science'
        assert self.mapper.get_label_welsh(
            subject) == 'Gwyddoniaeth gyfrifiadurol'

        logging.warning(self.mapper.get_labels(subject))

        return group_courses_by_institution(courses, counts, int(limit), int(offset), language)

        return 'TO BE IMPLEMENTED'
