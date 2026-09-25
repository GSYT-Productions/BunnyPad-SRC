import SwiftUI
import Combine
import UniformTypeIdentifiers

struct TextSnapshot: Sendable {
    var text: String
    var encoding: String.Encoding = .utf8
    var hasBOM = false
    var lineEnding = "\n"

    nonisolated static func decode(_ data: Data) throws -> TextSnapshot {
        guard data.count <= 16 * 1024 * 1024 else { throw TextFileError.tooLarge }
        let encoding: String.Encoding
        let payload: Data
        let hasBOM: Bool
        if data.starts(with: [0xFF, 0xFE]) {
            encoding = .utf16LittleEndian
            payload = data.dropFirst(2)
            hasBOM = true
        } else if data.starts(with: [0xFE, 0xFF]) {
            encoding = .utf16BigEndian
            payload = data.dropFirst(2)
            hasBOM = true
        } else {
            hasBOM = data.starts(with: [0xEF, 0xBB, 0xBF])
            payload = hasBOM ? data.dropFirst(3) : data
            encoding = String(data: payload, encoding: .utf8) == nil ? .isoLatin1 : .utf8
        }
        guard let text = String(data: payload, encoding: encoding), !text.contains("\0") else {
            throw TextFileError.unsupported
        }
        let ending = text.contains("\r\n") ? "\r\n" : (text.contains("\r") ? "\r" : "\n")
        return TextSnapshot(
            text: text.replacingOccurrences(of: "\r\n", with: "\n").replacingOccurrences(of: "\r", with: "\n"),
            encoding: encoding, hasBOM: hasBOM, lineEnding: ending
        )
    }

    nonisolated func encoded() throws -> Data {
        let output = text.replacingOccurrences(of: "\n", with: lineEnding)
        guard var data = output.data(using: encoding, allowLossyConversion: false) else {
            throw TextFileError.unrepresentable
        }
        if hasBOM {
            let prefix: [UInt8] = encoding == .utf16LittleEndian ? [0xFF, 0xFE]
                : encoding == .utf16BigEndian ? [0xFE, 0xFF] : [0xEF, 0xBB, 0xBF]
            data.insert(contentsOf: prefix, at: 0)
        }
        guard data.count <= 16 * 1024 * 1024 else { throw TextFileError.tooLarge }
        return data
    }
}

enum TextFileError: LocalizedError {
    case tooLarge, unsupported, unrepresentable

    var errorDescription: String? {
        switch self {
        case .tooLarge: "This file is larger than BunnyPad’s 16 MB editing limit. The file has not been changed."
        case .unsupported: "This file is not a supported plain-text document."
        case .unrepresentable: "Some characters cannot be saved in the original encoding. Choose Format > Use UTF-8 Encoding, then save again."
        }
    }
}

final class NoteDocument: ReferenceFileDocument, ObservableObject {
    typealias Snapshot = TextSnapshot

    static let readableContentTypes: [UTType] = [.plainText]
    static let writableContentTypes: [UTType] = [.plainText]

    @Published var content = TextSnapshot(text: "")

    init() {}

    required init(configuration: ReadConfiguration) throws {
        guard let data = configuration.file.regularFileContents else {
            throw TextFileError.unsupported
        }
        self.content = try TextSnapshot.decode(data)
    }

    func snapshot(contentType: UTType) throws -> TextSnapshot {
        content
    }

    func fileWrapper(snapshot: TextSnapshot, configuration: WriteConfiguration) throws -> FileWrapper {
        FileWrapper(regularFileWithContents: try snapshot.encoded())
    }

    func replace(with newContent: TextSnapshot, undoManager: UndoManager?) {
        let previous = content
        if previous.encoding != newContent.encoding ||
            previous.hasBOM != newContent.hasBOM ||
            previous.lineEnding != newContent.lineEnding {
            undoManager?.registerUndo(withTarget: self) { document in
                document.replace(with: previous, undoManager: undoManager)
            }
        } else if previous.text != newContent.text {
            let (location, deletedText, insertedText) = NoteDocument.computeEdit(oldText: previous.text, newText: newContent.text)
            undoManager?.registerUndo(withTarget: self) { document in
                document.applyEdit(location: location, deletedText: insertedText, insertedText: deletedText, undoManager: undoManager)
            }
        }
        content = newContent
    }

    private static func computeEdit(oldText: String, newText: String) -> (location: Int, deletedText: String, insertedText: String) {
        var oldStart = oldText.startIndex
        var newStart = newText.startIndex
        let oldEnd = oldText.endIndex
        let newEnd = newText.endIndex

        while oldStart < oldEnd && newStart < newEnd && oldText[oldStart] == newText[newStart] {
            oldText.formIndex(after: &oldStart)
            newText.formIndex(after: &newStart)
        }

        var oldBack = oldEnd
        var newBack = newEnd

        while oldBack > oldStart && newBack > newStart {
            let prevOld = oldText.index(before: oldBack)
            let prevNew = newText.index(before: newBack)
            if oldText[prevOld] != newText[prevNew] {
                break
            }
            oldBack = prevOld
            newBack = prevNew
        }

        let location = oldText.distance(from: oldText.startIndex, to: oldStart)
        let deletedText = String(oldText[oldStart..<oldBack])
        let insertedText = String(newText[newStart..<newBack])

        return (location, deletedText, insertedText)
    }

    private func applyEdit(location: Int, deletedText: String, insertedText: String, undoManager: UndoManager?) {
        var newText = content.text
        guard let startIdx = newText.index(newText.startIndex, offsetBy: location, limitedBy: newText.endIndex) else { return }
        guard let endIdx = newText.index(startIdx, offsetBy: deletedText.count, limitedBy: newText.endIndex) else { return }
        newText.replaceSubrange(startIdx..<endIdx, with: insertedText)

        let editLocation = location
        let oldDeleted = deletedText
        let oldInserted = insertedText

        undoManager?.registerUndo(withTarget: self) { document in
            document.applyEdit(location: editLocation, deletedText: oldInserted, insertedText: oldDeleted, undoManager: undoManager)
        }

        var updatedSnapshot = content
        updatedSnapshot.text = newText
        content = updatedSnapshot
    }
}
