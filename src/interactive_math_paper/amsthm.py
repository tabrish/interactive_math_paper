from typing import Optional, override
from TexSoup.data import TexEnv, TexCmd
from TexSoup.utils import Token
from .data import HtmlObject, Empty


class TheoremEnv(HtmlObject):
    _counter = 0
    _current_section = 0

    def __init__(self, label: str, current_section: int):
        super().__init__("")
        self.env_label = label
        if current_section > TheoremEnv._current_section:
            TheoremEnv._counter = 0
            TheoremEnv._current_section = current_section
        TheoremEnv._counter += 1
        self.number = (TheoremEnv._current_section, TheoremEnv._counter)

    @override
    def to_ref_label(self) -> str:
        return f"{self.number[0]}.{self.number[1]}"

    @override
    def to_html(self) -> str:
        citation = ""
        if len(self.args) == 1:
            citation = self.args[0].to_html()
        id_text = "" if not self.get_label() else f'id = "{self.get_label()}"'
        return f"""<div class="theorem" {id_text}>
            <span class="theorem-label">{self.env_label} {self.number[0]}.{self.number[1]}. {citation}</span> {super().to_html()}
        </div>"""


class TheoremConverter:
    def __init__(self, section_lambda):
        self.labels = {}
        self.section_lambda = section_lambda

    def convert_command(self, cmd: TexCmd) -> Optional[HtmlObject]:
        if cmd.name == "newtheorem":
            self.labels[cmd.args[0].contents[0]] = cmd.args[1].contents[0]
            return Empty()
        return None

    def convert_environment(self, env: TexEnv) -> Optional[HtmlObject]:
        if env.name in self.labels:
            return TheoremEnv(self.labels[env.name], self.section_lambda())
        return None

    def convert_token(self, token: Token) -> Optional[HtmlObject]:
        return None
