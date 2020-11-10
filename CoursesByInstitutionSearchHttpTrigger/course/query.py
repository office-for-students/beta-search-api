import os
import re


def build_course_search_query(
    course, institution, postcode_object, query_params
):
    query = Query(course, institution, postcode_object, query_params)

    query.build()

    return query.add_paging()


class Query:
    def __init__(
        self, course, institution, postcode_object, query_params
    ):

        self.postcode_object = postcode_object
        self.course = course
        self.institution = institution
        self.query_params = query_params

    def build(self):
        query = ""
        # Create search part of query
        search = list()

        if self.course:
            english_course_search_query = "course/title/english:" + self.course
            welsh_course_search_query = "course/title/welsh:" + self.course
            search.append(english_course_search_query)
            search.append(welsh_course_search_query)

        if search:
            query += "&search=" + " ".join(search) + "&queryType=full"
        else:
            query += "&search=*"

        # Create filter part of query
        filters = list()
        if self.query_params["language"] == "cy":
            filters.append("course/institution/pub_ukprn_welsh_name eq '" + self.institution + "'")
        else:
            filters.append("course/institution/pub_ukprn_name eq '" + self.institution + "'")

        if "countries" in self.query_params and self.query_params["countries"]:

            countries = list()
            for country in self.query_params["countries"]:
                countries.append("course/country/code eq '" + country + "'")

            if len(countries) > 1:
                filters.append("(" + " or ".join(countries) + ")")
            else:
                filters.append(countries[0])

        if "distance_learning" in self.query_params:
            if self.query_params["distance_learning"]:
                filters.append("course/distance_learning/code ne 0")
            else:
                filters.append("course/distance_learning/code ne 1")

        if "foundation_year" in self.query_params:
            if self.query_params["foundation_year"]:
                filters.append("course/foundation_year_availability/code ne 0")
            else:
                filters.append("course/foundation_year_availability/code ne 2")

        if "full_time" in self.query_params:
            filters.append("course/mode/code eq 1")

        if "honours_award" in self.query_params:
            if self.query_params["honours_award"]:
                filters.append("course/honours_award_provision/code eq 1")
            else:
                filters.append("course/honours_award_provision/code eq 0")

        if (
            "length_of_course" in self.query_params
            and self.query_params["length_of_course"]
        ):
            loc = ",".join(self.query_params["length_of_course"])
            filters.append(
                "search.in(course/length_of_course/code, '" + str(loc) + "')"
            )

        if "part_time" in self.query_params:
            filters.append("course/mode/code eq 2")

        if "sandwich_year" in self.query_params:
            if self.query_params["sandwich_year"]:
                filters.append("course/sandwich_year/code ne 0")
            else:
                filters.append("course/sandwich_year/code ne 2")

        if "subjects" in self.query_params and self.query_params["subjects"]:
            subjects = list()

            for subject in self.query_params["subjects"]:
                subjects.append("s/code eq '" + subject + "'")

            if len(subjects) > 1:
                filters.append("course/subjects/any(s: " + " or ".join(subjects) + ")")
            else:
                filters.append("course/subjects/any(s: " + subjects[0] + ")")

        if "year_abroad" in self.query_params:
            if self.query_params["year_abroad"]:
                filters.append("course/year_abroad/code ne 0")
            else:
                filters.append("course/year_abroad/code ne 2")

        if self.postcode_object != {}:
            latitude = self.postcode_object["latitude"]
            longitude = self.postcode_object["longitude"]
            distance = self.postcode_object["distance"]

            filters.append(
                "course/locations/any(location: geo.distance(\
                           location/geo, geography'POINT("
                + str(longitude)
                + " "
                + str(latitude)
                + ")') le "
                + distance
                + ")"
            )

        filter_query = " and ".join(filters)

        if filter_query != "":
            query += "&$filter=" + filter_query

        # TODO Reinstate alphabetic ordering based on the course name 
        # after ordering by search score; search mappings in backend
        # pipeline need to be updated to be able to sort on course title
        # query += "&$orderby=course/title/english"

        self.query = query

    def add_paging(self):
        query = self.query

        # Add limit and offset parameters
        if "limit" in self.query_params:
            query += "&$top=" + str(self.query_params["limit"])

        if "offset" in self.query_params:
            query += "&$skip=" + str(self.query_params["offset"])

        return query
