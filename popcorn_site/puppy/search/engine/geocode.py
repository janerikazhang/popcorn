# -*- coding: utf8 -*-

import urllib2
import json

from puppy.search import SearchEngine
from puppy.model import Query, Response
from math import atan2, sin, cos, sqrt, radians

from puppy.search.exceptions import SearchEngineError

class GoogleGeocode(SearchEngine):
  """
  GoogleGeocode search service.

  Parameters:

  * sensor(str): does your device have a GPS sensor or not, not recommended to change from 'false' but the other option is, naturally, 'true' - must be lowercase

  """
    
  def __init__(self, service, sensor = 'false', **args):
    super(GoogleGeocode, self).__init__(service, **args)
    self.sensor = sensor

  def calcDistance(self, lat1, lat2, lon1, lon2):
    # Credit for this method: http://www.movable-type.co.uk/scripts/latlong.html - modified by Doug for Python
    radiusEarth = 6371; # km
    dLat = radians(lat2-lat1)
    dLon = radians(lon2-lon1)
    self.lat1 = radians(lat1)
    self.lat2 = radians(lat2)

    a = sin(dLat/2) * sin(dLat/2) + sin(dLon/2) * sin(dLon/2) * cos(lat1) * cos(lat2); 
    c = 2 * atan2(sqrt(a), sqrt(1-a)); 
    distance = radiusEarth * c;

    return distance
  
    
  def search(self, query, offset):
    """Search function for Google Geocode Search.
        
    
    Parameters:
    
    * query (puppy.model.Query)

    * offset (int): result offset for the search
    
    Returns:
    
    * puppy.model.Response
    
    Raises:
    
    * urllib2.URLError
    
    """
    
    def parse_geocode_json(site, url, query, results):
      """Create a OpenSearch Response from Google Geoode results results.
      
      Google's Geocode search API returns results in JSON format. This function simply loads the JSON into memory and creates an equivalent representation that is OpenSearch compliant.
      
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
      
      response.feed.setdefault("opensearch_totalresults", 0)
      response.feed.setdefault("opensearch_itemsperpage", 0)
      response.feed.setdefault("opensearch_startindex", 0)

      i = 0 # count results for use in the feed fields later
      
      try:
        for result in results:
          resultDict ={}
          resultDict['title'] = result['formatted_address']
          longTitle = ''
          for component in result['address_components']:
              longTitle += (component['long_name'] + ', ')
          resultDict['link'] = ''
          resultDict['longTitle'] = longTitle[:len(longTitle)-2]
          resultDict['lat'] = result['geometry']['location']['lat']
          resultDict['lon'] = result['geometry']['location']['lng']
          resultDict['neBorderLat'] = result['geometry']['bounds']['northeast']['lat']
          resultDict['neBorderLon'] = result['geometry']['bounds']['northeast']['lng']
          resultDict['swBorderLat'] = result['geometry']['bounds']['southwest']['lat']
          resultDict['swBorderLon'] = result['geometry']['bounds']['southwest']['lng']
          resultDict['distanceAcross'] = self.calcDistance(resultDict['neBorderLat'], resultDict['swBorderLat'], resultDict['neBorderLon'], resultDict['swBorderLon'])
          resultDict['summary'] = "{0} is found at: Latitude: {1}, Longitude: {2}. The area it covers is {3}km across (between the NE and SW corners).".format(resultDict['title'], resultDict['lat'], resultDict['lon'], resultDict['distanceAcross'])
          response.entries.append(resultDict)
          i += 1

      # If there is an arithmetic error pass on the result but note it for the user
      except ArithmeticError, e:
        print "\n\n!!! Arithmetic Error in Google Geocode Search for result {0} !!! \n\n1) With Url: '{1}'\n".format(i, url)
        pass

      # If there is an Type error pass on the result but note it for the user
      except TypeError, e:
        print "\n\n!!! Type Error in Google Geocode Search in lat/lon variables for result {0} !!! \n\n1) With Url: '{1}'\n".format(i, url)
        pass

      # Otherwise rely on the exception in question
      except Exception, e:
        print "\n\n!!! {0}, Error in Google Geocode Search for result {1} !!! \n\n1) With Url: '{2}'\n".format(e, i, url)
        pass

      response.feed['opensearch_totalresults'] = i
      response.feed['opensearch_itemsperpage'] = i
      return response

    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json?address={0}&sensor={1}".format(urllib2.quote(query.search_terms), self.sensor)   
        data = urllib2.urlopen(url).read()
        results = json.loads(data)
        return parse_geocode_json('Google Geocode', url, query.search_terms, results['results'])
    
    # urllib2 - this catches http errors due to the service being down, lack of a proxy etc
    except urllib2.URLError, e:
      raise SearchEngineError("Google Geocode", e, errorType = 'urllib2', url = url)

    # Check for a type error for offset or resultsPerPage
    except TypeError, e:
      note = "Please ensure that 'offset' and 'resultsPerPage' are integers if used"
      if isinstance(offset, int) == False:
          raise SearchEngineError("Google Geocode", e, note = note, offsetType = type(offset))

      if isinstance(self.resultsPerPage, int) == False:
          raise SearchEngineError("Google Geocode", e, note = note, resultsPerPageType = type(self.resultsPerPage))

	  raise SearchEngineError("Google Geocode", e, note = note)

    # Catch all exception, just in case
    except Exception, e:
      raise SearchEngineError("Google Geocode", e, url = url)