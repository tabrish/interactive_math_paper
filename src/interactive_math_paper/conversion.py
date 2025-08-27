from typing import Optional, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from TexSoup import TexSoup, TexNode
from TexSoup.data import TexEnv, TexCmd, Token, TexExpr, TexArgs


def lex_tex_source(tex: str) -> TexNode:
    return TexSoup(tex)


class HtmlNode(ABC):
    def __init__(self):
        self.args = []
        self.children = []

    def add_argument(self, arg: "HtmlNode"):
        self.args.append(arg)

    def add_child(self, child: "HtmlNode"):
        self.children.append(child)

    @abstractmethod
    def to_html(self) -> str:
        pass


class TexContext:
    pass


# todo i think this class makes no sense the way it is currently
class Consumed(Enum):
    no = 0
    yes = 1
    also_children = 2


@dataclass
class VisitResult:
    node: Optional[HtmlNode]
    consumed: Consumed

    @staticmethod
    def pass_by() -> "VisitResult":
        return VisitResult(node=None, consumed=Consumed.no)

    @staticmethod
    def use(node: HtmlNode, parse_children: bool = True) -> "VisitResult":
        return VisitResult(
            node=node,
            consumed=Consumed.yes if parse_children else Consumed.also_children,
        )


class TexVisitor(ABC):
    @abstractmethod
    def visit_env(self, env: TexEnv, context: TexContext) -> VisitResult:
        pass

    @abstractmethod
    def visit_cmd(self, cmd: TexCmd, context: TexContext) -> VisitResult:
        pass

    @abstractmethod
    def visit_token(self, token: Token, context: TexContext) -> VisitResult:
        pass


def convert(
    node: Union[TexNode, TexEnv, TexCmd, Token, TexExpr], visitor: TexVisitor
) -> HtmlNode:
    # todo make iterative
    if isinstance(node, TexNode):
        return convert(node.expr, visitor)
    if isinstance(node, TexEnv):
        result = visitor.visit_env(node, TexContext())
        if result.consumed == Consumed.also_children:
            return result.node
        html_object = result.node
        assert html_object
        args = node.args  # todo add test for the weird behaviour of contents
        # todo maybe add feature request
        for arg in node.args:
            html_object.add_argument(convert(arg, visitor))
        node.args = TexArgs()
        for child in node.contents:
            html_object.add_child(convert(child, visitor))
        node.args = args
        return html_object
    if isinstance(node, TexCmd):
        result = visitor.visit_cmd(node, TexContext())
        if result.consumed == Consumed.also_children:
            return result.node
        html_object = result.node
        assert html_object
        args = node.args
        for arg in node.args:
            html_object.add_argument(convert(arg, visitor))
        node.args = TexArgs()
        for child in node.contents:
            html_object.add_child(convert(child, visitor))
        node.args = args
        return html_object
    if isinstance(node, Token):
        result = visitor.visit_token(node, TexContext())
        html_object = result.node
        assert html_object
        return html_object
    raise ValueError(f"unknown object of type {type(node)}")
