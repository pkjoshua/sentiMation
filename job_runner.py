import argparse
import subprocess
import os
from pathlib import Path
import notifier


parser = argparse.ArgumentParser(description="Run a generator job")
parser.add_argument("generator", help="Generator directory name")
parser.add_argument("--notify", action="store_true", help="Send pushover notification when done")
args = parser.parse_args()

call_script = Path(__file__).parent / "generators" / args.generator / "call.py"
if not call_script.is_file():
    raise SystemExit(f"Generator {args.generator} not found")

print(f"Running generator {args.generator}...")
env = dict(os.environ)
if args.notify:
    env["NOTIFY_AFTER"] = "1"
result = subprocess.run(["python3", str(call_script)], env=env)

if result.returncode != 0:
    print(f"Generator {args.generator} exited with code {result.returncode}")
else:
    if args.notify:
        notifier.send_pushover_notification(f"Job {args.generator} completed")
