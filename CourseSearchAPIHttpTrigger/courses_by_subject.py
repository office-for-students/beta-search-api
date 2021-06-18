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
            # logging.warning(f'{course["institution"]["pub_ukprn"]}\t{course["kis_course_id"]}\t{course["mode"]["code"]}\t{len(course["subjects"])}\t{course["title"]["english"]}\t\t\t{course["subjects"][0]["english"]}')
            if len(course["subjects"]) == 1:
                groupA[course["kis_course_id"]] = course
 
            if len(course["subjects"]) > 1:
                groupB[course["kis_course_id"]] = course


            ###################################################################
            # STEP 4
            # Identify most common single subjects in Group A (where the number
            # of courses with this subject >1% of the total number of results). 
            # 
            # Each of these subject groups is given an accordion with the subject 
            # label and the number of courses and sorted in descending order by 
            # number of courses. 
            # 
            # Remaining courses in Group A are grouped together 
            # under a “Courses in other subjects” accordion
            ###################################################################

            # group all courses by their subject label
            for course in groupA.values():
                label = course["subjects"][0]["english"]
                if label not in accordionsGroupA:
                    accordionsGroupA[label]=[]

                if course not in accordionsGroupA[label]:
                    accordionsGroupA[label].append(course)
                    
        logging.warning(accordionsGroupA.keys())

        # group courses that are <= 1% of total number of courses
        for key in list(accordionsGroupA.keys()):
            label = 'Courses in other subjects'

            percentage = len(accordionsGroupA[key]) / len(courses) * 100
            logging.warning(f'{key}: {len(accordionsGroupA[key])} ({round(percentage,1)}%)')

            if key == label:
                continue
            
            # move to other group
            if percentage <= 1:
                if label not in accordionsGroupA:
                    accordionsGroupA[label]=[]

                for c in list(accordionsGroupA[key]):
                    if c not in accordionsGroupA[label]:
                        accordionsGroupA[label].append(c)
                accordionsGroupA.pop(key)


        logging.warning('---------------------------------------')
        for key in accordionsGroupA.keys():
            percentage = len(accordionsGroupA[key]) / len(courses) * 100
            logging.warning(f'{key}: {len(accordionsGroupA[key])} ({round(percentage,1)}%)')

        return accordionsGroupA


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
