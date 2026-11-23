#!/usr/bin/env python3
"""Check the Windows 11 visual assets before a portable build."""
from pathlib import Path
from xml.etree import ElementTree as ET
import re

root = Path(__file__).resolve().parent.parent
theme_dir = root / "Debug" / "Themes"
theme_cpp = (root / "src" / "Theme.cpp").read_text(encoding="utf-8-sig")
window_header = (root / "src" / "Windows11UI.h").read_text(encoding="utf-8-sig")
resource = (root / "CP_Main.rc").read_text(encoding="utf-8-sig", errors="replace")
packager = (root / "DittoSetup" / "BuildPortableZIP.bat").read_text(encoding="utf-8-sig")

fields = {
    "CaptionLeft", "CaptionRight", "CaptionLeftTopMost", "CaptionRightTopMost",
    "CaptionLeftNotConnected", "CaptionRightNotConnected", "CaptionTextColor",
    "ListBoxOddRowsBG", "ListBoxEvenRowsBG", "ListBoxOddRowsText",
    "ListBoxEvenRowsText", "ListBoxSelectedBG", "ListBoxSelectedNoFocusBG",
    "ListBoxSelectedText", "ListBoxSelectedNoFocusText", "Border",
    "BorderTopMost", "BorderNotConnected", "GroupTreeBG", "GroupTreeText",
    "CaptionSize", "CaptionFontSize", "DescriptionWindowBG",
    "DescriptionWindowText", "ClipPastedColor", "MainWindowBG",
    "SearchTextBoxFocusBG", "SearchTextBoxFocusText",
    "SearchTextBoxFocusBorder", "SearchTextHighlight",
    "ScrollBarThumb", "ScrollBarThumbHover", "ScrollBarTrack",
}
for name in ("Windows11Light", "Windows11Dark"):
    document = ET.parse(theme_dir / f"{name}.xml").getroot()
    assert document.tag == "Ditto_Theme_File", name
    assert set(child.tag for child in document) == fields, name
    for child in document:
        value = (child.text or "").strip()
        if child.tag in {"CaptionSize", "CaptionFontSize"}:
            assert 12 <= int(value) <= 48, (name, child.tag, value)
        else:
            match = re.fullmatch(r"RGB\((\d+),(\d+),(\d+)\)", value)
            assert match and all(0 <= int(v) <= 255 for v in match.groups()), (name, child.tag, value)
    assert f'_T("{name}")' in theme_cpp
assert 'FONT 9, "Segoe UI"' in resource
for attr in (20, 33, 34, 38):
    assert f'static_cast<DWMWINDOWATTRIBUTE>({attr})' in window_header
assert 'InstallDialogHook' in window_header
assert 'copy ..\\Debug\\themes\\*.xml' in packager, "Portable ZIP must contain both Windows 11 themes"
print("Windows 11 theme and chrome checks passed")
