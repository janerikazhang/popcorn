# -*- coding: utf8 -*-

import urllib2
import json

from puppy.search.engine.site import sitesearch
from puppy.search import SearchEngine
from puppy.model import Query, Response

from puppy.search.exceptions import SearchEngineError

class Wordnik(SearchEngine):
  """
  Worknik search engine wrapper for their dictionary based API. This wrapper allows for searching for spelling corrections, examples of the usage of a word (in web results),
  and also definitions for a word.

  This API is only for English however, other languages are not supported.

  You must include your api key for Wordnik in your service manage config to use this service. It should be under the identifier "wordnik_api_key"

  With sourceDictionaries (see below) you can select multiple values i.e. ahd,webster but this will just return the first definition from ahd or if it doesn't have one from webster

  Parameters:

  * source (str): what source the results should come from, valid options are: 'Suggestions', 'Examples', 'Definitions'

  * resultsPerPage (int): How many (the maximum number) results to return


  -- Definitions Only Parameters --

  * sourceDictionaries (str): the dictionary to search, if blank it defaults to the first definition. Other options are: 'all', 'ahd', 'century', 'wiktionary', 'webster', 'wordnet'

  """
    
  def __init__(self, service, source = 'Definitions', resultsPerPage = 8, sourceDictionaries = None, **args):
    SearchEngine.__init__(self, service, **args)

    self.source = source
    self.resultsPerPage = resultsPerPage
    self.sourceDictionaries = sourceDictionaries

  def search(self, query, offset):
    """Search function for Worknik Search.
        
    
    Parameters:
    
    * query (puppy.model.Query)

    * offset (int): result offset for the search
    
    Returns:
    
    * puppy.model.Response
    
    Raises:
    
    * urllib2.URLError
    
    """
    
    def parse_wordnik_json(site, query, results, url):
      """Create a OpenSearch Response from Wordnik results.
      
      Wordnik's search API returns results in JSON format. This function simply loads the JSON into memory and creates an equivalent representation that is OpenSearch compliant.
      
      Parameters:
      
      * site (str): search engine name
      * query (str): query search terms (n.b. not a OpenSearch Query object)
      * results (dict): results from service
      
      Returns:
      
      * puppy.model.OpenSearch.Response
      
      """
      response = Response()
      response.version = 'json'
      response.feed.setdefault('title', "{0}: {1}".format(site, query))
      response.feed.setdefault('link', url)
      response.feed.setdefault('description', "Search results for '{0}' at {1}".format(query, site))
      response.namespaces.setdefault("opensearch", "http://a9.com/-/spec/opensearch/1.1/")
      try:
        response.feed.setdefault("opensearch_itemsperpage", self.resultsPerPage)
        response.feed.setdefault("opensearch_startindex", 0)
      except KeyError:
        response.feed.setdefault("opensearch_totalresults", 0)
        response.feed.setdefault("opensearch_itemsperpage", 0)
        response.feed.setdefault("opensearch_startindex", 0)
      
      try:
	
        if self.source == 'Suggestions':
          response.entries = parseSuggestionsJson(results, query)
          response.feed.setdefault("opensearch_totalresults", int(len(results['suggestions'])))
        elif self.source == 'Examples':
          response.entries = parseExamplesJson(results)
          response.feed.setdefault("opensearch_totalresults", int(len(results['examples'])))
        elif self.source == 'Definitions':
          response.entries = parseDefinitionsJson(results)
          response.feed.setdefault("opensearch_totalresults", int(len(results)))

      except Exception, e:
        pass
      
      return response

    def parseSuggestionsJson(results, query):

        parsedResults = []

        for result in results['suggestions']:
            result_dict = {"title": "Spelling Suggestion for: '{0}'".format(query),  "link": ''}
            result_dict['summary'] = "Original query: '{0}'. Suggested correction of query: '{1}'.".format(query, result) 
            result_dict['suggestion'] = result
            parsedResults.append(result_dict)
        return parsedResults

    def parseExamplesJson(results):

        parsedResults = []

        for result in results['examples']:
            result_dict = {"title": result['title'], "summary": result['text'], "rating": result['rating'], "year": result['year']}
            if "url" in result:
                result_dict['link'] = result['url']
            else:
                result_dict['link'] = ''
            parsedResults.append(result_dict)
        return parsedResults

    def parseDefinitionsJson(results):
    
        parsedResults = []

        for result in results:
            result_dict = {"title": result['word'], "summary": result['text'], "link": '', "score": result['score'], "sourceDictionary": result['sourceDictionary']}

            if 'partOfSpeech' in result:
                result_dict['partOfSpeech'] = result['partOfSpeech']
            parsedResults.append(result_dict)

        return parsedResults

    # Try and get the API key from config, if it's not there raise an API Key error - the application will have to deal with this
    try:
      apiKey = self.service.config["wordnik_api_key"]
    except KeyError:
      raise ApiKeyError("Wordnik Search API", "wordnik_api_key")
	
    try:
      url = "http://api.wordnik.com/v4/word.json/{0}".format(urllib2.quote(query.search_terms))

      # If we are using suggestions we actually use the word search api with suggestions i.e. related words and spelling suggestions
      if(self.source.lower() == 'suggestions'):
          url += "?includeSuggestions=true"

      # If we are using examples source type
      if(self.source.lower() == 'examples'):
          url += "/examples?limit={0}".format(self.resultsPerPage)

      # If we are using the definitions source type we can add the source dictionary parameter to get results from a specific dictionary only
      if(self.source.lower() == 'definitions'):
          url += "/definitions?limit={0}&useCanonical=true".format(self.resultsPerPage)
          if self.sourceDictionaries:
              url += "&sourceDictionaries={0}".format(self.sourceDictionaries)

      # Add in the API key
      url += "&api_key={0}".format(apiKey)

      data = urllib2.urlopen(url).read()
      results = json.loads(data)
      return parse_wordnik_json('Wordnik Search API', query.search_terms, results, url)

    # urllib2 - this catches http errors due to the service being down, lack of a proxy etc
    except urllib2.URLError, e:
      raise SearchEngineError("Wordnik Search API", e, errorType = 'urllib2', url = url)

    # Check for a type error for offset or resultsPerPage
    except TypeError, e:
      note = "Please ensure that 'resultsPerPage' is an integer if used"

      if isinstance(self.resultsPerPage, int) == False:
          raise SearchEngineError("Wordnik Search API", e, note = note, resultsPerPageType = type(self.resultsPerPage))

	  raise SearchEngineError("Wordnik Search API", e, note = note)

    # Catch all exception, just in case
    except Exception, e:
      raise SearchEngineError("Wordnik Search API", e, url = url)
