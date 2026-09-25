import AppKit

final class BunnyTextView: NSTextView {
    var convertEncoding: (() -> Void)?

    @objc func useUTF8(_ sender: Any?) {
        convertEncoding?()
    }

    override func changeFont(_ sender: Any?) {
        guard let manager = sender as? NSFontManager else { return }
        let selectedFont = manager.convert(font ?? .monospacedSystemFont(ofSize: 14, weight: .regular))
        font = selectedFont
        UserDefaults.standard.set(selectedFont.pointSize, forKey: "editorFontSize")
    }
}
