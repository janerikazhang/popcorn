# -*- coding: utf8 -*-

from puppy.query.queryfilter import QueryFilter, QueryModifier
from puppy.core.type_checking import check
from puppy.result.resultfilter import ResultFilter, ResultModifier

from puppy.query.tokenizer import PunctuationAwareTokenizer

from puppy.query.exceptions import QueryRejectionError

from puppy.logging import QueryLogger


def embolden(query, text):
    query_terms = query.tokenize()

    new_text = []
    for term in text.split():
        check_term = term
        for p in PunctuationAwareTokenizer.PUNCTUATION:
            check_term = check_term.replace(p, '')

        if check_term.lower() in query_terms:
            term = '<em>%s</em>' % term
        new_text.append(term)

    return ' '.join(new_text)


class SearchService(object):
  """Models the configuration of a QueryFilter pipeline, Search Engine, and a ResultFilter pipeline."""
  
  def __init__(self, service_manager, name):
    """Constructor for Service."""
    self.service_manager = service_manager
    self.name = name
    self.config = service_manager.config
    self.search_engine = None
    self.query_logger = None
    self.postLogging = False
    self._init_filters()

  def _init_filters(self):
    self.query_filters = []
    self.query_modifiers = []
    self.results_filters = []
    self.results_modifiers = []
  
  def simplesearch(self, query, offset=0):
    """Search without query and result filter pipelines.
    
    Parameters:
    
    * query (puppy.model.Query): search query
    * offset (int): result offset
    
    Returns:
    
    * results (puppy.model.Response): search results
    """

    return self.search_engine.search(query, offset)
  
  
  def search(self, query, offset=0, highlight=False):
    """
    Search with query and result filter pipelines active.
    
    Parameters:
    
    * query (puppy.model.Query): search query
    * offset (int): result offset
    
    Returns:
    
    * results (puppy.model.Response): search results
    """
    
    # do logging
    if self.query_logger:
      self.query_logger.log(query)

    # process query
    for query_filter in sorted(self.query_filters, key=lambda x: x.order, reverse=False):
        q = query_filter(query)
        if q != True:
            raise QueryRejectionError(query)
    
    # process query
    for query_modifier in sorted(self.query_modifiers, key=lambda x: x.order,
            reverse=False):
        query = query_modifier(query)

    # do post logging if enabled
    if (self.query_logger) and (self.postLogging == True):
      self.query_logger.log(query, processed=True) # Processed i.e. the query after going through the query pipeline

    # search engine
    results = self.search_engine.search(query, offset)
    
    # process results

    # apply each filter. importantly, if any filter works as a generator, it
    # will act as an iterator here, filtering one item at a time before passing
    # each off to the next filter. hence, generator filter design is preferred
    # when possible

    search_results = results.entries

    for filt in sorted(self.results_filters, key=lambda x: x.order,
            reverse=True):

        # XXX TODO this should be parallelized since filters should be
        # independent!

        search_results = filt(search_results)

    for modifier in sorted(self.results_modifiers, key=lambda x: x.order,
            reverse=True):

        search_results = modifier(search_results)

    def _embolden_results(sr):
        for item in sr:
            item.title = embolden(query, item.title)
            item.summary = embolden(query, item.summary)

    if highlight:
        _embolden_results(search_results)

    results.entries = search_results
    return results


  def clear_filters(self):
      """ Remove all existing filters. """
      self._init_filters()

  def add_filters(self, *filters):
      """ Add one or more filters. Detects filter type (e.g., QueryFilter,
      ResultModifier) and places in appropriate pipeline. """

      for f in filters:
        dest = None

        if isinstance(f, QueryFilter):
            dest = self.query_filters
        elif isinstance(f, QueryModifier):
            dest = self.query_modifiers
        elif isinstance(f, ResultFilter):
            dest = self.results_filters
        elif isinstance(f, ResultModifier):
            dest = self.results_modifiers
        else:
            raise TypeError('%s (type=%s) not filter' % (f, type(f)))

        dest.append(f)

  def replace_filters(self, *filters):
      """ Replace existing filters with new filters. """
      self.clear_filters()
      self.add_filters(*filters)

  def add_query_modifier(self, query_modifier):
    """Add modifier to query modifier pipeline."""
    check(query_modifier, QueryModifier)
    self.query_modifiers.append(query_modifier)
  
  def add_query_filter(self, query_filter):
    """Add filter to query filter pipeline."""
    check(query_filter, QueryFilter)
    self.query_filters.append(query_filter)
  
  def add_result_filter(self, result_filter):
    """Add filter to result filter pipeline."""
    check(result_filter, ResultFilter)
    self.results_filters.append(result_filter)
  
  def add_result_modifier(self, result_modifier):
    """Add filter to result filter pipeline."""
    check(result_modifier, ResultModifier)
    self.results_modifiers.append(result_modifier)
