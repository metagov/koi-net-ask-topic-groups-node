import re
from koi_net.cache import Cache
from slack_bolt import App, Respond
from slack_sdk import WebClient
from koi_net.processor.kobj_queue import KobjQueue


class SlackHandlers:
    slack_app: App
    slack_admin_client: WebClient
    kobj_queue: KobjQueue
    cache: Cache
    
    def __init__(self, slack_app, slack_admin_client, kobj_queue, cache):
        self.slack_app = slack_app
        self.slack_admin_client = slack_admin_client
        self.kobj_queue = kobj_queue
        self.cache = cache
        
        self.msg_channel = None
        self.msg_ts = None
        
        self.register_handlers()
    
    def register_handlers(self):
        self.slack_app.command("/join-topic")(self.topic_group_join)
        self.slack_app.command("/leave-topic")(self.topic_group_leave)
    
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
            respond(f"{ug_handle} is not a valid topic group")
            
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
    
    