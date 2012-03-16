.. _overview:

Overview and background of the PuppyIR Framework
================================================

The framework is part of the PuppyIR project [#f1]_, funded by the European Union, which is investigating children's information retrieval (IR). The project's long term goal is to work towards universal access of information for both children and adults. As part of this, the framework is being developed as a suite of tools to assist developers and researchers in rapidly developing interaction IR applications for children.

In summary, it aims to:

1. Simplify the process of building interactive IR services;
2. provide a disparate and extensive suite of components, specifically tailored for children;
3. incorporate current research findings in children's IR;
4. be highly extensible (in all the main sections, and their respective components, of the framework), so that the framework can be adapted for an applications specific needs;
5. and, to provide extensive documentation [this document] with tutorials detailing how to use, extend and customise all the different parts of the framework.

The main features of the framework
**********************************

In this Chapter, the key functionalities of the framework are introduced and discussed; links are provided to the Chapters that provide more detailed commentary (and examples) of each functionality discussed here. To accomplish the aims listed above, the framework offers a developer, or researcher, a large variety of functionalities and associated components. These are split up into several distinct sections of the framework (for a full list, of all the individual components in these sections, please see consult the :ref:`api`).

Data Formatting
------------------------------

PuppyIR provides a standardised format for both queries and the results of a search, called a response. This is so that all the components are able to interoperate and also because having this consistency, makes it easier for developers/researchers to make use of these elements in their applications. This standardised format is an implementation of the `OpenSearch Standard <http://www.opensearch.org/Specifications/OpenSearch/1.1>`_ and the frameworks model of them can be found in PuppyIR's 'query' and 'response' classes; which are used by all the components that deal with such data. Many search services and API's support this standard, but, in some cases, some processing is required - in order to present data in a form that it is compliant with the OpenSearch standard (there are many examples of this processing in the framework's search engine wrappers).

Architectural Paradigms
------------------------------

There are two paradigms, included with the framework, for developers/researchers to use to build PuppyIR based applications, these are:

1. **One Pipeline, One Search Engine (Search Service)**: this is the standard (in terms of prototype and demonstrator adoption) paradigm for creating PuppyIR based applications. In it, a unique query and result pipeline is created for each search service. A search service is then linked to a source, i.e. a search engine wrapper like Bing or YouTube so that it can retrieve and process results. See: :ref:`service_architecture` for a more in-depth discussion of this paradigm.
2. **One Pipeline, Many Search Engines (Pipeline Service)**: an alternative to the search service paradigm, where only one query and result pipeline is created, various search engine wrappers can the be associated with the pipeline (defined by the pipeline service). Either search all, or search specific (i.e. search a specific search engine wrapper associated with the pipeline service) can be used to retrieve results using the defined query & result pipelines. See: :ref:`pipeline_architecture` for a more in-depth discussion of this paradigm.

A developer/researcher can select the paradigm that is most suited to their application; no matter which one is used, the same components and options (for configuring them) are available. This is due to all the components being generalised, in terms of their: interface, methods and parameters. All of the paradigms, however, make use of the 'query' and 'response' formats as mentioned earlier (however, the a pipeline service returns 'response' objects in a slightly different way).

Event and Query Logging
------------------------------

Included with the framework are two kinds of logger, both of these are designed to assist developers and researchers in evaluating their applications, they are: (1) a query logger and (2), an event logger. Between these two kinds of logger, any kind of data required to be logged can be, for evaluation/analytical purposes.

Both the Search and Pipeline Services provide the ability to log queries, sent to the service in question, by a user. It is possible to log such queries at two distinct stages:

1. **Un-processed**: the query passed to the service in question before it goes through the query pipeline.
2. **Processed**: the query after it has gone through the pipeline (assuming it was not rejected during processing), for example it may have been extended via new terms being appended or spelling mistakes automatically being corrected.

This allows two key areas to be investigated: (1) what sort of queries the users are sending and (2), the results of the query pipeline(s), defined in the application, on these queries.

The event logger provides a developer with a component that allows them to log only the details they wish (for the event being logged) to be logged for their specific application. This is possible via a keyword arguments parameter to the log method. However, an 'identifier' and 'type' must be supplied in order to differentiate the different events and assist with categorisation for analysis of the log file(s).

Query and Result Filters
------------------------------

Filters in both the Query and Result pipelines are components which decide whether or not to accept a specific result (in a response) or a query - depending upon which pipeline it belongs to.

Query and Result Modifiers
------------------------------

Search Engine Wrappers
------------------------------

Testing and Exception Handling
------------------------------

Extensibility of the framework
*******************************

As stated in the aims detailed earlier, the extensibility of the framework and its components is a key aspect of its design. In is possible to add, customise and extend all of the components, discussed above, for use in a PuppyIR based application. However, several distinct areas have been selected to be written up for this document, i.e. the process for going about adding new components is detailed. These areas were identified as being the most likely for developers/researchers to wish to extend and are described briefly below.

Search Engine Wrappers
--------------------------

It is expected that the area, of the framework, especially, is one with great potential for future expansion and development. This is due to the inevitable influx of new API's and updates to the ones currently supported by the PuppyIR framework. The section detailing this area, therefore, looks at how to write new wrappers that are compatibly both with the architectural paradigms as well as the other components that interact with search engine wrappers (i.e. filters etc). See: :ref:`extending_the_search_engine` for more details on this.

Query and Result Filters
--------------------------

Query and Result Modifiers
--------------------------

Other features and framework support
************************************

Which version of Python is the framework for?
---------------------------------------------

The PuppyIR framework is designed, built and maintained using Python 2.7; Python 3.x is not supported and earlier versions may have compatibility issue. It is, therefore, recommended to upgrade to Python 2.7 rather than using earlier versions. For details of some of the known Python compatibility issues please consult the :ref:`issues` page.

Standalone Services
-------------------

The PuppyIR framework can be used to build a standalone service for research and development purposes.  This mode has minimal requirements and simplifies the process of building custom search services that do not require a user interface. See :ref:`building-a-standalone-puppyir-service` for more information.

Proxy Server Support
--------------------

Many workplaces and research institutions use a proxy server and so, any applications created, using PuppyIR, would need to go through such a proxy server. The framework, therefore, offers a simple interface for its components that enables developers/researchers to easily set-up the components they are using to work with a defined proxy server. The code below shows how to create a service in both the paradigms, included with the framework:

::

  # Set-up a config setting for a proxy server
  config = {"proxyhost": "http://your-proxy-server-address"}

  # -- Paradigm 1 and proxy servers -- 
  # ----------------------------------

  # Create a service manager and set it to use config
  sm = ServiceManager(config)

  # Create a search service for Bing Web
  ss = SearchService(sm, "bing_web")

  # Set our new search service to use the Bing wrapper
  ss.search_engine = Bing(ss)

  # Add new search service to ServiceManager
  sm.add_search_service(ss)

  # -- Paradigm 2 and proxy servers --
  # ----------------------------------

  # Create a Pipeline Service called 'myPipeline' using config
  pipelineService = PipelineService(config, "myPipeline")

  # Create a Bing search engine wrapper
  bing = Bing(pipelineService)

  # Add Bing to our search engine manager (this stores all our search engines)
  pipelineService.searchEngineManager.add_search_engine("Bing", bing)

Django support
--------------

The PuppyIR framework can be integrated with the Django web application framework to provide a toolkit for rapidly prototyping and deploying search services for children on the web.  PuppyIR includes a number of components that augment the existing Django functionality. See :ref:`building-a-puppyir-django-service` for more information.

N.B. Django is provided as an example, the framework can also work with other Python based web application frameworks as no parts of the framework are tied into Django.

.. [#f1] For more details about the PuppyIR project, please visit the project's website at: http://www.puppyir.eu/