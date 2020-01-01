from .base import *


class GameEventHandler(BaseActorHandler):

    @classmethod
    def can_handle(cls, actor: dict) -> bool:
        return actor['ClassName'].startswith('TAGame.GameEvent_Soccar_TA') \
               or actor['ClassName'].startswith('TAGame.GameEvent_SoccarPrivate_TA')  # Needed for RLCS S1
        # May need more ClassNames here, such as TAGame.GameEvent_SoccarSplitscreen_TA
        # See GameEvents here:
        # https://github.com/jjbott/RocketLeagueReplayParser/blob/34b2c72fddd24d21c2aa8c5a2e1ac9f85942306c/RocketLeagueReplayParser/NetworkStream/ActorState.cs#L88

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        self.parser.soccar_game_event_actor = actor
        frame_data = {
            'time': time,
            'delta': delta,
            'seconds_remaining': actor.get('TAGame.GameEvent_Soccar_TA:SecondsRemaining', None),
            'replicated_seconds_remaining': actor.get('TAGame.GameEvent_TA:ReplicatedGameStateTimeRemaining', None),
            'is_overtime': actor.get('TAGame.GameEvent_Soccar_TA:bOverTime', None),
            'ball_has_been_hit': actor.get('TAGame.GameEvent_Soccar_TA:bBallHasBeenHit', None)
        }
        self.parser.frames_data[frame_number] = frame_data
