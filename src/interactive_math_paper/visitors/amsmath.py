from typing import override
from TexSoup.data import TexEnv, TexCmd, Token
from ..conversion import TexVisitor, VisitResult, TexContext
from .tex import TextNode


class AmsMathVisitor(TexVisitor):
    @override
    def visit_env(self, env: TexEnv, context: TexContext) -> VisitResult:
        if env.name == "equation":
            return VisitResult.use(TextNode(str(env)), False)
        return VisitResult.pass_by()

    @override
    def visit_cmd(self, cmd: TexCmd, context: TexContext) -> VisitResult:
        if cmd.name == "hdots":
            return VisitResult.use(TextNode(r"\dots"))
        return VisitResult.pass_by()

    @override
    def visit_token(self, token: Token, context: TexContext) -> VisitResult:
        return VisitResult.pass_by()
