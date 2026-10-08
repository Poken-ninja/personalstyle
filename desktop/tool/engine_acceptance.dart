import 'dart:convert';
import 'dart:io';

import 'package:personalstyle_desktop/engine.dart';

// Actual Windows transport acceptance. No writing, store mutation or model calls.
Future<void> main(List<String> args) async {
  if (args.length != 2) {
    stderr.writeln(
      'Usage: dart run tool/engine_acceptance.dart <python> <config>',
    );
    exitCode = 2;
    return;
  }
  final session = EngineSession(python: args[0], config: args[1]);
  final timer = Stopwatch()..start();
  Uri? endpoint;
  try {
    await session.start();
    endpoint = session.endpoint!;
    final handshake = await session.call('handshake', {});
    await session.stop();
    var portClosed = false;
    try {
      final socket = await Socket.connect(
        endpoint.host,
        endpoint.port,
        timeout: const Duration(seconds: 2),
      );
      socket.destroy();
    } on SocketException {
      portClosed = true;
    }
    if (!portClosed || session.endpoint != null) {
      throw const EngineException(EngineFailure.operation);
    }
    stdout.writeln(
      jsonEncode({
        'acceptance': 'PASS',
        'client_version': '$clientVersion+1',
        'dart': Platform.version.split(' ').first,
        'os': Platform.operatingSystemVersion,
        'bind_host': endpoint.host,
        'handshake': handshake,
        'shutdown':
            'owned process exited; endpoint closed; session invalidated',
        'seconds': timer.elapsedMilliseconds / 1000,
        'profile_mutations': 0,
        'model_calls': 0,
      }),
    );
  } catch (error) {
    stderr.writeln(
      jsonEncode({
        'acceptance': 'FAIL',
        'code': error is EngineException ? error.failure.name : 'operation',
      }),
    );
    exitCode = 1;
  } finally {
    await session.stop();
  }
}
