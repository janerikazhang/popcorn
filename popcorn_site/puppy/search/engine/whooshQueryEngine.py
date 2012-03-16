# -*- coding: utf8 -*-
from puppy.search import SearchEngine
from puppy.model import Query, Response
from whoosh.index import open_dir
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh import highlight

class WhooshQueryEngine(SearchEngine):
    """
    Whoosh Query log search engine.

    Parameters:

    * resultsPerPage (int): select how many results per page

    * whoosh_query_index_dir (str): the absolute path for where you want queries indexed at
    """
  
    def __init__(self, service, whoosh_query_index_dir = "", resultsPerPage = 8, **args):
        super(WhooshQueryEngine, self).__init__(service, **args)
        self.resultsPerPage = resultsPerPage
        print "In construction of Whoosh Query log search engine"   
        try:
            self.queryIndex = open_dir( whoosh_query_index_dir )
            print "Whoosh query index open"
            print  self.queryIndex.doc_count()
        except:
            print "Could not open Whoosh query index at: " + whoosh_query_index_dir
  
    def search(self, query, offset):
        """
        Search service for query log data held in a Whoosh query index
        with a Schema(title=ID(unique=True, stored=True), content=TEXT(stored=True), ncontent=NGRAM(stored=True), issued=DATETIME(stored=True))
    
        Parameters:
  
        * query (puppy.model.Query)

        * offset (int): result offset for the search
  
        Returns:
  
        * results puppy.model.Response
  
        Raises:
  
        * ?  
        """
        def parse_whoosh_trec(site, query, results):
            response = Response()
            response.version = 'trec'
            response.feed.setdefault('title', "{0}: {1}".format(site, query))
            response.feed.setdefault('link','')
            response.feed.setdefault('description',"Search results for '{0}' at {1}".format(query, site))
            response.namespaces.setdefault("opensearch", "http://a9.com/-/spec/opensearch/1.1/")
            response.feed.setdefault("opensearch_totalresults", len(results) )
            response.feed.setdefault("opensearch_itemsperpage", len(results))
            response.feed.setdefault("opensearch_startindex", 1)
            response.feed.setdefault('query', query)
            try:
                if len(results)>1:
                    resultNum = 1
                    for hit in results:
                        if resultNum > self.resultsPerPage:
                            break
                        title = hit["title"]
                        link = "?query=" + title.replace(' ','+')
                        desc = hit.highlights("content")                        
                        response.entries.append({'title': title, 'link': link, 'summary': desc })
                        resultNum += 1
                    else:
                        print "No hits found for query: " + query
            except Exception, e:
                print "Converting results to OpenSearch Failed"
            return response
            # end parse_whoosh_trec
          
        try:
            parser = QueryParser("content", self.queryIndex.schema)
            print query.search_terms
            myquery = parser.parse( query.search_terms  )
            results = []
            reponse = []
            with self.queryIndex.searcher() as searcher:
                results = searcher.search( myquery )
                results.fragmenter = highlight.ContextFragmenter(surround=40)
                results.formatter = highlight.UppercaseFormatter()
                print "WhooshQueryEngine found: " + str(len(results)) + " results"
                response = parse_whoosh_trec('WhooshQueryEngine', query.search_terms, results)
            return response
        except:
            print "Error in Search Service: Whoosh query search failed"
