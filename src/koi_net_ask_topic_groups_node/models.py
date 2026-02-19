from pydantic import BaseModel
from rid_lib.types import SlackMessage, SlackUser

from .rid_types import AskCoreThread, SlackUserGroup


class TopicGroupModel(BaseModel):
    usergroup: SlackUserGroup
    handle: str
    name: str
    emoji: str
    users: list[SlackUser] = []
    threads: list[AskCoreThread] = []
    
class ThreadLinkModel(BaseModel):
    thread: AskCoreThread
    message: SlackMessage

