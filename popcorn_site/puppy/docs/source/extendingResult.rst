.. _extending_the_result_pipeline:

Extending the Result Pipeline 
===================================

This section details adding new Result Filters and Result Modifiers. 

Note: there is an optional parameter for both called 'order' to indicate the precedence of a the filter or modifier in question.

The Orderable base class
-----------------------------

Both filters and modifiers extend the base class Orderable:

::

  class Orderable(object):
    def __init__(self, order=0):
      self.order = order
      self._init()

    def _init(self):
      raise NotImplementedError()

This contains the attributes common to both filters and modifiers: the order (this defines the order in which a filter or a modifier is executed in their respective pipelines).

Note: this class is detailed for reference only, since it is not expected that this base class will be modified when extending PuppyIR.

Creating new Result Filters
---------------------------

All Result Filters must extend the base class ResultFilter:

::

  class ResultFilter(Orderable):
    """Abstract result filter."""

    def _init(self):
        self.name = self.__class__.__name__
        self.description = ""

    def __call__(self, *args):
        return self.filter(*args)

    def filter(self, results):
        """ Return a boolean of whether this filter succeeded. """

        raise NotImplementedError()

The filter method *must* return either: true or false - depending upon whether, or not, the defined criteria is met.

For example, a ProfanityFilter that rejects results if their title does not pass the WDYL services test (this is a Google web service):

::

  from puppy.result import ResultFilter
  from puppy.query.filter.profanity_filter import WdylProfanityFilter as WQF

  import urllib

  class WdylProfanityFilter(ResultFilter):
    """ Filters results with profanity in them by using the wdyl service."""

    def __init__(self, order=0):
        super(WdylProfanityFilter, self).__init__(order)
        self._filter = WQF()

    def filter(self, results):
    # Go through each result and check each field doesn't contain words in the exclusion list
        for result in results:
            if self._filter(result['title']):
                yield result


Creating new Result Modifiers
-----------------------------

All Result Modifiers must extend the base class ResultModifier:

::

  class ResultModifier(Orderable):
    """ Change result. """

    def _init(self):
        self.name = self.__class__.__name__
        self.description = ""

    def __call__(self, *args):
        return self.modify(*args)

    def modify(self, results):
        """ Return a result, modified. """
        raise NotImplementedError()

The modify method *must* be passed and also return a response object.

For example, a modifier called TitleBlackListModifier that replaces blacklisted words in the title with \***.

::

  import string
  from puppy.result import ResultModifier


  class TitleBlackListModifier(ResultModifier):
    """
    Modify processes result entry content and replaces blacklisted words
  
    Options:
    * order (int): modifier precedence
    * terms (str): terms that, if appearing in the result, will be replaced with ***
    """
  
    def __init__(self, order=0, terms=""):
        """
        Constructor for BlackListResultModifier.

        Parameters: 
        * order (int): filter precedence
        * terms (str): separated by + characters
        """

        super(TitleBlackListModifier, self).__init__(order)
        self.info = "Modify search results based on a blacklist."
        self.terms = terms
        self.black_list = " ".join(filter(str.isalpha, terms.replace('+', ' ').lower().split()))
  
    def apply_black_list(self, input_string):
        """
        Replaces words in black list for *** characters.
    
        Parameters:
        * black_list_string: string with words included in the black list
        * input_string: string with words separated by blank spaces 
    
        Returns:    
        * ouput_string: string of words separated by blank spaces which 
        words included in the black list has been replaced by ***       
        """
        input_list = input_string.split()
        output_string = input_string

        for input in input_list:  
            try:  
                input_filtered = "".join(filter(str.isalpha, list(input.lower())))
            except TypeError:
                 tmp = input.encode("utf-8").lower()
                 input_filtered = "".join(filter(str.isalpha, list(tmp)))
             
            if input_filtered in self.black_list:
                if input_filtered not in ' ':
                    output_string = output_string.replace(input, '***')
        return output_string

    def modify(self, results):
        """
        Filters the results according to black list - 
        censoring any blacklisted words occurring in results.
    
        Parameters:      
        * results (puppy.model.Opensearch.Response): results to be filtered
    
        Returns:    
        * results_returned (puppy.model.Opensearch.Response): filtered results          
        """   
        for result in results:
            result['title'] = self.apply_black_list(result['title'])
            yield result
