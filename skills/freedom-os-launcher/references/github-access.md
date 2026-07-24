# GitHub access

Use this when the team repository cannot be cloned or pulled.

## Detect

```bash
git --version
gh --version 2>/dev/null || echo "gh not installed"
gh auth status 2>/dev/null || true
ssh -T git@github.com 2>&1 || true
git config --global user.name || true
git config --global user.email || true
```

## Preferred: gh CLI

If `gh` exists:

```bash
gh auth login
gh auth setup-git
gh auth status
```

## SSH fallback

Check keys:

```bash
ls -la ~/.ssh/id_*.pub 2>/dev/null || echo "No SSH public keys found"
```

Generate a key only after user confirmation:

```bash
ssh-keygen -t ed25519 -C "USER_EMAIL" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub
```

Ask the user to add the public key at:

```text
https://github.com/settings/keys
```

Verify:

```bash
ssh -T git@github.com
```

## Git identity

If name/email are missing, ask the user first, then set:

```bash
git config --global user.name "USER_NAME"
git config --global user.email "USER_EMAIL"
```

Never ask the user to paste a private key or token into chat.
