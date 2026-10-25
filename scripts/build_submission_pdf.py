#!/usr/bin/env python3
"""Build a two-page description, original sketch and complete vector preview panels.

Usage: python scripts/build_submission_pdf.py PREVIEW.pdf BLOCKS.json ORIGINAL.pdf
The preview is a static rendering of the prepared HTML and all 14 Vega charts.
It is not evidence that GitHub Pages has deployed the revision.
"""
import io
import json
import pathlib
import re
import sys
from html import escape
import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'output/pdf/FIT3179_DV2_Tony_Su_33809453.pdf'
FONT='/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('ReviewSans',FONT+'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('ReviewSansBold',FONT+'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('ReviewSans',normal='ReviewSans',bold='ReviewSansBold')
BLUE=colors.HexColor('#245883')
BODY=ParagraphStyle('Body',fontName='ReviewSans',fontSize=10,leading=14,spaceAfter=7)
HEADING=ParagraphStyle('Heading',parent=BODY,fontName='ReviewSansBold',fontSize=10.5,spaceBefore=9,spaceAfter=5)
TITLE=ParagraphStyle('Title',parent=BODY,fontSize=16,textColor=BLUE,spaceBefore=12,spaceAfter=12)
SMALL=ParagraphStyle('Small',parent=BODY,fontSize=8.5,leading=12)

def paragraph(text,style=BODY):
    return Paragraph(escape(text),style)

def link(label,url):
    return Paragraph(f'<link href="{escape(url,quote=True)}" color="#0563c1"><u>{escape(label)}</u></link>',BODY)

def page_decoration(canvas,doc):
    canvas.setFillColor(colors.HexColor('#609acf'))
    canvas.setFont('ReviewSans',10)
    canvas.drawString(66,A4[1]-42,'FIT3179 Data Visualisation, Monash University')
    canvas.setFillColor(colors.black)
    canvas.setFont('ReviewSans',9)
    canvas.drawRightString(A4[0]-55,28,str(doc.page))

def description_pages():
    text=(ROOT/'submission/PDF_DESCRIPTION.md').read_text()
    sections={}
    for heading,body in re.findall(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)',text,re.M|re.S):sections[heading]=body.strip()
    stream=io.BytesIO()
    doc=SimpleDocTemplate(stream,pagesize=A4,leftMargin=66,rightMargin=55,topMargin=67,bottomMargin=48)
    story=[]
    table=Table([['Name','Tony Su'],['Student ID','33809453'],['Studio Session','Studio 1']],colWidths=[110,364])
    table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'ReviewSans'),('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),.6,colors.black),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story.extend([table,Spacer(1,20),paragraph('Part A: URL of the Visualisation',TITLE),paragraph('Walking the Uneven Map',HEADING),link('https://tsuu0008.github.io/FIT3179_visualisation_2/','https://tsuu0008.github.io/FIT3179_visualisation_2/'),Spacer(1,7),paragraph('Part B: Domain Description',TITLE)])
    for name,label in [('Domain','Describe your domain chosen for DV II'),('Why and who','Describe the Why and Who aspects of your DV II'),('What','Describe the “What” aspect of your DV II')]:
        story.append(paragraph(label,HEADING))
        for chunk in sections[name].split('\n\n'):story.append(paragraph(chunk))
    story.append(PageBreak())
    story.append(paragraph('Describe the “How” aspect of your DV II',HEADING))
    for chunk in sections['How'].split('\n\n'):story.append(paragraph(chunk))
    story.append(paragraph('Sources',HEADING))
    for label,url in [
        ('Victorian Government Recreation Tracks','https://discover.data.vic.gov.au/dataset/recreation-tracks'),
        ('ABS Regional population 2024–25','https://www.abs.gov.au/statistics/people/population/regional-population/2024-25'),
        ('ABS Local Government Areas 2025 (GDA2020)','https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/LGA_2025_AUST_GDA2020.zip'),
        ('Parks Victoria: public walking grades (context only)','https://www.parks.vic.gov.au/things-to-do/hiking-and-bushwalking/choose-the-right-hike/how-walking-tracks-are-rated')]:story.append(link(label,url))
    story.append(paragraph('AI acknowledgement',HEADING))
    story.append(paragraph(sections['AI acknowledgement']))
    doc.build(story,onFirstPage=page_decoration,onLaterPages=page_decoration)
    result=fitz.open(stream=stream.getvalue(),filetype='pdf')
    assert len(result)==2,f'Description unexpectedly occupies {len(result)} pages'
    return result

def main():
    preview=fitz.open(sys.argv[1]); blocks=json.loads(pathlib.Path(sys.argv[2]).read_text())
    original=fitz.open(sys.argv[3]); result=description_pages()
    result.insert_pdf(original,from_page=2,to_page=3)
    # Break only outside complete chart cards and paired-chart rows.
    items=list(blocks.values())
    intervals=[(b['top'],b['bottom']) for b in items if any(c in b['classes'].split() for c in ['chart-card','two-col','grade-guide'])]
    bottom=max(b['bottom'] for b in items)
    candidates=sorted({0,bottom}|{round(v,2) for b in items for v in [b['top'],b['bottom']] if not any(lo+1<v<hi-1 for lo,hi in intervals)})
    segments=[];start=0
    while start<bottom-1:
        eligible=[p for p in candidates if start+20<p<=min(bottom,start+2050)]
        end=max(eligible) if eligible else min(p for p in candidates if p>start+20)
        segments.append((start,end));start=end
    if len(segments)>1 and segments[-1][1]-segments[-1][0]<700 and segments[-1][1]-segments[-2][0]<2600:
        segments[-2:]=[(segments[-2][0],segments[-1][1])]
    for i,(top,bottom) in enumerate(segments):
        page=result.new_page(width=A4[0],height=A4[1])
        page.insert_text((66,42),'FIT3179 Data Visualisation, Monash University',fontname='helv',fontsize=10,color=(.38,.60,.81))
        page.insert_text((66,77),'Part D: Full-size visualisation preview',fontname='helv',fontsize=15,color=(.14,.34,.51))
        page.insert_text((66,99),f'Prepared revision | 25 October 2026 | Segment {i+1} of {len(segments)}',fontname='helv',fontsize=10)
        clip=fitz.Rect(0,top*.75,1363*.75,bottom*.75)
        area=fitz.Rect(50,116,A4[0]-40,A4[1]-45)
        ratio=min(area.width/clip.width,area.height/clip.height)
        dest=fitz.Rect(area.x0,area.y0,area.x0+clip.width*ratio,area.y0+clip.height*ratio)
        page.show_pdf_page(dest,preview,0,clip=clip)
        page.insert_text((A4[0]-64,A4[1]-28),str(len(result)),fontname='helv',fontsize=9)
    result.set_metadata({'title':'FIT3179 DV II — Walking the Uneven Map','author':'Tony Su','subject':'Recorded grade explanations, verified ABS 2025 boundaries and complete chart panels'})
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    result.save(OUTPUT,garbage=4,deflate=True)
    print(json.dumps({'output':str(OUTPUT),'pages':len(result),'preview_segments':len(segments),'segments':segments},indent=2))

if __name__=='__main__':main()
