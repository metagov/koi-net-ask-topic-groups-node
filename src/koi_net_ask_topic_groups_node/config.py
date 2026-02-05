from rid_lib.types import KoiNetNode
from koi_net.config.core import EnvConfig
from koi_net.config.full_node import (
    FullNodeConfig, 
    KoiNetConfig, 
    ServerConfig, 
    NodeProfile, 
    NodeProvides
)

from .rid_types import AskMetagovThread


class SlackEnvConfig(EnvConfig):
    ask_tg_slack_bot_token: str
    ask_tg_slack_signing_secret: str
    ask_tg_slack_app_token: str
    ask_tg_slack_user_token: str

class AskTopicGroupsConfig(FullNodeConfig):
    env: SlackEnvConfig = SlackEnvConfig()
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="ask-topic-groups",   # human readable name for your node
        node_profile=NodeProfile(
            provides=NodeProvides(
                event=[],
                state=[]
            )
        ),
        rid_types_of_interest=[KoiNetNode, AskMetagovThread] # RID types this node should subscribe to
    )