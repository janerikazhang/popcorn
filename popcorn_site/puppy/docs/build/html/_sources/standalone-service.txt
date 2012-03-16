.. _building-a-standalone-puppyir-service:

Building a Standalone PuppyIR Service
===========================================

The PuppyIR framework can be used to build a standalone service with no user interface. This is a good place to start when initially developing with PuppyIR and can also be more appropriate for experimental development of new child-friendly information processing components.

Service Implementation
----------------------

The following steps will create and configure a new service, consisting of: a search engine, a query logger & filtering for both the queries and the results retrieved (from the search engine wrappers used).

1. Create and Configure the ServiceManager
******************************************

Create a new python script, e.g. service.py

::

  from puppy.service import ServiceManager
  
  config = {}
  
  # Create the ServiceManager
  sm = ServiceManager(config)

2. Create a SearchService
*************************

::
  
  # new imports
  from puppy.service import ServiceManager, SearchService
  
  config = {}
  
  sm = ServiceManager(config)
  
  # create SearchService and give it a name
  ss = SearchService(sm, "bing_web")
  
  # Add new SearchServices to ServiceManager
  sm.add_search_service(ss)

3. Add a SearchEngine
*********************

::

  from puppy.service import ServiceManager, SearchService
  # new imports
  from puppy.search.engine import Bing
  
  config = {}
  
  sm = ServiceManager(config)
  ss = SearchService(sm, "bing_web")
  sm.add_search_service(ss)
  
  # Assign new Bing SearchEngine to SearchService
  ss.search_engine = Bing(ss)
  

4. Perform a Search
*******************

At this stage, we can now use the service we have created to search Bing.

::

  from puppy.service import ServiceManager, SearchService
  from puppy.search.engine import Bing
  # new imports
  from puppy.model import Query, Response
  
  config = {}
  
  sm = ServiceManager(config)
  ss = SearchService(sm, "bing_web")
  sm.add_search_service(ss)
  ss.search_engine = Bing(ss)
  
  # make a new Query and search
  query = Query("puppy")
  results = sm.search_services['bing_web'].search(query).entries
  
  # print results
  for result in results:
    print result['title']
    print result['summary']
    print result['link'] + '\n'

5. Enable the QueryLogger
*************************

It may be useful to start logging queries to file.

::

  from puppy.service import ServiceManager, SearchService
  from puppy.search.engine import Bing
  from puppy.model import Query, Response
  # new imports
  from puppy.logging import QueryLogger
  
  config = {
    "log_dir": "/path/to/log/directory", # Set this to where you want the logs stored
  }
  
  sm = ServiceManager(config)
  ss = SearchService(sm, "bing_web")
  sm.add_search_service(ss)
  ss.search_engine = Bing(ss)
  
  # Assign QueryLogger to SearchService
  ss.query_logger = QueryLogger(ss, log_mode=0)
  
  query = Query("puppy")
  results = sm.search_services['bing_web'].search(query).entries
  
  for result in results.entries:
    print result['title']
    print result['summary']
    print result['link'] + '\n'

6. Adding QueryFilters and ResultFilters
****************************************

::

  from puppy.service import ServiceManager, SearchService
  from puppy.search.engine import Bing
  from puppy.model import Query, Response
  from puppy.logging import QueryLogger
  # new imports
  from puppy.query.modifier import TermExpansionModifier
  from puppy.result.filter import ExclusionFilter
  
  config = {
    "log_dir": "/path/to/log/directory", # Set this to where you want the logs stored
  }
  
  sm = ServiceManager(config)
  ss = SearchService(sm, "bing_web")
  sm.add_search_service(ss)
  ss.search_engine = Bing(ss)
  ss.query_logger = QueryLogger(ss, log_mode=0)
  
  # Add TermExpansionModifier to SearchService
  ss.add_query_modifier(TermExpansionModifier(terms='for+kids'))

  # Add ExclusionFilter to SearchService
  ss.add_result_filter(ExclusionFilter(terms='bad+nasty'))
  
  query = Query("puppy")
  results = sm.search_services['bing_web'].search(query).entries
  
  for result in results.entries:
    print result['title']
    print result['summary']
    print result['link']
    print result['suitability'] + '\n'

Multiple Search Services
------------------------

Whilst searching one source is useful, there are many possible situations in which a PuppyIR based service might need to search multiple sources.  The simplest example, is a service that provides search suggestions alongside the main search results. The search suggestions may come from a completely different source, but, in this case, they come from a separate instance of Bing with a different source type: 'relatedSearch' (which retrieves query suggestions).

::

  from puppy.service import ServiceManager, SearchService
  from puppy.search.engine import Bing
  from puppy.model import Query, Response
  
  config = {} 
  sm = ServiceManager(config)
  
  # As before, create a SearchService for Bing (e.g. for main results)
  ss1 = SearchService(sm, "bing_web")
  sm.add_search_service(ss1)

  # The default source is 'web' below is an example of using a different source
  ss1.search_engine = Bing(ss1)

  # create our suggestion service
  suggestions_service = SearchService(serviceManager, "suggestion_search")
  suggestions_service.search_engine = Bing(suggestions_service, source = "RelatedSearch")

  # add SearchService to ServiceManager
  serviceManager.add_search_service(suggestions_service)
  
  query = Query("puppy")
  webResults = sm.search_services['bing_web'].search(query).entries
  suggestions = sm.search_services['suggestion_search'].search(query).entries
  
  for result in webResults:
    print result['title']
    print result['summary']
    print result['link']

  for result in suggestions:
    # The title is the query suggestion, i.e. for Batman a suggestion could be: Batman Begins
    print result['title']
