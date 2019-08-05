""" exceptions.py: PostcodeSearchBuilder Custom Exceptions """


class Error(Exception):
    """ Base Exception Class """
    pass

class UnexpectedErrorExceptionFromSearchIndex(Error):
    """ An error is raised whilst calling search index """
    pass
