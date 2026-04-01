import sys
from pathlib import Path
from time import sleep

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from busclock.LED_management.test import main

if __name__ == "__main__":
    main()