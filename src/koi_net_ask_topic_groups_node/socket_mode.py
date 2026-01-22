from koi_net.utils import bind_logdir
from slack_bolt.adapter.socket_mode import SocketModeHandler


class SocketMode:
    def __init__(self, slack_app, config, root_dir):
        self.slack_app = slack_app
        self.config = config
        self.root_dir = root_dir
        
        self.handler = SocketModeHandler(
            app=self.slack_app,
            app_token=config.env.slack_app_token
        )
    
    @bind_logdir
    def start(self):
        self.handler.connect()