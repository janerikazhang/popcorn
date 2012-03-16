# -*- coding: utf8 -*-

import urllib2

from puppy.search import SearchEngine
from puppy.model import Query, Response

class BingSite(SearchEngine):
  """
  Bing site search engine wrapper.

  Parameters:

  * site: if you wish to search specific websites for results

  * source (str): web, image, news are the options

  """
  
  def __init__(self, service, site = None, source = 'web'):
    self.site = site
    self.source = source
    super(BingSite, self).__init__(service)
  
  
  def search(self, query, offset):
    """
    Search function for Microsoft Bing.
    
    Parameters:
    
    * query (puppy.model.Query)

    * offset (int): result offset for the search
    
    Returns:
    
    * results (puppy.model.Response)
    
    Raises:
    
    * urllib2.URLError
    
    """
    pos = self._origin() + offset
    
    if self.site:
      #create query using the list of sites
      extended_q = "site:http://www.amc.nl"
      for domain in self.site:
	extended_q = extended_q + " OR site:"+ domain
      extended_q= query.search_terms + " (" + extended_q+ ")"
      extended_q = urllib2.quote(extended_q)
      url = 'http://api.search.live.net/rss.aspx?query='+ extended_q + '&source={1}&{1}.count=10&{1}.offset={2}'.format(extended_q,self.source, pos)
     # url = 'http://api.search.live.net/rss.aspx?query=kids&source=web'
      
    else:
      url = 'http://api.search.live.net/rss.aspx?&query={0}&source={1}&{1}.count=10&{1}.offset={2}'.format(urllib2.quote(query.search_terms), self.source, pos)
    try:
      
      data = urllib2.urlopen(url)
      
      return Response.parse_feed(data.read())
    except urllib2.URLError, e:
      print "Error in Search Service: Bing search failed"
