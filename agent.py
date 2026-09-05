"""Back-compat CLI entry at repo root."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from agent.__main__ import main

if __name__ == "__main__":
    main()
