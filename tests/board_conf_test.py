#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2026 Styves Goupil
"""fm1.toml's KEY_smk37 as tools/build.py reads it (board_conf): the SMK-37's builds take it over KEY (an Elite
release's id_prefix_smk37, its pool_spare_smk37, its firmware.json's install_smk37 and screenshot_smk37), board and
model never; the FM-1's build reads fm1.toml as it is, its _smk37 keys unread. Run from the repo root:
  python3 tests/board_conf_test.py"""
import importlib
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
build = importlib.import_module("build")

failed = 0


def ok(cond, what):
    global failed
    print(("  ok   " if cond else "  FAIL ") + what)
    failed += not cond


TOML = '''name = "DRIFT"
id_prefix = "FM-1_47"          # dev FM-1_4700, releases FM-1_47XXYYZZ
pool_spare = 8192
install = "https://example.org/install/"
id_prefix_smk37 = "FM-1_4"     # SMK-37 Elite_4XXYYZZ: 20 characters
pool_spare_smk37 = 8032
install_smk37 = "https://example.org/install/smk37/"
board_smk37 = "fm1"
model_smk37 = "pro"
tags_smk37 = ["synth", "ambient"]
'''
with tempfile.TemporaryDirectory() as d:
    (Path(d) / "fm1.toml").write_text(TOML)
    conf = build.read_conf(Path(d) / "fm1.toml")

fm1 = build.board_conf(conf, "fm1")
ok(fm1 == conf and fm1["id_prefix"] == "FM-1_47" and fm1["pool_spare"] == 8192 and
   fm1["install"] == "https://example.org/install/", "the FM-1's build: fm1.toml as it is (its _smk37 keys unread)")
smk = build.board_conf(conf, "smk37")
ok(smk["id_prefix"] == "FM-1_4" and smk["pool_spare"] == 8032 and smk["install"] == "https://example.org/install/smk37/",
   "an SMK-37 build: id_prefix_smk37, pool_spare_smk37, install_smk37 over id_prefix, pool_spare, install")
ok(smk["tags"] == ["synth", "ambient"] and smk["name"] == "DRIFT", "any other key too (a list), the rest as it was")
ok("board" not in smk and "model" not in smk, "board_smk37 and model_smk37: never (the board and the model are the build's)")
ok(conf["id_prefix"] == "FM-1_47" and "pool_spare_smk37" in smk, "fm1.toml's own settings untouched, its _smk37 keys kept")
ok(build.board_conf({"_smk37": 1}, "smk37") == {"_smk37": 1}, "a bare _smk37 is no key's")
# the identity an Elite release gets from it (main: the model, the prefix's digits, XXYYZZ): 20 characters, the most
product = build.SMK_MODELS["elite"][2] + smk["id_prefix"][len("FM-1"):] + "%02d%02d%02d" % (3, 3, 1)
ok(product == "SMK-37 Elite_4030301" and len(product) == 20, f"an Elite 3.3.1 release: {product} ({len(product)} characters)")
ok(len(build.SMK_MODELS["elite"][2] + conf["id_prefix"][len("FM-1"):] + "030301") == 21,
   "with the FM-1's FM-1_47 it would be 21: over the package's 20")

print("board-conf: " + ("FAILED" if failed else "all passed"))
sys.exit(1 if failed else 0)
