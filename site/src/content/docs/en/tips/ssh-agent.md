---
title: Skip the SSH passphrase prompt in VS Code Remote-SSH
description: Register your private key with ssh-agent once and avoid retyping the passphrase every time VS Code Remote-SSH connects
---

If VS Code Remote-SSH asks for your SSH key passphrase every time you connect to camphor (or any other host), register the key with `ssh-agent` once and the prompts mostly disappear. The VS Code docs explicitly recommend running an SSH Agent locally when you use a passphrase-protected key ([VS Code Tips & Tricks](https://code.visualstudio.com/docs/remote/troubleshooting)).

## Standard setup on Windows

### 1. Enable the `ssh-agent` service so it starts automatically

:::caution
Run this in an **elevated (Administrator) PowerShell** — right-click PowerShell → "Run as administrator". A normal shell cannot change service startup configuration.
:::

```powershell
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
```

Reference: [Microsoft Learn: Key-Based Authentication in OpenSSH for Windows](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement)

### 2. Add your private key to the agent

In a regular (non-admin) PowerShell, with the key path adjusted to your environment:

```powershell
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

Type the passphrase **just this once**.

### 3. Verify the registration

```powershell
ssh-add -l
```

If the fingerprint of your key shows up, you are good. When you connect from VS Code, running `ssh-add -l` from the local-side VS Code terminal should show the same fingerprint, which means VS Code is talking to the agent.

### 4. (Optional) Add `AddKeysToAgent yes` to `~/.ssh/config`

Keys loaded from a file are then added to the agent automatically ([OpenBSD man: ssh_config(5)](https://man.openbsd.org/ssh_config)).

```sshconfig
Host camphor
    HostName camphor.kudpc.kyoto-u.ac.jp
    User <your-username>
    IdentityFile ~/.ssh/id_ed25519
    AddKeysToAgent yes
```

## macOS / Linux

`ssh-agent` is usually already running (macOS via `launchd`, Linux via `gnome-keyring` / `keychain` / similar). Just register the key once:

```bash
ssh-add ~/.ssh/id_ed25519
ssh-add -l
```

On macOS, also adding `UseKeychain yes` to `~/.ssh/config` stores the passphrase in Keychain so it is restored automatically after reboot.

## If VS Code still keeps asking

- From the local-side VS Code terminal, run `ssh-add -l` to confirm the agent is reachable.
- If the agent is not reachable, start it and **restart VS Code**.
- The VS Code setting `remote.SSH.showLoginTerminal: true` makes it easier to see where authentication actually stalls.

## Bonus: using git over SSH on the remote

Add `ForwardAgent yes` to `~/.ssh/config` to expose your local agent to the remote host, so you can `git push` from camphor with the same key.

```sshconfig
Host camphor
    HostName camphor.kudpc.kyoto-u.ac.jp
    User <your-username>
    IdentityFile ~/.ssh/id_ed25519
    AddKeysToAgent yes
    ForwardAgent yes
```

## References

- [VS Code: Remote Development Tips and Tricks](https://code.visualstudio.com/docs/remote/troubleshooting)
- [Microsoft Learn: Key-Based Authentication in OpenSSH for Windows](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement)
- [OpenBSD man: ssh_config(5)](https://man.openbsd.org/ssh_config)
