""" Helper class to interact with B2SHARE REST API to create draft records
from ECAS user workspace.
Please refer to https://eudat.eu/services/userdoc/b2share-usage
 for more information.

.. Note:: this module is not considered as B2SHARE client and it is specific
 to ECAS use case.

Author: Sofiane Bendoukha (DKRZ), 2019

"""

import requests
import json
import os
import logging

from requests import Request, Session
from . import exceptions


from urllib.parse import urljoin
from requests.exceptions import HTTPError

logging.basicConfig(level=logging.INFO)


class EcasShare (object):

    """ ECAS B2SHARE main class """

    # Initialize

    def __init__(self, url=None, token_file=None):
        """
        Initialize the client.

        :param url: URL of the B2SHARE instance.  One of the following
        hostnames can be used to identify the B2SHARE instance:

                     * b2share.eudat.eu - the hostname of the production site.
                     * trng-b2share.eudat.eu - the base url of the training
                     site. Use this URL for testing.

        :param token_file: B2SHARE API ACCESS token
        """

        # Default path in container
        CONTAINER_PATH = '/home/jovyan/work/conf'

        # TODO: set up b2share url (prod or test), token and payload?
        if url is None:
            self.B2SHARE_URL = 'https://eudat-b2share-test.csc.fi'
        else:
            self.B2SHARE_URL = url

        if token_file is None:
            self.token_path = os.path.join(CONTAINER_PATH, 'token.txt')
        else:
            self.token_path = token_file

    # Token

    def retrieve_access_token(self):
        """ Read the token from a given file named 'token' """

        token_file = open(self.token_path, 'r')
        return token_file.read().strip()

    # communities

    def list_communities(self, token=None):
        """
        List all the communities, without any filtering.

        :param token: Optional: B2SHARE API ACCESS token
        :return: list of communities in json
        """

        url = urljoin(self.B2SHARE_URL, 'api/communities')

        if token is None:
            try:
                req = self.__send_get_request(url)
                req.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)

        else:
            payload = {'access_token': token}
            try:
                req = self.__send_get_request(url, params=payload)
                req.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)

        if req.status_code == 200:
            return req.json()

    def retrieve_community_specific_records(self, community_id):
        """
        List all records of a specific community.

        :param community_id: community id. Can be retrieved from the list of
        communities
        :exc:`~ecasb2share.ecasb2shareclient.EcasShare.list_communities`
        :return:  the list of records (in JSON format) or an exception message
        """

        payload = {'q': 'community:' + community_id}
        url = urljoin(self.B2SHARE_URL, '/api/records/')

        try:
            req = self.__send_get_request(url,
                                          params=payload)
            req.raise_for_status()
            number_of_records = req.json()['hits']['total']
            print("Total number of records in this community: {}".format(number_of_records))
            if number_of_records > 0:
                return req.json()
            else:
                print("No records in this community")
        except requests.exceptions.HTTPError as err:
            print(err)

    def get_community_schema(self, community_id):
        """
        Retrieves the JSON schema of records approved by a specific community.

        :param community_id: community id. Can be found from the list of
        communities
                            :exc:`~ecasb2share.ecasb2shareclient.EcasShare.list_communities`
        :return: community schema in json format.
        """

        base = self.B2SHARE_URL
        url = '/api/communities/' + community_id + '/schemas/last'

        try:
            req = self.__send_get_request(urljoin(base, url))
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)

        if req.status_code == 200:
            return req.json()

    # records

    def list_all_records(self, size=None):
        """
        List all the records, without any filtering
        TODO add pagination
        :param size: Optional
        :return: list of records in json format.
        """

        url = urljoin(self.B2SHARE_URL, 'api/records')
        if size:
            payload = {'size': size, 'page': 1}
        else:
            payload = {'size': 10, 'page': 1}

        try:
            req = self.__send_get_request(url, params=payload)
            req.raise_for_status()
            return req.json()
        except requests.exceptions.HTTPError as err:
            print(err)

    def get_specific_record(self, record_id, draft=True):
        """ List the metadata of the record specified by RECORD_ID.

        :param record_id: record id.
        :param draft: True/False to specify which type of record to search for.
               Default: True.
        :return: list of records.

         """

        header = {'Content-Type': 'application-json'}
        token = self.retrieve_access_token().rstrip()
        payload = {'access_token': token}

        if draft:
            url = urljoin(self.B2SHARE_URL, 'api/records/' + record_id +
                          '/draft')
        else:
            url = urljoin(self.B2SHARE_URL, 'api/records/' + record_id)

        try:
            req = self.__send_get_request(url, params=payload, headers=header)
            if req is not None:
                req.raise_for_status()
                return json.loads(req.text)
        except requests.exceptions.HTTPError as err:
            print(err)

    def get_record_pid(self, record_id):
        """
        Get the pid from the record metadata (published).

        :param record_id: record id
        :return: epicPID, prefix/suffix
        """

        record = self.get_specific_record(record_id)

        try:
            "{ePIC_PID}".format(**record['metadata'])
            return record['metadata']['ePIC_PID']
        except KeyError as e:
            msg = " missing {} key".format(e)
            raise exceptions.MetadataKeyMissingException(msg=msg)

    def create_draft_record(self, community_id, title):
        """
        Create a new record with minimal metadata, in the draft state.

        :param community_id:
        :param title: title for the record
        :return: record_id, filebucket_id
        """

        token = self.retrieve_access_token().rstrip()
        header = {"Content-Type": "application/json"}
        payload = {'access_token': token}
        metadata = {"titles": [{"title": title}],
                    "community": community_id,
                    "open_access": True}
        url = urljoin(self.B2SHARE_URL, '/api/records/')
        try:
            req = self.__send_post_request(url,
                                           data=json.dumps(metadata),
                                           params=payload,
                                           headers=header)

            req.raise_for_status()
            record_id = req.json()
            filebucket_id = self.get_filebucketid_from_record(record_id['id'])
            print("Draft record created:\n" + record_id['id'])
            print('filebucketid:\n' + filebucket_id)

        except requests.exceptions.HTTPError as err:
            print(err)

        if req.status_code == 201:
            logging.info("Draft record successfully created!")
            return record_id['id'], filebucket_id

    def create_draft_record_with_pid(self, title=None, original_pid=None,
                                     metadata_json=None):
        """

        Create a draft record and specifying the original pid.
        Adapted from DataCite schema:
           * relatedIdentifierType: Handle
           * relationType: isDerivedFrom

        :param title: title for the record.
        :param original_pid: PID (prefix/suffix) of the input Dataset.
        :return: record_id and filebucket_id
        """

        ECAS_COMMUNITY_ID = 'd2c6e694-0c0a-4884-ad15-ddf498008320'
        token = self.retrieve_access_token().rstrip()
        header = {"Content-Type": "application/json"}
        payload = {"access_token": token}
        url = urljoin(self.B2SHARE_URL, '/api/records/')

        if metadata_json:
            metadata = self.load_metadata_from_json(metadata_json)
            self.validate_metadata(metadata)

            related_identifiers = metadata['related_identifiers']

            for pid in range(len(related_identifiers)):
                self.check_pid_syntax(
                    related_identifiers[pid]['related_identifier'])

            try:
                req = self.__send_post_request(url,
                                               data=json.dumps(metadata),
                                               params=payload,
                                               headers=header)

                req.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)

        else:
            metadata = {"titles": [{"title": title}],
                        "community": ECAS_COMMUNITY_ID,
                        "related_identifiers": [
                            {
                                "related_identifier": original_pid,
                                "related_identifier_type": "Handle",
                                "relation_type": "IsDerivedFrom"
                            }
            ],
                "open_access": True
            }
            try:
                req = self.__send_post_request(url,
                                               data=json.dumps(metadata),
                                               params=payload,
                                               headers=header)

                req.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)

        record_id = req.json()
        filebucket_id = self.get_filebucketid_from_record(record_id['id'])
        print("Draft record created:\n" + record_id['id'])
        print('filebucketid:\n' + filebucket_id)

        if req.status_code == 201:
            logging.info("Draft record successfully created!")
            return record_id['id'], filebucket_id

    def submit_draft_for_publication(self, record_id):
        """

        :param record_id: record id
        :return: request status (HTTP response)
        """

        header = {'Content-Type': 'application/json-patch+json'}
        commit = '[{"op": "add", "path": "/publication_state", "value": "submitted"}]'
        token = self.retrieve_access_token().rstrip()
        url = self.B2SHARE_URL + record_id + "/draft"
        payload = {"access_token": token}

        try:
            req = requests.patch(
                url, data=commit, params=payload, headers=header)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)

        return req.status_code

    def delete_draft_record(self, record_id):
        """

        :param record_id: record id
        :return: request status
        """

        url = urljoin(self.B2SHARE_URL, '/api/records/' + record_id + '/draft')
        token = self.retrieve_access_token().rstrip()
        payload = {'access_token': token}
        header = {"Content-Type": "application/json"}

        req = requests.delete(url, params=payload, headers=header)
        logging.info(req.status_code)
        return req.status_code

    def delete_published_record(self, record_id):
        """
        Notes: only a site administrator can delete a published record.

        :param record_id: the id of the draft record to delete
        :return: request status
        """

        url = urljoin(self.B2SHARE_URL, '/api/records/' + record_id)
        token = self.retrieve_access_token().rstrip()
        payload = {'access_token': token}
        header = {"Content-Type": "application/json"}

        req = requests.delete(url, params=payload, headers=header)

        return req.status_code

    def search_records(self):
        """
        List all the records, without any filtering

        """

        token = self.retrieve_access_token().rstrip()
        header = {"Content-Type": "application/json"}
        payload = {'access_token': token}

        url = urljoin(self.B2SHARE_URL, '/api/records')
        req = self.__send_get_request(url,
                                      params=payload, headers=header)
        return req.json()

    def get_filebucketid_from_record(self, record_id):
        """
        TODO add exception when record not found

        :param record_id:  identifier for a specific record, which
         can be in draft or published state
        :return: filebucket id.
        """

        record = self.get_specific_record(record_id)

        if record is not None:
            filebucket = record["links"]["files"].split('/')[-1]
            return filebucket

    def search_drafts(self):
        """
        Search for all drafts (unpublished records) that are accessible
        by the requestor.
        Usually this means own records only.

        :return: the list of matching drafts (in JSON format).
        """

        token = self.retrieve_access_token().rstrip()
        header = {"Content-Type": "application/json"}
        payload = {'draft': 1, 'access_token': token}
        url = urljoin(self.B2SHARE_URL, '/api/records/?drafts')

        req = self.__send_get_request(url,
                                      params=payload,
                                      headers=header)

        result = json.loads(req.text)
        print(result["hits"]["total"])
        return result

    def search_specific_record(self, search_value):

        payload = {'q': search_value}
        url = urljoin(self.B2SHARE_URL, '/api/records')

        req = self.__send_get_request(url,
                                      params=payload)
        return req.json()

    # files

    def add_file_to_draft_record(self, file_path, filebucket_id):
        """

        :param file_path: path to the file to be uploaded.
        :param filebucket_id: identifier for a set of files.
               Each record has its own file set, usually found
               in the links -> files section


        :return: request status
        """

        header = {'Accept': 'application/json', 'Content-Type': 'octet-stream'}
        token = self.retrieve_access_token().rstrip()
        payload = {'access_token': token}
        upload_file = {"file": open(file_path, 'rb')}
        file_name = os.path.basename(file_path)
        url = urljoin(self.B2SHARE_URL, '/api/files/' + filebucket_id)

        req = self.__send_put_request(url + '/' + file_name,
                                      files=upload_file,
                                      params=payload,
                                      headers=header)

        return req.json()

    def list_files_in_bucket(self, filebucket_id):
        """
        List the files uploaded into a record object.

        :param filebucket_id: identifier for a set of files.
               Each record has its own file set, usually found in
               the links -> files section

        :return: information about all the files in the record object
        """

        token = self.retrieve_access_token()
        payload = {'access_token': token}

        if filebucket_id:
            url = urljoin(self.B2SHARE_URL, '/api/files/' + filebucket_id)
            try:
                req = self.__send_get_request(url, params=payload)
                return req.json()
            except HTTPError as err:
                msg = '{empty request}'.format(err)
                raise exceptions.MetadataKeyMissingException(msg=msg)
        else:
            print("Filebucket ID is None!")
    # requests

    @staticmethod
    def __send_get_request(url, params=None, headers=None):

        s = Session()
        REQUEST_METHOD = 'GET'

        # Build the request
        _request = Request(REQUEST_METHOD, url, params=params, headers=headers)
        prepared_request = _request.prepare()

        try:
            response = s.send(prepared_request)

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print('HTTP error occurred:' + str(http_err))
        except Exception as err:
            print('Other error occurred: ' + err)
        else:
            return response

    @staticmethod
    def __send_put_request(url, files, params, headers):

        s = Session()

        REQUEST_METHOD = 'PUT'

        # Build the request
        _request = Request(REQUEST_METHOD, url, files=files,
                           params=params, headers=headers)
        prepared_request = _request.prepare()

        try:
            response = s.send(prepared_request)

        # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print('HTTP error occurred:' + http_err)
        except Exception as err:
            print('Other error occurred: ' + err)
        else:
            logging.info('Success!')
            return response

    @staticmethod
    def __send_post_request(url, data, params, headers):

        s = Session()

        REQUEST_MEHOD = 'POST'

        # Build he request
        _request = Request(REQUEST_MEHOD, url, data=data,
                           params=params, headers=headers)
        prepared_request = _request.prepare()

        try:
            response = s.send(prepared_request)
        # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print('HTTP error occurred:' + http_err)
        except Exception as err:
            print('Other error occurred: ' + err)
        else:
            logging.info('Record created!')
            return response

    @staticmethod
    def __response_status(response):

        if response:
            print("Success!")
        else:
            print('An error has occured.')

    # metadata

    @staticmethod
    def load_metadata_from_json(metadata_json=None):
        if metadata_json:
            with open(metadata_json, 'r') as metadata_json:
                return json.load(metadata_json)

    def validate_metadata(self, metadata=None, metadata_file=None):
        """
        Check if mandatory metadata are passed.

        :param metadata: Optional: metadata as dict (key, value)
        :param metadata_file: Optional. metadata in a json file.
        :return: metadata in json format.
        """

        if metadata_file:
            metadata = self.load_metadata_from_json(metadata_json=metadata_file)

        try:
            "{titles} {related_identifiers} {community} {open_access}".format(**metadata)
        except KeyError as e:
            msg = "missing {} key".format(e)
            raise exceptions.MetadataException(msg=msg)

        return metadata

    @staticmethod
    def check_pid_syntax(pid):
        """
        Checks if the syntax of the Handle is correct.
        Handles should be in this form:
             prefix/suffix

        :param pid: Value of the handle to be checked
        :raise: :exc:`~ecasb2share.exceptions.PIDSyntaxException`
        :return: True, otherwise, exception raised.
        """

        correct_syntax = 'prefix/suffix'

        try:
            arr = pid.split('/')
        except AttributeError:
            raise exceptions.PidSyntaxException(
                msg='The provided handle is None',
                correct_syntax=correct_syntax)

        if len(arr) < 2:
            msg = 'No slash'
            raise exceptions.PidSyntaxException(
                msg=msg, pid=pid, correct_syntax=correct_syntax)

        if len(arr[0]) == 0:
            msg = 'Empty prefix'
            raise exceptions.PidSyntaxException(
                msg=msg, pid=pid, correct_syntax=correct_syntax)

        if len(arr[1]) == 0:
            msg = 'Empty suffix'
            raise exceptions.PidSyntaxException(
                msg=msg, pid=pid, correct_syntax=correct_syntax)

        return True
