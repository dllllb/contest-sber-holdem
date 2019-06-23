from bots.template_bot import TemplatePlayer


class FishPlayer(TemplatePlayer):
    def __init__(self, props):
        super().__init__(props)

    def strategy(self, features, valid_actions):
        call_action_info = valid_actions[1]  # fetch CALL action info
        action, amount = call_action_info["action"], call_action_info["amount"]
        return action, amount
