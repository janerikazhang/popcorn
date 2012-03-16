.. _repo:

The structure and the PuppyIR repository
==========================================================

The PuppyIR repository is organised, as most SVN repositories are, into three folders: trunk, branches and tags. Each of these folders is detailed below with a picture of their structure and a short description of the key parts contained within them.

To checkout the whole repository (this is a large download of ~600MB) and browse to the top level of the repository use the following commands:

::

  $ svn co https://puppyir.svn.sourceforge.net/svnroot/puppyir puppyir
  $ cd puppyir

N.B. the diagrams shown in this section are simplified, in that, except for a couple of exceptions, no files are shown; only folders. Also, standard Django application folders (like *'site_media'* - for example) are not shown in order to make the diagrams easier to read.

Trunk
----------------

This section is the main development area of PuppyIR, it contains the latest version of the framework and various applications (plus demonstrators) that make use of it. Following the diagram below, the key sections of trunk's contents are summarised.

.. figure::  images/trunk.png
   :align:   center

   *Diagram showing the structure of the 'trunk' folder in the repository.*

Framework
^^^^^^^^^

This folder contains the latest version of the framework, the test suite and the documentation (both the source and 'compiled' versions). The main sections of this part are summarised below in terms of their contents (see :ref:`service_architecture` for a conceptual description from the perspective of a search service based architecture):

* **build** and **setup.py**: are the build directory (for when installing the framework) and the Python script to install the framework.
* **puppy**: the framework itself, its components are detailed below.
    * **core**: contains a type checking system and also various components for running threads.
    * **docs**: the documentation for the framework, including the source and compiled versions in addition to a make file to build the source.
    * **interface**: contains an early version of a Django application for configuring a search service.
    * **logging**: contains the query and event loggers.
    * **misc**: contains assorted files regarding aspects like stylistic conventions for code in the framework.
    * **model**: contains all the classes associated with the OpenSearch standard.
    * **query**: contains all the filters and modifiers belonging to the query pipeline in addition to the associated exceptions. It also contains various query tokenizers.
    * **result**: contains all the filters and modifiers belonging to the result pipeline in addition to the associated exceptions.
    * **search**: contains all the search engine wrappers and associated exceptions.
    * **service**: contains the service manager and search service classes. It also contains early work on configurable versions of the aforementioned, but, since these are tied into Django - they are not automatically imported by the framework.
    * **tests**: an old legacy version of the test suite; the new version is detailed below and supersedes this one.
* **test** and **unit.py**: contains the test suite directory and the Python script for running the tests, please see: :ref:`the_puppyir_framework_test_suite` for details of this component.


Trunk/Demonstrators
-------------------

In the trunk there are two demonstrators which serve as showcases for the PuppyIR project; these demonstrators are described below.

Hospital Demonstrator
^^^^^^^^^^^^^^^^^^^^^

This demonstrator, also known as the Emma Search service (EmSe), is being built for Emma Kinderziekenhuis (EKZ), which is part of the Amsterdam 
Medical Centre (AMC). At the EKZ, children have access to a dedicated information centre as well as a dedicated bedside terminal. A user study carried out by hospital staff from the information centre has uncovered that children are reluctant to engage with the physical information centre (depending instead upon a family member or carer) and so, EmSe is designed to make use of these bedside terminals to allow them to access this resource via the web.

The motivators behind this demonstrator are, therefore, to: 

1. improve knowledge of existence and possibilities of the information centre; 
2. improve the accessibility of the information centre and its content for children; 
3. expand the information content with reference to more extensive information on the internet that is both appropriate and suitable for the various development stages of the children. 

EmSe assists the children by providing appropriate query suggestions, simplifying difficult content and filtering unsuitable content based on age appropriateness.

.. figure::  images/puppy-emse.png
   :align:   center

   *EmSe in action showing results from all the services; the dog's speech bubble is a query suggestion with the thought bubble containing more suggestions.*


Musueon Demonstrator
^^^^^^^^^^^^^^^^^^^^^^

The Museum Demonstrator creates an interactive museum visit using advanced  technologies such as multitouch tables and marker tracking, creating the basis for additional data retrieval and filtering using the PuppyIR framework. Up to four users can use a multitouch table simultaneously to browse through the different exhibition subjects and together they determine the contents of an interactive quest. 
  
Subsequently in a trail through the exhibitions users/players answer questions related to the chosen topics that have to be found. Throughout the museum various touch-screens equipped with scanners for reading and identifying the players are installed that when 
triggered present the questions and provide feedback to answers. 

After all questions have been answered, the multitouch table provides further information about the visited exhibits.

.. figure::  images/puppy-musueon.png
   :align:   center

   *The Musueon demonstrator being used on multitouch tables; showing various topics.*

You can view a video of this demonstrator in action by visiting: http://www.youtube.com/watch?v=b5zycfgqlKo

Prototypes
^^^^^^^^^^^^^^^^^^

This folder contains prototypes made using the latest version of the framework. These prototypes are either completed or in the late stages of development and so are all in a demonstrable state.

These prototypes are explained in: :ref:`prototypes` - please consult this page for more details.

Interfaces
^^^^^^^^^^^^^^^^^^

This folder contains the University of Strathclyde's experimental environment on collaborative search interfaces.

Branches
-------------------

This folder contains standalone components and unfinished/work-in-progress prototypes.

.. figure::  images/branches.png
   :align:   center

   *Diagram showing the structure of the 'branches' folder in the repository.*

Branches contains:

* **AnSe** this is an application that uses the PuppyIR framework to query, using the Bing and YouTube wrappers, and retrieve results in the JSON format. It is totally standalone as it contains its own, reduced, local copy of the PuppyIR framework.
* **conf demos (framework and hospital)** these are early versions of a method to allow for easy configuration of these resources.
* **Interns**: a application called 'sniffer' created by student interns working on PuppyIR, this application consists of: a search application similar to BaSe (see below for more on BaSe) and an automated logging application called ALF (Automated Logging Facility).
* **Student projects** this contains applications made by students studying the *Internet Technology* module at the University of Glasgow. At present it only contains the original version of the aMuSe application (the new versions, as detailed earlier, can be found in trunk) using an old version of the PuppyIR framework.
* **Teaching**: this folder contains various applications created (using the PuppyIR framework) as part of the *Internet Technology* course at the University of Glasgow to teach students about web development. The individual applications it includes are:
    * **BaSe**: a basic search engine that searches for and display web results.
    * **BaSe CSS**: same as BaSe but with CSS styling applied to it.
    * **BaSe Free CSS**: same as BaSe but with multiple different styles available and style switching code (in JavaScript).
    * **BaSe Ajax**: same as BaSe but it searches for, retrieves and displays web results using Ajax.
    * **BaSe Instant**: same as above but using code from a live in-lecture demo - no major differences to BaSe Ajax.
    * **TwiSe**: a basic twitter search engine for finding and displaying tweets.
    * **SeSu**: another alternate version of the now deprecated SeSu prototype.
    * **ImaSe**: a basic image search engine for finding and displaying images.
* **Working**: this folder contains prototypes that, while using the latest version of the framework, are still work-in-progress. These prototypes are described at the end of the 'branches' section.
    * **Deprecated**: these prototypes use an outdated local version of the framework (called 'util'). SeSu does not work anymore but JuSe does still function. Both applications and 'util' are no longer supported (however, SeSu has been remade and can be found in the 'trunk').

Work-in-progress prototypes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are several prototypes contained within the aforementioned 'working' folder. These prototypes provide further examples of how to use the framework but remain in-complete and as such, may contain flaws and/or not fully function.

* **aMuSeV4**: an application based around children retrieving image results and using these to create stories in a comic book style format. This application is, currently, very incomplete.
* **FiFi**: this folder is a placeholder for an application deployed on a server at Glasgow - http://pooley.dcs.gla.ac.uk:8080/fifi/
* **LSee**: an application allowing children to search for a location and, from this location, retrieve a mash-up of search results (image, video, tweets and news) taken from that location. LSee (Location Search) is, functionality wise, fairly well developed but the layout and styling is very basic.
* **YouSee**: YouSee is a web application designed to provide a fun, safe, environment for children to browse videos. Videos are presented in the form of carousels. Each carousel represents a category and contains a series of videos related to it. A child using YouSee can, watch a video and browse videos in the current carousel or change to a different one. Carousels are created for the children by their parent/guardian. This application is functionally almost complete but, interaction wise, the carousel browsing is in-complete - existing only in a temporary static form.

N.B. Once completed, these prototypes will be moved to **'trunk/prototypes'**.

Tags
---------------

This folder contains archived versions of the Hospital demonstrator (EmSe/Emma Search), the framework and the teaching applications (found in branches). These will only be of interest with respect to the evolution of the various parts and/or in the event of having to revert to a older version - for whatever reason.

.. figure::  images/tag.png
   :align:   center

   *Diagram showing the structure of the 'tags' folder in the repository.*