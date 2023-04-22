import unittest

from unittest.mock import patch
from unittest.mock import call
from unittest.mock import Mock

from iplocationchanger.model.whatismyip_response import WhatIsMyIPResponse
from iplocationchanger.exception.whatismyip_response_exception import WhatIsMyIPResponseException

class TestWhatIsMyIPService(unittest.TestCase):
  IP_RESPONSE = '{"ip_address":"95.223.119.45"}'
  LOCATION_RESPONSE = '{ "ip_address_lookup": [{"status":"ok","ip":"95.223.119.45","asn":"3209","country":"DE","region":"Pessen","city":"Main","postalcode":"55931","isp":"An ISP","time":"+02:00","latitude":"50.110882","longitude":"8.681996"}]}'

  def test_init(self):
    test_cases = [
      {
        'response_content': TestWhatIsMyIPService.IP_RESPONSE,
        'expects_error': False,
        'expected_type': WhatIsMyIPResponse.TYPE_IP,
        'expected_ip': '95.223.119.45',
        'expected_location': None,
        'msg': 'Valid IP response',
      },
      {
        'response_content': '{}',
        'expects_error': True,
        'expected_type': None,
        'expected_ip': None,
        'expected_location': None,
        'msg': 'Empty response',
      },
      {
        'response_content': TestWhatIsMyIPService.LOCATION_RESPONSE,
        'expects_error': False,
        'expected_type': WhatIsMyIPResponse.TYPE_LOCATION,
        'expected_ip': None,
        'expected_location': 'DE',
        'msg': 'Valid location response',
      },
    ]

    for tc in test_cases:
      if tc['expects_error']:
        with self.assertRaises(WhatIsMyIPResponseException):
          WhatIsMyIPResponse(tc['response_content'])
      else:
        wimir = WhatIsMyIPResponse(tc['response_content'])
        self.assertEqual(wimir.type, tc['expected_type'])
        self.assertEqual(wimir.ip, tc['expected_ip'])
        self.assertEqual(wimir.location, tc['expected_location'])

  def test_check_error(self):
    test_cases = [
      {
        'content': '0',
        'expects_error': True,
        'expected_msg': 'API key was not entered',
      },
      {
        'content': '1',
        'expects_error': True,
        'expected_msg': 'API key is invalid',
      },
      {
        'content': '2',
        'expects_error': True,
        'expected_msg': 'API key is inactive',
      },
      {
        'content': '3',
        'expects_error': True,
        'expected_msg': 'Too many lookups',
      },
      {
        'content': '4',
        'expects_error': True,
        'expected_msg': 'Invalid IP address',
      },
      {
        'content': '5',
        'expects_error': True,
        'expected_msg': 'IP address not found',
      },
      {
        'content': '6',
        'expects_error': True,
        'expected_msg': 'IP address not found',
      },
      {
        'content': TestWhatIsMyIPService.IP_RESPONSE,
        'expects_error': False,
        'expected_msg': '',
      },
      {
        'content': TestWhatIsMyIPService.LOCATION_RESPONSE,
        'expects_error': False,
        'expected_msg': '',
      }
    ]

    for tc in test_cases:
      if tc['expects_error']:
        with self.assertRaises(WhatIsMyIPResponseException, msg=tc['expected_msg']):
          WhatIsMyIPResponse(tc['content'])
      else:
        WhatIsMyIPResponse(tc['content'])
