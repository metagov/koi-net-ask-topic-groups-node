from koi_net.core import FullNode
from slack_bolt import App as SlackApp
from slack_sdk import WebClient

from .user_group_sensor import UserGroupSensor

from .slack_config_manager import SlackConfigManager

from .slack_handlers import SlackHandlers
from .handler_context import ExtendedHandlerContext
from .socket_mode import SocketMode
from .config import AskTopicGroupsConfig
from .knowledge_handlers import handle_ask_metagov_thread, handle_slack_usergroup


class AskTopicGroupsNode(FullNode):
    config_schema = AskTopicGroupsConfig
    
    slack_app: SlackApp = lambda config: SlackApp(
        token=config.env.ask_tg_slack_bot_token,
        signing_secret=config.env.ask_tg_slack_signing_secret)
    
    slack_admin_client: WebClient = lambda config: WebClient(
        token=config.env.ask_tg_slack_user_token)
    
    handler_context = ExtendedHandlerContext
    socket_mode = SocketMode
    slack_handlers = SlackHandlers
    slack_config_manager = SlackConfigManager
    
    user_group_sensor = UserGroupSensor
    
    knowledge_handlers = FullNode.knowledge_handlers + [
        handle_ask_metagov_thread,
        handle_slack_usergroup
    ]