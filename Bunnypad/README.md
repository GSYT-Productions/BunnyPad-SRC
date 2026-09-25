# BunnyPad for macOS

A native SwiftUI/AppKit port of `prettyfonts/v11-FPL2/PyQt6/main.py`.
The Windows/Python sources are unchanged. No Python or Qt installation is required.

## Build

Open `Bunnypad.xcodeproj` in Xcode 27.2 or later, select the Bunnypad scheme
and My Mac, then Run. The existing project targets macOS 27.2 and uses the
SwiftUI Document APIs. Signing uses the development team configured in Xcode.

## Features

- Native document windows, New, Open, Open Recent, Save, native document duplication,
  autosave and macOS document restoration; standard unsaved-document handling.
- Plain-text editing, clipboard actions, undo/redo, native Find and Replace (Command-F
  and Option-Command-F), Go to Line (Command-L), and date/time insertion.
- Word wrapping, native font panel, adjustable text size, and optional status bar
  showing line, column, character count, encoding and line endings.
- Native printing (Command-P), with Save as PDF in the system print dialog.
- Settings, light/dark appearance, accessible native controls, and original branding
  and attribution in About BunnyPad.

UTF-8, UTF-8 with BOM, BOM-marked UTF-16, and Latin-1 documents can be opened.
The original encoding and predominant detected line-ending style are preserved;
files with mixed line endings are normalized to CRLF if present, otherwise CR or LF.
New files use UTF-8 and LF. Format > Use UTF-8 Encoding converts a legacy document
when new characters cannot be represented in its original encoding. This is undoable.
Files over 16 MiB are rejected without truncating or overwriting their contents.

## Platform differences

The Mac version uses system document restoration instead of importing Python's
temporary-session files. Windows installers, the Windows update checker, tool-download
launcher, custom translation files, system-information dialog and Easter eggs are not
ported. Source and help are available from the Help menu. Font size, wrapping and
status-bar preferences persist; the font family is selected per document window.

## Verification

The project builds and launches in Xcode. Executed checks cover six byte-preserving
encoding round trips (including emoji, CRLF, BOMs, UTF-16 and Latin-1), binary/oversize
rejection, document undo/redo, and Unicode-aware line navigation. The editor preview
was rendered and inspected. Interactive save-dialog, restoration, Find/Replace and
printer flows still need a manual acceptance pass on the target Mac.

Suggested acceptance pass: create two documents, edit and undo/redo independently,
save and reopen each, find and replace text, navigate to the last line, change font
and wrapping, print to PDF, then quit and reopen with document restoration enabled.

Original BunnyPad and artwork: https://github.com/GSYT-Productions/BunnyPad-SRC
Apache License 2.0; see the repository's root LICENSE and README for attribution.
