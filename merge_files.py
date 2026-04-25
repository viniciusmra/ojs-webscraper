import os
import glob
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import img2pdf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import tempfile


def find_cover_file(folder_path):
    """Encontra o arquivo de capa na pasta"""
    cover_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
    for ext in cover_extensions:
        cover_path = os.path.join(folder_path, f"capa{ext}")
        if os.path.exists(cover_path):
            return cover_path
    return None


def convert_image_to_pdf_a4(image_path, output_path):
    """Converte uma imagem para PDF no formato A4"""
    # Abrir a imagem
    img = Image.open(image_path)

    # Converter para RGB se necessário
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Redimensionar para A4 (595x842 pontos)
    img_resized = img.resize((595, 842), Image.Resampling.LANCZOS)

    # Criar PDF temporário
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Salvar imagem temporariamente
    temp_img_path = tempfile.mktemp(suffix=".jpg")
    img_resized.save(temp_img_path, "JPEG", quality=95)

    # Adicionar imagem ao PDF
    c.drawImage(temp_img_path, 0, 0, width, height)
    c.save()

    # Limpar arquivo temporário
    os.remove(temp_img_path)


def get_indexed_pdfs(folder_path):
    """Obtém lista de PDFs indexados ordenados numericamente"""
    pdf_pattern = os.path.join(folder_path, "[0-9][0-9]*.pdf")
    pdf_files = glob.glob(pdf_pattern)

    # Ordenar pelos números no início do nome
    def extract_number(filename):
        basename = os.path.basename(filename)
        number_str = ""
        for char in basename:
            if char.isdigit():
                number_str += char
            else:
                break
        return int(number_str) if number_str else 0

    return sorted(pdf_files, key=extract_number)


def merge_pdfs_to_folder(folder_path):
    """
    Junta todos os PDFs de uma pasta em um único arquivo

    Args:
        folder_path (str): Caminho para a pasta com os arquivos
    """
    if not os.path.exists(folder_path):
        print(f"Erro: A pasta '{folder_path}' não existe.")
        return False

    output_filename = "00_-_edicao_completa.pdf"
    writer = PdfWriter()
    files_processed = []

    # 1. Processar arquivo de capa primeiro
    cover_file = find_cover_file(folder_path)
    if cover_file:
        print(f"Encontrada capa: {cover_file}")

        if cover_file.lower().endswith(".pdf"):
            # Se já é PDF, adicionar diretamente
            reader = PdfReader(cover_file)
            for page in reader.pages:
                writer.add_page(page)
        else:
            # Se é imagem, converter para PDF A4
            temp_cover_pdf = tempfile.mktemp(suffix=".pdf")
            convert_image_to_pdf_a4(cover_file, temp_cover_pdf)

            reader = PdfReader(temp_cover_pdf)
            for page in reader.pages:
                writer.add_page(page)

            os.remove(temp_cover_pdf)

        files_processed.append(cover_file)

    # 2. Processar PDFs indexados em ordem
    indexed_pdfs = get_indexed_pdfs(folder_path)

    for pdf_file in indexed_pdfs:
        print(f"Processando: {os.path.basename(pdf_file)}")
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                writer.add_page(page)
            files_processed.append(pdf_file)
        except Exception as e:
            print(f"Erro ao processar {pdf_file}: {e}")

    # 3. Salvar arquivo final
    if files_processed:
        output_path = os.path.join(folder_path, output_filename)

        try:
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            print(f"\nArquivo mesclado criado com sucesso: {output_path}")
            print(f"Total de arquivos processados: {len(files_processed)}")
            print("Arquivos incluídos:")
            for file in files_processed:
                print(f"  - {os.path.basename(file)}")
            return True

        except Exception as e:
            print(f"Erro ao salvar arquivo final: {e}")
            return False
    else:
        print("Nenhum arquivo válido encontrado para mesclar.")
        return False


def main():
    """Função principal"""
    print("=== MESCLADOR DE PDFs ===")
    print("Digite 'sair' ou 'quit' para encerrar o programa")
    print()

    while True:
        # Solicitar pasta do usuário
        folder_path = input("Digite o caminho da pasta com os arquivos: ").strip()

        # Verificar se o usuário quer sair
        if folder_path.lower() in ["sair", "quit", "exit"]:
            print("Encerrando o programa...")
            break

        # Remover aspas se existirem
        if folder_path.startswith('"') and folder_path.endswith('"'):
            folder_path = folder_path[1:-1]

        # Verificar se a pasta existe
        if not folder_path:
            print("Por favor, digite um caminho válido.")
            continue

        # Executar merge
        success = merge_pdfs_to_folder(folder_path)

        if success:
            print("\n✅ Processo concluído com sucesso!")
        else:
            print("\n❌ Erro durante o processamento.")

        print("-" * 50)
        print()


if __name__ == "__main__":
    main()
