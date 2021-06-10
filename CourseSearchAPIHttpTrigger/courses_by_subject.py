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


    def group(self, courses, counts, limit, offset, language):

        groupA = {} # single subject courses (courses with  1 subject label)
        groupB = {} # subject combinations   (courses with >1 subject label)
        accordionsGroupA = {}

        # ADD EACH COURSE TO LIST OF INSTITUTION COURSES
        institutions = {}
        institution_count = 0

        for c in courses:
            course = c["course"]

            if course["institution"]["pub_ukprn_name"] == "not available":
                continue

            ################################################################
            # STEP 1 - map subject to label
            ################################################################

            ################################################################
            # STEP 3 - sort results into two categories (groups)
            ################################################################
            # logging.warning(f'{course["institution"]["pub_ukprn"]}\t{course["kis_course_id"]}\t{course["mode"]["code"]}\t{len(course["subjects"])}\t{course["title"]["english"]}\t\t\t{course["subjects"][0]["english"]}')
            if len(course["subjects"]) == 1:
                groupA[course["kis_course_id"]] = course
 
            if len(course["subjects"]) > 1:
                groupB[course["kis_course_id"]] = course


            ################################################################
            # STEP 4
            ################################################################
            cont=0
            # for cont in range(10):
            #     logging.warning(f'cont={cont}')

            # logging.warning('STARTING CONT LOOP')
            for course in groupA.values():
                subject_title = course["subjects"][0]["english"]
                if subject_title not in accordionsGroupA:
                    accordionsGroupA[subject_title]=[]

                # if subject_title == 'Tourism, transport and travel':
                #     logging.warning(f'adding {course}')
                #     logging.warning(f'going to add {course["kis_course_id"]} to {subject_title}')

                
                if course not in accordionsGroupA[subject_title]:
                    accordionsGroupA[subject_title].append(course)
            continue
        
        # logging.warning(f'{title} - {item}')
        
        logging.warning(f'len(groupA)={len(groupA)}')
        logging.warning(f'len(groupB)={len(groupB)}')
        logging.warning(f'      total={len(groupA) + len(groupB)}')

        logging.warning(len(accordionsGroupA.keys()))
        logging.warning(accordionsGroupA.keys())

        # logging.warning(accordionsGroupA['Economics'])

        for key in accordionsGroupA.keys():
            # logging.warning(key)
            logging.warning(f'{key}: {len(accordionsGroupA[key])}')

        logging.warning(len(accordionsGroupA['Tourism, transport and travel']))

        assert 250 == len(accordionsGroupA['Marketing'])
        assert 37 == len(accordionsGroupA['Business studies'])
        assert 24 == len(accordionsGroupA['Design studies'])
        assert 19 == len(accordionsGroupA['Management studies'])
        assert 9 == len(accordionsGroupA['Tourism, transport and travel'])

        # assert len(accordionsGroupA['Marketing']) == 250
        # logging.warning(len(groupA.get("K00054")["subjects"]))
        # logging.warning(len(groupB.get("43395")["subjects"]))
        
        # logging.warning(len(accordionsGroupA))
        # logging.warning(len(accordionsGroupA['Marketing']))
        # logging.warning(accordionsGroupA.keys())
        # logging.warning(len(accordionsGroupA.keys()))
        # logging.warning(accordionsGroupA['Marketing'])
        # logging.warning(len(accordionsGroupA['Marketing']))




        logging.warning(len(courses))
        return "HELLO"


# def logging.warning(string):
#     logging.warning(string)




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
