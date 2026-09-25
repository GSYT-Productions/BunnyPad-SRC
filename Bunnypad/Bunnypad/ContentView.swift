import SwiftUI

struct ContentView: View {
    let document: NoteDocument
    @State private var session = EditorSession()
    @AppStorage("wordWrap") private var wordWrap = true
    @AppStorage("showStatusBar") private var showStatusBar = true
    @AppStorage("editorFontSize") private var fontSize = 14.0

    var body: some View {
        VStack(spacing: 0) {
            BunnyToolbar(session: session)
            NativeTextEditor(document: document, session: session, wrapsLines: wordWrap, fontSize: fontSize)
            if showStatusBar {
                EditorStatusBar(session: session, content: document.content)
            }
        }
        .frame(minWidth: 520, minHeight: 340)
        .focusedSceneValue(\.editorSession, session)
        .background(BunnyTheme.editorGradient)
        .overlay {
            Rectangle().strokeBorder(.white.opacity(0.3), lineWidth: 1)
                .allowsHitTesting(false)
        }
        .sheet(isPresented: $session.showGoToLine) {
            GoToLineView(session: session)
        }
    }
}

private struct EditorStatusBar: View {
    let session: EditorSession
    let content: TextSnapshot

    var body: some View {
        HStack {
            Text("Ln \(session.line), Col \(session.column)")
            Spacer()
            Text("\(content.text.count) characters")
            Divider().frame(height: 12)
            Text(content.encoding == .utf8 ? "UTF-8" : content.encoding == .isoLatin1 ? "Latin-1" : "UTF-16")
            Text(content.lineEnding == "\r\n" ? "CRLF" : content.lineEnding == "\r" ? "CR" : "LF")
        }
        .font(.caption)
        .foregroundStyle(.white)
        .padding(.horizontal, 12)
        .padding(.vertical, 5)
        .background(BunnyTheme.barGradient)
        .overlay(alignment: .top) {
            Rectangle().fill(.white.opacity(0.25)).frame(height: 1)
        }
    }
}

private struct GoToLineView: View {
    let session: EditorSession
    @Environment(\.dismiss) private var dismiss
    @State private var line = ""
    @State private var invalidLine = false

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Go to Line").font(.headline)
            TextField("Line number", text: $line)
                .onSubmit { navigate() }
            if invalidLine {
                Text("Enter a line number in this document.")
                    .foregroundStyle(.red)
            }
            HStack {
                Spacer()
                Button("Cancel") { dismiss() }.keyboardShortcut(.cancelAction)
                Button("Go") { navigate() }.keyboardShortcut(.defaultAction)
            }
        }
        .padding(24)
        .frame(width: 300)
    }

    private func navigate() {
        if let number = Int(line), session.go(to: number) {
            dismiss()
        } else {
            invalidLine = true
        }
    }
}

#Preview {
    ContentView(document: NoteDocument())
        .frame(width: 860, height: 620)
}

struct SettingsView: View {
    @AppStorage("wordWrap") private var wordWrap = true
    @AppStorage("showStatusBar") private var showStatusBar = true
    @AppStorage("editorFontSize") private var fontSize = 14.0

    var body: some View {
        Form {
            Toggle("Wrap long lines", isOn: $wordWrap)
            Toggle("Show status bar", isOn: $showStatusBar)
            Slider(value: $fontSize, in: 10...32, step: 1) {
                Text("Text size: \(Int(fontSize)) pt")
            }
            Text("Font and wrapping affect the editor’s appearance. Documents remain plain text.")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding(24)
        .frame(width: 420)
    }
}

#Preview("About BunnyPad") {
    AboutView()
}

struct AboutView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image("AboutLogo")
                .renderingMode(.original)
                .resizable()
                .scaledToFit()
                .frame(width: 96, height: 96)
                .accessibilityHidden(true)
            Text("BunnyPad").font(.largeTitle.bold())
            Text("The Newest and Cutest way to take notes")
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
            Text("BunnyPad by GSYT Productions")
                .multilineTextAlignment(.center)
            Text("An open-source notepad, dedicated to PBbunnypower. This native macOS port is developed by Aoterno Technologies, based on the original BunnyPad app.")
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
            Text("Original app by GarryStraitYT. Dedicated to PBbunnypower, creator of the BunnyPad icon. Thanks to the BunnyPad contributors.")
                .font(.caption)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
            Link("BunnyPad source and contributors", destination: bunnyPadRepositoryURL)
            Text("Licensed under Apache License 2.0").font(.caption).foregroundStyle(.secondary)
        }
        .padding(32)
        .frame(width: 420)
    }
}
