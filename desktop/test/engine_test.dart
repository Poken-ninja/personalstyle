import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:personalstyle_desktop/engine.dart';

void main() {
  late HttpServer server;
  late ProtocolClient client;
  late List<Map<String, dynamic>> received;
  late Map<String, Object?> response;
  late int status;
  setUp(() async {
    received = [];
    status = 200;
    response = {
      'protocol_version': '1.0',
      'ok': true,
      'result': {
        'protocol_version': '1.4',
        'compatibility': 'compatible',
        'supported_capabilities': requiredCapabilities.toList(),
      },
    };
    server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    server.listen((request) async {
      expect(request.uri.path, '/v1');
      expect(request.uri.query, isEmpty);
      expect(
        request.headers.value('authorization'),
        'Bearer synthetic-test-token',
      );
      expect(request.headers.value('origin'), isNull);
      expect(request.contentLength, greaterThan(0));
      received.add(
        jsonDecode(await utf8.decoder.bind(request).join())
            as Map<String, dynamic>,
      );
      request.response.statusCode = status;
      request.response.headers.contentType = ContentType.json;
      request.response.write(jsonEncode(response));
      await request.response.close();
    });
    client = ProtocolClient(
      Uri.parse('http://127.0.0.1:${server.port}/v1'),
      'synthetic-test-token',
    );
  });
  tearDown(() async {
    client.close();
    await server.close(force: true);
  });

  test(
    'authenticated 1.x handshake sends the existing desktop envelope',
    () async {
      await client.handshake();
      expect(received.single, {
        'protocol_version': '1.0',
        'client_version': '0.1.0',
        'client_kind': 'desktop',
        'requested_capability': 'handshake',
        'payload': <String, Object?>{},
      });
    },
  );
  test('major mismatch fails explicitly', () async {
    response['protocol_version'] = '2.0';
    await expectLater(
      client.handshake(),
      throwsA(
        isA<EngineException>().having(
          (e) => e.failure,
          'failure',
          EngineFailure.incompatible,
        ),
      ),
    );
  });
  test('missing required capability fails', () async {
    (response['result'] as Map)['supported_capabilities'] = ['handshake'];
    await expectLater(
      client.handshake(),
      throwsA(
        isA<EngineException>().having(
          (e) => e.failure,
          'failure',
          EngineFailure.capability,
        ),
      ),
    );
  });
  test('authentication error ignores untrusted diagnostic text', () async {
    status = 401;
    response = {
      'protocol_version': '1.0',
      'ok': false,
      'error': {
        'code': 'AUTHENTICATION_INVALID',
        'detail': 'synthetic-test-token private-writing C:/private.db',
      },
    };
    try {
      await client.handshake();
      fail('Expected an authentication failure');
    } catch (error) {
      expect(error.toString(), 'EngineException(authentication)');
    }
    expect(client.toString(), isNot(contains('synthetic-test-token')));
  });
  test('oversized input is rejected before HTTP execution', () async {
    await expectLater(
      client.call('rewrite', {'original': 'x' * 73729}),
      throwsA(
        isA<EngineException>().having(
          (e) => e.failure,
          'failure',
          EngineFailure.invalidRequest,
        ),
      ),
    );
    expect(received, isEmpty);
  });
  test('non-loopback, URL auth and query endpoints rejected', () {
    for (final uri in [
      'http://localhost:42/v1',
      'http://192.168.1.2:42/v1',
      'http://secret@127.0.0.1:42/v1',
      'http://127.0.0.1:42/v1?token=secret',
    ]) {
      expect(
        () => ProtocolClient(Uri.parse(uri), 'synthetic'),
        throwsA(isA<EngineException>()),
      );
    }
  });
  test('closed session cannot make calls', () async {
    client.close();
    await expectLater(
      client.call('rewrite', {}),
      throwsA(isA<EngineException>()),
    );
    expect(received, isEmpty);
  });
  test(
    'mutation and evaluation delegate one request each without retries',
    () async {
      for (final capability in [
        'example.write',
        'feedback.write',
        'preference.evaluate',
      ]) {
        await client.call(capability, {
          'context': 'work.email',
          'id': 'synthetic-id',
        });
      }
      expect(received.map((e) => e['requested_capability']).toList(), [
        'example.write',
        'feedback.write',
        'preference.evaluate',
      ]);
    },
  );
  test('HTTP redirect is not followed', () async {
    status = 302;
    await expectLater(client.handshake(), throwsA(isA<EngineException>()));
    expect(received, hasLength(1));
  });
  test('mutation identifiers are canonical distinct UUIDv4', () {
    final ids = List.generate(20, (_) => newMutationId());
    expect(ids.toSet(), hasLength(20));
    for (final id in ids) {
      expect(
        RegExp(
          r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$',
        ).hasMatch(id),
        isTrue,
      );
    }
  });

  test('closing during process launch prevents a late ready session', () async {
    final root = Platform.environment['FLUTTER_ROOT']!;
    final dart = '$root/bin/cache/dart-sdk/bin/dart.exe';
    final fixture = File('.dart_tool/wire_engine.exe').absolute.path;
    final compile = await Process.run(dart, [
      'compile',
      'exe',
      'test/fixtures/wire_engine.dart',
      '-o',
      fixture,
    ]).timeout(const Duration(seconds: 60));
    expect(compile.exitCode, 0);
    final session = EngineSession(python: fixture, config: 'unused');
    try {
      final launching = session.start();
      await session.stop();
      await expectLater(launching, throwsA(isA<EngineException>()));
      expect(session.endpoint, isNull);
    } finally {
      await session.stop();
    }
  }, timeout: const Timeout(Duration(seconds: 90)));
}
