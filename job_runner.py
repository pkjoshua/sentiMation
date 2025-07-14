import argparse
import subprocess
import os
from pathlib import Path
import notifier
import sys

# Add the webapp directory to the path so we can import config
sys.path.append(str(Path(__file__).parent / "webapp"))
from config import SD_ENV_VARS


parser = argparse.ArgumentParser(description="Run a generator job")
parser.add_argument("generator", help="Generator directory name")
parser.add_argument("--notify", action="store_true", help="Send pushover notification when done")
args = parser.parse_args()

call_script = Path(__file__).parent / "generators" / args.generator / "call.py"
if not call_script.is_file():
    raise SystemExit(f"Generator {args.generator} not found")

print(f"Running generator {args.generator}...")
env = dict(os.environ)

# Add SD API configuration to environment
env.update(SD_ENV_VARS)

if args.notify:
    env["NOTIFY_AFTER"] = "1"

# Change to the generator directory before running the script
generator_dir = Path(__file__).parent / "generators" / args.generator
os.chdir(generator_dir)
print(f"Changed working directory to: {os.getcwd()}")
print(f"SD API URL: {env.get('SD_TXT2IMG_URL')}")

result = subprocess.run(["python3", str(call_script)], env=env, cwd=generator_dir)

if result.returncode != 0:
    print(f"Generator {args.generator} exited with code {result.returncode}")
else:
    if args.notify:
        notifier.send_pushover_notification(f"Job {args.generator} completed")
