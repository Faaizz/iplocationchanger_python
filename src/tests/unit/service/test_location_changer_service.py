import unittest

from unittest.mock import Mock
from unittest.mock import patch

from iplocationchanger.service.location_changer_service import LocationChangerService

class TestLocationChangerService(unittest.TestCase):
  @patch('iplocationchanger.service.location_changer_service.OpenVPNService')
  def test_disconnect_region(self, OpenVPNServiceMock):
    test_cases = [
      {
        'case_name': 'True True',
        'open_vpn_service': {
          'success': True,
          'stdout': 'standard output stream message\n',
          'stderr': 'standard error stream message\n',
        },
        'expected': {
          'success': True,
          'msg': 'standard output stream message\nstandard error stream message\n',
        },
      },
      {
        'case_name': 'False False',
        'open_vpn_service': {
          'success': False,
          'stdout': 'could not connect ',
          'stderr': 'an error occurred ',
        },
        'expected': {
          'success': False,
          'msg': 'could not connect an error occurred ',
        },
      },
    ]

    for tc in test_cases:
      success_status = tc['open_vpn_service']['success']
      stdout = tc['open_vpn_service']['stdout']
      stderr = tc['open_vpn_service']['stderr']
      OpenVPNServiceMockObject = Mock()
      OpenVPNServiceMockObject.disconnect = Mock(return_value=(
        success_status,
        stdout,
        stderr,
      ))
      OpenVPNServiceMock.return_value = OpenVPNServiceMockObject

      lcs = LocationChangerService(
        'api_key',
        {},
        'openvpnexec',
      )
      success_response, std_response = lcs.disconnect_region()

      OpenVPNServiceMockObject.disconnect.assert_called_once_with()
      self.assertEqual(
        success_response, 
        tc['expected']['success'],
        tc['case_name'],
      )
      self.assertEqual(
        std_response, 
        tc['expected']['msg'],
        tc['case_name'],
      )

  @patch('iplocationchanger.service.location_changer_service.OpenVPNService')
  @patch('iplocationchanger.service.location_changer_service.WhatIsMyIPService')
  def test_connect_region_ovs_connect(self, WhatIsMyIPServiceMock, OpenVPNServiceMock):
    test_cases = [
      {
        'case_name': 'True True True',
        'country': 'country name',
        'open_vpn_service': {
          'success': True,
          'stdout': 'all good from here ',
          'stderr': '',
        },
        'whatismyip_service': {
          'status': True,
          'output': 'connected to specified region',
        },
        'expected': {
          'success': True,
          'msg': 'all good from here connected to specified region',
        },
      },
      {
        'case_name': 'False True False',
        'country': 'country name',
        'open_vpn_service': {
          'success': False,
          'stdout': 'all good from here\n',
          'stderr': '',
        },
        'whatismyip_service': {
          'status': True,
          'output': 'connected to specified region',
        },
        'expected': {
          'success': False,
          'msg': 'all good from here\nconnected to specified region',
        },
      },
      {
        'case_name': 'False False False',
        'country': 'country name',
        'open_vpn_service': {
          'success': False,
          'stdout': 'config invalid\n',
          'stderr': 'config file invalid\n',
        },
        'whatismyip_service': {
          'status': False,
          'output': 'could not connect to specified region',
        },
        'expected': {
          'success': False,
          'msg': 'config invalid\nconfig file invalid\ncould not connect to specified region',
        },
      },
    ]

    for tc in test_cases:
      country = tc['country']
      ovs_success = tc['open_vpn_service']['success']
      ovs_stdout = tc['open_vpn_service']['stdout']
      ovs_stderr = tc['open_vpn_service']['stderr']
      OpenVPNServiceMockObject = Mock()
      OpenVPNServiceMockObject.connect = Mock(return_value=(
        ovs_success,
        ovs_stdout,
        ovs_stderr,
      ))
      OpenVPNServiceMock.return_value = OpenVPNServiceMockObject


      wms_success = tc['whatismyip_service']['status']
      wms_out = tc['whatismyip_service']['output']
      WhatIsMyIPServiceMockObject = Mock()
      WhatIsMyIPServiceMockObject.validate_connection = Mock(
        return_value=(
        wms_success,
        wms_out,
      ))
      WhatIsMyIPServiceMock.return_value = WhatIsMyIPServiceMockObject

      lcs = LocationChangerService(
        'api_key',
        {},
        'openvpnexec',
      )
      success_response, response_msg = lcs.connect_region(
        country,
        0,
      )

      OpenVPNServiceMockObject.connect.assert_called_with(country)
      WhatIsMyIPServiceMockObject.validate_connection.assert_called_once_with(country)

      self.assertEqual(
        success_response,
        tc['expected']['success'],
        msg = tc['case_name']
      )
      self.assertEqual(
        response_msg,
        tc['expected']['msg'],
        msg = tc['case_name']
      )
