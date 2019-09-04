.. image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/SofianeB/ECAS-B2SHARE/master?filepath=demo-ecas-ophidia%2Fecas-b2share.ipynb
 
.. image:: https://travis-ci.org/SofianeB/ECAS-B2SHARE.svg?branch=master
   :target: https://travis-ci.org/SofianeB/ECAS-B2SHARE 
    
.. image:: https://readthedocs.org/projects/ecas-b2share/badge/?version=latest
   :target: https://ecas-b2share.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
   
.. image:: https://badge.fury.io/py/ecasb2share.svg
    :target: https://badge.fury.io/py/ecasb2share
   
.. image:: https://coveralls.io/repos/github/SofianeB/ECAS-B2SHARE/badge.svg?branch=master
    :target: https://coveralls.io/github/SofianeB/ECAS-B2SHARE?branch=master

    
============
ECAS B2SHARE
============


Python module to interact with the B2SHARE HTTP REST API!

.. note::

   This module does not cover the whole B2SHARE API and is specific to the `ECAS use case <https://ee-docs.readthedocs.io/en/latest/>`_.


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
   client = Client(url, token_file)


Create a draft record
::

   client.create_draft_record_with_pid(title, pid)

Documentation
=============

For more details, please check the technical documentation `here <https://ecas-b2share.readthedocs.io/en/latest/>`_. 
