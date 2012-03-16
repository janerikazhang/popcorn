# -*- coding: utf8 -*-

import urllib2
import json

from puppy.search import SearchEngine
from puppy.model import Query, Response

from puppy.search.exceptions import SearchEngineError

class Digg(SearchEngine):
  """
  Digg search engine wrapper.

  Parameters:

  * resultsPerPage (int): How many results per page
 
  * sort (str): how to sort results (see Digg site for a list of the options) an example is 'submit_date-desc' to sort via the item's submit date

  * topic (str): restrict the search to a specific topic (see Digg site for a list of them)

  * media (str): options are: 'all', 'news', 'videos', 'images'

  * max_date (unix timestamp - converted to str): latest date results returned were posted

  * min_date (unix timestamp - converted to str): earliest date results returned were posted

  """
    
  def __init__(self, service, resultsPerPage = 8, sort = None, topic = None, media = 'all', max_date = None, min_date = None, **args):
    super(Digg, self).__init__(service, **args)
    self.resultsPerPage = resultsPerPage
    self.sort = sort
    self.topic = topic
    self.media = media
    self.max_date = max_date
    self.min_date = min_date
    
  def search(self, query, offset):
    """Search function for Dig Search.
        
    
    Parameters:
    
    * query (puppy.model.Query)
    
    Returns:
    
    * puppy.model.Response
    
    Raises:
    
    * urllib2.URLError
    
    """
    
    def parse_digg_json(site, pos, query, results):
      """Create a OpenSearch Response from Digg results.
      
      Digg's search API returns results in JSON format. This function simply loads the JSON into memory and creates an equivalent representation that is OpenSearch compliant.
      
      Parameters:
      
      * pos(int): which page number we're on
      * site (str): search engine name
      * query (str): query search terms (n.b. not a OpenSearch Query object)
      * results (dict): results from service
      
      Returns:
      
      * puppy.model.OpenSearch.Response
      
      """
      response = Response()
      response.version = 'json'
      response.feed.setdefault('title', "{0}: {1}".format(site, query))
      response.feed.setdefault('description', "Search results for '{0}' at {1}".format(query, site))
      response.namespaces.setdefault("opensearch", "http://a9.com/-/spec/opensearch/1.1/")
      try:
        response.feed.setdefault("opensearch_totalresults", results['total'])
        response.feed.setdefault("opensearch_itemsperpage", self.resultsPerPage)
        response.feed.setdefault("opensearch_startindex", pos)
      except KeyError:
        response.feed.setdefault("opensearch_totalresults", 0)
        response.feed.setdefault("opensearch_itemsperpage", 0)
        response.feed.setdefault("opensearch_startindex", 0)
      
      try:
        for result in results['stories']:
            item_dict = result # See Digg for the result format for all the other data
            item_dict['summary'] = result['description']
            item_dict['link'] = result['href']
            response.entries.append(item_dict)
      except Exception, e:
        pass
      
      return response
    try:    
      pos = self._origin() + offset
      url = "http://services.digg.com/2.0/search.search?query={0}&count={1}&offset={2}&media={3}".format(urllib2.quote(query.search_terms), self.resultsPerPage, pos, self.media)

      if self.topic:
          url += "&topic={0}".format(self.topic)

      if self.sort:
          url += "&sort={0}".format(self.sort)
	
      if self.max_date:
          url += "&max_date={0}".format(self.max_date)
		
      if self.min_date:
          url += "&min_date={0}".format(self.min_date)

      data = urllib2.urlopen(url).read()
      results = json.loads(data)
      return parse_digg_json('Digg', pos, query.search_terms, results)

    # urllib2 - this catches http errors due to the service being down, lack of a proxy etc
    except urllib2.URLError, e:
      raise SearchEngineError("Digg", e, errorType = 'urllib2', url = url)

    # Check for a type error for offset or resultsPerPage
    except TypeError, e:
      note = "Please ensure that 'offset' and 'resultsPerPage' are integers if used"
      if isinstance(offset, int) == False:
          raise SearchEngineError("Digg", e, note = note, offsetType = type(offset))

      if isinstance(self.resultsPerPage, int) == False:
          raise SearchEngineError("Digg", e, note = note, resultsPerPageType = type(self.resultsPerPage))

	  raise SearchEngineError("Digg", e, note = note)

    # Catch all exception, just in case
    except Exception, e:
      raise SearchEngineError("Digg", e, url = url)