# -*- coding: utf8 -*-

import urllib2
import json

from puppy.search.engine.site import sitesearch
from puppy.search import SearchEngine
from puppy.model import Query, Response

from puppy.search.exceptions import SearchEngineError, ApiKeyError

class BingV2(SearchEngine, sitesearch):
  """
  Bing search engine wrapper for Version 2.X of the API - allowing for News, Web, Image and Video results to be retrieved

  One of the key advantages of using this wrapper is using the new features and also being able to use multiple sources to create a mash-up.
  i.e. source="Web+Image" gets results from the web and also image search services.

  You must include your application's Bing ID in your service manage config to use this service. It should be under the identifier "bing_api_key"

  If you are using the 'Spell' then you must set the 'market' parameter to match the language you are querying in i.e. English UK set Market to en-gb or Dutch set it to nl-nl

  Parameters:

  * source (str): what source the results should come from, valid options are: Web, News, Video, Image, Spell, RelatedSearch.

  * adult (str):  Strict is the default, not recommended to change this

  * market (str): For UK: en-GB, For Netherlands: nl-NL etc

  * resultsPerPage (int): How many results per page


  -- Image and Video Only Parameters --

  * filters (str): filter options split up by '+' you can only have one of each type see Bing API documentation for what these are


  -- Video and News Only Paramters --

  * sortBy (str): sort news by either 'Date' or 'Relevance'


  -- News Only Parameters --

  * newsCategory (str): what sort of news is wanted - see BingAPI for list of options, for example: 'rt_ScienceAndTechnology'

  """
    
  def __init__(self, service, source = 'Web', adult = 'Strict', market = 'en-GB', resultsPerPage = 8, filters = None, sortBy = None, newsCategory = None, sites=None, **args):
    SearchEngine.__init__(self, service, **args)
    sitesearch.__init__(self, sites)

    self.source = source
    self.adult = adult
    self.market = market
    self.resultsPerPage = resultsPerPage
    self.filters = filters
    self.sortBy = sortBy
    self.newsCategory = newsCategory

  def search(self, query, offset):
    """Search function for Bing V2 Search.
        
    
    Parameters:
    
    * query (puppy.model.Query)

    * offset (int): result offset for the search
    
    Returns:
    
    * puppy.model.Response
    
    Raises:
    
    * urllib2.URLError
    
    """
    
    def parse_bing_json(site, query, results, sources, pos):
      """Create a OpenSearch Response from Bing V2 results.
      
      Bing's search API returns results in JSON format. This function simply loads the JSON into memory and creates an equivalent representation that is OpenSearch compliant.
      
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
      response.feed.setdefault('link', results['link'])
      response.feed.setdefault('description', "Search results for '{0}' at {1}".format(query, site))
      response.namespaces.setdefault("opensearch", "http://a9.com/-/spec/opensearch/1.1/")
      try:
        response.feed.setdefault("opensearch_totalresults", int(results[self.source]['Total']))
        response.feed.setdefault("opensearch_itemsperpage", self.resultsPerPage)
        response.feed.setdefault("opensearch_startindex", pos )
      except KeyError:
        response.feed.setdefault("opensearch_totalresults", 0)
        response.feed.setdefault("opensearch_itemsperpage", 0)
        response.feed.setdefault("opensearch_startindex", 0)
      
      try:
        parsedResults  = []

        for sourceType in sources: # Go through every source type selected, parse its results and store them.
    
            sourceTypeResults = []

            if sourceType == 'Web':
                sourceTypeResults = parseWebJson(results)
            elif sourceType == 'News':
                sourceTypeResults = parseNewsJson(results)
            elif sourceType == 'Image':
                sourceTypeResults = parseImageJson(results)
            elif sourceType == 'Video':
                sourceTypeResults = parseVideoJson(results)
            elif sourceType == 'Spell':
                sourceTypeResults = parseSpellJson(results, query)
            elif sourceType == 'RelatedSearch':
                sourceTypeResults = parseRelatedSearchJson(results, query)

            for result in sourceTypeResults:
                response.entries.append(result) # Add the results to the response

      except Exception, e:
        pass
      
      return response

    def parseWebJson(results):

        parsedResults = []

        for result in results['Web']['Results']:
            result_dict = {}
            result_dict['title'] = result['Title']
            result_dict['link'] = result['Url']
            result_dict['datetime'] = result['DateTime'] # Last update to the site/result
            result_dict['summary'] = result['Description']

            if 'SearchTags' in result:
                result_dict['tags'] = result['SearchTags'] # Tags associated with this result
            else:
                result_dict['tags'] = ''

            deepLinks = [] # URL's associated with the main result i.e. news, about etc pages from the result

            if 'DeepLinks' in result: 
                for deepLink in result['DeepLinks']:
                    deeplink_dict = {'url': deepLink['Url'], 'title': deepLink['Title']}
                    deepLinks.append(deeplink_dict)

            result_dict['deepLinks'] = deepLinks
 
            parsedResults.append(result_dict)

        return parsedResults

    def parseNewsJson(results):

        parsedResults = []

        for result in results['News']['Results']:
            result_dict = {}
            result_dict['title'] = result['Title']
            result_dict['link'] = result['Url']
            result_dict['datetime'] = result['Date'] # When the news story was posted
            result_dict['summary'] = result['Snippet']
            result_dict['breakingNews'] = result['BreakingNews'] # 1 = yes, 0 = no

            # Related Searches
            relatedSearches = []

            if 'RelatedSearches' in result: 
                for relatedSearch in result['RelatedSearches']:
                    relatedSearch_dict = {'url': relatedSearch['Url'], 'title': relatedSearch['Title']}
                    relatedSearches.append(relatedSearch_dict)

            result_dict['relatedSearches'] = relatedSearches

            # Related News Collections
            
            relatedCollections = []
 
            if 'NewsCollections' in result: 
                for collection in result['NewsCollections']:
                    collection_dict = {}
                    if 'Name' in collection:
                        collection_dict['name'] = collection['Name']
                    articlesArray = []
                    if 'NewsArticles' in collection: # If we have articles in it
                        for article in collection['NewsArticles']: # Grab all the related articles in the collection
                            article_dict = {}
                            article_dict['title'] = article['Title']
                            article_dict['url'] = article['Url']

                            # The following fields are not always in related collection articles
                            if 'Date' in article:
                                article_dict['date'] = article['Date']

                            if 'Snippet' in article:
                                article_dict['summary'] = article['Snippet']

                            if 'Source' in article:
                                article_dict['source'] = article['Source']

                            articlesArray.append(article_dict)

                    collection_dict['articles'] = articlesArray
                    relatedCollections.append(collection_dict)

            result_dict['relatedCollections'] = relatedCollections

            parsedResults.append(result_dict)

        return parsedResults

    def parseImageJson(results):
    
        parsedResults = []

        for result in results['Image']['Results']:
            result_dict = {}
            result_dict['title'] = result['Title']
            result_dict['link'] = result['MediaUrl'] # Full Resolution Version
            result_dict['displayLink'] = result['DisplayUrl'] # Full Resolution Version - normally same as above
            result_dict['sourceLink'] = result['Url'] # Website the image is from
            result_dict['width'] = result['Width']
            result_dict['height'] = result['Height']
            result_dict['summary'] = "Image result for '{0}' from {1}".format(query, 'Bing Search Api')
            result_dict['thumbnail'] = result['Thumbnail']['Url']
            result_dict['thumbnailWidth'] = result['Thumbnail']['Width']
            result_dict['thumbnailHeight'] = result['Thumbnail']['Height']
            parsedResults.append(result_dict)

        return parsedResults

    def parseVideoJson(results):
    
        parsedResults = []

        for result in results['Video']['Results']:
            result_dict = {}
            result_dict['title'] = result['Title']
            result_dict['link'] = result['ClickThroughPageUrl']
            result_dict['sourceLink'] = result['PlayUrl'] # Original url - with YouTube results this often doesn't work
            result_dict['sourceTitle'] = result['SourceTitle'] # Title of website the video is from
            result_dict['summary'] = "Video result for '{0}' from {1}".format(query, result['SourceTitle'])
            result_dict['thumbnail'] = result['StaticThumbnail']['Url']
            parsedResults.append(result_dict)

        return parsedResults

    def parseSpellJson(results, query):
        parsedResults = []
     
        for result in results['Spell']['Results']:
            result_dict = {"title": "Spelling Suggestion for: '{0}'".format(query),  "link": ''}
            result_dict['summary'] = "Original query: '{0}'. Suggested correction of query: '{1}'.".format(query, result['Value']) 
            result_dict['suggestion'] = result['Value']
            parsedResults.append(result_dict)
        return parsedResults

    def parseRelatedSearchJson(results, query):
        parsedResults = []

        for result in results['RelatedSearch']['Results']:
            result_dict = {"title": result['Title'],  "link": result['Url']}
            result_dict['summary'] = "Search Suggestion of: '{0}' for the original query of: '{1}'.".format(result['Title'], query)
            parsedResults.append(result_dict)
        return parsedResults

    # Try and get the API key from config, if it's not there raise an API Key error - the application will have to deal with this
    try:
      appId = self.service.config["bing_api_key"]
    except KeyError:
      raise ApiKeyError("Bing Search API V2", "bing_api_key")
	
    # Now that an API key has been supplied try to get results from the search engine itself
    try:
      formattedQuery = urllib2.quote(query.search_terms)
      pos = self._origin()

      pos = pos + (offset * self.resultsPerPage)

      url = "http://api.search.live.net/json.aspx?Appid={0}&version=2.2&query={1}&sources={2}&market={3}&{2}.count={4}&adult={5}&{2}.offset={6}".format(appId, urllib2.quote(self._modify_query(query.search_terms)), self.source, self.market, self.resultsPerPage, self.adult, pos)

      sources = self.source.split('+')

      for sourceType in sources:

          # If we are using the image or video source type we can use filtering - i.e. only widescreen images or high res videos
          if(sourceType == 'Image') or (sourceType == 'Video'):
              if self.filters:
                  url += "&{0}.filters={1}".format(self.source, self.filters)

          # If we are sing Video or news we can sort the results
          if (sourceType == 'Video') or (sourceType == 'News'):
              if self.sortBy:
                  url += "&SortBy={0}".format(self.sortBy)

          # If we are using the news source type we can add the custom news paramters
          if sourceType == 'News':
              if self.newsCategory:
                  url += "&Category={0}".format(self.newsCategory)

      results = ''
    
      data = urllib2.urlopen(url).read()
      results = json.loads(data)
      results['SearchResponse'].setdefault(u'link', url)
      return parse_bing_json('Bing Search API V2', query.search_terms, results['SearchResponse'], sources, pos)

    # urllib2 - this catches http errors due to the service being down, lack of a proxy etc
    except urllib2.URLError, e:
      raise SearchEngineError("Bing Search API V2", e, errorType = 'urllib2', url = url)

    # Check for a type error for offset or resultsPerPage
    except TypeError, e:
      note = "Please ensure that 'offset' and 'resultsPerPage' are integers if used"
      if isinstance(offset, int) == False:
          raise SearchEngineError("Bing Search API V2", e, note = note, offsetType = type(offset))

      if isinstance(self.resultsPerPage, int) == False:
          raise SearchEngineError("Bing Search API V2", e, note = note, resultsPerPageType = type(self.resultsPerPage))

	  raise SearchEngineError("Bing Search API V2", e, note = note)

    # Catch all exception, just in case
    except Exception, e:
      raise SearchEngineError("Bing Search API V2", e, url = url)
