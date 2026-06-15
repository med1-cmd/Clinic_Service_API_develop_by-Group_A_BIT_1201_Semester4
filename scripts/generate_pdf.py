from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

import os

INPUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'PROJECT_REPORT.md')
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'PROJECT_REPORT.pdf')

def parse_md_lines(lines):
    elems = []
    styles = getSampleStyleSheet()
    heading1 = ParagraphStyle('Heading1', parent=styles['Heading1'], fontSize=16, spaceAfter=6)
    heading2 = ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=12, spaceAfter=4)
    normal = styles['BodyText']
    bullet = ParagraphStyle('Bullet', parent=normal, leftIndent=12)

    for line in lines:
        line = line.rstrip('\n')
        if not line.strip():
            elems.append(Spacer(1, 4))
            continue
        if line.startswith('# '):
            elems.append(Paragraph(line[2:].strip(), heading1))
        elif line.startswith('## '):
            elems.append(Paragraph(line[3:].strip(), heading2))
        elif line.startswith('- '):
            elems.append(Paragraph('&#8226; ' + line[2:].strip(), bullet))
        elif line.lstrip().startswith(('1. ', '2. ', '3. ', '4. ', '5. ')):
            elems.append(Paragraph(line.strip(), normal))
        else:
            elems.append(Paragraph(line.strip(), normal))
    return elems


def main():
    if not os.path.exists(INPUT):
        print('Input markdown not found:', INPUT)
        return
    with open(INPUT, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    elems = parse_md_lines(lines)
    doc.build(elems)
    print('Wrote', OUTPUT)

if __name__ == '__main__':
    main()
