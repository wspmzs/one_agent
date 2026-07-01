# -*- coding: utf-8 -*-
"""html-2-md 插件打包脚本。排除 __pycache__、test_output、process。"""
import zipfile, os

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, "html-2-md.zip")
EXCLUDE = {"__pycache__", "test_output", "process", ".git"}

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        for f in files:
            if f.endswith((".pyc", ".bak")):
                continue
            full = os.path.join(root, f)
            arc = os.path.relpath(full, SRC)
            z.write(full, arc)

print(f"[OK] html-2-md.zip ({os.path.getsize(OUT) / 1024:.0f} KB)")
