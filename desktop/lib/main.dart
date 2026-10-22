import 'dart:async';
import 'dart:ui' show AppExitResponse;

import 'package:flutter/material.dart';

import 'document_picker.dart';
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
    picker: const NativeDocumentFilePicker(),
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

String statusForFailure(EngineFailure failure) => switch (failure) {
  EngineFailure.start => 'ENGINE_START_FAILED',
  EngineFailure.exited => 'ENGINE_UNAVAILABLE',
  EngineFailure.authentication => 'AUTHENTICATION_FAILED',
  EngineFailure.incompatible => 'PROTOCOL_INCOMPATIBLE',
  EngineFailure.capability => 'CAPABILITY_UNSUPPORTED',
  EngineFailure.invalidRequest => 'INVALID_INPUT',
  EngineFailure.mutationConflict => 'MUTATION_CONFLICT',
  EngineFailure.sourceUnavailable => 'SOURCE_UNAVAILABLE',
  EngineFailure.protectedStorage => 'PROTECTED_STORAGE_ERROR',
  EngineFailure.profileDatabase => 'PROFILE_DATABASE_ERROR',
  EngineFailure.noEligibleExamples => 'NO_ELIGIBLE_VOICE_EVIDENCE',
  EngineFailure.profileInvalid => 'PROFILE_INVALID',
  EngineFailure.modelUnavailable => 'MODEL_UNAVAILABLE',
  EngineFailure.operationTimeout => 'OPERATION_TIMEOUT',
  EngineFailure.resourceLimit => 'RESOURCE_LIMIT',
  EngineFailure.verificationRejected => 'VERIFICATION_REJECTED',
  _ => 'ENGINE_OPERATION_FAILED',
};

String messageFor(EngineFailure failure, {String? safeCode}) {
  final explanation = switch (failure) {
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
    EngineFailure.mutationConflict => 'This request ID was already used with different content. No new change was accepted.',
    EngineFailure.sourceUnavailable => 'The source result for this operation is no longer available in the current engine session.',
    EngineFailure.protectedStorage => 'PersonalStyle could not verify protected profile storage. The engine did not report a more specific storage step. Do not reset the profile.',
    EngineFailure.profileDatabase => 'PersonalStyle could not read or update the protected profile database. Do not reset the profile.',
    EngineFailure.noEligibleExamples => 'There are no eligible writing examples for this context. Add an authorized example for this context to personalize the result.',
    EngineFailure.profileInvalid => 'The profile data is invalid or uses an unsupported version. Do not reset the profile.',
    EngineFailure.modelUnavailable => 'The selected local model is unavailable or incompatible. Check that the configured Ollama model is ready.',
    EngineFailure.operationTimeout =>
      'The operation exceeded its time limit. No automatic retry was made.',
    EngineFailure.resourceLimit => 'The operation reached a configured resource limit. Shorten the input or reduce its requirements.',
    EngineFailure.verificationRejected => 'The engine could not verify that the result preserves the required meaning and information. Review the input and requirements.',
    EngineFailure.operation => 'The engine could not complete the operation. Its exact cause is not available.',
  };
  final reference = safeCode != null && engineFailureCodes.containsKey(safeCode)
      ? safeCode
      : null;
  return reference == null
      ? explanation
      : '$explanation\nReference: $reference';
}

String pendingOperationName(String capability) => switch (capability) {
  'example.write' => 'writing example save',
  'feedback.write' => 'feedback submission',
  _ => 'profile update',
};

bool mutationWasDefinitelyRejected(EngineFailure failure) =>
    failure == EngineFailure.invalidRequest ||
    failure == EngineFailure.mutationConflict ||
    failure == EngineFailure.sourceUnavailable;

class PersonalStyleApp extends StatelessWidget {
  const PersonalStyleApp({
    super.key,
    required this.connection,
    this.picker = const NativeDocumentFilePicker(),
  });
  final EngineConnection connection;
  final DocumentFilePicker picker;
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'PersonalStyle',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      colorSchemeSeed: const Color(0xff275d72),
      useMaterial3: true,
    ),
    home: WritingScreen(connection: connection, picker: picker),
  );
}

class WritingScreen extends StatefulWidget {
  const WritingScreen({
    super.key,
    required this.connection,
    this.picker = const NativeDocumentFilePicker(),
  });
  final EngineConnection connection;
  final DocumentFilePicker picker;
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
  EngineException? lastFailure;
  String? documentId;
  bool documentResult = false;
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
        documentId = null;
        documentResult = false;
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
      lastFailure = null;
    });
    try {
      await action();
    } catch (error) {
      if (mounted && state != ViewState.engineUnavailable) {
        setState(() {
          state = ViewState.operationFailed;
          lastFailure = error is EngineException ? error : null;
          final failure = lastFailure?.failure ?? EngineFailure.operation;
          final rejected =
              pending != null && mutationWasDefinitelyRejected(failure);
          if (rejected) pending = null;
          notice = messageFor(failure, safeCode: lastFailure?.safeCode);
          if (rejected) notice = '$notice\nNo change was saved.';
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
    final payload = <String, Object?>{
      'original': original.text,
      'intent': intent.text,
      'context': contextInput.text,
      'constraints': constraints.text
          .split('\n')
          .where((c) => c.trim().isNotEmpty)
          .toList(),
    };
    final isDocument = documentId != null;
    if (isDocument) payload['document_id'] = documentId;
    final value = await widget.connection.call(
      isDocument ? 'document.rewrite' : 'rewrite',
      payload,
    );
    if (value is! Map<String, dynamic>) {
      throw const EngineException(EngineFailure.operation);
    }
    if (isDocument) {
      if (value['state'] != 'VERIFIED' ||
          value['whole_document_verification'] != 'verified' ||
          value['output'] is! String) {
        throw const EngineException(EngineFailure.operation);
      }
    } else {
      // Receipt validation only: semantic/fact/constraint verification stays in P01.
      if (value['state'] != 'SUCCEEDED' ||
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
    }
    if (!mounted || state == ViewState.engineUnavailable) return;
    setState(() {
      result = value;
      documentResult = isDocument;
      state = ViewState.result;
      edited.text = candidateText;
    });
  });

  String get candidateText {
    final value = result;
    if (documentResult) return value?['output'] as String? ?? '';
    final candidates = value?['candidates'] as Map?;
    return (candidates?[mode] as Map?)?['text'] as String? ?? '';
  }

  String formatForPath(String path) {
    final filename = path.replaceAll('\\', '/').split('/').last;
    final dot = filename.lastIndexOf('.');
    return dot < 0 ? '' : filename.substring(dot + 1).toLowerCase();
  }

  Future<void> importDocument() => operate(() async {
    final path = await widget.picker.openDocument();
    if (path == null) return;
    final format = formatForPath(path);
    final value = await widget.connection.call('document.import', {
      'path': path,
      'format': format,
    });
    if (value is! Map ||
        value['document_id'] is! String ||
        value['text'] is! String) {
      throw const EngineException(EngineFailure.operation);
    }
    if (!mounted) return;
    setState(() {
      original.text = value['text'] as String;
      documentId = value['document_id'] as String;
      result = null;
      documentResult = false;
      pending = null;
      feedbackSaved = false;
      state = ViewState.ready;
      notice = 'Document imported.';
    });
  });

  Future<void> exportDocument() => operate(() async {
    final path = await widget.picker.saveDocument('PersonalStyle-result.txt');
    if (path == null) return;
    final format = formatForPath(path);
    await widget.connection.call('document.export', {
      'path': path,
      'format': format,
      'text': candidateText,
    });
    if (mounted) setState(() => notice = 'Verified document exported.');
  });

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
    lastFailure = null;
    if (mounted) {
      setState(() {
        if (request.$1 == 'feedback.write') feedbackSaved = true;
        notice =
            'The same request was accepted or an earlier save was confirmed.';
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
      ViewState.operationFailed => statusForFailure(
        lastFailure?.failure ?? EngineFailure.operation,
      ),
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
              OutlinedButton(
                onPressed: available ? importDocument : null,
                child: const Text('Open .txt or .md document'),
              ),
              input('Intent', intent),
              input('Explicit context', contextInput),
              input('Constraints (one per line)', constraints, lines: 2),
              FilledButton(
                onPressed: available ? rewrite : null,
                child: const Text('Rewrite'),
              ),
              if (pending != null) ...[
                Card(
                  key: const Key('pending-mutation'),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Unconfirmed ${pendingOperationName(pending!.$1)}',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'The outcome is unknown. PersonalStyle did not retry automatically. Retrying sends the same request ID: an already-saved matching request is deduplicated; different content is rejected.',
                        ),
                        if (connected)
                          Padding(
                            padding: const EdgeInsets.only(top: 12),
                            child: OutlinedButton(
                              onPressed: busy ? null : retryMutation,
                              child: Text(
                                'Retry ${pendingOperationName(pending!.$1)} with same ID',
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ],
              if (result != null) ...[
                const Divider(height: 32),
                Text(
                  documentResult
                      ? 'Whole document verified by the engine'
                      : 'Verified by the engine',
                  key: const Key('verified'),
                ),
                if (documentResult &&
                    result?['verified_segments'] is int &&
                    result?['total_segments'] is int)
                  Text(
                    'Verified segments: ${result!['verified_segments']} / ${result!['total_segments']}',
                    key: const Key('document-progress'),
                  ),
                SelectableText(candidateText, key: const Key('result')),
                if (documentResult)
                  OutlinedButton(
                    onPressed: available ? exportDocument : null,
                    child: const Text('Export verified document'),
                  )
                else ...[
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
                      DropdownMenuItem(
                        value: 'generic',
                        child: Text('Generic'),
                      ),
                    ],
                  ),
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
