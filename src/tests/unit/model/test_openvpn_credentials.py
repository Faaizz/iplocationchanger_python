import unittest

from unittest.mock import patch
from unittest.mock import call
from unittest.mock import Mock

from iplocationchanger.model.openvpn_credentials import OpenVPNCredentials

class TestOpenVPNCredentials(unittest.TestCase):
  @patch('iplocationchanger.model.openvpn_credentials.open')
  @patch('iplocationchanger.model.openvpn_credentials.TemporaryDirectory')
  def test_init(self, TemporaryDirectoryMock, open_mock):
    f_ptr_write_mock = Mock()
    f_ptr_mock = Mock()
    f_ptr_mock.write = f_ptr_write_mock
    open_mock_return = Mock()
    open_mock_return.__enter__ = Mock(return_value=f_ptr_mock)
    open_mock_return.__exit__ = Mock()
    open_mock.return_value = open_mock_return

    tmp_dir_path = '/temp/dir'
    tdm = Mock()
    tdm.name = tmp_dir_path
    tdm_cleanup = Mock()
    tdm.cleanup = tdm_cleanup
    TemporaryDirectoryMock.return_value = tdm
    
    user = 'username'
    password = 'password'
    ovnc = OpenVPNCredentials(user, password)

    credentials_path = tmp_dir_path + '/openvpn_credentials'
    open_mock.assert_called_once_with(credentials_path, 'w')

    f_ptr_write_mock.assert_has_calls(
      [
        call(f'{user}\n'),
        call(f'{password}\n'),
      ],
    )

    self.assertEqual(
      ovnc.file_path(),
      credentials_path,
    )

    del(ovnc)
    tdm_cleanup.assert_called_once()
