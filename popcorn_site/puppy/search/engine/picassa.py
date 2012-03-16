# -*- coding: utf8 -*-

import urllib2

from puppy.search import SearchEngine
from puppy.model import Query, Response

from puppy.search.exceptions import SearchEngineError

class Picassa(SearchEngine):
  """
  Picassa search engine.

  Parameters:

  * resultsPerPage (int): select how many results per page

  * access (str): public, private (it is not recommended to change to private), all, visible
  
  * kind (str): photo is the only working option

  """
  
  def __init__(self, service, resultsPerPage = 8, access = 'public', kind = 'photo', **args):
    super(Picassa, self).__init__(service, **args)
    self.resultsPerPage = resultsPerPage
    self.access = access
    self.kind = kind
    

  def _origin(self):
    """ This overrides SearchEngine's default origin (for results from a search engine) for Picassa """
    return 1  
  
  def search(self, query, offset):
    """
    Search function for Picassa.
    
    Parameters:
    
    * query (puppy.model.OpenSearch.Query)

    * offset (int): result offset for the search
    
    Returns:
    
    * puppy.model.OpenSearch.Response
    
    Raises:
    
    * urllib2.URLError
    
    """
    def setThumbnail(picassaResponse):
      """This goes through the results and sets thumnail"""
      for result in picassaResponse.entries:
          result['thumbnail'] = result['media_thumbnail'][2]['url']
      return picassaResponse

    try:
      pos = self._origin() + offset    
      url ='https://picasaweb.google.com/data/feed/api/all?q={0}&access={1}&kind={2}&start-index={3}&max-results={4}'.format(urllib2.quote(query.search_terms), self.access, self.kind, pos, self.resultsPerPage)
    
      data = urllib2.urlopen(url)
      picassaResponse = Response.parse_feed(data.read())
      return setThumbnail(picassaResponse)

	# urllib2 - this catches http errors due to the service being down, lack of a proxy etc
    except urllib2.URLError, e:
      raise SearchEngineError("Picassa", e, errorType = 'urllib2', url = url)

    # Check for a type error for offset or resultsPerPage
    except TypeError, e:
      note = "Please ensure that 'offset' and 'resultsPerPage' are integers if used"
      if isinstance(offset, int) == False:
          raise SearchEngineError("Picassa", e, note = note, offsetType = type(offset))

      if isinstance(self.resultsPerPage, int) == False:
          raise SearchEngineError("Picassa", e, note = note, resultsPerPageType = type(self.resultsPerPage))

      raise SearchEngineError("Picassa", e, note = note)

    # Catch all exception, just in case
    except Exception, e:
      raise SearchEngineError("Picassa", e, url = url)
