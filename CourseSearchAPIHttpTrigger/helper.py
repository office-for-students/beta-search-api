import os
import sys
import inspect

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

    for facet in facets:
        if total_institutions < lower_range:
            offset += facet["count"]
        elif lower_range <= total_institutions < upper_range:
            limit += facet["count"]

        total_institutions += 1
        total_courses += facet["count"]

    return limit, offset, total_institutions, total_courses


def group_courses_by_institution(search_results, counts, limit, offset):
    courses = search_results["value"]

    institutions = {}
    for c in courses:
        course = c["course"]

        pub_ukprn = course["institution"]["pub_ukprn"]
        if pub_ukprn not in institutions:
            institution_body = {
                "pub_ukprn_name": course["institution"]["pub_ukprn_name"],
                "pub_ukprn": pub_ukprn,
                "courses": [],
                "number_of_courses": 0,
            }
            institutions[pub_ukprn] = institution_body

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
        items.append(institutions.get(item))

    results = {
        "items": items,
        "limit": limit,
        "number_of_items": len(institutions),
        "offset": offset,
        "total_number_of_courses": counts["courses"],
        "total_results": counts["institutions"],
    }

    return results


def remove_conjunctions_from_searchable_fields(course, institution):
    if course != "":
        course = remove_conjunctions(course)

    if institution != "":
        institution = remove_conjunctions(institution)

    return course, institution


def remove_conjunctions(searchable_field):
    conjunctions = {"&", "and", "for", "in", "the", "with"}

    string_parts = searchable_field.split(" ")

    list_of_string_parts = []
    for string_part in string_parts:
        if string_part.lower() not in conjunctions:
            list_of_string_parts.append(string_part)

    return " ".join(list_of_string_parts)


def handle_apostrophes_in_search(field):
    return field.replace("'", "''",)
