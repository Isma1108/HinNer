from __future__ import annotations
from antlr4 import *
from hmLexer import hmLexer
from hmParser import hmParser
from hmVisitor import hmVisitor
from graphviz import Graph
from dataclasses import dataclass
import streamlit as st
import pandas as pd


@dataclass
class Constant:
    ty: str

@dataclass
class Variable:
    ty: str

@dataclass
class Application:
    left: Type
    right: Type

Type = Constant | Variable | Application

# Given a type it parses it to a well-parenthised string
def showType(t: Type) -> str:
    match t:
        case Constant(ty):
            return ty
        case Variable(ty):
            return ty
        case Application(tyLeft, tyRight):
            return '(' + showType(tyLeft) + '->' + showType(tyRight) + ')'

class Empty:
    pass

@dataclass
class Node:
    val: str
    nodeTy : Type
    left: Tree
    right: Tree

Tree = Node | Empty

localSymTable = {}
varTypes = {}
needToTraverse = False


class SymbolsTableVisitor(hmVisitor):
    def visitTypeDef(self, ctx:hmParser.TypeDefContext):
        leftType = ctx.leftType().getText()
        ty = self.visit(ctx.ty())
        st.session_state.symTable[leftType] = ty
        st.session_state.symTableToShow[leftType] = showType(ty)

    def visitSingleType(self, ctx:hmParser.SingleTypeContext):
        if ctx.tipus().CNT():
            return Constant(ctx.tipus().getText())
        else:
            return Variable(ctx.tipus().getText())

    def visitMultiType(self, ctx:hmParser.MultiTypeContext):
        leftType = Constant(ctx.tipus().getText())
        if ctx.tipus().VAR(): leftType = Variable(ctx.tipus().getText())
        rightType = self.visit(ctx.ty())
        return Application(leftType, rightType)


class SemanticTreeBuilder(hmVisitor):
    def __init__(self):
        super().__init__()
        self.charTy = 'a'

    def _getSelfType(self, key):
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

    def visitAplRec(self, ctx:hmParser.AplRecContext):
        ty = self.charTy;
        self.charTy = chr(ord(self.charTy) + 1)
        nodeApl = self.visit(ctx.aplicacio())
        nodeExpr = self.visit(ctx.expr())
        return Node('@', Variable(ty), nodeApl, nodeExpr)


    def visitAplOp(self, ctx:hmParser.AplOpContext):
        ty = self.charTy;
        self.charTy = chr(ord(self.charTy) + 1)
        nodeOp = self.visit(ctx.operador())
        nodeExpr = self.visit(ctx.expr())
        return Node('@', Variable(ty), nodeOp, nodeExpr)

    def visitAplAbs(self, ctx:hmParser.AplAbsContext):
        ty = self.charTy;
        self.charTy = chr(ord(self.charTy) + 1)
        nodeAbs = self.visit(ctx.abstraccio())
        nodeExpr = self.visit(ctx.expr())
        return Node('@', Variable(ty), nodeAbs, nodeExpr)

    def visitAbstraccio(self, ctx:hmParser.AbstraccioContext):
        ty = self.charTy;
        self.charTy = chr(ord(self.charTy) + 1)
        nodeVar = self.visit(ctx.variable())
        nodeExpr = self.visit(ctx.expr())
        return Node('λ', Variable(ty), nodeVar, nodeExpr)

    def visitVariable(self, ctx:hmParser.VariableContext):
        value = ctx.getText()
        ty = self._getSelfType(value)
        return Node(value, ty, Empty(), Empty())

    def visitNatural(self, ctx:hmParser.NaturalContext):
        value = ctx.getText()
        ty = self._getSelfType(value)
        return Node(value, ty, Empty(), Empty())

    def visitOperador(self, ctx:hmParser.OperadorContext):
        value = ctx.getText()
        ty = self._getSelfType(value)
        return Node(value, ty, Empty(), Empty())

def aplUnification(nodeTy: Type, tyLeft: Type, tyRight: Type):
    match tyLeft:
        case Variable(var):
            tyLeft = Application(tyRight, nodeTy)
            varTypes[var] = tyLeft
        case Application(tl, tr):
            st.write("arroba")
            if isinstance(tyRight, Constant):
                if tl != tyRight:
                    st.write(f"Type error: {tl.ty} vs {tyRight.ty}")
                    return False
                varTypes[nodeTy.ty] = tr
                nodeTy = tr
            else:
                varTypes[nodeTy.ty] = tr
                nodeTy = tr
                varTypes[tyRight.ty] = tl
                tyRight = tl

    return True


def updateType(t:Type):
    if isinstance(t, Constant): return t
    if isinstance(t, Variable):
        if t.ty in varTypes: return varTypes[t.ty]
        return t
    if isinstance(t, Application):
        tl = updateType(t.left)
        tr = updateType(t.right)
        return Application(tl, tr)

def doTypeInference(t: Tree):
    global needToTraverse
    if isinstance(t.left, Node):
        allCorrect = doTypeInference(t.left)
        if not allCorrect: return False

    if isinstance(t.right, Node):
        allCorrect = doTypeInference(t.right)
        if not allCorrect: return False

    if t.val == '@':
        leftTy = t.left.nodeTy
        rightTy = t.right.nodeTy

        leftTy = updateType(leftTy)
        rightTy = updateType(rightTy)

        match leftTy:
            case Variable(var):
                if var in varTypes: leftTy = varTypes[var]
                else:
                    leftTy = Application(rightTy, t.nodeTy)
                    varTypes[var] = leftTy
                    needToTraverse = True

            case Application(tl, tr):
                if isinstance(rightTy, Constant):
                    if isinstance(tl, Constant):
                        if tl != rightTy:
                            st.write(f"<h3 style='color: red;'>Type error: {tl.ty} vs {rightTy.ty}</h3>", unsafe_allow_html=True)
                            return False
                    else:
                        varTypes[tl.ty] = rightTy
                        leftTy = Application(rightTy, tr)
                        needToTraverse = True

                elif tl != rightTy:
                    varTypes[rightTy.ty] = tl
                    rightTy = tl
                    needToTraverse = True

                if isinstance(t.nodeTy, Application) and isinstance(tr, Variable):
                    varTypes[tr.ty] = t.nodeTy
                    leftTy = Application(tl, t.nodeTy)
                    needToTraverse = True

                elif isinstance(t.nodeTy, Variable) and tr != t.nodeTy:
                    varTypes[t.nodeTy.ty] = tr
                    t.nodeTy = tr
                    needToTraverse = True

        t.left.nodeTy = leftTy
        t.right.nodeTy = rightTy

    elif t.val == 'λ':
        leftTy = updateType(t.left.nodeTy)
        rightTy = updateType(t.right.nodeTy)
        t.left.nodeTy = leftTy
        t.right.nodeTy = rightTy

        if isinstance(t.nodeTy, Variable):
            varTypes[t.nodeTy.ty] = Application(leftTy, rightTy)
            needToTraverse = True
        t.nodeTy = Application(leftTy, rightTy)


    return True



def displaySemanticTree(t: Tree):
    def _display(node, graph, parent_id = None):
        if isinstance(node, Node):
            node_id = str(id(node))
            value = node.val
            if value in st.session_state.symTableToShow:
                graph.node(node_id, label=value + "\n" + st.session_state.symTableToShow[value])
            else:
                graph.node(node_id, label=value + "\n" + showType(node.nodeTy))


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
        st.session_state.symTableToShow = {}

    symVisitor = SymbolsTableVisitor()

    # We visit the tree to update the symTable
    symVisitor.visit(tree)

    df = pd.DataFrame.from_dict(st.session_state.symTableToShow, orient='index', columns=['Tipus'])
    st.dataframe(df, width=400)


def typeCheck(stream):
    global needToTraverse
    lexer = hmLexer(stream)
    token_stream = CommonTokenStream(lexer)
    parser = hmParser(token_stream)
    tree = parser.root()

    num_errors = parser.getNumberOfSyntaxErrors()

    if num_errors > 0 :
        st.write(f"<h3 style='color: red;'>{num_errors} error/s de sintaxi</h3>", unsafe_allow_html=True)
        return
    else: st.write(f"{num_errors} error/s de sintaxi")


    semantic_builder = SemanticTreeBuilder()
    semantic_tree = semantic_builder.visit(tree)
    displaySemanticTree(semantic_tree)

    st.subheader(f"Inferència de tipus:")

    travels = 1
    allCorrect = doTypeInference(semantic_tree)

    while allCorrect and needToTraverse and travels <= 10:
        needToTraverse = False
        allCorrect = doTypeInference(semantic_tree)
        travels += 1

    if allCorrect:
        st.write(f"Inferència obtinguda amb {travels-1} recorregut/s")
        displaySemanticTree(semantic_tree)
        varTypesToShow = {k: showType(v) for k, v in varTypes.items()}
        st.subheader("Taula de variables")
        st.table(pd.DataFrame.from_dict(varTypesToShow, orient='index', columns=['Tipus']))



def main():
    global localSymTable
    st.title("HinNer Type Analyzer")
    tipusText = st.text_area("Tipus:")
    text = st.text_input("Expressió:")

    if (st.button("Fer")):
        localSymTable = {}
        varTypes = {}
        st.subheader("Taula de símbols")
        updateSymbolsTable(InputStream(tipusText))
        if (text.strip() != ""):
            st.subheader("Arbre semàntic")
            typeCheck(InputStream(text))

if __name__ == "__main__":
    main()
