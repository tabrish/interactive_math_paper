from typing import Optional
from TexSoup.data import TexEnv, TexCmd
from TexSoup.utils import Token
from .data import HtmlObject, Empty


class AmsMathConverter:
    def convert_command(self, cmd: TexCmd) -> Optional[HtmlObject]:
        if cmd.name == "hdots":
            return HtmlObject(r"\dots")
        return None

    def convert_environment(self, env: TexEnv) -> Optional[HtmlObject]:
        if env.name == "equation":
            return Empty(str(env))
        return None

    def convert_token(self, token: Token) -> Optional[HtmlObject]:
        return None
