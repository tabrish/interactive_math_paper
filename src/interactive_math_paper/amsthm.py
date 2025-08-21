from typing import Optional, override
from TexSoup.data import TexEnv, TexCmd
from TexSoup.utils import Token
from .data import HtmlObject, Empty


class TheoremEnv(HtmlObject):
    def __init__(self, label: str):
        super().__init__("")
        self.env_label = label

    @override
    def to_html(self) -> str:
        id_text = "" if not self.get_label() else f'id = "{self.get_label()}"'
        return f"""<div class="theorem" {id_text}>
            <span class="theorem-label">{self.env_label}.</span> {super().to_html()}
        </div>"""


class TheoremConverter:
    def __init__(self):
        self.labels = {}

    def convert_command(self, cmd: TexCmd) -> Optional[HtmlObject]:
        if cmd.name == "newtheorem":
            self.labels[cmd.args[0].contents[0]] = cmd.args[1].contents[0]
            return Empty()
        return None

    def convert_environment(self, env: TexEnv) -> Optional[HtmlObject]:
        if env.name in self.labels:
            return TheoremEnv(self.labels[env.name])
        return None

    def convert_token(self, token: Token) -> Optional[HtmlObject]:
        return None
