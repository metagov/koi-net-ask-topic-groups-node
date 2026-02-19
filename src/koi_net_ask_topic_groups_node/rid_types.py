from rid_lib.types import SlackMessage, SlackUserGroup


class AskCoreThread(SlackMessage):
    namespace = "ask-core.thread"
    
class AskCoreResponse(SlackMessage):
    namespace = "ask-core.response"

class ThreadLink(SlackMessage):
    namespace = "ask-tg.thread-link"

class AskTopicGroup(SlackUserGroup):
    namespace = "ask-tg.topic-group"