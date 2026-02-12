from dataclasses import dataclass
from logging import Logger
import re
from koi_net.cache import Cache
from rid_lib.ext import Bundle
from rid_lib.types import SlackUser
from slack_bolt import App, Respond
from slack_sdk import WebClient
from koi_net.processor.kobj_queue import KobjQueue

from .config import AskTopicGroupsConfig

from .models import ThreadLinkModel, TopicGroupModel

from .rid_types import AskTopicGroup, SlackUserGroup, ThreadLink


@dataclass
class SlackHandlers:
    log: Logger
    slack_app: App
    slack_admin_client: WebClient
    kobj_queue: KobjQueue
    config: AskTopicGroupsConfig
    cache: Cache

    def __post_init__(self):
        self.register_handlers()
        
    def register_handlers(self):
        self.slack_app.command("/join-topic")(self.topic_group_join)
        self.slack_app.command("/leave-topic")(self.topic_group_leave)
        self.slack_app.event("subteam_members_changed")(self.handle_user_group_update)
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
    
    def handle_user_group_update(self, event: dict):
        self.log.info("Handling user group update...")
        
        added_users: list[str] = event.get("added_users", [])
        removed_users: list[str] = event.get("removed_users", [])
        ug_id = event["subteam_id"]
        team_id = event["team_id"]
        
        topic_group_rid = AskTopicGroup(team_id=team_id, subteam_id=ug_id)
        
        bundle = self.cache.read(topic_group_rid)
        
        if bundle:
            topic_group = bundle.validate_contents(TopicGroupModel)
            
            for removed_user in removed_users:
                user_rid = SlackUser(team_id, removed_user)
                if user_rid not in topic_group.users:
                    continue
                topic_group.users.remove(user_rid)
            
            for added_user in added_users:
                user_rid = SlackUser(team_id, added_user)
                if user_rid not in topic_group.users:
                    topic_group.users.append(user_rid)
            
            self.log.info(f"Updated topic group: {topic_group}")
            
            updated_bundle = Bundle.generate(
                rid=topic_group_rid,
                contents=topic_group.model_dump()
            )
        else:
            usergroup = self.slack_app.client.usergroups_users_list(usergroup=ug_id)
            topic_group = TopicGroupModel(
                users=[SlackUser(team_id, user_id) for user_id in usergroup["users"]])
            
            self.log.info(f"New topic group: {topic_group}")
            
            updated_bundle = Bundle.generate(
                rid=topic_group_rid,
                contents=topic_group.model_dump()
            )
            
        self.kobj_queue.push(bundle=updated_bundle)
    
    def get_user_group(self, ug_id: str):
        resp = self.slack_app.client.usergroups_list()
        usergroups = resp["usergroups"]
        
        for usergroup in usergroups:
            if usergroup["id"] == ug_id:
                return usergroup
    
    def topic_group_join(self, ack, respond: Respond, command):
        ack()

        user_id = command["user_id"]
        text = command['text']
        
        capture_pattern = re.compile(r'<!subteam\^(S[A-Z0-9]+)\|@[^>]+>')
        ug_id = capture_pattern.findall(text)[0]
        
        usergroup = self.get_user_group(ug_id)
        ug_name: str = usergroup["name"]
        ug_handle: str = usergroup["handle"]
        
        if ug_handle.startswith("tg-"):
            ug_users: list[str] = self.slack_app.client.usergroups_users_list(usergroup=ug_id)['users']
            
            if user_id not in ug_users:
                ug_users.append(user_id)
                self.slack_admin_client.usergroups_users_update(usergroup=ug_id, users=ug_users)
                respond(f"Joined {ug_name}!")
                
            else:
                respond(f"You are already a member of {ug_name}")
        else:
            respond(f"{ug_handle} is not a topic group")
            
    def topic_group_leave(self, ack, respond: Respond, command):
        ack()

        user_id = command["user_id"]
        text = command['text']
        
        capture_pattern = re.compile(r'<!subteam\^(S[A-Z0-9]+)\|@[^>]+>')
        ug_id = capture_pattern.findall(text)[0]
        
        usergroup = self.get_user_group(ug_id)
        ug_name: str = usergroup["name"]
        ug_handle: str = usergroup["handle"]
        
        if ug_handle.startswith("tg-"):
            ug_users: list[str] = self.slack_app.client.usergroups_users_list(usergroup=ug_id)['users']
            
            if user_id in ug_users:
                ug_users.remove(user_id)
                
                if len(ug_users) > 0:
                    self.slack_admin_client.usergroups_users_update(usergroup=ug_id, users=ug_users or "")
                    respond(f"Left {ug_name}")
                else:
                    respond("Cannot leave group, you are the only user!")
            else:
                respond(f"You are not a member of {ug_name}")
        else:
            respond(f"{ug_handle} is not a valid topic group")
    
    