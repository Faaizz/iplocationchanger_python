from __future__ import annotations

import subprocess
import requests
import logging

logger = logging.getLogger(__name__)

class Utils:
  @classmethod
  def run_proc(cls: Utils, cmd: list[str], expect_error=False) -> tuple[bool, str, str]:
    try:
      proc = subprocess.run(
        cmd,
        capture_output = True,
        check = True,
      )
      success = proc.returncode == 0

      return (
        success,
        proc.stdout.decode('utf-8'),
        proc.stderr.decode('utf-8'),
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
    res = requests.get(url)
    success = res.status_code > 199 and res.status_code < 300
    res_body = res.content.decode('utf-8')
    return success, res_body

  @classmethod
  def extract_location(cls: Utils, location_str: str) -> str:
    cty_idx = location_str.find('country')
    country_code = location_str[cty_idx:].split(':')[1].split('\r\n')[0].strip()
    return country_code
