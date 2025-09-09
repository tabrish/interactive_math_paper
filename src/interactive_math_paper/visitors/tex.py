from typing import override
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


class Tag(EmptyNode):
    def __init__(self, tag: str):
        super().__init__()
        self.tag = tag


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
            global_js += visitor.load_js()
            global_js += visitor.global_js()
            global_css += visitor.load_css()
            global_css += visitor.global_css()

        return f"""
        <html>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interactive Mathematical Paper</title>
        <head>
        {global_js}

        <style>
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
        super().__init__()
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


class Section(Tag):
    def __init__(self, number: int):
        super().__init__(str(number))
        self.number = number

    @override
    def to_html(self) -> str:
        number_text = f" {self.number} "
        return f"<h2>{number_text}{self.args[0].to_html()}</h2>"


class SectionAst(HtmlNode):
    @override
    def to_html(self) -> str:
        return f"<h2>{self.args[0].to_html()}</h2>"


class DefaultTexVisitor(TexVisitor):
    def __init__(self):
        super().__init__("tex")

    labels = {}

    @override
    def visit_env(self, env: TexEnv, context: TexContext) -> VisitResult:
        if env.name == "[tex]":
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
            return VisitResult.use(HtmlBraces(False))
        return VisitResult.pass_by()

    @override
    def visit_cmd(self, cmd: TexCmd, context: TexContext) -> VisitResult:
        if cmd.name == "section":
            section_number = (context.first(Section) or Section(0)).number + 1
            section = Section(section_number)
            return VisitResult.use(section)
        if cmd.name == "section*":
            return VisitResult.use(SectionAst())
        if cmd.name == "item":
            return VisitResult.use(Item())
        if cmd.name == "pageref":
            raise Exception(
                "it does not make sense to use pageref when converting to html"
            )
        if cmd.name == "author":
            return VisitResult.use(Author())
        if cmd.name == "address":
            return VisitResult.use(Address())
        if cmd.name == "title":
            return VisitResult.use(Title())
        if cmd.name == "maketitle":
            return VisitResult.use(
                MakeTitle(
                    context.first(Title) or Title(),
                    context.all(Author),
                    context.all(Address),
                )
            )
        if cmd.name == "cite":
            return VisitResult.use(Cite())
        if cmd.name == "bibitem":
            return VisitResult.use(Bibitem())
        if cmd.name == "ref":
            return VisitResult.use(
                Ref(lambda key: DefaultTexVisitor.labels.get(key, "??"))
            )
        if cmd.name == "label":
            label_id = cmd.args[0].contents[0]
            DefaultTexVisitor.labels[label_id] = (context.first(Tag) or Tag("??")).tag
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

        </script>"""
