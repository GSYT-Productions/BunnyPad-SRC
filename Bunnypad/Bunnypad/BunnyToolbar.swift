import AppKit
import SwiftUI

enum BunnyTheme {
    static let gold = Color(red: 1, green: 0.77, blue: 0.23)
    static let editorGradient = LinearGradient(
        colors: [
            Color(red: 0.10, green: 0.38, blue: 0.68),
            Color(red: 0.45, green: 0.25, blue: 0.73),
            Color(red: 0.77, green: 0.51, blue: 0.65)
        ],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )
    static let barGradient = LinearGradient(
        colors: [
            Color(red: 0.12, green: 0.40, blue: 0.82),
            Color(red: 0.52, green: 0.24, blue: 0.91),
            Color(red: 0.84, green: 0.42, blue: 0.71)
        ],
        startPoint: .leading, endPoint: .trailing
    )
}

struct BunnyToolbar: View {
    let session: EditorSession
    @Environment(\.undoManager) private var undoManager

    var body: some View {
            HStack(spacing: 4) {
                tool("New", icon: "doc.badge.plus") { send(#selector(NSDocumentController.newDocument(_:))) }
                tool("Open", icon: "folder.fill") { send(#selector(NSDocumentController.openDocument(_:))) }
                tool("Save", icon: "square.and.arrow.down.fill") { send(#selector(NSDocument.save(_:))) }
                tool("Print", icon: "printer.fill") { session.printDocument() }
                separator
                tool("Cut", icon: "scissors") { session.textView?.cut(nil) }
                tool("Copy", icon: "doc.on.doc.fill") { session.textView?.copy(nil) }
                tool("Paste", icon: "clipboard.fill") { session.textView?.paste(nil) }
                separator
                tool("Undo", icon: "arrow.uturn.backward") { undoManager?.undo() }
                    .disabled(undoManager?.canUndo != true)
                tool("Redo", icon: "arrow.uturn.forward") { undoManager?.redo() }
                    .disabled(undoManager?.canRedo != true)
                separator
                tool("Find", icon: "magnifyingglass") { session.find() }
                tool("Replace", icon: "arrow.left.arrow.right") { session.find(replacing: true) }
                tool("Font", icon: "textformat") { showFonts() }
                Spacer(minLength: 0)
            }
            .buttonStyle(BunnyToolButtonStyle())
        .padding(.horizontal, 10)
        .padding(.vertical, 5)
        .background(BunnyTheme.barGradient)
    }

    private var separator: some View {
        Rectangle().fill(.white.opacity(0.3)).frame(width: 1, height: 18).padding(.horizontal, 4)
    }

    private func tool(_ title: LocalizedStringKey, icon: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Label(title, systemImage: icon).labelStyle(.iconOnly)
        }
        .help(Text(title))
    }

    private func send(_ action: Selector) {
        session.textView?.window?.makeFirstResponder(session.textView)
        NSApp.sendAction(action, to: nil, from: nil)
    }

    private func showFonts() {
        session.textView?.window?.makeFirstResponder(session.textView)
        NSFontManager.shared.orderFrontFontPanel(nil)
    }
}

private struct BunnyToolButtonStyle: ButtonStyle {
    @Environment(\.isEnabled) private var isEnabled

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 16, weight: .semibold))
            .foregroundStyle(BunnyTheme.gold.opacity(isEnabled ? 1 : 0.4))
            .frame(width: 27, height: 26)
            .background(.white.opacity(configuration.isPressed ? 0.24 : 0), in: RoundedRectangle(cornerRadius: 3))
            .contentShape(Rectangle())
    }
}
