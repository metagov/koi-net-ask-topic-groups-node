import re
from dataclasses import dataclass
from logging import Logger

from slack_bolt import App, Respond
from slack_sdk import WebClient

from .config import AskTopicGroupsConfig


@dataclass
class SlackCommandHandler:
    log: Logger
    slack_app: App
    slack_admin_client: WebClient
    config: AskTopicGroupsConfig

    def __post_init__(self):
        self.register_handlers()
        
    def register_handlers(self):
        self.slack_app.command("/join-topic")(self.topic_group_join)
        self.slack_app.command("/leave-topic")(self.topic_group_leave)
        self.slack_app.command("/my-topics")(self.topic_group_check)
    
    def get_user_groups(self):
        resp = self.slack_app.client.usergroups_list()
        usergroups = resp["usergroups"]
        return usergroups
        
    def get_user_group(self, ug_id: str):
        for usergroup in self.get_user_groups():
            if usergroup["id"] == ug_id:
                return usergroup
            
    def topic_group_check(self, ack, respond: Respond, command):
        ack()
        
        user_id = command["user_id"]
        
        member_usergroups = []
        for usergroup in self.get_user_groups():
            ug_name: str = usergroup["name"]
            ug_handle: str = usergroup["handle"]
            
            if not ug_handle.startswith(self.config.slack.topic_group_prefix):
                continue
            
            ug_users: list[str] = self.slack_app.client.usergroups_users_list(
                usergroup=usergroup["id"])['users']
            
            if user_id in ug_users:
                member_usergroups.append(ug_name)
        
        if member_usergroups:
            respond(blocks=[{
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "You are currently a member of:"
                            }
                        ]
                    },
                    {
                        "type": "rich_text_list",
                        "style": "bullet",
                        "indent": 0,
                        "border": 0,
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {
                                        "type": "text",
                                        "text": topic_group_name
                                    }
                                ]
                            } for topic_group_name in member_usergroups
                        ]
                    }
                ]
            }])
        else:
            respond("You are not currently a member of any user groups")
        
    def topic_group_join(self, ack, respond: Respond, command):
        ack()

        user_id = command["user_id"]
        text = command['text']
        
        capture_pattern = re.compile(r'<!subteam\^(S[A-Z0-9]+)\|@[^>]+>')
        ug_id = capture_pattern.findall(text)[0]
        
        usergroup = self.get_user_group(ug_id)
        ug_name: str = usergroup["name"]
        ug_handle: str = usergroup["handle"]
        
        if ug_handle.startswith(self.config.slack.topic_group_prefix):
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
        
        if ug_handle.startswith(self.config.slack.topic_group_prefix):
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
    
    