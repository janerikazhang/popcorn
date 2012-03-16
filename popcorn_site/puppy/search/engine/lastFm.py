# -*- coding: utf8 -*-

import urllib2
import json

from puppy.search import SearchEngine
from puppy.model import Query, Response

from puppy.search.exceptions import SearchEngineError, ApiKeyError

class LastFM(SearchEngine):
  """
  LastFM search engine wrapper - allowing for Track, Album and Artist search results to be retrieved

  You must include your application's LastFM ID in your service manage config to use this service. It should be under the identifier "last_fm_api_key"

  Parameters:

  * source (str): What to search for, valid types: 'track', 'album' and 'artist'

  * resultsPerPage (int): How many results per page

  -- Track Only Parameters --

  * artist (str): the artist for the tracks you are searching for

  """
    
  def __init__(self, service, source = 'track', resultsPerPage = 8, artist = None, **args):
    super(LastFM, self).__init__(service, **args)
    self.source = source
    self.resultsPerPage = resultsPerPage
    self.artist = artist

  def _origin(self):
    """ This overrides SearchEngine's default origin (for results from a search engine) for LastFM """
    return 1

  def search(self, query, offset):
    """Search function for LastFM Search.
        
    
    Parameters:
    
    * query (puppy.model.Query)

    * offset (int): result offset for the search
    
    Returns:
    
    * puppy.model.Response
    
    Raises:
    
    * urllib2.URLError
    
    """
    
    def parse_last_fm_json(site, query, results, pos):
      """Create a OpenSearch Response from Bing V2 results.
      
      LastFM's search API returns results in JSON format. This function simply loads the JSON into memory and creates an equivalent representation that is OpenSearch compliant.
      
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
      response.feed.setdefault('description', "Search results for '{0}' at {1}".format(query, site))
      response.namespaces.setdefault("opensearch", "http://a9.com/-/spec/opensearch/1.1/")
      try:
        response.feed.setdefault("opensearch_totalresults", results['opensearch_totalresults'])
        response.feed.setdefault("opensearch_itemsperpage", results['opensearch_itemsperpage'])
        response.feed.setdefault("opensearch_startindex", pos)
      except KeyError:
        response.feed.setdefault("opensearch_totalresults", 0)
        response.feed.setdefault("opensearch_itemsperpage", 0)
        response.feed.setdefault("opensearch_startindex", 0)

      
      try:
          if self.source == 'track':
              response.entries = parseTrackJson(results)
          elif self.source == 'album':
              response.entries = parseAlbumJson(results)
          elif self.source == 'artist':
              response.entries = parseArtistJson(results)

      except Exception, e:
        pass
      
      return response

    def parseTrackJson(results):

        parsedResults = []

        for result in results['trackmatches']['track']:
            track_dict = {"title": result['name'], "link": result['url']}

            if 'image' in result:
                track_dict['thumbnail'] = result['image'][0]['#text']
                for i in range(1, len(result['image'])):	# If we have more images add them as well
                    track_dict[result['image'][i]['size'] + 'Image'] = result['image'][i]['#text']     
            else:
                track_dict['thumbnail'] = ''

            track_dict['artist'] = result['artist']
            track_dict['listeners'] = result['listeners']

            if result['streamable']['fulltrack'] == '0':	# Can we listen to the whole track
                track_dict['streamable'] = False 
            else:
                track_dict['streamable'] = True

            if result['streamable']['#text'] == '0': 		# Can we preview the track
                track_dict['preview'] = False
            else:
                track_dict['preview'] = True
            track_dict['summary'] = "'{0}' by {1}, with {2} listeners.".format(track_dict['title'], track_dict['artist'], track_dict['listeners'])
            parsedResults.append(track_dict)

        return parsedResults

    def parseAlbumJson(results):
        parsedResults = []

        for result in results['albummatches']['album']:
            track_dict = {"title": result['name'], "link": result['url']}

            if 'image' in result:
                track_dict['thumbnail'] = result['image'][0]['#text']
                for i in range(1, len(result['image'])):	# If we have more images add them as well
                    track_dict[result['image'][i]['size'] + 'Image'] = result['image'][i]['#text']     
            else:
                track_dict['thumbnail'] = ''

            track_dict['artist'] = result['artist']
            track_dict['id'] = result['id']

            if result['streamable'] == '0':	# Can we listen to this artists music?
                track_dict['streamable'] = False 
            else:
                track_dict['streamable'] = True

            track_dict['summary'] = "'{0}' by {1}.".format(track_dict['title'], track_dict['artist'])
            parsedResults.append(track_dict)

        return parsedResults

    def parseArtistJson(results):
        parsedResults = []

        for result in results['artistmatches']['artist']:
            track_dict = {"title": result['name'], "link": result['url'], "summary": ''}

            if 'image' in result:
                track_dict['thumbnail'] = result['image'][0]['#text']
                for i in range(1, len(result['image'])):	# If we have more images add them as well
                    track_dict[result['image'][i]['size'] + 'Image'] = result['image'][i]['#text']     
            else:
                track_dict['thumbnail'] = ''

            if result['streamable'] == '0':	# Can we listen to this artists music?
                track_dict['streamable'] = False 
            else:
                track_dict['streamable'] = True

            parsedResults.append(track_dict)

        return parsedResults


    # Try and get the API key from config, if it's not there raise an API Key error - the application will have to deal with this
    try:
      appId = self.service.config["last_fm_api_key"]
    except KeyError:
      raise ApiKeyError("LastFM", "last_fm_api_key")

    # Now that an API key has been supplied try to get results from the search engine itself
    try:
      pos = self._origin() + offset
      url = "http://ws.audioscrobbler.com/2.0/?method={0}.search&{0}={1}&api_key={2}&limit={3}&page={4}&format=json".format(self.source, urllib2.quote(query.search_terms), appId, int(self.resultsPerPage), pos)

      if self.artist and self.source == 'track':
          url += "&artist={0}".format(self.artist)
          
      data = urllib2.urlopen(url).read()
      results = json.loads(data)
      return parse_last_fm_json('LastFM', query.search_terms, results['results'], pos)

    # urllib2 - this catches http errors due to the service being down, lack of a proxy etc
    except urllib2.URLError, e:
      raise SearchEngineError("LastFM", e, errorType = 'urllib2', url = url)

	# Check for a value error with resultsPerPage
    except ValueError, e:
      note = "Please ensure that 'resultsPerPage' is an integer"
      raise SearchEngineError("LastFM", e, note = note, resultsPerPageType = type(self.resultsPerPage))

    # Check for a type error for offset or resultsPerPage
    except TypeError, e:
      note = "Please ensure that 'offset' and 'resultsPerPage' are integers if used"
      if isinstance(offset, int) == False:
          raise SearchEngineError("LastFM", e, note = note, offsetType = type(offset))

      if isinstance(self.resultsPerPage, int) == False:
          raise SearchEngineError("LastFM", e, note = note, resultsPerPageType = type(self.resultsPerPage))

	  raise SearchEngineError("LastFM", e, note = note)

    # Catch all exception, just in case
    except Exception, e:
      raise SearchEngineError("LastFM", e, url = url)