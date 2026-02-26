from pydantic import BaseModel, Field
from rid_lib.types import KoiNetNode
from koi_net.config import (
    FullNodeConfig, 
    KoiNetConfig, 
    ServerConfig, 
    FullNodeProfile, 
    NodeProvides,
    EnvConfig
)

from .rid_types import AskCoreThread, AskTopicGroup, SlackUserGroup


class SlackEnvConfig(EnvConfig):
    ask_tg_slack_bot_token: str
    ask_tg_slack_signing_secret: str
    ask_tg_slack_app_token: str
    ask_tg_slack_user_token: str


class SlackConfig(BaseModel):
    team_id: str | None = None

class AskTopicGroupsConfig(FullNodeConfig):
    env: SlackEnvConfig = Field(default_factory=SlackEnvConfig)
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="ask-topic-groups",   # human readable name for your node
        node_profile=FullNodeProfile(
            provides=NodeProvides(
                event=[AskTopicGroup],
                state=[AskTopicGroup, SlackUserGroup]
            )
        ),
        rid_types_of_interest=[KoiNetNode, AskCoreThread] # RID types this node should subscribe to
    )
    slack: SlackConfig = SlackConfig()
