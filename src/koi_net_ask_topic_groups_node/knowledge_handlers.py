from koi_net.processor.handler import HandlerType, KnowledgeHandler
from koi_net.processor.knowledge_object import KnowledgeObject
from rid_lib.ext import Bundle
from rid_lib.types import SlackMessage, SlackUser

from .models import ThreadLinkModel, TopicGroupModel

from .handler_context import ExtendedHandlerContext
from .rid_types import AskCoreThread, AskTopicGroup, SlackUserGroup, ThreadLink


@KnowledgeHandler.create(
    handler_type=HandlerType.Network,
    rid_types=[AskCoreThread])
def handle_ask_metagov_thread(ctx: ExtendedHandlerContext, kobj: KnowledgeObject):
    thread: AskCoreThread = kobj.rid
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
    
    thread_link = ThreadLinkModel(thread, slack_msg)
    ctx.kobj_queue.push(bundle=Bundle.generate(
        rid=ThreadLink(slack_msg.team_id, slack_msg.channel_id, slack_msg.ts),
        contents=thread_link.model_dump()
    ))
    
@KnowledgeHandler.create(HandlerType.Network, rid_types=[SlackUserGroup])
def handle_slack_usergroup(ctx: ExtendedHandlerContext, kobj: KnowledgeObject):
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
    
    bundle = ctx.cache.read(tg_rid)
    if bundle:
        topic_group = bundle.validate_contents(TopicGroupModel)
    else:
        topic_group = TopicGroupModel.model_construct()
        
    topic_group.handle = ug_handle
    topic_group.name = ug_name
    topic_group.emoji = emoji_str
    topic_group.users = user_rids
    
    tg_bundle = Bundle.generate(
        rid=tg_rid,
        contents=topic_group.model_dump()
    )
    ctx.kobj_queue.push(bundle=tg_bundle)