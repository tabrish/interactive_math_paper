from typing import override
from TexSoup.data import TexEnv, TexCmd, Token
from ..conversion import TexVisitor, VisitResult, TexContext


class TheoremVisitor(TexVisitor):
    @override
    def visit_env(self, env: TexEnv, context: TexContext) -> VisitResult:
        return VisitResult.pass_by()

    @override
    def visit_cmd(self, cmd: TexCmd, context: TexContext) -> VisitResult:
        return VisitResult.pass_by()

    @override
    def visit_token(self, token: Token, context: TexContext) -> VisitResult:
        return VisitResult.pass_by()
