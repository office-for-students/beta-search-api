import logging
from helper import is_welsh

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
class CoursesBySubject:
    def __init__(self, mapper, language):
        self.mapper = mapper
        self.language = language


    def group(self, courses, limit, offset):
        logging.debug('group')
        single_course_accordions = {}
        multiple_course_accordions = {}
        institutions = []

        self.add_courses_to_accordions(
            courses, 
            single_course_accordions, 
            multiple_course_accordions,  
            institutions,           
        )                    
        
        # single courses
        single_course_accordions = self.sort_by_count(single_course_accordions)  
        most_common_subject_code = get_first_accordion_subject_code(single_course_accordions)
        most_common_subject_label = self.mapper.get_label(most_common_subject_code)
        combine_most_common_subjects(self.mapper, most_common_subject_code, most_common_subject_label, single_course_accordions)
        self.group_single_courses_that_are_less_than_one_percent(
            courses, 
            single_course_accordions,
        )        
        self.replace_codes_with_labels(most_common_subject_label, single_course_accordions)
        single_course_accordions = self.sort_by_count(single_course_accordions) 
                
        # multiple courses
        self.group_multiple_courses_that_are_less_than_one_percent(
            courses, 
            multiple_course_accordions, 
            most_common_subject_code,
        )
        self.replace_codes_with_labels(most_common_subject_label, multiple_course_accordions)
        multiple_course_accordions = sort_alphabetically(multiple_course_accordions)
        self.sort_other_combinations(most_common_subject_label, multiple_course_accordions)

        self.sort_contents(single_course_accordions)          
        self.sort_contents(multiple_course_accordions)   

        add_number_of_courses(single_course_accordions)
        add_number_of_courses(multiple_course_accordions)
        
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


    def add_courses_to_accordions(self, courses, single_course_accordions, multiple_course_accordions, institutions):
        logging.debug('add_courses_to_accordions')
        single_courses = {}
        multiple_courses = {}
        
        for c in courses:
            institution = c[key_course][key_institution]
            if institution[key_pub_ukprn_name] == "not available":
                continue

            add_institution_to_list(institution, institutions)

            course = build_course(c[key_course], institution, self.language)

            sort_results_into_groups(
                course, 
                single_courses, 
                multiple_courses,
            )

            add_single_courses_to_accordions(
                single_courses, 
                single_course_accordions, 
            )

            add_multiple_courses_to_accordions(
                multiple_courses, 
                multiple_course_accordions, 
            )
            

    def sort_contents(self, accordion):
        logging.debug('sort_contents')
        self.sort_contents_alphabetically_by_subject(accordion)
        self.sort_contents_alphabetically_by_institution(accordion)


    def sort_contents_alphabetically_by_subject(self, accordion):
        logging.debug('sort_contents_alphabetically_by_subject')
        for key in list(accordion.keys()):
            accordion[key][key_courses] = sorted(accordion[key][key_courses], key=lambda k: self.get_translation(k[key_title])) 


    def sort_contents_alphabetically_by_institution(self, accordion):
        logging.debug('sort_contents_alphabetically_by_institution')
        for key in list(accordion.keys()):
            courses = {}
            for course in accordion[key][key_courses]:
                title = self.get_translation(course[key_title])
                group_courses(key, course, title, courses)

            accordion[key][key_courses] = []
            for k, v in courses.items():
                for k2, v2 in v.items():
                    v2 = sorted(v2, key=lambda k3: k3[key_institution][key_pub_ukprn_name]) 
                    accordion[key][key_courses].extend(v2)


    def get_translation(self, json):
        logging.debug(f'get_translation({self.language})')
        language_name = 'welsh' if is_welsh(self.language) else 'english'

        if not json[language_name]:
            logging.warning(f'missing translation: {json}')
            return json['english']        
        return json[language_name]


    def replace_codes_with_labels(self, most_common_subject_label, accordions):
        logging.debug('replace_codes_with_labels')
        key_other_combinations_with = get_key_other_combinations_with(self.language)
        for codes in list(accordions):
            if codes.startswith(key_other_combinations_with):
                #TODO needs translating
                accordions[f'{key_other_combinations_with} {most_common_subject_label}'] = accordions.pop(codes)
                continue
            labels = []
            for code in codes.split():
                if code.startswith('CAH'):
                    labels.append(self.mapper.get_label(code))
            label = wrap_with_course(labels, self.language)
            
            if codes.startswith('CAH'):
                accordions[label] = accordions.pop(codes)


    def group_multiple_courses_that_are_less_than_one_percent(self, courses, accordions, most_common_subject_code):
        logging.debug('group_multiple_courses_that_are_less_than_one_percent')
        key_other_combinations_with = get_key_other_combinations_with(self.language)
        for key in list(accordions.keys()): 
            if most_common_subject_code == key:
                continue  

            percentage = len(accordions[key][key_courses]) / len(courses) * 100

            if percentage <= 1:
                if most_common_subject_code in key.split(): 
                    label = f'{key_other_combinations_with} {most_common_subject_code}'
                    move_course(accordions, key, label)
                else:
                    label = get_key_other_combinations(self.language)
                    move_course(accordions, key, label)


    def sort_other_combinations(self, most_common_subject_label, accordions):
        logging.debug('sort_other_combinations')
        key_other_combinations_with = get_key_other_combinations_with(self.language)
        key = f'{key_other_combinations_with} {most_common_subject_label}'
        if accordions.get(key):
            other_combinations_with = accordions[key]
            accordions.pop(key)
            accordions[key] = other_combinations_with    

        key_other_combinations = get_key_other_combinations(self.language)
        if accordions.get(key_other_combinations):
            other_combinations = accordions[key_other_combinations]
            accordions.pop(key_other_combinations)
            accordions[key_other_combinations] = other_combinations    


    def sort_by_count(self, accordion):
        logging.debug('sort_by_count')
        keys = accordion.keys()
        sorted_keys = sorted(keys, key=lambda key: len(accordion[key][key_courses]), reverse=True)
        [accordion[key] for key in sorted_keys]
        sorted_accordion = {}
        for key in sorted_keys:
            sorted_accordion[key] = accordion[key]
        key_courses_in_other_subjects = get_key_courses_in_other_subjects(self.language)
        if key_courses_in_other_subjects in sorted_accordion:
            sorted_accordion[key_courses_in_other_subjects] = sorted_accordion.pop(key_courses_in_other_subjects)
        return sorted_accordion


    def group_single_courses_that_are_less_than_one_percent(self, courses, accordions):
        logging.debug('group_single_courses_that_are_less_than_one_percent')
        key_courses_in_other_subjects = get_key_courses_in_other_subjects(self.language)
        for key in list(accordions.keys()):
            label = key_courses_in_other_subjects
            if label == key:
                continue            

            percentage = len(accordions[key][key_courses]) / len(courses) * 100

            if percentage <= 1:
                move_course(accordions, key, label)


def get_key_courses_in_other_subjects(language):
    return key_courses_in_other_subjects[get_language_name(language)]


def get_key_other_combinations(language):
    return key_other_combinations[get_language_name(language)]


def get_key_other_combinations_with(language):
    return key_other_combinations_with[get_language_name(language)]


def get_language_name(language):
    return 'welsh' if is_welsh(language) else 'english'


def wrap_with_course(labels, language):
    return f'Cyrsiau {" & ".join(labels)}' if is_welsh(language) else f'{" & ".join(labels)} courses'


def build_course(course, institution, language):
    logging.debug('build_course')
    institution_body = {
        key_pub_ukprn_name: institution[key_pub_ukprn_welsh_name] if is_welsh(language) else institution[key_pub_ukprn_name],
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


def add_institution_to_list(institution, institutions):
    logging.debug('add_institution_to_list')
    pub_ukprn = institution[key_pub_ukprn]
    if pub_ukprn not in institutions:
        institutions.append(pub_ukprn)


def sort_results_into_groups(course, single_courses, multiple_courses):
    logging.debug('sort_results_into_groups')
    if len(course[key_subjects]) == 1:
        single_courses[course[key_kis_course_id]] = course
    if len(course[key_subjects]) > 1:
        multiple_courses[course[key_kis_course_id]] = course


def add_single_courses_to_accordions(courses, accordions):
    logging.debug('add_single_courses_to_accordions')
    for course in courses.values():
        label = course[key_subjects][0][key_code]
        add_course_to_accordions(course, label, accordions)


def add_course_to_accordions(course, label, accordions):
    if label not in accordions:
        accordions[label] = {}
        accordions[label][key_courses] = []  
    if course not in accordions[label][key_courses]:
        accordions[label][key_courses].append(course)


def add_multiple_courses_to_accordions(courses, accordions):
    logging.debug('add_multiple_courses_to_accordions')
    for course in courses.values():
        subject_codes = []
        for subject in course[key_subjects]:            
            subject_codes.append(subject[key_code])
        label = f'{" ".join(subject_codes)}'
        add_course_to_accordions(course, label, accordions)


def move_course(accordions, key, label):
    if label not in accordions:
        accordions[label] = {}
        accordions[label][key_courses] = []
    for c in accordions[key][key_courses]:
        if c not in accordions[label][key_courses]:
            accordions[label][key_courses].append(c)
    accordions.pop(key)


def group_courses(key, course, title, accordions):
    logging.debug('group_courses')
    if not accordions.get(key):
        accordions[key] = {}
    if not accordions[key].get(title):
        accordions[key][title] = []
    accordions[key][title].append(course)


def sort_alphabetically(accordions):
    logging.debug('sort_alphabetically')
    return dict(sorted(accordions.items()))


def get_first_accordion_subject_code(accordions):
    logging.debug('get_first_accordion_subject_code')
    key = next(iter(accordions))
    return accordions.get(key)[key_courses][0][key_subjects][0][key_code]


def combine_most_common_subjects(mapper, most_common_subject_code, most_common_subject_label, accordions):
    for key in list(accordions.keys()):
        if key != most_common_subject_code:
            if mapper.get_label(key) == most_common_subject_label:
                accordions[most_common_subject_code][key_courses].extend(accordions[key][key_courses])
                accordions.pop(key)
                break


def add_number_of_courses(accordions):
    logging.debug('add_number_of_courses')
    for key in accordions.keys():
        accordions[key][key_number_of_courses] = len(accordions.get(key)[key_courses])


def log_accordions(accordions, courses):
    logging.info('---------------------------------------')
    for key in accordions.keys():
        percentage = len(accordions[key][key_courses]) / len(courses) * 100
        logging.info(f'{key}: {len(accordions[key][key_courses])} ({round(percentage,1)}%)')


key_code = 'code'
key_course = 'course'
key_courses = 'courses'
key_courses_in_other_subjects = {'english': 'Courses in other subjects', 'welsh': 'Cyrsiau mewn pynciau eraill'}
key_institution = 'institution'
key_institutions = 'institutions'
key_kis_course_id = 'kis_course_id'
key_locations = 'locations'
key_name = 'name'
key_number_of_courses = 'number_of_courses'
key_other_combinations = {'english': 'Other combinations', 'welsh': 'Cyfuniadau arall'}
key_other_combinations_with = {'english': 'Other combinations with', 'welsh': 'Cyfuniadau eraill gyda'}
key_pub_ukprn = 'pub_ukprn'
key_pub_ukprn_name = 'pub_ukprn_name'
key_pub_ukprn_welsh_name = 'pub_ukprn_welsh_name'
key_subjects = 'subjects'
key_title = 'title'
