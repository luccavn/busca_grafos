import pygame
import pandas as pd
from os import path
from collections import defaultdict
from heapq import *
from pygame.locals import *
from math import ceil, sqrt

# Constantes:

COLOR_BLACK = (0,0,0)       # Valores RGB da cor preta.
COLOR_WHITE = (255,255,255) # Valores RGB da cor branca.
SCREEN_SIZE = (800, 600)    # Dimensões da janela.
FONT_SIZE = 11              # Tamanho da fonte.
DOT_RADIUS = 4              # Raio dos pontos do mapa.
LINE_WIDTH = 2              # Espessura das linhas de rota.

ROOT_DIR = path.dirname(path.abspath(__file__)) # Diretório raiz do projeto.

# Carrega a imagem do mapa.
map_path = path.join(ROOT_DIR, 'mapa_vale.png')
with pygame.image.load(map_path) as map_image:
    vale_map_img = pygame.transform.scale(map_image), SCREEN_SIZE)

pygame.init()   # Inicializa os módulos do pygame.
pygame.display.set_caption('Projeto Vale do Paraíba')   # Altera o título da janela.

screen = pygame.display.set_mode(SCREEN_SIZE)    # Altera as dimensões da janela.

sys_font = pygame.font.SysFont('Comic Sans MS', FONT_SIZE) # Carrega uma fonte específica do sistema para uso.
title_font = pygame.font.SysFont('Comic Sans MS', FONT_SIZE+10) # Carrega uma fonte específica do sistema para uso.
medium_font = pygame.font.SysFont('Comic Sans MS', FONT_SIZE+2)

@class
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

@class
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

def already_exists(name, lst):
    """Retorna um vértice já existente em uma lista.
    
    - name : Identificador do vértice.
    - lst : Lista de vértices.

    Se o objeto do tipo Node não existir na lista, retorna None."""
    for node in lst:
        if node.get_name() == name:
            return node
    return None

def get_city_byname(cities, name):
    """Retorna o município especificado.
    
    Retorna um objeto do tipo County.

    - cities : lista de municípios.
    - name : nome do município desejado."""
    for city in cities:
        if city.get_name() == name:
            return city
    return None

def dijkstra(edges, f, t):
    """Algoritmo de Dijkstra

    Encontra a rota mais curta entre dois municípios."""
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

# Função main.
if __name__ == "__main__":

    # Faz a leitura dos dados contidos no arquivo dist_vale.csv e cria uma tabela.
    data = pd.read_csv(path.join(ROOT_DIR, 'dist_vale.csv'), sep=',', encoding='utf-8')
    values = data.values    # Transforma os valores da tabela em uma matriz.

    # Varre a matriz e cria uma lista de Vértices.
    vertexes = list()
    for i in range(len(values)):
        current_city = values[i][0]
        current_node = already_exists(current_city, vertexes)
        if current_node:
            new_neighbour = Vertex()
            new_neighbour.name = values[i][1]
            new_neighbour.distance = values[i][2]
            current_node.add_neighbour(new_neighbour)
        else:
            new_vertex = Vertex()
            new_neighbour = Vertex()
            new_vertex.name = values[i][0]
            new_neighbour.name = values[i][1]
            new_neighbour.distance = values[i][2]
            new_vertex.add_neighbour(new_neighbour)
            vertexes.append(new_vertex)

    # Varre a lista de Nodes e cria a lista de Vértices para uso no algoritmo de Dijkstra.
    edges = list()
    for node in nodes:
        for neighbour in node.neighbours:
            new_edge = (node.get_name(), neighbour.get_name(), neighbour.get_distance())
            edges.append(new_edge)

    # Faz a leitura das posições dos pontos no mapa, contidos no arquivo map_dots.csv
    map_data = pd.read_csv(path.join(ROOT_DIR, 'map_dots.csv'), sep=',', encoding='utf-8')
    map_values = map_data.values    # Transforma os dados em uma matriz.

    # Cria os MapDots que representam os pontos no mapa.
    map_cities = [County(map_values[i][0], (map_values[i][1], map_values[i][2])) for i in range(len(map_values))]
    city_count = len(map_cities)

    route_path = None   # Variável do município atual.
    route_dist = None   # Variável da distância da rota atual.
    from_city = None    # Variável do município de origem.
    to_city = None      # Variável do município de destino.

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
                    for city in map_cities:
                        if city.get_rect().colliderect(mouse_rect): # Verifica se o retângulo do ponteiro colide com o retângulo do ponto no mapa.
                            from_city = city.get_name()
                elif event.button == 3: # Botão esquerdo do mouse determina o município de destino do mapa.
                    for city in map_cities:
                        if city.get_rect().colliderect(mouse_rect):
                            to_city = city.get_name()
                if from_city and to_city:   # Traça a rota entre os municípios escolhidos no mapa.
                    path = dijkstra(edges, from_city, to_city)
                    route_dist = path[0]
                    make_path = lambda tupla: (*make_path(tupla[1]), tupla[0]) if tupla else () # Função lambda recursiva que organiza a rota.
                    route_path = make_path(path[1])
                    # Imprime a rota no console.
                    print('\nRota: {} ate {}\nDistancia: aprox. {} km.\nPercurso: {}\n'.format(from_city, to_city, ceil(route_dist), route_path))

        screen.fill(COLOR_WHITE)    # Preenche o fundo com a cor específica.
        screen.blit(vale_map_img, (0, 0))   # Desenha a imagem do mapa.

        for city in map_cities: # Varre a lista de municípios.
            pygame.draw.circle(screen, COLOR_BLACK, city.get_pos(), DOT_RADIUS) # Desenha o ponto do município no mapa.
            name_text = medium_font.render(city.get_name(), True, COLOR_BLACK)    # Cria o texto que representa o nome do município.
            screen.blit(name_text, (city.get_pos()[0]-len(city.get_name())*3, city.get_pos()[1]))   # Desenha o nome do município no mapa.

        if route_path:    # Desenha as linhas da rota atual.
            for i in range(len(route_path)-1):
                pygame.draw.line(screen, COLOR_BLACK, get_city_byname(map_cities, route_path[i]).get_pos(), get_city_byname(map_cities, route_path[i+1]).get_pos(), LINE_WIDTH)
                title_text = title_font.render('Rota: {} até {}, Distância: aprox. {} km.'.format(from_city, to_city, ceil(route_dist)), True, COLOR_BLACK)
                screen.blit(title_text, (SCREEN_SIZE[0]/4 - 70, 0))


        pygame.display.flip()   # Atualiza a janela do programa.
