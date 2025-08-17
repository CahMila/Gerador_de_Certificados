import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Função para escolher arquivo
def escolher_arquivo(titulo, tipos):
    root = tk.Tk()
    root.withdraw()
    caminho = filedialog.askopenfilename(title=titulo, filetypes=tipos)
    root.destroy()
    return caminho

# Função para escolher posição clicando na imagem
def escolher_posicao(imagem_path):
    coords = []

    def on_click(event):
        coords.append((event.x, event.y))
        janela.destroy()

    janela = tk.Tk()
    janela.title("Clique no local para inserir o nome")

    img = Image.open(imagem_path)
    img_tk = ImageTk.PhotoImage(img)

    canvas = tk.Canvas(janela, width=img.width, height=img.height)
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=img_tk)

    canvas.bind("<Button-1>", on_click)
    janela.mainloop()

    return coords[0] if coords else (0, 0)

# Função para centralizar texto
def centralizar_texto(draw, texto, fonte, posicao):
    bbox = draw.textbbox((0, 0), texto, font=fonte)
    largura_texto = bbox[2] - bbox[0]
    altura_texto = bbox[3] - bbox[1]
    x = posicao[0] - largura_texto // 2
    y = posicao[1] - altura_texto // 2
    return x, y

# Função para ajustar tamanho da fonte
def ajustar_tamanho_fonte(draw, texto, fonte_path, tamanho_max, largura_max):
    tamanho = tamanho_max
    while tamanho > 10:
        fonte = ImageFont.truetype(fonte_path, tamanho)
        largura_texto = draw.textbbox((0, 0), texto, font=fonte)[2]
        if largura_texto <= largura_max:
            return fonte
        tamanho -= 1
    return ImageFont.truetype(fonte_path, 10)

# Escolher arquivos
arquivo_nomes = escolher_arquivo('Selecione o arquivo CSV com os nomes', [('CSV', '*.csv')])
imagem_certificado = escolher_arquivo('Selecione a imagem do certificado', [('Imagem', '*.png;*.jpg;*.jpeg')])

# Escolher posição do nome
posicao_nome = escolher_posicao(imagem_certificado)
print(f"📍 Posição escolhida: {posicao_nome}")

# Fonte personalizada
fonte_nome = os.path.join(os.path.dirname(__file__), 'GreatVibes-Regular.ttf')
tamanho_fonte_max = 80
largura_max_nome = 1000

# Ler CSV
try:
    df = pd.read_csv(arquivo_nomes)
except Exception as e:
    messagebox.showerror("Erro ao ler CSV", str(e))
    exit()

if df.empty or df.shape[1] < 1:
    messagebox.showerror("Erro", "O arquivo CSV está vazio ou inválido.")
    exit()

# Pasta de saída
pasta_saida = os.path.join(os.path.dirname(arquivo_nomes), 'certificados')
os.makedirs(pasta_saida, exist_ok=True)

# Gerar certificados
total = len(df)
for index, row in enumerate(df.itertuples(index=False), start=1):
    nome = str(row[0]).strip()
    if not nome:
        continue

    print(f"Gerando certificado {index}/{total}: {nome}")

    img = Image.open(imagem_certificado).convert("RGB")
    draw = ImageDraw.Draw(img)

    fonte = ajustar_tamanho_fonte(draw, nome, fonte_nome, tamanho_fonte_max, largura_max_nome)
    pos_centrada = centralizar_texto(draw, nome, fonte, posicao_nome)
    draw.text(pos_centrada, nome, font=fonte, fill=(0, 0, 0))

    caminho_pdf = os.path.join(pasta_saida, f'certificado_{index}_{nome}.pdf')
    img.save(caminho_pdf, "PDF")

print("\n🎉 Todos os certificados foram gerados com sucesso!")