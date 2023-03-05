import unittest

from unittest.mock import patch
from unittest.mock import Mock
from subprocess import CalledProcessError

from iplocationchanger.utils.utils import Utils

class TestUtils(unittest.TestCase):
  @patch('iplocationchanger.utils.utils.subprocess')
  def test_run_proc(self, subprocess_mock):
    test_cases = [
      {
        'cmd': ['command_to_run', 'arg1', '--arg2'],
        'expect_error': False,
        'returncode': 0,
        'expected': {
          'success': True,
          'stdout': b'normal output',
          'stderr': b'error output',
        },
      },
      {
        'cmd': ['command_to_run', 'arg1', '--arg2'],
        'expect_error': False,
        'returncode': 1,
        'expected': {
          'success': False,
          'stdout': b'',
          'stderr': b'error output',
        },
      },
    ]

    for tc in test_cases:
      proc = Mock()
      proc.returncode = tc['returncode']
      proc.stdout = tc['expected']['stdout']
      proc.stderr = tc['expected']['stderr']
      subprocess_mock.run = Mock(return_value=proc)

      success, stdout, stderr = Utils.run_proc(
        tc['cmd'],
        tc['expect_error'],
      )

      subprocess_mock.run.assert_called_once_with(
        tc['cmd'],
        capture_output=True,
        check=True,
      )

      self.assertEqual(
        tc['expected']['success'],
        success,
      )
      self.assertEqual(
        tc['expected']['stdout'].decode('utf-8'),
        stdout,
      )
      self.assertEqual(
        tc['expected']['stderr'].decode('utf-8'),
        stderr,
      )

  @patch('iplocationchanger.utils.utils.subprocess')
  def test_run_proc_expect_error(self, subprocess_mock):
    test_cases = [
      {
        'cmd': ['command_to_run', 'arg1', '--arg2'],
        'expect_error': True,
        'returncode': 0,
        'expected': {
          'success': True,
          'stdout': 'execution failed',
          'stderr': 'called process error',
        },
      },
    ]

    for tc in test_cases:
      subprocess_mock.run = Mock(
        side_effect=CalledProcessError(
          tc['returncode'],
          tc['cmd'],
        )
      )

      success, stdout, stderr = Utils.run_proc(
        tc['cmd'],
        tc['expect_error'],
      )

      self.assertEqual(
        tc['expected']['success'],
        success,
      )
      self.assertEqual(
        tc['expected']['stdout'].decode('utf-8'),
        stdout,
      )
      self.assertEqual(
        tc['expected']['stderr'].decode('utf-8'),
        stderr,
      )

  @patch('iplocationchanger.utils.utils.subprocess')
  def test_run_proc_expect_error(self, subprocess_mock):
    test_cases = [
      {
        'cmd': ['command_to_run', 'arg1', '--arg2'],
        'expect_error': False,
        'returncode': 1,
        'expected': {
          'success': False,
          'stdout': b'',
          'stderr': b'error output',
        },
      },
      {
        'cmd': ['command_to_run', 'arg1', '--arg2'],
        'expect_error': False,
        'returncode': 0,
        'expeted': {
          'success': False,
          'stdout': b'',
          'stderr': b'error output',
        },
      },
    ]

    for tc in test_cases:
      subprocess_mock.run = Mock(
        side_effect=CalledProcessError(
          tc['returncode'],
          tc['cmd'],
        )
      )

      with self.assertRaises(CalledProcessError):
        Utils.run_proc(
          tc['cmd'],
          tc['expect_error'],
        )

  @patch('iplocationchanger.utils.utils.requests')
  def test_exec_get_request(self, requests_mock):
    test_cases = [
      {
        'url': 'http://host.internal.pc',
        'res_status_code': 200,
        'res_content': b'successful request',
        'expected': {
          'success': True,
          'msg': 'successful request',
        }
      },
      {
        'url': 'http://host.internal.pc',
        'res_status_code': 200,
        'res_content': b'request successful',
        'expected': {
          'success': True,
          'msg': 'request successful',
        }
      },
      {
        'url': 'http://host.internal.pc',
        'res_status_code': 404,
        'res_content': b'not found',
        'expected': {
          'success': False,
          'msg': 'not found',
        }
      },
      {
        'url': 'http://host.internal.pc',
        'res_status_code': 500,
        'res_content': b'internal server error',
        'expected': {
          'success': False,
          'msg': 'internal server error',
        }
      },
    ]

    for tc in test_cases:
      request_res = Mock()
      request_res.status_code = tc['res_status_code']
      request_res.content = tc['res_content']
      requests_mock.get = Mock(return_value=request_res)

      success, res_body = Utils.exec_get_request(tc['url'])

      requests_mock.get.assert_called_once_with(tc['url'])
      self.assertEqual(
        success,
        tc['expected']['success'],
      )
      self.assertEqual(
        res_body,
        tc['expected']['msg'],
      )

  def test_extract_location(self):
    test_cases = [
      {
        'location_str': 'status:ok  \r\nip:37.201.195.102  \r\nasn:3209  \r\ncountry:DE  \r\nregion:Hessen  \r\ncity:Schlitz  \r\npostalcode:36110  \r\nisp:Vodafone West GmbH  \r\ntime:+01:00  \r\nlatitude:50.67416  \r\nlongitude:9.56102  \r\n',
        'expected_country_code': 'DE',
      },
      {
        'location_str': 'status:ok  \r\nip:82.102.23.74  \r\nasn:9009  \r\ncountry:BG  \r\nregion:Sofia (stolitsa)  \r\ncity:Sofia  \r\npostalcode:1000  \r\nisp:Venus Business Communications Limited  \r\ntime:+02:00  \r\nlatitude:42.69751  \r\nlongitude:23.32415  \r\n',
        'expected_country_code': 'BG',
      },
      {
        'location_str': 'status:ok  \r\nip:199.33.69.27  \r\nasn:54138  \r\ncountry:AR  \r\nregion:Ciudad Autonoma de Buenos Aires  \r\ncity:Buenos Aires  \r\npostalcode:C1871  \r\nisp:Overplay Inc  \r\ntime:-03:00  \r\nlatitude:-34.603729  \r\nlongitude:-58.381577  \r\n',
        'expected_country_code': 'AR',
      },
      {
        'location_str': 'status:ok  \r\nip:87.249.139.233  \r\nasn:  \r\ncountry:TR  \r\nregion:Istanbul  \r\ncity:Istanbul  \r\npostalcode:34080  \r\nisp:DataCamp Limited  \r\ntime:+03:00  \r\nlatitude:41.01384  \r\nlongitude:28.949659  \r\n',
        'expected_country_code': 'TR',
      },
    ]

    for tc in test_cases:
      country_code = Utils.extract_location(tc['location_str'])
      self.assertEqual(
        tc['expected_country_code'],
        country_code,
      )
    
