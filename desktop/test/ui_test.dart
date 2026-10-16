import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personalstyle_desktop/engine.dart';
import 'package:personalstyle_desktop/main.dart'
    show
        PersonalStyleApp,
        WritingContext,
        constraintsForRequirements,
        engineContext,
        intentForRefinement,
        messageFor,
        mutationWasDefinitelyRejected,
        statusForFailure;

class WireFake implements EngineConnection {
  @override
  void Function()? onExit;
  EngineFailure? startFailure;
  Object? operationFailure;
  Completer<Object?>? rewriteResponse;
  final calls = <(String, Map<String, Object?>)>[];
  bool stopped = false;
  Map<String, dynamic> receipt = {
    'state': 'SUCCEEDED',
    'verification_status': 'verified',
    'run_id': '11111111-1111-4111-8111-111111111111',
    'candidates': {
      'generic': {
        'text': 'Generic synthetic result.',
        'verification_status': 'verified',
      },
      'personalized': {
        'text': 'Personalized synthetic result.',
        'verification_status': 'verified',
      },
    },
    'model_identity': {
      'provider': 'ollama',
      'model': 'synthetic',
      'digest': 'test',
    },
  };
  @override
  Future<void> start() async {
    if (startFailure != null) throw EngineException(startFailure!);
  }

  @override
  Future<Object?> call(String capability, Map<String, Object?> payload) async {
    calls.add((capability, payload));
    if (operationFailure != null) throw operationFailure!;
    if (capability == 'rewrite') return rewriteResponse?.future ?? receipt;
    return {'id': 'synthetic-record'};
  }

  @override
  Future<void> stop() async {
    stopped = true;
  }
}

Future<void> boot(WidgetTester tester, WireFake fake) async {
  tester.view.resetPhysicalSize();
  tester.view.physicalSize = const Size(1100, 1800);
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);
  await tester.pumpWidget(PersonalStyleApp(connection: fake));
  await tester.pumpAndSettle();
}

Finder field(String label) => find.widgetWithText(TextField, label);
Future<void> rewrite(WidgetTester tester) async {
  await tester.enterText(
    field('Paste or write your draft'),
    'Synthetic source.',
  );
  await tester.enterText(field('Maximum words (optional)'), '80');
  await tester.enterText(
    field('Exact terms to preserve (one per line)'),
    'Keep names\nKeep dates',
  );
  await tester.tap(find.byKey(const Key('humanize')));
  await tester.pump();
}

void main() {
  test('protected-storage failures explain distinct safe stages', () {
    final directory = messageFor(
      EngineFailure.protectedStorage,
      safeCode: 'PROFILE_DIRECTORY_PROTECTION_FAILED',
    );
    final verifier = messageFor(
      EngineFailure.protectedStorage,
      safeCode: 'PROFILE_ACL_CHECK_UNAVAILABLE',
    );
    final file = messageFor(
      EngineFailure.protectedStorage,
      safeCode: 'PROFILE_FILE_PROTECTION_FAILED',
    );
    expect(directory, contains('profile directory protection check'));
    expect(verifier, contains('permission check'));
    expect(file, contains('database protection check'));
    expect(directory, isNot(verifier));
    expect(verifier, isNot(file));
    expect(directory, isNot(contains('C:\\')));
  });

  test(
    'friendly controls map to stable engine values and bounded constraints',
    () {
      expect(engineContext(WritingContext.academic), 'academic.writing');
      expect(engineContext(WritingContext.professional), 'work.email');
      expect(engineContext(WritingContext.everyday), 'casual.chat');
      expect(
        intentForRefinement('Humanize only'),
        contains('preserving its meaning and facts'),
      );
      expect(constraintsForRequirements('80', 'ModelProvider\n42'), [
        'max_words:80',
        'required_literal:ModelProvider',
        'required_literal:42',
      ]);
      expect(
        () => constraintsForRequirements('0', ''),
        throwsA(isA<EngineException>()),
      );
    },
  );

  test('known failures have distinct stable presentation categories', () {
    expect(statusForFailure(EngineFailure.invalidRequest), 'INVALID_INPUT');
    expect(
      statusForFailure(EngineFailure.protectedStorage),
      'PROTECTED_STORAGE_ERROR',
    );
    expect(
      statusForFailure(EngineFailure.profileDatabase),
      'PROFILE_DATABASE_ERROR',
    );
    expect(
      statusForFailure(EngineFailure.noEligibleExamples),
      'NO_ELIGIBLE_VOICE_EVIDENCE',
    );
    expect(
      statusForFailure(EngineFailure.modelUnavailable),
      'MODEL_UNAVAILABLE',
    );
    expect(
      statusForFailure(EngineFailure.operationTimeout),
      'OPERATION_TIMEOUT',
    );
    expect(statusForFailure(EngineFailure.resourceLimit), 'RESOURCE_LIMIT');
    expect(
      statusForFailure(EngineFailure.verificationRejected),
      'VERIFICATION_REJECTED',
    );
    expect(
      statusForFailure(EngineFailure.capability),
      'CAPABILITY_UNSUPPORTED',
    );
    expect(
      statusForFailure(EngineFailure.incompatible),
      'PROTOCOL_INCOMPATIBLE',
    );
    expect(
      statusForFailure(EngineFailure.operation),
      'ENGINE_OPERATION_FAILED',
    );
    expect(mutationWasDefinitelyRejected(EngineFailure.invalidRequest), isTrue);
    expect(
      mutationWasDefinitelyRejected(EngineFailure.mutationConflict),
      isTrue,
    );
    expect(mutationWasDefinitelyRejected(EngineFailure.operation), isFalse);
    expect(
      messageFor(
        EngineFailure.protectedStorage,
        safeCode: 'STORAGE_BOUNDARY_INVALID',
      ),
      contains('Reference: STORAGE_BOUNDARY_INVALID'),
    );
  });

  testWidgets('friendly workspace maps context, refinement and requirements', (
    tester,
  ) async {
    final fake = WireFake()..rewriteResponse = Completer<Object?>();
    await boot(tester, fake);
    expect(find.text('READY'), findsOneWidget);
    expect(find.text('Make this sound like me.'), findsOneWidget);
    expect(find.text('Explicit context'), findsNothing);
    expect(find.text('casual.chat'), findsNothing);
    expect(find.text('Add your writing example'), findsNothing);

    await tester.tap(find.byKey(const Key('writing-context')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Everyday').last);
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('refinement')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('More concise').last);
    await tester.pumpAndSettle();
    await rewrite(tester);
    expect(find.text('REWRITING'), findsOneWidget);
    expect(fake.calls.single.$1, 'rewrite');
    expect(fake.calls.single.$2, {
      'original': 'Synthetic source.',
      'intent': 'Humanize this draft in my writing voice more concisely while preserving its meaning and facts.',
      'context': 'casual.chat',
      'constraints': [
        'max_words:80',
        'required_literal:Keep names',
        'required_literal:Keep dates',
      ],
    });
    fake.rewriteResponse!.complete(fake.receipt);
    await tester.pumpAndSettle();
    expect(find.text('RESULT'), findsOneWidget);
    expect(find.byKey(const Key('verified')), findsOneWidget);
    expect(find.byKey(const Key('result')), findsOneWidget);
    expect(find.byKey(const Key('original-result')), findsOneWidget);
    expect(find.byKey(const Key('verification-explanation')), findsOneWidget);
    expect(
      tester
          .widget<SelectableText>(
            find.descendant(
              of: find.byKey(const Key('result')),
              matching: find.byType(SelectableText),
            ),
          )
          .data,
      'Personalized synthetic result.',
    );
  });

  for (final failure in [
    EngineFailure.start,
    EngineFailure.incompatible,
    EngineFailure.capability,
  ]) {
    testWidgets('startup ${failure.name} fails visibly', (tester) async {
      await boot(tester, WireFake()..startFailure = failure);
      expect(
        find.text(
          failure == EngineFailure.start
              ? 'ENGINE_UNAVAILABLE'
              : 'PROTOCOL_INCOMPATIBLE',
        ),
        findsOneWidget,
      );
      expect(
        tester
            .widget<FilledButton>(find.byKey(const Key('humanize')))
            .onPressed,
        isNull,
      );
    });
  }

  testWidgets('unverified receipt is never rendered as success', (
    tester,
  ) async {
    final fake = WireFake();
    fake.receipt['verification_status'] = 'not_verified';
    await boot(tester, fake);
    await rewrite(tester);
    await tester.pumpAndSettle();
    expect(find.text('ENGINE_OPERATION_FAILED'), findsOneWidget);
    expect(find.byKey(const Key('verified')), findsNothing);
  });

  for (final event in ['accept', 'edit']) {
    testWidgets(
      '$event feedback uses source run, UUID, explicit authorization, no classification',
      (tester) async {
        final fake = WireFake();
        await boot(tester, fake);
        await rewrite(tester);
        await tester.pumpAndSettle();
        if (event == 'edit') {
          await tester.enterText(
            field('Edit your result'),
            'Synthetic edited result.',
          );
        }
        final button = find.text(
          event == 'accept' ? 'Accept result' : 'Submit my edit',
        );
        await tester.ensureVisible(button);
        await tester.tap(button);
        await tester.pumpAndSettle();
        final request = fake.calls.last;
        expect(request.$1, 'feedback.write');
        expect(request.$2['run_id'], fake.receipt['run_id']);
        final payload = request.$2['event'] as Map;
        expect(payload['event_type'], event);
        expect(payload['candidate_mode'], 'personalized');
        expect(payload['id'], matches(RegExp(r'^[a-f0-9-]{36}$')));
        expect(payload['authorized'], isTrue);
        expect(payload['learning_authorized'], isFalse);
        expect(payload['classification_hint'], isNull);
        expect(
          payload['edited_text'],
          event == 'edit' ? 'Synthetic edited result.' : null,
        );
        expect(fake.calls, hasLength(2));
      },
    );
  }

  testWidgets('engine exit invalidates result and session UI', (tester) async {
    final fake = WireFake();
    await boot(tester, fake);
    await rewrite(tester);
    await tester.pumpAndSettle();
    fake.onExit!();
    await tester.pumpAndSettle();
    expect(find.text('ENGINE_UNAVAILABLE'), findsOneWidget);
    expect(find.byKey(const Key('result')), findsNothing);
    await tester.pumpWidget(const SizedBox());
    expect(fake.stopped, isTrue);
  });

  testWidgets(
    'arbitrary exceptions never leak writing, credentials or internal paths',
    (tester) async {
      final fake = WireFake()
        ..operationFailure = Exception(
          'credential-secret raw-private-writing C:/private.db',
        );
      await boot(tester, fake);
      await rewrite(tester);
      await tester.pumpAndSettle();
      expect(find.textContaining('credential-secret'), findsNothing);
      expect(find.textContaining('raw-private-writing'), findsNothing);
      expect(find.textContaining('private.db'), findsNothing);
      expect(find.text('ENGINE_OPERATION_FAILED'), findsOneWidget);
    },
  );

  testWidgets('protected storage error shows safe category and reference', (
    tester,
  ) async {
    final fake = WireFake()
      ..operationFailure = const EngineException(
        EngineFailure.protectedStorage,
        safeCode: 'STORAGE_BOUNDARY_INVALID',
      );
    await boot(tester, fake);
    await rewrite(tester);
    await tester.pumpAndSettle();
    expect(find.text('PROTECTED_STORAGE_ERROR'), findsOneWidget);
    expect(find.textContaining('Do not reset the profile.'), findsOneWidget);
    expect(
      find.textContaining('Reference: STORAGE_BOUNDARY_INVALID'),
      findsOneWidget,
    );
    expect(find.textContaining('C:/'), findsNothing);
  });

  testWidgets('unknown safeCode is not rendered as a reference', (
    tester,
  ) async {
    expect(
      messageFor(
        EngineFailure.operation,
        safeCode: 'unknown raw-writing C:/private.db',
      ),
      isNot(contains('unknown')),
    );
  });

  testWidgets(
    'uncertain mutation has no automatic retry and manual confirmation reuses payload',
    (tester) async {
      final fake = WireFake();
      await boot(tester, fake);
      await rewrite(tester);
      await tester.pumpAndSettle();
      fake.operationFailure = const EngineException(EngineFailure.operation);
      await tester.ensureVisible(find.text('Accept result'));
      await tester.tap(find.text('Accept result'));
      await tester.pumpAndSettle();
      expect(fake.calls, hasLength(2));
      final originalMutation = fake.calls.last;
      fake.operationFailure = null;
      expect(find.text('Unconfirmed feedback submission'), findsOneWidget);
      expect(
        find.textContaining(
          'The outcome is unknown. PersonalStyle did not retry automatically.',
        ),
        findsOneWidget,
      );
      await tester.ensureVisible(
        find.text('Retry feedback submission with same ID'),
      );
      await tester.tap(find.text('Retry feedback submission with same ID'));
      await tester.pumpAndSettle();
      expect(fake.calls.last, originalMutation);
      expect(fake.calls, hasLength(3));
    },
  );

  testWidgets(
    'pending feedback remains visible after engine exit without retry',
    (tester) async {
      final fake = WireFake();
      await boot(tester, fake);
      await rewrite(tester);
      await tester.pumpAndSettle();
      fake.operationFailure = const EngineException(EngineFailure.operation);
      await tester.ensureVisible(find.text('Accept result'));
      await tester.tap(find.text('Accept result'));
      await tester.pumpAndSettle();
      expect(find.text('Unconfirmed feedback submission'), findsOneWidget);
      expect(fake.calls, hasLength(2));
      fake.onExit!();
      await tester.pumpAndSettle();
      expect(find.text('ENGINE_UNAVAILABLE'), findsOneWidget);
      expect(find.text('Unconfirmed feedback submission'), findsOneWidget);
      expect(find.text('Save authorized example'), findsNothing);
      expect(fake.calls, hasLength(2));
    },
  );

  testWidgets(
    'structured invalid rewrite failure is shown without claiming a save',
    (tester) async {
      final fake = WireFake()
        ..operationFailure = const EngineException(
          EngineFailure.invalidRequest,
        );
      await boot(tester, fake);
      await tester.enterText(
        field('Paste or write your draft'),
        'Synthetic source.',
      );
      await tester.tap(find.byKey(const Key('humanize')));
      await tester.pumpAndSettle();
      expect(find.text('INVALID_INPUT'), findsOneWidget);
      expect(find.textContaining('No change was saved.'), findsNothing);
      expect(fake.calls, hasLength(1));
    },
  );
}
