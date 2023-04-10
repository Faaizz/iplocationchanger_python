from __future__ import annotations

import subprocess
import requests
import logging

logger = logging.getLogger(__name__)

class Utils:
  @classmethod
  def run_proc(cls: Utils, cmd: list[str], expect_error=False) -> tuple[bool, str, str]:
    try:
      logger.debug(f'CMD: {cmd}')
      proc = subprocess.run(
        cmd,
        capture_output = True,
        check = True,
      )
      success = proc.returncode == 0

      stdout = proc.stdout.decode('utf-8')
      stderr = proc.stderr.decode('utf-8')
      logger.debug(f'STDOUT: {stdout}')
      logger.debug(f'STDERR: {stderr}')

      return (
        success,
        stdout,
        stderr,
      )
    except Exception as e:
      logger.debug(e, exc_info=True)
      if expect_error:
        return (
          True,
          'execution failed',
          '',
        )
      raise e

  @classmethod
  def exec_get_request(cls: Utils, url: str) -> tuple[bool, str]:
    logger.debug(f'URL: {url}')
    res = requests.get(url)
    success = res.status_code > 199 and res.status_code < 300
    res_body = res.content.decode('utf-8')
    logger.debug(f'RESPONSE: {res_body}')
    return success, res_body

  @classmethod
  def extract_location(cls: Utils, location_str: str) -> str:
    logger.debug(f'LOCATION STR: {location_str}')
    cty_idx = location_str.find('country')
    country_code = location_str[cty_idx:].split(':')[1].split('\r\n')[0].strip()
    logger.debug(f'CTR CODE: {country_code}')
    return country_code
