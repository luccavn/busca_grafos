#!/usr/bin/python
# -*- coding: UTF-8 -*-

from os import path

WINDOW_TITLE = 'Interface'          # Título da janela.
SCREEN_SIZE = (800, 600)            # Dimensões da janela.
FONT_SIZE = 14                      # Tamanho da fonte a ser utilizada.
DOT_RADIUS = 4                      # Raio dos pontos do mapa.
LINE_WIDTH = 2                      # Espessura das linhas de rota.
FONT_FAMILY = 'Consolas'            # Nome da fonte.
ARQ_MAPA = 'mapa_vale.png'          # Nome do arquivo do mapa.
ARQ_DISTANCIAS = 'distancias.csv'   # Nome do arquivo de distâncias.
ARQ_MUNICIPIOS = 'municipios.csv'   # Nome do arquivo de municípios.

METHOD_NAMES = ['Amplitude',
                'Profundidade',
                'Profundidade Limitada',
                'Profundidade Interativa',
                'Bi-direcional']

# Diretório raiz do projeto:
root_dir = path.dirname(path.abspath(__file__))
# Diretório da imagem do mapa:
map_path = path.join(root_dir, 'res/' + ARQ_MAPA)
# Diretório do arquivo de distâncias:
distances_path = path.join(root_dir, 'res/' + ARQ_DISTANCIAS)
# Diretório do arquivo de posições:
positions_path = path.join(root_dir, 'res/' + ARQ_MUNICIPIOS)
