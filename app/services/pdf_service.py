from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

class PDFGenerator:
    @staticmethod
    def generate_discrepancy_report(discrepancia):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        elements = []
        
        elements.append(Paragraph(f"Relatório de Discrepância - {discrepancia['Transportadora']}", styles['Title']))
        elements.append(Spacer(1, 12))
        
        dados = [
            ["Nota Fiscal", discrepancia['NF']],
            ["CEP", discrepancia['CEP']],
            ["Peso (kg)", f"{discrepancia['Peso']:.3f}"],
            ["Valor Cobrado (Frete)", f"R$ {discrepancia['Valor Cobrado (Frete)']:.2f}"],
            ["Valor Correto (Frete)", f"R$ {discrepancia['Valor Correto (Frete)']:.2f}"],
            ["Diferença (Frete)", f"R$ {discrepancia['Diferença (Frete)']:.2f}"],
            ["Valor Total Cobrado", f"R$ {discrepancia['Valor Total Cobrado']:.2f}"],
            ["Valor Total Correto", f"R$ {discrepancia['Valor Total Correto']:.2f}"],
            ["Diferença Total", f"R$ {discrepancia['Diferença Total']:.2f}"]
        ]
        
        tabela = Table(dados, colWidths=[200, 200])
        estilo = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ])
        
        tabela.setStyle(estilo)
        elements.append(tabela)
        
        elementos_impostos = [
            ["Imposto", "Valor Recalculado"],
            ["Advalorem", f"R$ {discrepancia['Impostos Recalculados']['Advalorem']:.2f}"],
            ["GRIS", f"R$ {discrepancia['Impostos Recalculados']['GRIS']:.2f}"],
            ["ICMS", f"R$ {discrepancia['Impostos Recalculados']['ICMS']:.2f}"],
            ["ISS", f"R$ {discrepancia['Impostos Recalculados']['ISS']:.2f}"]
        ]
        
        tabela_impostos = Table(elementos_impostos, colWidths=[200, 200])
        tabela_impostos.setStyle(estilo)
        elements.append(Spacer(1, 12))
        elements.append(tabela_impostos)
        
        # Observações
        obs_texto = """
        <b>Observações:</b><br/>
        Esta diferença deve ser contestada com a transportadora dentro do prazo contratual.
        Recomenda-se anexar este documento à solicitação formal de reembolso.
        """
        elements.append(Paragraph(obs_texto, styles['Normal']))
        
        doc.build(elements)
        return buffer