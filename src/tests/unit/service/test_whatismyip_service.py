import unittest

from unittest.mock import patch
from unittest.mock import Mock

from iplocationchanger.service.whatismyip_service import WhatIsMyIPService

class TestWhatsIsMyIpService(unittest.TestCase):
  @patch('iplocationchanger.service.whatismyip_service.Utils')
  def test_get_ip(self, UtilsMock):
    test_cases = [
      {
        'success': True,
        'expected': True,
        'out': 'standard output',
        'api_key': 'apikeyisthisstring',
      },
      {
        'success': False,
        'expected': False,
        'out': 'a big error has occurred',
        'api_key': 'apikeyisthisstring',
      },
    ]

    for tc in test_cases:
      UtilsMock.exec_get_request = Mock(return_value=(
        tc['success'],
        tc['out'],
      ))

      wms = WhatIsMyIPService(tc['api_key'])
      success, out = wms.get_ip()

      UtilsMock.exec_get_request.assert_called_once_with(
        f'https://api.whatismyip.com/ip.php?key={tc["api_key"]}',
      )

      self.assertEqual(
        tc['expected'],
        success,
      )
      self.assertEqual(
        tc['out'],
        out,
      )

  @patch('iplocationchanger.service.whatismyip_service.Utils')
  def test_get_location_from_ip(self, UtilsMock):
    test_cases = [
      {
        'success': True,
        'expected': True,
        'out': 'standard output',
        'api_key': 'apikeyisthisstring',
        'ip': '192.168.0.1',
      },
      {
        'success': False,
        'expected': False,
        'out': 'error occurred',
        'api_key': 'apikeyisthisstring',
        'ip': '192.168.0.1',
      },
    ]

    for tc in test_cases:
      UtilsMock.exec_get_request = Mock(return_value=(
        tc['success'],
        tc['out'],
      ))

      wms = WhatIsMyIPService(tc['api_key'])
      success, out = wms.get_location_from_ip(tc['ip'])

      UtilsMock.exec_get_request.assert_called_once_with(
        f'https://api.whatismyip.com/ip-address-lookup.php?key={tc["api_key"]}&input={tc["ip"]}',
      )

      self.assertEqual(
        tc['expected'],
        success,
      )
      self.assertEqual(
        tc['out'],
        out,
      )

  @patch('iplocationchanger.service.whatismyip_service.Utils')
  def test_validate_connection(self, UtilsMock):
    test_cases = [
      {
        'get_ip': { 
          'success': True,
          'msg': '',
         },
        'get_location': {
          'success': True,
          'msg': '',
        },
        'extract_location_response': 'DE',
        'country_code': 'de',
        'expected': {
          'success': True,
          'msg': 'success',
        },
        'test_case': 'True, DE de',
      },
      {
        'get_ip': { 
          'success': False,
          'msg': 'error occurred',
         },
        'get_location': {
          'success': True,
          'msg': '',
        },
        'extract_location_response': 'DE',
        'country_code': 'de',
        'expected': {
          'success': False,
          'msg': 'could not obtain IP address: error occurred',
        },
        'test_case': 'False, IP address',
      },
      {
        'get_ip': { 
          'success': True,
          'msg': '',
         },
        'get_location': {
          'success': False,
          'msg': 'service error',
        },
        'extract_location_response': 'DE',
        'country_code': 'de',
        'expected': {
          'success': False,
          'msg': 'could not obtain location: service error',
        },
        'test_case': 'False, location',
      },
      {
        'get_ip': { 
          'success': True,
          'msg': '',
         },
        'get_location': {
          'success': True,
          'msg': '',
        },
        'extract_location_response': 'FR',
        'country_code': 'DE',
        'expected': {
          'success': False,
          'msg': 'DE not FR',
        },
        'test_case': 'False, FR DE',
      },
    ]

    for tc in test_cases:
      wms = WhatIsMyIPService('api_key')

      wms.get_ip = Mock(return_value=(
        tc['get_ip']['success'],
        tc['get_ip']['msg'],
      ))
      wms.get_location_from_ip = Mock(return_value=(
        tc['get_location']['success'],
        tc['get_location']['msg'],
      ))

      UtilsMock.extract_location = Mock(return_value=tc['extract_location_response'])

      success, msg = wms.validate_connection(tc['country_code'])

      self.assertEqual(
        tc['expected']['success'],
        success,
      )
      self.assertEqual(
        tc['expected']['msg'],
        msg,
      )
