# Aegis Discord Bot

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Discord.py](https://img.shields.io/badge/discord-py-blue.svg)](https://github.com/Rapptz/discord.py)
[![Chutes.ai](https://img.shields.io/badge/Powered%20by-Chutes.ai-00C7B7)](https://chutes.ai)

> Drop-in Discord automod replacement that actually understands context. Detects toxicity, subtle hate speech, and spam in real-time using Qwen3Guard.

[Why not just use Discord AutoMod?](#why-not-discord-automod) • [Installation](#installation) • [Commands](#commands)

---
**Latency:** ~800ms per message (including network roundtrip to Chutes.ai)

---

## Features

- **Zero-config toxicity detection** –> Just add the bot, no regex rules to maintain
- **Context-aware** –> Understands nuance, not just word lists  
- **Self-hosted** –> Your messages never touch our servers (only Chutes.ai API)
- **Lightweight** –> Single Python file, no database required, ~50MB RAM usage (you may upgrade to Sqlite)
- **Smart reactions** –> Deletes unsafe content, silently logs controversial stuff
- **Owner-only commands** –> No permission hell, only you control the toggle

---

## Installation

### Prerequisites

- Python 3.9+
- A Discord bot token ([get one here](https://discord.com/developers/applications))
- Chutes.ai API key ([get one here](https://chutes.ai))

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/aegis-discord.git
cd aegis-discord
pip install -r requirements.txt
