import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';

const clientVersion = '0.1.0';
const protocolVersion = '1.0';
const requiredCapabilities = {
  'handshake',
  'rewrite',
  'example.write',
  'feedback.write',
  'preference.evaluate',
};

enum EngineFailure {
  start,
  exited,
  authentication,
  incompatible,
  capability,
  invalidRequest,
  operation,
}

class EngineException implements Exception {
  const EngineException(this.failure);
  final EngineFailure failure;
  @override
  String toString() => 'EngineException(${failure.name})';
}

String newMutationId() {
  final random = Random.secure();
  final bytes = List.generate(16, (_) => random.nextInt(256));
  bytes[6] = (bytes[6] & 15) | 64;
  bytes[8] = (bytes[8] & 63) | 128;
  final hex = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
  return '${hex.substring(0, 8)}-${hex.substring(8, 12)}-'
      '${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20)}';
}

// Presentation tests fake only this wire/lifecycle interface, never engine rules.
abstract interface class EngineConnection {
  set onExit(void Function()? callback);
  Future<void> start();
  Future<Object?> call(String capability, Map<String, Object?> payload);
  Future<void> stop();
}

class ProtocolClient {
  ProtocolClient(this.endpoint, String credential) : _credential = credential {
    if (endpoint.scheme != 'http' ||
        endpoint.host != '127.0.0.1' ||
        endpoint.path != '/v1' ||
        endpoint.hasQuery ||
        endpoint.hasFragment ||
        endpoint.userInfo.isNotEmpty ||
        endpoint.port < 1 ||
        endpoint.port > 65535) {
      throw const EngineException(EngineFailure.start);
    }
    _http.findProxy = (_) => 'DIRECT';
    _http.connectionTimeout = const Duration(seconds: 10);
  }
  final Uri endpoint;
  String? _credential;
  final HttpClient _http = HttpClient();

  Future<Object?> call(String capability, Map<String, Object?> payload) async {
    if (_credential == null) throw const EngineException(EngineFailure.exited);
    try {
      return await _send(
        capability,
        payload,
      ).timeout(const Duration(seconds: 600));
    } on EngineException {
      rethrow;
    } catch (_) {
      throw const EngineException(EngineFailure.operation);
    }
  }

  Future<Object?> _send(String capability, Map<String, Object?> payload) async {
    final body = utf8.encode(
      jsonEncode({
        'protocol_version': protocolVersion,
        'client_version': clientVersion,
        'client_kind': 'desktop',
        'requested_capability': capability,
        'payload': payload,
      }),
    );
    if (body.length > 73728) {
      throw const EngineException(EngineFailure.invalidRequest);
    }
    final request = await _http.postUrl(endpoint);
    request.followRedirects = false;
    request.headers.set(HttpHeaders.authorizationHeader, 'Bearer $_credential');
    request.headers.contentType = ContentType.json;
    request.contentLength = body.length; // P01 rejects chunked request bodies.
    request.add(body);
    final response = await request.close();
    final bytes = <int>[];
    await for (final chunk in response) {
      if (bytes.length + chunk.length > 1024 * 1024) {
        throw const EngineException(EngineFailure.operation);
      }
      bytes.addAll(chunk);
    }
    final decoded = jsonDecode(utf8.decode(bytes));
    if (decoded is! Map<String, dynamic>) {
      throw const EngineException(EngineFailure.operation);
    }
    if (!_compatible(decoded['protocol_version'])) {
      throw const EngineException(EngineFailure.incompatible);
    }
    if (response.statusCode != 200 || decoded['ok'] != true) {
      final error = decoded['error'];
      final code = error is Map ? error['code'] : null;
      throw EngineException(switch (code) {
        'AUTHENTICATION_REQUIRED' ||
        'AUTHENTICATION_INVALID' => EngineFailure.authentication,
        'PROTOCOL_MAJOR_INCOMPATIBLE' => EngineFailure.incompatible,
        'CAPABILITY_UNSUPPORTED' => EngineFailure.capability,
        'REQUEST_MALFORMED' ||
        'REQUEST_RESOURCE_LIMIT' => EngineFailure.invalidRequest,
        _ => EngineFailure.operation,
      });
    }
    return decoded['result'];
  }

  Future<void> handshake() async {
    final result = await call('handshake', {});
    if (result is! Map ||
        !_compatible(result['protocol_version']) ||
        result['compatibility'] != 'compatible') {
      throw const EngineException(EngineFailure.incompatible);
    }
    final capabilities = result['supported_capabilities'];
    if (capabilities is! List ||
        !requiredCapabilities.every(capabilities.contains)) {
      throw const EngineException(EngineFailure.capability);
    }
  }

  static bool _compatible(Object? version) =>
      version is String && RegExp(r'^1\.[0-9]+$').hasMatch(version);
  void close() {
    _credential = null;
    _http.close(force: true);
  }
}

class EngineSession implements EngineConnection {
  EngineSession({required this.python, required this.config});
  final String python;
  final String config;
  Process? _process;
  ProtocolClient? _client;
  bool _exited = true;
  bool _stopping = false;
  bool _starting = false;
  Future<void>? _termination;
  @override
  void Function()? onExit;
  Uri? get endpoint => _client?.endpoint;

  @override
  Future<void> start() async {
    if (_process != null || _stopping || _starting) {
      throw const EngineException(EngineFailure.start);
    }
    _starting = true;
    try {
      final random = Random.secure();
      final credential = base64Url
          .encode(List.generate(32, (_) => random.nextInt(256)))
          .replaceAll('=', '');
      final process = await Process.start(python, [
        '-m',
        'personalstyle.protocol',
        '--config',
        config,
        '--port',
        '0',
      ], runInShell: false);
      _process = process;
      _exited = false;
      process.stderr
          .drain<void>(); // Never forward arbitrary child diagnostics.
      if (_stopping) {
        process.stdout.drain<void>();
        await stop();
        throw const EngineException(EngineFailure.exited);
      }
      final ready = Completer<Map<String, dynamic>>();
      final line = <int>[];
      process.stdout.listen(
        (chunk) {
          if (ready.isCompleted) return;
          for (final byte in chunk) {
            if (byte == 10) {
              try {
                final value = jsonDecode(utf8.decode(line));
                if (value is! Map<String, dynamic>) {
                  throw const FormatException();
                }
                ready.complete(value);
              } catch (_) {
                ready.completeError(const EngineException(EngineFailure.start));
              }
              return;
            }
            if (line.length >= 1024) {
              ready.completeError(const EngineException(EngineFailure.start));
              return;
            }
            line.add(byte);
          }
        },
        onError: (Object _) {
          if (!ready.isCompleted) {
            ready.completeError(const EngineException(EngineFailure.start));
          }
        },
      );
      unawaited(
        process.exitCode.then((_) {
          _exited = true;
          _client?.close();
          _client = null;
          if (!ready.isCompleted) {
            ready.completeError(const EngineException(EngineFailure.start));
          }
          if (!_stopping) onExit?.call();
        }),
      );
      final readiness = ready.future.timeout(const Duration(seconds: 60));
      process.stdin.writeln(jsonEncode({'credential': credential}));
      await process.stdin.close();
      final value = await readiness;
      if (value['state'] != 'READY' ||
          value['host'] != '127.0.0.1' ||
          value['port'] is! int ||
          _exited ||
          _stopping) {
        throw const EngineException(EngineFailure.start);
      }
      if (!ProtocolClient._compatible(value['protocol_version'])) {
        throw const EngineException(EngineFailure.incompatible);
      }
      _client = ProtocolClient(
        Uri(
          scheme: 'http',
          host: '127.0.0.1',
          port: value['port'] as int,
          path: '/v1',
        ),
        credential,
      );
      await _client!.handshake();
      if (_exited || _stopping) {
        throw const EngineException(EngineFailure.exited);
      }
    } catch (error) {
      await stop();
      if (error is EngineException) rethrow;
      throw const EngineException(EngineFailure.start);
    } finally {
      _starting = false;
    }
  }

  @override
  Future<Object?> call(String capability, Map<String, Object?> payload) async {
    final client = _client;
    if (client == null || _exited) {
      throw const EngineException(EngineFailure.exited);
    }
    return client.call(capability, payload);
  }

  @override
  Future<void> stop() {
    _stopping = true;
    _client?.close();
    _client = null;
    final process = _process;
    if (process == null) return Future<void>.value();
    return _termination ??= _terminate(process);
  }

  Future<void> _terminate(Process process) async {
    if (!_exited) {
      // A Windows venv may have a launcher child; stop only our owned process tree.
      if (Platform.isWindows) {
        final termination = await Process.start('taskkill', [
          '/PID',
          '${process.pid}',
          '/T',
          '/F',
        ]);
        termination.stdout.drain<void>();
        termination.stderr.drain<void>();
        await termination.exitCode.timeout(const Duration(seconds: 10));
      } else {
        process.kill();
      }
      await process.exitCode.timeout(const Duration(seconds: 10));
    }
    _exited = true;
    _process = null;
  }
}
