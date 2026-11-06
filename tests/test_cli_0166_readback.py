"""CLI-level replay of the two 0.166.0 observations, using only in-memory pipes."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import test_active_chat as fixtures

active = fixtures.active


class ReadbackCases(unittest.TestCase):
    def inspect(self, wire=b'', diagnostic=b''):
        proc = mock.Mock(stdin=io.BytesIO(), stdout=io.BytesIO(wire),
                         stderr=io.BytesIO(diagnostic))
        proc.poll.return_value = 1 if not wire else None
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(active.subprocess, 'Popen', return_value=proc) as launch, \
             mock.patch.object(active.os, 'urandom', side_effect=lambda n: b'K' * n), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = active.main(['inspect', '--chat-id', 'chat-one'])
        self.assertEqual(launch.call_count, 1)
        self.assertEqual(launch.call_args.args[0], ['codex', 'app-server', 'proxy'])
        if rc:
            self.assertEqual(rc, 2)
            self.assertEqual(out.getvalue(), '')
            self.assertNotIn('/private/fixture', err.getvalue())
            error = json.loads(err.getvalue())
            self.assertEqual(error['selection_status'], 'unknown')
            self.assertFalse(error['selection_confirmed'])
            self.assertNotIn('thread', error)
            return error
        return json.loads(out.getvalue())

    def test_sandbox_path_alias_warning_and_socket_enoent(self):
        result = self.inspect(diagnostic=(
            b'WARNING: proceeding, even though we could not create PATH aliases: '
            b'Operation not permitted (os error 1)\n'
            b'Error: failed to connect to socket at /private/fixture\n'
            b'Caused by: No such file or directory (os error 2)'
        ))
        self.assertEqual(result['code'], 'socket_not_found')
        self.assertFalse(result.get('requires_host_approval', False))

    def test_approved_proxy_exit_missing_endpoint(self):
        result = self.inspect(diagnostic=(
            b'Error: failed to connect to socket at /private/fixture\n'
            b'Caused by: No such file or directory (os error 2)'
        ))
        self.assertEqual(result['code'], 'socket_not_found')
        self.assertFalse(result.get('requires_host_approval', False))

    def test_genuine_socket_denial(self):
        result = self.inspect(diagnostic=(
            b'failed to connect to socket at /private/fixture\n'
            b'Operation not permitted (os error 1)'
        ))
        self.assertEqual(result['code'], 'socket_permission_denied')
        self.assertTrue(result['requires_host_approval'])

    def test_silent_eof_keeps_cause_unknown(self):
        self.assertEqual(self.inspect()['code'], 'proxy_eof_before_reply')

    def test_incompatible_response(self):
        for wire in (b'HTTP/1.1 200 OK\r\n\r\n', b'{"unsupported":"reply"}\n',
                     fixtures.upgrade_response() + fixtures.server_frame(b'bad json'),
                     fixtures.upgrade_response() + fixtures.server_frame({'id': 1, 'result': []})):
            with self.subTest(wire=wire):
                self.assertEqual(self.inspect(wire)['code'], 'incompatible_proxy_reply')

    def test_incomplete_selection(self):
        thread = {'id':'chat-one', 'model':'model-b', 'status':{'type':'notLoaded'}}
        wire = (fixtures.upgrade_response() + fixtures.server_frame({'id':1,'result':{}})
                + fixtures.server_frame({'id':2,'result':{'thread':thread}}))
        self.assertEqual(self.inspect(wire)['code'], 'incomplete_selection')

    def test_verification_requires_each_expected_field(self):
        observed = self.inspect(fixtures.upgrade_response() + fixtures.metadata_reply())
        exact = {'chat_id':'chat-one', 'model':'model-b', 'effort':'medium'}
        with tempfile.TemporaryDirectory() as tmp:
            request, readback = Path(tmp)/'request.json', Path(tmp)/'readback.json'
            readback.write_text(json.dumps(observed))
            for difference in ({}, {'chat_id':'another'}, {'model':'other'}, {'effort':'high'}):
                with self.subTest(difference=difference):
                    request.write_text(json.dumps({'action':'native_request', 'expected':{**exact, **difference}}))
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        rc = active.main(['verify', '--request', str(request), '--readback', str(readback)])
                    self.assertEqual(rc, 2 if difference else 0)
                    value = json.loads(err.getvalue() if difference else out.getvalue())
                    self.assertEqual(value['selection_confirmed'], not difference)
                    if difference:
                        self.assertEqual(value['selection_status'], 'unknown')
                    self.assertFalse(value['execution_confirmed'])
