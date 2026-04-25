"""Project entry point.

Keeps the repository root as a simple launcher, similar to stem_analysis.
"""

import sys
from pathlib import Path

# Ensure imports from the project root are available.
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from scripts.main import main


if __name__ == "__main__":
    main()