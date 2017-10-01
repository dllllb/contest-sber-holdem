from bots.template_bot import TemplatePlayer


class FoldMan(TemplatePlayer):
    def strategy(self, features, valid_actions):
        return 'fold', 0
