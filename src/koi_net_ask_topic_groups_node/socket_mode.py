from dataclasses import dataclass, field
from koi_net import logging_context
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from koi_net.logging_context import LoggingContext

from .config import AskTopicGroupsConfig


@dataclass
class SlackSocketMode:
    slack_app: App
    config: AskTopicGroupsConfig
    handler: SocketModeHandler | None = field(init=False, default=None)
    
    def start(self):
        self.handler = SocketModeHandler(
            app=self.slack_app, 
            app_token=self.config.env.ask_tg_slack_app_token)
        self.handler.connect()
        
    def stop(self):
        if self.handler:
            self.handler.close()