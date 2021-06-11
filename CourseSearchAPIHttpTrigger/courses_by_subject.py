import logging

class CoursesBySubject:
    def __init__(self, mapper):
        self.mapper = mapper

    def group(self, queried_course_title, courses ,counts, limit, offset, language):

        groupA = {} # single subject courses (courses with  1 subject label)
        groupB = {} # subject combinations   (courses with >1 subject label)
        accordionsGroupA = {}
        accordionsGroupB = {}
        institutions = []

        for c in courses:
            course = c["course"]
            institution = course["institution"]

            if institution["pub_ukprn_name"] == "not available":
                continue

            pub_ukprn = institution["pub_ukprn"]
            if pub_ukprn not in institutions:
                institutions.append(pub_ukprn)

            course = self.build_course(c["course"], institution, language)

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

        ###################################################################
        # STEP 4.2 Move groups that are <= 1% of total courses to 'other' group
        ###################################################################
        for key in list(accordionsGroupA.keys()):
            label = 'Courses in other subjects'
            if label == key:
                continue            

            percentage = len(accordionsGroupA[key]) / len(courses) * 100

            # move to other group
            if percentage <= 1:
                if label not in accordionsGroupA:
                    accordionsGroupA[label]=[]

                for c in list(accordionsGroupA[key]):
                    if c not in accordionsGroupA[label]:
                        accordionsGroupA[label].append(c)
                accordionsGroupA.pop(key)

        # sort alphabetically
        accordionsGroupB = dict(sorted(accordionsGroupB.items()))

        ###################################################################
        # STEP 6 Move groups that are <= 1% of total courses to 'other' groups
        ###################################################################
        for key in list(accordionsGroupB.keys()):
            if label == key:
                continue            

            percentage = len(accordionsGroupB[key]) / len(courses) * 100

            # move to other groups
            if percentage <= 1:
                if queried_course_title.lower() in key.lower(): 
                    label = f'Other combinations with {queried_course_title.title()}'
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

        # ensure that GroupB 'Other combinations' is at the end of the list
        other_combinations = accordionsGroupB['Other combinations']
        if other_combinations:
            accordionsGroupB.pop('Other combinations')
            accordionsGroupB['Other combinations'] = other_combinations

        # self.log(accordionsGroupA, courses)
        # self.log(accordionsGroupB, courses) 

        items = {'single_subject_courses': accordionsGroupA, 'multiple_subject_courses': accordionsGroupB}

        # CREATE DICTIONARY AND RETURN
        return {
            "items": items,
            "limit": limit,
            "number_of_items": len(accordionsGroupA) + len(accordionsGroupB),
            "offset": offset,
            "total_number_of_courses": counts["courses"],
            "total_results": counts["institutions"],
        }


    def log(self, accordionsGroup, courses):
        logging.warning('---------------------------------------')
        for key in accordionsGroup.keys():
            percentage = len(accordionsGroup[key]) / len(courses) * 100
            logging.warning(f'{key}: {len(accordionsGroup[key])} ({round(percentage,1)}%)')


    def build_course(self, course, institution, language):
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
