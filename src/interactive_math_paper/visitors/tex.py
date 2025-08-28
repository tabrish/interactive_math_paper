from typing import override, Optional
from TexSoup.data import TexCmd, TexEnv, Token
from ..conversion import HtmlNode, TexVisitor, VisitResult, TexContext


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
        if env.name == "proof":
            return VisitResult.use(Proof())
        if env.name == "enumerate":
            return VisitResult.use(Enumerate())
        if env.name == "itemize":
            return VisitResult.use(Itemize())
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
        return VisitResult.pass_by()

    @override
    def visit_token(self, token: Token, context: TexContext) -> VisitResult:
        return VisitResult.pass_by()
