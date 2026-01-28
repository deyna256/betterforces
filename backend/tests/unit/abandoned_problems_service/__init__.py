import sys
import os

# Get the path to the project root (betterforces)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up 4 levels: abandoned_problems_service -> unit -> tests -> backend -> betterforces
project_root = os.path.abspath(os.path.join(current_dir, "../../../.."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)
