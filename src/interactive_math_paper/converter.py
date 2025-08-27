import sys
from TexSoup.data import TexEnv, TexCmd
from TexSoup.utils import Token
from pathlib import Path
from .tex import TexConversion, ConversionChain
from .conversion import (
    VisitResult,
    lex_tex_source,
    convert,
    TexVisitor,
    TexContext,
    Consumed,
)


class ConversionChainVisitor(TexVisitor):
    def __init__(self, conversion_chain: ConversionChain):
        self.conversion_chain = conversion_chain

    def visit_env(self, env: TexEnv, context: TexContext) -> VisitResult:
        return VisitResult(
            node=self.conversion_chain.convert_environment(env), consumed=Consumed.yes
        )

    def visit_cmd(self, cmd: TexCmd, context: TexContext) -> VisitResult:
        return VisitResult(
            node=self.conversion_chain.convert_command(cmd), consumed=Consumed.yes
        )

    def visit_token(self, token: Token, context: TexContext) -> VisitResult:
        return VisitResult(
            node=self.conversion_chain.convert_token(token), consumed=Consumed.yes
        )


def main_cli():
    if len(sys.argv) < 2:
        print("Need args input.tex [output.html]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if output_file is None:
        output_file = input_file.with_suffix(".html")

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            latex_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    soup = lex_tex_source(latex_content)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(
            convert(
                soup, ConversionChainVisitor(ConversionChain([TexConversion()]))
            ).to_html()
        )
