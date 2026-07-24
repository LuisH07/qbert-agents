import random
import pickle
from collections import defaultdict

class AgenteReforcoDinamico:
    def __init__(
        self,
        alpha=0.2,
        gamma=0.95,
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.9995,
    ):

        self.alpha = alpha
        self.gamma = gamma

        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        self.q_table = defaultdict(float)

    def estado_para_chave(
        self,
        estado_blocos,
        posicao_qbert,
        posicao_coily,
        estado_coily,
    ):

        # Coily ainda não apareceu no mapa
        if posicao_coily is None:
            dx = 99
            dy = 99
        else:
            dx = posicao_coily[0] - posicao_qbert[0]
            dy = posicao_coily[1] - posicao_qbert[1]

            dx = max(-3, min(3, dx))
            dy = max(-3, min(3, dy))

        return (
            posicao_qbert,
            estado_coily,
            dx,
            dy,
            tuple(sorted(estado_blocos.items()))
        )

    def escolher_acao(
        self,
        estado_blocos,
        posicao_qbert,
        posicao_coily,
        estado_coily,
        grafo,
    ):

        estado = self.estado_para_chave(
            estado_blocos,
            posicao_qbert,
            posicao_coily,
            estado_coily,
        )

        acoes = list(grafo[posicao_qbert].keys())

        if random.random() < self.epsilon:
            return random.choice(acoes)

        melhor = None
        melhor_q = float("-inf")

        for acao in acoes:
            q = self.q_table[(estado, acao)]

            if q > melhor_q:
                melhor_q = q
                melhor = acao

        if melhor is None:
            return random.choice(acoes)

        return melhor

    def atualizar(
        self,
        estado,
        acao,
        recompensa,
        proximo_estado,
        proximas_acoes,
        terminou,
    ):

        atual = self.q_table[(estado, acao)]

        if terminou:
            alvo = recompensa
        else:

            maior_q = max(
                self.q_table[(proximo_estado, a)]
                for a in proximas_acoes
            )
            alvo = recompensa + self.gamma * maior_q

        self.q_table[(estado, acao)] = (
            atual
            + self.alpha * (alvo - atual)
        )

    def treinar(self, env, episodios=10000):
        for episodio in range(episodios):
            env.reset()
            terminou = False

            while not terminou:
                estado = self.estado_para_chave(
                    env.estado_blocos,
                    env.posicao_agente,
                    env.posicao_coily,
                    env.coily.estado,
                )

                acao = self.escolher_acao(
                    env.estado_blocos,
                    env.posicao_agente,
                    env.posicao_coily,
                    env.coily.estado,
                    env.grafo,
                )

                nova_posicao, recompensa, terminou = env.step(acao)

                proximo_estado = self.estado_para_chave(
                    env.estado_blocos,
                    nova_posicao,
                    env.posicao_coily,
                    env.coily.estado,
                )

                proximas_acoes = list(
                    env.grafo[nova_posicao].keys()
                )

                self.atualizar(
                    estado,
                    acao,
                    recompensa,
                    proximo_estado,
                    proximas_acoes,
                    terminou,
                )

            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

            if episodio % 500 == 0:
                print(
                    f"Episódio {episodio}"
                    f" | epsilon = {self.epsilon:.3f}"
                )

    def obter_acao(
        self,
        estado_blocos,
        posicao_qbert,
        posicao_coily,
        estado_coily,
        grafo,
    ):

        estado = self.estado_para_chave(
            estado_blocos,
            posicao_qbert,
            posicao_coily,
            estado_coily,
        )

        acoes = list(grafo[posicao_qbert].keys())

        melhor = None
        melhor_q = float("-inf")

        for acao in acoes:
            q = self.q_table[(estado, acao)]

            if q > melhor_q:
                melhor_q = q
                melhor = acao

        if melhor is None:
            return random.choice(acoes)

        return melhor

    def salvar(self, arquivo):
        with open(arquivo, "wb") as f:
            pickle.dump(dict(self.q_table), f)

    def carregar(self, arquivo):
        with open(arquivo, "rb") as f:
            tabela = pickle.load(f)

        self.q_table = defaultdict(float, tabela)