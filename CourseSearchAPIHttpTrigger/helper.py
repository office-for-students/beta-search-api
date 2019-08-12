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
