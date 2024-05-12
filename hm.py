import streamlit as st
import pandas as pd
from antlr4 import *
from hmLexer import hmLexer
from hmParser import hmParser

from graphviz import Graph

#input_stream = InputStream(input('? ')) #-> una linia
#input_stream = StdinStream()
#lexer = hmLexer(input_stream)
#token_stream = CommonTokenStream(lexer)
#parser = hmParser(token_stream)
#tree = parser.root()

#print(parser.getNumberOfSyntaxErrors(), 'errors de sintaxi.')
#print(tree.toStringTree(recog=parser))

def generate_dot_tree():
    dot = Graph()
    dot.node('A', 'A', shape='circle')
    dot.node('B', 'B', shape='circle')
    dot.node('C', 'C', shape='circle')
    dot.edge('A', 'B')
    dot.edge('A', 'C')
    return dot

# Generar el árbol DOT

text = st.text_input("Expressió:")

if (st.button("Fer")):
    lexer = hmLexer(InputStream(text))
    token_stream = CommonTokenStream(lexer)
    parser = hmParser(token_stream)
    tree = parser.root()
    num_errors = parser.getNumberOfSyntaxErrors()
    st.write(f"{num_errors} error/s de sintaxi")
    
    dot_tree = generate_dot_tree()

    # Mostrar el árbol en Streamlit
    st.graphviz_chart(dot_tree.source)



