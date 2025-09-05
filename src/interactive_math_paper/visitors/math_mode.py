from typing import override
from TexSoup.data import TexEnv, TexCmd, Token
from ..conversion import TexVisitor, VisitResult, TexContext, HtmlNode
from .tex import TextNode, HtmlBraces


class MathModeNode(HtmlNode):
    def __init__(self, boundary: str):
        super().__init__()
        self.boundary = boundary

    @override
    def to_html(self) -> str:
        return f"{self.boundary}{self.children_to_html()}{self.boundary}"


class MathModeVisitor(TexVisitor):
    def __init__(self):
        super().__init__("math_mode")

    math_commands = ""

    @override
    def visit_env(self, env: TexEnv, context: TexContext) -> VisitResult:
        if env.name == "$" or env.name == "$$":
            return VisitResult.use(MathModeNode(env.name))
        if context.surrounding(MathModeNode):
            if env.name == "BraceGroup":
                return VisitResult.use(HtmlBraces(True))
        return VisitResult.pass_by()

    @override
    def visit_cmd(self, cmd: TexCmd, context: TexContext) -> VisitResult:
        if (context.surrounding(MathModeNode) is not None) or cmd.name == "eqref":
            return VisitResult.use(TextNode(str(cmd) + " "), False)
        if cmd.name == "renewcommand" or cmd.name == "newcommand" or cmd.name == "def":
            MathModeVisitor.math_commands += str(cmd)
            return VisitResult.hidden(False)
        if cmd.name == "DeclareMathOperator":
            assert len(cmd.args) == 2, (
                f"declare math operator {str(cmd)} has a bad number of args"
            )
            operator_cmd = cmd.args[0].contents[0]
            operator_text = cmd.args[1].contents[0]
            MathModeVisitor.math_commands += (
                f"\\newcommand{{{operator_cmd}}}{{\\text{{{operator_text}}}}}"
            )
            return VisitResult.hidden(False)
        return VisitResult.pass_by()

    @override
    def visit_token(self, token: Token, context: TexContext) -> VisitResult:
        return VisitResult.pass_by()

    @override
    def global_js(self) -> str:
        return f"""
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
        """
