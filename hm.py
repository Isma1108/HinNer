from __future__ import annotations
from antlr4 import *
from hmLexer import hmLexer
from hmParser import hmParser
from hmVisitor import hmVisitor
from graphviz import Graph
from dataclasses import dataclass
import streamlit as st


class Empty:
    pass

@dataclass
class Node:
    val: str
    left: Tree
    right: Tree

Tree = Node | Empty


class SemanticTreeBuilder(hmVisitor):

    def visitAplRec(self, ctx:hmParser.AplRecContext):
        nodeApl = self.visit(ctx.aplicacio())
        nodeExpr = self.visit(ctx.expr())
        return Node('@', nodeApl, nodeExpr)


    def visitAplOp(self, ctx:hmParser.AplOpContext):
        nodeOp = Node(ctx.OP().getText(), Empty(), Empty())
        nodeExpr = self.visit(ctx.expr())
        return Node('@', nodeOp, nodeExpr)


    def visitAplAbs(self, ctx:hmParser.AplAbsContext):
        nodeAbs = self.visit(ctx.abstraccio())
        nodeExpr = self.visit(ctx.expr())
        return Node('@', nodeAbs, nodeExpr)

    def visitAbstraccio(self, ctx:hmParser.AbstraccioContext):
        nodeVar = self.visit(ctx.variable())
        nodeExpr = self.visit(ctx.expr())
        return Node('λ', nodeVar, nodeExpr)

    def visitVariable(self, ctx:hmParser.VariableContext):
        return Node(ctx.getText(), Empty(), Empty())

    def visitNatural(self, ctx:hmParser.NaturalContext):
        return Node(ctx.getText(), Empty(), Empty())




def displaySemanticTree(t: Tree):
    def _display(node, graph, parent_id = None):
        if isinstance(node, Node):
            node_id = str(id(node))
            graph.node(node_id, label=node.val)

            if parent_id is not None:
                graph.edge(parent_id, node_id)

            # Recursive calls
            _display(node.left, graph, node_id)
            _display(node.right, graph, node_id)

    dot = Graph()
    _display(t, dot)

    st.graphviz_chart(dot)


def typeCheck(stream):
    lexer = hmLexer(stream)
    token_stream = CommonTokenStream(lexer)
    parser = hmParser(token_stream)
    tree = parser.root()

    num_errors = parser.getNumberOfSyntaxErrors()
    st.write(f"{num_errors} error/s de sintaxi")

    semantic_builder = SemanticTreeBuilder()
    semantic_tree = semantic_builder.visit(tree)
    displaySemanticTree(semantic_tree)


def main():
    text = st.text_input("Expressió:")
    if (st.button("Fer")):
        typeCheck(InputStream(text))


if __name__ == "__main__":
    main()
