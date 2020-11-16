#!/usr/bin/env python2.7

import sys
import json
import copy
from os import path
import requests
import xlrd
import config
from datetime import datetime
from static import static_text

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import BaseDocTemplate, Frame, Spacer, Table, TableStyle, Paragraph, PageTemplate, PageBreak, Image

limsUsername = config.CONFIG_PATHS['limsUsername']
limsPassword = config.CONFIG_PATHS['limsPassword']
pmauth = config.CONFIG_PATHS['pmauth']
limsapi = config.CONFIG_PATHS['limsapi']

def create_reports(outdir, sampleID): #infile
    
    sample_record = get_record_info_limsapi(sampleID)
    Report(outdir, sampleID, sample_record)

    print ('Reports written successfully.')

def get_record_info_limsapi(sampleID):

    print(sampleID)
    
    auth_url = pmauth
    token_headers = {'content-type':'application/json'}
    token_body = {'username':'{}'.format(limsUsername),'password':'{}'.format(limsPassword)}

    token_req = requests.post(auth_url, headers=token_headers, data=json.dumps(token_body))
    token = token_req.json()

    print("Token request status code:")
    print(token_req.status_code)
    
    #Get entire oncorseq spreadsheet or by just sample GET IS TO GET AN ENTRY
    sample_url = "{}/{}".format(limsapi,sampleID)
    print(sample_url)
    sample_headers = {'accept':'application/json', 'Authorization':'{}'.format(token['Token'])}
    sample_req = requests.get(sample_url, headers=sample_headers)
    print(sample_req)
    sample_record = sample_req.json()

    return sample_record['dataRecords'][0]['fields']

class Report():

    def __init__(self, outdir, sampleID, sample_record):
        self.sample_record = sample_record
        self.sampleID = sampleID

        self.outfile = path.join(outdir, '{}.pdf'.format(self.sampleID))

        self.__set_styles()
        self.__set_tables()
        self.__set_heading_table()
        self.generate_report()

    def __set_styles(self):
        self.styles = getSampleStyleSheet()
        self.standard_spacer = Spacer(1, 0.2*inch)
        self.smaller_spacer = Spacer(1, 0.15*inch)
        self.table_style = [
            ('BACKGROUND', 
                (0,0), (-1,0), colors.HexColor('#99CCFF')),
            ('LINEBELOW', 
                (0,0), (-1,0), 0.5, colors.black),
            ('BOX', 
                (0,0), (-1,-1), 0.5, colors.black), 
            ('VALIGN', 
                (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', 
                (0,'splitlast'), (-1,'splitlast'), 0.5, colors.black),
            ('ROWBACKGROUNDS',
                (0,1), (-1,-1), 
                (colors.HexColor('#FFFFFF'), colors.HexColor('#D6EBFF')))
        ]
        self.comment_style = ParagraphStyle('Regular indents', firstLineIndent=25, spaceAfter=10)
        self.no_genomic_findings = ParagraphStyle('Regular indents', fontSize=10, fontName='Helvetica-Bold')
        self.text_block_style = ParagraphStyle('Fine Print', fontSize=9)
        self.tier_text_style = ParagraphStyle('Hanging indents', fontSize=9, leftIndent=35, firstLineIndent=-35)
        self.centered_text = ParagraphStyle('Centered', alignment='TA_CENTER')
        self.reference_text_style = ParagraphStyle('Regular indents', fontSize=10, leftIndent=35, firstLineIndent=-20)

    def __set_tables(self):

        self.available_table_names = []
        self.all_tables = {}
        self.interpretations = {}
        self.static_text = static_text()

    def __set_heading_table(self):
        self.heading_table = [
            ['Patient Name:', self.sample_record['Name']],
            ['DOB:', self.sample_record['DOB']],
            ['Sex:', self.sample_record['Sex']],
            ['MRN:', self.sample_record['MRN']],
            ['Tumor Type:', self.sample_record['TumorType']],
            ['Primary site:', self.sample_record['PrimarySite']],
            ['Tissue Tested:' , self.sample_record['TissueTested']]
        ]

        self.heading_table_2 = [
            ['Ordering Physician:', self.sample_record['OrderingPhysicianName']],
            ['Neoplastic content:', "{}%".format(self.sample_record['TumorPercent'])],
            ['Specimen ID:', self.sample_record['PathologyId']],
            ['Sample Type:', self.sample_record['SampleType']],
            ['Sample Collected:', self.sample_record['DateCollected']],
            ['Sample Received:', self.sample_record['DateReceivedInLab']],
            ['Date of Service:', self.sample_record['DateOfService']]
        ]

    def __resize(self, img, height):
        iw, ih = img.getSize()
        aspect = iw / float(ih)
        width = height*aspect
        return (width, height)

    def __page_header(self, canvas, doc):
        canvas.saveState()
        high=10.3

        logo = ImageReader('{}/wcm_nyp_ClinicalGenomicsLab_Letterhead_CB_Opt01r.png'.format(path.dirname(path.realpath(__file__))))
        logo_width, logo_height = self.__resize(logo, inch*0.75)
        canvas.drawImage(logo, inch*0.5, inch*10.1, width=logo_width, 
                                                     height=logo_height, 
                                                     mask='auto')
        canvas.setFont("Helvetica",14)
        canvas.drawString(inch*2.75, inch*(high-.4), 'Oncomine Comprehensive Report')
        canvas.setFont("Helvetica",8)
        canvas.drawString(inch*6.175, inch*10.6, 'Wayne Tam, MD, PhD - Director')
        canvas.drawString(inch*6.175, inch*10.5, 'Lab of Oncology-Molecular Detection')
        canvas.drawString(inch*6.175, inch*10.4, 'Weill Cornell Medicine')
        canvas.drawString(inch*6.175, inch*10.3, '1300 York Avenue K502, LC-904')
        canvas.drawString(inch*6.175, inch*10.2, 'New York, NY 10065')
        canvas.drawString(inch*6.175, inch*10.1, 'T:646.962.3816 F:212.746.8362')

        canvas.setFillColorRGB(255,0,0)
        canvas.setFillColorRGB(0,0,0)

        canvas.drawString(inch*7.5, inch*(0.4), 'Page {}'.format(doc.page))
        canvas.line(inch/2, inch*(high-0.5), inch*8, inch*(high-0.5))
        canvas.drawString(inch/2, inch*(high-0.4), "GX{}".format(self.sample_record['GX']))
        
        canvas.restoreState()

    def generate_report(self):

        print ('Writing report PDF {}...'.format(self.outfile))

        report = BaseDocTemplate(self.outfile,
                                 pagesize=letter,
                                 leftMargin=inch/2,
                                 rightMargin=inch/2,
                                 topMargin=inch,
                                 bottomMargin=inch)
        frame = Frame(report.leftMargin, 
                      report.bottomMargin, 
                      report.width, 
                      report.height - inch*0.3)
        report.addPageTemplates([PageTemplate(id='normal', 
                                              frames=frame, 
                                              onPage=self.__page_header
                                              )])

        el = []

        ht = Table(self.heading_table, hAlign='LEFT')
        ht.setStyle(TableStyle([('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold')]))

        ht2 = Table(self.heading_table_2, hAlign='RIGHT')
        ht2.setStyle(TableStyle([('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold')]))

        ht_w = 3.75 * inch
        ht2_w = 4 * inch

        data = [[ht, ht2]]
        data_table = Table(data, colWidths=[ht_w, ht2_w])
        el.append(data_table)

        el.append(Spacer(1, 0.2*inch))

        el.append(Paragraph("FAILED REPORT:", self.no_genomic_findings))
        el.append(Paragraph("{}".format(self.sample_record['PathologyNotes']), self.no_genomic_findings))
        el.append(Spacer(1, 0.2*inch))

        for text in self.static_text['tiers']:
            el.append(Paragraph(text, self.tier_text_style))

        el.append(self.standard_spacer)

        el.append(Paragraph(self.static_text['method'], self.text_block_style))
        el.append(Spacer(1, 0.2*inch))

        el.append(Paragraph(self.static_text['technical assessment'], self.text_block_style))
        el.append(Spacer(1, 0.2*inch))

        el.append(Paragraph(self.static_text['disclaimer'], self.text_block_style))

        el.append(self.standard_spacer)

        hotspot_1 = [(Paragraph(self.static_text['hotspot_1'], self.text_block_style))]
        hotspot_2 = [(Paragraph(self.static_text['hotspot_2'], self.text_block_style))]
        hotspot_3 = [(Paragraph(self.static_text['hotspot_3'], self.text_block_style))]

        cds = [(Paragraph(self.static_text['cds'], self.text_block_style))]

        cnv_1 = [(Paragraph(self.static_text['cnv_1'], self.text_block_style))]
        cnv_2 = [(Paragraph(self.static_text['cnv_2'], self.text_block_style))]

        fusion = [(Paragraph(self.static_text['fusion'], self.text_block_style))]
        
        gene_list = [[hotspot_1, hotspot_2, hotspot_3, cds, cnv_1, cnv_2, fusion]]

        gene_list_table = Table(gene_list)
        el.append(gene_list_table)

        report.build(el)

if __name__ == '__main__':
    
    sampleID = sys.argv[1]
    outdir = sys.argv[2]
    create_reports(outdir, sampleID)
