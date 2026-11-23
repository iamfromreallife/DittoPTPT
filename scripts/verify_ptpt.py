#!/usr/bin/env python3
"""Ensure the pt-PT language file covers the current Ditto UI identifiers."""
from pathlib import Path
from xml.etree import ElementTree as ET

root = Path(__file__).resolve().parent.parent / "Debug" / "Language"
english = ET.parse(root / "English.xml").getroot()
brazil = ET.parse(root / "Portuguese (Brazil).xml").getroot()
portugal = ET.parse(root / "Portuguese.xml").getroot()

def keys(doc):
    result = {}
    for section in doc:
        for item in section.findall("Item"):
            item_id = item.get("ID", "").strip()
            english_text = item.get("English_Text", "")
            # Submenu headings have no numeric ID and are matched by their source label.
            identifier = (section.tag, item_id, english_text if item_id == "-1" else "")
            result[identifier] = (item.text or "").strip()
    return result

pt = keys(portugal)
missing = []
untranslated = []
internal = {"NEXTTABCONTROL", "PREVTABCONTROL", "HOMELIST",
            "MODIFIER_ACTVE_SELECTIONUP", "MODIFIER_ACTVE_SELECTIONDOWN",
            "MODIFIER_ACTVE_MOVEFIRST", "MODIFIER_ACTVE_MOVELAST"}
for reference in (english, brazil):
    for key in keys(reference):
        if key not in pt:
            missing.append(key)
        elif not pt[key] and key[2] not in internal and key[1] not in {"10","11","15","16","17","18","20"}:
            untranslated.append(key)
if missing or untranslated:
    raise SystemExit(f"Missing pt-PT entries: {missing}\nBlank translations: {untranslated}")
assert portugal.attrib.get("LanguageCode") == "pt_PT"

# Verify all runtime GetString calls in the application's own C++ source.
import re
string_table = {
    item.get("ID") for item in portugal.find("Ditto_String_Table").findall("Item")
}
untranslated_cpp = {}
for source_file in (root.parent.parent / "src").glob("*.cpp"):
    source = source_file.read_text(encoding="utf-8-sig", errors="replace")
    keys_used = set(re.findall(
        r'\bGetString\s*\(\s*(?:_T\s*\(\s*)?"([A-Za-z_]\w*)"', source))
    missing_keys = sorted(keys_used - string_table)
    if missing_keys:
        untranslated_cpp[source_file.name] = missing_keys
if untranslated_cpp:
    raise SystemExit(f"Missing C++ GetString translations: {untranslated_cpp}")
print(f"pt-PT coverage passed: {len(pt)} identifiers; C++ UI keys and both reference files checked")
