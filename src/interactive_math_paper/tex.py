from typing import Optional, override
from TexSoup.data import TexCmd, BraceGroup, TexEnv
from TexSoup.utils import Token
from TexSoup.tokens import TC
from .amsmath import AmsMathConverter
from .amsthm import TheoremConverter
from .data import HtmlObject, Empty


class Bibliography(HtmlObject):
    @override
    def to_html(self) -> str:
        heading = "<h2>Bibliography</h2>"
        bib = {}
        current_bibitem = None
        for child in self.children:
            if isinstance(child, Bibitem):
                current_bibitem = child.to_html()
                bib[current_bibitem] = []
                continue
            if current_bibitem is None:
                heading += child.to_html()
                continue
            bib[current_bibitem].append(child.to_html())
        for key, value in bib.items():
            content = ""
            for v in value:
                content += v
            heading += f"""<div class="references">
                <div class="reference-item">
                    <span class="ref-label">[{key}]</span>
                    <div class="ref-content" id="{key}">{content}</div>
                </div>
            </div>"""

        return heading


class Bibitem(HtmlObject):
    @override
    def to_html(self) -> str:
        return self.args[0].to_html()


class Cite(HtmlObject):
    @override
    def to_html(self) -> str:
        return (
            '<a href="#' + f'{self.args[0].to_html()}">[{self.args[0].to_html()}]</a>'
        )


class Title(HtmlObject):
    @override
    def to_html(self) -> str:
        return ""

    def _to_html(self) -> str:
        return f"<h1>{self.args[0].to_html()}</h1>"


class Author(HtmlObject):
    @override
    def to_html(self) -> str:
        return ""

    def _to_html(self) -> str:
        return f'<div class="author">{self.args[0].to_html()}</div>'


class Address(HtmlObject):
    @override
    def to_html(self) -> str:
        return ""

    def _to_html(self) -> str:
        return f'<div class="address">{self.args[0].to_html()}</div>'


class MakeTitle(HtmlObject):
    def __init__(self, title: Title, authors: list[Author], address: list[Address]):
        self.title = title
        self.authors = authors
        self.address = address

    @override
    def to_html(self) -> str:
        content = self.title._to_html()
        for author in self.authors:
            content += author._to_html()
        for add in self.address:
            content += add._to_html()
        return content


class Abstract(HtmlObject):
    @override
    def to_html(self) -> str:
        return f'<div class="abstract"><h3>Abstract</h3>{super().to_html()}</div>'


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
    counter = 0

    def __init__(self):
        super().__init__("")
        Section.counter += 1
        self.number = Section.counter

    @override
    def to_html(self) -> str:
        return f"<h2>{self.number} {self.args[0].to_html()}</h2>"


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
        stack = [self]
        while stack:
            child = stack.pop()
            if isinstance(child, HtmlBraceGroup):
                child.visible = True
            stack.extend(child.children)
        return f" {self.delimiter}{super().to_html()}{self.delimiter} "


class Root(HtmlObject):
    def __init__(self):
        super().__init__("")
        self.math_commands = ""
        self.title = ""
        self.author = []
        self.address = []

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
                displayMath: [['$$', '$$']],
                tags: "ams"
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
                width: 80%;
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
            .popup {{
                position: absolute;
                background: white;
                border: 2px solid #0066cc;
                border-radius: 6px;
                padding: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                max-width: 300px;
                font-size: 14px;
                line-height: 1.4;
                display: none;
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
            .references {{
                padding-top: 1em;
                font-size: 0.95em;
                line-height: 1.4;
            }}

            .reference-item {{
                margin-bottom: 1em;
            }}

            .ref-label {{
                font-weight: bold;
                margin-right: 0.5em;
                color: #333;
            }}

            .ref-content {{
                display: inline;
                color: #555;
            }}

        </style>
            </head>
            <body>
                {super().to_html()}

                <script>
                    const popup = document.createElement('div');
                    popup.className = 'popup';
                    document.body.appendChild(popup);

                    // Add interactivity to all anchor tags
                    document.querySelectorAll('a').forEach(link => {{
                        link.addEventListener('mouseenter', function () {{
                            const href = this.getAttribute('href');

                            if (href && href.startsWith('#')) {{
                                const targetId = href.substring(1);
                                const targetEl = document.getElementById(targetId);

                                if (targetEl) {{
                                    popup.innerHTML = targetEl.innerHTML;
                                    showPopup(this);

                                    // Optional: process MathJax
                                    if (window.MathJax && window.MathJax.typesetPromise) {{
                                        MathJax.typesetPromise([popup]).catch((err) => {{
                                            console.log('MathJax error in popup:', err);
                                        }});
                                    }}
                                }}
                            }}
                        }});

                        link.addEventListener('mouseleave', function () {{
                            popup.style.display = 'none';
                        }});
                    }});

                    function showPopup(element) {{
                        popup.style.display = 'block';

                        const rect = element.getBoundingClientRect();
                        popup.style.left = rect.left + window.scrollX + 'px';
                        popup.style.top = (rect.bottom + window.scrollY + 2) + 'px';

                        const popupRect = popup.getBoundingClientRect();
                        if (popupRect.right > window.innerWidth) {{
                            popup.style.left = (window.innerWidth - popupRect.width - 10 + window.scrollX) + 'px';
                        }}
                        if (popupRect.bottom > window.innerHeight) {{
                            popup.style.top = (rect.top + window.scrollY - popupRect.height - 2) + 'px';
                        }}
                    }}

                    // Hide popup when clicking outside
                    document.addEventListener('click', function (e) {{
                        if (!popup.contains(e.target)) {{
                            popup.style.display = 'none';
                        }}
                    }});
                </script>

            </body>
        </html>
        """


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
                        self.chain.append(TheoremConverter(lambda: Section.counter))
                    if "amsmath" in arg.contents[0]:
                        self.chain.append(AmsMathConverter())
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

    def convert_environment(self, env: Root) -> Optional[HtmlObject]:
        if env.name == "[tex]":
            self.tex_env = Root()
            return self.tex_env
        if env.name == "$":
            return MathObject("$")
        if env.name == "$$":
            return MathObject("$$")
        if env.name == "BraceGroup":
            if isinstance(env.contents[0], TexCmd) and env.contents[0].name == "em":
                return EmBraces()
            return HtmlBraceGroup()
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
            return Bibliography()
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
        if cmd.name == "author":
            new_author = Author()
            self.tex_env.author.append(new_author)
            return new_author
        if cmd.name == "address":
            new_address = Address()
            self.tex_env.address.append(new_address)
            return new_address
        if cmd.name == "title":
            self.tex_env.title = Title()
            return self.tex_env.title
        if cmd.name == "maketitle":
            return MakeTitle(
                self.tex_env.title, self.tex_env.author, self.tex_env.address
            )
        if cmd.name == "cite":
            return Cite()
        if cmd.name == "bibitem":
            return Bibitem()
        return None

    def convert_token(self, token: Token) -> Optional[HtmlObject]:
        if token.category == TC.Text:
            return HtmlObject(
                token.text.replace("\n\n", "<hr>")
                .replace(r"``", "“")
                .replace(r"''", "”")
            )
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

    def convert_environment(self, env: Root) -> Optional[HtmlObject]:
        print(f"unknown environment {env.name} with args {env.args}")

        return HtmlObject("")

    def convert_command(self, cmd: TexCmd) -> Optional[HtmlObject]:
        return HtmlObject(str(cmd) + " ")

    def convert_token(self, token: Token) -> Optional[HtmlObject]:
        print(f"unhandeled token {token.__dict__}")
        return HtmlObject(token.text)
