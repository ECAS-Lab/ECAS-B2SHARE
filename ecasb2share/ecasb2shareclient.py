''' Helper class to interact with B2SHARE REST API to create draft records
from ECAS user workspace.
Please refer to https://eudat.eu/services/userdoc/b2share-usage for more information.

.. Note:: this module is not considered as B2SHARE client and it is specific to ECAS use case.

Author: Sofiane Bendoukha (DKRZ), 2019

'''

import requests
import json
import os
from urllib.parse import urljoin

class EcasShare (object):

    ''' ECAS B2SHARE main class '''

    ####### Initialize ######

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

    ######## Token ########

    def access_token_file(self):
        ''' Read the token from a given file named 'token' '''

        token_file = open(self.token_path, 'r')
        return token_file.read().strip()


    ###### communities #####

    def list_communities(self, token=None):
        '''

        :return: list of communities in json
        '''

        url = urljoin(self.B2SHARE_URL, 'api/communities')

        if token is None:
            req = requests.get(url)
        else:
            payload = {'access_token': token}
            req = requests.get(url, params=payload)

        return req.json()

    def retrieve_community_specific_records(self, community_id):
        '''

        :param community_id:
        :return:
        '''

        payload = {'q': 'community_id:' + community_id}
        r = requests.get(self.B2SHARE_URL + '/api/records', params=payload)
        return r.json()

    def get_community_shema(self, community_id):

        r = requests.get(self.B2SHARE_URL + '/api/communities/' + community_id + '/schemas/last')
        return r.json()

    ##### records ########

    def list_records(self):
        '''
        List all the records, without any filtering
        TODO add pagination
        :return:
        '''
        url = urljoin(self.B2SHARE_URL, 'api/records')
        payload = {'size': 10, 'page': 1}
        req = requests.get(url)
        return req.json()

    def get_specific_record(self, record_id, draft=True):
        ''' List specific records
         TODO add access token
         '''

        header = {'Content-Type': 'application-json'}
        token = self.access_token_file().rstrip()
        #f = open(r'token.txt', 'r')
        #token = f.read().rstrip()
        payload = {'access_token': token}

        if draft:
            url = urljoin(self.B2SHARE_URL, 'api/records/' + record_id + '/draft')
            req = requests.get(url, params=payload, headers=header, verify=False)
            temp = json.loads(req.text)
            return temp

    def get_record_pid(self, record_id):
        '''
        Get the pid from the record metadata.

        :param record_id:
        :return:
        '''

        record = self.get_specific_record(record_id)
        return record['metadata']['ePIC_PID']

    def create_draft_record(self, community_id, title):
        '''
        Create a new record with minimal metadata, in the draft state.
        :return:
        '''

        token = self.access_token_file().rstrip()
        header = {"Content-Type": "application/json"}
        metadata = {"titles": [{"title": title}],
                    "community": community_id,
                    "open_access": True}
        r = requests.post(self.B2SHARE_URL + '/api/records/', params={'access_token': token},
                          data=json.dumps(metadata), headers=header)
        record_id = r.json()
        #filebucket_id = record_id['links']['files'].split('/')[-1]
        filebucket_id = self.get_filebucketid_from_record(record_id['id'])
        print("Draft record created:\n" + record_id['id'])
        print('filebucketid:\n' + filebucket_id)

        return record_id['id'], filebucket_id


    def delete_draft_record(self, record_id):


        url = urljoin(self.B2SHARE_URL, '/api/records/' + record_id + '/draft')
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

    ##### files ######

    def add_file_to_draft_record(self, file_path, filebucket_id):


        header = {'Accept': 'application/json', 'Content-Type': 'octet-stream'}
        token = self.access_token_file().rstrip()
        payload = {'access_token': token}
        upload_file = {"file": open(file_path, 'rb')}
        file_name = os.path.basename(file_path)
        url = urljoin(self.B2SHARE_URL, '/api/files/' + filebucket_id)

        req = requests.put(url + '/' + file_name, files=upload_file, params=payload, headers=header)

        return req.json()


    def list_files_in_bucket(self, filebucket_id):


        url = urljoin(self.B2SHARE_URL, '/api/files/' + filebucket_id)
        token = self.access_token_file()
        payload = {'access_token': token}
        req = requests.get(url, params=payload)
        return req.json()


    ##### metadata #######










