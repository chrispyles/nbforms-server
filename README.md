# Okpy Test Generator

[![Build Status](https://travis-ci.org/chrispyles/okpy-test-generator.svg?branch=master)](https://travis-ci.org/chrispyles/okpy-test-generator) [![codecov](https://codecov.io/gh/chrispyles/okpy-test-generator/branch/master/graph/badge.svg)](https://codecov.io/gh/chrispyles/okpy-test-generator)

This is the source code for a Heroku-deployed webapp that generates Python test cases in ok format. This test format is used in various autograders, including [otter-grader](https://github.com/ucbds-infra/otter-grader), [okpy](https://github.com/okpy/ok), and [gofer-grader](https://github.com/data-8/gofer-grader).

The generator is at [https://oktests.herokuapp.com](https://oktests.herokuapp.com).

## Changelog

**v0.3.1:**

* Removed extraneous code

**v0.3.0:**

* Added Cucumber tests
* Added Travis CI and Codecov

**v0.2.0:**

* Changed "Copy to Clipboard" button to "Download" button

**v0.1.1:**

* Fixed bug where last test case was not included in output
* Reorganized `lib/test.rb` so that fewer abstraction barriers are violated

**v0.1.0:**

* Added hidden and locked test cases
* Added scoring and points to suites

**v0.0.1:**

* Initial release!
