from rid_lib.types import SlackMessage


class AskMetagovThread(SlackMessage):
    namespace = "ask-metagov.thread"
    
class AskMetagovResponse(SlackMessage):
    namespace = "ask-metagov.response"
    