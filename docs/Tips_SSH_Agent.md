Lang: [日本語](Tips_SSH_Agent.md) | [English](Tips_SSH_Agent_en.md)

# VS Code Remote-SSH のパスフレーズ入力を自動化する (`ssh-agent`)

VS Code Remote-SSH で camphor などへ接続するたびにパスフレーズを聞かれて煩わしい場合、`ssh-agent` に秘密鍵を 1 度だけ登録しておけば以後の入力をほぼ省略できます。VS Code 公式も「パスフレーズ付き鍵を使う場合はローカルで SSH Agent を動かす」ことを推奨しています ([VS Code 公式 Tips & Tricks](https://code.visualstudio.com/docs/remote/troubleshooting))。

## Windows での標準手順

### 1. `ssh-agent` サービスを自動起動にする

> **管理者権限の PowerShell** で実行してください（PowerShell を右クリック →「管理者として実行」）。サービスの起動設定を変更するため、通常権限では失敗します。

```powershell
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
```

参考: [Microsoft Learn: Key-Based Authentication in OpenSSH for Windows](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement)

### 2. 秘密鍵を agent に登録する

通常の PowerShell で（鍵ファイル名は環境に合わせて）:

```powershell
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

ここで **1 回だけ** パスフレーズを入力します。

### 3. 登録を確認する

```powershell
ssh-add -l
```

登録済みの鍵フィンガープリントが表示されれば OK。VS Code から接続したときも、ローカル側のターミナルで `ssh-add -l` が見えていれば agent 経由で認証されます。

### 4. （任意）`~/.ssh/config` に `AddKeysToAgent yes` を入れておく

鍵をファイルから読み込んだ際に自動で agent へ追加されます ([OpenBSD man: ssh_config(5)](https://man.openbsd.org/ssh_config))。

```sshconfig
Host camphor
    HostName camphor.kudpc.kyoto-u.ac.jp
    User <your-username>
    IdentityFile ~/.ssh/id_ed25519
    AddKeysToAgent yes
```

## macOS / Linux

`ssh-agent` は標準で動いている (macOS は `launchd` 管理、Linux は `gnome-keyring` / `keychain` 等) ことが多いです。鍵を 1 度だけ追加します:

```bash
ssh-add ~/.ssh/id_ed25519
ssh-add -l
```

macOS では `~/.ssh/config` に `UseKeychain yes` も書いておくとパスフレーズが Keychain に保存され、再起動後も自動で復元されます。

## それでも VS Code から毎回聞かれる場合

- ローカル側の VS Code 内ターミナルで `ssh-add -l` を実行して agent が見えているか確認する
- `agent` が動いていなければ起動後に **VS Code を再起動**する
- VS Code 設定 `remote.SSH.showLoginTerminal: true` を入れると、認証ステップがどこで止まっているか切り分けやすくなる

## おまけ: リモート側で git over SSH を使いたい

`~/.ssh/config` に `ForwardAgent yes` を加えると、ローカルの agent がリモートからも見えるようになり、camphor 側で `git push` 等ができるようになります。

```sshconfig
Host camphor
    HostName camphor.kudpc.kyoto-u.ac.jp
    User <your-username>
    IdentityFile ~/.ssh/id_ed25519
    AddKeysToAgent yes
    ForwardAgent yes
```

## 参考

- [VS Code: Remote Development Tips and Tricks](https://code.visualstudio.com/docs/remote/troubleshooting)
- [Microsoft Learn: Key-Based Authentication in OpenSSH for Windows](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement)
- [OpenBSD man: ssh_config(5)](https://man.openbsd.org/ssh_config)
