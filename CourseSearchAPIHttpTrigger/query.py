import logging

def build_search_query(course, institution, institutions, postcode_object, query_params):
    
    try:
        query = Query(course, institution, institutions, postcode_object, query_params)

        return query.build()
    except Exception:
        raise


class Query():
    def __init__(self, course, institution, institutions, postcode_object, query_params):
        if "geo_location" in postcode_object:
            self.geolocation = postcode_object["geo_location"]

        self.course = course
        self.institution = institution
        self.institutions = institutions
        self.query_params = query_params

    def build(self):
        # TODO build query string
        query = ""
        if "countries" in self.query_params and len(self.query_params["countries"]) > 0:
            query+=  ""
            for code in self.query_params["countries"]:
                query+= ""+code

        if "distance_learning" in self.query_params:
            query+= ""

        if "foundation_year" in self.query_params:
            query+= ""

        if "full_time" in self.query_params:
            query+= ""

        if "honours_award" in self.query_params:
            query+= ""

        if "length_of_courses" in self.query_params and len(self.query_params["length_of_courses"]) > 0:
            query+=  ""
            for l in self.query_params["length_of_courses"]:
                query+= ""+l

        if "limit" in self.query_params:
            query+= ""

        if "part_time" in self.query_params:
            query+= ""

        if "offset" in self.query_params:
            query+= ""

        if "sandwich_year" in self.query_params:
            query+= ""

        if "year_abroad" in self.query_params:
            query+= ""

        if self.institutions != "":
            # TODO split comma separated list
            query+= ""

        if self.geolocation != "":
            query+= ""

        if self.institution != "":
            query+= ""

        if self.course != "":
            query+= ""

        return query
