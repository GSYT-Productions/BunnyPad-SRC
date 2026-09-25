import AppKit
import SwiftUI

@Observable
final class EditorSession {
    weak var textView: NSTextView?
    var line = 1
    var column = 1
    var showGoToLine = false

    func find(replacing: Bool = false) {
        guard let textView else { return }
        textView.window?.makeFirstResponder(textView)
        let item = NSMenuItem()
        item.tag = replacing ? NSTextFinder.Action.showReplaceInterface.rawValue : NSTextFinder.Action.showFindInterface.rawValue
        textView.performFindPanelAction(item)
    }

    func insertDate() {
        guard let textView else { return }
        textView.insertText(Date.now.formatted(date: .abbreviated, time: .shortened), replacementRange: textView.selectedRange())
    }

    func go(to line: Int) -> Bool {
        guard let textView, line > 0 else { return false }
        let lines = textView.string.components(separatedBy: "\n")
        guard line <= lines.count else { return false }
        let position = lines.prefix(line - 1).reduce(0) { $0 + $1.utf16.count + 1 }
        textView.window?.makeFirstResponder(textView)
        textView.setSelectedRange(NSRange(location: position, length: 0))
        textView.scrollRangeToVisible(textView.selectedRange())
        return true
    }

    func printDocument() {
        guard let textView else { return }
        // Use a separate, wrapped view so printing never changes the editor layout.
        guard let info = NSPrintInfo.shared.copy() as? NSPrintInfo else { return }
        info.horizontalPagination = .fit
        info.verticalPagination = .automatic
        info.isHorizontallyCentered = false
        info.isVerticallyCentered = false
        let width = info.paperSize.width - info.leftMargin - info.rightMargin
        let printable = NSTextView(frame: NSRect(x: 0, y: 0, width: width, height: 0))
        printable.isRichText = false
        printable.appearance = NSAppearance(named: .aqua)
        printable.textColor = .black
        printable.backgroundColor = .white
        printable.drawsBackground = true
        printable.font = textView.font
        printable.string = textView.string
        printable.textContainer?.containerSize = NSSize(width: width, height: .greatestFiniteMagnitude)
        printable.textContainer?.widthTracksTextView = true
        guard let container = printable.textContainer else { return }
        printable.layoutManager?.ensureLayout(for: container)
        let height = printable.layoutManager?.usedRect(for: container).height ?? 0
        printable.setFrameSize(NSSize(width: width, height: max(height + 24, 24)))
        let operation = NSPrintOperation(view: printable, printInfo: info)
        operation.showsPrintPanel = true
        operation.showsProgressPanel = true
        if let window = textView.window {
            operation.runModal(for: window, delegate: nil, didRun: nil, contextInfo: nil)
        } else {
            operation.run()
        }
    }
}

struct EditorSessionKey: FocusedValueKey {
    typealias Value = EditorSession
}

extension FocusedValues {
    var editorSession: EditorSession? {
        get { self[EditorSessionKey.self] }
        set { self[EditorSessionKey.self] = newValue }
    }
}

struct NativeTextEditor: NSViewRepresentable {
    let document: NoteDocument
    let session: EditorSession
    let wrapsLines: Bool
    let fontSize: Double
    @Environment(\.undoManager) private var undoManager

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeNSView(context: Context) -> NSScrollView {
        let scroll = NSScrollView()
        scroll.drawsBackground = false
        scroll.contentView.drawsBackground = false
        scroll.hasVerticalScroller = true
        scroll.autohidesScrollers = true
        let text = BunnyTextView(frame: .zero)
        text.convertEncoding = { context.coordinator.useUTF8() }
        text.drawsBackground = false
        text.textColor = .white
        text.insertionPointColor = .white
        text.isRichText = false
        // Model undo uses the document's environment manager, which also drives autosave.
        text.allowsUndo = false
        text.usesFindBar = true
        text.isIncrementalSearchingEnabled = true
        text.isAutomaticQuoteSubstitutionEnabled = false
        text.isAutomaticDashSubstitutionEnabled = false
        text.isAutomaticTextReplacementEnabled = false
        text.isVerticallyResizable = true
        text.minSize = .zero
        text.maxSize = NSSize(width: CGFloat.greatestFiniteMagnitude, height: CGFloat.greatestFiniteMagnitude)
        text.textContainerInset = NSSize(width: 20, height: 20)
        text.font = .monospacedSystemFont(ofSize: fontSize, weight: .regular)
        text.setAccessibilityLabel("Document text")
        text.string = document.content.text
        text.delegate = context.coordinator
        scroll.documentView = text
        session.textView = text
        configure(text, in: scroll)
        return scroll
    }

    func updateNSView(_ scroll: NSScrollView, context: Context) {
        context.coordinator.parent = self
        guard let text = scroll.documentView as? NSTextView else { return }
        if text.string != document.content.text {
            let selection = text.selectedRange()
            text.string = document.content.text
            context.coordinator.resetLineStarts()
            text.setSelectedRange(NSRange(location: min(selection.location, text.string.utf16.count), length: 0))
        }
        if text.font?.pointSize != CGFloat(fontSize) {
            text.font = NSFontManager.shared.convert(text.font ?? .systemFont(ofSize: fontSize), toSize: fontSize)
        }
        configure(text, in: scroll)
    }

    private func configure(_ text: NSTextView, in scroll: NSScrollView) {
        scroll.hasHorizontalScroller = !wrapsLines
        text.isHorizontallyResizable = !wrapsLines
        text.autoresizingMask = wrapsLines ? [.width] : []
        text.textContainer?.widthTracksTextView = wrapsLines
        text.textContainer?.containerSize = NSSize(
            width: wrapsLines ? max(scroll.contentSize.width - 40, 1) : CGFloat.greatestFiniteMagnitude,
            height: CGFloat.greatestFiniteMagnitude
        )
        let width = wrapsLines ? scroll.contentSize.width : max(text.frame.width, scroll.contentSize.width)
        text.setFrameSize(NSSize(width: width, height: text.frame.height))
    }

    final class Coordinator: NSObject, NSTextViewDelegate {
        var parent: NativeTextEditor
        private var lineStarts: [Int] = []

        init(_ parent: NativeTextEditor) { self.parent = parent }

        func resetLineStarts() {
            lineStarts.removeAll()
        }

        func useUTF8() {
            var snapshot = parent.document.content
            snapshot.encoding = .utf8
            snapshot.hasBOM = false
            parent.document.replace(with: snapshot, undoManager: parent.undoManager)
        }

        func textDidChange(_ notification: Notification) {
            guard let text = notification.object as? NSTextView else { return }
            updateLineStarts(for: text.string)
            var snapshot = parent.document.content
            snapshot.text = text.string
            parent.document.replace(with: snapshot, undoManager: parent.undoManager)
            updatePosition(text)
        }

        func textViewDidChangeSelection(_ notification: Notification) {
            guard let text = notification.object as? NSTextView else { return }
            updatePosition(text)
        }

        private func updateLineStarts(for string: String) {
            var starts = [0]
            var idx = 0
            for unit in string.utf16 {
                idx += 1
                if unit == 0x0A {
                    starts.append(idx)
                }
            }
            self.lineStarts = starts
        }

        private func lineIndex(for offset: Int) -> Int {
            guard !lineStarts.isEmpty else { return 0 }
            var low = 0
            var high = lineStarts.count - 1
            var result = 0
            while low <= high {
                let mid = (low + high) / 2
                if lineStarts[mid] <= offset {
                    result = mid
                    low = mid + 1
                } else {
                    high = mid - 1
                }
            }
            return result
        }

        private func updatePosition(_ text: NSTextView) {
            let nsString = text.string as NSString
            let length = nsString.length
            let offset = min(text.selectedRange().location, length)

            if lineStarts.isEmpty {
                updateLineStarts(for: text.string)
            }

            let lineIdx = lineIndex(for: offset)
            let lineStart = lineStarts[lineIdx]
            let line = lineIdx + 1

            let linePrefixLength = min(max(0, offset - lineStart), max(0, length - lineStart))
            let column: Int
            if linePrefixLength > 0 {
                let linePrefix = nsString.substring(with: NSRange(location: lineStart, length: linePrefixLength))
                column = linePrefix.count + 1
            } else {
                column = 1
            }

            Task { @MainActor [session = parent.session] in
                session.line = line
                session.column = column
            }
        }
    }
}
