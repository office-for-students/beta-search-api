import os
import re
import urllib.parse

from helper import is_welsh


def build_course_search_query(
        course, institution, institutions, postcode_object, query_params
):
    query = Query(course, institution, institutions, postcode_object, query_params)

    query.build()

    return query.add_paging()


def build_institution_search_query(
        course, institution, institutions, postcode_object, query_params
):
    query = Query(course, institution, institutions, postcode_object, query_params)

    query.build()

    return query.add_facet()


class Query:
    def __init__(
            self, course, institution, institutions, postcode_object, query_params
    ):

        self.postcode_object = postcode_object
        self.course = course
        self.institution = institution
        self.institutions = institutions
        self.query_params = query_params

    def generate_course_search_terms(self, course=None) -> str:
        english_course_search_query = f"course/title/english:{course}"
        welsh_course_search_query = f"course/title/welsh:{course}"

        if course:
            return f"{english_course_search_query}, {welsh_course_search_query}"

        return "*"

    def build(self):
        query_dict = {}

        search = self.generate_course_search_terms(self.course)
        query_dict["search"] = search
        query_dict["queryType"] = "full"
        query_dict["searchMode"] = "any"

        # Create filter part of query
        filters = list()
        if "countries" in self.query_params and self.query_params["countries"]:

            countries = list()
            for country in self.query_params["countries"]:
                countries.append("course/country/code eq '" + country + "'")

            if len(countries) > 1:
                filters.append("(" + " or ".join(countries) + ")")
            else:
                filters.append(countries[0])

        filters.append(Query.build_distance_learning_filter(self.query_params))

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

        if "first_degree" in self.query_params:
            filters.append("course/qualification/level eq 'first-degree'")

        if "other_undergraduate" in self.query_params:
            filters.append("course/qualification/level eq 'other-undergraduate'")

        if self.institutions != "":
            institution_filter_list = Query.build_institution_filter(self.institutions, self.query_params)

            for x in institution_filter_list:
                filters.append(x)

        # Condition that will remove distance learning from the filters, and run a function for a separate distance learning filter
        if '(course/distance_learning/code eq 0 or course/distance_learning/code eq 1 or course/distance_learning/code eq 2)' in filters:
            distance_filter = Query.build_or_distance_filter(self.query_params, filters)
            filters.remove(
                f'(course/distance_learning/code eq 0 or course/distance_learning/code eq 1 or course/distance_learning/code eq 2)')
            filters.append(f'course/distance_learning/code ne 1')

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
            filter_query += " or "
            filter_query += " and ".join(distance_filter)
        else:

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
            query_dict["filter"] = filter_query

        # Add alphabetic ordering based on the institution name after
        # ordering by search score
        if is_welsh(self.query_params["language"]):
            query_dict["orderby"] = "course/institution/sort_pub_ukprn_welsh_name"
        else:
            query_dict["orderby"] = "course/institution/sort_pub_ukprn_name"

        # print(f"search: {query_dict['search']}")
        # print(f"search: {query_dict['searchFields']}")

        self.query = query_dict

    def add_paging(self):
        result = dict()
        # Add limit and offset parameters
        if "limit" in self.query_params:
            result["top"] = str(self.query_params["limit"])

        if "offset" in self.query_params:
            result["skip"] = str(self.query_params["offset"])

        return {**self.query, **result}

    def add_facet(self):

        # Set top to be zero
        result = dict(top=0)

        # Build facet query for categorising courses by institution
        if is_welsh(self.query_params["language"]):
            result["facets"] = ["course/institution/sort_pub_ukprn_welsh_name,\
                count:500, sort:value"]
        else:
            result["facets"] = ["course/institution/sort_pub_ukprn_name,\
                count:500,sort:value"]

        return {**self.query, **result}

    def build_distance_learning_filter(query_params):
        on_campus = query_params.get('on_campus')
        distance_learning = query_params.get('distance_learning')
        doc = 'course/distance_learning/code'
        filter = f'({doc} eq 0 or {doc} eq 1 or {doc} eq 2)'

        if on_campus and not distance_learning:
            filter = f'{doc} ne 1'
        elif not on_campus and distance_learning:
            filter = f'{doc} ne 0'
        return filter

    def build_country_filter(query_params):
        filters = list()
        if "countries" in query_params and query_params["countries"]:

            countries = list()
            for country in query_params["countries"]:
                countries.append("course/country/code eq '" + country + "'")

            if len(countries) > 1:
                filters.append("(" + " or ".join(countries) + ")")
            else:
                filters.append(countries[0])

            return filters[0]

    def build_or_distance_filter(query_params, filters):
        distance_filter = filters.copy()
        on_campus = query_params.get('on_campus')
        distance_learning = query_params.get('distance_learning')
        doc = 'course/distance_learning/code'

        if f'({doc} eq 0 or {doc} eq 1 or {doc} eq 2)' in filters:
            distance_filter.remove(f'({doc} eq 0 or {doc} eq 1 or {doc} eq 2)')
            distance_filter.append(f'{doc} ne 0')

        if "countries" in query_params and query_params["countries"]:
            # remove all countries from the duplicate filter
            countries = list()
            for country in query_params["countries"]:
                countries.append("course/country/code eq '" + country + "'")

            if len(countries) > 1:
                distance_filter.remove("(" + " or ".join(countries) + ")")
            else:
                distance_filter.remove(countries[0])

        return distance_filter

    def build_institution_filter(institutions, query_params):
        institution_filters = list()
        split_institutions = institutions.split("@")
        institution_list = list()
        search_public_ukprn = os.environ["SearchPubUKPRN"]

        for institution in split_institutions:
            institution = institution.strip('"')

            if search_public_ukprn == "False":
                if is_welsh(query_params["language"]):
                    institution_list.append(
                        "course/institution/pub_ukprn_welsh_name eq '" + institution + "'"
                    )
                else:
                    institution_list.append(
                        "course/institution/pub_ukprn_name eq '" + institution + "'"
                    )
            else:
                institution_list.append(
                    "course/institution/pub_ukprn eq '" + institution + "'"
                )

        if len(institution_list) > 1:
            institution_filters.append("(" + " or ".join(institution_list) + ")")
        else:
            institution_filters.append(institution_list[0])

        return institution_filters
