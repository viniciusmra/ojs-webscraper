import os
import utils
from urllib.request import urlretrieve
from urllib.error import HTTPError, URLError


def extract_first_names(authors_string):
    """
    Extrai os primeiros nomes dos autores a partir da string de autores.
    Retorna uma lista com até 2 primeiros nomes.
    """
    if not authors_string:
        return []

    # Dividir por vírgula e pegar os dois primeiros autores
    authors_list = [author.strip() for author in authors_string.split(",")]
    first_names = []

    for i, author in enumerate(authors_list[:2]):  # Máximo 2 autores
        # Dividir o nome por espaços e pegar o primeiro nome
        name_parts = author.strip().split()
        if name_parts:
            first_name = name_parts[0]
            # Limpar caracteres especiais do primeiro nome
            first_name = utils.clear_name_dir(first_name)
            first_names.append(first_name)

    return first_names


def download(journal, save_dir):

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for year in journal:
        print(year)
        year_dir = os.path.join(save_dir, year)

        if not os.path.exists(year_dir):
            os.makedirs(year_dir)

        for issue in journal[year]:
            print("\t" + issue["TITULO"])
            issue_dir = os.path.join(year_dir, utils.clear_name_dir(issue["TITULO"]))

            if not os.path.exists(issue_dir):
                os.makedirs(issue_dir)

            # Tentar baixar a capa com tratamento de erro
            if issue["CAPA_URL"] and issue["CAPA_URL"].strip():
                try:
                    urlretrieve(
                        issue["CAPA_URL"],
                        os.path.join(issue_dir, f"capa.{issue['CAPA_URL'][-3:]}"),
                    )
                except HTTPError as e:
                    if e.code == 404:
                        print(
                            f"\t\tCapa não encontrada (404) para a edição '{issue['TITULO']}'"
                        )
                    else:
                        print(
                            f"\t\tErro HTTP {e.code} ao baixar capa da edição '{issue['TITULO']}'"
                        )
                    print(f"\t\tContinuando sem a capa...")
                except URLError as e:
                    print(
                        f"\t\tErro de URL ao baixar capa da edição '{issue['TITULO']}': {e}"
                    )
                    print(f"\t\tContinuando sem a capa...")
                except Exception as e:
                    print(
                        f"\t\tErro inesperado ao baixar capa da edição '{issue['TITULO']}': {e}"
                    )
                    print(f"\t\tContinuando sem a capa...")
            else:
                print(
                    f"\t\tURL da capa não encontrada para a edição '{issue['TITULO']}'"
                )

            for index, file in enumerate(issue["ARQUIVOS"], 1):
                if file["ARQUIVO_URL"]:
                    # Extrair primeiros nomes dos autores
                    first_names = extract_first_names(file["AUTORES"])

                    # Construir parte dos autores para o nome do arquivo
                    authors_part = ""
                    if len(first_names) >= 1:
                        authors_part = f" - {first_names[0]}"
                        if len(first_names) >= 2:
                            authors_part += f" - {first_names[1]}"

                    # Construir o nome do arquivo conforme especificado:
                    # [Seção] - [index] - [primeiros 10 caracteres do titulo] - primeiro nome do primeiro autor - primeiro nome do segundo autor (caso exista).pdf
                    filename = utils.clear_name_dir(
                        f"{index:02d} - {file['SECAO']} - {file['TITULO'][:10]}{authors_part}.pdf"
                    )
                    filepath = os.path.join(issue_dir, filename)
                    try:
                        urlretrieve(file["ARQUIVO_URL"], filepath)
                    except HTTPError as e:
                        if e.code == 404:
                            print(
                                f"\t\t\tPDF não encontrado (404): {file['TITULO'][:20]}"
                            )
                        else:
                            print(
                                f"\t\t\tErro HTTP {e.code} ao baixar: {file['TITULO'][:20]}"
                            )
                    except URLError as e:
                        print(
                            f"\t\t\tErro de URL ao baixar: {file['TITULO'][:20]} - {e}"
                        )
                    except Exception as e:
                        print(
                            f"\t\t\tErro inesperado ao baixar: {file['TITULO'][:20]} - {e}"
                        )
