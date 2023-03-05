from __future__ import annotations

import logging
import time

from iplocationchanger.service.openvpn_service import OpenVPNService
from iplocationchanger.service.whatismyip_service import WhatIsMyIPService

logger = logging.getLogger(__name__)

class LocationChangerService:
  def __init__(
    self: LocationChangerService,
    whatismyip_api_key: str,
    openvpn_config_to_country_map: dict,
    openvpn_executable_path: str,
    openvpn_credentials_path: str = '',
  ) -> None:
    """Initialize LocationChangerService.
    Sample usage: 
    try:
      lcs = LocationChangerService(
        'whatismyip_api_key',
        'openvpn_config_to_country_map',
        'openvpn_executable_path',
        'openvpn_credentials_path',
      )
    finally:
      # Disconnect VPN connection
      lcs.disconnect_region()
    """
    self.wms = WhatIsMyIPService(whatismyip_api_key)
    self.ovs = OpenVPNService(
      openvpn_config_to_country_map,
      openvpn_executable_path,
      credentials_path=openvpn_credentials_path,
    )

  def disconnect_region(
    self: LocationChangerService,
  ) -> tuple[bool, str]:
    logger.info('disconnecting...')
    success, stdout, stderr = self.ovs.disconnect()
    return success, (stdout + stderr)

  def connect_region(
    self: LocationChangerService,
    country: str,
    OPENVPN_DELAY: int = 5,
  ) -> tuple[bool, str]:
    logger.info(f'connecting to {country}...')
    success, stdout, stderr = self.ovs.connect(country)
    # buy openvpn some time
    time.sleep(OPENVPN_DELAY)
    valid_connection, out = self.wms.validate_connection(country)
    return (success and valid_connection), (stdout + stderr + out)
