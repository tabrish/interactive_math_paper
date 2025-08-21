from typing import override


class HtmlObject:
    reference_names = {}

    def __init__(self, content: str = ""):
        self.content = content
        self._label = ""
        self.children = []
        self.args = []

    @staticmethod
    def get_name(ref: str) -> str:
        return HtmlObject.reference_names.get(ref, "???")

    def add(self, child: "HtmlObject"):
        child.set_parent(self)
        self.children.append(child)

    def label(self, label:str):
        self._label = label

    def get_label(self) -> str:
        return self._label

    def set_parent(self, parent: "HtmlObject"):
        pass

    def add_arg(self, arg: "HtmlObject"):
        self.args.append(arg)

    def to_html(self) -> str:
        html = self.content
        for child in self.children:
            html += child.to_html()
        return html


class Empty(HtmlObject):
    def __init__(self):
        super().__init__("")

    @override
    def to_html(self) -> str:
        return ""
