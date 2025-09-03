import sys
from pathlib import Path
from .visitors import DefaultTexVisitor, MathModeVisitor, AmsMathVisitor, TheoremVisitor
from .conversion import (
    lex_tex_source,
    convert,
    TexReader,
    ErrorVisitor,
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
                soup,
                TexReader(
                    [MathModeVisitor(), DefaultTexVisitor()],
                    ErrorVisitor(),
                    {
                        "amsthm": TheoremVisitor(),
                        "amsmath": AmsMathVisitor(),
                    },
                ),
            ).to_html()
        )
