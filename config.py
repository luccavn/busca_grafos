#!/usr/bin/python
# -*- coding: UTF-8 -*-

from os import path

WINDOW_TITLE = 'Interface'          # Título da janela.
SCREEN_SIZE = (800, 600)            # Dimensões da janela.
FONT_SIZE = 12                      # Tamanho da fonte a ser utilizada.
DOT_RADIUS = 3                      # Raio dos pontos do mapa.
LINE_WIDTH = 1                      # Espessura das linhas de rota.
FONT_FAMILY = 'Consolas'            # Nome da fonte.
ARQ_MAPA = 'mapa_vale.png'          # Nome do arquivo do mapa.
ARQ_DISTANCIAS = 'distancias.csv'   # Nome do arquivo de distâncias.
ARQ_MUNICIPIOS = 'municipios.csv'   # Nome do arquivo de municípios.
METHOD_NAMES = ['Amplitude', 'Profundidade']    # Nome dos métodos de busca.

root_dir = path.dirname(path.abspath(__file__))                 # Diretório raiz do projeto.
map_path = path.join(root_dir, 'res/' + ARQ_MAPA)               # Diretório da imagem do mapa.
distances_path = path.join(root_dir, 'res/' + ARQ_DISTANCIAS)   # Diretório do arquivo de distâncias.
positions_path = path.join(root_dir, 'res/' + ARQ_MUNICIPIOS)   # Diretório do arquivo de posições.
