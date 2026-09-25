import AppKit
import SwiftUI

let bunnyPadRepositoryURL = URL(string: "https://github.com/GSYT-Productions/BunnyPad-SRC") ?? URL(fileURLWithPath: "/")

@main
struct BunnypadApp: App {
    var body: some Scene {
        DocumentGroup(newDocument: { NoteDocument() }) { configuration in
            ContentView(document: configuration.document)
        }
        .defaultSize(width: 860, height: 620)
        .commands {
            EditorCommands()
        }

        Settings { SettingsView() }

        Window("About BunnyPad", id: "about") {
            AboutView()
        }
        .windowResizability(.contentSize)
    }
}

struct EditorCommands: Commands {
    @FocusedValue(\.editorSession) private var session
    @Environment(\.openWindow) private var openWindow
    @AppStorage("wordWrap") private var wordWrap = true
    @AppStorage("showStatusBar") private var showStatusBar = true

    var body: some Commands {
        CommandGroup(replacing: .appInfo) {
            Button("About BunnyPad") { openWindow(id: "about") }
        }
        CommandGroup(after: .saveItem) {
            Divider()
            Button("Print…") { session?.printDocument() }
                .keyboardShortcut("p")
                .disabled(session == nil)
        }
        CommandGroup(after: .textEditing) {
            Divider()
            Button("Find…") { session?.find() }.keyboardShortcut("f")
            Button("Find and Replace…") { session?.find(replacing: true) }
                .keyboardShortcut("f", modifiers: [.command, .option])
            Button("Go to Line…") { session?.showGoToLine = true }
                .keyboardShortcut("l")
            Divider()
            Button("Insert Date and Time") { session?.insertDate() }
                .keyboardShortcut("d", modifiers: [.command, .shift])
        }
        CommandMenu("Format") {
            Toggle("Word Wrap", isOn: $wordWrap)
            Button("Font…") {
                guard let textView = session?.textView else { return }
                textView.window?.makeFirstResponder(textView)
                NSFontManager.shared.orderFrontFontPanel(nil)
            }
            .keyboardShortcut("t")
            .disabled(session == nil)
            Button("Use UTF-8 Encoding") {
                (session?.textView as? BunnyTextView)?.useUTF8(nil)
            }
            .disabled(session == nil)
        }
        CommandGroup(after: .toolbar) {
            Toggle("Show Status Bar", isOn: $showStatusBar)
        }
        CommandGroup(replacing: .help) {
            Link("BunnyPad Source and Help", destination: bunnyPadRepositoryURL)
        }
    }
}
