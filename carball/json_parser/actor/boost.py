import re
from typing import Optional

from .base import *

REPLICATED_PICKUP_KEY = 'TAGame.VehiclePickup_TA:ReplicatedPickupData'
REPLICATED_PICKUP_KEY_168 = 'TAGame.VehiclePickup_TA:NewReplicatedPickupData'


def get_boost_actor_data(actor: dict) -> Optional[dict]:
    if REPLICATED_PICKUP_KEY in actor:
        replicated_pickup_data_actor = actor[REPLICATED_PICKUP_KEY]
        pickup_actor = replicated_pickup_data_actor['pickup']
    elif REPLICATED_PICKUP_KEY_168 in actor:
        replicated_pickup_data_actor = actor[REPLICATED_PICKUP_KEY_168]
        pickup_actor = replicated_pickup_data_actor['pickup_new']
    else:
        return

    if 'instigator_id' in pickup_actor and pickup_actor['instigator_id'] != -1:
        return pickup_actor


class BoostHandler(BaseActorHandler):
    type_name = 'Archetypes.CarComponents.CarComponent_Boost'

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        car_actor_id = actor.get('TAGame.CarComponent_TA:Vehicle', None)

        if car_actor_id is None or car_actor_id not in self.parser.current_car_ids_to_collect:
            return

        player_actor_id = self.parser.car_player_ids[car_actor_id]
        boost_is_active_random_int = actor.get(
            COMPONENT_ACTIVE_KEY,
            actor.get(COMPONENT_REPLICATED_ACTIVE_KEY, False))
        # boost_is_active when random_int is odd?!
        boost_is_active = (boost_is_active_random_int % 2 == 1)
        boost_amount = actor.get('TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount', None)

        actor_frame = self.parser.player_data[player_actor_id][frame_number]
        actor_frame['boost_temp'] = boost_amount / 255 * 100 if boost_amount is not None else None
        actor_frame['boost_active'] = boost_is_active


class BoostPickupHandler(BaseActorHandler):
    @classmethod
    def can_handle(cls, actor: dict) -> bool:
        return actor['ClassName'] == 'TAGame.VehiclePickup_Boost_TA'

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        pickup_actor = get_boost_actor_data(actor)

        if pickup_actor is not None:
            car_actor_id = pickup_actor['instigator_id']
            if car_actor_id in self.parser.car_player_ids:
                player_actor_id = self.parser.car_player_ids[car_actor_id]
                if frame_number in self.parser.player_data[player_actor_id]:
                    type_name = actor['TypeName']
                    match = re.match(r".*VehiclePickup_Boost_TA_(\d*)$", type_name)
                    boost_id = int(match.group(1))
                    self.parser.player_data[player_actor_id][frame_number]['potential_boost_collect'] = boost_id
                    # TODO: Investigate and fix random imaginary boost collects
                # set to false after acknowledging it's turned True
                # it does not turn back false immediately although boost is only collected once.
                # using actor_id!=-1
                pickup_actor["instigator_id"] = -1

