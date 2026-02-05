from dataclasses import dataclass
from logging import Logger
from koi_net.processor.kobj_queue import KobjQueue
from rid_lib.ext import Bundle, Cache
from slack_bolt import App

from .models import TopicGroupModel

from .rid_types import AskTopicGroup, SlackUserGroup


lookup = {
    "🏛️": "classical_building"
}

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
    
    def start(self):
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
            continue
        
            
            
            tg_emoji = None
            for emoji in lookup:
                if emoji in ug_name:
                    tg_emoji = emoji
                    print(ug_name, "->", lookup[emoji])
                    break
                
            if not tg_emoji:
                continue
            
            topic_group_rid = AskTopicGroup(ug_team_id, ug_id)
            bundle = self.cache.read(topic_group_rid)
            
            if bundle:
                topic_group = bundle.validate_contents(TopicGroupModel)
                
                
            else:
                
                topic_group = TopicGroupModel(
                    handle=ug_handle,
                    name=ug_name,
                    emoji=tg_emoji,
                    users=ug_users
                )