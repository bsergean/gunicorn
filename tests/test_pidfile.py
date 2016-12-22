# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.

import errno
import sys

try:
    import unittest.mock as mock
except ImportError:
    import mock

import gunicorn.pidfile


def mock_patch_builtin(name):
    if sys.version_info >= (3, 0):
        module = 'builtins'
    else:
        module = '__builtin__'

    def patcher(func):
        full_name = '{0}.{1}'.format(module, name)
        return mock.patch(full_name)(func)

    return patcher


@mock_patch_builtin('open')
def test_validate_no_file(_open):
    pidfile = gunicorn.pidfile.Pidfile('test.pid')
    _open.side_effect = IOError(errno.ENOENT)
    assert pidfile.validate() is None


@mock_patch_builtin('open')
@mock.patch('os.kill')
def test_validate_file_pid_exists(kill, _open):
    pidfile = gunicorn.pidfile.Pidfile('test.pid')
    fileobj = mock.MagicMock()
    fileobj.read.return_value = '1'
    ctx = mock.MagicMock()
    ctx.__enter__ = mock.Mock(return_value=fileobj)
    _open.return_value = ctx
    assert pidfile.validate() == 1


@mock_patch_builtin('open')
def test_validate_file_pid_malformed(_open):
    pidfile = gunicorn.pidfile.Pidfile('test.pid')
    fileobj = mock.MagicMock()
    fileobj.read.return_value = 'a'
    ctx = mock.MagicMock()
    ctx.__enter__ = mock.Mock(return_value=fileobj)
    _open.return_value = ctx
    assert pidfile.validate() is None


@mock_patch_builtin('open')
@mock.patch('os.kill')
def test_validate_file_pid_exists_kill_exception(kill, _open):
    pidfile = gunicorn.pidfile.Pidfile('test.pid')
    fileobj = mock.MagicMock()
    fileobj.read.return_value = '1'
    ctx = mock.MagicMock()
    ctx.__enter__ = mock.Mock(return_value=fileobj)
    _open.return_value = ctx
    kill.side_effect = OSError(errno.EPERM)
    assert pidfile.validate() == 1


@mock_patch_builtin('open')
@mock.patch('os.kill')
def test_validate_file_pid_does_not_exist(kill, _open):
    pidfile = gunicorn.pidfile.Pidfile('test.pid')
    fileobj = mock.MagicMock()
    fileobj.read.return_value = '1'
    ctx = mock.MagicMock()
    ctx.__enter__ = mock.Mock(return_value=fileobj)
    _open.return_value = ctx
    kill.side_effect = OSError(errno.ESRCH)
    assert pidfile.validate() is None
