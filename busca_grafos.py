import pygame
import pandas as pd
from os import path
from collections import defaultdict
from heapq import *
from pygame.locals import *
from math import ceil, sqrt

##############
# Constantes #
##############

COLOR_BLACK = (0,0,0)       # Valores RGB da cor preta.
COLOR_WHITE = (255,255,255) # Valores RGB da cor branca.
SCREEN_SIZE = (800, 600)    # Dimensões da janela.
FONT_SIZE = 11              # Tamanho da fonte.
DOT_RADIUS = 4              # Raio dos pontos do mapa.
LINE_WIDTH = 2              # Espessura das linhas de rota.

#################
# Inicialização #
#################

root_dir = path.dirname(path.abspath(__file__)) # Diretório raiz do projeto.
map_path = path.join(root_dir, 'mapa_vale.png') # Diretório da imagem do mapa.

pygame.init()   # Inicializa os módulos do pygame.
pygame.display.set_caption('Algoritmos de Busca em Grafo - Vale do Paraíba')   # Altera o título da janela.

screen = pygame.display.set_mode(SCREEN_SIZE)    # Altera as dimensões da janela.

# Carrega fontes específicas do sistema para uso na interface do usuário.
sys_font = pygame.font.SysFont('Comic Sans MS', FONT_SIZE)
title_font = pygame.font.SysFont('Comic Sans MS', FONT_SIZE+10)
medium_font = pygame.font.SysFont('Comic Sans MS', FONT_SIZE+2)

# Carrega a imagem do mapa para uso na interface do usuário.
map_image = pygame.image.load(map_path)
map_image_scaled = pygame.transform.scale(map_image, SCREEN_SIZE)

###########
# Classes #
###########

class Vertex:
    """ Representa um vértice do grafo 

    - name : Identificador do vértice.
    - neighbours : Set que armazena os vizinhos deste vértice.
    - distance : Distância do vizinho até este vértice."""

    def __init__(self):
        self._name = None
        self._neighbours = set()
        self._distance = None
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def distance(self):
        return self._distance
    
    @distance.setter
    def distance(self, value):
        self._distance = value
    
    @property
    def neighbours(self):
        return self._neighbours
    
    def add_neighbour(self, neighbour):
        self._neighbours.add(neighbour)

class County():
    """ Representa um município no mapa 
    
    - name : Identificador do município.
    - pos : Posição do ponto do município no mapa.
    - rect : Retângulo de colisão do ponto do município."""

    def __init__(self, name, pos):
        self._name = name
        self._pos = pos
        self._rect = Rect((pos[0], pos[1]), (DOT_RADIUS+2, DOT_RADIUS+2))

    @property
    def name(self):
        return self._name

    @property
    def pos(self):
        return self._pos

    @property
    def rect(self):
        return self._rect

###########
# Métodos #
###########

def already_exists(name, lst):
    """Retorna um vértice já existente em uma lista.
    
    - name : Identificador do vértice.
    - lst : Lista de vértices.

    Se o objeto do tipo Node não existir na lista, retorna None."""
    for node in lst:
        if node.name == name:
            return node
    return None

def get_county_byname(counties, name):
    """Retorna o município especificado.
    
    Retorna um objeto do tipo County.

    - counties : lista de municípios.
    - name : nome do município desejado."""
    for county in counties:
        if county.name == name:
            return county
    return None

####################
# Métodos de Busca #
####################

def dijkstra(edges, f, t):
    """Algoritmo de Dijkstra

    Encontra a rota mais curta entre dois municípios.
    
    - edges : Arestas do grafo.
    - f : Vértice de origem ou inicial.
    - t : Vértice de objetivo ou final."""
    g = defaultdict(list)
    for l,r,c in edges:
        g[l].append((c,r))
    q, seen, mins = [(0,f,())], set(), {f: 0}
    while q:
        (cost,v1,path) = heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = (v1, path)
            if v1 == t: return (cost, path)
            for c, v2 in g.get(v1, ()):
                if v2 in seen: continue
                prev = mins.get(v2, None)
                next = cost + c
                if prev is None or next < prev:
                    mins[v2] = next
                    heappush(q, (next, v2, path))
    return float("inf")

###############
# Função main #
###############

if __name__ == "__main__":

    # Faz a leitura dos dados contidos no arquivo dist_vale.csv e cria uma tabela.
    data = pd.read_csv(path.join(root_dir, 'dist_vale.csv'), sep=',', encoding='utf-8')
    data_matrix = data.values    # Transforma os valores da tabela em uma matriz.
    del data

    # Varre a matriz e cria uma lista de Vértices.
    vertexes = list()
    for data in data_matrix:
        current_county = data[0]
        current_vertex = already_exists(current_county, vertexes)
        if current_vertex:    # Se um vértice com este identificador já existir:
            new_neighbour = Vertex()
            new_neighbour.name = data[1]
            new_neighbour.distance = data[2]
            current_vertex.add_neighbour(new_neighbour)
        else:
            new_vertex = Vertex()
            new_neighbour = Vertex()
            new_vertex.name = data[0]
            new_neighbour.name = data[1]
            new_neighbour.distance = data[2]
            new_vertex.add_neighbour(new_neighbour)
            vertexes.append(new_vertex)

    # Varre a lista de Vértices e cria uma lista traduzida para uso no algoritmo de Dijkstra.
    edges = list()
    for vertex in vertexes:
        for neighbour in vertex.neighbours:
            new_edge = (vertex.name, neighbour.name, neighbour.distance)
            edges.append(new_edge)

    # Faz a leitura das posições dos pontos no mapa, contidos no arquivo map_dots.csv
    data = pd.read_csv(path.join(root_dir, 'map_dots.csv'), sep=',', encoding='utf-8')
    data_matrix = data.values    # Transforma os dados em uma matriz.
    del data

    # Cria os municípios que serão desenhados em cima do mapa.
    map_counties = [County(data[0], (data[1], data[2])) for data in data_matrix]
    county_count = len(map_counties)

    route_path = None   # Variável do município atual.
    route_dist = None   # Variável da distância da rota atual.
    from_county = None    # Variável do município de origem.
    to_county = None      # Variável do município de destino.

    running = True  # Determina se o programa está ativo.
    while running:
        pygame.event.pump() # Atualiza os eventos do pygame.

        mouse_pos = pygame.mouse.get_pos()  # Atualiza a posição do ponteiro do mouse.
        mouse_rect = Rect((mouse_pos[0], mouse_pos[1]), (4, 4)) # Atualiza o retângulo de colisão do ponteiro do mouse.

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:   # Botão direito do mouse determina o município de origem do mapa.
                    for county in map_counties:
                        if county.rect.colliderect(mouse_rect): # Verifica se o retângulo do ponteiro colide com o retângulo do ponto no mapa.
                            from_county = county.name
                elif event.button == 3: # Botão esquerdo do mouse determina o município de destino do mapa.
                    for county in map_counties:
                        if county.rect.colliderect(mouse_rect):
                            to_county = county.name
                if from_county and to_county:   # Traça a rota entre os municípios escolhidos no mapa.
                    path = dijkstra(edges, from_county, to_county)
                    route_dist = path[0]
                    make_path = lambda tupla: (*make_path(tupla[1]), tupla[0]) if tupla else () # Função lambda recursiva que organiza a rota.
                    route_path = make_path(path[1])
                    # Imprime a rota no console.
                    print('\nRota: {} ate {}\nDistancia: aprox. {} km.\nPercurso: {}\n'.format(from_county, to_county, ceil(route_dist), route_path))

        screen.fill(COLOR_WHITE)    # Preenche o fundo com a cor específica.
        screen.blit(map_image_scaled, (0, 0))   # Desenha a imagem do mapa.

        for county in map_counties: # Varre a lista de municípios.
            pygame.draw.circle(screen, COLOR_BLACK, county.pos, DOT_RADIUS) # Desenha o ponto do município no mapa.
            name_text = medium_font.render(county.name, True, COLOR_BLACK)    # Cria o texto que representa o nome do município.
            screen.blit(name_text, (county.pos[0]-len(county.name)*3, county.pos[1]))   # Desenha o nome do município no mapa.

        if route_path:    # Desenha as linhas da rota atual.
            for i in range(len(route_path)-1):
                pygame.draw.line(screen, COLOR_BLACK, get_county_byname(map_counties, route_path[i]).pos, get_county_byname(map_counties, route_path[i+1]).pos, LINE_WIDTH)
                title_text = title_font.render('Rota: {} até {}, Distância: aprox. {} km.'.format(from_county, to_county, ceil(route_dist)), True, COLOR_BLACK)
                screen.blit(title_text, (SCREEN_SIZE[0]/4 - 70, 0))

        pygame.display.flip()   # Atualiza a janela do programa.