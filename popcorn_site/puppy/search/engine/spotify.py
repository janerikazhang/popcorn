# -*- coding: utf8 -*-

import urllib2
import json

from puppy.search import SearchEngine
from puppy.model import Query, Response

from puppy.search.exceptions import SearchEngineError

class Spotify(SearchEngine):
  """
  Spotify search engine.

  Parameters:

  * resultType (str):  what result type should be returned, the options are: 'tracks', 'albums', 'artists'

  """
    
  def __init__(self, service, resultType = 'tracks', **args):
    super(Spotify, self).__init__(service, **args)
    self.resultType = resultType

  def _origin(self):
    """ This overrides SearchEngine's default origin (for results from a search engine) for Spotify """
    return 1
    
  def search(self, query, offset):
    """Search function for Spotify Search.
        
    
    Parameters:
    
    * query (puppy.model.Query)
    
    Returns:
    
    * puppy.model.Response
    
    Raises:
    
    * urllib2.URLError
    
    """
    
    def parse_spotify_json(site, query, results):
      """Create a OpenSearch Response from Spotify results.
      
      Spotify's search API returns results in JSON format. This function simply loads the JSON into memory and creates an equivalent representation that is OpenSearch compliant.
      
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
        response.feed.setdefault("opensearch_totalresults", int(results['info']['num_results']))
        response.feed.setdefault("opensearch_itemsperpage", int(results['info']['limit']))
        response.feed.setdefault("opensearch_startindex", int(results['info']['page']))
      except KeyError:
        response.feed.setdefault("opensearch_totalresults", 0)
        response.feed.setdefault("opensearch_itemsperpage", 0)
        response.feed.setdefault("opensearch_startindex", 0)
      
      try:
        if self.resultType == 'tracks':
            response = parse_tracks_json(response, results)
        elif self.resultType == 'albums':
            response = parse_albums_json(response, results)
        elif self.resultType == 'artists':
            response = parse_artists_json(response, results)
      except Exception, e:
        pass
      
      return response

    def parse_tracks_json(response, results):
      for result in results['tracks']:
        track_dict = {}
        track_dict['title'] = result['name']
        track_dict['link'] = result['href']
        track_dict['trackNumber'] = result['track-number']
        track_dict['length'] = result['length']
        artists = []
        for artist in result['artists']:
            artists_dict = {'name': artist['name'], 'link': artist['href']}
            artists.append(artists_dict)
        track_dict['artists'] = artists
        track_dict['album'] = {'name': result['album']['name'], 'year': result['album']['released'], 'link': result['album']['href']}
        track_dict['summary'] = 'Monkey'
        track_dict['popularity'] = result['popularity']
        response.entries.append(track_dict)
      return response

    def parse_albums_json(response, results):
      for result in results['albums']:
        album_dict = {'title': result['name'], 'link': result['href'], 'summary': '', 'popularity': result['popularity']}
        artists = []
        for artist in result['artists']:
            artists_dict = {'name': artist['name'], 'link': artist['href']}
            artists.append(artists_dict)
        album_dict['artists'] = artists
        response.entries.append(album_dict)
      return response

    def parse_artists_json(response, results):
      for result in results['artists']:
        response.entries.append({'title': result['name'], 'link': result['href'], 'summary': '', 'popularity': result['popularity']})
      return response

    try:    
      pos = self._origin() + offset
      serviceName = self.resultType[:len(self.resultType) - 1]
      url = "http://ws.spotify.com/search/1/{0}.json?q={1}&page={2}".format(serviceName, urllib2.quote(query.search_terms), pos) 
      data = urllib2.urlopen(url).read()
      results = json.loads(data)
      return parse_spotify_json('Spotify', query.search_terms, results)

    # urllib2 - this catches http errors due to the service being down, lack of a proxy etc
    except urllib2.URLError, e:
      raise SearchEngineError("Spotify", e, errorType = 'urllib2', url = url)

    # Check for a type error for offset or resultsPerPage
    except TypeError, e:
      note = "Please ensure that 'offset' is an integer if used"

      if isinstance(offset, int) == False:
          raise SearchEngineError("Spotify", e, note = note, offsetType = type(offset))

	  raise SearchEngineError("Spotify", e, note = note)

    # Catch all exception, just in case
    except Exception, e:
      raise SearchEngineError("Spotify", e, url = url)