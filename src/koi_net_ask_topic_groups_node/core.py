from koi_net.core import FullNode
from slack_bolt import App as SlackApp
from slack_sdk import WebClient

from .slack_event_handler import SlackEventHandler

from .knowledge_handlers.slack_usergroup_handler import SlackUserGroupHandler
from .knowledge_handlers.ask_thread_handler import AskThreadHandler
from .user_group_sensor import UserGroupSensor
from .slack_config_manager import SlackConfigManager
from .slack_command_handler import SlackCommandHandler
from .socket_mode import SlackSocketMode
from .config import AskTopicGroupsConfig


class AskTopicGroupsNode(FullNode):
    config_schema = AskTopicGroupsConfig
    
    slack_app: SlackApp = lambda config: SlackApp(
        token=config.env.ask_tg_slack_bot_token,
        signing_secret=config.env.ask_tg_slack_signing_secret)
    
    slack_admin_client: WebClient = lambda config: WebClient(
        token=config.env.ask_tg_slack_user_token)
    
    socket_mode = SlackSocketMode
    slack_command_handler = SlackCommandHandler
    slack_event_handler = SlackEventHandler
    slack_config_manager = SlackConfigManager
    
    user_group_sensor = UserGroupSensor
    
    # knowledge handlers
    ask_thread_handler = AskThreadHandler
    slack_usergroup_handler = SlackUserGroupHandler