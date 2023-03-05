import unittest

from unittest.mock import patch
from unittest.mock import Mock

from iplocationchanger.service.openvpn_service import OpenVPNService

class TestOpenVPNService(unittest.TestCase):
  def test_has_credentials(self):
    test_cases = [
      {
        'credentials_path': 'path/to/credentials',
        'expected': True,
      },
      {
        'credentials_path': '',
        'expected': False,
      },
    ]

    for tc in test_cases:
      ovs = OpenVPNService(
        {},
        '',
        tc['credentials_path'],
      )

      self.assertEqual(
        tc['expected'],
        ovs.has_credentials,
      )

  @patch('iplocationchanger.service.openvpn_service.Utils')
  def test_disconnect(self, UtilsMock):
    test_cases = [
      {
        'success': True,
        'stdout': 'success',
        'stderr': 'error message',
        'expected': True,
        'case_name': 'True from success',
      },
    ]

    for tc in test_cases:
      ovs = OpenVPNService({}, '')

      UtilsMock.run_proc = Mock(return_value=(
        True,
        tc['stdout'],
        tc['stderr'],
      ))

      success, stdout, stderr = ovs.disconnect()

      UtilsMock.run_proc.assert_called_once_with(
        ['sudo', 'killall', 'openvpn'],
        expect_error = True,
      )

      self.assertEqual(
        success,
        tc['expected'],
      )
      self.assertEqual(
        stdout,
        tc['stdout'],
      )
      self.assertEqual(
        stderr,
        tc['stderr'],
      )

  @patch('iplocationchanger.service.openvpn_service.Utils')
  def test_connect(self, UtilsMock):
    config_to_country = {
      'sample country 1': '/path/to/config/1.ovpn',
      'sample country 2': '/path/to/config/2.ovpn',
      'sample country 3': '/path/to/config/3.ovpn',
    }
    
    test_cases = [
      {
        'openvpn_executable': 'usr/bin/openvpn',
        'openvpn_daemon_name': 'openvpn_iplocationchanger',
        'config_path': '',
        'country': '',
        'credentials_path': 'path/to/credentials',
        'has_credentials': True,
        'success': True,
        'expected': False,
        'stdout': '',
        'stderr': 'no config for specified country',
        'case_name': 'Failed, country not found',
      },
      {
        'openvpn_executable': 'usr/bin/openvpn',
        'openvpn_daemon_name': 'openvpn_iplocationchanger',
        'config_path': '/path/to/config1.ovpn',
        'country': 'country name 1',
        'credentials_path': 'path/to/credentials',
        'has_credentials': True,
        'success': False,
        'expected': False,
        'stdout': 'openvpn failed',
        'stderr': 'could not connect',
        'case_name': 'Failed, with config',
      },
      {
        'openvpn_executable': 'usr/bin/openvpn',
        'openvpn_daemon_name': 'openvpn_iplocationchanger',
        'config_path': '/path/to/config2.ovpn',
        'country': 'country name 2',
        'credentials_path': 'path/to/credentials',
        'has_credentials': True,
        'success': True,
        'expected': True,
        'stdout': '',
        'stderr': 'no config for specified country',
        'case_name': 'Success, with credentials',
      },
      {
        'openvpn_executable': 'usr/bin/openvpn',
        'openvpn_daemon_name': 'openvpn_iplocationchanger',
        'config_path': '/path/to/config3.ovpn',
        'country': 'country name 3',
        'credentials_path': '',
        'has_credentials': False,
        'success': True,
        'expected': True,
        'stdout': '',
        'stderr': 'no config for specified country',
        'case_name': 'Success, without credentials',
      },
    ]

    for tc in test_cases:
      if len(tc['country']) != 0:
        config_to_country[tc['country']] = tc['config_path']

      ovs = OpenVPNService(
        config_to_country, 
        tc['openvpn_executable'],
        tc['credentials_path'],
      )

      UtilsMock.run_proc = Mock(return_value=(
        tc['success'],
        tc['stdout'],
        tc['stderr'],
      ))

      success, stdout, stderr = ovs.connect(tc['country'])

      if len(tc['country']) != 0:
        run_proc_args = [
          'sudo', tc['openvpn_executable'],
          '--auth-retry', 'nointeract',
          '--config', tc['config_path'],
          '--script-security', '2',
          '--daemon', tc['openvpn_daemon_name'],
        ]
        if tc['has_credentials']:
          run_proc_args.extend(
            [ '--auth-user-pass', tc['credentials_path'] ],
          )

        UtilsMock.run_proc.assert_called_once_with(
          run_proc_args,
        )

      self.assertEqual(
        success,
        tc['expected'],
      )
      self.assertEqual(
        stdout,
        tc['stdout'],
      )
      self.assertEqual(
        stderr,
        tc['stderr'],
      )
  