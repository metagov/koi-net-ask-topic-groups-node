from dataclasses import dataclass
from logging import Logger

from rid_lib.ext import Bundle
from slack_bolt import App
from slack_sdk import WebClient
from koi_net.components import Cache, KobjQueue

from .config import AskTopicGroupsConfig
from .models import ThreadLinkModel, TopicGroupModel
from .rid_types import AskTopicGroup, ThreadLink


@dataclass
class SlackEventHandler:
    log: Logger
    slack_app: App
    slack_admin_client: WebClient
    kobj_queue: KobjQueue
    config: AskTopicGroupsConfig
    cache: Cache

    def __post_init__(self):
        self.register_handlers()
        
    def register_handlers(self):
        self.slack_app.event("reaction_added")(self.handle_reaction_added)
        self.slack_app.event("reaction_removed")(self.handle_reaction_removed)
        
    def handle_reaction_added(self, event: dict):
        self.log.info(f"reactions added: {event}")
        
        item = event["item"]
        if item["type"] != "message":
            return
        
        # reaction emoji -> user group -> thread link -> thread -> topic group model
        
        found_match = False
        for topic_group_rid in self.cache.list_rids(rid_types=[AskTopicGroup]):
            bundle = self.cache.read(topic_group_rid)
            if not bundle:
                continue
            
            topic_group = bundle.validate_contents(TopicGroupModel)
            
            if topic_group.emoji == event["reaction"]:
                found_match = True
                break
        
        if not found_match:
            return
        
        self.log.info(f"Matched reaction to {topic_group_rid}")
        
        thread_link_rid = ThreadLink(
            team_id=self.config.slack.team_id,
            channel_id=item["channel"],
            ts=item["ts"]
        )
        
        bundle = self.cache.read(thread_link_rid)
        if not bundle:
            return
        
        thread_link = bundle.validate_contents(ThreadLinkModel)
        
        topic_group.threads.append(thread_link.thread)
        
        self.log.info(f"Appending thread {thread_link.thread}")
        
        self.kobj_queue.push(bundle=Bundle.generate(
            rid=topic_group_rid,
            contents=topic_group.model_dump()
        ))
        
        self.slack_app.client.chat_postMessage(
            channel=thread_link.thread.channel_id,
            thread_ts=thread_link.thread.ts,
            text=f"Inviting {topic_group.usergroup.mention} to participate!"
        )
        
    def handle_reaction_removed(self, event: dict):
        self.log.info(f"reactions removed: {event}")
