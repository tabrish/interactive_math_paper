from typing import override, Optional
from TexSoup.data import TexCmd, TexEnv, Token
from TexSoup.tokens import TC
from ..conversion import HtmlNode, TexVisitor, VisitResult, TexContext, EmptyNode


class HtmlBraces(HtmlNode):
    def __init__(self, visible: bool):
        super().__init__()
        self.visible = visible

    @override
    def to_html(self) -> str:
        if any(isinstance(child, EmBraces) for child in self.children):
            return f"<i>{self.children_to_html()}</i>"
        return (
            self.children_to_html()
            if not self.visible
            else f"{{{self.children_to_html()}}}"
        )


class EmBraces(EmptyNode): ...


class Label(EmptyNode):
    def __init__(self, label_id: str):
        super().__init__()
        self.label_id = label_id


class Ref(HtmlNode):
    def __init__(self, ref_resolution):
        super().__init__()
        self.ref_resolution = ref_resolution

    @override
    def to_html(self) -> str:
        return (
            '<a href="#'
            + f'{self.args[0].to_html()}">{self.ref_resolution(self.args[0].to_html())}</a>'
        )


class Root(HtmlNode):
    def __init__(self):
        super().__init__()

    @override
    def to_html(self) -> str:
        global_js = ""
        global_css = ""
        for visitor in TexVisitor.visitors:
            global_js += visitor.global_js()
            global_css += visitor.global_css()

        return f"""
        <html>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interactive Mathematical Paper</title>
        <head>
        {global_js}

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
            {global_css}

        </style>
            </head>
            <body>
                {self.children_to_html()}
            </body>
        </html>
        """


class BracketGroup(EmptyNode): ...


class Document(EmptyNode): ...


class Bibliography(HtmlNode):
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


class Bibitem(HtmlNode):
    @override
    def to_html(self) -> str:
        if len(self.args) == 0:
            raise ValueError("bibitem without a child")
        return self.args[0].to_html()


class Cite(HtmlNode):
    @override
    def to_html(self) -> str:
        return (
            '<a href="#' + f'{self.args[0].to_html()}">[{self.args[0].to_html()}]</a>'
        )


class Abstract(HtmlNode):
    @override
    def to_html(self) -> str:
        return f'<div class="abstract"><h3>Abstract</h3>{self.children_to_html()}</div>'


class Title(HtmlNode):
    @override
    def to_html(self) -> str:
        return f"<h1>{self.args[0].to_html()}</h1>"


class Author(HtmlNode):
    @override
    def to_html(self) -> str:
        return f'<div class="author">{self.args[0].to_html()}</div>'


class Address(HtmlNode):
    @override
    def to_html(self) -> str:
        return f'<div class="address">{self.args[0].to_html()}</div>'


class MakeTitle(HtmlNode):
    def __init__(self, title: Title, authors: list[Author], address: list[Address]):
        super().__init__()
        self.add_child(title)
        for author in authors:
            self.add_child(author)
        for add in address:
            self.add_child(add)

    @override
    def to_html(self) -> str:
        return self.children_to_html()


class Enumerate(HtmlNode):
    @override
    def to_html(self) -> str:
        return f"<ol>{self.children_to_html()}</ol>"


class Itemize(HtmlNode):
    @override
    def to_html(self) -> str:
        return f"<ul>{self.children_to_html()}</ul>"


class TextNode(HtmlNode):
    def __init__(self, text: str):
        self.text = text
        self.parent = None

    @override
    def to_html(self):
        return self.text


class Item(HtmlNode):
    @override
    def to_html(self) -> str:
        return f"<li>{self.children_to_html()}</li>"


class Proof(HtmlNode):
    @override
    def to_html(self) -> str:
        return (
            """<details><summary>Proof</summary>"""
            f"""<div class="proof-content">{self.children_to_html()} □</div></details>"""
        )


class Section(HtmlNode):
    def __init__(self, number: Optional[int] = None):
        super().__init__()
        self.number = number

    @override
    def to_html(self) -> str:
        number_text = f" {self.number} " if self.number is not None else ""
        return f"<h2>{number_text}{self.args[0].to_html()}</h2>"


class DefaultTexVisitor(TexVisitor):
    @override
    def visit_env(self, env: TexEnv, context: TexContext) -> VisitResult:
        if env.name == "[tex]":
            context.register("labels", {})
            return VisitResult.use(Root())
        if env.name == "proof":
            return VisitResult.use(Proof())
        if env.name == "enumerate":
            return VisitResult.use(Enumerate())
        if env.name == "itemize":
            return VisitResult.use(Itemize())
        if env.name == "abstract":
            return VisitResult.use(Abstract())
        if env.name == "thebibliography":
            return VisitResult.use(Bibliography())
        if env.name == "BracketGroup":
            return VisitResult.use(BracketGroup())
        if env.name == "document":
            return VisitResult.use(Document())
        if env.name == "BraceGroup":
            return VisitResult.use(HtmlBraces(context.get("math_mode") or False))
        return VisitResult.pass_by()

    @override
    def visit_cmd(self, cmd: TexCmd, context: TexContext) -> VisitResult:
        if cmd.name == "section":
            current_section_number = context.get("section") or 0
            context.register_env("section", current_section_number + 1)
            context.register_env("tag", str(current_section_number + 1))
            return VisitResult.use(Section(current_section_number + 1))
        if cmd.name == "section*":
            context.register_env("tag", "??")
            return VisitResult.use(Section())
        if cmd.name == "item":
            return VisitResult.use(Item())
        if cmd.name == "pageref":
            raise Exception(
                "it does not make sense to use pageref when converting to html"
            )
        if cmd.name == "author":
            new_author = Author()
            context.register_env("author", (context.get("author") or []) + [new_author])
            return VisitResult.use(new_author)
        if cmd.name == "address":
            new_address = Address()
            context.register_env(
                "address", (context.get("address") or []) + [new_address]
            )
            return VisitResult.use(new_address)
        if cmd.name == "title":
            context.register_env("title", Title())
            return VisitResult.use(context.get("title"))
        if cmd.name == "maketitle":
            return VisitResult.use(
                MakeTitle(
                    context.get("title"), context.get("author"), context.get("address")
                )
            )
        if cmd.name == "cite":
            return VisitResult.use(Cite())
        if cmd.name == "bibitem":
            return VisitResult.use(Bibitem())
        if cmd.name == "ref":
            return VisitResult.use(
                Ref(lambda key: (context.get("labels") or {}).get(key, "??"))
            )
        if cmd.name == "label":
            label_id = cmd.args[0].contents[0]
            context.get("labels")[label_id] = context.get("tag") or "??"
            return VisitResult.use(Label(label_id))
        if cmd.name == "em":
            return VisitResult.use(EmBraces())
        if cmd.name == "documentclass":
            return VisitResult.hidden(False)
        if cmd.name == "usepackage":
            return VisitResult.hidden(False)
        if cmd.name == "hspace":
            return VisitResult.hidden(False)
        return VisitResult.pass_by()

    @override
    def visit_token(self, token: Token, context: TexContext) -> VisitResult:
        if token.category == TC.Text:
            return VisitResult.use(
                TextNode(
                    token.text.replace("\n\n", "<hr>")
                    .replace(r"``", "“")
                    .replace(r"''", "”")
                )
            )
        if token.category == TC.Comment:
            return VisitResult.use(TextNode(""))
        if token.category == TC.EscapedComment:
            if token.text == r"\\\\":
                return VisitResult.use(TextNode("<br>"))
            return VisitResult.use(TextNode(token.text[2:]))
        return VisitResult.pass_by()

    @override
    def global_js(self) -> str:
        return """<script>
            window.onload = () => {
            console.log("yay we are done loading");
            const popup = document.createElement('div');
            popup.className = 'popup';
            document.body.appendChild(popup);

            // Add interactivity to all anchor tags
            document.querySelectorAll('a').forEach(link => {
                link.addEventListener('mouseenter', function () {
                    const href = this.getAttribute('href');

                    if (href && href.startsWith('#')) {
                        const targetId = href.substring(1);
                        const targetEl = document.getElementById(targetId);

                        if (targetEl) {
                            popup.innerHTML = targetEl.innerHTML;
                            showPopup(this);

                            // Optional: process MathJax
                            if (window.MathJax && window.MathJax.typesetPromise) {
                                MathJax.typesetPromise([popup]).catch((err) => {
                                    console.log('MathJax error in popup:', err);
                                });
                            }
                        }
                    }
                });

                link.addEventListener('mouseleave', function () {
                    popup.style.display = 'none';
                });
            });

            function showPopup(element) {
                popup.style.display = 'block';

                const rect = element.getBoundingClientRect();
                popup.style.left = rect.left + window.scrollX + 'px';
                popup.style.top = (rect.bottom + window.scrollY + 2) + 'px';

                const popupRect = popup.getBoundingClientRect();
                if (popupRect.right > window.innerWidth) {
                    popup.style.left = (window.innerWidth - popupRect.width - 10 + window.scrollX) + 'px';
                }
                if (popupRect.bottom > window.innerHeight) {
                    popup.style.top = (rect.top + window.scrollY - popupRect.height - 2) + 'px';
                }
            }

            // Hide popup when clicking outside
            document.addEventListener('click', function (e) {
                if (!popup.contains(e.target)) {
                    popup.style.display = 'none';
                }
            });}
        </script>"""
