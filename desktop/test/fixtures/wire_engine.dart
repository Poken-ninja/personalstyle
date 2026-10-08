import 'dart:convert';
import 'dart:io';

// Child-process wire fixture only; no engine behavior, storage or model logic.
Future<void> main() async {
  await stdin.transform(utf8.decoder).transform(const LineSplitter()).first;
  final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
  stdout.writeln(
    jsonEncode({
      'state': 'READY',
      'host': '127.0.0.1',
      'port': server.port,
      'protocol_version': '1.0',
    }),
  );
  await for (final request in server) {
    await request.drain<void>();
    request.response.write(
      jsonEncode({
        'protocol_version': '1.0',
        'ok': true,
        'result': {
          'protocol_version': '1.0',
          'compatibility': 'compatible',
          'supported_capabilities': [
            'handshake',
            'rewrite',
            'example.write',
            'feedback.write',
            'preference.evaluate',
          ],
        },
      }),
    );
    await request.response.close();
  }
}
