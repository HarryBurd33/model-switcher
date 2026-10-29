#!/usr/bin/env python3
"""Guard native same-chat selection requests and inspect selection metadata.

This helper never sends chat messages or starts/resumes a model turn. Authorization,
catalog and resource fields are fresh operator attestations, not recovered permissions.
The caller owns checkpointing, the task lease and durable intent/outcome recording.
"""
import argparse
import base64
import hashlib
import hmac
import os
import struct
import datetime as dt
import json
from pathlib import Path
import queue
import re
import stat
import subprocess
import sys
import threading
import time


class GuardError(ValueError):
    pass


class SocketPermissionError(GuardError):
    """An observation failure requiring the host's normal approval boundary."""
    code = 'socket_permission_denied'


def socket_permission_denied(stderr):
    text = stderr.decode('utf-8', errors='replace').lower()
    return 'failed to connect to socket' in text and any(
        word in text for word in ('operation not permitted', 'permission denied', 'access is denied'))



def require(condition, message):
    if not condition:
        raise GuardError(message)


def token(value, label, maximum=128):
    require(isinstance(value, str) and 0 < len(value) <= maximum
            and re.fullmatch(r'[A-Za-z0-9_.:-]+', value), 'Invalid ' + label)
    return value


def timestamp(value):
    require(isinstance(value, str), 'Timestamp is unknown')
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise GuardError('Invalid timestamp')
    require(parsed.tzinfo is not None and parsed.utcoffset() is not None,
            'Timezone-aware timestamp required')
    return parsed


def fresh(value, now):
    age = (now - timestamp(value)).total_seconds()
    require(0 <= age <= 120, 'Observation is stale or future-dated')


def object_field(context, field):
    value = context.get(field)
    require(isinstance(value, dict), field + ' is unknown or invalid')
    return value


def plan(context, now=None):
    """Return native tool arguments only after all declared guards pass."""
    require(isinstance(context, dict), 'Context must be an object')
    now = now or dt.datetime.now(dt.timezone.utc)
    chat = token(context.get('chat_id'), 'chat id')
    require(chat == context.get('current_chat_id'), 'Target is not the current chat')
    require(context.get('host_id') == 'local', 'Only the verified local host is supported')
    operation = token(context.get('operation_id'), 'operation id', 80)
    model = token(context.get('target_model'), 'model')
    effort = token(context.get('target_effort'), 'effort', 20)
    require(effort in ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra'),
            'Effort is not supported by the native tool')
    auth = object_field(context, 'authorization')
    require(auth.get('confirmed') is True and isinstance(auth.get('source'), str)
            and bool(auth['source'].strip()), 'Current human authorization is required')
    resources = object_field(context, 'resources')
    fresh(resources.get('observed_at'), now)
    require(resources.get('ordinary_usage_allowed') is True and resources.get('reserve_ok') is True,
            'Resource stop or unknown resource sufficiency')
    pending = context.get('pending_operations')
    require(isinstance(pending, list), 'Pending-operation state is unknown')
    require(not pending, 'An active or uncertain selection operation blocks another request')
    catalog = object_field(context, 'catalog')
    fresh(catalog.get('observed_at'), now)
    models = catalog.get('data')
    require(isinstance(models, list), 'Model catalog is unknown')
    matches = [item for item in models if isinstance(item, dict) and item.get('model') == model]
    require(len(matches) == 1, 'Target model is unavailable or ambiguous')
    efforts = matches[0].get('efforts')
    require(isinstance(efforts, list) and effort in efforts, 'Target effort is unavailable')
    expected = {'chat_id': chat, 'model': model, 'effort': effort}
    result = {'action': 'native_request', 'operation_id': operation, 'expected': expected,
              'claim_scope': 'configured_for_subsequent_turns', 'execution_confirmed': False}
    current = context.get('current_selection')
    if isinstance(current, dict) and current.get('model') == model and current.get('effort') == effort:
        return dict(result, action='no_op')
    prompt = ('Model Switcher configuration cue, operation ' + operation + '. '
              'Select ' + model + ' with ' + effort + ' reasoning for subsequent turns '
              'of this same chat. Keep the current task and authority intact. Do not '
              'restart or duplicate work, repost this cue, create a worker, or claim '
              'that in-flight inference changed. The coordinator must verify host readback.')
    result['tool'] = 'mcp__codex_app__send_message_to_thread'
    result['arguments'] = {'threadId': chat, 'hostId': 'local', 'model': model,
                           'thinking': effort, 'prompt': prompt}
    return result


def verify(request, readback, now=None):
    """Confirm only configured/persisted selection, never per-turn execution."""
    require(isinstance(request, dict) and request.get('action') in ('native_request', 'no_op'),
            'Invalid prepared request')
    expected = object_field(request, 'expected')
    require(set(expected) == {'chat_id', 'model', 'effort'}, 'Invalid expected selection')
    for label, value in expected.items():
        token(value, label)
    require(isinstance(readback, dict)
            and readback.get('source') == 'codex-app-server-thread-read'
            and readback.get('transport') == 'existing-server-proxy-websocket'
            and readback.get('server_start_attempted') is False,
            'Trusted host readback source is required')
    fresh(readback.get('observed_at'), now or dt.datetime.now(dt.timezone.utc))
    thread = object_field(readback, 'thread')
    require(thread.get('id') == expected['chat_id'], 'Readback belongs to another chat')
    require(thread.get('model') == expected['model']
            and thread.get('reasoningEffort') == expected['effort'], 'Selection readback mismatch')
    status = thread.get('status')
    require(isinstance(status, dict), 'Thread loading state is unknown')
    kind = status.get('type')
    require(kind in ('notLoaded', 'active', 'idle', 'loaded', 'systemError'),
            'Thread loading state is unknown')
    return {'selection_confirmed': True, 'execution_confirmed': False,
            'claim_scope': 'configured_for_subsequent_turns',
            'transport': 'existing-server-proxy-websocket',
            'server_start_attempted': False,
            'metadata_scope': 'latest_persisted' if kind == 'notLoaded' else 'current_configured',
            'expected': expected}


HEADER_LIMIT = 8192
FRAME_LIMIT = 1024 * 1024
WIRE_LIMIT = 4 * FRAME_LIMIT
MESSAGE_LIMIT = 64
WS_GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'


class ProxyChannel:
    """Bounded binary pipe IO; no server spawn, retry or arbitrary RPC dispatch."""
    def __init__(self, process, deadline):
        self.process, self.deadline = process, deadline
        self.buffer = bytearray()
        self.items = queue.Queue(maxsize=16)
        self.stopped = threading.Event()
        self.workers = []
        self.stderr_prefix = bytearray()
        self.stderr_done = threading.Event()
        error_reader = threading.Thread(target=self._receive_stderr, daemon=True)
        error_reader.start(); self.workers.append(error_reader)
        reader = threading.Thread(target=self._receive, daemon=True)
        reader.start()
        self.workers.append(reader)

    def _receive_stderr(self):
        # Drain continuously while retaining only a bounded diagnostic prefix.
        try:
            while not self.stopped.is_set():
                chunk = self.process.stderr.read(4096)
                if not isinstance(chunk, bytes) or not chunk:
                    break
                room = 8192 - len(self.stderr_prefix)
                if room > 0:
                    self.stderr_prefix.extend(chunk[:room])
        except (OSError, ValueError):
            pass
        finally:
            self.stderr_done.set()

    def remaining(self):
        remaining = self.deadline - time.monotonic()
        require(remaining > 0, 'Existing-server metadata probe timed out')
        return remaining

    def _put(self, value):
        while not self.stopped.is_set():
            try:
                self.items.put(value, timeout=.05)
                return
            except queue.Full:
                pass

    def _receive(self):
        total = 0
        try:
            while not self.stopped.is_set():
                chunk = self.process.stdout.read(4096)
                if not chunk:
                    self._put(None)
                    return
                total += len(chunk)
                if total > WIRE_LIMIT:
                    self._put(GuardError('Existing-server proxy output exceeds bound'))
                    return
                self._put(chunk)
        except (OSError, ValueError):
            self._put(GuardError('Existing-server proxy input unavailable'))

    def _next(self):
        try:
            value = self.items.get(timeout=self.remaining())
        except queue.Empty:
            raise GuardError('Existing-server metadata probe timed out')
        if isinstance(value, GuardError):
            raise value
        require(value is not None, 'Existing-server proxy exited before reply; no fallback')
        require(isinstance(value, bytes), 'Proxy must provide binary WebSocket data')
        self.buffer.extend(value)

    def read_exact(self, count):
        require(0 <= count <= FRAME_LIMIT, 'WebSocket frame exceeds bound')
        while len(self.buffer) < count:
            self._next()
        self.remaining()
        value = bytes(self.buffer[:count]); del self.buffer[:count]
        return value

    def read_headers(self):
        while True:
            end = self.buffer.find(b'\r\n\r\n')
            if end >= 0:
                require(end + 4 <= HEADER_LIMIT, 'WebSocket headers exceed bound')
                value = bytes(self.buffer[:end]); del self.buffer[:end+4]
                return value
            require(len(self.buffer) <= HEADER_LIMIT, 'WebSocket headers exceed bound')
            self._next()

    def write(self, data):
        require(len(data) <= HEADER_LIMIT, 'Fixed metadata request exceeds bound')
        result = queue.Queue(maxsize=1)
        def send():
            try:
                view = memoryview(data)
                while view:
                    if self.stopped.is_set():
                        raise GuardError('Existing-server proxy stopped')
                    self.remaining()
                    size = self.process.stdin.write(view)
                    require(isinstance(size, int) and 0 < size <= len(view), 'Proxy write made no progress')
                    view = view[size:]
                self.process.stdin.flush()
                result.put(None)
            except (OSError, ValueError) as error:
                result.put(error)
        worker = threading.Thread(target=send, daemon=True)
        worker.start(); self.workers.append(worker)
        try:
            error = result.get(timeout=self.remaining())
        except queue.Empty:
            raise GuardError('Existing-server proxy write timed out')
        require(error is None, 'Existing-server proxy write unavailable; no fallback')


def websocket_upgrade(channel):
    key = base64.b64encode(os.urandom(16)).decode('ascii')
    request = ('GET / HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\n'
               'Connection: Upgrade\r\nSec-WebSocket-Version: 13\r\n'
               'Sec-WebSocket-Key: ' + key + '\r\n\r\n')
    channel.write(request.encode('ascii'))
    try:
        lines = channel.read_headers().decode('ascii').split('\r\n')
    except UnicodeError:
        raise GuardError('Invalid WebSocket upgrade headers')
    require(lines[0].split(' ', 2)[:2] == ['HTTP/1.1', '101'], 'Existing server refused WebSocket upgrade')
    headers = {}
    for line in lines[1:]:
        require(':' in line and not line.startswith((' ', '\t')), 'Malformed WebSocket header')
        name, value = line.split(':', 1); name = name.lower()
        require(re.fullmatch(r"[!#$%&'*+.^_`|~0-9a-z-]+", name) and name not in headers,
                'Invalid or duplicate WebSocket header')
        headers[name] = value.strip()
    expected = base64.b64encode(hashlib.sha1((key + WS_GUID).encode('ascii')).digest()).decode('ascii')
    require(headers.get('upgrade', '').lower() == 'websocket'
            and 'upgrade' in [x.strip().lower() for x in headers.get('connection', '').split(',')]
            and hmac.compare_digest(headers.get('sec-websocket-accept', ''), expected),
            'WebSocket upgrade validation failed')
    require('sec-websocket-extensions' not in headers and 'sec-websocket-protocol' not in headers,
            'Unrequested WebSocket extension or subprotocol')


def websocket_send(channel, payload, opcode=1):
    require(opcode in (1, 10) and len(payload) <= HEADER_LIMIT - 14, 'Invalid outgoing metadata frame')
    mask = os.urandom(4); size = len(payload)
    prefix = bytes([0x80 | opcode, 0x80 | size]) if size < 126 else bytes([0x80 | opcode, 0xfe]) + struct.pack('!H', size)
    channel.write(prefix + mask + bytes(value ^ mask[i % 4] for i, value in enumerate(payload)))


def websocket_receive(channel):
    first, second = channel.read_exact(2)
    require(first & 0x80 and not first & 0x70, 'Fragmented or extended WebSocket frames unsupported')
    require(not second & 0x80, 'Server WebSocket frame must not be masked')
    opcode, size = first & 0x0f, second & 0x7f
    require(opcode in (1, 8, 9, 10), 'Unsupported WebSocket frame opcode')
    if size == 126:
        size = struct.unpack('!H', channel.read_exact(2))[0]
        require(size >= 126, 'Noncanonical WebSocket length')
    elif size == 127:
        size = struct.unpack('!Q', channel.read_exact(8))[0]
        require(65536 <= size < 2**63, 'Noncanonical WebSocket length')
    require(size <= FRAME_LIMIT and (opcode == 1 or size <= 125), 'WebSocket frame exceeds bound')
    payload = channel.read_exact(size)
    if opcode == 8:
        raise GuardError('Existing-server WebSocket closed before reply')
    if opcode == 9:
        websocket_send(channel, payload, opcode=10)
        return None
    if opcode == 10:
        return None
    try:
        value = json.loads(payload.decode('utf-8'))
    except (UnicodeError, ValueError):
        raise GuardError('Invalid WebSocket metadata JSON')
    require(isinstance(value, dict), 'Metadata message must be an object')
    return value


def inspect_selection(chat_id, executable='codex', timeout=20, include_catalog=False):
    """Attach to the existing server through proxy WebSocket pipes; never auto-start.

    Only initialize, initialized, thread/read and optional model/list are sent. Unsupported framing,
    absence or uncertainty blocks. Deadlines bound userspace waits and cleanup;
    uninterruptible OS operations are not a hard real-time guarantee.
    """
    token(chat_id, 'chat id')
    require(isinstance(timeout, (int, float)) and not isinstance(timeout, bool)
            and 1 <= timeout <= 60, 'Probe timeout must be 1–60 seconds')
    deadline = time.monotonic() + timeout
    work_deadline = deadline - min(2, timeout / 2)
    process = subprocess.Popen([executable, 'app-server', 'proxy'], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
    channel = None
    messages_seen = 0
    def send(message):
        websocket_send(channel, json.dumps(message, separators=(',', ':')).encode('utf-8'))
    def request(ident, method, params):
        nonlocal messages_seen
        send({'id': ident, 'method': method, 'params': params})
        while True:
            channel.remaining()
            messages_seen += 1
            require(messages_seen <= MESSAGE_LIMIT, 'Metadata message count exceeds bound')
            value = websocket_receive(channel)
            if value is None:
                continue
            require(not ('method' in value and 'id' in value), 'Unexpected server request')
            if value.get('id') == ident:
                require('error' not in value and isinstance(value.get('result'), dict),
                        'Existing-server metadata method unavailable')
                return value['result']
    try:
        channel = ProxyChannel(process, work_deadline)
        websocket_upgrade(channel)
        request(1, 'initialize', {'clientInfo': {'name': 'model_switcher_selection_probe',
                                               'version': '0.3.1'}})
        send({'method': 'initialized', 'params': {}})
        data = request(2, 'thread/read', {'threadId': chat_id, 'includeTurns': False})
        thread = object_field(data, 'thread')
        require(thread.get('id') == chat_id, 'Probe returned another chat')
        result = {'source': 'codex-app-server-thread-read',
                'transport': 'existing-server-proxy-websocket', 'server_start_attempted': False,
                'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                'thread': {key: thread.get(key) for key in
                           ('id', 'model', 'reasoningEffort', 'modelProvider', 'status')}}
        if include_catalog:
            catalog = request(3, 'model/list', {'limit': 100, 'includeHidden': False})
            require(isinstance(catalog.get('data'), list) and not catalog.get('nextCursor'),
                    'Complete live model catalog unavailable')
            models = []
            for item in catalog['data']:
                require(isinstance(item, dict), 'Invalid live model catalog')
                efforts = item.get('supportedReasoningEfforts', [])
                require(isinstance(efforts, list), 'Invalid live model efforts')
                models.append({'model': item.get('model'), 'efforts': [
                    x.get('reasoningEffort') if isinstance(x, dict) else x for x in efforts]})
            result['catalog'] = {'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                                 'source': 'existing-server-model-list', 'data': models}
        return result
    except GuardError:
        if channel is not None:
            channel.stderr_done.wait(timeout=max(0, min(.1, deadline-time.monotonic())))
            if socket_permission_denied(bytes(channel.stderr_prefix)):
                raise SocketPermissionError(
                    "Host denied access to the existing Codex daemon socket. Use the host's "
                    "approved read-only command boundary when authorized; do not change socket "
                    "permissions, profiles, or start a server.") from None
        raise
    finally:
        if channel is not None:
            channel.stopped.set()
        try:
            if process.poll() is None:
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass
            process.wait(timeout=max(0, min(1, (deadline - time.monotonic()) / 2)))
        except subprocess.TimeoutExpired:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=max(0, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                raise GuardError('Existing-server proxy cleanup outcome unknown')
        finally:
            process.stdin.close(); process.stdout.close(); process.stderr.close()
            for worker in channel.workers if channel is not None else []:
                worker.join(timeout=max(0, deadline - time.monotonic()))
        require(channel is None or not any(worker.is_alive() for worker in channel.workers),
                'Existing-server proxy IO cleanup outcome unknown')


def read_json(path):
    path = Path(path)
    require(not path.is_symlink() and stat.S_ISREG(path.stat().st_mode),
            'JSON input must be a regular file')
    require(path.stat().st_size <= 1024 * 1024, 'JSON input exceeds 1 MiB')
    return json.loads(path.read_text())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare = commands.add_parser('plan'); prepare.add_argument('--input', type=Path, required=True)
    check = commands.add_parser('verify')
    check.add_argument('--request', type=Path, required=True)
    check.add_argument('--readback', type=Path, required=True)
    probe = commands.add_parser('inspect'); probe.add_argument('--chat-id', required=True)
    probe.add_argument('--include-catalog', action='store_true')
    probe.add_argument('--timeout', type=float, default=20); probe.add_argument('--codex', default='codex')
    args = parser.parse_args(argv)
    try:
        if args.command == 'plan':
            result = plan(read_json(args.input))
        elif args.command == 'verify':
            result = verify(read_json(args.request), read_json(args.readback))
        else:
            result = inspect_selection(args.chat_id, args.codex, args.timeout, args.include_catalog)
        print(json.dumps(result, indent=2))
        return 0
    except (GuardError, OSError, ValueError, TypeError, KeyError) as error:
        result = {'status': 'blocked', 'reason': str(error)}
        if isinstance(error, SocketPermissionError):
            result.update(code=error.code, requires_host_approval=True, server_start_attempted=False)
        print(json.dumps(result), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
