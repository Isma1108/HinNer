from __future__ import annotations
from antlr4 import *
from hmLexer import hmLexer
from hmParser import hmParser
from hmVisitor import hmVisitor
from graphviz import Graph
from dataclasses import dataclass
import streamlit as st
import pandas as pd

# Important:
# La symbolsTable del session state es per constants definides per l'usuari
# La localSymTable es per variables, per si hi ha dos values repetits assignar 

@dataclass
class Constant:
    ty: str

@dataclass
class Variable:
    ty: str

@dataclass
class Aplication:
    left: Type
    right: Type

Type = Constant | Variable | Aplication

# Given a type it parses it to a well-parenthised string
def showType(t: Type) -> str:
    match t:
        case Constant(ty):
            return ty
        case Variable(ty):
            return ty
        case Aplication(tyLeft, tyRight):
            return '(' + showType(tyLeft) + '->' + showType(tyRight) + ')'

class Empty:
    pass

@dataclass
class Node:
    val: str
    ty : Type
    left: Tree
    right: Tree

Tree = Node | Empty

localSymTable = {}
needToTraverse = False


class SymbolsTableVisitor(hmVisitor):
    def __init__(self, table):
        super().__init__()
        self.table = table

    def visitTypeDef(self, ctx:hmParser.TypeDefContext):
        leftType = ctx.leftType().getText()
        ty = self.visit(ctx.ty())
        self.table[leftType] = ty

    def visitSingleType(self, ctx:hmParser.SingleTypeContext):
        #if ctx.tipus().CNT():
            return Constant(ctx.tipus().getText())
        #else:
            #return Variable(ctx.tipus().getText())

    def visitMultiType(self, ctx:hmParser.MultiTypeContext):
        leftType = Constant(ctx.tipus().getText())
        #if ctx.tipus().VAR(): leftType = Variable(ctx.tipus().getText())
        rightType = self.visit(ctx.ty())
        return Aplication(leftType, rightType)


class SemanticTreeBuilder(hmVisitor):
    def __init__(self):
        super().__init__()
        self.charTy = 'a'

    def _getCharType(self, key):
        ty = Variable(self.charTy)

        if key in st.session_state.symTable:
            # Constante
            ty = st.session_state.symTable[key]
            return ty
        elif key in localSymTable:
            # Variable 
            ty = localSymTable[key]
            return ty
        else:
            # Variable
            localSymTable[key] = ty
            self.charTy = chr(ord(self.charTy) + 1)
            return ty

    #def visitExpr(self, ctx:hmParser.ExprContext):
        #if (ctx.expr()) return 
        #return self.visitChildren(ctx)


    def visitAplRec(self, ctx:hmParser.AplRecContext):
        ty = self.charTy;
        self.charTy = chr(ord(self.charTy) + 1)
        nodeApl = self.visit(ctx.aplicacio())
        nodeExpr = self.visit(ctx.expr())
        #tyLeft = nodeApl.ty
        #tyRight = nodeExpr.ty
        return Node('@', Variable(ty), nodeApl, nodeExpr)


    def visitAplOp(self, ctx:hmParser.AplOpContext):
        ty = self.charTy;
        self.charTy = chr(ord(self.charTy) + 1)
        nodeOp = self.visit(ctx.operador())
        nodeExpr = self.visit(ctx.expr())
        #tyLeft = nodeOp.ty
        #tyRight = nodeExpr.ty
        return Node('@', Variable(ty), nodeOp, nodeExpr)


    def visitAplAbs(self, ctx:hmParser.AplAbsContext):
        ty = self.charTy;
        self.charTy = chr(ord(self.charTy) + 1)
        nodeAbs = self.visit(ctx.abstraccio())
        nodeExpr = self.visit(ctx.expr())
        #tyLeft = nodeAbs.ty
        #tyRight = nodeExpr.ty
        return Node('@', Variable(ty), nodeAbs, nodeExpr)

    def visitAbstraccio(self, ctx:hmParser.AbstraccioContext):
        ty = self.charTy;
        self.charTy = chr(ord(self.charTy) + 1)
        nodeVar = self.visit(ctx.variable())
        nodeExpr = self.visit(ctx.expr())
        return Node('λ', Variable(ty), nodeVar, nodeExpr)

    def visitVariable(self, ctx:hmParser.VariableContext):
        value = ctx.getText()
        ty = self._getCharType(value)
        return Node(value, ty, Empty(), Empty())

    def visitNatural(self, ctx:hmParser.NaturalContext):
        value = ctx.getText()
        ty = self._getCharType(value)
        return Node(value, ty, Empty(), Empty())

    def visitOperador(self, ctx:hmParser.OperadorContext):
        value = ctx.getText()
        ty = self._getCharType(value)
        return Node(value, ty, Empty(), Empty())


def doTypeInference(t: Tree):
    global needToTraverse
    if isinstance(t.left, Node): doTypeInference(t.left)
    if isinstance(t.right, Node): doTypeInference(t.right)

    if t.val == '@' and isinstance(t.ty, Variable):
        #match t.left.ty.left:
            #case Variable(ty):
                #pass

            #case Constant(ty):
        t.right.ty = t.left.ty.left
        t.ty = t.left.ty.right

        if isinstance(t.right.ty, Constant):
            key = t.right.val
            localSymTable[key] = t.right.ty

    elif t.val == 'λ':
        t.ty = Aplication(t.left.ty, t.right.ty)

    if isinstance(t.ty, Variable) and t.val in localSymTable:
        if isinstance(localSymTable[t.val], Constant):
            t.ty = localSymTable[t.val]

    if isinstance(t.ty, Variable): needToTraverse = True



def displaySemanticTree(t: Tree):
    def _display(node, graph, parent_id = None):
        if isinstance(node, Node):
            node_id = str(id(node))
            graph.node(node_id, label=node.val + "\n" + showType(node.ty))

            if parent_id is not None:
                graph.edge(parent_id, node_id)

            # Recursive calls
            _display(node.left, graph, node_id)
            _display(node.right, graph, node_id)

    dot = Graph()
    _display(t, dot)

    st.graphviz_chart(dot)


def updateSymbolsTable(stream):
    lexer = hmLexer(stream)
    token_stream = CommonTokenStream(lexer)
    parser = hmParser(token_stream)
    tree = parser.root()

    if "symTable" not in st.session_state:
        st.session_state.symTable = {}

    symVisitor = SymbolsTableVisitor(st.session_state.symTable)

    # We visit the tree to update the symTable
    symVisitor.visit(tree)

    symTableToShow = {k: showType(v) for k, v in st.session_state.symTable.items()}


    df = pd.DataFrame.from_dict(symTableToShow, orient='index', columns=['Tipus'])
    st.dataframe(df, width=400)


def typeCheck(stream):
    global needToTraverse
    lexer = hmLexer(stream)
    token_stream = CommonTokenStream(lexer)
    parser = hmParser(token_stream)
    tree = parser.root()

    num_errors = parser.getNumberOfSyntaxErrors()
    st.write(f"{num_errors} error/s de sintaxi")

    if num_errors > 0 : return

    semantic_builder = SemanticTreeBuilder()
    semantic_tree = semantic_builder.visit(tree)
    displaySemanticTree(semantic_tree)

    doTypeInference(semantic_tree)
    doTypeInference(semantic_tree)

    #r = 1
    #while needToTraverse == True:
        #st.subheader(f"Inferència de tipus, recorregut {r}")
        #r += 1
        #displaySemanticTree(semantic_tree)
        #needToTraverse = False
        #doTypeInference(semantic_tree)

    st.subheader(f"Inferència de tipus:")
    displaySemanticTree(semantic_tree)




def main():
    tipusText = st.text_area("Tipus:")
    text = st.text_input("Expressió:")

    if (st.button("Fer")):
        st.subheader("Taula de símbols")
        updateSymbolsTable(InputStream(tipusText))
        st.subheader("Arbre semàntic")
        typeCheck(InputStream(text))


if __name__ == "__main__":
    main()

