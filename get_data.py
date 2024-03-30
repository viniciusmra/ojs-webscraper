from urllib.request import urlretrieve

import requests
from bs4 import BeautifulSoup


def get_journal(mainURL):
    all_issues = {}
    total = 0
    response = requests.get(mainURL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    all_h3 = soup.find_all('h3')
    
    for h3 in all_h3:
        all_issues[h3.text] = []
        print(h3.text)
        parent_div = h3.find_parent()
        issue_divs = parent_div.find_all('div', recursive=False)
        for div in issue_divs:
            issue = {}
            issue['TITULO'] = div.find('h4').find('a').text
            issue['ID'] = int(div.get("id").replace("issue-",''))
            issue['CAPA_URL'] = div.find('div', class_="issueCoverImage").find('img').get('src')
            issue['SUMARIO_URL'] = div.find('h4').find('a').get('href') + "/showToc" #f"https://revistas.ufpi.br/index.php/parfor/issue/view/{issue['ID']}/showToc"
            issue['ARQUIVOS'] = get_files(issue['SUMARIO_URL'])
            all_issues[h3.text].append(issue)
            print(f"\t{issue['TITULO']} - {len(issue['ARQUIVOS'])} artigos")
            total = total + len(issue['ARQUIVOS'])
    print(f"Total: {total} artigos")
    return all_issues


def get_files(toc_url):
    files = []
    response = requests.get(toc_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    section_title = None
    for element in soup.find(id="content").find_all(['h4', 'table']):

        if(element.name == 'h4'):
            section_title = element.text.strip()
        elif(element.name == 'table'):
            title = element.find(class_='tocTitle').text.strip()
            file_url = None
            try:
                file_url = element.find(class_="file").get('href').replace("view", "download")
            except:
                print(f'Artigo "{title}" sem link para download. Página: {toc_url}')
                
            authors_div = element.find('div', class_="tocAuthors")
            authors = None
            if(authors_div):
                authors = authors_div.text.strip().replace("\t", "")

            view_url = element.find(class_="tocTitle").find('a')
            abstract = None
            subject = None
            if(view_url):
                article_response = requests.get(view_url.get('href'))
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                abstract = article_soup.find('div', id="articleAbstract").find('div').text
                
                article_subject = article_soup.find('div', id="articleSubject")
                if(article_subject):
                    subject = article_subject.find('div').text.strip()
            file_dict = {}
            file_dict['SECAO'] = section_title
            file_dict['TITULO'] = title
            file_dict['AUTORES'] = authors
            file_dict['PALAVRA_CHAVE'] = subject
            file_dict['RESUMO'] = abstract
            file_dict['ARQUIVO_URL'] = file_url
            files.append(file_dict)
   
    return files
