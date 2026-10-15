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

enum WritingContext { academic, professional, everyday }

String contextLabel(WritingContext context) => switch (context) {
  WritingContext.academic => 'Academic',
  WritingContext.professional => 'Professional',
  WritingContext.everyday => 'Everyday',
};

String engineContext(WritingContext context) => switch (context) {
  WritingContext.academic => 'academic.writing',
  WritingContext.professional => 'work.email',
  WritingContext.everyday => 'casual.chat',
};

String intentForRefinement(String refinement) => switch (refinement) {
  'Humanize only' => 'Humanize this draft in my writing voice while preserving its meaning and facts.',
  'Simpler wording' => 'Humanize this draft in my writing voice using simpler wording while preserving its meaning and facts.',
  'More concise' => 'Humanize this draft in my writing voice more concisely while preserving its meaning and facts.',
  'More conversational' => 'Humanize this draft in my writing voice with a more conversational tone while preserving its meaning and facts.',
  _ => throw const EngineException(EngineFailure.invalidRequest),
};

List<String> constraintsForRequirements(
  String wordLimit,
  String protectedTerms,
) {
  final constraints = <String>[];
  final words = wordLimit.trim();
  if (words.isNotEmpty) {
    final parsed = int.tryParse(words);
    if (parsed == null || parsed < 1 || parsed > 9999999) {
      throw const EngineException(EngineFailure.invalidRequest);
    }
    constraints.add('max_words:$parsed');
  }
  for (final term in protectedTerms.split('\n').map((value) => value.trim())) {
    if (term.isNotEmpty) constraints.add('required_literal:$term');
  }
  if (constraints.length > 16 ||
      constraints.any((value) => value.length > 1024)) {
    throw const EngineException(EngineFailure.invalidRequest);
  }
  return constraints;
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
    EngineFailure.noEligibleExamples => 'No eligible writing samples are available for this context. Your draft is still here; personalization requires genuine examples from the same context.',
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
  final wordLimit = TextEditingController();
  final protectedTerms = TextEditingController();
  final edited = TextEditingController();
  late final AppLifecycleListener lifecycle;
  ViewState state = ViewState.starting;
  Map<String, dynamic>? result;
  String mode = 'personalized';
  WritingContext selectedContext = WritingContext.academic;
  String refinement = 'Humanize only';
  String? notice;
  bool busy = false;
  bool feedbackLearning = false;
  bool feedbackSaved = false;
  EngineException? lastFailure;
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
    for (final controller in [original, wordLimit, protectedTerms, edited]) {
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
    final value = await widget.connection.call('rewrite', {
      'original': original.text,
      'intent': intentForRefinement(refinement),
      'context': engineContext(selectedContext),
      'constraints': constraintsForRequirements(
        wordLimit.text,
        protectedTerms.text,
      ),
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
    String? hint,
  }) => Padding(
    padding: const EdgeInsets.only(top: 12),
    child: TextField(
      controller: controller,
      maxLines: lines,
      enabled: !busy,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
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
    final connectionLabel = switch (state) {
      ViewState.starting => 'Starting engine',
      ViewState.engineUnavailable => 'Engine unavailable',
      ViewState.protocolIncompatible => 'Protocol incompatible',
      ViewState.ready => 'READY',
      ViewState.rewriting => 'REWRITING',
      ViewState.result => 'RESULT',
      ViewState.operationFailed => 'Local engine ready',
    };
    final wide = MediaQuery.sizeOf(context).width >= 900;
    final resultCard = result == null
        ? const SizedBox.shrink()
        : Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      'Your result',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                  ),
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
                        child: Text('My context voice'),
                      ),
                      DropdownMenuItem(
                        value: 'generic',
                        child: Text('Generic candidate'),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const Text(
                'The engine verified meaning, required information and constraints. This does not certify voice resemblance. Both candidates were generated in this run; switching the view does not opt out of using context voice evidence.',
                key: Key('verification-explanation'),
              ),
              const SizedBox(height: 16),
              Flex(
                direction: wide ? Axis.horizontal : Axis.vertical,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: _comparisonCard(
                      context,
                      title: 'Original draft',
                      text: original.text,
                      key: const Key('original-result'),
                    ),
                  ),
                  SizedBox(width: wide ? 16 : 0, height: wide ? 0 : 16),
                  Expanded(
                    child: _comparisonCard(
                      context,
                      title: 'Humanized draft',
                      text: candidateText,
                      key: const Key('result'),
                    ),
                  ),
                ],
              ),
              input('Edit your result', edited, lines: 5),
              CheckboxListTile(
                value: feedbackLearning,
                onChanged: available && !feedbackSaved
                    ? (value) => setState(() => feedbackLearning = value!)
                    : null,
                title: const Text('Allow this feedback to inform my voice'),
                subtitle: const Text(
                  'Optional. Accepting a result does not authorize learning.',
                ),
                controlAffinity: ListTileControlAffinity.leading,
                contentPadding: EdgeInsets.zero,
              ),
              Wrap(
                spacing: 12,
                children: [
                  FilledButton.tonal(
                    onPressed: available && !feedbackSaved
                        ? () => feedback('accept')
                        : null,
                    child: const Text('Accept result'),
                  ),
                  OutlinedButton(
                    onPressed: available && !feedbackSaved
                        ? () => feedback('edit')
                        : null,
                    child: const Text('Submit my edit'),
                  ),
                ],
              ),
            ],
          );
    return Scaffold(
      backgroundColor: const Color(0xfff4f5f3),
      appBar: AppBar(
        backgroundColor: const Color(0xfff4f5f3),
        title: const Text('PersonalStyle'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 20),
            child: Chip(
              avatar: Icon(
                connected ? Icons.circle : Icons.circle_outlined,
                size: 12,
                color: connected ? const Color(0xff347668) : Colors.grey,
              ),
              label: Text(connectionLabel, key: const Key('connection-status')),
            ),
          ),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1240),
          child: ListView(
            padding: const EdgeInsets.fromLTRB(32, 28, 32, 40),
            children: [
              Text(
                'Make this sound like me.',
                style: Theme.of(context).textTheme.headlineMedium
                    ?.copyWith(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              Text(
                'Humanize your draft while keeping its meaning and important requirements.',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              const SizedBox(height: 22),
              if (busy || state == ViewState.starting)
                const LinearProgressIndicator(),
              if (notice != null)
                Card(
                  key: const Key('notice-card'),
                  color: const Color(0xfffff3df),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(status, key: const Key('failure-status')),
                        const SizedBox(height: 6),
                        Text(notice!, key: const Key('notice')),
                      ],
                    ),
                  ),
                ),
              Card(
                elevation: 0,
                color: Colors.white,
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Wrap(
                    spacing: 24,
                    runSpacing: 12,
                    children: [
                      SizedBox(
                        width: 260,
                        child: DropdownButtonFormField<WritingContext>(
                          key: const Key('writing-context'),
                          initialValue: selectedContext,
                          isExpanded: true,
                          decoration: const InputDecoration(
                            labelText: 'Writing context',
                            border: OutlineInputBorder(),
                          ),
                          items: WritingContext.values
                              .map(
                                (item) => DropdownMenuItem(
                                  value: item,
                                  child: Text(contextLabel(item)),
                                ),
                              )
                              .toList(),
                          onChanged: available
                              ? (value) => setState(() {
                                  selectedContext = value!;
                                  mode = 'personalized';
                                })
                              : null,
                        ),
                      ),
                      SizedBox(
                        width: 260,
                        child: DropdownButtonFormField<String>(
                          key: const Key('refinement'),
                          initialValue: refinement,
                          isExpanded: true,
                          decoration: const InputDecoration(
                            labelText: 'Optional refinement',
                            border: OutlineInputBorder(),
                          ),
                          items: const [
                            DropdownMenuItem(
                              value: 'Humanize only',
                              child: Text('Humanize only'),
                            ),
                            DropdownMenuItem(
                              value: 'Simpler wording',
                              child: Text('Simpler wording'),
                            ),
                            DropdownMenuItem(
                              value: 'More concise',
                              child: Text('More concise'),
                            ),
                            DropdownMenuItem(
                              value: 'More conversational',
                              child: Text('More conversational'),
                            ),
                          ],
                          onChanged: available
                              ? (value) => setState(() => refinement = value!)
                              : null,
                        ),
                      ),
                      SizedBox(
                        width: 280,
                        child: Padding(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Writing voice',
                                style: Theme.of(context).textTheme.labelLarge,
                              ),
                              const SizedBox(height: 5),
                              Text(
                                'Uses eligible writing from this context only: ${contextLabel(selectedContext)}.',
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              LayoutBuilder(
                builder: (context, constraintsBox) {
                  final editor = _workspaceCard(
                    context,
                    title: 'Your draft',
                    child: input(
                      'Paste or write your draft',
                      original,
                      lines: 14,
                      hint: 'Your writing stays on this device.',
                    ),
                  );
                  final requirements = _workspaceCard(
                    context,
                    title: selectedContext == WritingContext.academic
                        ? 'Requirements'
                        : 'Keep these details',
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Set only the requirements you want checked.',
                        ),
                        input('Maximum words (optional)', wordLimit),
                        input(
                          'Exact terms to preserve (one per line)',
                          protectedTerms,
                          lines: 4,
                          hint: 'Names, technical terms or phrases',
                        ),
                        const Text(
                          'These exact requirements are checked by the engine. Other assignment or rubric criteria need your review.',
                        ),
                      ],
                    ),
                  );
                  if (constraintsBox.maxWidth < 820) {
                    return Column(
                      children: [
                        editor,
                        const SizedBox(height: 16),
                        requirements,
                      ],
                    );
                  }
                  return Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(flex: 3, child: editor),
                      const SizedBox(width: 16),
                      Expanded(flex: 2, child: requirements),
                    ],
                  );
                },
              ),
              const SizedBox(height: 16),
              Align(
                alignment: Alignment.centerLeft,
                child: FilledButton.icon(
                  key: const Key('humanize'),
                  onPressed: available ? rewrite : null,
                  icon: const Icon(Icons.auto_awesome),
                  label: const Text('Humanize in My Voice'),
                ),
              ),
              if (state == ViewState.rewriting)
                const Padding(
                  padding: EdgeInsets.only(top: 12),
                  child: Text('Humanizing and verifying your draft…'),
                ),
              if (pending != null) ...[
                const SizedBox(height: 16),
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
                const SizedBox(height: 28),
                const Text('Verified result', key: Key('verified')),
                const SizedBox(height: 10),
                resultCard,
              ],
              const SizedBox(height: 20),
              const Text(
                'PersonalStyle sends your request to its local engine. Your context voice is kept separate from other contexts.',
                key: Key('privacy-note'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _workspaceCard(
    BuildContext context, {
    required String title,
    required Widget child,
  }) => Card(
    elevation: 0,
    color: Colors.white,
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 4),
          child,
        ],
      ),
    ),
  );

  Widget _comparisonCard(
    BuildContext context, {
    required String title,
    required String text,
    required Key key,
  }) => Card(
    key: key,
    elevation: 0,
    color: const Color(0xfff7f8f6),
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 12),
          SelectableText(text),
        ],
      ),
    ),
  );
}
