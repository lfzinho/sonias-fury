import pygame
import os

# Define as variaveis do jogo
GRAVIDADE = 0.7


# Variáveis Globais
LARGURA_TELA = 800
ALTURA_TELA = int(LARGURA_TELA * 0.8)
TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))

# Imagens
imagem_lapis = pygame.image.load(r"C:\Users\Kayo\sonias-fury\sprites\bullet.png").convert_alpha()


class Soldado(pygame.sprite.Sprite):
    """
        Classe para jogadores e inimigos
    """

    def __init__(self, tipo, x, y, escala, velocidade, municao):
        pygame.sprite.Sprite.__init__(self)
        self.health = 100
        self.vivo = True
        self.tipo = tipo
        self.velocidade = velocidade
        self.vel_y = 0
        self.direcao = 1
        self.virar = False
        self.lista_animacoes = []
        self.frame_indice = 0
        self.acao = 0
        self.no_ar = True
        self.pular = False
        self.vida = 100
        self.municao = municao
        self.tempo_tiro = 0

        self.tempo_de_atualizacao = pygame.time.get_ticks()

        tipos_de_animacao = ["Idle", "Run", "Jump"]
        for animation in tipos_de_animacao:
            lista_temporaria = []
            # conta quantos arquivos tem na pasta (ou seja, quantos frames tem a animação)
            num_de_frames = len(os.listdir(os.path.join("sprites", self.tipo, animation)))
            print(num_de_frames, " em ", animation)
            for i in range(num_de_frames):
                imagem = pygame.image.load(os.path.join("sprites", self.tipo, animation, (str(i) + ".png")))
                imagem = pygame.transform.scale(imagem,
                                                (int(imagem.get_width() * escala), int(imagem.get_height() * escala)))
                lista_temporaria.append(imagem)
            self.lista_animacoes.append(lista_temporaria)

        self.image = self.lista_animacoes[self.acao][self.frame_indice]
        self.tempo_de_atualizacao = pygame.time.get_ticks()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        """
            Vai cuidar de todas as atualizações
        """
        self.update_animation()
        self.check_alive()
        # Atualiza o cooldown do tiro
        if self.tempo_tiro > 0:
            self.tempo_tiro -= 1

    def move(self, movendo_esquerda, movendo_direita):
        """
            Verifica se o personagem deveria estar se movendo, e altera sua posição em x e y.
            Também verifica se o sprite necessita ser espelhado.
            :param movendo_esquerda: False ou True
            :param movendo_direita: False ou True
            :return:
        """
        dx = 0
        dy = 0

        if movendo_esquerda:
            dx = -self.velocidade
            self.direcao = -1
            self.virar = True
        if movendo_direita:
            dx = self.velocidade
            self.direcao = 1
            self.virar = False

        # Pular
        if self.pular == True and self.no_ar == False:
            self.vel_y = -11
            self.pular = False
            self.no_ar = True

        # Aplicando Gravidade
        self.vel_y += GRAVIDADE

        # Coloca uma velocidade limite
        if self.vel_y > 10:
            self.vel_y = 10

        dy += self.vel_y

        # Checa colisão com o solo ficticio (para teste)
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.no_ar = False

        # Atualiza a posição do retângulo
        self.rect.x += dx
        self.rect.y += dy

    def shooting(self):
        if self.tempo_tiro == 0 and self.municao > 0:
            self.tempo_tiro = 20
            lapis = Bala(
                self.rect.centerx + (0.6 * self.rect.size[0] * self.direcao),
                self.rect.centery,
                self.direcao)
            grupo_de_balas.add(lapis)
            self.municao -= 1

    def update_animation(self):
        """
            Aqui é o onde é mudado entre os frames da animação do personagem
        """

        # Tempo entre as trocas de imagens
        ANIMATION_COOLDOWN = 100
        # Atualiza a imagem dependendo do frame atual
        self.image = self.lista_animacoes[self.acao][self.frame_indice]
        # Checa se passou um tempo suficiente desde a ultima atualização
        if pygame.time.get_ticks() - self.tempo_de_atualizacao > ANIMATION_COOLDOWN:
            self.tempo_de_atualizacao = pygame.time.get_ticks()
            self.frame_indice += 1
            # Volta para o primeiro frame da animação quando passa do ultimo
            if self.frame_indice >= len(self.lista_animacoes[self.acao]):
                self.frame_indice = 0

    def update_action(self, new_action):
        # Checa se a nova ação é diferente da antiga
        if new_action != self.acao:
            self.acao = new_action
            # Atualiza as variáveis da atualização
            self.frame_indice = 0
            self.tempo_de_atualizacao = pygame.time.get_ticks()

    def check_alive(self):
        if self.vida <= 0:
            self.vida = 0
            self.velocidade = 0
            self.vivo = False
            self.update_action(3)

    def draw(self, tela):
        """
            Desenha o personagem na tela
            :param tela: objeto tela
            :return:
        """
        tela.blit(pygame.transform.flip(self.image, self.virar, False), self.rect)


class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, direcao):
        super().__init__()
        self.x = 10
        self.direcao = direcao
        self.image = imagem_lapis
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        # Movimenta a bala
        self.rect.x += (self.direcao * self.x)
        # Checa se as balas sairam da tela para tira-las da memória
        if self.rect.right < 0 or self.rect.left > TELA.get_width():
            self.kill()
        # Checa a colisão entre objetos
        if pygame.sprite.spritecollide(jogador, grupo_de_balas, False):
            if jogador.alive:
                jogador.health -= 5
                self.kill()
        if pygame.sprite.spritecollide(inimigo, grupo_de_balas, False):
            if inimigo.alive:
                inimigo.health -= 25
                self.kill()

# Cria objetos da classe Soldado
jogador = Soldado("jogador", 200, 200, 2, 2, 9999)
inimigo = Soldado("inimigo", 400, 300, 2, 3, 0)

# Cria uma grupo para os projéteis
grupo_de_balas = pygame.sprite.Group()
