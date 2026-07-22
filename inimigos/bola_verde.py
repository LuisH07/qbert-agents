import random

class BolaVerde:
    def __init__(self):
        self.posicao = (0, 0)
        self.ativa = True

    def mover(self, max_linhas):
        if not self.ativa:
            return None
        
        acao = random.choice(['baixo_esq', 'baixo_dir'])

        l, c = self.posicao
        if acao == 'baixo_esq':
            nova_posicao = (l + 1, c)
        else:
            nova_posicao = (l + 1, c + 1)

        if nova_posicao[0] >= max_linhas:
            self.ativa = False
            return None
        else:
            self.posicao = nova_posicao
        
        return self.posicao