import sys
from TexSoup import TexSoup, TexNode
from TexSoup.data import TexEnv, TexCmd, TexArgs
from TexSoup.utils import Token
from pathlib import Path
from .tex import HtmlObject, TexConversion, ConversionChain


def parse(node, converter) -> HtmlObject:
    if isinstance(node, TexNode):
        return parse(node.expr, converter)
    if isinstance(node, TexEnv):
        html_object = converter.convert_environment(node)
        args = node.args  # todo add test for the weird behaviour of contents
        # todo maybe add feature request
        for arg in node.args:
            html_object.add_arg(parse(arg, converter))
        node.args = TexArgs()
        for child in node.contents:
            html_object.add(parse(child, converter))
        node.args = args
        return html_object
    if isinstance(node, TexCmd):
        html_object = converter.convert_command(node)
        args = node.args
        for arg in node.args:
            html_object.add_arg(parse(arg, converter))
        node.args = TexArgs()
        for child in node.contents:
            html_object.add(parse(child, converter))
        node.args = args
        return html_object
    if isinstance(node, Token):
        html_object = converter.convert_token(node)
        return html_object
    raise ValueError(f"unknown object of type {type(node)}")


if __name__ == "__main__":
    output_path = Path("html_examples/tabrish_paper.html")


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

    soup = TexSoup(latex_content)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(parse(soup, ConversionChain([TexConversion()])).to_html())
