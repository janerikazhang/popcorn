# -*- coding: utf8 -*-

import urllib2
from lxml import etree

from puppy.search import SearchEngine
from puppy.model import Query, Response

from puppy.search.exceptions import SearchEngineError

class SimpleWikipedia(SearchEngine):
  """
  Simple Wikipedia search engine.

  Parameters:

  * resultsPerPage (int): How many results per page - note with Wiki only one page of results is returned.

  """
  
  def __init__(self, service,  resultsPerPage = 8, **args):
    super(SimpleWikipedia, self).__init__(service, **args)
    self.resultsPerPage = resultsPerPage
    
  
  def search(self, query, offset):
    """
    Search function for Simple Wikipedia.
  
    Parameters:
  
    * query (puppy.model.OpenSearch.Query)

    * offset (int): result offset for the search
  
    Returns:
  
    * puppy.model.OpenSearch.Response
  
    Raises:
  
    * urllib2.URLError
  
    """
  
    def parse_wiki_xml(query, results):
      """docstring for parse_wiki_xml"""
      response = Response()
      response.feed.setdefault("title", "Simple Wikipedia Search")
      response.feed.setdefault("description", "Simple Wikipedia Search Suggestions for: {0}".format(query))
      response.namespaces.setdefault("searchsuggest", "{http://opensearch.org/searchsuggest2}")
      response.version = 'xml'
    
      root = etree.XML(results)
      ns = response.namespaces["searchsuggest"]
      section = root.find("{0}Section".format(ns))
      items = section.findall("{0}Item".format(ns))
      for item in items:
        title = item.find("{0}Text".format(ns)).text
        summary = item.find("{0}Description".format(ns)).text
        link = item.find("{0}Url".format(ns)).text
        image = item.find("{0}Image".format(ns))
        image_thumbnail = image.get("source") if image is not None else ""
        image_fullsize = ""
        if image_thumbnail is not "":
          image_fullsize = image_thumbnail.replace("thumb/", "").rpartition('/')[0]
        response.entries.append({'title': title, 'summary': summary, 'link': link, 'image_thumbnail': image_thumbnail, 'image_fullsize': image_fullsize})    
    
      return response
   
    try:
      url = 'http://simple.wikipedia.org/w/api.php?action=opensearch&format=xml&search={0}&namespace=0&limit={1}'.format(urllib2.quote(query.search_terms), self.resultsPerPage)
      data = urllib2.urlopen(url)
      return parse_wiki_xml(query.search_terms, data.read())

	# urllib2 - this catches http errors due to the service being down, lack of a proxy etc
    except urllib2.URLError, e:
      raise SearchEngineError("Simple Wikipedia", e, errorType = 'urllib2', url = url)

    # Check for a type error for offset or resultsPerPage
    except TypeError, e:
      note = "Please ensure that 'resultsPerPage' is an integer if used"

      if isinstance(self.resultsPerPage, int) == False:
          raise SearchEngineError("Simple Wikipedia", e, note = note, resultsPerPageType = type(self.resultsPerPage))

	  raise SearchEngineError("Simple Wikipedia", e, note = note)

    # Catch all exception, just in case
    except Exception, e:
      raise SearchEngineError("Simple Wikipedia", e, url = url)

