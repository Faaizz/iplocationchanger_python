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
