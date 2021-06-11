import logging

from courses_by_institution import CoursesByInstitution
from helper import course_sort_key


class CoursesBySubject:
    def __init__(self, mapper):
        self.mapper = mapper

    # def group(self, courses, counts, limit, offset, language):
    #     logging.info('sort')

    #     # TODO THIS IS WHERE ALL THE WORK IS DONE
    #     subject = 'CAH11-01-01'

    #     assert self.mapper.get_label(subject) == 'Computer science'
    #     assert self.mapper.get_label_welsh(
    #         subject) == 'Gwyddoniaeth gyfrifiadurol'

    #     logging.warning(self.mapper.get_labels(subject))

    #     return self.group(courses, counts, int(limit), int(offset), language)

    #     return 'TO BE IMPLEMENTED'


    def group(self, queried_course_title, courses ,counts, limit, offset, language):

        groupA = {} # single subject courses (courses with  1 subject label)
        groupB = {} # subject combinations   (courses with >1 subject label)
        accordionsGroupA = {}
        accordionsGroupB = {}

        # ADD EACH COURSE TO LIST OF INSTITUTION COURSES
        institutions = {}
        institution_count = 0

        for c in courses:
            course = c["course"]

            if course["institution"]["pub_ukprn_name"] == "not available":
                continue

            ###################################################################
            # STEP 2
            # SBJ nodes of results are mapped to subject labels. 
            # 
            # If a course has two SBJ values that map to the same label, it is 
            # given only one label.
            ###################################################################


            ###################################################################
            # STEP 3
            # Sort results into two categories:
            #   A – single subject courses (courses with 1 subject label)
            #   B – subject combinations (courses with >1 subject label)
            ###################################################################
            if len(course["subjects"]) == 1:
                groupA[course["kis_course_id"]] = course
 
            if len(course["subjects"]) > 1:
                groupB[course["kis_course_id"]] = course


            ###################################################################
            # STEP 4.1 Group single courses by subject label
            ###################################################################
            for course in groupA.values():
                label = f'{self.mapper.get_label(course["subjects"][0]["code"])} courses'
                if label not in accordionsGroupA:
                    accordionsGroupA[label]=[]

                if course not in accordionsGroupA[label]:
                    accordionsGroupA[label].append(course)

            ###################################################################
            # STEP 5 Group multiple courses by subject labels
            ###################################################################
            for course in groupB.values():
                subjects = []
                for subject in course["subjects"]:
                    subjects.append(self.mapper.get_label(subject["code"]))

                label = f'{" & ".join(subjects)} courses'

                if label not in accordionsGroupB:
                    accordionsGroupB[label]=[]

                if course not in accordionsGroupB[label]:
                    accordionsGroupB[label].append(course)

        # logging.warning(accordionsGroupA.keys())
        # logging.warning(accordionsGroupB.keys())

        ###################################################################
        # STEP 4.2 Move groups that are <= 1% of total courses to 'other' group
        ###################################################################
        for key in list(accordionsGroupA.keys()):
            label = 'Courses in other subjects'
            if label == key:
                continue            

            percentage = len(accordionsGroupA[key]) / len(courses) * 100
            # logging.warning(f'{key}: {len(accordionsGroupA[key])} ({round(percentage,1)}%)')

            # move to other group
            if percentage <= 1:
                if label not in accordionsGroupA:
                    accordionsGroupA[label]=[]

                for c in list(accordionsGroupA[key]):
                    if c not in accordionsGroupA[label]:
                        accordionsGroupA[label].append(c)
                accordionsGroupA.pop(key)

        ###################################################################
        # STEP 6 Move groups that are <= 1% of total courses to 'other' groups
        ###################################################################
        for key in list(accordionsGroupB.keys()):
            if label == key:
                continue            

            percentage = len(accordionsGroupB[key]) / len(courses) * 100
            # logging.warning(f'{key}: {len(accordionsGroupB[key])} ({round(percentage,1)}%)')

            # move to other groups
            if percentage <= 1:
                if queried_course_title in key: 
                    label = f'Other combinations with {queried_course_title}'
                    if label not in accordionsGroupB:
                        accordionsGroupB[label]=[]

                    for c in list(accordionsGroupB[key]):
                        if c not in accordionsGroupB[label]:
                            accordionsGroupB[label].append(c)
                    accordionsGroupB.pop(key)
                else:
                    label = f'Other combinations'
                    if label not in accordionsGroupB:
                        accordionsGroupB[label]=[]

                    for c in list(accordionsGroupB[key]):
                        if c not in accordionsGroupB[label]:
                            accordionsGroupB[label].append(c)
                    accordionsGroupB.pop(key)


        # self.log(accordionsGroupA, courses)
        self.log(accordionsGroupB, courses)

        # assert False
        return {'single_subject_courses': accordionsGroupA, 'multiple_subject_courses': accordionsGroupB}


    def log(self, accordionsGroup, courses):
        logging.warning('---------------------------------------')
        for key in accordionsGroup.keys():
            percentage = len(accordionsGroup[key]) / len(courses) * 100
            # logging.warning(f'{key}: {len(accordionsGroup[key])} ({round(percentage,1)}%)')
            # if key == 'Business and management & Marketing':
            # if key == 'Marketing & Design studies' or key == 'Marketing & Journalism':
            logging.warning(f'{key}: {len(accordionsGroup[key])} ({round(percentage,1)}%)')


        #     # CREATE INSTITUTION IF NOT ALREADY IN LIST OF INSTITUTIONS
        #     pub_ukprn = course["institution"]["pub_ukprn"]
        #     logging.warning(f'pub_ukprn={pub_ukprn}')
        #     if pub_ukprn not in institutions:
        #         institution = course["institution"]
        #         institution_body = {
        #             "pub_ukprn_name": institution["pub_ukprn_welsh_name"] if language == "cy" else institution["pub_ukprn_name"],
        #             "pub_ukprn": pub_ukprn,
        #             "courses": [],
        #             "number_of_courses": 0,
        #         }
        #         institutions[pub_ukprn] = institution_body
        #         institution_count += 1
        #         # logging.warning('******************************************************')
        #         # logging.warning(f'pub_ukprn={institutions[pub_ukprn]["pub_ukprn_name"]}')

        #     # ADD EACH COURSE LOCATION TO LIST OF LOCATIONS
        #     locations = []
        #     for location in course["locations"]:
        #         locations.append(location["name"])
        #         # logging.warning(f'location["name"]={location["name"]}')
        #         # logging.warning(f'location["name"]["english"]={location["name"]["english"]}')
        #     # logging.warning(f'locations={locations}')

        #     # CREATE COURSE AND ADD TO LIST OF INSTITUTION COURSES
        #     new_course = {
        #         "country":           course["country"]["label"],
        #         "distance_learning": course["distance_learning"]["label"],
        #         "foundation_year":   course["foundation_year_availability"]["label"],
        #         "honours_award":     course["honours_award_provision"],
        #         "kis_course_id":     course["kis_course_id"],
        #         "length_of_course":  course["length_of_course"]["label"],
        #         "mode":              course["mode"]["label"],
        #         "qualification":     course["qualification"]["label"],
        #         "sandwich_year":     course["sandwich_year"]["label"],
        #         "subjects":          course["subjects"],
        #         "title":             course["title"],
        #         "year_abroad":       course["year_abroad"]["label"],
        #         "locations":         locations,
        #     }
        #     institution = institutions.get(pub_ukprn)
        #     institution["courses"].append(new_course)
        #     institution["number_of_courses"] += 1

        #     # logging.warning(f'new_course["subjects"]={new_course["subjects"]}')
        #     # logging.warning('------------------------------------------------')
        #     # for subject in new_course["subjects"]:
        #     #     logging.warning(f'subject={subject["code"]} - {subject["english"]}')
        #     # logging.warning('------------------------------------------------')
                
        #     # if len(new_course["subjects"]) == 1:
        #     #     groupA[new_course["code"]] = new_course
        #     # logging.warning(f'len(groupA)={len(groupA)}')

        # # logging.warning(f'HELLO - 0015')

        # # SORT COURSES BASED ON LANGUAGE
        # items = []
        # for item in institutions:
        #     institution = institutions.get(item)
        #     institution["courses"].sort(key=lambda x: course_sort_key(x, language))
        #     items.append(institution)

        # # logging.warning(f'HELLO - 0020')

        # # CREATE DICTIONARY AND RETURN
        # results = {
        #     "items": items,
        #     "limit": limit,
        #     "number_of_items": len(institutions),
        #     "offset": offset,
        #     "total_number_of_courses": counts["courses"],
        #     "total_results": counts["institutions"],
        # }
        # # logging.warning(f'HELLO - 0030')
        # return results
