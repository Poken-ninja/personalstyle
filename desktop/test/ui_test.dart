import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personalstyle_desktop/engine.dart';
import 'package:personalstyle_desktop/main.dart';
import 'package:personalstyle_desktop/document_picker.dart';

class WireFake implements EngineConnection {
  @override
  void Function()? onExit;
  EngineFailure? startFailure;
  Object? operationFailure;
  Completer<Object?>? rewriteResponse;
  final calls = <(String, Map<String, Object?>)>[];
  bool stopped = false;
  Object? importResult = {
    'document_id': '22222222-2222-4222-8222-222222222222',
    'format': 'md',
    'text': '# Synthetic imported document\n\nOriginal paragraph.',
  };
  Object? documentResult = {
    'state': 'VERIFIED',
    'whole_document_verification': 'verified',
    'output': '# Synthetic imported document\n\nVerified paragraph.',
  };
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
    if (capability == 'document.import') return importResult;
    if (capability == 'document.rewrite') return documentResult;
    return {'id': 'synthetic-record'};
  }

  @override
  Future<void> stop() async {
    stopped = true;
  }
}

class PickerFake implements DocumentFilePicker {
  String? openPath = r'C:\synthetic\input.md';
  String? savePath = r'C:\synthetic\output.md';
  String? suggestedName;
  int openCalls = 0;
  int saveCalls = 0;

  @override
  Future<String?> openDocument() async {
    openCalls++;
    return openPath;
  }

  @override
  Future<String?> saveDocument(String suggestedName) async {
    saveCalls++;
    this.suggestedName = suggestedName;
    return savePath;
  }
}

Future<void> boot(
  WidgetTester tester,
  WireFake fake, {
  DocumentFilePicker picker = const NativeDocumentFilePicker(),
}) async {
  tester.view.resetPhysicalSize();
  tester.view.physicalSize = const Size(1100, 1800);
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);
  await tester.pumpWidget(PersonalStyleApp(connection: fake, picker: picker));
  await tester.pumpAndSettle();
}

Finder field(String label) => find.widgetWithText(TextField, label);
Future<void> rewrite(WidgetTester tester) async {
  await tester.enterText(field('Original text'), 'Synthetic source.');
  await tester.enterText(field('Intent'), 'Be concise');
  await tester.enterText(field('Explicit context'), 'work.email');
  await tester.enterText(
    field('Constraints (one per line)'),
    'Keep names\nKeep dates',
  );
  await tester.tap(find.text('Rewrite'));
  await tester.pump();
}

void main() {
  test('operation failure status preserves the safe error category', () {
    expect(
      statusForFailure(EngineFailure.protectedStorage),
      'PROTECTED_STORAGE_ERROR',
    );
    expect(
      statusForFailure(EngineFailure.modelUnavailable),
      'MODEL_UNAVAILABLE',
    );
    expect(
      statusForFailure(EngineFailure.verificationRejected),
      'VERIFICATION_REJECTED',
    );
    expect(
      statusForFailure(EngineFailure.operation),
      'ENGINE_OPERATION_FAILED',
    );
    expect(statusForFailure(EngineFailure.invalidRequest), 'INVALID_INPUT');
    expect(
      statusForFailure(EngineFailure.noEligibleExamples),
      'NO_ELIGIBLE_VOICE_EVIDENCE',
    );
    expect(
      statusForFailure(EngineFailure.documentOperation),
      'DOCUMENT_OPERATION_FAILED',
    );
  });

  testWidgets('document picker cancellation makes no engine request', (
    tester,
  ) async {
    final fake = WireFake();
    final picker = PickerFake()..openPath = null;
    await boot(tester, fake, picker: picker);
    await tester.tap(find.text('Open .txt or .md document'));
    await tester.pumpAndSettle();
    expect(picker.openCalls, 1);
    expect(fake.calls, isEmpty);
  });

  testWidgets('import, long rewrite, and verified export delegate to engine', (
    tester,
  ) async {
    final fake = WireFake();
    final picker = PickerFake();
    await boot(tester, fake, picker: picker);
    await tester.tap(find.text('Open .txt or .md document'));
    await tester.pumpAndSettle();
    expect(fake.calls.single.$1, 'document.import');
    expect(fake.calls.single.$2, {'path': picker.openPath, 'format': 'md'});
    expect(
      tester.widget<TextField>(field('Original text')).controller!.text,
      '# Synthetic imported document\n\nOriginal paragraph.',
    );
    await tester.enterText(field('Intent'), 'Clarify without changing facts');
    await tester.enterText(field('Explicit context'), 'work.email');
    await tester.tap(find.text('Rewrite'));
    await tester.pumpAndSettle();
    expect(fake.calls[1].$1, 'document.rewrite');
    expect(
      fake.calls[1].$2['document_id'],
      '22222222-2222-4222-8222-222222222222',
    );
    expect(fake.calls[1].$2['original'], contains('Original paragraph.'));
    expect(find.text('Whole document verified by the engine'), findsOneWidget);
    expect(find.text('Accept'), findsNothing);
    expect(find.text('Submit edited feedback'), findsNothing);
    await tester.tap(find.text('Export verified document'));
    await tester.pumpAndSettle();
    expect(picker.saveCalls, 1);
    expect(picker.suggestedName, 'PersonalStyle-result.txt');
    expect(fake.calls.last.$1, 'document.export');
    expect(fake.calls.last.$2, {
      'path': picker.savePath,
      'format': 'md',
      'text': '# Synthetic imported document\n\nVerified paragraph.',
    });
  });

  testWidgets('export dialog cancellation creates no export request', (
    tester,
  ) async {
    final fake = WireFake();
    final picker = PickerFake()..savePath = null;
    await boot(tester, fake, picker: picker);
    await tester.tap(find.text('Open .txt or .md document'));
    await tester.pumpAndSettle();
    await tester.enterText(field('Intent'), 'Clarify');
    await tester.enterText(field('Explicit context'), 'work.email');
    await tester.tap(find.text('Rewrite'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Export verified document'));
    await tester.pumpAndSettle();
    expect(picker.saveCalls, 1);
    expect(fake.calls.map((call) => call.$1), [
      'document.import',
      'document.rewrite',
    ]);
  });

  testWidgets('READY and rewrite transitions delegate exact request', (
    tester,
  ) async {
    final fake = WireFake()..rewriteResponse = Completer<Object?>();
    await boot(tester, fake);
    expect(find.text('READY'), findsOneWidget);
    await rewrite(tester);
    expect(find.text('REWRITING'), findsOneWidget);
    expect(fake.calls.single.$1, 'rewrite');
    expect(fake.calls.single.$2, {
      'original': 'Synthetic source.',
      'intent': 'Be concise',
      'context': 'work.email',
      'constraints': ['Keep names', 'Keep dates'],
    });
    fake.rewriteResponse!.complete(fake.receipt);
    await tester.pumpAndSettle();
    expect(find.text('RESULT'), findsOneWidget);
    expect(find.byKey(const Key('verified')), findsOneWidget);
    expect(find.byKey(const Key('result')), findsOneWidget);
    expect(
      tester.widget<SelectableText>(find.byKey(const Key('result'))).data,
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
            .widget<FilledButton>(find.widgetWithText(FilledButton, 'Rewrite'))
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
    expect(find.text('VERIFICATION_REJECTED'), findsOneWidget);
    expect(find.byKey(const Key('verified')), findsNothing);
    expect(find.byKey(const Key('result')), findsNothing);
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
            field('Edit result'),
            'Synthetic edited result.',
          );
        }
        final button = find.text(
          event == 'accept' ? 'Accept' : 'Submit edited feedback',
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

  testWidgets(
    'example writing requires ownership authorization and exact context',
    (tester) async {
      final fake = WireFake();
      await boot(tester, fake);
      await tester.enterText(field('Explicit context'), 'friends.chat');
      await tester.enterText(field('Writing example'), 'Synthetic example.');
      await tester.tap(
        find.text('I own this writing and authorize storing it'),
      );
      await tester.pumpAndSettle();
      await tester.ensureVisible(find.text('Save authorized example'));
      await tester.tap(find.text('Save authorized example'));
      await tester.pumpAndSettle();
      expect(fake.calls.single.$1, 'example.write');
      expect(fake.calls.single.$2, containsPair('context', 'friends.chat'));
      expect(fake.calls.single.$2, containsPair('authorized', true));
      expect(fake.calls.single.$2, containsPair('learning_eligible', false));
      expect(fake.calls.single.$2, containsPair('source_kind', 'user_owned'));
    },
  );

  testWidgets('example failure shows safe reason and named pending action', (
    tester,
  ) async {
    final fake = WireFake()
      ..operationFailure = const EngineException(
        EngineFailure.protectedStorage,
        safeCode: 'STORAGE_BOUNDARY_INVALID',
        safePhase: 'directory_acl_verify',
        safePhaseDetail: 'acl_rule_count_mismatch',
      );
    await boot(tester, fake);
    await tester.enterText(field('Explicit context'), 'casual.chat');
    await tester.enterText(field('Writing example'), 'Synthetic owned sample.');
    await tester.tap(find.text('I own this writing and authorize storing it'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Save authorized example'));
    await tester.tap(find.text('Save authorized example'));
    await tester.pumpAndSettle();

    expect(fake.calls, hasLength(1));
    expect(fake.calls.single.$1, 'example.write');
    expect(find.text('PROTECTED_STORAGE_ERROR'), findsOneWidget);
    expect(find.textContaining('STORAGE_BOUNDARY_INVALID'), findsOneWidget);
    expect(
      find.textContaining('profile directory protection check'),
      findsOneWidget,
    );
    expect(find.textContaining('unexpected ACL rule count'), findsOneWidget);
    expect(find.byKey(const Key('pendingNotice')), findsOneWidget);
    expect(find.textContaining('same request ID'), findsOneWidget);
    expect(
      find.text('Retry writing example save with same ID'),
      findsOneWidget,
    );
    expect(
      tester
          .widget<FilledButton>(find.widgetWithText(FilledButton, 'Rewrite'))
          .onPressed,
      isNull,
    );
    expect(find.textContaining('credential'), findsNothing);
    expect(
      tester
          .widget<OutlinedButton>(
            find.widgetWithText(OutlinedButton, 'Open .txt or .md document'),
          )
          .onPressed,
      isNull,
    );
  });

  testWidgets('engine exit preserves uncertain mutation status', (
    tester,
  ) async {
    final fake = WireFake()
      ..operationFailure = const EngineException(EngineFailure.profileDatabase);
    await boot(tester, fake);
    await tester.enterText(field('Explicit context'), 'casual.chat');
    await tester.enterText(field('Writing example'), 'Synthetic owned sample.');
    await tester.tap(find.text('I own this writing and authorize storing it'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Save authorized example'));
    await tester.tap(find.text('Save authorized example'));
    await tester.pumpAndSettle();
    fake.onExit!();
    await tester.pumpAndSettle();

    expect(find.text('ENGINE_UNAVAILABLE'), findsOneWidget);
    expect(find.text('Unconfirmed writing example save'), findsOneWidget);
    expect(
      tester.widget<Text>(find.byKey(const Key('pendingNotice'))).data,
      contains('status is unknown'),
    );
    expect(find.text('Retry writing example save with same ID'), findsNothing);
  });

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

  testWidgets(
    'uncertain mutation has no automatic retry and manual confirmation reuses payload',
    (tester) async {
      final fake = WireFake();
      await boot(tester, fake);
      await rewrite(tester);
      await tester.pumpAndSettle();
      fake.operationFailure = const EngineException(EngineFailure.operation);
      await tester.ensureVisible(find.text('Accept'));
      await tester.tap(find.text('Accept'));
      await tester.pumpAndSettle();
      expect(fake.calls, hasLength(2));
      final originalMutation = fake.calls.last;
      fake.operationFailure = null;
      await tester.ensureVisible(
        find.text('Retry feedback submission with same ID'),
      );
      await tester.tap(find.text('Retry feedback submission with same ID'));
      await tester.pumpAndSettle();
      expect(fake.calls.last, originalMutation);
      expect(fake.calls, hasLength(3));
    },
  );

  testWidgets('definite mutation rejection clears pending state', (
    tester,
  ) async {
    final fake = WireFake()
      ..operationFailure = const EngineException(EngineFailure.invalidRequest);
    await boot(tester, fake);
    await tester.enterText(field('Explicit context'), 'casual.chat');
    await tester.enterText(field('Writing example'), 'Synthetic owned sample.');
    await tester.tap(find.text('I own this writing and authorize storing it'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Save authorized example'));
    await tester.tap(find.text('Save authorized example'));
    await tester.pumpAndSettle();

    expect(fake.calls, hasLength(1));
    expect(find.byKey(const Key('pending-mutation')), findsNothing);
    expect(find.textContaining('No change was saved.'), findsOneWidget);
  });
}
