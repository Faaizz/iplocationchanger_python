import unittest

from unittest.mock import patch
from unittest.mock import Mock
from unittest.mock import PropertyMock

from iplocationchanger.service.whatismyip_service import WhatIsMyIPService
from iplocationchanger.exception.whatismyip_service_exception import WhatIsMyIPServiceException

class TestWhatsIsMyIpService(unittest.TestCase):
  def test_check_request_error(self):
    test_cases = [
      {
        'expects_exception': True,
        'expected_msg': 'API key was not entered',
        'response': '0',
      },
      {
        'expects_exception': True,
        'expected_msg': 'API key is invalid',
        'response': '1',
      },
      {
        'expects_exception': True,
        'expected_msg': 'API key is inactive',
        'response': '2',
      },
      {
        'expects_exception': True,
        'expected_msg': 'Too many lookups',
        'response': '3',
      },
      {
        'expects_exception': True,
        'expected_msg': 'No input',
        'response': '4',
      },
      {
        'expects_exception': True,
        'expected_msg': 'Invalid input',
        'response': '5',
      },
      {
        'expects_exception': True,
        'expected_msg': 'Unknown error',
        'response': '6',
      },
      {
        'expects_exception': False,
        'expected_msg': '',
        'response': '{"ip_address":"95.223.119.45"}',
      },
      {
        'expects_exception': False,
        'expected_msg': '',
        'response': '{ "ip_address_lookup": [{"status":"ok","ip":"95.223.119.45","asn":"3209","country":"DE","region":"Pessen","city":"Main","postalcode":"55931","isp":"An ISP","time":"+02:00","latitude":"50.110882","longitude":"8.681996"}]}',
      }
    ]

    for tc in test_cases:
      ws = WhatIsMyIPService('apikeyisthisstring')
      if tc['expects_exception']:
        with self.assertRaises(WhatIsMyIPServiceException):
          ws.check_request_error(tc['response'])
      else:
        res = ws.check_request_error(tc['response'])
        self.assertEqual(res, None)

  @patch('iplocationchanger.service.whatismyip_service.requests.get')
  @patch('iplocationchanger.service.whatismyip_service.WhatIsMyIPService.check_request_error')
  def test_request_valid(self, MockCheckRequestError, MockRequestsGet):
    self.maxDiff = None
    # MockCheckRequestError: Mock object for check_request_error
    test_cases = [
      {
        'path': 'ip',
        'other_params': {},
        'request_response': b'{"ip_address":"192.168.0.1"}',
        'expected_result': {
          'ip_address': '192.168.0.1',
        },
      },
      {
        'path': 'ip-address-lookup',
        'other_params': {
          'ip': '192.168.0.1',
        },
        'request_response': b'{ "ip_address_lookup": [{"status":"ok","ip":"192.168.0.1","asn":"3209","country":"DE","region":"Pessen","city":"Main","postalcode":"55931","isp":"An ISP","time":"+02:00","latitude":"50.110882","longitude":"8.681996"}]}',
        'expected_result': {
          'ip_address_lookup': [{
            'status': 'ok',
            'ip': '192.168.0.1',
            'asn': '3209',
            'country': 'DE',
            'region': 'Pessen',
            'city': 'Main',
            'postalcode': '55931',
            'isp': 'An ISP',
            'time': '+02:00',
            'latitude': '50.110882',
            'longitude': '8.681996',
          }],
        },
      }
    ]

    for tc in test_cases:
      ws = WhatIsMyIPService('apikeyisthisstring')

      type(MockRequestsGet.return_value).content = PropertyMock(return_value=tc['request_response'])
      type(MockRequestsGet.return_value).status_code = PropertyMock(return_value=200)
      
      res = ws.request(tc['path'], tc['other_params'])

      url = f'https://api.whatismyip.com/{tc["path"]}.php'
      params = {
        'key': 'apikeyisthisstring',
        'output': 'json',
        **tc['other_params'],
      }
      MockRequestsGet.assert_called_with(url, params=params)
      self.assertTrue(isinstance(res, dict))
      self.assertEqual(res, tc['expected_result'])


  @patch('iplocationchanger.service.whatismyip_service.requests.get')
  def test_request_with_exception(self, MockRequestsGet):
    # MockCheckRequestError: Mock object for check_request_error
    tc1 = {
      'path': 'ip',
      'other_params': {},
      'request_response': b'dummy response',
      'expected_msg': 'Could not complete request "ip".',
    }
    ws = WhatIsMyIPService('apikeyisthisstring')
    type(MockRequestsGet.return_value).content = PropertyMock(return_value=tc1['request_response'])
    type(MockRequestsGet.return_value).status_code = PropertyMock(return_value=404)
    with self.assertRaises(WhatIsMyIPServiceException):  
      ws.request(tc1['path'], tc1['other_params'])

    tc2 = {
      'path': 'ip-address-lookup',
      'other_params': {},
      'request_response': b'dummy response',
      'expected_msg': 'Could not complete request "ip-address-lookup".',
    }
    ws = WhatIsMyIPService('apikeyisthisstring')
    type(MockRequestsGet.return_value).content = PropertyMock(return_value=tc2['request_response'])
    type(MockRequestsGet.return_value).status_code = PropertyMock(return_value=500)
    with self.assertRaises(WhatIsMyIPServiceException):  
      ws.request(tc2['path'], tc2['other_params'])

    tc3 = {
      'path': 'ip-address-lookup',
      'other_params': {},
      'request_response': b'{"malformed:json"',
      'expected_msg': 'Invalid JSON',
    }
    ws = WhatIsMyIPService('apikeyisthisstring')
    type(MockRequestsGet.return_value).content = PropertyMock(return_value=tc3['request_response'])
    type(MockRequestsGet.return_value).status_code = PropertyMock(return_value=200)
    with self.assertRaises(WhatIsMyIPServiceException):  
      ws.request(tc3['path'], tc3['other_params'])
   
  @patch('iplocationchanger.service.whatismyip_service.WhatIsMyIPService.get_ip')
  @patch('iplocationchanger.service.whatismyip_service.WhatIsMyIPService.get_location_from_ip')
  def test_validate_connection(self, MockGetLocationFromIP, MockGetIP):
    test_cases_valid = [
      {
        'returned_location': 'DE',
        'expected_country_code': 'DE',
      },
      {
        'returned_location': 'US',
        'expected_country_code': 'us',
      },
      {
        'returned_location': 'ar',
        'expected_country_code': 'ar',
      },
    ]

    test_cases_invalid = [
      {
        'returned_location': 'US',
        'expected_country_code': 'DE',
      },
      {
        'returned_location': 'br',
        'expected_country_code': 'ar',
      },
    ]

    MockGetIP.return_value = ''

    for tc in test_cases_valid:
      MockGetLocationFromIP.return_value = tc['returned_location']
      ws = WhatIsMyIPService('apikeyisthisstring')
      # should not raise exception

    for tc in test_cases_invalid:
      MockGetLocationFromIP.return_value = tc['returned_location']
      with self.assertRaises(WhatIsMyIPServiceException):
        ws.validate_connection(tc['expected_country_code'])

  @patch('iplocationchanger.service.whatismyip_service.WhatIsMyIPService.request')
  def test_get_ip(self, MockRequest):
    test_cases_valid = [
      {
        'returned_body': {'ip_address':'95.223.119.45'},
        'expected_ip': '95.223.119.45',
      },
      {
        'returned_body': {'ip_address':'192.168.10.2'},
        'expected_ip': '192.168.10.2',
      },
    ]

    test_cases_invalid = [
      { 
        'returned_body': {},
      },
      { 
        'returned_body': {'body': '192.168.0.100'},
      },
    ]

    for tc in test_cases_valid:
      MockRequest.return_value = tc['returned_body']
      ws = WhatIsMyIPService('apikeyisthisstring')
      res = ws.get_ip()
      MockRequest.assert_called_with('ip')
      self.assertEqual(res, tc['expected_ip'])
    
    for tc in test_cases_invalid:
      MockRequest.return_value = tc['returned_body']
      with self.assertRaises(WhatIsMyIPServiceException):
        ws.get_ip()

  @patch('iplocationchanger.service.whatismyip_service.WhatIsMyIPService.request')
  def test_get_location_from_ip(self, MockRequest):
    test_cases_valid = [
      {
        'requested_ip': '95.223.119.45',
        'returned_body': {
          'ip_address_lookup': [{
            'status': 'ok',
            'ip': '95.223.119.45',
            'country': 'DE',
          }],
        },
        'expected_location': 'DE',
      },
      {
        'requested_ip': '192.168.20.12',
        'returned_body': {
          'ip_address_lookup': [{
            'status': 'ok',
            'ip': '192.168.20.12',
            'country': 'TR',
          }],
        },
        'expected_location': 'TR',
      },
    ]

    test_cases_invalid = [
      { 
        'requested_ip': '95.223.119.45',
        'returned_body': {},
      },
      { 
        'requested_ip': '192.168.20.12',
        'returned_body': {'body': 'blank'},
      },
    ]

    for tc in test_cases_valid:
      MockRequest.return_value = tc['returned_body']
      ws = WhatIsMyIPService('apikeyisthisstring')
      res = ws.get_location_from_ip(tc['requested_ip'])
      MockRequest.assert_called_with('ip-address-lookup', {'input': tc['requested_ip']})
      self.assertEqual(res, tc['expected_location'])
    
    for tc in test_cases_invalid:
      MockRequest.return_value = tc['returned_body']
      with self.assertRaises(WhatIsMyIPServiceException):
        ws.get_location_from_ip(tc['requested_ip'])
