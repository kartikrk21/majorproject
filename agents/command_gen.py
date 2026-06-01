import openai
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from session_context import get_api_key

openai.api_key = get_api_key()

def generate_command_agent(state):
    prompt = state["prompt"]
    cwd = state["cwd"]
    # Recursively list files (excluding virtual environments, git metadata, and caches)
    file_list = []
    for root, dirs, files in os.walk(cwd):
        # Prune unwanted directories
        dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__', 'heyrudra.egg-info', '.DS_Store', 'history', 'prompts']]
        for file in files:
            if not file.startswith('.') and file not in ['b', 'c', 'd']:
                rel_path = os.path.relpath(os.path.join(root, file), cwd)
                file_list.append(rel_path)

    user_prompt = f"""
You are a CLI assistant. You are currently in: {cwd}
This project contains the following files: {file_list}
 
Instruction: "{prompt}"
 
Convert this to a standard Bash/zsh command that can be run on macOS. Output ONLY the valid shell command.

Guidelines:
1. If the instruction asks to run, start, or show a long-running dashboard, web app, or server (such as `dashboard/server.py`), you MUST run it in the background, redirect its output, wait a second, and then open the URL in the browser so that the CLI returns immediately. Use this exact pattern:
   `python dashboard/server.py > /dev/null 2>&1 & sleep 1 && open http://127.0.0.1:5000`
2. Do NOT use Windows PowerShell cmdlets. Use standard macOS/Linux bash/zsh commands.
"""

    response = openai.ChatCompletion.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": user_prompt}],
        temperature=0
    )

    command = response['choices'][0]['message']['content'].strip()
    
    # Strip markdown backticks
    if command.startswith("```"):
        lines = command.split('\n')
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        command = '\n'.join(lines).strip()

    state["command"] = command
    return state
