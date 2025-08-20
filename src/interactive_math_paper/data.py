class HtmlObject:
    def __init__(self, content: str):
        self.content = content
        self.children = []
        self.args = []

    def add(self, child: "HtmlObject"):
        self.children.append(child)

    def add_arg(self, arg: "HtmlObject"):
        self.args.append(arg)

    def to_html(self) -> str:
        html = self.content
        for child in self.children:
            html += child.to_html()
        return html
