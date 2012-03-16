.. _faq:

Frequently Asked Questions
==========================================================

The following are questions regarding the usage of the PuppyIR framework; it will be added to and amended over time.

Why can't you limit the results from 'RelatedSearch' in Bing and BingV2
------------------------------------------------------------------------------------

Microsoft have not enabled the ability to limit the number of results - as in their other source-types (Web etc). It is, therefore, down to the developer to select a subset of these results if they wish to limit the results.

Why can't you you search for 'Videos' in the Bing wrapper?
------------------------------------------------------------------------------------

The 'Bing' wrapper uses the old version of Microsoft's Bing Search API; using the RSS/Atom feed output format. However, this version of the API does not support searching with the video source-type - 'BingV2' however, uses the latest version of the API (with JSON output) and allows searching with this source-type.

How does the offset affect which page, of results, is retrieved from a search engine wrapper?
---------------------------------------------------------------------------------------------

An offset is used, instead of a page number, because the number of the first page of results varies between search engines: some are 0-indexed and some 1-indexed. Therefore, in order to implement a generalised method the aforementioned offset is used with '0' retrieving the first page and '1' the second (i.e. go 1 page past the first page) etc.

What's the difference between YouTube/YouTubeV2 and which should I use?
------------------------------------------------------------------------------------

YouTube uses the old version of the YouTube API and allows for no customisation - via parameters like 'resultsPerPage'. Whereas, YouTubeV2, uses the latest version of the YouTube API which allows for greater customisation via a variety of options like 'resultsPerPage' and location based searching - see the API documentation for full details. So, if you want a basic search service use the 'YouTube' wrapper, but, if you want to customise your search service and take advantage of the new API features use 'YouTubeV2'.

What's the difference between Bing/BingV2 and which should I use?
------------------------------------------------------------------------------------

'Bing' uses the old version of the Bing Search API - without an API key - to search all the source types offered by Bing apart from videos. 'BingV2' uses the latest version of the API which allows for not only video searching but retrieval of multiple source types in one call (i.e. get Video and News results for query X). However, to use 'BingV2' you require an API key - this is a simple process of registering an application to get said key. 'BingV2' also allows for new filters to be used like only retrieving square images (amongst other options), again see API reference page for the full details. It is, therefore, like with the YouTube/YouTubeV2 wrappers, dependent upon the needs of the application being developed which one to use.
