from typing import Optional, Union, Any, override
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

    @abstractmethod
    def to_html(self) -> str:
        pass

    def global_css(self) -> str:
        return ""

    def global_js(self) -> str:
        return ""


class TexContext:
    def __init__(self):
        self.stack = [{}]

    def register_env(self, key: str, value: Any):
        assert len(self.stack) > 1, "stack is to short to register"
        self.stack[-2][key] = value

    def register(self, key: str, value: Any):
        self.stack[-1][key] = value

    def get(self, key: str) -> Optional[Any]:
        for dictionary in self.stack[::-1]:
            item = dictionary.get(key, None)
            if item is not None:
                return item
        return None

    def push(self):
        self.stack.append({})

    def pop(self):
        self.stack.pop()


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


@dataclass
class ReaderResult:
    node: HtmlNode
    consume_children: bool


class DocumentNode(HtmlNode):
    @override
    def to_html(self) -> str:
        return ""


class TexReader:
    def __init__(self, tex_visitors: list[TexVisitor], fallback: TexVisitor):
        self.chain = tex_visitors + [fallback]
        self.context = TexContext()

    def parse_packages(self, node):
        if not isinstance(node, TexCmd):
            return
        if node.name == "usepackage":
            print(node.name, node.__dict__)

    def convert(self, node: Union[TexExpr, Token]) -> ReaderResult:
        self.parse_packages(node)
        for visitor in self.chain:
            if isinstance(node, TexEnv):
                result = visitor.visit_env(node, self.context)
            elif isinstance(node, TexCmd):
                result = visitor.visit_cmd(node, self.context)
            elif isinstance(node, Token):
                result = visitor.visit_token(node, self.context)
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

    def push(self) -> "TexReader":
        self.context.push()
        return self

    def pop(self) -> "TexReader":
        self.context.pop()
        return self


def convert(node: Union[TexNode, TexExpr, Token], visitor: TexReader) -> HtmlNode:
    # todo make iterative
    if isinstance(node, TexNode):
        return convert(node.expr, visitor)
    if not isinstance(node, TexExpr) and not isinstance(node, Token):
        raise ValueError(f"unknown object of type {type(node)}")
    result = visitor.convert(node)
    if result.consume_children or isinstance(node, Token):
        return result.node
    html_node = result.node
    args = node.args  # todo add test for the weird behaviour of contents
    # todo maybe add feature request
    for arg in node.args:
        html_node.add_argument(convert(arg, visitor.push()))
        visitor.pop()
    node.args = TexArgs()
    for child in node.contents:
        html_node.add_child(convert(child, visitor.push()))
        visitor.pop()
    node.args = args
    return html_node
