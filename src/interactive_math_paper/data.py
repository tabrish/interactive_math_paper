from typing import override
from .conversion import HtmlNode


class HtmlObject(HtmlNode):
    references = {}

    def __init__(self, content: str = ""):
        super().__init__()
        self.content = content
        self._label = ""

    @staticmethod
    def get_name(ref: str) -> str:
        object = HtmlObject.references.get(ref, None)
        if not object:
            return "???"
        return object.to_ref_label()

    @override
    def add_child(self, child: HtmlNode):
        if isinstance(child, HtmlObject):
            child.set_parent(self)
        else:
            assert child.parent is None
            child.parent = self
        self.children.append(child)

    def to_ref_label(self) -> str:
        return "???"

    def label(self, label: str):
        HtmlObject.references[label] = self
        self._label = label

    def get_label(self) -> str:
        return self._label

    def set_parent(self, parent: "HtmlObject"):
        pass

    @override
    def to_html(self) -> str:
        html = self.content
        for child in self.children:
            html += child.to_html()
        return html


class Empty(HtmlObject):
    def __init__(self, text=""):
        super().__init__(text)

    @override
    def to_html(self) -> str:
        return self.content
