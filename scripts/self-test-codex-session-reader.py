#!/usr/bin/env python3
"""Regression checks for the deterministic Codex session reader."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("read_codex_session.py")
THREAD_ID = "11111111-2222-4333-8444-555555555555"


def run_reader(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )


def open_shared_writer(path: Path):
    if os.name != "nt":
        return path.open("r+b")

    import ctypes
    import msvcrt
    from ctypes import wintypes

    generic_read = 0x80000000
    generic_write = 0x40000000
    share_all = 0x00000001 | 0x00000002 | 0x00000004
    open_existing = 3
    handle_api = ctypes.WinDLL("kernel32", use_last_error=True)
    create_file = handle_api.CreateFileW
    create_file.argtypes = (
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    )
    create_file.restype = wintypes.HANDLE
    handle = create_file(
        str(path),
        generic_read | generic_write,
        share_all,
        None,
        open_existing,
        0x00000080,
        None,
    )
    if handle == ctypes.c_void_p(-1).value:
        raise OSError(ctypes.get_last_error(), "CreateFileW failed")
    descriptor = msvcrt.open_osfhandle(handle, os.O_RDWR | os.O_BINARY)
    return os.fdopen(descriptor, "r+b", closefd=True)


def assert_active_writer_snapshot() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        source = root / f"rollout-sample-{THREAD_ID}.jsonl"
        complete = b'{"type":"first"}\n{"type":"second"}\n'
        incomplete = b'{"type":"still-writing"'
        source.write_bytes(complete + incomplete)
        output = root / "snapshots"
        with open_shared_writer(source) as writer:
            completed = run_reader(
                "--thread-id",
                THREAD_ID,
                "--source",
                str(source),
                "--output-dir",
                str(output),
            )
            if completed.returncode != 0:
                raise AssertionError(completed.stderr)
            manifest = json.loads(completed.stdout)
            snapshot = Path(manifest["snapshot"])
            if snapshot.read_bytes() != complete:
                raise AssertionError("snapshot did not stop at the complete JSONL boundary")
            if manifest["complete_records"] != 2:
                raise AssertionError("complete record count is incorrect")
            if manifest["trailing_incomplete_bytes"] != len(incomplete):
                raise AssertionError("incomplete tail length is incorrect")
            if manifest["parse_errors"] != 0:
                raise AssertionError("valid complete records were reported as invalid")
            writer.seek(0, os.SEEK_END)
            writer.write(b'}\n')
            writer.flush()
            if snapshot.read_bytes() != complete:
                raise AssertionError("snapshot changed after the live source advanced")


def assert_exact_identity_and_ambiguity() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        sessions = root / "codex" / "sessions"
        first = sessions / "2026" / "01" / "01"
        first.mkdir(parents=True)
        (first / f"rollout-a-{THREAD_ID}.jsonl").write_text(
            '{"type":"one"}\n', encoding="utf-8"
        )
        output = root / "snapshots"
        completed = run_reader(
            "--thread-id",
            THREAD_ID,
            "--codex-home",
            str(root / "codex"),
            "--output-dir",
            str(output),
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr)

        second = sessions / "2026" / "01" / "02"
        second.mkdir(parents=True)
        (second / f"rollout-b-{THREAD_ID}.jsonl").write_text(
            '{"type":"two"}\n', encoding="utf-8"
        )
        ambiguous = run_reader(
            "--thread-id",
            THREAD_ID,
            "--codex-home",
            str(root / "codex"),
            "--output-dir",
            str(output),
        )
        if ambiguous.returncode != 2:
            raise AssertionError("ambiguous exact records did not fail closed")
        error = json.loads(ambiguous.stderr)["error"]
        if error["code"] != "session_record_ambiguous":
            raise AssertionError(f"unexpected ambiguity error: {error}")


def main() -> int:
    assert_active_writer_snapshot()
    assert_exact_identity_and_ambiguity()
    print("Codex 会话读取器回归通过：活动写入、完整边界和准确身份正常")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
