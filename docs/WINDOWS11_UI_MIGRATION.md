# Windows 11 user-interface migration

## Current, built implementation

Ditto is a C++ MFC/Win32 application. Its fast clipboard/history popup, database,
hotkeys, add-ins, editor, networking and tray icon share a process and multiple
custom-drawn controls. Removing those controls without equivalent replacements
would delete functionality. This change set is therefore a **compatible Windows
SDK visual modernization**, not a completed rewrite to Windows App SDK / WinUI 3.

- Windows SDK DWM: rounded window corners, Windows 11 light/dark caption
  preferences, subtle system border, optional system-drawn backdrop.
- UI-thread-only CBT activation hook gives all legacy top-level MFC dialogs
  the updated non-client chrome, without changing control IDs or messages.
- Explorer-native visual styles for standard list/tree/combo controls in dialogs.
- Two Fluent-inspired light/dark themes for the main clipboard UI, selected
  automatically when the application's Theme setting is set to follow Windows.
- Updated Segoe UI dialog typography; existing control layout, command IDs
  and clipboard behaviour remain intact.
- All user-selected custom themes, stored user options and database paths remain.

The Win32 UI must still be visually tested at 100%, 150% and 200% DPI, across
light/dark and Windows high-contrast modes. A successful build does not prove
that the full interaction matrix is visually correct.

## Full Windows App SDK migration (not yet implemented)

A complete WinUI 3 migration must **not** be labelled done until these
capabilities have 1:1 feature parity and tests:

1. Move clipboard monitoring/DB access/paste operations into a stable
   native C++ core with explicit thread-safe interfaces; keep the Win32
   clipboard listener, custom formats, elevated-paste broker and add-ins.
2. Introduce an unpackaged, self-contained Windows App SDK (WinUI 3)
   shell and bootstrapper, with Windows App SDK framework assets bundled
   in the portable ZIP (not merely a NuGet reference).
3. Replace the Quick Paste window with a WinUI 3 ItemsRepeater/virtualized
   list, search, nested groups, row preview and system accent colour support.
   Preserve all context menus, keyboard/mouse gestures and drag/drop.
4. Migrate the settings PropertySheet, history editor, clip properties,
   advanced database management, statistics and connection dialogs.
5. Integrate tray icon and background hotkey handling with the same core;
   start-on-login and command-line modes must stay compatible.
6. Automate UI interaction, accessibility, focus, DPI, high contrast and
   packaging tests. Test SQLite migrations and external database paths.
7. Only after parity, remove unused legacy MFC views and ship the
   self-contained Windows App SDK portable build.

Microsoft reference: https://learn.microsoft.com/windows/apps/desktop/modernize/host-controls-existing-desktop-apps

The existing Windows App SDK / WinUI 3 islands integration is not yet part
of this build; no WinUI runtime dependency is added at this stage. The
existing portable ZIP therefore remains executable with its existing
runtime dependencies.
