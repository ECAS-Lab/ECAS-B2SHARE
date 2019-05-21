
Sharing with B2SHARE
====================


.. image:: https://raw.githubusercontent.com/SofianeB/ECAS-B2SHARE/master/demo-ecas-ophidia/ecas-b2share.png
    :alt: ECAS B2SHARE


`B2SHARE <https://b2share.eudat.eu>`_ is a user-friendly, reliable and trustworthy way for researchers, scientific communities and citizen scientists to store and share small-scale research data from diverse contexts.

In the context of ECAS, B2SHARE is integrated for two major reasons:

* enable publishing of results (data, notebooks, etc) directly from the **ECAS** environment
* enhance research reproducibility

Sharing data from ECAS to B2SHARE is performed using the `ecasb2share <https://github.com/SofianeB/ECAS-B2SHARE>`_ Python library. The library is already installed in each user environment and
can be called directly from the jupyter notebook.
It helps to create draft records with minimal metadata and upload different types of files.

.. note:: After the creation of a draft record, it is recommended to switch to the B2SHARE graphical user interface to check the correctness of the metadata and submit request for publication.
          These features are available in the user workspace.

.. note:: The ECAS-B2SHARE python client covers only the mandatory steps when creating new records in B2SHARE.
          Please consult `user documentation <https://eudat.eu/services/userdoc/b2share-usage>`_ for more details about the service.

In B2SHARE there are different research communities to store the records.
An extra community has been added to cover the ECAS use case with a specific metadata schema.


============
Requirements
============

In order to upload and share ECAS data with B2SHARE, users need to register for an account.
Please use this `link <https://b2access.eudat.eu/oauth2-as/oauth2-authz-web-entry>`_ to create a new account.

======================
How to use the client?
======================


1. initialize the client:

.. code-block:: python

   from ecasb2share.ecasb2shareclient import EcasShare as Client
   client = Client(url='{b2share-url}', token_file='{path to token}')

default url is https://b2share.eudat.eu

.. code-block:: python

   help(client)

2. create a draft record

This methods reads metadata from a json file, creates a draft record and returns useful informations.

.. code-block:: python

   client.create_draft_record_with_pid(metadata_json='{metada json file}')

.. note:: it is possible to pass the metadata to the method manually but it is recommended to use
   the json file to avoid syntax validation issues in case of multiple related identifiers.


Example of metadata:
--------------------

.. code-block:: json

   {"titles": [{"title": "ECAS TEST Multiple PIDs"}],
    "community": "d2c6e694-0c0a-4884-ad15-ddf498008320",
    "related_identifiers": [
                            {
                              "related_identifier": "original_pid1",
                              "related_identifier_type": "Handle",
                              "relation_type": "IsDerivedFrom"
                            },
                            {
                              "related_identifier": "original_pid",
                              "related_identifier_type": "Handle",
                              "relation_type": "IsDerivedFrom"
                            }
                        ],

    "open_access": true
    }



