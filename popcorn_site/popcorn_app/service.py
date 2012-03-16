import os, os.path
from puppy.service import ServiceManager, SearchService
from puppy.search.engine import Bing, BingV2, Twitter, YouTubeV2, Wikipedia
from puppy.model import Query, Response
#from puppy.search.engine.whooshQueryEngine import WhooshQueryEngine
#from puppy.query.filter.whooshQueryLogger import WhooshQueryLogger
from puppy.logging import QueryLogger
from puppy.query.filter import BlackListFilter

#from settings import ONDOLLEMAN, DOLLEMANPATH

log_dir = "popcorn_app/query_logs"

#if ONDOLLEMAN:
#    whoosh_dir = os.path.join(DOLLEMANPATH, "popcorn_app/query_logs/index")

#    log_dir = os.path.join(DOLLEMANPATH, log_dir)
#else:
#    whoosh_dir = os.path.join(os.getcwd(), "popcorn_app/query_logs/index")

config = {
 #"proxyhost": "http://wwwcache.gla.ac.uk:8080", # <-- remove if not UGLW
 "log_dir": log_dir,
 "bing_api_key": "FA5E0EB846B909111D77EDA50D180AD1145506B3",
}

# create a ServiceManager
service = ServiceManager(config)

# create a SearchService, called 'web_search'
web_search_service = SearchService(service, "web_search")

# Set our SearchService to use the Bing search engine (it defaults to search for web results)
web_search_service.search_engine = Bing(web_search_service)

# add SearchService to our ServiceManager (this handles all the search services MaSe contains)
service.add_search_service(web_search_service)
