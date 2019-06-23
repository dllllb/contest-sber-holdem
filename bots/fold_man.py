from bots.template_bot import TemplatePlayer


class FoldMan(TemplatePlayer):
    def __init__(self, props):
        super().__init__(props)

    def strategy(self, features, valid_actions):
        return 'fold', 0
