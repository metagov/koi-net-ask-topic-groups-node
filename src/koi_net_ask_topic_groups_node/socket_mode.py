from koi_net import logging_context
from slack_bolt.adapter.socket_mode import SocketModeHandler
from koi_net.logging_context import LoggingContext


class SocketMode:
    def __init__(self, slack_app, config, logging_context: LoggingContext):
        self.logging_context = logging_context
        
        self.handler = SocketModeHandler(
            app=slack_app,
            app_token=config.env.ask_tg_slack_app_token
        )
    
    def start(self):
        with logging_context.bound_contextvars():
            self.handler.connect()
        
    def stop(self):
        self.handler.close()