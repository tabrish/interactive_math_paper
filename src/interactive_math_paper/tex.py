from typing import Optional, override
from TexSoup.data import TexCmd, BraceGroup, TexEnv
from TexSoup.utils import Token
from .amsthm import TheoremConverter
from .data import HtmlObject, Empty


class Label(Empty):
    def __init__(self, label: str):
        super().__init__()
        self.data = label

    @override
    def set_parent(self, parent: "HtmlObject"):
        parent.label(self.data)


class Link(HtmlObject):
    @override
    def to_html(self) -> str:
        return (
            '<a href="#'
            + f'{self.args[0].to_html()}">{HtmlObject.get_name(self.args[0].to_html())}</a>'
        )


class HtmlBraceGroup(HtmlObject):
    def __init__(self):
        super().__init__()
        self.visible = False

    @override
    def to_html(self) -> str:
        return super().to_html() if not self.visible else f"{{{super().to_html()}}}"


class EmBraces(HtmlObject):
    def __init__(self):
        super().__init__("")

    @override
    def to_html(self) -> str:
        return f"<i>{super().to_html()}</i>"


class ConversionChain:
    def __init__(self, chain: list):
        self.chain = chain
        self.default = [DefaultConversion()]

    def convert_environment(self, env: TexEnv) -> HtmlObject:
        for converter in self.chain + self.default:
            converted = converter.convert_environment(env)
            if converted:
                return converted
        raise Exception("default conversion must be missing")

    def convert_command(self, cmd: TexCmd) -> HtmlObject:
        if cmd.name == "usepackage":
            for arg in cmd.args:
                if isinstance(arg, BraceGroup):
                    if "amsthm" in arg.contents[0]:
                        self.chain.append(TheoremConverter(lambda: 0))
            return Empty()
        for converter in self.chain + self.default:
            converted = converter.convert_command(cmd)
            if converted:
                return converted
        raise Exception("default conversion must be missing")

    def convert_token(self, token: Token) -> HtmlObject:
        for converter in self.chain + self.default:
            converted = converter.convert_token(token)
            if converted:
                return converted
        raise Exception("default conversion must be missing")


class TexConversion:
    def __init__(self):
        self.tex_env = None

    def convert_environment(self, env: TexEnv) -> Optional[HtmlObject]:
        if env.name == "BraceGroup":
            if isinstance(env.contents[0], TexCmd) and env.contents[0].name == "em":
                return EmBraces()
            return HtmlBraceGroup()
        return None

    def convert_command(self, cmd: TexCmd) -> Optional[HtmlObject]:
        if (
            cmd.name == "em"
            and isinstance(cmd.parent, BraceGroup)
            and cmd.parent.contents[0] == cmd
        ):
            return HtmlObject("")
        if cmd.name == "documentclass":
            return Empty()
        if cmd.name == "renewcommand" or cmd.name == "newcommand" or cmd.name == "def":
            self.tex_env.math_commands += str(cmd)
            return Empty()
        if cmd.name == "DeclareMathOperator":
            assert len(cmd.args) == 2, (
                f"declare math operator {str(cmd)} has a bad number of args"
            )
            operator_cmd = cmd.args[0].contents[0]
            operator_text = cmd.args[1].contents[0]
            self.tex_env.math_commands += (
                f"\\newcommand{{{operator_cmd}}}{{\\text{{{operator_text}}}}}"
            )
            return Empty()
        if cmd.name == "label":
            assert len(cmd.args) == 1, (
                f"why does label {cmd} not have exactly one args?"
            )
            return Label(str(cmd.args[0].contents[0]))
        if cmd.name == "ref":
            return Link()
        return None

    def convert_token(self, token: Token):
        return None


class DefaultConversion:
    def __init__(self):
        pass

    def convert_environment(self, env: TexEnv) -> Optional[HtmlObject]:
        print(f"unknown environment {env.name} with args {env.args}")

        return HtmlObject("")

    def convert_command(self, cmd: TexCmd) -> Optional[HtmlObject]:
        print(f"unknown command {str(cmd)}")
        return HtmlObject(str(cmd) + " ")

    def convert_token(self, token: Token) -> Optional[HtmlObject]:
        print(f"unhandeled token {token.__dict__}")
        return HtmlObject(token.text)
