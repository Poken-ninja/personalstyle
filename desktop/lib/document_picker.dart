import 'package:file_selector/file_selector.dart';

abstract interface class DocumentFilePicker {
  Future<String?> openDocument();
  Future<String?> saveDocument(String suggestedName);
}

class NativeDocumentFilePicker implements DocumentFilePicker {
  const NativeDocumentFilePicker();

  static const _documents = XTypeGroup(
    label: 'Text documents',
    extensions: ['txt', 'md'],
  );

  @override
  Future<String?> openDocument() async =>
      (await openFile(acceptedTypeGroups: [_documents]))?.path;

  @override
  Future<String?> saveDocument(String suggestedName) async =>
      (await getSaveLocation(
        suggestedName: suggestedName,
        acceptedTypeGroups: [_documents],
      ))?.path;
}
