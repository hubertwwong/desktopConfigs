# 🤠 Herdr - Terminal Runtime for AI Coding Agents

[Herdr](https://herdr.dev) is an open-source terminal runtime and multiplexer built specifically for running, managing, and coordinating autonomous AI coding agents (such as Antigravity, Claude Code, Cursor, OpenCode, and Grok).

---

## 🌟 Why Herdr?

Unlike traditional terminal multiplexers (tmux, screen) that treat terminals as basic shell windows, Herdr is agent-native:

1. **Persistent Sessions**: Agent terminals run inside a background server daemon (`herdr-core`). You can disconnect, close your laptop, or detach without losing the running task.
2. **Status Awareness**: Tracks each terminal pane as `working`, `blocked` (waiting for human input), or `idle`.
3. **Agent Orchestration**: Agents can drive Herdr programmatically via CLI or local socket APIs to split panes, prompt peer agents, and monitor workflows.
4. **Multi-Machine Management**: Seamlessly manages local terminals and remote SSH sessions in a single cohesive workspace.

---

## 🚀 Installation & Usage

### Method A: Via `./setup.sh`
```bash
cd ~/projects/desktopConfigs
./setup.sh herdr
```

### Method B: Via Standalone Installer Script
```bash
./scripts/setup-herdr.sh
```

### Method C: One-Liner (Remote Machine)
```bash
curl -fsSL https://herdr.dev/install.sh | sh
```

---

## 💻 Basic CLI Commands

```bash
# Launch Herdr terminal interface
herdr

# Check installed version
herdr --version

# Spawn a session with a designated coding agent
herdr new -- "agy"
```
