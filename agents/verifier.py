import re
import os

def verifier_agent(state):
    command = state.get("command", "")
    cwd = state.get("cwd", os.getcwd())

    if not command:
        state["verification_error"] = "No command to verify"
        return state

    safety_result = _check_command_safety(command, cwd)
    state["verification_result"] = safety_result
    state["safety_score"] = safety_result["score"]
    state["safety_warnings"] = safety_result["warnings"]

    # HARD BLOCK — no question, just stop
    if safety_result["blocked"]:
        state["verification_error"] = f"Command blocked: {safety_result['reason']}"
        state["status"] = "cancelled"
        state["command"] = ""
        print(f"\n🚫 BLOCKED: {safety_result['reason']}")
        print("   This command cannot be executed.")
        return state

    syntax_check = _check_syntax(command)
    if not syntax_check["valid"]:
        state["verification_error"] = f"Syntax error: {syntax_check['error']}"
        state["status"] = "syntax_error"
        print(f"❌ Syntax error: {syntax_check['error']}")
        return state

    # ASK — semi-dangerous
    if safety_result["score"] < 70:
        print(f"⚠️  Safety warnings: {', '.join(safety_result['warnings'])}")
        if not _confirm_risky_command(command, safety_result["warnings"]):
            state["verification_error"] = "Command execution cancelled by user"
            state["status"] = "cancelled"
            state["command"] = ""
            print("🛑 Command cancelled.")
            return state

    state["verification_passed"] = True
    state["status"] = "verified"
    print(f"✅ Command verified (safety score: {safety_result['score']}/100)")
    return state


def _check_command_safety(command, cwd):
    score = 100
    warnings = []
    cmd = command.strip()
    cmd_lower = cmd.lower()

    # ── HARD BLOCK (no confirmation ever) ──────────────────────────────────
    hard_block = [
        (r'\brm\s+-rf\s+/',           "Deleting root filesystem"),
        (r'\brm\s+-rf\s+~',           "Deleting home directory"),
        (r'\brm\s+-rf\s+\$HOME',      "Deleting home directory"),
        (r'\brm\s+-rf\s+/home',       "Deleting /home"),
        (r'\brm\s+-rf\s+/etc',        "Deleting /etc"),
        (r'\brm\s+-rf\s+/usr',        "Deleting /usr"),
        (r'\brm\s+-rf\s+/bin',        "Deleting /bin"),
        (r'\brm\s+-rf\s+/boot',       "Deleting /boot"),
        (r'\bsudo\s+rm\s+-rf\b',      "Root-level recursive deletion"),
        (r'\bmkfs\b',                  "Formatting filesystem"),
        (r'\bfdisk\b.*\b/dev/',        "Modifying disk partitions"),
        (r'\bdd\s+if=/dev/zero',       "Overwriting disk"),
        (r'\bformat\s+c:',             "Formatting system drive"),
        (r'\bshutdown\b',              "System shutdown"),
        (r'\breboot\b',                "System reboot"),
        (r'\bhalt\b',                  "System halt"),
        (r'\bpoweroff\b',              "System poweroff"),
        (r'\bcurl\b.*\|\s*sh',         "Downloading and executing remote script"),
        (r'\bwget\b.*\|\s*sh',         "Downloading and executing remote script"),
    ]

    for pattern, reason in hard_block:
        if re.search(pattern, cmd, re.IGNORECASE):
            return {"score": 0, "warnings": [reason], "reason": reason, "blocked": True}

    # ── SEMI-DANGEROUS (ask confirmation) ──────────────────────────────────
    risky = [
        (r'\brm\s+-rf\b',   "Recursive deletion",          30),
        (r'\brm\s+-r\b',    "Recursive deletion",          30),
        (r'\bkillall\b',    "Killing all processes",       35),
        (r'\bchmod\s+777',  "Overly permissive chmod",     40),
        (r'\bsudo\b',       "Running as root",             20),
        (r'\brm\b',         "File deletion",               10),
        (r'\bchmod\b',      "Changing permissions",        10),
        (r'\bchown\b',      "Changing ownership",          10),
    ]

    for pattern, description, penalty in risky:
        if re.search(pattern, cmd_lower):
            score -= penalty
            warnings.append(description)

    return {"score": max(1, score), "warnings": warnings, "reason": warnings[0] if warnings else "", "blocked": False}


def _check_syntax(command):
    try:
        if command.count("'") % 2 != 0:
            return {"valid": False, "error": "Unmatched single quote"}
        if command.count('"') % 2 != 0:
            return {"valid": False, "error": "Unmatched double quote"}
        paren = 0
        for ch in command:
            if ch == '(': paren += 1
            elif ch == ')':
                paren -= 1
                if paren < 0:
                    return {"valid": False, "error": "Unmatched closing parenthesis"}
        if paren != 0:
            return {"valid": False, "error": "Unmatched opening parenthesis"}
        return {"valid": True, "error": None}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def _confirm_risky_command(command, warnings):
    print(f"\n⚠️  RISKY COMMAND DETECTED:")
    print(f"   Command : {command}")
    print(f"   Warnings: {', '.join(warnings)}")
    try:
        response = input("\n   Proceed? (yes/no): ").strip().lower()
        return response in ['yes', 'y']
    except (EOFError, KeyboardInterrupt):
        return False
