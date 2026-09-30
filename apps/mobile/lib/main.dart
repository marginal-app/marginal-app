import 'dart:collection';
import 'dart:developer';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';

import 'highlight_store.dart';
import 'selection_menu_policy.dart';

const _startUrl = 'https://example.com';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MarginalApp());
}

class MarginalApp extends StatelessWidget {
  const MarginalApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Marginal',
      theme: ThemeData(colorSchemeSeed: const Color(0xFF5B5BD6)),
      home: const ReaderScreen(),
    );
  }
}

class ReaderScreen extends StatefulWidget {
  const ReaderScreen({super.key});

  @override
  State<ReaderScreen> createState() => _ReaderScreenState();
}

class _ReaderScreenState extends State<ReaderScreen> {
  final _store = HighlightStore();
  late final Future<String> _bridgeSource = rootBundle.loadString(
    'assets/bridge/marginal.js',
  );
  SelectionMenuPolicy _policy = SelectionMenuPolicy.hideSystem;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Marginal'),
        actions: [
          PopupMenuButton<SelectionMenuPolicy>(
            initialValue: _policy,
            onSelected: (policy) => setState(() => _policy = policy),
            itemBuilder: (context) => [
              for (final policy in SelectionMenuPolicy.values)
                PopupMenuItem(value: policy, child: Text(policy.label)),
            ],
          ),
        ],
      ),
      body: SafeArea(
        child: FutureBuilder<String>(
          future: _bridgeSource,
          builder: (context, snapshot) {
            final source = snapshot.data;
            if (source == null) return const SizedBox.shrink();
            // The context menu is fixed at creation, so a policy change
            // rebuilds the WebView.
            return InAppWebView(
              key: ValueKey(_policy),
              initialUrlRequest: URLRequest(url: WebUri(_startUrl)),
              initialSettings: InAppWebViewSettings(
                isInspectable: true,
                javaScriptEnabled: true,
              ),
              initialUserScripts: UnmodifiableListView([
                UserScript(
                  source: source,
                  injectionTime: UserScriptInjectionTime.AT_DOCUMENT_END,
                  forMainFrameOnly: true,
                ),
              ]),
              contextMenu: _policy.contextMenu,
              onWebViewCreated: (controller) {
                controller.addJavaScriptHandler(
                  handlerName: 'marginal',
                  callback: (args) {
                    final message = Map<String, dynamic>.from(
                      args.first as Map,
                    );
                    log(
                      '${message['type']} ${message['payload']}',
                      name: 'marginal',
                    );
                    return _store.handle(message);
                  },
                );
              },
              onConsoleMessage: (controller, message) {
                log(message.message, name: 'marginal.page');
              },
            );
          },
        ),
      ),
    );
  }
}
