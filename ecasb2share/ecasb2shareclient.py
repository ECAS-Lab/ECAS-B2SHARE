''' Helper class to interact with B2SHARE REST API to create draft records
from ECAS user workspace.
Please refer to https://eudat.eu/services/userdoc/b2share-usage
 for more information.

.. Note:: this module is not considered as B2SHARE client and it is specific
 to ECAS use case.

Author: Sofiane Bendoukha (DKRZ), 2019

'''

import requests
import json
import os
import logging
import click
from urllib.parse import urljoin
from requests.exceptions import HTTPError

logging.basicConfig(level=logging.INFO)

class EcasShare (object):

    ''' ECAS B2SHARE main class '''

    # Initialize

    def __init__(self, url=None, token_file=None):
        ''' Instantiate
        TODO set path for token file.
        '''

        # TODO: set up b2share url (prod or test), token and payload?
        if url is None:
            self.B2SHARE_URL = 'https://trng-b2share.eudat.eu'
        else:
            self.B2SHARE_URL = url

        if token_file is None:
            self.token_path = '/home/jovyan/work/conf/token.txt'
        else:
            self.token_path = token_file

    # Token

    def access_token_file(self):
        ''' Read the token from a given file named 'token' '''

        token_file = open(self.token_path, 'r')
        return token_file.read().strip()

    # communities

    def list_communities(self, token=None):
        '''
        List all the communities, without any filtering.

        :param token: Optional:
        :return: list of communities in json
        '''

        url = urljoin(self.B2SHARE_URL, 'api/communities')

        if token is None:
            try:
                req = requests.get(url)
                req.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)

        else:
            payload = {'access_token': token}
            try:
                req = requests.get(url, params=payload)
                req.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)

        return req.json()

    def retrieve_community_specific_records(self, community_id):
        '''

        :param community_id:
        :return:
        '''

        payload = {'q': 'community:' + community_id}

        try:
            req = requests.get(self.B2SHARE_URL + '/api/records/', params=payload)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)

        return req.json()

    def get_community_shema(self, community_id):
        '''

        :param community_id:
        :return: community schema in json format.
        '''

        try:
            req = requests.get(self.B2SHARE_URL +
                '/api/communities/' + community_id + '/schemas/last')
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)

        if str(req.status_code) == 200:
            return req.json()

    # records

    def list_all_records(self, size=None):
        '''
        List all the records, without any filtering
        TODO add pagination
        :return:
        '''

        url = urljoin(self.B2SHARE_URL, 'api/records')
        if size:
            payload = {'size': size, 'page': 1}

        payload = {'size': 10, 'page': 1}

        try:
            req = requests.get(url, params=payload)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)

        return req.json()

    def get_specific_record(self, record_id, draft=True):
        ''' List specific records
         TODO add access token
         '''

        header = {'Content-Type': 'application-json'}
        token = self.access_token_file().rstrip()
        payload = {'access_token': token}

        if draft:
            url = urljoin(self.B2SHARE_URL, 'api/records/' + record_id +
                          '/draft')
        else:
            url = urljoin(self.B2SHARE_URL, 'api/records/' + record_id)

        try:
            req = requests.get(url, params=payload, headers=header,
                               verify=False)
            req.raise_for_status()

        except requests.exceptions.HTTPError as err:
            print(err)

        temp = json.loads(req.text)
        return temp

    def get_record_pid(self, record_id):
        '''
        Get the pid from the record metadata (published).

        :param record_id:
        :return:
        '''

        record = self.get_specific_record(record_id)
        return record['metadata']['ePIC_PID']

    def create_draft_record(self, community_id, title):
        '''
        Create a new record with minimal metadata, in the draft state.
        :return: record_id, filebucket_id
        '''

        token = self.access_token_file().rstrip()
        header = {"Content-Type": "application/json"}
        metadata = {"titles": [{"title": title}],
                    "community": community_id,
                    "open_access": True}
        try:
            r = requests.post(self.B2SHARE_URL + '/api/records/',
                          params={'access_token': token},
                          data=json.dumps(metadata), headers=header)
            r.raise_for_status()
            record_id = r.json()
            filebucket_id = self.get_filebucketid_from_record(record_id['id'])
            print("Draft record created:\n" + record_id['id'])
            print('filebucketid:\n' + filebucket_id)

        except requests.exceptions.HTTPError as err:
            print(err)

        if r.status_code == 201:
            logging.info("Draft record successfully created!")
            return record_id['id'], filebucket_id

    def create_draft_record_with_pid(self, title=None, original_pid=None, metadata_json=None):
        '''
        Create a draft record and specifying the original pid.
         adapted from DataCite schema:
           relatedIdentifierType: Handle
           relationType: isDerivedFrom

        :param title: title for the record.
        :param original_pid: PID of the input Dataset.
        :return: record_id and filebucket_id
        '''

        ECAS_COMMUNITY_ID = 'd2c6e694-0c0a-4884-ad15-ddf498008320'
        token = self.access_token_file().rstrip()
        header = {"Content-Type": "application/json"}
        payload = {"access_token": token}

        if metadata_json:
            metadata = self.load_metadata_from_json(metadata_json)
            try:
                r = requests.post(self.B2SHARE_URL + '/api/records/',
                                  params=payload,
                                  data=json.dumps(metadata),
                                  headers=header)
                r.raise_for_status()
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
                r = requests.post(self.B2SHARE_URL + '/api/records/',
                                  params={'access_token': token},
                                  data=json.dumps(metadata), headers=header)
                r.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)

        record_id = r.json()
        filebucket_id = self.get_filebucketid_from_record(record_id['id'])
        print("Draft record created:\n" + record_id['id'])
        print('filebucketid:\n' + filebucket_id)

        if r.status_code == 201:
            logging.info("Draft record successfully created!")
            return record_id['id'], filebucket_id

    def submit_draft_for_publication(self, record_id):
        '''

        :param record_id:
        :return: request status
        '''

        header = {'Content-Type': 'application/json-patch+json'}
        commit = '[{"op": "add", "path":"/publication_state", "value": "submitted"}]'
        token = self.access_token_file().rstrip()
        url = self.B2SHARE_URL + record_id + "/draft"
        payload = {"access_token": token}

        try:
            req = requests.patch(url, data=commit, params=payload, headers=header)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)

        return req.status_code

    def delete_draft_record(self, record_id):
        '''

        :param record_id:
        :return:
        '''

        url = urljoin(self.B2SHARE_URL, '/api/records/' + record_id + '/draft')
        token = self.access_token_file().rstrip()
        payload = {'access_token': token}
        header = {"Content-Type": "application/json"}

        req = requests.delete(url, params=payload, headers=header)

        return req

    def delete_published_record(self, record_id):
        '''

        :param record_id:
        :return:
        '''

        url = urljoin(self.B2SHARE_URL, '/api/records/' + record_id)
        token = self.access_token_file().rstrip()
        payload = {'access_token': token}
        header = {"Content-Type": "application/json"}

        req = requests.delete(url, params=payload, headers=header)

        return req


    def search_records(self):

        token = self.access_token_file().rstrip()
        header = {"Content-Type": "application/json"}
        payload = {'access_token': token}
        r = requests.get(self.B2SHARE_URL + '/api/records', params=payload, headers=header)
        return r.json()

    def get_filebucketid_from_record(self, record_id):
        '''
        TODO add exception when record not found
        :param record_id:
        :return:
        '''

        record = self.get_specific_record(record_id)
        filebucket = record["links"]["files"].split('/')[-1]

        return filebucket

    def search_drafts(self):
        '''
        Search for all drafts (unpublished records) that are accessible by the requestor.
        Usually this means own records only.

        :return:
        '''

        token = self.access_token_file().rstrip()
        header = {"Content-Type": "application/json"}
        payload = {'draft': 1, 'access_token': token}
        r = requests.get(self.B2SHARE_URL + '/api/records/?drafts', params=payload, headers=header)
        result = json.loads(r.text)
        print(result["hits"]["total"])
        return result

    def search_specific_record(self, search_value):

        payload = {'q': search_value}
        r = requests.get(self.B2SHARE_URL + '/api/records', params=payload)
        return r.json()

    # files

    def add_file_to_draft_record(self, file_path, filebucket_id):
        '''

        :param file_path:
        :param filebucket_id:
        :return:
        '''

        header = {'Accept': 'application/json', 'Content-Type': 'octet-stream'}
        token = self.access_token_file().rstrip()
        payload = {'access_token': token}
        upload_file = {"file": open(file_path, 'rb')}
        file_name = os.path.basename(file_path)
        url = urljoin(self.B2SHARE_URL, '/api/files/' + filebucket_id)

        req = requests.put(url + '/' + file_name, files=upload_file, params=payload, headers=header)

        return req.json()

    def list_files_in_bucket(self, filebucket_id):
        '''

        :param filebucket_id:
        :return:
        '''

        url = urljoin(self.B2SHARE_URL, '/api/files/' + filebucket_id)
        token = self.access_token_file()
        payload = {'access_token': token}
        req = requests.get(url, params=payload)
        return req.json()


    # requests

    @staticmethod
    def __send_get_request(url):

        try:
            response = requests.get(url)

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
        else:
            print('Success!')
        pass

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
            with open('metadata.json', 'r') as metadata_json:
                return json.load(metadata_json)


