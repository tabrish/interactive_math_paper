from typing import override, Optional
from TexSoup.data import TexEnv, TexCmd, Token
from ..conversion import TexVisitor, VisitResult, TexContext, HtmlNode
from .tex import Label, Tag


class TheoremEnv(HtmlNode):
    def __init__(self, number: int, label: str, tag: str):
        super().__init__()
        self.label = label
        self.tag = tag
        self.number = number

    def _get_label(self) -> Optional[str]:
        for child in self.children:
            if isinstance(child, Label):
                return child.label_id
        return None

    @override
    def to_html(self) -> str:
        citation = ""
        if len(self.args) == 1:
            citation = self.args[0].to_html()
        id_text = "" if not self._get_label() else f'id = "{self._get_label()}"'
        return f"""<div class="theorem" {id_text}>
            <span class="theorem-label">{self.label} {self.tag}. {citation}</span> {self.children_to_html()}
        </div>"""


class TheoremVisitor(TexVisitor):
    previous_tag = None

    def __init__(self):
        super().__init__()
        self.labels = {}

    @override
    def visit_env(self, env: TexEnv, context: TexContext) -> VisitResult:
        if env.name in self.labels:
            last_env = context.first(TheoremEnv)
            next_number = last_env.number + 1 if last_env else 1
            if TheoremVisitor.previous_tag != context.first(Tag):
                TheoremVisitor.previous_tag = context.first(Tag)
                next_number = 1
            print(context.first(Tag))
            theorem_tag = (context.first(Tag) or Tag("")).tag
            if theorem_tag == "??":
                theorem_tag = ""
            theorem_tag = (
                f"{theorem_tag}.{next_number}"
                if theorem_tag != ""
                else str(next_number)
            )
            environment = TheoremEnv(next_number, self.labels[env.name], theorem_tag)
            environment.add_child(Tag(theorem_tag))

            return VisitResult.use(environment)
        return VisitResult.pass_by()

    @override
    def visit_cmd(self, cmd: TexCmd, context: TexContext) -> VisitResult:
        if cmd.name == "newtheorem":
            self.labels[cmd.args[0].contents[0]] = cmd.args[1].contents[0]
            return VisitResult.hidden(False)
        return VisitResult.pass_by()

    @override
    def visit_token(self, token: Token, context: TexContext) -> VisitResult:
        return VisitResult.pass_by()
