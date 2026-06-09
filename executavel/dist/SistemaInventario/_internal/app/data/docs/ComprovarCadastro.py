#gerar pdf com a assinatura do funcionario
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Spacer, Paragraph, Table, SimpleDocTemplate, Image as RLImage
from reportlab.lib.units import cm
from PIL import Image, ImageOps
from pathlib import Path
from io import BytesIO

def CentralizarAssinatura(AssinaturaPath,largura_max=8*cm, altura_max=4*cm):
    img = Image.open(AssinaturaPath).convert("RGBA")

    # Fundo branco para remover transparência antes do crop
    fundo = Image.new("RGBA", img.size, (255, 255, 255, 255))
    fundo.paste(img, mask=img.split()[3])
    img_rgb = fundo.convert("RGB")

    # Recorta espaço em branco ao redor da assinatura
    img_crop = ImageOps.invert(img_rgb)           # inverte para o crop achar bordas escuras
    bbox = img_crop.getbbox()
    if bbox:
        img_rgb = img_rgb.crop(bbox)

    # Calcula dimensões mantendo proporção
    w_orig, h_orig = img_rgb.size
    escala = min(largura_max / w_orig, altura_max / h_orig)
    w_final = w_orig * escala
    h_final = h_orig * escala

    # Converte para buffer em memória (evita salvar arquivo temporário)
    buffer = BytesIO()
    img_rgb.save(buffer, format="PNG")
    buffer.seek(0)

    rl_img = RLImage(buffer, width=w_final, height=h_final)
    rl_img.hAlign = "CENTER"
    return rl_img

#data salve como xx-xx-xxxx e nn como xx/xx/xxxx(pensa como path deste jeito)
def GerarPDF(AssinaturaPath,Funcionario,TipoEpi,ca,codigo,DiaAssinatura,DiaDescarte,registrador):
    #arquivo

    pasta_saida = Path("app\data\docs\comprovantes")
    pasta_saida.mkdir(parents=True, exist_ok=True)

    caminho_pdf = str(pasta_saida / f"comprovante_epi_{Funcionario}_{DiaAssinatura}.pdf")
    Comprovante = SimpleDocTemplate(caminho_pdf, pagesize=A4)

    style = getSampleStyleSheet()
    
    Titulo = Paragraph(f"comprovante epi {Funcionario}: {TipoEpi} {ca}",style['Title'])

    Comprometimento = Paragraph(f"eu {Funcionario}, afirmo que recibi o Equipamento de proteção individual com o codigo de controle {codigo} e que me responsabilizo em caso de perdas e acidentes para a reposição do epi",style['Heading2'])
    #dados do epi
    #dias
    DataDias = [
        ["Recebimento",str(DiaAssinatura)],
        ["Devolver até o dia",str(DiaDescarte)]
    ]
    Dias = Table(DataDias,style=[
        ('GRID',(0,0),(-1,-1),0.5, colors.darkturquoise)
    ])
    #registrado por
    registradoPor = Paragraph(f"Registrado por: {registrador}",style['Heading3'])
    #assinatura
    Assinatura = Paragraph("Assinatura",style['Heading1'])
    ImgAssinatura   = CentralizarAssinatura(AssinaturaPath)

    #salvar pdf
    Comprovante.build([Titulo,Spacer(0,12),Comprometimento,Spacer(0,36),Dias,Spacer(0,12),registradoPor,Spacer(0,36),Assinatura,Spacer(0,12),ImgAssinatura])

#testes
if __name__ == "__main__":
    GerarPDF("app/assinaturas/João Silva_2026-05-29.png","fulano","algum","12345","algum 123","03-03","09-09","Responsavel")