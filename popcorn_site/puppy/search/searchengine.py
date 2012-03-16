# -*- coding: utf8 -*-

import urllib2

class SearchEngine(object):
  """Abstract search engine interface."""
  
  def __init__(self, service, **args):
    """
    Constructor for SearchEngine.
    
    Parameters:
    
    * service (puppy.service.SearchService): A reference to the parent search service
    * options (dict) a dictionary of engine specific options
    """
    self.name = self.__class__.__name__
    self.service = service
    self.configure_opener()

    # Prints invalid paramters recieved for the Search Engine - this allows the developer's code not to crash and alerts them to their mistake
    for parameter in args:
        print "'{0}' recieved invalid parameter called: '{1}'. Please consult the API reference document for a list of valid parameters.".format(self.name, parameter)

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
    * pos (int): result offset
    
    Returns:
      
    * results (puppy.model.Response): results of the search
    
    """
    pass
  

