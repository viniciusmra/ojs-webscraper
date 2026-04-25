import requests
from bs4 import BeautifulSoup
import time
import os
import yaml
from urllib.parse import urljoin
from datetime import datetime


class OJSSession:
    def __init__(self, username=None, password=None):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        self.base_url = "https://revistas.ufpi.br"
        self.logged_in = False
        self.username = username
        self.password = password

    def login(self, username=None, password=None):
        """Faz login no sistema OJS"""
        # Usar credenciais fornecidas ou as do construtor
        login_user = username or self.username
        login_pass = password or self.password

        if not login_user or not login_pass:
            print("❌ Credenciais não fornecidas")
            return False

        login_url = f"{self.base_url}/index.php/equador/login"

        print(f"🔐 Fazendo login automático como: {login_user}")

        # Primeiro, acessa a página de login para obter o formulário
        response = self.session.get(login_url)

        if response.status_code != 200:
            print(f"❌ Erro ao acessar página de login: {response.status_code}")
            return False

        # Parse do HTML para extrair dados do formulário
        soup = BeautifulSoup(response.text, "html.parser")
        form = soup.find("form", {"id": "signinForm"})

        if not form:
            print("❌ Formulário de login não encontrado")
            return False

        # Extrair action do formulário
        action_url = form.get("action")
        if not action_url.startswith("http"):
            action_url = urljoin(self.base_url, action_url)

        # Preparar dados do login
        login_data = {
            "username": login_user,
            "password": login_pass,
            "remember": "1",  # Checkbox "Lembrete com login e senha"
        }

        # Adicionar campos ocultos do formulário
        hidden_inputs = form.find_all("input", {"type": "hidden"})
        for hidden_input in hidden_inputs:
            name = hidden_input.get("name")
            value = hidden_input.get("value", "")
            if name:
                login_data[name] = value

        print(f"📨 Enviando dados de login para: {action_url}")

        # Fazer login
        response = self.session.post(action_url, data=login_data)

        if response.status_code == 200:
            # Verificar se o login foi bem-sucedido
            if (
                "login" not in response.url.lower()
                and "error" not in response.text.lower()
            ):
                print("✅ Login realizado com sucesso!")
                self.logged_in = True
                return True
            else:
                print("❌ Falha no login - credenciais inválidas")
                return False
        else:
            print(f"❌ Erro no login: {response.status_code}")
            return False

    def get_page(self, url):
        """Obtém uma página, fazendo login automático se necessário"""
        print(f"🌐 Acessando: {url}")

        response = self.session.get(url, timeout=30)

        if response.status_code == 200:
            # Verificar se foi redirecionado para página de login
            if "login" in response.url.lower() and not self.logged_in:
                print("🔒 Página requer autenticação - fazendo login automático...")

                if self.login():
                    print("🔄 Tentando acessar a página novamente...")
                    response = self.session.get(url, timeout=30)

                    if response.status_code == 200:
                        print("✅ Página carregada após login!")
                        return response.text
                    else:
                        print(f"❌ Erro após login: {response.status_code}")
                        return None
                else:
                    print("❌ Não foi possível fazer login automático")
                    return None
            else:
                print("✅ Página carregada com sucesso!")
                return response.text
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return None


def save_html_to_file(html_content, filename="page_content.html"):
    """Salva o conteúdo HTML em arquivo"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"💾 HTML salvo em: {filename}")


def analyze_page(html_content):
    """Faz análise básica da página"""
    soup = BeautifulSoup(html_content, "html.parser")

    print(f"\n📊 ESTATÍSTICAS DA PÁGINA:")
    print(f"Título: {soup.title.string if soup.title else 'Não encontrado'}")
    print(f"Total de links: {len(soup.find_all('a'))}")
    print(f"Total de formulários: {len(soup.find_all('form'))}")
    print(f"Total de tabelas: {len(soup.find_all('table'))}")
    print(f"Total de divs: {len(soup.find_all('div'))}")


def extract_submission_ids(html_content):
    """Extrai os IDs das submissões da página de review"""
    soup = BeautifulSoup(html_content, "html.parser")

    # Procurar a div com id "submissions"
    submissions_div = soup.find("div", {"id": "submissions"})

    if not submissions_div:
        print("❌ Div 'submissions' não encontrada")
        return []

    print("✅ Div 'submissions' encontrada!")

    # Procurar todas as linhas <tr> dentro da div
    rows = submissions_div.find_all("tr", {"valign": "top"})

    submission_ids = []

    for row in rows:
        # Pegar a primeira <td> de cada linha
        first_td = row.find("td")

        if first_td and first_td.get_text().strip().isdigit():
            submission_id = first_td.get_text().strip()
            submission_ids.append(submission_id)
            print(f"📄 ID encontrado: {submission_id}")

    return submission_ids


def extract_submission_title(ojs_session, submission_id):
    """Extrai o título de uma submissão específica"""
    submission_url = (
        f"{ojs_session.base_url}/index.php/equador/editor/submission/{submission_id}"
    )

    print(f"🔗 Acessando submissão {submission_id}...")

    html_content = ojs_session.get_page(submission_url)

    if not html_content:
        print(f"❌ Erro ao acessar submissão {submission_id}")
        return None

    soup = BeautifulSoup(html_content, "html.parser")

    # Procurar a div com id "submission"
    submission_div = soup.find("div", {"id": "submission"})

    if not submission_div:
        print(f"❌ Div 'submission' não encontrada para ID {submission_id}")
        return None

    # Procurar a célula com texto "Título"
    title_cells = submission_div.find_all("td")

    for i, cell in enumerate(title_cells):
        if cell.get_text().strip() == "Título":
            # Pegar a próxima célula (td) que contém o título
            if i + 1 < len(title_cells):
                title_cell = title_cells[i + 1]
                title = title_cell.get_text().strip()
                print(f"✅ Título encontrado: {title}")
                return title

    print(f"❌ Título não encontrado para ID {submission_id}")
    return None


def get_all_submission_titles(ojs_session, submission_ids):
    """Obtém os títulos de todas as submissões"""
    titles = {}

    print(f"\n📚 COLETANDO TÍTULOS DE {len(submission_ids)} SUBMISSÕES:")
    print("=" * 60)

    for i, submission_id in enumerate(submission_ids, 1):
        print(f"\n[{i}/{len(submission_ids)}] Processando ID: {submission_id}")

        title = extract_submission_title(ojs_session, submission_id)

        if title:
            titles[submission_id] = title
        else:
            titles[submission_id] = "Título não encontrado"

        # Pequena pausa entre requisições
        time.sleep(1)

    return titles


def extract_submission_details(ojs_session, submission_id):
    """Extrai todos os detalhes de uma submissão específica"""
    submission_url = (
        f"{ojs_session.base_url}/index.php/equador/editor/submission/{submission_id}"
    )

    print(f"🔗 Acessando submissão {submission_id}...")

    html_content = ojs_session.get_page(submission_url)

    if not html_content:
        print(f"❌ Erro ao acessar submissão {submission_id}")
        return None

    soup = BeautifulSoup(html_content, "html.parser")

    submission_data = {
        "id": submission_id,
        "titulo": None,
        "resumo": None,
        "autores": [],
        "situacao": None,
        "data_iniciado": None,
    }

    # Extrair título e resumo da div "titleAndAbstract"
    title_abstract_div = soup.find("div", {"id": "titleAndAbstract"})
    if title_abstract_div:
        cells = title_abstract_div.find_all("td")
        for i, cell in enumerate(cells):
            cell_text = cell.get_text().strip()
            if cell_text.lower() == "título":
                if i + 1 < len(cells):
                    submission_data["titulo"] = cells[i + 1].get_text().strip()
            elif cell_text.lower() == "resumo":
                if i + 1 < len(cells):
                    submission_data["resumo"] = cells[i + 1].get_text().strip()

    # Extrair autores da div "authors"
    authors_div = soup.find("div", {"id": "authors"})
    if authors_div:
        cells = authors_div.find_all("td")
        for i, cell in enumerate(cells):
            if cell.get_text().strip().lower() == "nome":
                if i + 1 < len(cells):
                    author_name = cells[i + 1].get_text().strip()
                    if author_name and author_name not in submission_data["autores"]:
                        submission_data["autores"].append(author_name)

    # Extrair situação e data da div "status"
    status_div = soup.find("div", {"id": "status"})
    if status_div:
        cells = status_div.find_all("td")
        for i, cell in enumerate(cells):
            cell_text = cell.get_text().strip()
            if cell_text.lower() == "situação":
                if i + 1 < len(cells):
                    submission_data["situacao"] = cells[i + 1].get_text().strip()
            elif cell_text.lower() == "iniciado":
                if i + 1 < len(cells):
                    date_text = cells[i + 1].get_text().strip()
                    # Converter de YYYY-MM-DD para DD/MM/AAAA
                    try:
                        date_obj = datetime.strptime(date_text, "%Y-%m-%d")
                        submission_data["data_iniciado"] = date_obj.strftime("%d/%m/%Y")
                    except ValueError:
                        submission_data["data_iniciado"] = (
                            date_text  # Se não conseguir converter, manter original
                        )

    print(f"✅ Dados extraídos para ID {submission_id}")
    return submission_data


def get_all_submissions_data(ojs_session, submission_ids):
    """Obtém todos os dados de todas as submissões"""
    submissions_data = {}

    print(f"\n📚 COLETANDO DADOS DE {len(submission_ids)} SUBMISSÕES:")
    print("=" * 60)

    for i, submission_id in enumerate(submission_ids, 1):
        print(f"\n[{i}/{len(submission_ids)}] Processando ID: {submission_id}")

        submission_data = extract_submission_details(ojs_session, submission_id)

        if submission_data:
            submissions_data[submission_id] = submission_data

        # Pequena pausa entre requisições
        time.sleep(1)

    return submissions_data


def save_to_yaml(data, filename="submissions_data.yaml"):
    """Salva os dados em arquivo YAML"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
        print(f"💾 Dados salvos em YAML: {filename}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar YAML: {e}")
        return False


def extract_review_data(ojs_session, submission_id):
    """Extrai dados da página de revisão de uma submissão específica"""
    review_url = f"{ojs_session.base_url}/index.php/equador/editor/submissionReview/{submission_id}"

    print(f"🔍 Acessando página de revisão {submission_id}...")

    html_content = ojs_session.get_page(review_url)

    if not html_content:
        print(f"❌ Erro ao acessar página de revisão {submission_id}")
        return None

    soup = BeautifulSoup(html_content, "html.parser")

    review_data = {
        "revisores": [],
        "versao_avaliacao": None,
        "versao_autor": [],
    }

    # Extrair revisores
    reviewer_rows = soup.find_all("tr", {"class": "reviewer"})
    print(f"🔍 Encontrados {len(reviewer_rows)} revisores")

    for idx, reviewer_row in enumerate(reviewer_rows):
        reviewer_info = {
            "nome": None,
            "recomendacao": None,
            "data_recomendacao": None,
            "arquivo_revisor": None,
            "data_arquivo_revisor": None,
            "comentarios": None,
        }

        # Nome do revisor (primeira tabela)
        r2_cell = reviewer_row.find("td", {"class": "r2"})
        if r2_cell:
            h4_tag = r2_cell.find("h4")
            if h4_tag:
                reviewer_info["nome"] = h4_tag.get_text().strip()
                print(f"👤 Revisor {idx+1}: {reviewer_info['nome']}")

        # Buscar a próxima tabela após este revisor (segunda tabela com informações)
        current_element = reviewer_row.parent  # Pegar a tabela que contém o revisor

        # Procurar a próxima tabela após a tabela do revisor
        next_table = current_element.find_next_sibling("table")

        if next_table:
            print(f"📋 Analisando tabela de informações do revisor {idx+1}")

            # Buscar todas as linhas da tabela de informações
            info_rows = next_table.find_all("tr")

            for row in info_rows:
                cells = row.find_all("td")

                if len(cells) >= 2:
                    first_cell_text = cells[0].get_text().lower().strip()

                    # Verificar se a primeira célula contém "Documentos enviados"
                    if "documentos enviados" in first_cell_text:
                        print(f"📎 Encontrada linha 'Documentos enviados'")

                        # A segunda célula contém os documentos
                        docs_cell = cells[1]

                        # Procurar link do arquivo
                        file_link = docs_cell.find("a", {"class": "file"})
                        if file_link:
                            file_url = file_link.get("href")
                            file_name = file_link.get_text().strip()
                            print(f"📁 Arquivo encontrado: {file_name}")
                            print(f"🔗 URL: {file_url}")

                            # Extrair data do arquivo usando regex
                            import re

                            date_pattern = r"\d{4}-\d{2}-\d{2}"
                            date_match = re.search(date_pattern, docs_cell.get_text())
                            file_date = None

                            if date_match:
                                try:
                                    date_obj = datetime.strptime(
                                        date_match.group(), "%Y-%m-%d"
                                    )
                                    file_date = date_obj.strftime("%d/%m/%Y")
                                    print(f"📅 Data do arquivo: {file_date}")
                                except ValueError:
                                    pass

                            if file_url and file_name and reviewer_info["nome"]:
                                # Criar nome do arquivo com nome do revisor
                                reviewer_name_clean = clean_filename(
                                    reviewer_info["nome"]
                                )
                                new_file_name = f"{reviewer_name_clean}_{file_name}"

                                # Baixar arquivo do revisor
                                downloaded_file = download_file(
                                    ojs_session,
                                    file_url,
                                    submission_id,
                                    "avaliacao",
                                    new_file_name,
                                )
                                if downloaded_file:
                                    reviewer_info["arquivo_revisor"] = downloaded_file
                                    if file_date:
                                        reviewer_info["data_arquivo_revisor"] = (
                                            file_date
                                        )
                        else:
                            print(
                                f"❌ Link do arquivo não encontrado na célula de documentos"
                            )

                    # Verificar se a primeira célula contém "Recomendação"
                    elif "recomendação" in first_cell_text:
                        print(f"📝 Encontrada linha 'Recomendação'")

                        recommendation_text = cells[1].get_text()
                        # Limpar texto e extrair recomendação e data
                        lines = [
                            line.strip()
                            for line in recommendation_text.split("\n")
                            if line.strip()
                        ]
                        if lines:
                            reviewer_info["recomendacao"] = lines[0]
                            print(f"📋 Recomendação: {reviewer_info['recomendacao']}")

                            # Procurar data no formato YYYY-MM-DD
                            for line in lines:
                                if len(line) == 10 and line.count("-") == 2:
                                    try:
                                        date_obj = datetime.strptime(line, "%Y-%m-%d")
                                        reviewer_info["data_recomendacao"] = (
                                            date_obj.strftime("%d/%m/%Y")
                                        )
                                        print(
                                            f"📅 Data da recomendação: {reviewer_info['data_recomendacao']}"
                                        )
                                    except ValueError:
                                        pass

                    # Verificar se a primeira célula contém "Avaliação"
                    elif "avaliação" in first_cell_text:
                        print(f"💬 Encontrada linha 'Avaliação'")

                        # A segunda célula pode conter link para comentários
                        eval_cell = cells[1]

                        # Procurar link do JavaScript
                        js_link = eval_cell.find(
                            "a",
                            {"href": lambda x: x and "javascript:openComments" in x},
                        )
                        if js_link:
                            # Extrair URL do JavaScript
                            href = js_link.get("href")
                            # Extrair URL entre aspas simples do JavaScript
                            import re

                            url_match = re.search(r"openComments\('([^']+)'\)", href)
                            if url_match:
                                comments_url = url_match.group(1)
                                print(f"🔗 URL dos comentários: {comments_url}")

                                # Acessar página de comentários
                                comments = extract_comments(ojs_session, comments_url)
                                if comments:
                                    reviewer_info["comentarios"] = comments
                                    print(
                                        f"💬 Comentários extraídos: {len(comments)} caracteres"
                                    )
                        else:
                            print(
                                f"ℹ️ Nenhum link de comentários encontrado para este revisor"
                            )

        # Adicionar revisor à lista se tiver nome
        if reviewer_info["nome"]:
            review_data["revisores"].append(reviewer_info)
            print(f"✅ Revisor {idx+1} processado com sucesso")
        else:
            print(f"❌ Nome do revisor {idx+1} não encontrado")

    # Extrair versão para avaliação
    print(f"\n🔍 Procurando 'Versão para avaliação'...")
    all_cells = soup.find_all("td")
    for i, cell in enumerate(all_cells):
        if "versão para avaliação" in cell.get_text().lower():
            print(f"📋 Encontrada 'Versão para avaliação'")
            if i + 1 < len(all_cells):
                file_link = all_cells[i + 1].find("a", {"class": "file"})
                if file_link:
                    file_url = file_link.get("href")
                    file_name = file_link.get_text().strip()
                    print(f"📁 Arquivo de avaliação: {file_name}")
                    if file_url and file_name:
                        downloaded_file = download_file(
                            ojs_session,
                            file_url,
                            submission_id,
                            "versao_avaliacao",
                            file_name,
                        )
                        if downloaded_file:
                            review_data["versao_avaliacao"] = downloaded_file

    # Extrair versões do autor (podem ser múltiplas)
    print(f"\n🔍 Procurando 'Versão do autor'...")
    author_version_rows = []
    for i, cell in enumerate(all_cells):
        if "versão do autor" in cell.get_text().lower():
            print(f"📋 Encontrada 'Versão do autor'")
            # Encontrar a linha (tr) que contém esta célula
            current_row = cell.find_parent("tr")
            if current_row:
                author_version_rows.append(current_row)
                # Verificar se há linhas subsequentes relacionadas
                next_row = current_row.find_next_sibling("tr")
                while next_row:
                    # Se a próxima linha não tem label, pode ser uma continuação
                    label_cell = next_row.find("td", {"class": "label"})
                    if not label_cell or not label_cell.get_text().strip():
                        author_version_rows.append(next_row)
                        next_row = next_row.find_next_sibling("tr")
                    else:
                        break

    # Processar todas as linhas de versão do autor
    for row in author_version_rows:
        value_cell = row.find("td", {"class": "value"})
        if value_cell:
            file_link = value_cell.find("a", {"class": "file"})
            if file_link:
                file_url = file_link.get("href")
                file_name = file_link.get_text().strip()
                print(f"📁 Arquivo do autor: {file_name}")
                if file_url and file_name:
                    downloaded_file = download_file(
                        ojs_session, file_url, submission_id, "versao_autor", file_name
                    )
                    if downloaded_file:
                        review_data["versao_autor"].append(downloaded_file)

    print(f"✅ Dados de revisão extraídos para ID {submission_id}")
    print(
        f"📊 Resumo: {len(review_data['revisores'])} revisores, versão_avaliacao: {'Sim' if review_data['versao_avaliacao'] else 'Não'}, versões_autor: {len(review_data['versao_autor'])}"
    )

    return review_data


def clean_filename(name):
    """Limpa o nome para usar como nome de arquivo"""
    import re

    # Remove acentos e caracteres especiais
    name = name.replace(" ", "_")
    name = re.sub(r"[^\w\-_.]", "", name)
    return name


def extract_comments(ojs_session, comments_url):
    """Extrai comentários da página de comentários"""
    try:
        print(f"🔍 Acessando página de comentários: {comments_url}")

        html_content = ojs_session.get_page(comments_url)

        if not html_content:
            print(f"❌ Erro ao acessar página de comentários")
            return None

        soup = BeautifulSoup(html_content, "html.parser")

        # Procurar div com class "comments"
        comments_div = soup.find("div", {"class": "comments"})

        if comments_div:
            comments_text = comments_div.get_text().strip()
            print(f"✅ Comentários encontrados")
            return comments_text
        else:
            print(f"❌ Div 'comments' não encontrada")
            return None

    except Exception as e:
        print(f"❌ Erro ao extrair comentários: {e}")
        return None


def download_file(ojs_session, file_url, submission_id, file_type, file_name):
    """Baixa um arquivo e salva na estrutura de pastas apropriada"""
    try:
        # Criar estrutura de pastas
        base_dir = f"submissions/{submission_id}"
        if file_type == "avaliacao":
            save_dir = os.path.join(base_dir, "avaliacao")
        elif file_type == "versao_avaliacao":
            save_dir = os.path.join(base_dir, "versao_avaliacao")
        elif file_type == "versao_autor":
            save_dir = os.path.join(base_dir, "versao_autor")
        else:
            save_dir = base_dir

        os.makedirs(save_dir, exist_ok=True)

        # Baixar arquivo
        print(f"⬇️ Baixando: {file_name}")
        response = ojs_session.session.get(file_url, timeout=30)

        if response.status_code == 200:
            file_path = os.path.join(save_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Arquivo salvo: {file_path}")
            return file_name
        else:
            print(f"❌ Erro ao baixar arquivo: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Erro ao baixar arquivo {file_name}: {e}")
        return None


def extract_submission_complete_data(ojs_session, submission_id):
    """Extrai todos os dados completos de uma submissão (detalhes + revisão)"""
    print(f"\n🔍 Extraindo dados completos da submissão {submission_id}")

    # Dados básicos da submissão
    submission_data = extract_submission_details(ojs_session, submission_id)

    if not submission_data:
        return None

    # Dados de revisão
    review_data = extract_review_data(ojs_session, submission_id)

    if review_data:
        submission_data.update(review_data)

    time.sleep(1)  # Pausa entre requisições
    return submission_data


def get_all_complete_submissions_data(ojs_session, submission_ids):
    """Obtém todos os dados completos de todas as submissões"""
    submissions_data = {}

    print(f"\n📚 COLETANDO DADOS COMPLETOS DE {len(submission_ids)} SUBMISSÕES:")
    print("=" * 60)

    for i, submission_id in enumerate(submission_ids, 1):
        print(f"\n[{i}/{len(submission_ids)}] Processando ID: {submission_id}")

        submission_data = extract_submission_complete_data(ojs_session, submission_id)

        if submission_data:
            submissions_data[submission_id] = submission_data

    return submissions_data


def extract_all_submission_ids(ojs_session, base_url):
    """Extrai IDs de todas as páginas de submissões"""
    all_submission_ids = []

    # URLs das páginas (página 1 e 2)
    pages = [
        f"{base_url}&submissionsPage=1#submissions",
        f"{base_url}&submissionsPage=2#submissions",
    ]

    for page_num, page_url in enumerate(pages, 1):
        print(f"\n🔍 EXTRAINDO IDs DA PÁGINA {page_num}")
        print("=" * 50)

        html_content = ojs_session.get_page(page_url)

        if html_content:
            page_ids = extract_submission_ids(html_content)

            if page_ids:
                print(f"📊 Página {page_num}: {len(page_ids)} submissões encontradas")
                all_submission_ids.extend(page_ids)
            else:
                print(f"❌ Nenhuma submissão encontrada na página {page_num}")
        else:
            print(f"❌ Erro ao acessar página {page_num}")

    # Remover duplicatas (caso existam)
    all_submission_ids = list(set(all_submission_ids))

    print(f"\n📊 TOTAL GERAL: {len(all_submission_ids)} submissões únicas encontradas")
    return all_submission_ids


def create_excel_report(submissions_data, filename="submissions_report.xlsx"):
    """Cria um relatório em Excel com os dados das submissões usando o padrão do projeto"""
    try:
        print(f"\n📊 GERANDO RELATÓRIO EXCEL...")

        # Importar xlwt para manter consistência com o resto do projeto
        import xlwt

        # Criar workbook
        wb = xlwt.Workbook()

        # Estilo para cabeçalhos
        header_style = xlwt.XFStyle()
        header_font = xlwt.Font()
        header_font.bold = True
        header_style.font = header_font

        # ABA 1: Dados Completos das Submissões
        ws_complete = wb.add_sheet("Submissões Completas")

        # Cabeçalhos principais
        headers_complete = [
            "ID",
            "Título",
            "Autores",
            "Situação",
            "Data Iniciado",
            "Resumo",
            "Qtd Revisores",
            "Versão Avaliação",
            "Qtd Versões Autor",
            "Versões Autor",
        ]

        # Adicionar cabeçalhos dinâmicos para revisores (máximo de revisores encontrado)
        max_revisores = (
            max(len(data.get("revisores", [])) for data in submissions_data.values())
            if submissions_data
            else 0
        )

        for i in range(1, max_revisores + 1):
            headers_complete.extend(
                [
                    f"Revisor {i} - Nome",
                    f"Revisor {i} - Recomendação",
                    f"Revisor {i} - Data Recomendação",
                    f"Revisor {i} - Arquivo",
                    f"Revisor {i} - Data Arquivo",
                    f"Revisor {i} - Comentários",
                ]
            )

        # Escrever cabeçalhos
        for col, header in enumerate(headers_complete):
            ws_complete.write(0, col, header, header_style)

        # Escrever dados
        row = 1
        for submission_id, data in submissions_data.items():
            col = 0

            # Dados básicos
            ws_complete.write(row, col, submission_id)
            col += 1
            ws_complete.write(row, col, data.get("titulo", "N/A"))
            col += 1
            ws_complete.write(row, col, ", ".join(data.get("autores", [])))
            col += 1
            ws_complete.write(row, col, data.get("situacao", "N/A"))
            col += 1
            ws_complete.write(row, col, data.get("data_iniciado", "N/A"))
            col += 1

            # Resumo (limitado para Excel)
            resumo = data.get("resumo", "N/A")
            if len(resumo) > 500:
                resumo = resumo[:500] + "..."
            ws_complete.write(row, col, resumo)
            col += 1

            ws_complete.write(row, col, len(data.get("revisores", [])))
            col += 1
            ws_complete.write(row, col, data.get("versao_avaliacao", "N/A"))
            col += 1
            ws_complete.write(row, col, len(data.get("versao_autor", [])))
            col += 1
            ws_complete.write(row, col, ", ".join(data.get("versao_autor", [])))
            col += 1

            # Dados dos revisores
            revisores = data.get("revisores", [])
            for i in range(max_revisores):
                if i < len(revisores):
                    revisor = revisores[i]
                    ws_complete.write(row, col, revisor.get("nome", "N/A"))
                    col += 1
                    ws_complete.write(row, col, revisor.get("recomendacao", "N/A"))
                    col += 1
                    ws_complete.write(row, col, revisor.get("data_recomendacao", "N/A"))
                    col += 1
                    ws_complete.write(row, col, revisor.get("arquivo_revisor", "N/A"))
                    col += 1
                    ws_complete.write(
                        row, col, revisor.get("data_arquivo_revisor", "N/A")
                    )
                    col += 1

                    # Comentários (limitados para Excel)
                    comentarios = revisor.get("comentarios", "N/A")
                    if comentarios and len(comentarios) > 200:
                        comentarios = comentarios[:200] + "..."
                    ws_complete.write(row, col, comentarios)
                    col += 1
                else:
                    # Preencher com N/A se não houver revisor
                    for _ in range(6):
                        ws_complete.write(row, col, "N/A")
                        col += 1

            row += 1

        # ABA 2: Resumo
        ws_summary = wb.add_sheet("Resumo")

        headers_summary = [
            "ID",
            "Título",
            "Autores",
            "Situação",
            "Data Iniciado",
            "Qtd Revisores",
        ]

        # Escrever cabeçalhos
        for col, header in enumerate(headers_summary):
            ws_summary.write(0, col, header, header_style)

        # Escrever dados do resumo
        row = 1
        for submission_id, data in submissions_data.items():
            ws_summary.write(row, 0, submission_id)
            ws_summary.write(row, 1, data.get("titulo", "N/A"))
            ws_summary.write(row, 2, ", ".join(data.get("autores", [])))
            ws_summary.write(row, 3, data.get("situacao", "N/A"))
            ws_summary.write(row, 4, data.get("data_iniciado", "N/A"))
            ws_summary.write(row, 5, len(data.get("revisores", [])))
            row += 1

        # ABA 3: Revisores
        ws_reviewers = wb.add_sheet("Revisores")

        headers_reviewers = [
            "ID Submissão",
            "Título",
            "Nome Revisor",
            "Recomendação",
            "Data Recomendação",
            "Arquivo",
            "Data Arquivo",
            "Comentários",
        ]

        # Escrever cabeçalhos
        for col, header in enumerate(headers_reviewers):
            ws_reviewers.write(0, col, header, header_style)

        # Escrever dados dos revisores
        row = 1
        for submission_id, data in submissions_data.items():
            for revisor in data.get("revisores", []):
                ws_reviewers.write(row, 0, submission_id)
                ws_reviewers.write(row, 1, data.get("titulo", "N/A"))
                ws_reviewers.write(row, 2, revisor.get("nome", "N/A"))
                ws_reviewers.write(row, 3, revisor.get("recomendacao", "N/A"))
                ws_reviewers.write(row, 4, revisor.get("data_recomendacao", "N/A"))
                ws_reviewers.write(row, 5, revisor.get("arquivo_revisor", "N/A"))
                ws_reviewers.write(row, 6, revisor.get("data_arquivo_revisor", "N/A"))
                ws_reviewers.write(row, 7, revisor.get("comentarios", "N/A"))
                row += 1

        # Salvar arquivo
        wb.save(filename)

        print(f"✅ Relatório Excel criado: {filename}")
        print(f"📊 Abas criadas:")
        print(f"   📋 Submissões Completas: {len(submissions_data)} linhas")
        print(f"   📋 Resumo: {len(submissions_data)} linhas")

        total_revisores = sum(
            len(data.get("revisores", [])) for data in submissions_data.values()
        )
        print(f"   📋 Revisores: {total_revisores} linhas")

        return True

    except Exception as e:
        print(f"❌ Erro ao criar relatório Excel: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Função principal"""
    # CONFIGURAR SUAS CREDENCIAIS AQUI
    USERNAME = "bartira"  # ← Coloque seu usuário aqui
    PASSWORD = "karlamaria02"  # ← Coloque sua senha aqui

    # URL base para buscar submissões
    base_url = "https://revistas.ufpi.br/index.php/equador/editor/submissions/submissionsInReview?searchField=&searchMatch=&search=&dateFromDay=&dateFromYear=&dateFromMonth=&dateToDay=&dateToYear=&dateToMonth=&dateSearchField=&section=&sort=id&sortDirection=1"

    print("🔍 EXTRATOR COMPLETO DE DADOS DE SUBMISSÕES OJS - MÚLTIPLAS PÁGINAS")
    print("=" * 70)

    # Criar sessão OJS com credenciais
    ojs_session = OJSSession(username=USERNAME, password=PASSWORD)

    # Extrair IDs de todas as páginas
    all_submission_ids = extract_all_submission_ids(ojs_session, base_url)

    if all_submission_ids:
        print(f"\n📊 TOTAL DE SUBMISSÕES PARA PROCESSAR: {len(all_submission_ids)}")

        # Mostrar lista de IDs encontrados
        print("📋 LISTA DE IDs ENCONTRADOS:")
        for i, sub_id in enumerate(all_submission_ids, 1):
            print(f"  {i:2d}. {sub_id}")

        # Obter dados completos das submissões (incluindo revisão e downloads)
        submissions_data = get_all_complete_submissions_data(
            ojs_session, all_submission_ids
        )

        if submissions_data:
            # Mostrar resultado final
            print(f"\n📋 RELATÓRIO FINAL - DADOS COMPLETOS DAS SUBMISSÕES:")
            print("=" * 60)

            for i, (submission_id, data) in enumerate(submissions_data.items(), 1):
                print(f"\n{i:2d}. ID: {submission_id}")
                print(f"    Título: {data.get('titulo', 'N/A')}")
                print(f"    Autores: {', '.join(data.get('autores', []))}")
                print(f"    Situação: {data.get('situacao', 'N/A')}")
                print(f"    Revisores: {len(data.get('revisores', []))}")
                if data.get("versao_avaliacao"):
                    print(f"    Versão Avaliação: {data['versao_avaliacao']}")
                if data.get("versao_autor"):
                    print(f"    Versões Autor: {', '.join(data['versao_autor'])}")

            # Salvar dados completos em YAML
            save_to_yaml(submissions_data, "submissions_complete_data.yaml")

            # Criar relatório Excel (usando o padrão do projeto)
            create_excel_report(submissions_data, "submissions_report.xls")

            print(f"\n💾 Dados completos salvos em:")
            print(f"   📄 YAML: submissions_complete_data.yaml")
            print(f"   📊 Excel: submissions_report.xls")
            print(f"📁 Arquivos baixados em: ./submissions/")

            # Estatísticas finais
            total_revisores = sum(
                len(data.get("revisores", [])) for data in submissions_data.values()
            )
            total_arquivos_revisores = sum(
                1
                for data in submissions_data.values()
                for revisor in data.get("revisores", [])
                if revisor.get("arquivo_revisor")
            )
            total_comentarios = sum(
                1
                for data in submissions_data.values()
                for revisor in data.get("revisores", [])
                if revisor.get("comentarios")
            )

            print(f"\n📊 ESTATÍSTICAS FINAIS:")
            print(f"   📄 Total de submissões processadas: {len(submissions_data)}")
            print(f"   👥 Total de revisores: {total_revisores}")
            print(
                f"   📎 Total de arquivos de revisores baixados: {total_arquivos_revisores}"
            )
            print(f"   💬 Total de comentários extraídos: {total_comentarios}")
        else:
            print("❌ Nenhum dado de submissão foi coletado")
    else:
        print("❌ Nenhuma submissão encontrada em nenhuma página")


if __name__ == "__main__":
    main()
