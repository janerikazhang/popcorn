.. _mase-mash-up-search-engine-puppyir-tutorial:

MaSe Tutorial: Mash-up Search Engine Application
=======================================================

Getting Started
---------------

Before starting this tutorial we assume that you have downloaded and installed the PuppyIR framework along with required associated Python Libraries (this tutorial also requires Whoosh to be installed).

If you have not installed the PuppyIR framework and/or Whoosh go to :ref:`requirements_and_installation` and get everything set up.

This tutorial is designed to show the PuppyIR framework can be used to create and customise a web application, quickly, using the Django web framework. No Python experience is required to do this tutorial, as there is minimal coding involved and there are instructions regarding what coding there is (failing that, an answer file is included called '*complete-service.py*' which includes working code for all the tasks).

Please note that Javascript must be enabled for this tutorial to work, ask your teacher if this is the case and, if not, get them to enable Javascript.

Downloading the Source Code for the Tutorial
++++++++++++++++++++++++++++++++++++++++++++

Now that you've got PuppyIR, Django and Whoosh installed it's time to download the latest release of the tutorial from the PuppyIR repository using the following command (if you have problems with this step please ask your teacher for help):

::

  $ svn co https://puppyir.svn.sourceforge.net/svnroot/puppyir/trunk/prototypes/mase-tutorial

N.B. depending on your OS and SVN version you may need to add ' mase-tutorial' to the end of the above command.

Run MaSe
++++++++

To run MaSe, execute the following two commands (substituting in the path to where you downloaded MaSe to):

::
  
  $ cd /path/to/mase-tutorial
  $ python manage.py runserver
  
Now, visit: http://localhost:8000/mase which should bring up the screen shown below (if you are using Internet Explorer you will not get rounded edges for your result boxes): 

.. figure::  images/mase-1-initial.png
   :align:   center

   *MaSe running on a local machine.*

To search for results either press enter/return in the search box or click on the magnifying glass.

You can customise your search engine by:

1. Clicking on the title, 'MaSe', allows you to change the name of the search engine by typing in a new name - pressing enter/return will save your search engine's new name.
2. Clicking on the paw images in the '**Colour your search engine**' box will change the colour theme of the search engine.
3. You can also move the result boxes around on the screen (more on this in the next section).
4. Minimise results by clicking on the '**-**' on the top right of a result box; you can maximise it again by clicking on the '**+**' that appears when results are minimised.

Go ahead and name your search engine and pick a new colour scheme - your new settings will be saved (using cookies; ask your teacher to enable cookies if they are disabled) so there is no need to do this every time.

Adding our first services
-------------------------

However, we don't have any services added yet, so, will get no results when searching. Let's fix that now by adding our first service: web results. Open the '*service.py*' file in the *mase* directory and add the following lines of code, at the bottom of the file(the code comments, the lines starting with '#', detail the purpose of each line) :

::

  # create a SearchService, called 'web_search'
  web_search_service = SearchService(service, "web_search")

  # Set our SearchService to use the Bing search engine (it defaults to search for web results)
  web_search_service.search_engine = Bing(web_search_service)

  # add SearchService to our ServiceManager (this handles all the search services MaSe contains) 
  service.add_search_service(web_search_service)

Now refresh your browser and search for something. You should be presented with results, for your query, in a format similar to what is shown below:

.. figure::  images/mase-3-web.png
   :align:   center

   *Our now customised MaSe (custom title and new colour scheme) showing web results.*

Now, lets limit the number of web results to only three, this is done by changing the line of code with '**Bing**' in it to:

::

  # Set the resultsPerPage parameter to 3; this limits the results the service will return
  web_search_service.search_engine = Bing(web_search_service, resultsPerPage = 3)

But, it's boring just having one set of results - so lets add images as well. This is done by adding the code below (note the differences and similarities to adding web results):

::

  # create a SearchService, called 'image_search'
  image_service = SearchService(service, "image_search")

  # Set our SearchService to use Bing but this time with images
  image_service.search_engine = Bing(image_service, source='image', resultsPerPage = 3)

  # add SearchService to our ServiceManager
  service.add_search_service(image_service)

Go ahead and search for something, you should now see images and web results. You can also drag your results around and place them either on the left, centre, or right result columns; an example of this is shown below:

.. figure::  images/mase-4-webimages.png
   :align:   center

   *Re-arranging 'Web' and 'Image' results in MaSe.*

Extending MaSe with query logging and suggestions
--------------------------------------------------

Now let's add a query logger to record our queries by adding the code below just after where we created (and added) the web search service:

::

  # Create a Whoosh Query Logger that records all the unique queries
  whoosh_query_logger = WhooshQueryLogger(whoosh_query_index_dir=whoosh_dir, unique=True)

  # Add the Whoosh Query Logger to the web_search service
  web_search_service.add_query_filter(whoosh_query_logger)

Next we want query suggestions, add the following lines of code to enable this feature:

::

  # create a SearchService, called 'query_suggest_search'
  suggest_service = SearchService(service, "query_suggest_search")

  # Use the Whoosh Query Engine to record queries
  whooshEngine = WhooshQueryEngine(suggest_service, whoosh_query_index_dir=whoosh_dir)
  suggest_service.search_engine = whooshEngine

  # add SearchService to our ServiceManager
  service.add_search_service(suggest_service)

What the '*suggest_service* does is to look at past queries and see if any of them contain terms from the current query. If so, it recommends those past queries as suggestions. The picture below shows query suggestions in action. Go ahead and enter a few queries now; to test if the query suggestions are working.

.. figure::  images/mase-5-limitresults.png
   :align:   center

   *MaSe showing our now limited results for each service and query suggestions.*

Filtering and the Pipelining
--------------------------------------------------

Now that we've got results from three sources, lets add some filtering to stop people using your search engine to search for certain keywords. After the creation of the web_search_service, add the following lines of code to add a '**BlackListFilter**': 

::
  
  # Create a blacklist filter to block queries containing the terms below
  query_black_list = BlackListFilter(terms = "bad worse nasty filthy")

  # Add our blacklist filter to the web search service
  web_search_service.add_query_filter(query_black_list)

You will notice that if you type in "bad query", you still get results for the image service. This is because we didn't add the '**BlackListFilter**' to our '*image_service*'. Do that now and make sure nothing nasty gets through.

Also, if we added the '**WhooshQueryLogger**' before the '**BlackListFilter**' then we would record all the nasty queries before rejecting the query and then start to recommend them as suggestions.... ooops! So it is always a good idea to pay attention to your query and document pipelines - re-order these now to stop any bad suggestions being recommended.


.. figure::  images/mase-6-badsuggestions.png
   :align:   center

   *MaSe making bad suggestions and still showing image results; as in this case the filter was not added to image search*

Experimenting
--------------------------------------------------

Well done, that's you completed the tutorial :) - what's next is up to you, if you want to do more the following two sections contain details for suggestions for extending your search engine further.

Other Services
++++++++++++++

So far you've added images, web and query suggestions to MaSe but there's more available.

The table below details the other options (see the code for '*web_search_service*' and adapt it using the details below):

+-----------------+-----------------+-----------------+-----------------+
| Result Source	  | Service Name    | Class Name      | Extra parameters|
+=================+=================+=================+=================+
|   Wikipedia     |  *wiki_search*  | **Wikipedia**   |                 |
+-----------------+-----------------+-----------------+-----------------+
|   Bing News     |  *news_search*  | **Bing**        | source='news'   |
+-----------------+-----------------+-----------------+-----------------+
| Video (Youtube) | *video_search*  | **YouTubeV2**   |                 |
+-----------------+-----------------+-----------------+-----------------+
|     Twitter     | *twitter_search*| **Twitter**     |                 |
+-----------------+-----------------+-----------------+-----------------+

If you get stuck adding the above services then look at the file '*service-complete.py*' which includes working code to add them.

You can also add in past queries with the following code (change 'web_search_service' to whatever service to want to log queries for):

::
 
  # Log queries sent to the web search service
  web_search_service.query_logger = QueryLogger(web_search_service, log_mode=0)

.. figure::  images/mase-7-all.png
   :align:   center

   *MaSe with all the different result types added to it.*

The picture above shows what MaSe looks like with all the above services added to it with the results limited to only show the top result.

Other Parameters
++++++++++++++++

There are also a few other parameters you can try out for the video and twitter services beyond 'resultsPerPage':

* **Video** orderBy (string), can be: 'rating', 'viewCount' or 'relevance'

* **Twitter** language (string), 'en' for English, 'de' for German; type (string), can be: 'mixed', 'recent' or 'popular'