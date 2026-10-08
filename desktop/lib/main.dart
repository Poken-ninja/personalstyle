import 'dart:async';
import 'dart:ui' show AppExitResponse;

import 'package:flutter/material.dart';

import 'engine.dart';

void main() => runApp(
  PersonalStyleApp(
    connection: EngineSession(
      python: const String.fromEnvironment(
        'ENGINE_PYTHON',
        defaultValue: '../.venv/Scripts/python.exe',
      ),
      config: const String.fromEnvironment(
        'ENGINE_CONFIG',
        defaultValue: '../personalstyle.toml',
      ),
    ),
  ),
);

enum ViewState {
  starting,
  engineUnavailable,
  protocolIncompatible,
  ready,
  rewriting,
  result,
  operationFailed,
}

String messageFor(EngineFailure failure) => switch (failure) {
  EngineFailure.start =>
    'The local engine could not start. Check the development engine setup.',
  EngineFailure.exited =>
    'The local engine exited. Close and reopen PersonalStyle.',
  EngineFailure.authentication =>
    'The engine rejected this session. Close and reopen PersonalStyle.',
  EngineFailure.incompatible =>
    'This engine protocol is incompatible with PersonalStyle.',
  EngineFailure.capability => 'This engine is missing a required capability.',
  EngineFailure.invalidRequest =>
    'The request is invalid or too large. Check your input.',
  EngineFailure.operation => 'The engine could not complete the operation. Check protected profile and runtime readiness.',
};

class PersonalStyleApp extends StatelessWidget {
  const PersonalStyleApp({super.key, required this.connection});
  final EngineConnection connection;
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'PersonalStyle',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      colorSchemeSeed: const Color(0xff275d72),
      useMaterial3: true,
    ),
    home: WritingScreen(connection: connection),
  );
}

class WritingScreen extends StatefulWidget {
  const WritingScreen({super.key, required this.connection});
  final EngineConnection connection;
  @override
  State<WritingScreen> createState() => _WritingScreenState();
}

class _WritingScreenState extends State<WritingScreen> {
  final original = TextEditingController();
  final intent = TextEditingController();
  final contextInput = TextEditingController();
  final constraints = TextEditingController();
  final edited = TextEditingController();
  final example = TextEditingController();
  late final AppLifecycleListener lifecycle;
  ViewState state = ViewState.starting;
  Map<String, dynamic>? result;
  String mode = 'personalized';
  String? notice;
  bool busy = false;
  bool authorizedExample = false;
  bool exampleLearning = false;
  bool feedbackLearning = false;
  bool feedbackSaved = false;
  // One uncertain mutation can be confirmed manually with the same UUID/payload.
  (String, Map<String, Object?>)? pending;

  @override
  void initState() {
    super.initState();
    lifecycle = AppLifecycleListener(
      onExitRequested: () async {
        await widget.connection.stop();
        return AppExitResponse.exit;
      },
    );
    widget.connection.onExit = () {
      if (!mounted) return;
      setState(() {
        result = null;
        pending = null;
        state = ViewState.engineUnavailable;
        notice = messageFor(EngineFailure.exited);
      });
    };
    unawaited(start());
  }

  Future<void> start() async {
    try {
      await widget.connection.start();
      if (mounted) setState(() => state = ViewState.ready);
    } catch (error) {
      if (!mounted) return;
      final failure = error is EngineException
          ? error.failure
          : EngineFailure.start;
      setState(() {
        state =
            failure == EngineFailure.incompatible ||
                failure == EngineFailure.capability
            ? ViewState.protocolIncompatible
            : ViewState.engineUnavailable;
        notice = messageFor(failure);
      });
    }
  }

  @override
  void dispose() {
    lifecycle.dispose();
    widget.connection.onExit = null;
    unawaited(widget.connection.stop());
    for (final controller in [
      original,
      intent,
      contextInput,
      constraints,
      edited,
      example,
    ]) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> operate(Future<void> Function() action) async {
    if (busy) return;
    setState(() {
      busy = true;
      notice = null;
    });
    try {
      await action();
    } catch (error) {
      if (mounted && state != ViewState.engineUnavailable) {
        setState(() {
          state = ViewState.operationFailed;
          notice = messageFor(
            error is EngineException ? error.failure : EngineFailure.operation,
          );
        });
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> rewrite() => operate(() async {
    setState(() {
      state = ViewState.rewriting;
      result = null;
      pending = null;
      feedbackSaved = false;
      edited.clear();
    });
    final value = await widget.connection.call('rewrite', {
      'original': original.text,
      'intent': intent.text,
      'context': contextInput.text,
      'constraints': constraints.text
          .split('\n')
          .where((c) => c.trim().isNotEmpty)
          .toList(),
    });
    // Receipt validation only: semantic/fact/constraint verification stays in P01.
    if (value is! Map<String, dynamic> ||
        value['state'] != 'SUCCEEDED' ||
        value['verification_status'] != 'verified' ||
        value['run_id'] is! String ||
        value['candidates'] is! Map) {
      throw const EngineException(EngineFailure.operation);
    }
    for (final kind in ['generic', 'personalized']) {
      final candidate = (value['candidates'] as Map)[kind];
      if (candidate is! Map ||
          candidate['verification_status'] != 'verified' ||
          candidate['text'] is! String) {
        throw const EngineException(EngineFailure.operation);
      }
    }
    if (!mounted || state == ViewState.engineUnavailable) return;
    setState(() {
      result = value;
      state = ViewState.result;
      edited.text = candidateText;
    });
  });

  String get candidateText =>
      ((result?['candidates'] as Map?)?[mode] as Map?)?['text'] as String? ??
      '';

  Future<void> mutation(String capability, Map<String, Object?> payload) async {
    pending = (capability, payload);
    await widget.connection.call(capability, payload);
    pending = null;
  }

  Future<void> feedback(String type) => operate(() async {
    await mutation('feedback.write', {
      'run_id': result!['run_id'],
      'event': {
        'id': newMutationId(),
        'event_type': type,
        'candidate_mode': mode,
        'supplier': 'local_user',
        'authorizer': 'local_user',
        'authorized': true,
        'learning_authorized': feedbackLearning,
        'held_out': false,
        'edited_text': type == 'edit' ? edited.text : null,
        'corrected_context': null,
        'classification_hint': null,
      },
    });
    if (mounted) {
      setState(() {
        feedbackSaved = true;
        notice = 'Feedback saved.';
      });
    }
  });

  Future<void> addExample() => operate(() async {
    await mutation('example.write', {
      'id': newMutationId(),
      'text': example.text,
      'context': contextInput.text,
      'supplier': 'local_user',
      'authorizer': 'local_user',
      'source_kind': 'user_owned',
      'authorized': authorizedExample,
      'learning_eligible': exampleLearning,
      'held_out': false,
    });
    if (mounted) {
      setState(() {
        notice = 'Writing example saved.';
        example.clear();
      });
    }
  });

  Future<void> retryMutation() => operate(() async {
    final request = pending!;
    await widget.connection.call(request.$1, request.$2);
    pending = null;
    if (mounted) {
      setState(() {
        if (request.$1 == 'feedback.write') feedbackSaved = true;
        notice = 'Previous submission confirmed.';
      });
    }
  });

  Widget input(
    String label,
    TextEditingController controller, {
    int lines = 1,
  }) => Padding(
    padding: const EdgeInsets.only(bottom: 16),
    child: TextField(
      controller: controller,
      maxLines: lines,
      enabled: !busy,
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
      ),
    ),
  );

  @override
  Widget build(BuildContext context) {
    final connected =
        state != ViewState.starting &&
        state != ViewState.engineUnavailable &&
        state != ViewState.protocolIncompatible;
    final available = connected && !busy && pending == null;
    final status = switch (state) {
      ViewState.starting => 'STARTING',
      ViewState.engineUnavailable => 'ENGINE_UNAVAILABLE',
      ViewState.protocolIncompatible => 'PROTOCOL_INCOMPATIBLE',
      ViewState.ready => 'READY',
      ViewState.rewriting => 'REWRITING',
      ViewState.result => 'RESULT',
      ViewState.operationFailed => 'OPERATION_FAILED',
    };
    return Scaffold(
      appBar: AppBar(title: const Text('PersonalStyle')),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 880),
          child: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              Text(
                status,
                key: const Key('status'),
                style: Theme.of(context).textTheme.labelLarge,
              ),
              if (busy || state == ViewState.starting)
                const LinearProgressIndicator(),
              if (notice != null)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  child: Text(notice!, key: const Key('notice')),
                ),
              const SizedBox(height: 20),
              input('Original text', original, lines: 4),
              input('Intent', intent),
              input('Explicit context', contextInput),
              input('Constraints (one per line)', constraints, lines: 2),
              FilledButton(
                onPressed: available ? rewrite : null,
                child: const Text('Rewrite'),
              ),
              if (pending != null && connected)
                OutlinedButton(
                  onPressed: busy ? null : retryMutation,
                  child: const Text('Confirm previous submission'),
                ),
              if (result != null) ...[
                const Divider(height: 32),
                const Text('Verified by the engine', key: Key('verified')),
                DropdownButton<String>(
                  value: mode,
                  onChanged: available && !feedbackSaved
                      ? (value) {
                          setState(() {
                            mode = value!;
                            edited.text = candidateText;
                          });
                        }
                      : null,
                  items: const [
                    DropdownMenuItem(
                      value: 'personalized',
                      child: Text('Personalized'),
                    ),
                    DropdownMenuItem(value: 'generic', child: Text('Generic')),
                  ],
                ),
                SelectableText(candidateText, key: const Key('result')),
                const SizedBox(height: 16),
                input('Edit result', edited, lines: 4),
                CheckboxListTile(
                  value: feedbackLearning,
                  onChanged: available && !feedbackSaved
                      ? (value) => setState(() => feedbackLearning = value!)
                      : null,
                  title: const Text(
                    'Authorize learning from this feedback in its context',
                  ),
                ),
                Wrap(
                  spacing: 12,
                  children: [
                    FilledButton(
                      onPressed: available && !feedbackSaved
                          ? () => feedback('accept')
                          : null,
                      child: const Text('Accept'),
                    ),
                    OutlinedButton(
                      onPressed: available && !feedbackSaved
                          ? () => feedback('edit')
                          : null,
                      child: const Text('Submit edited feedback'),
                    ),
                  ],
                ),
              ],
              const Divider(height: 40),
              Text(
                'Add your writing example',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const Text(
                'Uses the explicit context above. Learning is optional.',
              ),
              const SizedBox(height: 16),
              input('Writing example', example, lines: 3),
              CheckboxListTile(
                value: authorizedExample,
                onChanged: available
                    ? (value) => setState(() => authorizedExample = value!)
                    : null,
                title: const Text(
                  'I own this writing and authorize storing it',
                ),
              ),
              CheckboxListTile(
                value: exampleLearning,
                onChanged: available
                    ? (value) => setState(() => exampleLearning = value!)
                    : null,
                title: const Text(
                  'Allow this example for personalization learning',
                ),
              ),
              OutlinedButton(
                onPressed: available && authorizedExample ? addExample : null,
                child: const Text('Save authorized example'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
