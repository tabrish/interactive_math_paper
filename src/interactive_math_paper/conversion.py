from typing import Optional, Union, override, TypeVar, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from TexSoup import TexSoup, TexNode
from TexSoup.data import TexEnv, TexCmd, Token, TexExpr, TexArgs


def lex_tex_source(tex: str) -> TexNode:
    return TexSoup(tex)


class HtmlNode:
    def __init__(self):
        self.args = []
        self.children = []
        self.parent = None

    def add_argument(self, arg: "HtmlNode"):
        self.args.append(arg)
        if arg.parent is not None:
            arg.parent.args.remove(arg)
        arg.parent = self

    def add_child(self, child: "HtmlNode"):
        self.children.append(child)
        if child.parent is not None:
            child.parent.children.remove(child)
        child.parent = self

    def children_to_html(self) -> str:
        html = ""
        for child in self.children:
            html += child.to_html()
        return html

    def to_html(self) -> str:
        return ""

    def global_css(self) -> str:
        return ""

    def global_js(self) -> str:
        return ""


T = TypeVar("T")


class TexContext:
    def __init__(self, nodes: list[HtmlNode], parents: list[HtmlNode]):
        self.nodes = nodes
        self.parents = parents

    def copy(self) -> "TexContext":
        return TexContext(self.nodes.copy(), self.parents.copy())

    def surrounding(self, type: Type[T]) -> Optional[T]:
        for node in self.parents[::-1]:
            if isinstance(node, type):
                return node
        return None

    def all(self, type: Type[T]) -> list[T]:
        output = []
        for node in self.nodes[::-1]:
            if isinstance(node, type):
                output.append(node)
        return output

    def first(self, type: Type[T]) -> Optional[T]:
        for node in self.nodes[::-1]:
            if isinstance(node, type):
                return node
        return None

    def stack_trace(self):
        print("stack trace")
        print(f"{self.nodes[::-1]}")


class EmptyNode(HtmlNode):
    @override
    def to_html(self):
        return self.children_to_html()


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

    @staticmethod
    def hidden(parse_children: bool = True) -> "VisitResult":
        return VisitResult(
            node=EmptyNode(),
            consumed=Consumed.yes if parse_children else Consumed.also_children,
        )


class TexVisitor(ABC):
    visitors = []

    def __init__(self):
        TexVisitor.visitors.append(self)

    @abstractmethod
    def visit_env(self, env: TexEnv, context: TexContext) -> VisitResult:
        pass

    @abstractmethod
    def visit_cmd(self, cmd: TexCmd, context: TexContext) -> VisitResult:
        pass

    @abstractmethod
    def visit_token(self, token: Token, context: TexContext) -> VisitResult:
        pass

    def global_css(self) -> str:
        return ""

    def global_js(self) -> str:
        return ""


@dataclass
class ReaderResult:
    node: HtmlNode
    consume_children: bool


class DocumentNode(HtmlNode):
    @override
    def to_html(self) -> str:
        return ""


class TexReader:
    def __init__(
        self,
        tex_visitors: list[TexVisitor],
        fallback: TexVisitor,
        packages: dict[str, TexVisitor],
    ):
        self.chain = [fallback] + tex_visitors
        self.packages = packages

    def parse_packages(self, node):
        if not isinstance(node, TexCmd):
            return
        if node.name != "usepackage":
            return
        for arg in node.args:
            for key, value in self.packages.items():
                if key in str(arg):
                    self.chain.append(value)

    def convert(self, node: Union[TexExpr, Token], context: TexContext) -> ReaderResult:
        self.parse_packages(node)
        for visitor in self.chain[::-1]:
            if isinstance(node, TexEnv):
                result = visitor.visit_env(node, context)
            elif isinstance(node, TexCmd):
                result = visitor.visit_cmd(node, context)
            elif isinstance(node, Token):
                result = visitor.visit_token(node, context)
            else:
                raise ValueError(f"node is of unknown type {type(node)}")
            if result.consumed == Consumed.no:
                continue
            if result.consumed == Consumed.yes:
                assert result.node
                return ReaderResult(node=result.node, consume_children=False)
            if result.consumed == Consumed.also_children:
                assert result.node
                return ReaderResult(node=result.node, consume_children=True)
        raise ValueError("oops no error handling yet")


def convert(
    node: Union[TexNode, TexExpr, Token],
    visitor: TexReader,
    context: Optional[TexContext] = None,
) -> HtmlNode:
    if context is None:
        context = TexContext([], [])
    # todo make iterative
    if isinstance(node, TexNode):
        return convert(node.expr, visitor, context)
    if not isinstance(node, TexExpr) and not isinstance(node, Token):
        raise ValueError(f"unknown object of type {type(node)}")
    result = visitor.convert(node, context)
    if result.consume_children or isinstance(node, Token):
        return result.node
    html_node = result.node
    context.nodes.append(html_node)
    context.nodes.extend(html_node.args)
    context.nodes.extend(html_node.children)
    context.parents.append(html_node)
    args = node.args  # todo add test for the weird behaviour of contents
    # todo maybe add feature request
    for arg in node.args:
        new_node = convert(arg, visitor, context.copy())
        context.nodes.append(new_node)
        html_node.add_argument(new_node)
    node.args = TexArgs()
    for child in node.contents:
        new_node = convert(child, visitor, context.copy())
        context.nodes.append(new_node)
        html_node.add_child(new_node)
    node.args = args
    return html_node


class ErrorVisitor(TexVisitor):
    @override
    def visit_cmd(self, cmd: TexCmd, context: TexContext) -> VisitResult:
        context.stack_trace()
        raise ValueError(f"{cmd} {context}")

    @override
    def visit_env(self, env: TexEnv, context: TexContext) -> VisitResult:
        context.stack_trace()
        raise ValueError(f"{env} {context}")

    @override
    def visit_token(self, token: Token, context: TexContext) -> VisitResult:
        context.stack_trace()
        raise ValueError(f"{token} {context}")
