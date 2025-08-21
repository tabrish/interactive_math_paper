import sys
from TexSoup import TexSoup, TexNode
from TexSoup.data import TexEnv, TexCmd
from TexSoup.utils import Token
from pathlib import Path
from .tex import HtmlObject, TexConversion, ConversionChain


def parse(node, converter) -> HtmlObject:
    if isinstance(node, TexNode):
        return parse(node.expr, converter)
    if isinstance(node, TexEnv):
        html_object = converter.convert_environment(node)
        for arg in node.args:
            html_object.add_arg(parse(arg, converter))
        for child in node.contents:
            html_object.add(parse(child, converter))
        return html_object
    if isinstance(node, TexCmd):
        html_object = converter.convert_command(node)
        for arg in node.args:
            html_object.add_arg(parse(arg, converter))
        return html_object
    if isinstance(node, Token):
        html_object = converter.convert_token(node)
        return html_object
    raise ValueError(f"unknown object of type {type(node)}")


if __name__ == "__main__":
    input_path = "texfiles/main.tex"
    input_path = Path(input_path)
    output_path = Path("html_examples/tabrish_paper.html")

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            latex_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    soup = TexSoup(latex_content)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(parse(soup, ConversionChain([TexConversion()])).to_html())
