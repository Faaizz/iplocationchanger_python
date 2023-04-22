from __future__ import annotations

import json
import logging

from iplocationchanger.exception.whatismyip_response_exception import WhatIsMyIPResponseException

logger = logging.getLogger(__name__)

class WhatIsMyIPResponse:
  TYPE_IP = 'ip'
  TYPE_LOCATION = 'location'

  def __init__(
    self: WhatIsMyIPResponse,
    response_content: bytes,
  ) -> None:
    self.check_error(response_content)
    try:
      content_dict = json.loads(response_content)
      logger.debug(f'response dict: {content_dict}')
    except json.decoder.JSONDecodeError as e:
      raise WhatIsMyIPResponseException('Invalid JSON') from e
    
    # Identify response type
    self.type = None
    self.ip = None
    self.location = None
    try:
      self.ip = content_dict['ip_address']
      self.type = WhatIsMyIPResponse.TYPE_IP
    except KeyError:
      pass
    try:
      self.location = content_dict['ip_address_lookup'][0]["country"]
      self.type = WhatIsMyIPResponse.TYPE_LOCATION
    except KeyError:
      pass

    if self.type is None:
      raise WhatIsMyIPResponseException('Could not identify response type')
    logger.debug(f'response type: {self.type}')


  def check_error(
    self: WhatIsMyIPResponse,
    content: str,
  ) -> tuple[bool, str]:
    msg = ''
    if content.lower().strip() == '0':
      msg = 'API key was not entered'
    if content.lower().strip() == '1':
      msg = 'API key is invalid'
    if content.lower().strip() == '2':
      msg = 'API key is inactive'
    if content.lower().strip() == '3':
      msg = 'Too many lookups'
    if content.lower().strip() == '4':
      msg = 'No input'
    if content.lower().strip() == '5':
      msg = 'Invalid input'
    if content.lower().strip() == '6':
      msg = 'Unknown error'

    if msg != '':
      raise WhatIsMyIPResponseException(msg)

  def __repr__(self: WhatIsMyIPResponse) -> str:
    return f'WhatIsMyIPResponse(type={self.type}, ip={self.ip}, location={self.location})'
