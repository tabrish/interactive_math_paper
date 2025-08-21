from typing import Optional, override
from TexSoup.data import TexCmd, BraceGroup
from TexSoup.utils import Token
from TexSoup.tokens import TC
from interactive_math_paper.amsmath import AmsMathConverter
from .amsthm import TheoremConverter
from .data import HtmlObject, Empty


class Abstract(HtmlObject):
    @override
    def to_html(self) -> str:
        return f'<div class="abstract"><h3>Abstract</h3>{super().to_html()}</div>'


class Enumerate(HtmlObject):
    def __init__(self):
        super().__init__("")

    @override
    def to_html(self) -> str:
        return f"<ol>{super().to_html()}</ol>"


class Itemize(HtmlObject):
    def __init__(self):
        super().__init__("")

    @override
    def to_html(self) -> str:
        return f"<ul>{super().to_html()}</ul>"


class Item(HtmlObject):
    def __init__(self):
        super().__init__("")

    @override
    def to_html(self) -> str:
        return f"<li>{super().to_html()}</li>"


class Proof(HtmlObject):
    def __init__(self):
        super().__init__("")

    @override
    def to_html(self) -> str:
        return f"""<details>
            <summary>Proof</summary>
            <div class="proof-content">{super().to_html()} □</div>
        </details>"""


class Section(HtmlObject):
    def __init__(self):
        super().__init__("")

    @override
    def to_html(self) -> str:
        return f"<h2>{self.args[0].to_html()}</h2>"


class EmBraces(HtmlObject):
    def __init__(self):
        super().__init__("")

    @override
    def to_html(self) -> str:
        return f"<i>{super().to_html()}</i>"


class MathObject(HtmlObject):
    def __init__(self, delimiter: str):
        super().__init__("")
        self.delimiter = delimiter

    @override
    def to_html(self) -> str:
        return f" {self.delimiter}{super().to_html()}{self.delimiter} "


class MathEnvironment(HtmlObject):
    def __init__(self):
        super().__init__("")
        self.math_commands = ""

    @override
    def to_html(self) -> str:
        return f"""
        <html>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interactive Mathematical Paper</title>

        <!-- MathJax for mathematical notation -->
        <script>
        window.MathJax = {{
            tex: {{
                inlineMath: [['$', '$']],
                displayMath: [['$$', '$$']]
            }},
            startup: {{
                ready: function () {{
                    MathJax.startup.defaultReady();
                    const {{STATE}} = MathJax._.core.MathItem;
                          MathJax.tex2mml(String.raw`
                            {self.math_commands}
                          `);
                    // Process math after page loads
                    MathJax.typesetPromise().then(() => {{
                        console.log('MathJax rendering complete');
                    }});
                }}
            }}
        }};
        </script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.min.js"></script>

        <style>
            body {{
                font-family: "Computer Modern", "Latin Modern", serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
                background-color: #fefefe;
            }}
            details {{
                margin: 15px 0;
            }}
            summary {{
                font-weight: bold;
                cursor: pointer;
                color: #0066cc;
                padding: 5px 0;
            }}
            .abstract {{
                background-color: #fafafe;
                width: 60%;
                display: block;
                  margin-left: auto;
                  margin-right: auto;
            }}
            .my-ref {{
                color: #cc6600;
                cursor: pointer;
                border-bottom: 1px dotted #cc6600;
                position: relative;
            }}

            .my-ref:hover {{
                background-color: #fff3e6;
            }}

            summary:hover {{
                background-color: #f0f8ff;
            }}
            .proof-content {{
                background-color: #fafafa;
                border-left: 3px solid #ddd;
                padding: 10px 15px;
                margin-top: 10px;
            }}
            h1, h2, h3 {{
                color: #333;
            }}
            hr {{
              margin-top: 10px;
              border: none;
            }}
            .theorem {{
                background-color: #f9f9f9;
                border-left: 4px solid #333;
                padding: 15px;
                margin: 15px 0;
                font-style: italic;
            }}

            .theorem-label {{
                font-weight: bold;
                font-style: normal;
            }}
        </style>
            </head>
            <body>
                {super().to_html()}
            </body>
        </html>
        """


class ConversionChain:
    def __init__(self, chain: list):
        self.chain = chain
        self.default = [DefaultConversion()]

    def convert_environment(self, env: MathEnvironment) -> Optional[HtmlObject]:
        for converter in self.chain + self.default:
            converted = converter.convert_environment(env)
            if converted:
                return converted
        return None

    def convert_command(self, cmd: TexCmd) -> Optional[HtmlObject]:
        if cmd.name == "usepackage":
            for arg in cmd.args:
                if isinstance(arg, BraceGroup):
                    if "amsthm" in arg.contents[0]:
                        self.chain.append(TheoremConverter())
                    if "amsmath" in arg.contents[0]:
                        self.chain.append(AmsMathConverter())
            return Empty()
        for converter in self.chain + self.default:
            converted = converter.convert_command(cmd)
            if converted:
                return converted
        return None

    def convert_token(self, token: Token) -> Optional[HtmlObject]:
        for converter in self.chain + self.default:
            converted = converter.convert_token(token)
            if converted:
                return converted
        return None


class TexConversion:
    def __init__(self):
        self.tex_env = None

    def convert_environment(self, env: MathEnvironment) -> Optional[HtmlObject]:
        if env.name == "[tex]":
            self.tex_env = MathEnvironment()
            return self.tex_env
        if env.name == "$":
            return MathObject("$")
        if env.name == "$$":
            return MathObject("$$")
        if env.name == "BraceGroup":
            if isinstance(env.contents[0], TexCmd) and env.contents[0].name == "em":
                return EmBraces()
            return HtmlObject("")
        if env.name == "BracketGroup":
            return HtmlObject("")
        if env.name == "proof":
            return Proof()
        if env.name == "enumerate":
            return Enumerate()
        if env.name == "itemize":
            return Itemize()
        if env.name == "document":
            return HtmlObject("")
        if env.name == "thebibliography":
            return HtmlObject("<h2>Bibliography</h2>")
        if env.name == "abstract":
            return Abstract()
        return None

    def convert_command(self, cmd: TexCmd) -> Optional[HtmlObject]:
        if cmd.name == "section":
            assert len(cmd.args) == 1
            return Section()
        if cmd.name == "section*":
            return Section()
        if (
            cmd.name == "em"
            and isinstance(cmd.parent, BraceGroup)
            and cmd.parent.contents[0] == cmd
        ):
            return HtmlObject("")
        if cmd.name == "item":
            return Item()
        if cmd.name == "documentclass":
            return Empty()
        return None

    def convert_token(self, token: Token) -> Optional[HtmlObject]:
        if token.category == TC.Text:
            return HtmlObject(token.text.replace("\n\n", "<hr>"))
        if token.category == TC.Comment:
            return HtmlObject("")
        if token.category == TC.EscapedComment:
            if token.text == r"\\\\":
                return HtmlObject("<br>")
            return HtmlObject(token.text[2:])
        return None


class DefaultConversion:
    def __init__(self):
        pass

    def convert_environment(self, env: MathEnvironment) -> Optional[HtmlObject]:
        print(f"unknown environment {env.name} with args {env.args}")

        return HtmlObject("")

    def convert_command(self, cmd: TexCmd) -> Optional[HtmlObject]:
        return HtmlObject(str(cmd) + " ")

    def convert_token(self, token: Token) -> Optional[HtmlObject]:
        print(f"unhandeled token {token.__dict__}")
        return HtmlObject(token.text)
