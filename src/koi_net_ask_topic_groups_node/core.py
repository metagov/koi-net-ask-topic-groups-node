from koi_net.core import FullNode
from slack_bolt import App as SlackApp
from slack_sdk import WebClient

from .slack_handlers import SlackHandlers
from .handler_context import ExtendedHandlerContext
from .socket_mode import SocketMode
from .config import AskTopicGroupsConfig
from .handlers import handle_ask_metagov_thread


class AskTopicGroupsNode(FullNode):
    config_schema = AskTopicGroupsConfig
    
    # NOTE: config_loader param is a workaround to force start ordering
    slack_app = lambda config, config_loader: SlackApp(
        token=config.env.slack_bot_token,
        signing_secret=config.env.slack_signing_secret)
    
    slack_admin_client = lambda config, config_loader: WebClient(
        token=config.env.slack_user_token)
    
    handler_context = ExtendedHandlerContext
    socket_mode = SocketMode
    slack_handlers = SlackHandlers
    
    knowledge_handlers = FullNode.knowledge_handlers + [
        handle_ask_metagov_thread
    ]