from koi_net.processor.handler import HandlerType, KnowledgeHandler
from koi_net.processor.knowledge_object import KnowledgeObject
from rid_lib.types import SlackMessage

from .handler_context import ExtendedHandlerContext
from .models import AskMetagovThread


@KnowledgeHandler.create(
    handler_type=HandlerType.Network,
    rid_types=[AskMetagovThread])
def handle_ask_metagov_thread(ctx: ExtendedHandlerContext, kobj: KnowledgeObject):
    thread: AskMetagovThread = kobj.rid
    result = ctx.slack_app.client.chat_postMessage(
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
    print(slack_msg)