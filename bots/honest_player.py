from bots.template_bot import TemplatePlayer


class HonestPlayer(TemplatePlayer):
    def strategy(self, features, valid_actions):
        win_rate = features['win_rate']

        if win_rate >= 1.0 / features['n_players']:
            action = valid_actions[1]  # fetch CALL action info
        else:
            action = valid_actions[0]  # fetch FOLD action info
        return action['action'], action['amount']
