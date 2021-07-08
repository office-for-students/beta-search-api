import json
import os
import sys
import inspect
import re
import logging

# TODO investigate setting PATH in Azure so can remove this
CURRENTDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENTDIR = os.path.dirname(CURRENTDIR)
sys.path.insert(0, CURRENTDIR)
sys.path.insert(0, PARENTDIR)

# from sort_by_subject import SortBySubject

def get_offset_and_limit(facets, requested_limit, requested_offset):
    limit = 0
    offset = 0
    total_courses = 0
    total_institutions = 0

    lower_range = requested_offset
    upper_range = requested_limit + requested_offset

    institution_course_counts = {}
    for facet in facets:
        if total_institutions < lower_range:
            offset += facet["count"]
        elif lower_range <= total_institutions < upper_range:
            limit += facet["count"]

        institution_course_counts[facet["value"]] = facet["count"]
        total_institutions += 1
        total_courses += facet["count"]

    return limit, offset, total_institutions, total_courses, institution_course_counts


def remove_conjunctions_from_searchable_fields(course, institution):
    if course != "":
        course = remove_conjunctions(course)

    if institution != "":
        institution = remove_conjunctions(institution)

    return course, institution


def remove_conjunctions(searchable_field):
    conjunctions = {"&", "and", "for", "in", "the", "with", "studies"}

    string_parts = searchable_field.split(" ")

    list_of_string_parts = []
    for string_part in string_parts:
        if string_part.lower() not in conjunctions:
            list_of_string_parts.append(string_part)

    return " ".join(list_of_string_parts)


def handle_apostrophes_in_search(field):
    return field.replace("'", "''")


def handle_search_terms(course, institution):
    return (
        remove_unwanted_chars_in_search_term(course),
        remove_unwanted_chars_in_search_term(institution),
    )


def remove_unwanted_chars_in_search_term(field):

    return re.sub("[^0-9A-Za-z'\\s]+", "", field)


def course_sort_key(course, language):
    if not course["title"]:
        return "course title is missing"
    elif not course["title"]["english"]:
        return "course title is missing"
    elif language == "cy":
        return (course["title"]["welsh"] if course["title"]["welsh"] else course["title"]["english"]) + course["qualification"] + (" Hons" if course["honours_award"] == 1 else "") 
    else:
        return (course["title"]["english"] if course["title"]["english"] else course["title"]["welsh"]) + course["qualification"] + (" Hons" if course["honours_award"] == 1 else "") 


def is_welsh(language):
    return language == 'cy'