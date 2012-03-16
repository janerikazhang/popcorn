.. _extending_the_query_pipeline:

Extending the Query Pipeline 
==================================

This section details adding new Query Filters and Query Modifiers.

Note: there is an optional parameter for both called 'order' to indicate the precedence of a the filter or modifier in question.

The Query Operator base class
-----------------------------

Both filters and modifiers extend the base class QueryOperator:

::

  class _QueryOperator(object):
    """Abstract class for query filters."""
  
    def __init__(self, order=0):
      self.name = self.__class__.__name__
      self.description = ""
      self.order = order

This contains the attributes common to both filters and modifiers: name, description and order (this defines the order in which a filter or a modifier is executed in their respective pipelines).

Note: this class is detailed for reference only, since it is not expected that this base class will be modified when extending PuppyIR.

Creating new Query Filters
--------------------------

All Query Filters must extend the base class QueryFilter:

::

  class QueryFilter(_QueryOperator):
    """Base class for query filters"""

    def __call__(self, *args):
        return self.filter(*args)

    @ensure_query
    def filter(self, query):
        raise NotImplementedError()

The filter method *must* return either: true or false - depending upon whether, or not, the defined criteria is met.

For example, a BlackListFilter that rejects queries if they contain blacklisted words:

::

  import string
  from puppy.query import QueryFilter
  from puppy.model import Query


  class BlackListFilter(QueryFilter):

    def __init__(self, order=0, terms=""):
        super(BlackListFilter, self).__init__(order)
        self.description = "Rejects queries containing any blacklisted terms."
        self.terms = set(terms.lower().split())


    def filter(self, query):
        """
        Rejects queries containing any of the defined blacklisted terms.

        Parameters:

        * query (puppy.model.Query): original query

        Returns:

        * query (puppy.model.Query): filtered query

        """
        original_terms = set(query.search_terms.lower().split())
        return not (original_terms & self.terms)

Creating new Query Modifiers
----------------------------

All Query Modifiers must extend the base class QueryModifier:

::

  class QueryModifier(_QueryOperator):
    def __call__(self, *args):
        # shortcut for modify
        return self.modify(*args)

    @ensure_query
    def modify(self, query):
        raise NotImplementedError()

The modify method *must* be passed and also return a query object.

For example, a TermExpansionModifier that appends extra terms onto a query for example adding "for kids" to each query:

::

  from puppy.query import QueryModifier
  from puppy.model import Query

  class TermExpansionModifier(QueryModifier):
    """Expands original query terms with extra terms."""

    def __init__(self, order=0, terms=""):
        super(TermExpansionModifier, self).__init__(order)
        self.description = "Expands original query terms with extra terms."
        self.terms = terms


    def modify(self, query):
        """
        Expands query with additional terms.

        Parameters:

        * query (puppy.model.Query): original query

        Returns:

        * query (puppy.model.Query): expanded query

        """
        query.search_terms = " ".join([query.search_terms, self.terms])
        return query