.. _extending_the_search_engine:

Adding new Search Engine Wrappers 
=======================================

This section details adding new search engine wrappers. Firstly, every wrapper must extend the base class SearchEngine.

The SearchEngine base class
---------------------------

This base class defines the standard attributes common to all search engine wrappers. It also provides the facility to use search engines within a proxy server if this is required. The key aspect is that the search method must be overwritten by any derived classes.

::

  import urllib2

  class SearchEngine(object):
    """Abstract search engine interface."""
  
    def __init__(self, service):
      """
      Constructor for SearchEngine.
    
      Parameters:
    
      * service (puppy.service.SearchService): A reference to the parent search service
      * options (dict) a dictionary of engine specific options
      """
      self.name = self.__class__.__name__
      self.service = service
      self.configure_opener()

    def _origin(self):
      """ This defines the default origin for results from a search engine """
      return 0
  
  
    def configure_opener(self):
      """Configure urllib2 opener with network proxy"""
    
      if "proxyhost" in self.service.config:
        proxy_support = urllib2.ProxyHandler({'http': self.service.config["proxyhost"]})
        opener = urllib2.build_opener(proxy_support)
      else:
        opener = urllib2.build_opener()
      urllib2.install_opener(opener)
    
  
    def search(self, query, pos=1):
      """
      Perform a search.
    
      Parameters:
    
      * query (puppy.model.Query): query object
      * offset (int): result offset
    
      Returns:
      
      * results (puppy.model.Response): results of the search
    
      """
      pass

Creating a new Search Engine wrapper
------------------------------------

When adding new search engine wrappers, the base class (SearchEngine) will be used and extended to process results from the new service. The Picassa (an online image sharing website) wrapper is included below to illustrate how to go about adding new wrappers.

The search method must be passed a Query object and return a Response object (these are models defined in the PuppyIR framework).

::

  import urllib2

  from puppy.search import SearchEngine
  from puppy.model import Query, Response

  class Picassa(SearchEngine):
    """
    Picassa search engine.

    Parameters:

    * resultsPerPage: select how many results per page
    """
  
    def __init__(self, service, resultsPerPage=8):
      self.maxResults = maxResults
      super(Picassa, self).__init__(service)
  
  
    def search(self, query, offset):
      """
      Search function for Picassa.
    
      Parameters:
    
      * query (puppy.model.OpenSearch.Query)
    
      Returns:
    
      * puppy.model.OpenSearch.Response
    
      Raises:
    
      * urllib2.URLError
    
      """
      userQuery = urllib2.quote(query.search_terms)
      url = "https://picasaweb.google.com/data/feed/api/all?q={0}&kind=photo".format(userQuery)

      # Add in the resultsPerPage parameter
      url += "&max-results={0}".format(self.resultsPerPage)

      try:
        data = urllib2.urlopen(url)
        return Response.parse_feed(data.read())
      except urllib2.URLError, e:
        print "Error in Search Service: Picassa search failed"

Origin of the results
---------------------

Results from a search engine are, generally, either 0 or 1 indexed depending upon the service in question. To account for this, as shown in the code of SearchEngine, there is an origin defined and each service uses the following code to work out which page to use (in the URL parameters):

::

   pos = self._origin() + offset

The default is '0' and so, if a search engine is 1-indexed, for example, the search engine wrapper must override the origin in SearchEngine with its own version (the code for pos is unchanged):

::

  def _origin(self):
    """ This SearchEngine is 1-indexed so override the default"""
    return 1

Json and other formats
----------------------

The standard method, as detailed above, is for wrappers to parse RSS/Atom feeds to retrieve the results. However, not all API's return results in this format and so, if other formats are used the wrapper itself will need to parse them. The result of this parsing must be a response object with all the standard fields required by the OpenSearch standard.

For examples of how to do this, consult the code in the following wrappers:

* JSON: the Guardian and Yahoo! wrappers.
* XML: the Wikipedia and Simple Wikipedia wrappers.