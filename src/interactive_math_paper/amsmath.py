from typing import Optional
from TexSoup.data import TexEnv, TexCmd
from TexSoup.utils import Token
from .data import HtmlObject


class AmsMathConverter:
    def convert_command(self, cmd: TexCmd) -> Optional[HtmlObject]:
        if cmd.name == "hdots":
            return HtmlObject(r"\dots")
        return None

    def convert_environment(self, env: TexEnv) -> Optional[HtmlObject]:
        return None

    def convert_token(self, token: Token) -> Optional[HtmlObject]:
        return None
