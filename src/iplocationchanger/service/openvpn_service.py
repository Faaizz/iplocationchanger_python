from __future__ import annotations
from tempfile import TemporaryDirectory

import logging
import os

from iplocationchanger.utils.utils import Utils

logger = logging.getLogger(__name__)

ASSETS_DIR = os.getcwd() + '/assets'

class OpenVPNService:

  def __init__(
    self: OpenVPNService,
    config_to_country: dict,
    openvpn_executable_path: str,
    credentials_path: str='',
  ):
    self.config_to_country = config_to_country

    self.has_credentials = False
    if len(credentials_path) > 0:
      self.credentials_path = credentials_path
      self.has_credentials = True

    self.openvpn_executable_path = openvpn_executable_path
    self.daemon_name = 'openvpn_iplocationchanger'

  def disconnect(self: OpenVPNService) -> tuple[bool, str, str]:
    cmd = ['sudo', 'killall', 'openvpn']
    _, stdout, stderr = Utils.run_proc(cmd, expect_error=True)
    if stderr != '':
      logger.error(stderr)
    success = True
    return success, stdout, stderr

  def connect(self: OpenVPNService, country: str) -> tuple[bool, str, str]:
    try:
      config_path = self.config_to_country[country]
    except KeyError as e:
      logger.debug(e)
      return False, '', 'no config for specified country'

    cmd = [
      'sudo', self.openvpn_executable_path,
      '--auth-retry', 'nointeract',
      '--config', config_path,
      '--script-security', '2',
      '--daemon', self.daemon_name,
    ]
    if self.has_credentials:
      cmd.extend(['--auth-user-pass', self.credentials_path])

    success, stdout, stderr =  Utils.run_proc(cmd)

    if not success:
      logger.error(stderr)
    return success, stdout, stderr
  