============
ECAS B2SHARE
============


Python module to interact with B2SHARE HTTP REST API!

.. note:: This module is not a B2SHARE client and is related to the ECAS use case.


How to install
==============

Using pip
::

   pip install ecasb2share


How to use
==========

Create a client
::

   from ecasb2share.ecasb2shareclient import EcasShare as Client
   client = Client()


Create a draft record
::

   client.create_draft_record(community_id, title, dataset_id)

Docs
====

Build the doc
::

    python setup.py build_sphinx