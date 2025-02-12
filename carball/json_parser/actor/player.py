import logging
from .base import *

logger = logging.getLogger(__name__)


class PlayerHandler(BaseActorHandler):
    type_name = 'TAGame.Default__PRI_TA'

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        if 'Engine.PlayerReplicationInfo:PlayerName' not in actor:
            return

        actor_id = actor['Id']
        player_dict = {
            'name': actor["Engine.PlayerReplicationInfo:PlayerName"],
        }
        # Conditionally add ['team'] key to player_dict
        player_team = actor.get("Engine.PlayerReplicationInfo:Team", None)
        if player_team is not None and player_team != -1:
            player_dict['team'] = player_team

        if "TAGame.PRI_TA:PartyLeader" in actor:
            try:
                actor_type = \
                    list(actor["Engine.PlayerReplicationInfo:UniqueId"]['unique_id'][
                             'remote_id'].keys())[
                        0]

                # handle UniqueID for plays_station and switch
                unique_id = None
                if actor_type == "play_station" or actor_type == "psy_net":
                    actor_name = actor["Engine.PlayerReplicationInfo:PlayerName"]
                    for player_stat in self.parser.game.properties['PlayerStats']['value']["array"]:
                        if actor_name == player_stat['value']['Name']['value']['str']:
                            unique_id = str(player_stat['value']['OnlineID']['value']['q_word'])
                if unique_id is None:
                    unique_id = str(
                        actor['Engine.PlayerReplicationInfo:UniqueId']['unique_id']['remote_id'][actor_type])

                # only process if party_leader id exists
                if "party_leader" in actor["TAGame.PRI_TA:PartyLeader"] and \
                        "id" in actor["TAGame.PRI_TA:PartyLeader"]["party_leader"]:
                    leader_actor_type = list(
                        actor["TAGame.PRI_TA:PartyLeader"]["party_leader"]["id"][0].keys()
                    )[0]
                    leader = None
                    if leader_actor_type == "play_station" or leader_actor_type == "psy_net":
                        leader_name = actor[
                            "TAGame.PRI_TA:PartyLeader"
                        ]["party_leader"]["id"][0][leader_actor_type][0]

                        for player_stat in self.parser.game.properties['PlayerStats']['value']["array"]:
                            if leader_name == player_stat['value']['Name']['value']['str']:
                                leader = str(player_stat['value']['OnlineID']['value']['q_word'])

                    if leader is None:  # leader is not using play_station nor switch (ie. xbox or steam)
                        leader = str(
                            actor[
                                "TAGame.PRI_TA:PartyLeader"
                            ]["party_leader"]["id"][0][leader_actor_type]
                        )

                    if leader in self.parser.parties:
                        if unique_id not in self.parser.parties[leader]:
                            self.parser.parties[leader].append(unique_id)
                    else:
                        self.parser.parties[leader] = [unique_id]

            except KeyError:
                logger.warning('Could not get party leader for actor id: ' + str(actor_id))

        if actor_id not in self.parser.player_dicts:
            # add new player
            self.parser.player_dicts[actor_id] = player_dict

            logger.debug('Found player actor: %s (id: %s)' % (player_dict['name'], actor_id))
            self.parser.player_data[actor_id] = {}

        self.parser.player_data[actor_id][frame_number] = {}

        # update player_dicts
        for _k, _v in {**actor, **player_dict}.items():
            self.parser.player_dicts[actor_id][_k] = _v

        if delta != 0:
            self.parser.player_data[actor_id][frame_number]['ping'] = \
                actor.get("Engine.PlayerReplicationInfo:Ping", None)
            if 'TAGame.PRI_TA:CameraSettings' in actor:
                # oldstyle camera settings
                if actor_id not in self.parser.cameras_data:
                    self.parser.cameras_data[actor_id] = actor['TAGame.PRI_TA:CameraSettings']
                ball_cam = actor.get('TAGame.CameraSettingsActor_TA:bUsingSecondaryCamera', None)
                self.parser.player_data[actor_id][frame_number]['ball_cam'] = ball_cam

            if 'TAGame.PRI_TA:TimeTillItem' in actor:
                time_till_item = actor['TAGame.PRI_TA:TimeTillItem']
                self.parser.player_data[actor_id][frame_number]['time_till_power_up'] = time_till_item
