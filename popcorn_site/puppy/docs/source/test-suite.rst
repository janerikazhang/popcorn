.. _the_puppyir_framework_test_suite:

The PuppyIR Framework Test Suite
======================================

The PuppyIR framework comes with an in-built test suite; for creating unit tests for all its components. The two main tasks are detailed below, briefly, and then discussed in the following sections.

Create a test (where <module> is the name of the Python file the test is for):

::

  $ cd /path/to/framework
  $ python unit.py create <module>

Run all tests:

::

  $ cd /path/to/framework
  $ python unit.py run 

Create
------

Creates a skeleton test file placed at a mirror location (a structure that mirrors the framework's module structure) in the test hierarchy.

For example:

::

  $ cd /path/to/framework
  $ python unit.py puppy/query/filter/cool_filter.py

We now see, from framework's root directory, a new file at: test/puppy/query/filter/cool_filter.py - with the following auto-generated code:

::

  from puppy.query.filter.cool_filter import *

  import unittest


  class TestCoolFilter(object):
      pass

  if __name__ == '__main__':
      unittest.main()

It is now ready to be used and it is up to the programmer to write tests for the component in question.

Run
---

This command searches for all the current test cases and runs them. Issues are reported at the end; nothing is outputted if a test succeeds.

If you are using a proxy server, there are two options: either use the in-built proxy system using a ServiceManager (via it's config variable) or write a work-around for your tests or they will all fail (due to proxy errors; unless, of course, you are testing a component that does not require access to the internet via aforementioned proxy).

Example: Testing the Blacklist Filter
-------------------------------------

To provide an example, the code below shows a test for the Blacklist query filter (this rejects queries with blacklisted words in them). What this code does is check that queries with blacklisted words are actually being rejected and that valid queries are not rejected.

::

  from puppy.query.filter.blacklistfilter import *

  import unittest


  class TestBlacklistfilter(unittest.TestCase):
      def test_main(self):
          t = BlackListFilter(terms='bad')
          self.assertTrue(t.filter(Query('hello')))
          self.assertTrue(t.filter(Query('friends')))
          self.assertFalse(t.filter(Query('bad friends')))
          self.assertFalse(t.filter(Query('bad hello')))


  if __name__ == '__main__':
      unittest.main()