import unittest

from unittest.mock import Mock
from unittest.mock import patch

from iplocationchanger.service.location_changer_service import LocationChangerService
from iplocationchanger.exception.location_changer_service_exception import LocationChangerServiceException
from iplocationchanger.exception.whatismyip_service_exception import WhatIsMyIPServiceException
from iplocationchanger.exception.openvpn_service_exception import OpenVPNServiceException

class TestLocationChangerService(unittest.TestCase):
  @patch('iplocationchanger.service.location_changer_service.OpenVPNService')
  def test_disconnect_region(self, OpenVPNServiceMock):
    OpenVPNServiceMockObject = Mock()
    OpenVPNServiceMockObject.disconnect = Mock()
    OpenVPNServiceMock.return_value = OpenVPNServiceMockObject

    lcs = LocationChangerService(
      'api_key',
      {},
      'openvpnexec',
    )
    lcs.disconnect_region()

    OpenVPNServiceMockObject.disconnect.assert_called_once_with()

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

    country = 'DE'
    OpenVPNServiceMockObject = Mock()
    OpenVPNServiceMockObject.connect = Mock()
    OpenVPNServiceMock.return_value = OpenVPNServiceMockObject
    WhatIsMyIPServiceMockObject = Mock()
    WhatIsMyIPServiceMockObject.validate_connection = Mock()
    WhatIsMyIPServiceMock.return_value = WhatIsMyIPServiceMockObject

    lcs = LocationChangerService(
      'api_key',
      {},
      'openvpnexec',
    )
    lcs.connect_region(
      country,
      0,
    )
    OpenVPNServiceMockObject.connect.assert_called_once_with(country)
    WhatIsMyIPServiceMockObject.validate_connection.assert_called_once_with(country)

    # OpenVPNServiceException
    OpenVPNServiceMockObject = Mock()
    OpenVPNServiceMockObject.connect = Mock(side_effect=OpenVPNServiceException(''))
    OpenVPNServiceMock.return_value = OpenVPNServiceMockObject
    WhatIsMyIPServiceMockObject = Mock()
    WhatIsMyIPServiceMockObject.validate_connection = Mock()
    WhatIsMyIPServiceMock.return_value = WhatIsMyIPServiceMockObject

    with self.assertRaises(LocationChangerServiceException):
      lcs = LocationChangerService(
        'api_key',
        {},
        'openvpnexec',
      )
      lcs.connect_region(
        country,
        0,
      )

    # WhatIsMyIPServiceException
    OpenVPNServiceMockObject = Mock()
    OpenVPNServiceMockObject.connect = Mock()
    OpenVPNServiceMock.return_value = OpenVPNServiceMockObject
    WhatIsMyIPServiceMockObject = Mock()
    WhatIsMyIPServiceMockObject.validate_connection = Mock(side_effect=WhatIsMyIPServiceException(''))
    WhatIsMyIPServiceMock.return_value = WhatIsMyIPServiceMockObject
    with self.assertRaises(LocationChangerServiceException):
      lcs = LocationChangerService(
        'api_key',
        {},
        'openvpnexec',
      )
      lcs.connect_region(
        country,
        0,
      )
