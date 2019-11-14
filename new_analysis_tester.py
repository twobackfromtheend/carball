import logging
from pathlib import Path

from carball.analysis2.replay_analysis import analyse_replay

logging.getLogger("carball.json_parser").setLevel(logging.ERROR)

# replays_folder_path = Path(r"D:\Replays\Replays\RLCS Season 7")
replays_folder_path = Path(r"C:\Users\harry\Documents\rocket_league\carball\test_replays")

replays = replays_folder_path.glob("**/*.replay")

# a = True

for replay in replays:
    # if "EB9FA3DB4114AA5E0260DB837A85699B" not in str(replay) and a:
    #     continue
    # if "M4 Ghost v G2" not in str(replay) and a:
    #     continue
    # else: a = False
    print("\n")
    print(replay)
    analyse_replay(str(replay))
