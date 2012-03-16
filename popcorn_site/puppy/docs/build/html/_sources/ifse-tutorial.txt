.. _information-foraging-puppyir-tutorial:

IfSe Tutorial: Information Foraging Search Application
=============================================================

Getting Started
---------------

To start this tutorial we assume that you have downloaded and installed the PuppyIR framework along with the associated Python Libraries (the later sections of this tutorial require Whoosh to be installed).

If you have not installed the PuppyIR framework or Whoosh go to :ref:`requirements_and_installation` and get everything set up.

This tutorial is designed to give you an idea of how the PuppyIR framework can be used in conjunction with Django to quickly and easily create web based search services. 

To take full advantage of the framework we would highly recommend learning Python and becoming familiar with Django, however, we have also designed this tutorial so that minimal coding is required. In fact, all the lines of code needed are provided below in a step-by-step guide.

Downloading the Source Code for the Tutorial
********************************************

Download the latest release of the tutorial from the PuppyIR repository:

::

  $ svn co https://puppyir.svn.sourceforge.net/svnroot/puppyir/trunk/prototypes/ifse-tutorial

N.B. depending on your OS and SVN version you may need to add ' ifse-tutorial' to the end of the above command.

Run IfSe
********

::
  
  $ cd /path/to/ifse-tutorial
  $ python manage.py runserver
  
Visit http://localhost:8000/ifse this should bring up interface below.

.. figure::  images/puppy-ifse-before.png
   :align:   center

   *IfSe running on a local machine.*

Excellent! You now have a simple search interface that is hooked up to the Bing search API. 

Go on, try it out. Search for something! 

While, this service means you can search the web, it doesn't record anything.

Logging Queries
---------------

Let's assume that we'd like to keep track of all the queries that users submit so that we can do a query log analysis later on.

There are a number of ways to do this. But let's do it the simple way first.

Load up a code editor and open up ``ifse/service.py`` 

This is where we can specify how we would like to configure our search service. We can easily add and modify search engines, query filters and result filters. See :ref:`api` for more information.

The PuppyIR framework provides a default query logger, lets include it by adding the following lines of code:

::

  from puppy.logging import QueryLogger

This is a file based query logging. To tell PuppyIR where to store the log we need to add a "log_dir" to the config:

::

  config = {
      "log_dir": "ifse/query_logs",
  }

After the declaration and creation of the ``web_search_service``, add the following line of code:

::

  web_search_service.query_logger = QueryLogger(web_search_service, log_mode=0)

This tells PuppyIR that you would like log queries that are submitted to this search service. 

Too Easy!

Now, make sure the server is still running, i.e. python manage.py runserver and visit http://127.0.0.1:8000/ifse 

Type in a few queries. 

Now, go and check the directory ``ifse/query_logs``, you should have a file in there called, ``web_search_query_log``. This will contain a list of the queries that you have just entered. I hope you didn't type in any naughty queries!

Modifying Queries
-----------------

Part of the PuppyIR project is to create child friendly services. So lets add a QueryFilter that stops naughty query terms being submitted to the search engine. To do this, we can use the ``BlackListFiter`` component that is part of the PuppyIR framework. Now add the following line of code to import it:

::
  
  from puppy.query.filter import BlackListFilter

Then after the declaration and creation of the web_search_service, add the following lines of code: 

::
  
  query_black_list = BlackListFilter(0, terms = "bad worse nasty filthy")
  web_search_service.add_query_filter(query_black_list)

What the Blacklist filter does, is, look at the query sent to the PuppyIR framework and check each word contained in it (the query) against the blacklist. The blacklist defines words that are not allowed (in the code example above the blacklist is populated via the second parameter; separated by spaces). If your query contains any of these words then the query will be rejected and a message displayed stating this.

Try the service now. Enter a really naughty query, like "bad test" and see what happens. A message should be displayed stating that the query was rejected because it contained blacklisted words.

Adding Another Search Service
-----------------------------

Instead of just returning web results, we might want to all add in other kinds of results. PuppyIR also contains various other search engine wrappers to APIs other than Bing, such as: Twitter, Yahoo, etc. For more details about search engine wrappers see :ref:`api`

Let's create a new search service, so that we can include Twitter results as well as web results. To do this add the following line of code:

::

  from puppy.search.engine import Twitter

And then declare and create this new SearchService and search engine, with:

::

  twitter_search_service = SearchService(service,"twitter_search")
  twitter_search_service.search_engine = Twitter(twitter_search_service)

Don't forget to add it to the PuppyIR service manager, which is called service:

::

  service.add_search_service(twitter_search_service)


Okay, let's try the service out now. When you enter a query now, it should return two panes of results: first, the web results and then the twitter results. 

Wow! How cool is that?

More Querying Logging
---------------------

The query logger above simply dumps all the queries entered to a flat file. While this is really handy to process afterwards, it would be nice if we could index all the queries and then present similar queries as query suggestions.

To do this we need two include two components, a ``QueryFilter`` that records and indexes queries submitted to the service, and a ``SearchService`` that recommends queries. Luckily we have already implemented a simple query indexing ``QueryFilter`` that uses the Python based Whoosh indexer. The filter is called, ``WhooshQueryLogger``, while the search engine is called ``WhooshQueryEngine``. Let's import then into our ``service.py``:

::

  from puppy.query.filter.whooshQueryLogger import WhooshQueryLogger
  from puppy.search.engine.whooshQueryEngine import WhooshQueryEngine


Now create the ``WhooshQueryLogger``. It will need the full path name to the index directory. And then it needs to be added to the ``search_service`` that we wish to log, so here we can log the ``web_search_service``:

::

  whoosh_dir = os.path.join(os.getcwd(), "ifse/query_logs/index")
  whoosh_query_logger = WhooshQueryLogger(whoosh_query_index_dir=whoosh_dir, unique=True)
  web_search_service.add_query_filter(whoosh_query_logger)

Now, we want to provide the suggestions, so we need to create a SearchService for query suggestions and then create the WhooshQueryEngine, which also needs to know the location of the index directory:

::

  suggest_service = SearchService(service, "query_suggest_search")
  whoosh_engine = WhooshQueryEngine(suggest_service, whoosh_query_index_dir=whoosh_dir)
  suggest_service.search_engine = whoosh_engine
  service.add_search_service(suggest_service)

Okay, so let's start entering a few queries. Note, you might have to enter a few queries before you start to see recommendations appearing.

Pipelining
---------------

You might notice that if you type in "bad query", you still get results for the twitter service. This is because we didn't add the ``BlackListFilter`` to our ``twitter_search_service``. Do that now and make sure nothing nasty gets through.

Also, if we added the ``WhooshQueryLogger`` before the ``BlackListFilter`` then we would record all the nasty queries before rejecting the query and then start to recommend them....ooops! So it is always a good idea to pay attention to your query and document pipelines.


Give IfSe a Style
-----------------

If you are interested in changing the look and feel of the application, then you can check out the html template files in ``templates/ifse/`` within the tutorial directory, and the corresponding style sheet held in, ``site_media/css/``

For example, open up ``index.html`` in ``template/ifse`` and change:

::
  
  <link href="{{ MEDIA_URL }}css/concurrence/style.css" rel="stylesheet"  type="text/css">

to:

::

  <link href="{{ MEDIA_URL }}css/twirling/style.css" rel="stylesheet"  type="text/css">

Doesn't IfSe look prettier in pink? 

Try changing ``perplex`` to ``combination``, ``passageway``, ``twirling`` or download any other CSS style from 
`<http://freecsstemplates.org>`_.

Summing Up
---------------
In this tutorial, we have only considered how to configure a service using some of the existing components within the PuppyIR framework. But it is really easy to develop your own components and customise your search service. To develop your own components, check out :ref:`extending_the_query_pipeline`, :ref:`extending_the_result_pipeline` and :ref:`extending_the_search_engine` for more details.