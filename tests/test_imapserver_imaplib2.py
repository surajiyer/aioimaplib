import asyncio

import functools
from imaplib2 import imaplib2
from mock import Mock
from tests import imapserver
from tests.imapserver import imap_receive, Mail, get_imapconnection
from tests.test_imapserver import WithImapServer


class TestImapServerIdle(WithImapServer):
    @asyncio.coroutine
    def test_idle(self):
        imap_client = yield from self.login_user('user', 'pass', select=True, lib=imaplib2.IMAP4)
        idle_callback = Mock()
        self.loop.run_in_executor(None, functools.partial(imap_client.idle, callback=idle_callback))
        yield from asyncio.wait_for(get_imapconnection('user').wait(imapserver.IDLE), 1)

        self.loop.run_in_executor(None, functools.partial(imap_receive, Mail(to=['user'], mail_from='me', subject='hello')))

        yield from asyncio.wait_for(get_imapconnection('user').wait(imapserver.SELECTED), 1)
        yield from asyncio.sleep(0.1) # eurk hate sleeps but I don't know how to wait for the lib to receive end of IDLE
        idle_callback.assert_called_once()
