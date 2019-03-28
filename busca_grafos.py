#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pygame
import pandas as pd
from pygame.locals import Rect
from lib.ordered_set import OrderedSet

##############
# CONSTANTES #
##############

COLOR_BLACK = (0, 0, 0)             # Valores RGB da cor preta.
COLOR_GREEN = (0, 255, 0)           # Valores RGB da cor verde.
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)       # Valores RGB da cor branca.
# Inteiro que representa o botão esquerdo do mouse.
MOUSE_LEFT = 1
# Inteiro que representa o botão direito do mouse.
MOUSE_RIGHT = 3

#################
# INICIALIZAÇÃO #
#################

Config = __import__('config')  # Importa as configurações.

pygame.init()   # Inicializa os módulos do pygame.

pygame.display.set_caption(Config.WINDOW_TITLE)   # Altera o título da janela.

# Altera as dimensões da janela.
screen = pygame.display.set_mode(Config.SCREEN_SIZE)

# Carregamos as fontes específicas do sistema que iremos utilizar na interface:
sys_font = pygame.font.SysFont(Config.FONT_FAMILY, Config.FONT_SIZE)
title_font = pygame.font.SysFont(Config.FONT_FAMILY, Config.FONT_SIZE+10)
medium_font = pygame.font.SysFont(Config.FONT_FAMILY, Config.FONT_SIZE+2)

# Carregamos e redimensionamos a imagem do mapa que será utilizada como imagem de fundo da interface:
map_image = pygame.image.load(Config.map_path)
map_image_scaled = pygame.transform.scale(map_image, Config.SCREEN_SIZE)

#####################
# CLASSES E FUNÇÕES #
#####################


class Graph(dict):
    """ Representa um grafo.

    Esta classe é uma implementação de um dicionário,
    ou seja, possui as mesmas funcionalidades de um 
    objeto do tipo dict().
    """

    def create_from_csv(self, path):
        """ Lê um arquivo .csv e cria os vértices do grafo.

        O arquivo deve conter 3 colunas separadas por vírgulas, onde:
        - Primeira coluna: Identificador do vértice origem;
        - Segunda coluna: Identificador do vértice vizinho;
        - Terceira coluna: Distância entre os dois vértices.

        Parâmetros:
        - path : caminho do arquivo .csv
        """
        # Fazemos a leitura das distâncias entre os municípios, gerando uma tabela de 3 colunas:
        data = pd.read_csv(path, sep=',', encoding='utf-8')
        # Convertemos a tabela em uma matriz:
        data_matrix = data.values
        # Criamos um dicionário onde as chaves serão o nome dos municípios da primeira coluna
        # e todas elas terão uma lista vazia como valor. Utilizamos listas do tipo set()
        # pois elas possuem um acesso mais rápido e não aceitam objetos repetidos:
        for row in data_matrix:
            from_city = row[0]
            self[from_city] = set()
        # Agora adicionamos os vizinhos desses municípios, que são os municípios da segunda coluna.
        # Note que por enquanto não estamos utilizando a coluna de distâncias:
        for from_city, to_city, distance in data_matrix:
            self[from_city].add(to_city)


class City:
    """ Representa um município no mapa 

    Parâmetros:
    - name : Identificador do município.
    - pos : Posição do ponto do município no mapa.
    - rect : Retângulo de colisão do ponto do município.
    """

    def __init__(self, name, pos):
        self._name = name
        self._pos = pos
        self._neighbours = set()
        rect_pos = (pos[0], pos[1])
        rect_dim = (Config.DOT_RADIUS+2, Config.DOT_RADIUS+2)
        self._rect = Rect(rect_pos, rect_dim)

    @property
    def name(self):
        return self._name

    @property
    def pos(self):
        return self._pos

    @property
    def rect(self):
        return self._rect

    @property
    def neighbours(self):
        return self._neighbours

    def add_neighbour(self, neighbour):
        if isinstance(neighbour, (tuple, list, set)):
            for neigh in neighbour:
                self._neighbours.add(neigh)
        else:
            self._neighbours.add(neighbour)


class Edge:
    """ Representa uma aresta.

    Parâmetros:
    - origin : Identificador da origem.
    - destiny : Identificador do destino.
    - orig_pos : Posição de origem.
    - dest_pos : Posição de destino.
    """

    def __init__(self, origin, orig_pos, destiny, dest_pos):
        self._origin = origin
        self._destiny = destiny
        self._orig_pos = orig_pos
        self._dest_pos = dest_pos

    @property
    def origin(self):
        return self._origin

    @property
    def destiny(self):
        return self._destiny

    @property
    def origin_pos(self):
        return self._orig_pos

    @property
    def destiny_pos(self):
        return self._dest_pos


def get_city_byname(cities, name):
    """ Retorna o município cujo o nome foi especificado.

    Retorna um objeto do tipo city ou None caso não seja encontrado.

    Parâmetros:
    - cities : lista de municípios.
    - name : nome do município desejado.
    """
    for city in cities:
        if city.name == name:
            return city
    return None


def get_edge(edge_list, origin, destiny):
    """ Retorna a aresta com a origem e o destino especificados,
    não importando o sentido.

    Retorna um objeto do tipo Edge ou None caso não seja encontrado.

    Parâmetros:
    - edge_list : Lista de arestas.
    - origin : Identificador da origem.
    - destiny : Identificador do destino.
    """
    for edge in edge_list:
        if edge.origin == origin and edge.destiny == destiny\
                or edge.origin == destiny and edge.destiny == origin:
            return edge
    return None


def format_visited_list(origin, graph, vlist):
    vertex = origin
    result = dict()
    result[vertex] = list()
    for i in range(len(vlist)):
        if vertex in graph[vlist[i]]:
            result[vertex].append(vlist[i])
        else:
            result[vlist[i]] = list()
            vertex = vlist[i]
    return result


#######################
# MÉTODO DE AMPLITUDE #
#######################

def bfs(graph, origin, goal):
    """ Visita todos os vizinhos partindo do vértice origin até encontrar o
    vértice goal.

    Retorna uma tupla com os vértices visitados e o caminho mais curto em
    forma de lista.

    Parâmetros:
    - origin : vértice inicial
    - goal : vértice objetivo
    """
    queue = [(origin, [origin])]
    visited = OrderedSet()
    while queue:
        vertex, path = queue.pop(0)
        visited.add(vertex)
        for neighbour in graph[vertex]:
            if neighbour == goal:
                # print(queue)
                return (visited, path + [goal])
            else:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append((neighbour, path + [neighbour]))
                    # print(queue)

##########################
# MÉTODO DE PROFUNDIDADE #
##########################


def dfs(graph, origin, goal):
    """ Inicia no vértice origin, voltando até encontrar o vértice goal.

    Retorna uma tupla com os vértices visitados e o caminho mais curto em forma de lista.

    Parâmetros:
    - origin : vértice inicial
    - goal : vértice objetivo
    """
    stack = [(origin, [origin])]
    visited = OrderedSet()
    while stack:
        vertex, path = stack.pop()
        visited.add(vertex)
        for neighbour in graph[vertex]:
            if neighbour == goal:
                # print(stack)
                return (visited, path + [goal])
            else:
                if neighbour not in visited:
                    visited.add(neighbour)
                    stack.append((neighbour, path + [neighbour]))
                    # print(stack)

###############
# FUNÇÃO MAIN #
###############


if __name__ == "__main__":

    # Instanciamos nosso grafo e geramos sua estrutura através da
    # função create_from_csv que lê um arquivo .csv e usa os dados
    # para criar os vértices do grafo:
    graph = Graph()
    graph.create_from_csv(Config.distances_path)

    # O grafo é apenas a representação do mapa em forma de lista,
    # ele será útil apenas durante a aplicação dos algoritmos,
    # portanto teremos que criar os objetos que realmente guardarão
    # as informações de cada município, além das arestas do grafo.

    # Fazemos a leitura das informações do mapa, gerando uma tabela
    # de 3 colunas, depois convertemos esta tabela em uma matriz:
    data = pd.read_csv(Config.positions_path, sep=',', encoding='utf-8')
    data_matrix = data.values

    map_cities = set()    # Lista de municípios.

    # Para cada linha i da matriz criamos um novo objeto
    # do tipo city e o adicionamos na lista:
    for city_name, pos_x, pos_y in data_matrix:
        new_city = City(name=city_name, pos=(pos_x, pos_y))
        map_cities.add(new_city)

    # Adicionamos os vizinhos desses municípios de acordo com o grafo
    # que possui todas as informações de vizinhança:
    for city, neighbours in graph.items():
        for neighbour in neighbours:
            # Buscamos pelo objeto dos municípios através da função get_city_byname():
            city_object = get_city_byname(map_cities, city)
            neighbour_object = get_city_byname(map_cities, neighbour)
            # Adicionamos o vizinho ao município de origem:
            city_object.add_neighbour(neighbour_object)

    map_edges = set()   # Lista de arestas.

    # Para cada vértice do grafo pegamos o nome e a lista
    # de vizinhos e buscamos pelo objeto do tipo city
    # para que possamos fazer as ligações:
    for city, neighbours in graph.items():
        for neighbour in neighbours:
            # Verificamos se a aresta desses municípios já existe:
            if get_edge(map_edges, city, neighbour) is None:
                # Buscamos pelo objeto dos municípios através da função get_city_byname():
                city_object = get_city_byname(map_cities, city)
                neighbour_object = get_city_byname(map_cities, neighbour)
                # Criamos a aresta e a adicionamos na lista de arestas:
                new_edge = Edge(origin=city, orig_pos=city_object.pos,
                                destiny=neighbour, dest_pos=neighbour_object.pos)
                map_edges.add(new_edge)

    # Variáveis auxiliares:
    method_index = 0        # Índice do método de busca selecionado.
    found_path = None       # Caminho realizado pelo algoritmo.
    visited_cities = None  # Municípios visitados pelo algoritmo.
    from_city = None      # Município de origem.
    to_city = None        # Município de destino.
    # Determina se as arestas serão mostradas na interface.
    draw_edges = False
    exit_ui = False         # Determina se o programa irá encerrar.

    while not exit_ui:
        pygame.event.pump()  # Atualizamos os eventos do pygame.

        # Atualizamos a posição do ponteiro do mouse.
        mouse_pos = pygame.mouse.get_pos()

        # Atualizamos o retângulo de colisão do ponteiro do mouse:
        left, top = (mouse_pos[0], mouse_pos[1])    # Posicionamento.
        width, height = (Config.DOT_RADIUS, Config.DOT_RADIUS)  # Dimensões.
        mouse_rect = Rect((left, top), (width, height))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Evento de encerramento do programa.
                exit_ui = True  # Finaliza o programa.
            if event.type == pygame.KEYDOWN:  # Verificamos se alguma tecla foi pressionada.
                if event.key == pygame.K_ESCAPE:  # K_ESCAPE -> Tecla Esc.
                    exit_ui = True  # Finaliza o programa.
                elif event.key == pygame.K_SPACE:   # K_SPACE -> Tecla Espaço.
                    # Alternamos entre mostrar ou não as arestas na interface.
                    draw_edges = True if draw_edges is False else False
                elif event.key == pygame.K_LEFT:    # K_LEFT -> Seta esquerda.
                    # Alterna entre os métodos de busca.
                    method_index = method_index - \
                        1 if method_index > 0 else len(Config.METHOD_NAMES)-1
                elif event.key == pygame.K_RIGHT:   # K_RIGHT -> Seta direita.
                    # Alterna entre os métodos de busca.
                    method_index = method_index + \
                        1 if method_index < len(Config.METHOD_NAMES)-1 else 0
            # Verificamos se algum botão do mouse foi pressionado:
            if event.type == pygame.MOUSEBUTTONUP:
                for city in map_cities:
                    # Verificamos se o retângulo do ponteiro colide com o
                    # retângulo de algum ponto no mapa:
                    if city.rect.colliderect(mouse_rect):
                        # Os botões esquerdo e direito do mouse determinam,
                        # respectivamente, os municípios de origem e de
                        # destino:
                        if event.button == MOUSE_LEFT:
                            from_city = city
                        elif event.button == MOUSE_RIGHT:
                            to_city = city
                # Caso já tenhamos os municípios de origem e de destino
                # selecionados, geramos a rota entre eles:
                if (from_city and to_city) is not None:
                    result = None
                    # Verificamos qual método de busca está selecionado e
                    # chamamos a função do mesmo:
                    if (method_index == 0):
                        # Resultado do algoritmo de amplitude.
                        result = bfs(graph, from_city.name, to_city.name)
                    else:
                        # Resultado do algoritmo de profundidade.
                        result = dfs(graph, from_city.name, to_city.name)
                    # Municípios que foram visitados pelo algoritmo.
                    visited_cities = [city for city in result[0]]
                    # Caminho mais curto da origem até o destino.
                    found_path = result[1]

                    # Imprimimos as informações no console:
                    info_text = '\n\n# Rota: {} ate {}.\n\nCaminho encontrado: {} passos -> {}.\n\nMunicípios visitados: {} -> {}'
                    print(info_text.format(from_city.name, to_city.name, len(found_path)-1, found_path, len(visited_cities), visited_cities))

        # Preenchemos o fundo da tela com uma cor específica.
        screen.fill(COLOR_WHITE)
        # Desenhamos a imagem do mapa na tela.
        screen.blit(map_image_scaled, (0, 0))

        # Renderizamos as arestas por pares de vértices:
        for edge in map_edges:
            # Verificamos se a origem e o destino da aresta coincide com o caminho resultante:
            is_path_edge = (found_path is not None) and (
                edge.origin in found_path and edge.destiny in found_path)
            is_visited_edge = (found_path is not None) and (
                edge.origin in found_path and edge.destiny in visited_cities)
            # Desenha as arestas que não fazem parte do caminho:
            if draw_edges is True:
                pygame.draw.line(screen, COLOR_BLACK, edge.origin_pos,
                                 edge.destiny_pos, Config.LINE_WIDTH)
                # Desenha as arestas que fazem parte dos visitados:
                if is_visited_edge:
                    pygame.draw.line(
                        screen, COLOR_RED, edge.origin_pos, edge.destiny_pos, Config.LINE_WIDTH)
            # Desenha as arestas que fazem parte do caminho:
            if is_path_edge:
                pygame.draw.line(screen, COLOR_GREEN, edge.origin_pos,
                                 edge.destiny_pos, Config.LINE_WIDTH)

        # Caso já tenhamos a rota:
        if found_path is not None:
            # Renderizamos um texto informativo acima do mapa:
            info_text = 'De {} até {}. Passos: {}.'.format(
                from_city.name, to_city.name, len(found_path)-1)
            # Criamos uma superfície renderizável:
            text_surface = title_font.render(info_text, True, COLOR_BLACK)
            # Adaptamos a posição do texto de acordo com o nome do município:
            text_position = (
                Config.SCREEN_SIZE[0]/4 - 9 * len(from_city.name) + len(to_city.name), 0)
            # Renderizamos a superfície do texto:
            screen.blit(text_surface, text_position)

        # Desenhamos o texto do método selecionado:
        method_text = 'Método de busca: ' + Config.METHOD_NAMES[method_index]
        method_surface = title_font.render(method_text, True, COLOR_BLACK)
        method_position = (Config.SCREEN_SIZE[0]/4, Config.SCREEN_SIZE[1]-24)
        screen.blit(method_surface, method_position)

        # Definimos as cores de destaque e renderizamos os municípios no mapa:
        for city in map_cities:
            paint_color = COLOR_BLACK  # Cor padrão (município sem destaque).

            # Definimos a cor verde para os municípios de origem e destino
            # e definimos a cor branca para os municípios que fazem parte da rota:
            if (found_path is not None) and (city.name == from_city or city.name == to_city):
                paint_color = COLOR_GREEN

            # Definimos a cor verde para os municípios nos quais o ponteiro colide:
            pointer_collides = city.rect.colliderect(mouse_rect)
            if pointer_collides:
                paint_color = COLOR_GREEN

            # Desenhamos o ponto e o nome dos municípios no mapa:
            pygame.draw.circle(screen, paint_color,
                               city.pos, Config.DOT_RADIUS)
            name_text = medium_font.render(city.name, True, paint_color)
            screen.blit(name_text, (city.pos[0]-len(city.name)*3, city.pos[1]))

        pygame.display.flip()   # Atualizamos a janela da interface.
