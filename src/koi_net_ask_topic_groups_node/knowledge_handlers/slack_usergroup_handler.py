from dataclasses import dataclass

from koi_net.components import Cache, KobjQueue
from koi_net.components.interfaces import KnowledgeHandler, HandlerType
from koi_net.protocol.knowledge_object import KnowledgeObject
from rid_lib.ext import Bundle
from rid_lib.types import SlackUser, SlackUserGroup
from slack_bolt import App

from ..models import TopicGroupModel
from ..rid_types import AskTopicGroup


@dataclass
class SlackUserGroupHandler(KnowledgeHandler):
    slack_app: App
    cache: Cache
    kobj_queue: KobjQueue
    
    handler_type = HandlerType.Network
    rid_types = (SlackUserGroup,)
    
    def handle(self, kobj: KnowledgeObject):
        ug_rid: SlackUserGroup = kobj.rid
        ug_handle: str = kobj.contents["handle"]
        ug_name: str = kobj.contents["name"]
        ug_users: list[str] = kobj.contents["users"]
        
        if not ug_handle.startswith("tg-"):
            return
        
        tg_rid = AskTopicGroup(ug_rid.team_id, ug_rid.subteam_id)
        
        lookup = {
            "🏛️": "classical_building"
        }
        
        emoji_str = None
        for emoji in lookup:
            if emoji in ug_name:
                emoji_str = lookup[emoji]
                break
            
        user_rids = [SlackUser(ug_rid.team_id, user_id) for user_id in ug_users]
        
        bundle = self.cache.read(tg_rid)
        if bundle:
            topic_group = bundle.validate_contents(TopicGroupModel)
        else:
            topic_group = TopicGroupModel.model_construct()
        
        topic_group.usergroup = ug_rid
        topic_group.handle = ug_handle
        topic_group.name = ug_name
        topic_group.emoji = emoji_str
        topic_group.users = user_rids
        
        tg_bundle = Bundle.generate(
            rid=tg_rid,
            contents=topic_group.model_dump()
        )
        self.kobj_queue.push(bundle=tg_bundle)
    
    