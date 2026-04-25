from urllib.request import urlretrieve

import requests
from bs4 import BeautifulSoup


def get_journal(mainURL):
    all_issues = {}
    total = 0
    response = requests.get(mainURL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    all_h3 = soup.find_all("h3")

    for h3 in all_h3:
        all_issues[h3.text] = []
        print(h3.text)
        parent_div = h3.find_parent()
        issue_divs = parent_div.find_all("div", recursive=False)
        for div in issue_divs:
            issue = {}
            issue["TITULO"] = div.find("h4").find("a").text
            issue["ID"] = int(div.get("id").replace("issue-", ""))
            issue["CAPA_URL"] = (
                div.find("div", class_="issueCoverImage").find("img").get("src")
            )
            issue["SUMARIO_URL"] = (
                div.find("h4").find("a").get("href") + "/showToc"
            )  # f"https://revistas.ufpi.br/index.php/parfor/issue/view/{issue['ID']}/showToc"

            # Extrair DOI da edição se existir
            issue["DOI"] = None
            toc_response = requests.get(issue["SUMARIO_URL"])
            toc_response.raise_for_status()
            toc_soup = BeautifulSoup(toc_response.text, "html.parser")

            doi_element = toc_soup.find("a", id="pub-id::doi")
            if doi_element:
                issue["DOI"] = doi_element.get("href")

            issue["ARQUIVOS"] = get_files(issue["SUMARIO_URL"], toc_soup)
            all_issues[h3.text].append(issue)
            print(f"\t{issue['TITULO']} - {len(issue['ARQUIVOS'])} artigos")
            total = total + len(issue["ARQUIVOS"])
    print(f"Total: {total} artigos")
    return all_issues


def get_files(toc_url, toc_soup=None):
    files = []

    # Se não foi passado o soup, fazer a requisição
    if toc_soup is None:
        response = requests.get(toc_url)
        response.raise_for_status()
        toc_soup = BeautifulSoup(response.text, "html.parser")

    soup = toc_soup

    section_title = None
    for element in soup.find(id="content").find_all(["h4", "table"]):

        if element.name == "h4":
            section_title = element.text.strip()
        elif element.name == "table":
            title = element.find(class_="tocTitle").text.strip()
            file_url = None
            try:
                file_url = (
                    element.find(class_="file").get("href").replace("view", "download")
                )
            except:
                print(f'Artigo "{title}" sem link para download. Página: {toc_url}')

            authors_div = element.find("div", class_="tocAuthors")
            authors = None
            if authors_div:
                authors = authors_div.text.strip().replace("\t", "")

            # Extrair páginas do artigo
            pages_div = element.find("div", class_="tocPages")
            pages = None
            if pages_div:
                pages = pages_div.text.strip()

            view_url = element.find(class_="tocTitle").find("a")
            abstract = None
            subject = None
            citations = []
            article_doi = None
            article_doi_pdf = None
            if view_url:
                article_response = requests.get(view_url.get("href"))
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, "html.parser")

                # Extrair resumo
                abstract_div = article_soup.find("div", id="articleAbstract")
                if abstract_div and abstract_div.find("div"):
                    abstract = abstract_div.find("div").text

                # Extrair palavras-chave
                article_subject = article_soup.find("div", id="articleSubject")
                if article_subject:
                    subject = article_subject.find("div").text.strip()

                # Extrair citações
                article_citations = article_soup.find("div", id="articleCitations")
                if article_citations:
                    citations_div = article_citations.find("div")
                    if citations_div:
                        citation_paragraphs = citations_div.find_all("p")
                        for p in citation_paragraphs:
                            citation_text = p.text.strip()
                            if citation_text:  # Só adiciona se não estiver vazio
                                citations.append(citation_text)

                # Extrair DOI do artigo
                article_doi_element = article_soup.find("a", id="pub-id::doi")
                if article_doi_element:
                    article_doi = article_doi_element.get("href")

                # Extrair DOI do PDF (procurar por IDs que começam com "pub-id::doi-")
                article_doi_pdf_elements = article_soup.find_all(
                    "a", id=lambda x: x and x.startswith("pub-id::doi-")
                )
                if article_doi_pdf_elements:
                    # Pegar o primeiro DOI PDF encontrado
                    article_doi_pdf = article_doi_pdf_elements[0].get("href")

            file_dict = {}
            file_dict["SECAO"] = section_title
            file_dict["TITULO"] = title
            file_dict["AUTORES"] = authors
            file_dict["PAGINAS"] = pages
            file_dict["PALAVRA_CHAVE"] = subject
            file_dict["RESUMO"] = abstract
            file_dict["CITACOES"] = citations
            file_dict["DOI"] = article_doi
            file_dict["DOI_PDF"] = article_doi_pdf
            file_dict["ARQUIVO_URL"] = file_url
            files.append(file_dict)

    return files
