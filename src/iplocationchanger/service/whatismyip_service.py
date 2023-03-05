from __future__ import annotations

import logging

from iplocationchanger.utils.utils import Utils

logger = logging.getLogger(__name__)

class WhatIsMyIPService:
  def __init__(
    self: WhatIsMyIPService,
    api_key: str,
  ) -> None:
    if len(api_key) <= 0:
      raise Exception('Invalid API Key')
    self.api_key = api_key

  def get_ip(self: WhatIsMyIPService) -> tuple[bool, str]:
    url =  f'https://api.whatismyip.com/ip.php?key={self.api_key}'

    success, res_body = Utils.exec_get_request(url)
    if not success:
      logger.error(res_body)
    return success, res_body

  def get_location_from_ip(
    self: WhatIsMyIPService, 
    ip: str,
  ) -> tuple[bool, str]:
    url = f'https://api.whatismyip.com/ip-address-lookup.php?key={self.api_key}&input={ip}'
    
    success, res_body = Utils.exec_get_request(url)
    if not success:
      logger.error(res_body)
    return success, res_body

  def validate_connection(
    self: WhatIsMyIPService, 
    country_code: str
  ) -> str:
    success, ip = self.get_ip()
    if not success:
      return success, f'could not obtain IP address: {ip}'
    success, location_result = self.get_location_from_ip(ip)
    if not success:
      return success, f'could not obtain location: {location_result}'
    pulled_country_code = Utils.extract_location(location_result)
    if (pulled_country_code.lower().strip() == country_code.lower().strip()):
      return True, 'success'
    return False, f'{country_code} not {pulled_country_code}'
