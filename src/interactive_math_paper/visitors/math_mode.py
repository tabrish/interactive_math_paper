from typing import override
from TexSoup.data import TexEnv, TexCmd, Token
from ..conversion import TexVisitor, VisitResult, TexContext, HtmlNode
from .tex import TextNode


class MathModeNode(HtmlNode):
    def __init__(self, boundary: str):
        super().__init__()
        self.boundary = boundary

    @override
    def to_html(self) -> str:
        return f"{self.boundary}{self.children_to_html()}{self.boundary}"


class MathModeVisitor(TexVisitor):
    @override
    def visit_env(self, env: TexEnv, context: TexContext) -> VisitResult:
        if env.name == "$" or env.name == "$$":
            context.register("math_mode", True)
            return VisitResult.use(MathModeNode(env.name))
        return VisitResult.pass_by()

    @override
    def visit_cmd(self, cmd: TexCmd, context: TexContext) -> VisitResult:
        if context.get("math_mode") or cmd.name == "eqref":
            return VisitResult.use(TextNode(str(cmd)), False)
        return VisitResult.pass_by()

    @override
    def visit_token(self, token: Token, context: TexContext) -> VisitResult:
        return VisitResult.pass_by()
