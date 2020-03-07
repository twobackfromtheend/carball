from .base import *
from carball.json_parser.actor_parsing import BallActor


class BallHandler(BaseActorHandler):

    @classmethod
    def can_handle(cls, actor: dict) -> bool:
        return actor['TypeName'].startswith('Archetypes.Ball.')

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        if actor.get('TAGame.RBActor_TA:bIgnoreSyncing', False):
            return
        ball_data = BallActor.get_data_dict(actor, self.parser.replay_version)
        self.parser.ball_data[frame_number] = ball_data

