#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pygame
import pandas as pd
import queue as Q
from pygame.locals import Rect
from lib.ordered_set import OrderedSet
from collections import deque

##############
# CONSTANTES #
##############

COLOR_BLACK = (0, 0, 0)         # Valores RGB da cor preta.
COLOR_GREEN = (0, 255, 0)       # Valores RGB da cor verde.
COLOR_RED = (255, 0, 0)         # Valores RGB da cor vermelha.
COLOR_WHITE = (255, 255, 255)   # Valores RGB da cor branca.
MOUSE_LEFT = 1                  # Representa clique esquerdo do mouse.
MOUSE_RIGHT = 3                 # Representa clique direito do mouse.

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

# Carregamos e redimensionamos a imagem do mapa que será utilizada como imagem
# de fundo da interface:
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
        # Fazemos a leitura das distâncias entre os municípios, gerando uma
        # tabela de 3 colunas:
        data = pd.read_csv(path, sep=',', encoding='utf-8')
        # Convertemos a tabela em uma matriz:
        data_matrix = data.values
        # Criamos um dicionário onde as chaves serão o nome dos municípios da
        # primeira coluna e todas elas terão uma lista vazia como valor.
        # Utilizamos listas do tipo set() pois elas possuem um acesso mais
        # rápido e não aceitam objetos repetidos:
        for row in data_matrix:
            from_city = row[0]
            self[from_city] = list()
        # Agora adicionamos os vizinhos desses municípios, que são os
        # municípios da segunda coluna. Note que por enquanto não estamos
        # utilizando a coluna de distâncias:
        for from_city, to_city, distance in data_matrix:
            self[from_city].append([to_city, distance])


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
            if neighbour[0] == goal:
                return (visited, path + [goal])
            else:
                if neighbour[0] not in visited:
                    visited.add(neighbour[0])
                    queue.append((neighbour[0], path + [neighbour[0]]))


##########################
# MÉTODO DE PROFUNDIDADE #
##########################

def dfs(graph, origin, goal):
    """ Inicia no vértice origin, voltando até encontrar o vértice goal.

    Retorna uma tupla com os vértices visitados e o caminho mais curto em
    forma de lista.

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
            if neighbour[0] == goal:
                return (visited, path + [goal])
            else:
                if neighbour[0] not in visited:
                    visited.add(neighbour[0])
                    stack.append((neighbour[0], path + [neighbour[0]]))


###################################
# MÉTODO DE PROFUNDIDADE LIMITADA #
###################################

def lim_dfs(graph, origin, goal, lim):
    """ Inicia no vértice origin, voltando até encontrar o vértice goal.

    Muda o sentido da busca caso alcançe o limite de passos estabelecido.
    Retorna uma tupla com os vértices visitados e o caminho mais curto em
    forma de lista.

    Parâmetros:
    - origin : vértice inicial
    - goal : vértice objetivo
    - lim : limite de passos em um determinado sentido
    """
    stack = [(origin, [origin])]
    visited = OrderedSet()
    depth = 0
    while stack:
        if depth < lim:
            vertex, path = stack.pop()
            visited.add(vertex)
            depth += 1
            for neighbour in graph[vertex]:
                if neighbour[0] == goal:
                    return (visited, path + [goal])
                else:
                    if neighbour[0] not in visited:
                        visited.add(neighbour[0])
                        stack.append((neighbour[0], path + [neighbour[0]]))
        else:
            return (visited, None)
    return (visited, None)


####################################
# MÉTODO DE PROFUNDIDADE ITERATIVA #
####################################

def deepening_dfs(graph, origin, goal, lim):
    """ Inicia no vértice origin, voltando até encontrar o vértice goal.

    Muda o sentido da busca caso alcançe o limite de passos estabelecido.
    Aumenta o limite de passos caso o objetivo não seja encontrado com o
    limite estabelecido.
    Retorna uma tupla com os vértices visitados e o caminho mais curto em
    forma de lista.

    Parâmetros:
    - origin : vértice inicial
    - goal : vértice objetivo
    - lim : limite de passos em um determinado sentido
    """
    stack = [(origin, [origin])]
    visited = OrderedSet()
    depth = 0
    while stack:
        if depth < lim:
            vertex, path = stack.pop()
            visited.add(vertex)
            depth += 1
            for neighbour in graph[vertex]:
                if neighbour[0] == goal:
                    return (visited, path + [goal])
                else:
                    if neighbour[0] not in visited:
                        visited.add(neighbour[0])
                        stack.append((neighbour[0], path + [neighbour[0]]))
        else:
            if lim < len(graph)-1:
                return deepening_dfs(graph, origin, goal, lim+1)
            else:
                return (visited, None)
    return (visited, None)


#####################################
# MÉTODO DE AMPLITUDE BI-DIRECIONAL #
#####################################

def bidir_bfs(graph, origin, goal):
    if origin == goal:
        return [origin]

    path_dict = {origin: [origin], goal: [goal]} # Dicionário para guardar o caminho.
    visited = set()

    while len(path_dict) > 0:
        active_vertices = list(path_dict.keys()) # Cópia do dicionário.
        for vertex in active_vertices:
            path = path_dict[vertex] # Caminho atual.
            origin = path[0]
            current_neighbours = set([n[0] for n in graph[vertex]]) - visited # Vizinhos disponíveis.
            # Verificamos se houve alguma intersecção entre os caminhos:
            if len(current_neighbours.intersection(active_vertices)) > 0:
                for meeting_vertex in current_neighbours.intersection(active_vertices):
                    # Verificamos se os caminhos possuem origens distintas,
                    # se sim então temos um resultado:
                    if origin != path_dict[meeting_vertex][0]:
                        # Invertemos a ordem de um dos caminhos:
                        path_dict[meeting_vertex].reverse()
                        # Retornamos a soma dos caminhos:
                        return (visited, path_dict[vertex] + path_dict[meeting_vertex])

            # Continuamos com a busca:
            if len(set(current_neighbours) - visited - set(active_vertices)) == 0:
                # Caso não exista mais vizinhos, removemos o caminho da lista:
                path_dict.pop(vertex, None)
                visited.add(vertex)
            else:
                # Caso contrário buscamos por novos vizinhos:
                for neighbour_vertex in current_neighbours - visited - set(active_vertices):
                    path_dict[neighbour_vertex] = path + [neighbour_vertex]
                    active_vertices.append(neighbour_vertex)
                path_dict.pop(vertex, None)
                visited.add(vertex)
    return None


############################
# MÉTODO DE CUSTO UNIFORME #
############################

def uniform_cost_search(graph, origin, goal):
    queue = Q.PriorityQueue()
    queue.put((0, [origin]))
    while not queue.empty():
        node = queue.get()
        current = node[1][len(node[1]) - 1]
        if goal in node[1]:
            return ([node[0]], node[1])
            break
        cost = node[0]
        for neighbor in graph[current]:
            temp = node[1][:]
            temp.append(neighbor[0])
            queue.put((cost + neighbour[1], temp))
    return ([], None)


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
            city_object = get_city_byname(map_cities, city)
            neighbour_object = get_city_byname(map_cities, neighbour[0])
            # Adicionamos o vizinho ao município de origem:
            city_object.add_neighbour(neighbour_object)

    map_edges = set()   # Lista de arestas.

    # Para cada vértice do grafo pegamos o nome e a lista
    # de vizinhos e buscamos pelo objeto do tipo city
    # para que possamos fazer as ligações:
    for city, neighbours in graph.items():
        for neighbour in neighbours:
            # Verificamos se a aresta desses municípios já existe:
            if get_edge(map_edges, city, neighbour[0]) is None:
                city_object = get_city_byname(map_cities, city)
                neighbour_object = get_city_byname(map_cities, neighbour[0])
                # Criamos a aresta e a adicionamos na lista de arestas:
                new_edge = Edge(origin=city, orig_pos=city_object.pos,
                                destiny=neighbour[0], dest_pos=neighbour_object.pos)
                map_edges.add(new_edge)

    # Variáveis auxiliares:
    method_index = 0        # Índice do método de busca selecionado.
    found_path = None       # Caminho realizado pelo algoritmo.
    visited_cities = None   # Municípios visitados pelo algoritmo.
    from_city = None        # Município de origem.
    to_city = None          # Município de destino.
    draw_edges = False      # Determina se as arestas serão desenhadas.
    exit_ui = False         # Determina se o programa irá encerrar.
    dfs_lim = 7             # Limite de passos dos algoritmos que possuem limite.

    while not exit_ui:
        pygame.event.pump()  # Atualizamos os eventos do pygame.

        # Atualizamos a posição do ponteiro do mouse.
        mouse_pos = pygame.mouse.get_pos()

        # Atualizamos o retângulo de colisão do ponteiro do mouse:
        left, top = (mouse_pos[0], mouse_pos[1])    # Posicionamento.
        width, height = (Config.DOT_RADIUS, Config.DOT_RADIUS)  # Dimensões.
        mouse_rect = Rect((left, top), (width, height))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_ui = True  # Finaliza o programa.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit_ui = True
                elif event.key == pygame.K_SPACE:
                    # Alternamos entre mostrar ou não as arestas na interface.
                    draw_edges = True if draw_edges is False else False
                elif event.key == pygame.K_LEFT:
                    # Alterna entre os métodos de busca.
                    method_index = method_index-1 if method_index > 0 \
                        else len(Config.METHOD_NAMES)-1
                elif event.key == pygame.K_RIGHT:
                    method_index = method_index+1 if method_index < \
                        len(Config.METHOD_NAMES)-1 else 0
                elif event.key == pygame.K_UP:
                    dfs_lim += 1
                elif event.key == pygame.K_DOWN:
                    dfs_lim -= 1 if dfs_lim > 0 else 0
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
                    if method_index == 0:
                        # Resultado do algoritmo de amplitude:
                        result = bfs(graph, from_city.name, to_city.name)
                    elif method_index == 1:
                        # Resultado do algoritmo de profundidade:
                        result = dfs(graph, from_city.name, to_city.name)
                    elif method_index == 2:
                        # Resultado do algoritmo de profundidade limitada:
                        result = lim_dfs(graph, from_city.name,
                                         to_city.name, dfs_lim)
                    elif method_index == 3:
                        result = deepening_dfs(
                            graph, from_city.name, to_city.name, dfs_lim)
                    elif method_index == 4:
                        result = bidir_bfs(graph, from_city.name, to_city.name)
                    else:
                        result = uniform_cost_search(graph, from_city.name, to_city.name)
                    # Municípios que foram visitados pelo algoritmo.
                    visited_cities = [city for city in result[0]]
                    # Caminho mais curto da origem até o destino.
                    found_path = result[1]

                    # Imprimimos as informações no console:
                    if found_path is not None:
                        info_text = '\n\n# Rota: {} ate {}.\n\nCaminho encontrado: {} passos -> {}.\n\nMunicípios visitados: {} -> {}'
                        print(info_text.format(from_city.name, to_city.name, len(
                            found_path)-1, found_path, len(visited_cities), visited_cities))
                    else:
                        info_text = '\n\n# Rota: {} ate {}.\n\nO objetivo nao foi encontrado dentro do limite estabelecido.\n\nMunicípios visitados: {} -> {}'
                        print(info_text.format(from_city.name, to_city.name, len(
                            visited_cities), visited_cities))

        # Preenchemos o fundo da tela com uma cor específica.
        screen.fill(COLOR_WHITE)
        # Desenhamos a imagem do mapa na tela.
        screen.blit(map_image_scaled, (0, 0))

        # Renderizamos as arestas por pares de vértices:
        for edge in map_edges:
            # Verificamos se a origem e o destino da aresta coincide com o
            # caminho resultante:
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
                from_city.name, to_city.name, len(found_path)-1 if found_path is not None else len(visited_cities))
            # Criamos uma superfície renderizável:
            text_surface = title_font.render(info_text, True, COLOR_BLACK)
            # Adaptamos a posição do texto de acordo com o nome do município:
            text_position = (
                Config.SCREEN_SIZE[0]/4 - 9 * len(from_city.name) + len(to_city.name), 0)
            # Renderizamos a superfície do texto:
            screen.blit(text_surface, text_position)

        # Desenhamos o texto do método selecionado:
        method_text = 'Método de busca: ' + \
            Config.METHOD_NAMES[method_index] + \
            '. Limite de passos: %s' % dfs_lim
        method_surface = title_font.render(method_text, True, COLOR_BLACK)
        method_position = (Config.SCREEN_SIZE[0]/4, Config.SCREEN_SIZE[1]-24)
        screen.blit(method_surface, method_position)

        # Definimos as cores de destaque e renderizamos os municípios no mapa:
        for city in map_cities:
            paint_color = COLOR_BLACK  # Cor padrão (município sem destaque).

            # Definimos a cor verde para os municípios de origem e destino
            # e definimos a cor branca para os municípios que fazem parte da
            # rota:
            if (found_path is not None) and (city.name == from_city or city.name == to_city):
                paint_color = COLOR_GREEN

            # Definimos a cor verde para os municípios nos quais o ponteiro
            # colide:
            pointer_collides = city.rect.colliderect(mouse_rect)
            if pointer_collides:
                paint_color = COLOR_GREEN

            # Desenhamos o ponto e o nome dos municípios no mapa:
            pygame.draw.circle(screen, paint_color,
                               city.pos, Config.DOT_RADIUS)
            name_text = medium_font.render(city.name, True, paint_color)
            screen.blit(name_text, (city.pos[0]-len(city.name)*3, city.pos[1]))

        pygame.display.flip()   # Atualizamos a janela da interface.
