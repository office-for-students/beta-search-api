from helper import course_sort_key

class CoursesByInstitution():
    def group(self, courses, counts, limit, offset, language):

        # ADD EACH COURSE TO LIST OF INSTITUTION COURSES
        institutions = {}
        institution_count = 0
        for c in courses:
            course = c["course"]

            if course["institution"]["pub_ukprn_name"] == "not available":
                continue

            # CREATE INSTITUTION IF NOT ALREADY IN LIST OF INSTITUTIONS
            pub_ukprn = course["institution"]["pub_ukprn"]
            if pub_ukprn not in institutions:
                institution = course["institution"]
                institution_body = {
                    "pub_ukprn_name": institution["pub_ukprn_welsh_name"] if language == "cy" else institution["pub_ukprn_name"],
                    "pub_ukprn": pub_ukprn,
                    "courses": [],
                    "number_of_courses": 0,
                }
                institutions[pub_ukprn] = institution_body
                institution_count += 1

            # ADD EACH COURSE LOCATION TO LIST OF LOCATIONS
            locations = []
            for location in course["locations"]:
                locations.append(location["name"])

            # CREATE COURSE AND ADD TO LIST OF INSTITUTION COURSES
            new_course = {
                "country":           course["country"]["label"],
                "distance_learning": course["distance_learning"]["label"],
                "foundation_year":   course["foundation_year_availability"]["label"],
                "honours_award":     course["honours_award_provision"],
                "kis_course_id":     course["kis_course_id"],
                "length_of_course":  course["length_of_course"]["label"],
                "mode":              course["mode"]["label"],
                "qualification":     course["qualification"]["label"],
                "sandwich_year":     course["sandwich_year"]["label"],
                "subjects":          course["subjects"],
                "title":             course["title"],
                "year_abroad":       course["year_abroad"]["label"],
                "locations":         locations,
            }
            institution = institutions.get(pub_ukprn)
            institution["courses"].append(new_course)
            institution["number_of_courses"] += 1

        # SORT COURSES BASED ON LANGUAGE
        items = []
        for item in institutions:
            institution = institutions.get(item)
            institution["courses"].sort(key=lambda x: course_sort_key(x, language))
            items.append(institution)

        # CREATE DICTIONARY AND RETURN
        results = {
            "items": items,
            "limit": limit,
            "number_of_items": len(institutions),
            "offset": offset,
            "total_number_of_courses": counts["courses"],
            "total_results": counts["institutions"],
        }
        return results
