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


def group_courses_by_institution(courses, counts, limit, offset, language):

    institutions = {}
    institution_count = 0
    for c in courses:
        course = c["course"]

        if course["institution"]["pub_ukprn_name"] == "not available":
            continue

        pub_ukprn = course["institution"]["pub_ukprn"]
        if pub_ukprn not in institutions:
            institution_body = {
                "pub_ukprn_name": course["institution"]["pub_ukprn_welsh_name"] if language == "cy" else course["institution"]["pub_ukprn_name"],
                "pub_ukprn": pub_ukprn,
                "courses": [],
                "number_of_courses": 0,
            }
            institutions[pub_ukprn] = institution_body
            institution_count += 1

        locations = []
        for location in course["locations"]:
            locations.append(location["name"])

        new_course = {
            "country": course["country"]["label"],
            "distance_learning": course["distance_learning"]["label"],
            "foundation_year": course["foundation_year_availability"]["label"],
            "honours_award": course["honours_award_provision"],
            "kis_course_id": course["kis_course_id"],
            "length_of_course": course["length_of_course"]["label"],
            "locations": locations,
            "mode": course["mode"]["label"],
            "qualification": course["qualification"]["label"],
            "sandwich_year": course["sandwich_year"]["label"],
            "subjects": course["subjects"],
            "title": course["title"],
            "year_abroad": course["year_abroad"]["label"],
        }

        institution = institutions.get(pub_ukprn)
        institution["courses"].append(new_course)
        institution["number_of_courses"] += 1

    items = []
    for item in institutions:
        institution = institutions.get(item)
        institution["courses"].sort(key=lambda x: course_sort_key(x, language))
        items.append(institution)

    results = {
        "items": items,
        "limit": limit,
        "number_of_items": len(institutions),
        "offset": offset,
        "total_number_of_courses": counts["courses"],
        "total_results": counts["institutions"],
    }

    return results


def group_courses_by_subject(courses, counts, limit, offset, language):
    return 'TO BE IMPLEMENTED'


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