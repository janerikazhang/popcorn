.. _exceptionsInPuppyIR:

Exception Handling in PuppyIR
===================================

PuppyIR provides a basic set of exceptions to handle errors specific to its components. These exceptions are split between errors that occur during the Query and Result pipelines, in addition to errors that occur within a search engine wrapper.

Exception handling in the Query Pipeline
------------------------------------------

The following exceptions are available at this stage:

* **Query Rejection Error**: use this exception for when a query is rejected due to it failing one or more query filter tests. For example, if a profanity filter is used and the users query contains a swear word the query will be rejected - when catching this exception callers should provide code to deal with this situation as no results will be returned if this occurs.
* **Query Filter Error**: use for situations in which the filter operationally failed and the filter's function cannot be realised. Callers should respond to this as if a rejection decision cannot be made.
* **Query Modifier Error**: Use for situations in which the modifier operationally failed and the modifier's function cannot be realised. Callers should respond to this as if a modification or rejection decision cannot be made.

They can all be imported with the following line of code:

::

  from puppy.query.exceptions import QueryRejectionError, QueryFilterError, QueryModifierError

An example of how to handle a query rejection error is detailed below:

::

  try:
    web_results = service.search_services['web_search'].search(query).entries
  except QueryRejectionError:
    # This variable can then be used to decide to show an error or the results
    result_dict['webQueryRejected'] = True


Exception handling for searching within an application
------------------------------------------------------

The following exceptions are available at this stage:

* **Search Engine Error**: use this exception for handling issues arising from the operation of a search engine wrapper like proxy errors, the web service being down, invalid parameters etc. This is a general exception that deals with the aforementioned problems and any others that might occur.
* **API Key Error**: use this exception only if you are using search engine wrappers that require an API key (like BingV2) to ensure that the API key is supplied and has the correct field name.

They can both be imported with the following line of code:

::

  from puppy.search.exceptions import SearchEngineError, ApiKeyError

A *'Search Engine Error'* contains the option of printing out a formatted error message; as opposed to the default, of it being outputted as one line; an example of how to handle both of the search engine exceptions and make use of the formatted print for *'SearchEngineError'* is given below:

::

  formattedDesc = True
   # The searching code in the 'try' in simplified (full examples are found elsewhere)
  try:
    results = serviceManager.search_services['bing_web'].search(query).entries
  except SearchEngineError, e:
    if formattedDesc:
      print(e.formattedStr())
    else:
      print(e) # Unformatted is the default
  except ApiKeyError, e:
    print(e)

Exception handling in a search engine wrapper
---------------------------------------------

The following two examples detail how to implement the exceptions detailed above, in a search engine wrapper, i.e. if you are extending this part of the framework (see: :ref:`extending_the_search_engine` for more details on adding a new search engine wrapper).

Below is an example of how to handle an 'API key Error's:

::

  # Try and get the API key from config, if it's not there raise the error
  try:
    appId = self.service.config["bing_api_key"]
  except KeyError:
    # First parameter is the wrapper name, the second is the field name for the API key
    raise ApiKeyError("BingV2", "bing_api_key")

Below is an example of how to use the 'Search Engine Error' to deal with:

1. A urllib2 error, adding in extra parameters for the error message.
2. A type error for some local variables.
3. A general catch-all error for anything unforeseen (this enables the 'Search Engine Error' to be used in an application as a general catch all exception; yet still provide specific details).

::

  try:
    # Omitted the code preceding the return statement see 'BingV2.py' for it in full
    return parse_bing_json('BingV2', query.search_terms, results, sources, pos)

  # urllib2 - this catches http errors due to the service being down, lack of a proxy etc
  except urllib2.URLError, e:
    raise SearchEngineError("BingV2", e, errorType = 'urllib2', url = url)

  # Check for a type error for offset or resultsPerPage
  except TypeError, e:
    note = "Please ensure that 'offset' and 'resultsPerPage' are integers if used"
    if isinstance(offset, int) == False:
      raise SearchEngineError("BingV2", e, note = note, offsetType = type(offset))

    if isinstance(self.resultsPerPage, int) == False:
      resultsType = type(self.resultsPerPage)
      raise SearchEngineError("BingV2", e, note = note, resultsPerPageType = resultsType)

    raise SearchEngineError("BingV2", e, note = note)

  # Catch all exception, just in case
  except Exception, e:
    raise SearchEngineError("BingV2", e, url = url)

You can pass a 'Search Engine Error' exception as many extra parameters as required - since it uses a key/value args parameter which enables extra information, specific to your wrapper, to be added and outputted as part of the exceptions error message.

Exception handling with the Result Pipeline
-------------------------------------------

The following exceptions are available at this stage:

* **Result Filter Error**: use for situations in which the filter operationally failed and the filter's function cannot be realised. Callers should respond to this as if a rejection decision cannot be made.
* **Result Modifier Error**: Use for exceptions in which the modifier operationally failed and the modifier's function cannot be realised. Callers should respond to this as if a modification or rejection decision cannot be made.

They can all be imported with the following line of code:

::

  from puppy.result.exceptions import ResultFilterError, ResultModifierError


Note on the current state of Filter and Modifier Exceptions
-------------------------------------------------------------

In both the Query and Result pipelines the Filter and Modifier errors are not fully implemented; in that, the modifiers and filters make little or no use of them in the current version of the framework. This is something that - should - be changing in forthcoming releases of the framework. The implementation and handling of these exceptions is recommended for anyone adding new filters and/or modifiers to these pipelines. See :ref:`extending_the_query_pipeline` and :ref:`extending_the_result_pipeline` for more on extending these parts of the framework.