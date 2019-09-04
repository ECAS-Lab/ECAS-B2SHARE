import unittest
import requests
import json

from ecasb2share.ecasb2shareclient import EcasShare
from ecasb2share.exceptions import MetadataKeyMissingException, MetadataException, PidSyntaxException
from unittest.mock import Mock, patch, mock_open
from nose.tools import assert_is_not_none

RECORD = json.load(open('test_files/record.json'))
RECORD_ID = 'b4da58206da24b1aacf3b35c66024ea8'
RECORD_ID_NO_PID = '359a7e017d164f6383e58bba925c4276'


class EcasShareTestCase(unittest.TestCase):

    def setUp(self):

        self.ecasb2share = EcasShare(token_file='test_files/token.txt')

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"titles": [{"title": "test 1"}],
                                                                          "community": "hkjhk4987dakh"}))
    def load_json_unit_test(self, mock_open):
        """
        Test if json files loaded properly.

        """

        expected_output = {"titles": [{"title": "test 1"}],
                           "community": "hkjhk4987dakh"}

        filename = 'metadata.json'
        actual_output = self.ecasb2share.load_metadata_from_json(filename)

        # Assert filename is file that is opened
        # mock_open.assert_called_with(filename)

        self.assertEqual(expected_output, actual_output)

    @patch('ecasb2share.ecasb2shareclient.requests.get')
    def send_get_request_unit_test(self, mock_get):

        mock_get.return_value.ok = True

        # Send a request to the API server and store the response.
        response = requests.get('https://b2share.eudat.eu/')

        assert_is_not_none(response)

    @patch('ecasb2share.ecasb2shareclient.requests.put')
    def send_put_request_unit_test(self, mock_get):

        mock_get.return_value.ok = True

        # Send a request to the API server and store the response.
        response = requests.get('https://b2share.eudat.eu/')

        assert_is_not_none(response)

    @patch('ecasb2share.ecasb2shareclient.requests.post')
    def send_post_request_unit_test(self, mock_get):

        mock_get.return_value.ok = True

        # Send a request to the API server and store the response.
        response = requests.post('https://b2share.eudat.eu/')

        assert_is_not_none(response)

    @patch('ecasb2share.ecasb2shareclient.requests.get')
    def list_communities_unit_test(self, mock_get):
        expected_response = {
            "hits": {
                "hits": [
                    {
                        "created": "Tue, 18 Oct 2016 08:30:47 GMT",
                        "description": "The big Eudat community. Use this community if no other is suited for you",
                        "id": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095",
                        "links": {
                            "self": "https://trng-b2share.eudat.eu/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095"},
                        "logo": "/img/communities/eudat.png",
                        "name": "EUDAT",
                        "updated": "Tue, 18 Oct 2016 08:30:47 GMT"},
                    ...],
                "total": 11},
            "links": {
                "self": "https://trng-b2share.eudat.eu/api/communities/"}}

        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = expected_response

        response = self.ecasb2share.list_communities()

        # assert_list_equal(response, expected_response)

    @patch('ecasb2share.ecasb2shareclient.requests.get')
    def list_communities_when_none_unit_test(self, mock_get):
        expected_response = {
            "hits": {
                "hits": [
                    {
                        "created": "Tue, 18 Oct 2016 08:30:47 GMT",
                        "description": "The big Eudat community. Use this community if no other is suited for you",
                        "id": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095",
                        "links": {
                            "self": "https://trng-b2share.eudat.eu/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095"},
                        "logo": "/img/communities/eudat.png",
                        "name": "EUDAT",
                        "updated": "Tue, 18 Oct 2016 08:30:47 GMT"},
                    ...],
                "total": 11},
            "links": {
                "self": "https://trng-b2share.eudat.eu/api/communities/"}}

        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = expected_response

        response = self.ecasb2share.list_communities()

        assert_is_not_none(response)

    # This method will be used by the mock to replace requests.get
    def mocked_requests_get(self, *args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        if args[0] == 'http://someurl.com/test.json':
            return MockResponse({"key1": "value1"}, 200)
        elif args[0] == 'http://someotherurl.com/anothertest.json':
            return MockResponse({"key2": "value2"}, 200)

        return MockResponse(None, 404)

    def server_running_unit_test(self):

        response = requests.get('https://b2share.eudat.eu')
        self.assertEqual(response.status_code, 200)

    def get_list_communities_unit_test(self):
        with patch('ecasb2share.ecasb2shareclient.requests.get') as mock_get:
            mock_get.return_value.ok = True

            communities = self.ecasb2share.list_communities()

            # self.assertEqual(communities, 'Success')

    def get_record_pid_unit_test(self):
        """
        Check if ePIC_PID found and retrieved from record.

        """

        with patch('ecasb2share.ecasb2shareclient.EcasShare.get_specific_record') as mock_request:

            mock_request.return_value = RECORD

            pid = self.ecasb2share.get_record_pid(RECORD_ID)

            self.assertEqual(pid, RECORD['metadata']['ePIC_PID'])

    def get_record_pid_not_existent_unit_test(self):
        """
        Test if exception is raised when ePIC_PID missing
        """

        with self.assertRaises(MetadataKeyMissingException):
            self.ecasb2share.get_record_pid(RECORD_ID_NO_PID)

    def validate_metadata_true_unit_test(self):
        """
        Check if metadata opened and load properly.
        """

        expected_metadata = json.load(open('test_files/fake_metadata.json', 'r'))
        metadata = self.ecasb2share.validate_metadata(metadata_file='test_files/fake_metadata.json')

        self.assertEqual(metadata, expected_metadata)

    def validate_metadata_false_unit_test(self):
        """
        Check if exception is raised when key missing.
        """

        with self.assertRaises(MetadataException):
            self.ecasb2share.validate_metadata(metadata_file='test_files/metadata_missing_key.json')

    def check_pid_syntax_unit_test(self):
        pid = '00.00000/xxxx-yyyy-zzzz'
        response = self.ecasb2share.check_pid_syntax(pid)
        self.assertTrue(response)

    def check_pid_no_slash_unit_test(self):
        """
        Check if exception raises when no slash in PID.

        """

        pid = '00.00000xxxx-yyyy-zzzz'
        with self.assertRaises(PidSyntaxException):
            self.ecasb2share.check_pid_syntax(pid)

    def check_pid_syntax_no_prefix_unit_test(self):
        """
        Check if exception raises when missing a prefix in the PID.

        """

        pid = '/xxxx-yyyy-zzzz'
        with self.assertRaises(PidSyntaxException):
            self.ecasb2share.check_pid_syntax(pid)

    def check_pid_syntax_no_suffix_unit_test(self):
        """
        Check if exception raises when missing a suffix in the PID.

        """

        pid = '00.00000/'
        with self.assertRaises(PidSyntaxException):
            self.ecasb2share.check_pid_syntax(pid)

    def get_filebucketid_from_record_unit_test(self):
        """
        Test if filebukcetid is correctly retrieved from the record.

        """

        # random id
        record_id = 'sadadasdadddd5dd9f1fa4441a79dfa5f270469f8d'

        # patch get_specific_record
        with patch('ecasb2share.ecasb2shareclient.EcasShare.get_specific_record') as mock_process:

            mock_process.return_value = RECORD
            filebucketid = self.ecasb2share.get_filebucketid_from_record(record_id)

            self.assertEqual(filebucketid, 'da7ddd6c-5d14-4986-91aa-d9a46b4138d8')

    def check_total_community_specific_records_unit_test(self):
        """
        Test if specific records are retrieved from the request response.
        """

        with patch('requests.get') as mock_request:

            mock_request.return_value.ok = True
            # mock_request.return_value.text = json.load(open('test_files/communiy_records.json'))

            records = self.ecasb2share.retrieve_community_specific_records(community_id='d2c6e694-0c0a-4884-ad15-ddf498008320')

            self.assertEqual(records['hits']['total'], 3)

    def check_total_community_specific_records_patched_unit_test(self):
        """
        Test if specific records are retrieved from the request response (patched).
        """

        with patch('ecasb2share.ecasb2shareclient.EcasShare.retrieve_community_specific_records') as mock_request:


             mock_request.return_value = json.load(open('test_files/community_records.json'))

             records = self.ecasb2share.retrieve_community_specific_records()
             print('Info is {}'.format(records))
             self.assertEqual(records['hits']['total'], 3)
