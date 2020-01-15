try:
    # from carball.decompile_replays import decompile_replay
    # from carball.decompile_replays import analyze_replay_file
    pass
except ModuleNotFoundError as e:
    print("Not importing functions due to missing packages:", e)

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "generated"))
