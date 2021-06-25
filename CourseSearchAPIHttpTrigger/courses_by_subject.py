import logging

class CoursesBySubject:
    def __init__(self, mapper):
        self.mapper = mapper


    def group(self, courses, limit, offset, language):
        single_course_accordions = {}
        multiple_course_accordions = {}
        institutions = []

        add_courses_to_accordions(
            self.mapper, 
            courses, 
            single_course_accordions, 
            multiple_course_accordions,  
            institutions,           
            language,
            )        
        
        group_single_courses_that_are_less_than_one_percent(
            courses, 
            single_course_accordions,
            )        
        
        single_course_accordions = sort_by_count(single_course_accordions)

        most_common_subject = get_most_common_subject_code(single_course_accordions)
        
        group_multiple_courses_that_are_less_than_one_percent(
            courses, 
            multiple_course_accordions, 
            most_common_subject,
            )

        add_number_of_courses(single_course_accordions)
        add_number_of_courses(multiple_course_accordions)
        
        #map codes to labels
        for codes in list(multiple_course_accordions):
            if codes.startswith(key_other_combinations_with):
                multiple_course_accordions[f'{key_other_combinations_with} {self.mapper.get_label(most_common_subject)}'] = multiple_course_accordions.pop(codes)
                continue

            labels = []
            for code in codes.split():
                if code.startswith('CAH'):
                    labels.append(self.mapper.get_label(code))
            label = f'{" & ".join(labels)} {key_courses}'
            if codes.startswith('CAH'):
                multiple_course_accordions[label] = multiple_course_accordions.pop(codes)


        multiple_course_accordions = sort_alphabetically(multiple_course_accordions)

        sort_other_combinations(multiple_course_accordions, most_common_subject, self.mapper)

        log_accordions(single_course_accordions, courses)
        log_accordions(multiple_course_accordions, courses)

        return {
            "items": {
                "single_subject_courses": single_course_accordions, 
                "multiple_subject_courses": multiple_course_accordions,
            },
            "limit": limit,
            "number_of_items": len(single_course_accordions) + len(multiple_course_accordions),
            "offset": offset,
            "total_number_of_courses": len(courses),
            "total_results": len(institutions),
        }


def add_courses_to_accordions(mapper, courses, single_course_accordions, multiple_course_accordions, institutions, language):
    single_courses = {}
    multiple_courses = {}
    
    for c in courses:
        institution = c[key_course][key_institution]
        if institution[key_pub_ukprn_name] == "not available":
            continue

        add_institution_to_list(institution, institutions)

        course = build_course(c[key_course], institution, language)

        sort_results_into_groups(
            course, 
            single_courses, 
            multiple_courses,
            )

        add_single_courses_to_accordions(
            course, 
            single_courses, 
            single_course_accordions, 
            mapper,
            )

        add_multiple_courses_to_accordions(
            course, 
            multiple_courses, 
            multiple_course_accordions, 
            mapper,
            )


def add_institution_to_list(institution, institutions):
    pub_ukprn = institution[key_pub_ukprn]
    if pub_ukprn not in institutions:
        institutions.append(pub_ukprn)

def build_course(course, institution, language):
    institution_body = {
        key_pub_ukprn_name: institution[key_pub_ukprn_welsh_name] if language == "cy" else institution[key_pub_ukprn_name],
        key_pub_ukprn: institution[key_pub_ukprn],
    }

    locations = []
    for location in course[key_locations]:
        locations.append(location[key_name])

    return {
        "country":           course["country"]["label"],
        "distance_learning": course["distance_learning"]["label"],
        "foundation_year":   course["foundation_year_availability"]["label"],
        "honours_award":     course["honours_award_provision"],
        "kis_course_id":     course[key_kis_course_id],
        "length_of_course":  course["length_of_course"]["label"],
        "mode":              course["mode"]["label"],
        "qualification":     course["qualification"]["label"],
        "sandwich_year":     course["sandwich_year"]["label"],
        "subjects":          course[key_subjects],
        "title":             course["title"],
        "year_abroad":       course["year_abroad"]["label"],
        key_locations:       locations,
        key_institution:     institution_body,
    }


def sort_results_into_groups(course, single_courses, multiple_courses):
    if len(course[key_subjects]) == 1:
        single_courses[course[key_kis_course_id]] = course
    if len(course[key_subjects]) > 1:
        multiple_courses[course[key_kis_course_id]] = course


def add_single_courses_to_accordions(course, courses, accordions, mapper):
    for course in courses.values():
        label = f'{mapper.get_label(course[key_subjects][0][key_code])} courses'
        add_course_to_accordions(course, label, accordions)


def add_course_to_accordions(course, label, accordions):
    if label not in accordions:
        accordions[label] = {}
        accordions[label][key_courses] = []  
    if course not in accordions[label][key_courses]:
        accordions[label][key_courses].append(course)


def add_multiple_courses_to_accordions(course, courses, accordions, mapper):
    for course in courses.values():
        subject_labels = []
        subject_codes = []
        for subject in course[key_subjects]:            
            subject_labels.append(mapper.get_label(subject[key_code]))
            subject_codes.append(subject[key_code])
        label = f'{" ".join(subject_codes)}'
        add_course_to_accordions(course, label, accordions)


def group_single_courses_that_are_less_than_one_percent(courses, accordions):
    for key in list(accordions.keys()):
        label = key_courses_in_other_subjects
        if label == key:
            continue            

        percentage = len(accordions[key][key_courses]) / len(courses) * 100

        if percentage <= 1:
            move_course(accordions, key, label)


def move_course(accordions, key, label):
    if label not in accordions:
        accordions[label] = {}
        accordions[label][key_courses] = []
    for c in accordions[key][key_courses]:
        if c not in accordions[label][key_courses]:
            accordions[label][key_courses].append(c)
    accordions.pop(key)


def sort_by_count(accordions):
    keys = accordions.keys()
    sorted_keys = sorted(keys, key=lambda key: len(accordions[key][key_courses]), reverse=True)
    [accordions[key] for key in sorted_keys]
    sorted_accordions = {}
    for key in sorted_keys:
        sorted_accordions[key] = accordions[key]
    if key_courses_in_other_subjects in sorted_accordions:
        sorted_accordions[key_courses_in_other_subjects] = sorted_accordions.pop(key_courses_in_other_subjects)
    return sorted_accordions


def sort_alphabetically(accordions):
    return dict(sorted(accordions.items()))


def get_most_common_subject_label(accordions):
    return next(iter(accordions)).replace(key_courses, '').strip()


def get_most_common_subject_code(accordions):
        first_accordion = next(iter(accordions))
        most_common_subject = first_accordion.replace(key_courses, '').strip()
        most_common_subject_accordion = accordions.get(first_accordion)
        code = most_common_subject_accordion[key_courses][0][key_subjects][0][key_code]
        return code


def group_multiple_courses_that_are_less_than_one_percent(courses, accordions, most_common_subject):
    for key in list(accordions.keys()): 
        if most_common_subject == key:
            continue  

        percentage = len(accordions[key][key_courses]) / len(courses) * 100

        if percentage <= 1:
            if most_common_subject in key.split(): 
                label = f'{key_other_combinations_with} {most_common_subject}'
                move_course(accordions, key, label)
            else:
                label = key_other_combinations
                move_course(accordions, key, label)


def sort_other_combinations(accordions, most_common_subject, mapper):
    key = f'{key_other_combinations_with} {mapper.get_label(most_common_subject)}'
    if accordions.get(key):
        other_combinations_with = accordions[key]
        accordions.pop(key)
        accordions[key] = other_combinations_with    

    if accordions.get(key_other_combinations):
        other_combinations = accordions[key_other_combinations]
        accordions.pop(key_other_combinations)
        accordions[key_other_combinations] = other_combinations    


def add_number_of_courses(accordions):
    for key in accordions.keys():
        accordions[key][key_number_of_courses] = len(accordions.get(key)[key_courses])


def log_accordions(accordions, courses):
    logging.warning('---------------------------------------')
    for key in accordions.keys():
        courses = accordions[key][key_courses]
        percentage = len(courses) / len(courses) * 100
        logging.warning(f'{key}: {len(courses)} ({round(percentage,1)}%)')


key_code = 'code'
key_course = 'course'
key_courses = 'courses'
key_courses_in_other_subjects = 'Courses in other subjects'
key_institution = 'institution'
key_institutions = 'institutions'
key_kis_course_id = 'kis_course_id'
key_locations = 'locations'
key_name = 'name'
key_number_of_courses = 'number_of_courses'
key_other_combinations = 'Other combinations'
key_other_combinations_with = 'Other combinations with'
key_pub_ukprn = 'pub_ukprn'
key_pub_ukprn_name = 'pub_ukprn_name'
key_pub_ukprn_welsh_name = 'pub_ukprn_welsh_name'
key_subjects = 'subjects'
