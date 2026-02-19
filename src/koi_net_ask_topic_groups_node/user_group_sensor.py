from dataclasses import dataclass
from logging import Logger
from rid_lib.ext import Bundle
from slack_bolt import App
from koi_net.components import KobjQueue

from .rid_types import SlackUserGroup


@dataclass
class UserGroupSensor:
    log: Logger
    slack_app: App
    kobj_queue: KobjQueue
    
    def __post_init__(self):
        self.register_handlers()

    def register_handlers(self):
        self.slack_app.event("subteam_updated")(self.handle_usergroup_update)
    
    def handle_usergroup_update(self, event: dict):
        usergroup = event["subteam"]
        ug_rid = SlackUserGroup(usergroup["team_id"], usergroup["id"])
        self.log.info(f"Detected update for {ug_rid}")
        
        self.kobj_queue.push(bundle=Bundle.generate(
            rid=ug_rid,
            contents=usergroup
        ))
        
    def backfill_usergroups(self):
        resp = self.slack_app.client.usergroups_list()
        usergroups = resp.data["usergroups"]
        
        for usergroup in usergroups:
            ug_rid = SlackUserGroup(usergroup["team_id"], usergroup["id"])
            self.log.info(f"Processing {ug_rid}")
            
            resp = self.slack_app.client.usergroups_users_list(usergroup=usergroup["id"])
            usergroup["users"] = resp.data["users"]
            
            self.kobj_queue.push(bundle=Bundle.generate(
                rid=ug_rid,
                contents=usergroup
            ))
    
    def start(self):
        self.backfill_usergroups()