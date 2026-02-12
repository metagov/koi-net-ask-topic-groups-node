from pydantic import BaseModel
from rid_lib import RID
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

# class ResponseRankingModel(BaseModel):
#     thread: RID
#     community_voted: RID | None  # 👍
#     metagov_staff_pick: RID | None # 🏅
#     accepted_answer: RID | None # ✅