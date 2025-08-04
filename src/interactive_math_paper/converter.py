#!/usr/bin/env python3
"""
Simple LaTeX to Interactive HTML Converter

Converts LaTeX files with mathematical content to interactive HTML.
Starting with just the basic features that we know work.

Usage:
    python simple_latex2interactive.py input.tex output.html
"""

import re
import sys
import json
from pathlib import Path
from TexSoup import TexSoup


class LaTeXToInteractiveConverter:
    def __init__(self):
        self.definitions = {}
        self.theorems = {}
        self.theorem_statements = {}  # Store theorem statements by label
        self.theorem_counter = 1
        self.lemma_counter = 1
        self.corollary_counter = 1

    def convert_file(self, input_path, output_path=None):
        """Convert a LaTeX file to interactive HTML"""
        input_path = Path(input_path)

        if output_path is None:
            output_path = input_path.with_suffix(".html")
        else:
            output_path = Path(output_path)

        # Read input file
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                latex_content = f.read()
        except FileNotFoundError:
            print(f"Error: File '{input_path}' not found.")
            return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False

        # Convert content
        html_content = self.convert_latex_to_html(latex_content)

        # Generate complete HTML document
        full_html = self.generate_complete_html(html_content)

        # Write output file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_html)
            print(f"✅ Successfully converted '{input_path}' to '{output_path}'")
            return True
        except Exception as e:
            print(f"Error writing output file: {e}")
            return False

    def convert_latex_to_html(self, latex_content):
        """Convert LaTeX content to HTML with interactive features"""
        html = latex_content

        # Step 0: Remove LaTeX comments and document structure
        html = self._remove_latex_comments(html)
        html = self._strip_document_structure(html)

        # Step 1: Parse definitions and store them (remove from output) - TEXSOUP POWERED!
        html = self._parse_definitions_with_texsoup(html)

        # Step 2: Parse theorems, lemmas, corollaries
        html = re.sub(
            r"\\begin\{theorem\}(.*?)\\end\{theorem\}",
            self._convert_theorem,
            html,
            flags=re.DOTALL,
        )

        html = re.sub(
            r"\\begin\{lemma\}(.*?)\\end\{lemma\}",
            self._convert_lemma,
            html,
            flags=re.DOTALL,
        )

        html = re.sub(
            r"\\begin\{corollary\}(.*?)\\end\{corollary\}",
            self._convert_corollary,
            html,
            flags=re.DOTALL,
        )

        # Step 3: Parse proofs (make them collapsible)
        html = re.sub(
            r"\\begin\{proof\}(.*?)\\end\{proof\}",
            self._convert_proof,
            html,
            flags=re.DOTALL,
        )

        # Step 3.5: Handle lists
        html = re.sub(
            r"\\begin\{itemize\}(.*?)\\end\{itemize\}",
            self._convert_itemize,
            html,
            flags=re.DOTALL,
        )

        html = re.sub(
            r"\\begin\{enumerate\}(.*?)\\end\{enumerate\}",
            self._convert_enumerate,
            html,
            flags=re.DOTALL,
        )

        # Step 4: Handle basic formatting - TEXSOUP POWERED!
        html = self._parse_formatting_with_texsoup(html)

        # Step 5: Handle basic paragraph breaks
        html = re.sub(r"\n\s*\n", "</p>\n<p>", html)
        html = "<p>" + html + "</p>"

        # Step 6: Handle references
        html = re.sub(r"\\ref\{([^}]+)\}", self._convert_ref, html)
        html = re.sub(r"\\eqref\{([^}]+)\}", self._convert_eqref, html)

        # Step 7: Make defined terms interactive (do this last)
        html = self._make_terms_interactive(html)

        return html

    def _remove_latex_comments(self, text):
        """Remove LaTeX comments (lines starting with %)"""
        lines = text.split("\n")
        filtered_lines = []

        for line in lines:
            # Remove comments: everything after % (but not \% which is escaped)
            result_line = ""
            i = 0
            while i < len(line):
                if line[i] == "%":
                    # Check if it's escaped with backslash
                    if i > 0 and line[i - 1] == "\\":
                        # It's escaped (\%), keep it
                        result_line += line[i]
                    else:
                        # It's a comment, ignore rest of line
                        break
                else:
                    result_line += line[i]
                i += 1

            # Only keep lines that aren't empty or just whitespace after comment removal
            if result_line.strip():
                filtered_lines.append(result_line)

        return "\n".join(filtered_lines)

    def _strip_document_structure(self, text):
        """Remove LaTeX document structure (documentclass, packages, begin/end document)"""
        # Remove documentclass
        text = re.sub(r"\\documentclass(\[.*?\])?\{.*?\}", "", text)

        # Remove usepackage commands
        text = re.sub(r"\\usepackage(\[.*?\])?\{.*?\}", "", text)

        # Remove begin/end document
        text = re.sub(r"\\begin\{document\}", "", text)
        text = re.sub(r"\\end\{document\}", "", text)

        # Remove other common preamble commands
        text = re.sub(r"\\author\{.*?\}", "", text)
        text = re.sub(r"\\date\{.*?\}", "", text)
        text = re.sub(r"\\maketitle", "", text)

        # Clean up multiple newlines
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

        return text.strip()

    def _remove_latex_comments(self, text):
        """Remove LaTeX comments (lines starting with %)"""
        lines = text.split("\n")
        filtered_lines = []

        for line in lines:
            # Remove comments: everything after % (but not \% which is escaped)
            # Simple approach: split on % and take the first part if % is not escaped
            result_line = ""
            i = 0
            while i < len(line):
                if line[i] == "%":
                    # Check if it's escaped with backslash
                    if i > 0 and line[i - 1] == "\\":
                        # It's escaped (\%), keep it
                        result_line += line[i]
                    else:
                        # It's a comment, ignore rest of line
                        break
                else:
                    result_line += line[i]
                i += 1

            # Only keep lines that aren't empty or just whitespace after comment removal
            if result_line.strip():
                filtered_lines.append(result_line)

        return "\n".join(filtered_lines)

    def _parse_definitions_with_texsoup(self, text):
        """Parse definitions using TexSoup for perfect nested brace handling"""
        soup = TexSoup(text)
        result = text

        # Find all defn commands and process them from end to beginning
        # (to maintain string positions when replacing)
        defn_nodes = []
        for item in soup:
            if hasattr(item, "name") and item.name == "defn":
                # Extract the term and definition
                contents = item.contents
                if len(contents) >= 2:
                    term = str(contents[0]).strip()
                    definition_parts = contents[1:]
                    definition = "".join(str(part) for part in definition_parts).strip()

                    # Store the definition
                    self.definitions[term] = definition

                    # Find the position of this defn in the original text
                    defn_str = str(item)
                    pos = text.find(defn_str)
                    if pos != -1:
                        defn_nodes.append((pos, pos + len(defn_str), definition))

        # Replace from end to beginning to maintain positions
        for start_pos, end_pos, definition in sorted(defn_nodes, reverse=True):
            replacement = f"""<div class="definition">
                <strong>Definition:</strong> {definition}
            </div>"""
            result = result[:start_pos] + replacement + result[end_pos:]

        return result

    def _parse_formatting_with_texsoup(self, text):
        """Parse all formatting commands using TexSoup for perfect nested brace handling"""
        soup = TexSoup(text)
        result = text

        # Define our formatting commands and their HTML conversions
        format_commands = {
            "title": lambda content: f"<h1>{content}</h1>",
            "section": lambda content: f"<h2>{content}</h2>",
            "subsection": lambda content: f"<h3>{content}</h3>",
            "textbf": lambda content: f"<strong>{content}</strong>",
            "textit": lambda content: f"<em>{content}</em>",
            "emph": lambda content: f"<em>{content}</em>",
        }

        # Find all formatting commands and collect replacements
        replacements = []
        for item in soup:
            if hasattr(item, "name") and item.name in format_commands:
                # Extract the content
                if item.contents:
                    content = "".join(str(part) for part in item.contents).strip()

                    # Find position in original text
                    item_str = str(item)
                    pos = text.find(item_str)
                    if pos != -1:
                        # Get the HTML replacement
                        html_replacement = format_commands[item.name](content)
                        replacements.append(
                            (pos, pos + len(item_str), html_replacement)
                        )

        # Replace from end to beginning to maintain positions
        for start_pos, end_pos, replacement in sorted(replacements, reverse=True):
            result = result[:start_pos] + replacement + result[end_pos:]

        return result

    def _convert_theorem(self, match):
        """Convert theorem environment to HTML"""
        content = match.group(1).strip()

        # Check if there's a label in the content
        label_match = re.search(r"\\label\{([^}]+)\}", content)
        if label_match:
            label = label_match.group(1)
            # Remove the label from the content
            content = re.sub(r"\\label\{[^}]+\}", "", content).strip()
            # Store the theorem statement for references
            self.theorem_statements[label] = (
                f"<strong>Theorem {self.theorem_counter}.</strong> {content}"
            )

        theorem_id = f"theorem-{self.theorem_counter}"
        self.theorems[theorem_id] = content

        html = f'''<div class="theorem" id="{label if label_match else theorem_id}">
            <span class="theorem-label">Theorem {self.theorem_counter}.</span> {content}
        </div>'''

        self.theorem_counter += 1
        return html

    def _convert_lemma(self, match):
        """Convert lemma environment to HTML"""
        content = match.group(1).strip()

        # Check if there's a label in the content
        label_match = re.search(r"\\label\{([^}]+)\}", content)
        if label_match:
            label = label_match.group(1)
            # Remove the label from the content
            content = re.sub(r"\\label\{[^}]+\}", "", content).strip()
            # Store the lemma statement for references
            self.theorem_statements[label] = (
                f"<strong>Lemma {self.lemma_counter}.</strong> {content}"
            )

        lemma_id = f"lemma-{self.lemma_counter}"
        self.theorems[lemma_id] = content

        html = f'''<div class="theorem" id="{label if label_match else lemma_id}">
            <span class="theorem-label">Lemma {self.lemma_counter}.</span> {content}
        </div>'''

        self.lemma_counter += 1
        return html

    def _convert_corollary(self, match):
        """Convert corollary environment to HTML"""
        content = match.group(1).strip()

        # Check if there's a label in the content
        label_match = re.search(r"\\label\{([^}]+)\}", content)
        if label_match:
            label = label_match.group(1)
            # Remove the label from the content
            content = re.sub(r"\\label\{[^}]+\}", "", content).strip()
            # Store the corollary statement for references
            self.theorem_statements[label] = (
                f"<strong>Corollary {self.corollary_counter}.</strong> {content}"
            )

        corollary_id = f"corollary-{self.corollary_counter}"
        self.theorems[corollary_id] = content

        html = f'''<div class="theorem" id="{label if label_match else corollary_id}">
            <span class="theorem-label">Corollary {self.corollary_counter}.</span> {content}
        </div>'''

        self.corollary_counter += 1
        return html

    def _convert_proof(self, match):
        """Convert proof environment to collapsible HTML"""
        content = match.group(1).strip()

        return f"""<details>
            <summary>Proof</summary>
            <div class="proof-content">{content} □</div>
        </details>"""

    def _convert_itemize(self, match):
        """Convert itemize environment to HTML"""
        content = match.group(1).strip()
        # Convert \item to <li>
        items = re.split(r"\\item\s*", content)
        # Remove empty first item (before first \item)
        items = [item.strip() for item in items if item.strip()]

        html_items = "".join(f"<li>{item}</li>" for item in items)
        return f"<ul>{html_items}</ul>"

    def _convert_enumerate(self, match):
        """Convert enumerate environment to HTML"""
        content = match.group(1).strip()
        # Convert \item to <li>
        items = re.split(r"\\item\s*", content)
        # Remove empty first item (before first \item)
        items = [item.strip() for item in items if item.strip()]

        html_items = "".join(f"<li>{item}</li>" for item in items)
        return f"<ol>{html_items}</ol>"

    def _convert_ref(self, match):
        """Convert ref to interactive reference"""
        label = match.group(1)
        if label in self.theorem_statements:
            ref_text = self._get_theorem_ref_text(label)
            return f'<span class="theorem-ref" data-ref="{label}">{ref_text}</span>'
        else:
            return '<span class="unresolved-ref">??</span>'

    def _convert_eqref(self, match):
        """Convert eqref to interactive reference"""
        label = match.group(1)
        if label in self.theorem_statements:
            ref_text = self._get_theorem_ref_text(label)
            return f'(<span class="theorem-ref" data-ref="{label}">{ref_text}</span>)'
        else:
            return '(<span class="unresolved-ref">??</span>)'

    def _get_theorem_ref_text(self, label):
        """Extract the full reference text (e.g. 'Theorem 1', 'Lemma 2') from a theorem statement"""
        statement = self.theorem_statements.get(label, "")
        # Extract "Theorem 1" or "Lemma 2" etc. from "Theorem 1. statement..."
        match = re.search(r"(Theorem|Lemma|Corollary)\s+(\d+)", statement)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        return "??"

    def _get_theorem_number(self, label):
        """Extract just the number from a theorem statement"""
        statement = self.theorem_statements.get(label, "")
        # Extract number from "Theorem 1." or "Lemma 2." etc.
        match = re.search(r"(Theorem|Lemma|Corollary)\s+(\d+)", statement)
        if match:
            return match.group(2)
        return "??"

    def _make_terms_interactive(self, html):
        """Make all defined terms interactive with popups"""
        # Sort terms by length (longest first) to avoid partial matches
        sorted_terms = sorted(self.definitions.keys(), key=len, reverse=True)

        for term in sorted_terms:
            # Escape special regex characters in the term
            escaped_term = re.escape(term)
            # Simple pattern to match terms - we'll check for existing spans in the replacement function
            pattern = r"\b" + escaped_term + r"s?\b"

            def replace_term(match):
                matched_text = match.group(0)
                # Check if we're already inside a defined-term span
                start_pos = match.start()
                preceding_context = html[:start_pos]

                # Simple check: if there's an unclosed defined-term span tag before this match
                open_spans = preceding_context.count('<span class="defined-term"')
                close_spans = preceding_context.count("</span>")
                if open_spans > close_spans:
                    # We're likely inside a span already, don't wrap
                    return matched_text

                return f'<span class="defined-term" data-term="{term}">{matched_text}</span>'

            html = re.sub(pattern, replace_term, html, flags=re.IGNORECASE)

        return html

    def generate_complete_html(self, body_content):
        """Generate the complete HTML document with styling and JavaScript"""

        # Convert Python dictionaries to JSON for JavaScript
        definitions_json = json.dumps(self.definitions)
        theorems_json = json.dumps(self.theorems)
        theorem_statements_json = json.dumps(self.theorem_statements)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Mathematical Paper</title>

    <!-- MathJax for mathematical notation -->
    <script>
    window.MathJax = {{
        tex: {{
            inlineMath: [['$', '$']],
            displayMath: [['$$', '$$']]
        }},
        startup: {{
            ready: function () {{
                MathJax.startup.defaultReady();
                // Process math after page loads
                MathJax.typesetPromise().then(() => {{
                    console.log('MathJax rendering complete');
                }});
            }}
        }}
    }};
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.min.js"></script>

    <style>
        body {{
            font-family: "Computer Modern", "Latin Modern", serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #fefefe;
        }}

        .definition {{
            background-color: #f0f8ff;
            border: 1px solid #b0d4f1;
            border-radius: 4px;
            padding: 15px;
            margin: 15px 0;
        }}

        .theorem {{
            background-color: #f9f9f9;
            border-left: 4px solid #333;
            padding: 15px;
            margin: 15px 0;
            font-style: italic;
        }}

        .theorem-label {{
            font-weight: bold;
            font-style: normal;
        }}

        .defined-term {{
            color: #0066cc;
            cursor: pointer;
            border-bottom: 1px dotted #0066cc;
            position: relative;
        }}

        .defined-term:hover {{
            background-color: #e6f3ff;
        }}

        .theorem-ref {{
            color: #cc6600;
            cursor: pointer;
            border-bottom: 1px dotted #cc6600;
            position: relative;
        }}

        .theorem-ref:hover {{
            background-color: #fff3e6;
        }}

        .unresolved-ref {{
            color: #cc0000;
            font-weight: bold;
        }}

        .definition-popup {{
            position: absolute;
            background: white;
            border: 2px solid #0066cc;
            border-radius: 6px;
            padding: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            max-width: 300px;
            font-size: 14px;
            line-height: 1.4;
            display: none;
        }}

        details {{
            margin: 15px 0;
        }}

        summary {{
            font-weight: bold;
            cursor: pointer;
            color: #0066cc;
            padding: 5px 0;
        }}

        summary:hover {{
            background-color: #f0f8ff;
        }}

        .proof-content {{
            background-color: #fafafa;
            border-left: 3px solid #ddd;
            padding: 10px 15px;
            margin-top: 10px;
        }}

        h1, h2, h3 {{
            color: #333;
        }}

        p {{
            margin: 1em 0;
        }}
    </style>
</head>
<body>
    {body_content}

    <script>
        // Data from LaTeX conversion
        const definitions = {definitions_json};
        const theorems = {theorems_json};
        const theoremStatements = {theorem_statements_json};

        // Create popup element
        const popup = document.createElement('div');
        popup.className = 'definition-popup';
        document.body.appendChild(popup);

        // Add interactivity to defined terms
        document.querySelectorAll('.defined-term').forEach(term => {{
            term.addEventListener('mouseenter', function() {{
                const termName = this.getAttribute('data-term');
                const definition = definitions[termName];

                if (definition) {{
                    popup.innerHTML = `<strong>${{termName}}:</strong> ${{definition}}`;
                    showPopup(this);

                    // Process any math in the popup with MathJax
                    if (window.MathJax && window.MathJax.typesetPromise) {{
                        MathJax.typesetPromise([popup]).catch((err) => {{
                            console.log('MathJax error in popup:', err);
                        }});
                    }}
                }}
            }});

            term.addEventListener('mouseleave', function() {{
                popup.style.display = 'none';
            }});
        }});

        // Add interactivity to theorem references
        document.querySelectorAll('.theorem-ref').forEach(ref => {{
            ref.addEventListener('mouseenter', function() {{
                const refLabel = this.getAttribute('data-ref');
                const statement = theoremStatements[refLabel];

                if (statement) {{
                    popup.innerHTML = statement;
                    showPopup(this);

                    // Process any math in the popup with MathJax
                    if (window.MathJax && window.MathJax.typesetPromise) {{
                        MathJax.typesetPromise([popup]).catch((err) => {{
                            console.log('MathJax error in theorem popup:', err);
                        }});
                    }}
                }}
            }});

            ref.addEventListener('mouseleave', function() {{
                popup.style.display = 'none';
            }});
        }});

        function showPopup(element) {{
            popup.style.display = 'block';

            const rect = element.getBoundingClientRect();
            popup.style.left = rect.left + window.scrollX + 'px';
            popup.style.top = (rect.bottom + window.scrollY + 2) + 'px';  // Just 2px below the text

            // Adjust if popup would go off screen
            const popupRect = popup.getBoundingClientRect();
            if (popupRect.right > window.innerWidth) {{
                popup.style.left = (window.innerWidth - popupRect.width - 10 + window.scrollX) + 'px';
            }}
            if (popupRect.bottom > window.innerHeight) {{
                popup.style.top = (rect.top + window.scrollY - popupRect.height - 2) + 'px';  // 2px above if no room below
            }}
        }}

        // Hide popup when clicking elsewhere
        document.addEventListener('click', function(e) {{
            if (!e.target.classList.contains('defined-term')) {{
                popup.style.display = 'none';
            }}
        }});
    </script>
</body>
</html>"""


def main_cli():
    if len(sys.argv) < 2:
        print("Usage: python simple_latex2interactive.py input.tex [output.html]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    converter = LaTeXToInteractiveConverter()
    success = converter.convert_file(input_file, output_file)

    if success:
        print("🎉 Interactive HTML generated successfully!")
    else:
        print("Error during conversion :(")
