from dataclasses import dataclass

from koi_net.components import KobjQueue
from koi_net.components.interfaces import KnowledgeHandler, HandlerType
from koi_net.protocol.knowledge_object import KnowledgeObject
from rid_lib.ext import Bundle
from rid_lib.types import SlackMessage
from slack_bolt import App

from ..models import ThreadLinkModel
from ..rid_types import AskCoreThread, ThreadLink


@dataclass
class AskThreadHandler(KnowledgeHandler):
    slack_app: App
    kobj_queue: KobjQueue
    
    handler_type = HandlerType.Network
    rid_types = (AskCoreThread,)
    
    def ensure_bot_in_channel(self, channel_id: str):
        try:
            result = self.slack_app.client.conversations_info(channel=channel_id)
            channel = result["channel"]
            
            if not channel.get("is_member", False):
                self.slack_app.client.conversations_join(channel=channel_id)
                self.log.info(f"Joined channel #{channel_id}")
        
        except Exception as e:
            self.log.error(f"Unhandled exception joining channel: {e}")
    
    def handle(self, kobj: KnowledgeObject):
        thread: AskCoreThread = kobj.rid
        
        self.ensure_bot_in_channel(channel_id=thread.channel_id)
        
        result = self.slack_app.client.chat_postMessage(
            channel=thread.channel_id,
            thread_ts=thread.ts,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "React to this message to tag a topic group!"
                    }
                }
            ]
        )
        slack_msg = SlackMessage(
            team_id=thread.team_id,
            channel_id=thread.channel_id,
            ts=result["ts"]
        )
        
        thread_link = ThreadLinkModel(thread=thread, message=slack_msg)
        self.kobj_queue.push(bundle=Bundle.generate(
            rid=ThreadLink(slack_msg.team_id, slack_msg.channel_id, slack_msg.ts),
            contents=thread_link.model_dump()
        ))
        
    
    