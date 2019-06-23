from bots.template_bot import TemplatePlayer


class HonestAggressivePlayer(TemplatePlayer):
    def __init__(self, props):
        super().__init__(props)

    def strategy(self, features, valid_actions):
        win_rate = features['win_rate']

        if win_rate >= 0.5:
            try:
                action = valid_actions[2]  # fetch RAISE action info
                action['amount'] = action['amount']['max']
            except:
                # all-in already
                action = valid_actions[1]  # fetch CALL action info
        elif win_rate >= 1.0 / features['n_players']:
            action = valid_actions[1]  # fetch CALL action info
        else:
            action = valid_actions[0]  # fetch FOLD action info

        return action['action'], action['amount']
