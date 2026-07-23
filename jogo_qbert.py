import pygame
import sys
from ambiente.qbert_env import QbertEnv
from agentes.busca_heuristica import AgenteBuscaHeuristica
from agentes.agente_genetico import AgenteGenetico
from agentes.agente_reforco import AgenteReforco

pygame.init()
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Q*bert Agentes")
relogio = pygame.time.Clock()

fonte_texto = pygame.font.SysFont("Arial", 24)
fonte_titulo = pygame.font.SysFont("Arial", 36, bold=True)

def desenhar_texto(texto, font, cor, x, y, centralizado=True):
    img = font.render(texto, True, cor)
    if centralizado:
        x -= img.get_width() // 2
    tela.blit(img, (x, y))

def rodar_menu():
    """
    Exibe a tela inicial de menu e retorna as escolhas do usuário.
    """
    agente_escolhido = "1"  # Padrão: A*
    com_inimigos = False    # Padrão: Sem inimigos (Cenário Estático)
    rodando = True

    while rodando:
        tela.fill((20, 20, 30)) # Fundo escuro moderno
        
        # --- TÍTULO ---
        desenhar_texto("Q*BERT - AGENTES", fonte_titulo, (255, 255, 0), LARGURA // 2, 60)
        desenhar_texto("Selecione o Agente (Teclas 1, 2 ou 3):", fonte_texto, (255, 255, 255), LARGURA // 2, 150)
        
        # --- OPÇÕES DE AGENTES ---
        cor_a   = (0, 255, 0) if agente_escolhido == "1" else (140, 140, 140)
        cor_gen = (0, 255, 0) if agente_escolhido == "2" else (140, 140, 140)
        cor_ql  = (0, 255, 0) if agente_escolhido == "3" else (140, 140, 140)
        
        desenhar_texto("[1] Busca Heurística (A*)", fonte_texto, cor_a, LARGURA // 2, 200)
        desenhar_texto("[2] Algoritmo Genético (Evolutivo)", fonte_texto, cor_gen, LARGURA // 2, 240)
        desenhar_texto("[3] Q-Learning (Aprendizado por reforço)", fonte_texto, cor_ql, LARGURA // 2, 280)
        
        # --- CONFIGURAÇÃO DE INIMIGOS ---
        desenhar_texto("Modo de Jogo (Pressione 'I' para alternar):", fonte_texto, (255, 255, 255), LARGURA // 2, 360)
        
        texto_ini = "COM INIMIGOS (Dinâmico)" if com_inimigos else "SEM INIMIGOS (Estático)"
        cor_ini = (255, 80, 80) if com_inimigos else (80, 200, 255)
        desenhar_texto(texto_ini, fonte_titulo, cor_ini, LARGURA // 2, 400)
        
        # --- INICIAR ---
        desenhar_texto("Pressione [ENTER] para Iniciar o Teste", fonte_texto, (255, 255, 0), LARGURA // 2, 510)

        pygame.display.flip()
        
        # --- CAPTURA DE EVENTOS ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    agente_escolhido = "1"
                elif evento.key == pygame.K_2:
                    agente_escolhido = "2"
                elif evento.key == pygame.K_3:
                    agente_escolhido = "3"
                elif evento.key == pygame.K_i:
                    com_inimigos = not com_inimigos
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return agente_escolhido, com_inimigos

        relogio.tick(30)

def carregar_agente(escolha, env):
    """
    Instancia e, se necessário, treina o agente escolhido antes de abrir o jogo.
    """
    if escolha == "1":
        print("\nCarregando Busca Heurística (A*)...")
        return AgenteBuscaHeuristica()
        
    elif escolha == "2":
        print("\nEvoluindo população com Algoritmo Genético...")
        
        # Exibe mensagem de carregamento na tela do Pygame
        tela.fill((20, 20, 30))
        desenhar_texto("Evoluindo Genética...", fonte_titulo, (0, 255, 255), LARGURA // 2, ALTURA // 2)
        pygame.display.flip()
        
        agente_gen = AgenteGenetico(tamanho_populacao=150, taxa_mutacao=0.05, tamanho_cromossomo=65)
        melhor_individuo = agente_gen.treinar(env, num_geracoes=1000)
        
        return melhor_individuo
        
    elif escolha == "3":
        print("\nCarregando agente Q-Learning...")

        tela.fill((20, 20, 30))
        desenhar_texto(
            "Treinando Q-Learning...",
            fonte_titulo,
            (0,255,255),
            LARGURA//2,
            ALTURA//2
        )
        pygame.display.flip()

        agente = AgenteReforco()

        try:
            agente.carregar("q_table.pkl")
            print("Tabela Q carregada.")

        except FileNotFoundError:
            print("Tabela não encontrada.")
            print("Treinando...")
            agente.treinar(
                env,
                episodios=10000
            )
            agente.salvar("q_table.pkl")

        return agente

def rodar_jogo(env, agente, escolha_agente, com_inimigos):
    """
    Controla o loop gráfico do Pygame, animando o agente escolhido na pirâmide.
    """
    try:
        img_bloco_dir_fase1 = pygame.image.load("sprites/cenario/plataforma-direita-fase1.png").convert_alpha()
        img_bloco_esq_fase1 = pygame.image.load("sprites/cenario/plataforma-esquerda-fase1.png").convert_alpha()
        img_bloco_esq_comp = pygame.image.load("sprites/cenario/plataforma-esquerda-fase1-completa.png").convert_alpha()
        img_bloco_dir_comp = pygame.image.load("sprites/cenario/plataforma-direita-fase1-completa.png").convert_alpha()
        img_agente = pygame.image.load("sprites/qbert/qbert-frente-esquerda.png").convert_alpha()
        

        # Carrega os sprites do Q*bert para diferentes direções
        sprites_qbert = {
            'baixo_esq': pygame.image.load("sprites/qbert/qbert-frente-esquerda.png").convert_alpha(),
            'baixo_dir': pygame.image.load("sprites/qbert/qbert-frente-direita.png").convert_alpha(),
            'cima_esq':  pygame.image.load("sprites/qbert/qbert-costas-esquerda.png").convert_alpha(),
            'cima_dir':  pygame.image.load("sprites/qbert/qbert-costas-direita.png").convert_alpha()
        }

        mult_x, mult_y = 1.4, 1
        nova_largura = int(img_bloco_dir_fase1.get_width() * mult_x)
        nova_altura = int(img_bloco_dir_fase1.get_height() * mult_y)

        img_bloco_dir_fase1 = pygame.transform.scale(img_bloco_dir_fase1, (nova_largura, nova_altura))
        img_bloco_esq_fase1 = pygame.transform.scale(img_bloco_esq_fase1, (nova_largura, nova_altura))
        img_bloco_dir_comp = pygame.transform.scale(img_bloco_dir_comp, (nova_largura, nova_altura))
        img_bloco_esq_comp = pygame.transform.scale(img_bloco_esq_comp, (nova_largura, nova_altura))
    except FileNotFoundError:
        print("Erro: Imagens não encontradas na pasta 'sprites/'. Verifique os caminhos.")
        return

    ESPACAMENTO_X, ESPACAMENTO_Y = 94, 58
    
    # Sincroniza posições e temporizador (500ms entre pulos para podermos assistir)
    posicao_atual = env.reset()
    linha_agente, coluna_agente = posicao_atual
    
    TEMPO_POR_PASSO = 500
    ultimo_passo = pygame.time.get_ticks()
    
    # Índice para ler a lista de comandos caso o agente seja o Genético
    passo_genetico = 0
    passos_totais = 0
    ultima_acao = 'baixo_esq'
    rodando = True

    while rodando:
        tempo_atual = pygame.time.get_ticks()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        if tempo_atual - ultimo_passo > TEMPO_POR_PASSO:
            ultimo_passo = tempo_atual
            acao = None

            # 1. Escolhe como pegar a ação dependendo do tipo de agente
            if escolha_agente == "2":  # Algoritmo Genético (Lista de Cromossomos)
                if passo_genetico < len(agente.cromossomo):
                    acao = agente.cromossomo[passo_genetico]
                    passo_genetico += 1
            else:  # A* ou Q-Learning (Método interativo obter_acao)
                acao = agente.obter_acao(env.estado_blocos, env.posicao_agente, env.grafo)

            # 2. Executa a ação no ambiente se ela existir
            if acao is not None:
                # Se desativamos os inimigos no menu, garantimos que a bola verde/coily não surjam
                if not com_inimigos and hasattr(env, 'bola_verde'):
                    env.bola_verde.ativa = False

                passos_totais += 1
                nova_posicao, recompensa, vitoria = env.step(acao)
                linha_agente, coluna_agente = nova_posicao

                if acao in sprites_qbert:
                    ultima_acao = acao

                print(f"Passo: {passo_genetico if escolha_agente == '2' else ''} | Ação: {acao.upper():10} | Posição: {nova_posicao} | Recompensa: {recompensa}")

                if vitoria:
                    print("\nVITÓRIA! O agente zerou a pirâmide!")
                    mostrar_tela_fim(True, passos_totais)
                    rodando = False
                elif recompensa in (-10, -100):
                    print("\nGAME OVER! O Q*bert caiu no abismo ou foi pego!")
                    mostrar_tela_fim(False, passos_totais)
                    rodando = False
            else:
                print("\nO agente finalizou sua sequência de ações.")
                rodando = False

        tela.fill((10, 10, 15))
        
        x_topo = LARGURA // 2 - (ESPACAMENTO_X // 2)
        y_topo = 100
        
        # Desenha os blocos da pirâmide
        for linha in range(6):
            for coluna in range(linha + 1):
                x_pixel = x_topo + (coluna * ESPACAMENTO_X) - (linha * (ESPACAMENTO_X // 2))
                y_pixel = y_topo + (linha * ESPACAMENTO_Y)

                ja_pintado = env.estado_blocos.get((linha, coluna), 0) == 1
                
                if coluna <= linha // 2:
                    img_atual = img_bloco_esq_comp if ja_pintado else img_bloco_esq_fase1
                else:
                    img_atual = img_bloco_dir_comp if ja_pintado else img_bloco_dir_fase1
                
                tela.blit(img_atual, (x_pixel, y_pixel))

        # Seleciona o sprite correto de acordo com a última direção
        img_agente_atual = sprites_qbert.get(ultima_acao, sprites_qbert['baixo_esq'])

        # Desenha o Q*bert na posição atual
        larg_bloco = img_bloco_dir_fase1.get_width()
        x_base_bloco = x_topo + (coluna_agente * ESPACAMENTO_X) - (linha_agente * (ESPACAMENTO_X // 2))
        y_base_bloco = y_topo + (linha_agente * ESPACAMENTO_Y)


        x_agente = x_base_bloco + (larg_bloco // 2) - (img_agente_atual.get_width() // 2)
        y_agente = y_base_bloco - img_agente_atual.get_height() + (ESPACAMENTO_Y // 2) - 24
        
        tela.blit(img_agente_atual, (x_agente, y_agente))

        pygame.display.flip()
        relogio.tick(30)

def mostrar_tela_fim(vitoria, passos_totais):
    """
    Exibe um painel centralizado com o resultado e os passos antes de voltar ao menu.
    """
    esperando = True
    while esperando:
        # Fundo escuro semi-transparente cobrindo o jogo
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        tela.blit(overlay, (0, 0))
        
        # Caixa de diálogo central
        larg_caixa, alt_caixa = 520, 260
        x_caixa = (LARGURA - larg_caixa) // 2
        y_caixa = (ALTURA - alt_caixa) // 2
        
        pygame.draw.rect(tela, (25, 25, 40), (x_caixa, y_caixa, larg_caixa, alt_caixa), border_radius=12)
        pygame.draw.rect(tela, (0, 255, 255), (x_caixa, y_caixa, larg_caixa, alt_caixa), 3, border_radius=12)
        
        # Textos informativos
        titulo = "VITÓRIA!" if vitoria else "FIM DE JOGO"
        cor_titulo = (0, 255, 0) if vitoria else (255, 80, 80)
        
        desenhar_texto(titulo, fonte_titulo, cor_titulo, LARGURA // 2, y_caixa + 35)
        
        status_txt = "A pirâmide foi totalmente pintada!" if vitoria else "O agente falhou ou caiu no abismo."
        desenhar_texto(status_txt, fonte_texto, (255, 255, 255), LARGURA // 2, y_caixa + 95)
        
        desenhar_texto(f"Passos utilizados: {passos_totais}", fonte_texto, (255, 255, 0), LARGURA // 2, y_caixa + 145)
        
        desenhar_texto("Pressione [ENTER] para voltar ao Menu", fonte_texto, (200, 200, 200), LARGURA // 2, y_caixa + 205)
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    esperando = False
        relogio.tick(30)

if __name__ == "__main__":
    while True:
        # 1. Abre o Menu Interativo
        escolha_agente, modo_inimigos = rodar_menu()
        print(f"\nConfiguração selecionada -> Agente: [{escolha_agente}] | Inimigos: {modo_inimigos}")
        
        # 2. Cria o ambiente
        env = QbertEnv(niveis=6)
        
        # 3. Carrega (ou treina) o agente na memória
        agente_carregado = carregar_agente(escolha_agente, env)
        
        # 4. Inicia o jogo gráfico com o agente pronto
        if agente_carregado:
            rodar_jogo(env, agente_carregado, escolha_agente, modo_inimigos)
            