from fpdf import FPDF
import re

class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('NanumGothic', '', 8)
        self.cell(0, 10, f'{self.page_no()}', 0, 0, 'C')

def clean_text(text):
    replacements = {
        '←': '<-',
        '→': '->',
        '↓': 'v',
        '▼': 'v',
        '│': '|',
        '├': '|--',
        '└': '\\--',
        '┌': '+--',
        '┐': '--+',
        '┘': '--+',
        '┬': '-+-',
        '┴': '-+-',
        '─': '-',
        '━': '-',
        '┼': '+',
        '◄': '<',
        '►': '>',
        '●': '*',
        '○': 'o',
        '■': '[#]',
        '□': '[ ]',
        '▪': '-',
        '▫': '-',
        '★': '*',
        '☆': '*',
        '✓': '[v]',
        '✗': '[x]',
        '✔': '[v]',
        '✘': '[x]',
        '•': '*',
        '◦': 'o',
        '–': '-',
        '—': '-',
        '…': '...',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '「': '[',
        '」': ']',
        '『': '[',
        '』': ']',
        '【': '[',
        '】': ']',
        '〈': '<',
        '〉': '>',
        '《': '<<',
        '》': '>>'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

pdf = PDF()
pdf.add_font('NanumGothic', '', 'C:/Windows/Fonts/malgun.ttf', uni=True)
pdf.add_font('NanumGothic', 'B', 'C:/Windows/Fonts/malgunbd.ttf', uni=True)
pdf.set_auto_page_break(auto=True, margin=15)

import os
import sys

# Fix for Korean path encoding on Windows
if sys.platform == 'win32':
    import locale
    locale.setlocale(locale.LC_ALL, '')

script_dir = os.path.dirname(os.path.abspath(__file__))
md_path = os.path.join(script_dir, 'ReadMe', 'readme_ver4.md')
print(f"Looking for: {md_path}")
print(f"Exists: {os.path.exists(md_path)}")

if not os.path.exists(md_path):
    # Try alternative path detection
    import pathlib
    script_dir = pathlib.Path(__file__).parent.resolve()
    md_path = script_dir / 'ReadMe' / 'readme_ver4.md'
    print(f"Alternative path: {md_path}")
    print(f"Alternative exists: {md_path.exists()}")

with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = clean_text(content)
lines = content.split('\n')

pdf.add_page()

in_code_block = False
code_buffer = []

for line in lines:
    if line.startswith('```'):
        if in_code_block:
            pdf.set_font('NanumGothic', '', 8)
            pdf.set_fill_color(240, 240, 240)
            for code_line in code_buffer:
                if pdf.get_y() > 270:
                    pdf.add_page()
                pdf.multi_cell(0, 4, code_line, 0, 'L', True)
            code_buffer = []
            in_code_block = False
        else:
            in_code_block = True
        continue

    if in_code_block:
        code_buffer.append(line)
        continue

    if line.startswith('# '):
        if pdf.get_y() > 250:
            pdf.add_page()
        pdf.set_font('NanumGothic', 'B', 18)
        pdf.ln(5)
        pdf.multi_cell(0, 10, line[2:])
        pdf.ln(3)
    elif line.startswith('## '):
        if pdf.get_y() > 250:
            pdf.add_page()
        pdf.set_font('NanumGothic', 'B', 14)
        pdf.ln(4)
        pdf.multi_cell(0, 8, line[3:])
        pdf.ln(2)
    elif line.startswith('### '):
        if pdf.get_y() > 260:
            pdf.add_page()
        pdf.set_font('NanumGothic', 'B', 12)
        pdf.ln(3)
        pdf.multi_cell(0, 7, line[4:])
        pdf.ln(1)
    elif line.startswith('#### '):
        pdf.set_font('NanumGothic', 'B', 10)
        pdf.ln(2)
        pdf.multi_cell(0, 6, line[5:])
        pdf.ln(1)
    elif line.startswith('|'):
        pdf.set_font('NanumGothic', '', 8)
        if pdf.get_y() > 270:
            pdf.add_page()
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if cells and not all(c.replace('-', '').strip() == '' for c in cells):
            col_width = 180 / max(len(cells), 1)
            for cell in cells:
                pdf.cell(col_width, 5, cell[:30], 1, 0, 'C')
            pdf.ln()
    elif line.startswith('- ') or line.startswith('* '):
        pdf.set_font('NanumGothic', '', 10)
        if pdf.get_y() > 270:
            pdf.add_page()
        pdf.multi_cell(0, 5, '  * ' + line[2:])
    elif line.startswith('---'):
        pdf.ln(2)
    elif line.strip():
        pdf.set_font('NanumGothic', '', 10)
        if pdf.get_y() > 270:
            pdf.add_page()
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        pdf.multi_cell(0, 5, text)

pdf_path = os.path.join(script_dir, 'ReadMe', 'readme_ver4.pdf')
pdf.output(pdf_path)
print(f'PDF created: {pdf_path}')
