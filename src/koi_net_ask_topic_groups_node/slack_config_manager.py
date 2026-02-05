from dataclasses import dataclass
from logging import Logger

from slack_bolt import App

from .config import AskTopicGroupsConfig


@dataclass
class SlackConfigManager:
    slack_app: App
    config: AskTopicGroupsConfig
    log: Logger
    
    def start(self):
        resp = self.slack_app.client.auth_test()
        team_id = resp.get("team_id")
        user_id = resp.get("user_id")
        
        if not team_id or not user_id:
            raise RuntimeError("Slack auth test failed")
        
        self.config.slack.team_id = team_id
        self.config.save_to_yaml()
        
        self.log.info(f"Set team id to {team_id}")
        