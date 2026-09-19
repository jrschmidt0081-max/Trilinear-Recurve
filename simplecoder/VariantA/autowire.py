# autowire.py
import json, os

vscode_dir = os.path.join(os.getcwd(), ".vscode")
os.makedirs(vscode_dir, exist_ok=True)

tasks = {
    "version": "2.0.0",
    "tasks": [
        {
            "label": "run-simplecoder",
            "type": "shell",
            "command": "python",
            "args": ["simplecoder.py", "${selectedText}"],
            "presentation": {"reveal": "always"}
        }
    ]
}

keybindings = [
    {
        "key": "ctrl+alt+p",
        "command": "workbench.action.tasks.runTask",
        "args": "run-simplecoder"
    }
]

with open(os.path.join(vscode_dir, "tasks.json"), "w") as f:
    json.dump(tasks, f, indent=2)
with open(os.path.join(vscode_dir, "keybindings.json"), "w") as f:
    json.dump(keybindings, f, indent=2)

print("VS Code wiring complete.")
