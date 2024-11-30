import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import polars as pl
from PIL import Image
import plotly.express as px
import os
import re

import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

st.set_page_config(page_title="AXXONN APP", page_icon='smile', layout='wide')

def bigram_edges(tokens):
    edgetable = list(zip(tokens[:-1], tokens[1:]))
    return edgetable

def text2list(path_text):
  text_w2v = []
  for line in open(path_text): 
    if line!='\n':
        text_w2v.append(line)
  text = ''.join(text_w2v)
  text = re.split(r'\n', text)
  return text

def Token2Graph(edges_token):
    G = nx.MultiDiGraph()
    G.add_edges_from(edges_token)
    return G

def PlotGraph(tokens):
	edges_token = bigram_edges(tokens)
	# st.text(edges_token)

	G = Token2Graph(edges_token)

	fig, ax = plt.subplots(figsize=(8, 6))  # Tamaño ajustado
	pos = nx.spring_layout(G, seed=42)  # Disposición de nodos
	nx.draw(
		G,
		pos,
		with_labels=True,
		node_color='red',
		node_size=12,
		edge_color='gray',
		font_size=10,
		ax=ax
	)

	st.title("Speech Graph")
	st.pyplot(fig)

from vis_utils import Network as Net

keywords_nodes = []

viskargs = dict(
    height="1050px", 
    width="100%", 
    bgcolor="white", 
    keyword_color = "#FF0000",
    # node_color="#4682B4", 
    node_color="#FF0000", 
    font_color="#222222", 
    key_weight=1.2,
    font_size=30,
    node_size=18,
    edge_width=2,
    directed=True, 
    ifplot=False,
    heading="",
)

def read_html():
	html_file = "textgraph.html"  
	try:
		with open(html_file, "r", encoding="utf-8") as file:
			html_content = file.read()
		components.html(html_content, height=600, scrolling=True)
	except FileNotFoundError:
		st.error("El archivo HTML no se encontró. Verifica la ruta.")

def main():
	st.title('Directed Multi Graph from word co-ocurrence')
	tokens = text2list('sample.txt')
	
	# tokens = [ 'hombre', 'negocios', 'año', 'edad', 'volver', 'psiquiatra', 'semana', 'muerte', 'hijo',  'año', 'joven', 'enfrentado', 'depresión', 'abuso', 'sustancia', 'encontrado', 'rodeado', 'frasco', 'pastilla', 'vacio', 'nota', 'suicidar', 'incoherente',  'sentir', 'maltrecho', 'hijo', 'destrozado', 'vida', 'tener', 'sentido',  'semana', 'siguiente', 'ver', 'imagen', 'constante', 'hijo', 'obsesionar', 'pensar', 'impedido', 'abuso', 'sustancia', 'suicidio', 'preocupar', 'padre', 'dedicado', 'tiempo', 'carrera', 'hijo', 'sentir', 'constantemente', 'triste', 'retirar', 'vida', 'social', 'habitual', 'incapaz', 'concentrar', 'trabajo', 'tomar', 'vasos', 'vino', 'semana', 'beber', 'medio', 'botella', 'venir', 'noches', 'momento', 'psiquiatra', 'pleno', 'duelo', 'reacción', 'normal', 'concertar', 'cita', 'terapiar', 'apoyo', 'evaluar', 'evolución', 'clínico', 'seguir', 'ver', 'psiquiatra', 'semanalmente', 'sexto', 'semana', 'suicidio', 'síntoma', 'empeorado', 'lugar', 'pensar', 'forma', 'distinto', 'empezar', 'angustiar', 'idea', 'deber', 'haber', 'morir', 'hijo', 'seguir', 'costar', 'trabajo', 'dormir', 'tender', 'despertar', 'madrugada', 'mirar', 'techo', 'sentir', 'agobiado', 'cansancio', 'tristezar', 'sentimiento', 'inutilidad', 'síntoma', 'mejorar', 'notar', 'pérdida', 'persistente', 'inusual', 'confianza', 'interés', 'sexual', 'entusiasmo', 'preguntar', 'psiquiatra', 'seguir', 'duelo', 'normal', 'depresión', 'antecedent', 'episodio', 'depresivo', 'mayor', 'anterior', 'mejorar', 'psicoterapio', 'medicación', 'antidepresivo', 'sufrido', 'episodio', 'importante', 'tanto', 'año', 'antecedente', 'abuso', 'alcohol', 'sustancia', 'padre', 'depresivo', 'tratado', 'suicidado', 'anteriormente', 'familia']
	
	with st.container():
		edges_token = bigram_edges(tokens)
		G = Token2Graph(edges_token)
		nt = Net(keywords_nodes = keywords_nodes,**viskargs)
		nt.from_nx(G)
		nt.options.edges.color = "#000000"
		nt.save_graph("textgraph.html")
		text = ' '.join(tokens)
		read_html()
		st.write(text)

	# with st.container():
	# 	st.write('---')
	# 	PlotGraph(tokens)
	# 	text = ' '.join(tokens)
	# 	st.write(text)

if __name__ == '__main__':
	main()