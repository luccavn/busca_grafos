import pygame
import pandas as pd
from os import path
from collections import defaultdict
from heapq import heappush, heappop
from math import ceil, sqrt
from pygame.locals import Rect

################
## CONSTANTES ##
################

COLOR_BLACK = (0, 0, 0)             # Valores RGB da cor preta.
COLOR_GREEN = (0, 255, 0)           # Valores RGB da cor verde.
COLOR_WHITE = (255, 255, 255)       # Valores RGB da cor branca.
MOUSE_LEFT = 1                      # Inteiro que representa o botão esquerdo do mouse.
MOUSE_RIGHT = 3                     # Inteiro que representa o botão direito do mouse.

###################
## INICIALIZAÇÃO ##
###################

Config = __import__('config')  # Importa as configurações.

pygame.init()   # Inicializa os módulos do pygame.

pygame.display.set_caption(Config.WINDOW_TITLE)   # Altera o título da janela.

screen = pygame.display.set_mode(Config.SCREEN_SIZE)    # Altera as dimensões da janela.

# Carregamos as fontes específicas do sistema que iremos utilizar na interface:
sys_font = pygame.font.SysFont(Config.FONT_FAMILY, Config.FONT_SIZE)
title_font = pygame.font.SysFont(Config.FONT_FAMILY, Config.FONT_SIZE+10)
medium_font = pygame.font.SysFont(Config.FONT_FAMILY, Config.FONT_SIZE+2)

# Carregamos e redimensionamos a imagem do mapa que será utilizada como imagem de fundo da interface:
map_image = pygame.image.load(Config.map_path)
map_image_scaled = pygame.transform.scale(map_image, Config.SCREEN_SIZE)

#############
## CLASSES ##
#############

class Vertex:
    """ Representa um vértice do grafo 

    - name : Identificador do vértice.
    - neighbours : Set que armazena os vizinhos deste vértice.
    - distance : Distância do vizinho até este vértice.
    """

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
    - rect : Retângulo de colisão do ponto do município.
    """
    
    def __init__(self, name, pos):
        self._name = name
        self._pos = pos
        self._rect = Rect((pos[0], pos[1]), (Config.DOT_RADIUS+2, Config.DOT_RADIUS+2))

    @property
    def name(self):
        return self._name

    @property
    def pos(self):
        return self._pos

    @property
    def rect(self):
        return self._rect

#############
## MÉTODOS ##
#############

def already_exists(name, v_list):
    """ Retorna um vértice já existente em uma lista.
    
    - name : Identificador do vértice.
    - v_list : Lista de vértices.

    Se o objeto do tipo Node não existir na lista, retorna None.
    """
    for vertex in v_list:
        if vertex.name == name:
            return vertex
    return None

def get_county_byname(counties, name):
    """ Retorna o município cujo o nome foi especificado.
    
    Retorna um objeto do tipo County.

    - counties : lista de municípios.
    - name : nome do município desejado.
    """
    for county in counties:
        if county.name == name:
            return county
    return None

######################
## MÉTODOS DE BUSCA ##
######################

def dijkstra(edges, f, t):
    """ Algoritmo de Dijkstra

    Encontra a rota mais curta entre dois municípios.
    
    - edges : Arestas do grafo.
    - f : Vértice de origem ou inicial.
    - t : Vértice de objetivo ou final.
    """
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

#################
## FUNÇÃO MAIN ##
#################

if __name__ == "__main__":

    # Fazemos a leitura das distâncias entre os municípios, gerando uma tabela:
    data = pd.read_csv(Config.distances_path, sep=',', encoding='utf-8')

    # Transformamos os valores da tabela em uma matriz:
    data_matrix = data.values

    vertexes = list()  # Lista global de vértices.
    # Varremos a matriz de dados e geramos os vértices:
    for data in data_matrix:
        current_county = data[0]  # Guardamos o nome do município da 1ª coluna.
        current_vertex = already_exists(current_county, vertexes)  # Verificamos se já existe um vértice deste município.
        # Se o método already_exists() retornar None significa que ainda não criamos um vértice para este município:
        if current_vertex is None:
            new_vertex = Vertex()  # Criamos o vértice do município atual.
            new_neighbour = Vertex()  # Criamos o vértice do vizinho.
            new_vertex.name = data[0]  # Atribuímos ao vértice principal o nome da 1ª coluna.
            new_neighbour.name = data[1]  # Atribuímos ao vizinho o nome da 2ª coluna.
            new_neighbour.distance = data[2]  # Atribuímos ao vizinho a distância da 3ª coluna.
            new_vertex.add_neighbour(new_neighbour)  # Adicionamos o vizinho ao vértice principal.
            vertexes.append(new_vertex)  # Adicionamos o vértice na lista global de vértices.
        else:  # Se um vértice deste município já existir, apenas adicionamos o município da 2ª coluna como vizinho dele:
            new_neighbour = Vertex()
            new_neighbour.name = data[1]
            new_neighbour.distance = data[2]
            current_vertex.add_neighbour(new_neighbour)

    # Varremos a lista global de vértices e geramos as arestas para uso no algoritmo de Dijkstra:
    edges = list()
    for vertex in vertexes:
        for neighbour in vertex.neighbours:
            new_edge = (vertex.name, neighbour.name, neighbour.distance)
            edges.append(new_edge)

    # Carregamos o arquivo que possui a posição dos municípios no mapa:
    data = pd.read_csv(Config.positions_path, sep=',', encoding='utf-8')

    # Transformamos os dados em uma matriz.
    data_matrix = data.values

    # Criamos uma lista de objetos do tipo County,
    # esses objetos representam os municípios do mapa.
    # data[0] -> nome do município;
    # data[1] -> posição no eixo x;
    # data[2] -> posição no eixo y.
    map_counties = [County(name=data[0], pos=(data[1], data[2])) for data in data_matrix]
    county_count = len(map_counties)  # Quant. de elementos da lista.

    route_path = None   # Variável do município atual.
    route_dist = None   # Variável da distância da rota atual.
    from_county = None  # Variável do município de origem.
    to_county = None    # Variável do município de destino.

    running = True  # Determina se o programa está ativo.
    while running:
        pygame.event.pump() # Atualizamos os eventos do pygame.

        mouse_pos = pygame.mouse.get_pos()  # Atualizamos a posição do ponteiro do mouse.
        
        # Atualizamos o retângulo de colisão do ponteiro do mouse:
        left, top = (mouse_pos[0], mouse_pos[1])
        width, height = (Config.DOT_RADIUS, Config.DOT_RADIUS)
        mouse_rect = Rect((left, top), (width, height))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Evento de encerramento do programa.
                running = False  # Finaliza o programa.
            if event.type == pygame.KEYDOWN:  # Verificamos se alguma tecla foi pressionada.
                if event.key == pygame.K_ESCAPE:  # K_ESCAPE -> tecla ESC.
                    running = False  # Finaliza o programa.
            if event.type == pygame.MOUSEBUTTONUP:  # Verificamos se algum botão do mouse foi despressionado.
                # Verificamos se o retângulo do ponteiro colide com o retângulo de algum ponto no mapa:
                for county in map_counties:
                    # Função que verifica colisão de retângulos:
                    if county.rect.colliderect(mouse_rect):
                        # Botão direito do mouse determina o município origem e botão esquerdo determina o município destino:
                        if event.button == MOUSE_RIGHT:
                            from_county = county.name
                        elif event.button == MOUSE_LEFT:
                            to_county = county.name
                # Caso já tenhamos os municípios origem e destino,
                # geramos a rota entre eles:
                if (from_county and to_county) is not None:
                    path = dijkstra(edges, from_county, to_county)
                    route_dist = path[0]
                    make_path = lambda tupla: (*make_path(tupla[1]), tupla[0]) if tupla else () # Função lambda recursiva que organiza a rota.
                    route_path = make_path(path[1])
                    # Imprimimos a rota no console:
                    print('\nRota: {} ate {}\nDistancia: aprox. {} km.\nPercurso: {}\n'.format(from_county, to_county, ceil(route_dist), route_path))

        screen.fill(COLOR_WHITE)    # Preenchemos o fundo da tela com a cor específica.
        screen.blit(map_image_scaled, (0, 0))   # Desenhamos a imagem do mapa na tela.

        # Caso já tenhamos a rota:
        if route_path is not None:
            # 1. Renderizamos as arestas por pares de vértices;
            for i in range(len(route_path)-1):
                county1_pos = get_county_byname(map_counties, route_path[i]).pos
                county2_pos = get_county_byname(map_counties, route_path[i+1]).pos
                pygame.draw.line(screen, COLOR_BLACK, county1_pos, county2_pos, Config.LINE_WIDTH)
            # 2. Renderizamos um texto informativo acima do mapa:
            info_text = 'Rota: {} até {}, Distância: aprox. {} km.'.format(from_county, to_county, ceil(route_dist))
            # Criamos uma superfície renderizável:
            text_surface = title_font.render(info_text, True, COLOR_BLACK)
            # Adaptamos a posição do texto de acordo com o nome do município:
            text_position = (Config.SCREEN_SIZE[0]/4 - 10 * len(from_county) + len(to_county), 0)
            # Renderizamos a superfície do texto:
            screen.blit(text_surface, text_position)

        # Definimos as cores de destaque e renderizamos os municípios no mapa:
        for county in map_counties:
            paint_color = COLOR_BLACK  # Cor padrão (município sem destaque).

            # Definimos a cor verde para os municípios de origem e destino
            # e definimos a cor branca para os municípios que fazem parte da rota:
            if route_path is not None:
                if county.name == from_county or county.name == to_county:
                    paint_color = COLOR_GREEN
                elif county.name in route_path:
                    paint_color = COLOR_WHITE

            # Definimos a cor verde para os municípios nos quais o ponteiro colide:
            pointer_collides = county.rect.colliderect(mouse_rect)
            if pointer_collides:
                paint_color = COLOR_GREEN

            # Desenhamos o ponto e o nome dos municípios no mapa:
            pygame.draw.circle(screen, paint_color, county.pos, Config.DOT_RADIUS)
            name_text = medium_font.render(county.name, True, paint_color)
            screen.blit(name_text, (county.pos[0]-len(county.name)*3, county.pos[1]))

        pygame.display.flip()   # Atualizamos a janela da interface.