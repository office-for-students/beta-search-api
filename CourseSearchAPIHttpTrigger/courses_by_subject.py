import logging

class CoursesBySubject:
    def __init__(self, mapper):
        self.mapper = mapper


    def group(self, queried_course_title, courses ,counts, limit, offset, language):
        single_course_accordions = {}
        multiple_course_accordions = {}

        add_courses_to_accordions(courses, single_course_accordions, multiple_course_accordions, self.mapper, language)

        group_single_courses_that_are_less_than_one_percent(courses, single_course_accordions)

        multiple_course_accordions = sort(multiple_course_accordions)

        group_multiple_courses_that_are_less_than_one_percent(courses, multiple_course_accordions, queried_course_title)

        log_accordions(single_course_accordions, courses)
        log_accordions(multiple_course_accordions, courses)

        return {
            "items": {
                'single_subject_courses': single_course_accordions, 
                'multiple_subject_courses': multiple_course_accordions,
            },
            "limit": limit,
            "number_of_items": len(single_course_accordions) + len(multiple_course_accordions),
            "offset": offset,
            "total_number_of_courses": counts["courses"],
            "total_results": counts["institutions"],
        }


def add_courses_to_accordions(courses, single_course_accordions, multiple_course_accordions, mapper, language):
    single_course = {}
    multiple_course = {}
    institutions = []

    for c in courses:
        course = c["course"]
        institution = course["institution"]

        if institution["pub_ukprn_name"] == "not available":
            continue

        add_institution_to_list(institution, institutions)

        course = build_course(c["course"], institution, language)

        sort_results_into_groups(course, single_course, multiple_course)

        add_single_courses_to_accordions(course, single_course, single_course_accordions, mapper)

        add_multiple_courses_to_accordions(course, multiple_course, multiple_course_accordions, mapper)


def add_institution_to_list(institution, institutions):
    pub_ukprn = institution["pub_ukprn"]
    if pub_ukprn not in institutions:
        institutions.append(pub_ukprn)


def build_course(course, institution, language):
    institution_body = {
        "pub_ukprn_name": institution["pub_ukprn_welsh_name"] if language == "cy" else institution["pub_ukprn_name"],
        "pub_ukprn": institution["pub_ukprn"],
    }

    locations = []
    for location in course["locations"]:
        locations.append(location["name"])

    return {
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
        "institution":       institution_body,
    }


def sort_results_into_groups(course, group_a, group_b):
    if len(course["subjects"]) == 1:
        add_course_id_to_group(group_a, course)

    if len(course["subjects"]) > 1:
        add_course_id_to_group(group_b, course)


def add_course_id_to_group(group, course):
    group[course["kis_course_id"]] = course


def add_single_courses_to_accordions(course, group, accordions, mapper):
    for course in group.values():
        label = f'{mapper.get_label(course["subjects"][0]["code"])} courses'
        add_course_to_accordions(course, label, accordions)


def add_course_to_accordions(course, label, accordions):
    if label not in accordions:
        accordions[label] = []
    if course not in accordions[label]:
        accordions[label].append(course)


def add_multiple_courses_to_accordions(course, group, accordions, mapper):
    for course in group.values():
        subjects = []
        for subject in course["subjects"]:
            subjects.append(mapper.get_label(subject["code"]))
        label = f'{" & ".join(subjects)} courses'
        add_course_to_accordions(course, label, accordions)


def group_single_courses_that_are_less_than_one_percent(courses, accordions):
    for key in list(accordions.keys()):
        label = 'Courses in other subjects'
        if label == key:
            continue            

        percentage = len(accordions[key]) / len(courses) * 100

        if percentage <= 1:
            move_course(accordions, key, label)


def move_course(accordions, key, label):
    if label not in accordions:
        accordions[label] = []
    for c in list(accordions[key]):
        if c not in accordions[label]:
            accordions[label].append(c)
    accordions.pop(key)


def sort(accordion):
    return dict(sorted(accordion.items()))


def group_multiple_courses_that_are_less_than_one_percent(courses, accordions, queried_course_title):
    for key in list(accordions.keys()):
        
        if queried_course_title == key:
            continue  

        percentage = len(accordions[key]) / len(courses) * 100

        if percentage <= 1:
            if queried_course_title.lower() in key.lower(): 
                label = f'Other combinations with {queried_course_title.title()}'
                move_course(accordions, key, label)
            else:
                label = f'Other combinations'
                move_course(accordions, key, label)

        sort_other_combinations(accordions)


def sort_other_combinations(accordions):
    if accordions.get('Other combinations'):
        other_combinations = accordions['Other combinations']
        if other_combinations:
            accordions.pop('Other combinations')
            accordions['Other combinations'] = other_combinations    


def log_accordions(accordions, courses):
    logging.warning('---------------------------------------')
    for key in accordions.keys():
        percentage = len(accordions[key]) / len(courses) * 100
        logging.warning(f'{key}: {len(accordions[key])} ({round(percentage,1)}%)')
