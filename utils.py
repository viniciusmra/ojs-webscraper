import json
import yaml
import os
from datetime import datetime


def save_journal(journal, save_dir, filename):
    # Reorganizar dados em estrutura mais limpa para YAML
    organized_data = {
        "metadata": {
            "extraido_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_anos": len(journal),
            "total_artigos": sum(
                len(issue["ARQUIVOS"]) for year in journal.values() for issue in year
            ),
        },
        "dados": {},
    }

    for year, issues in journal.items():
        organized_data["dados"][year] = []
        for issue in issues:
            organized_issue = {
                "titulo": issue["TITULO"],
                "id": issue["ID"],
                "doi": issue.get("DOI"),
                "capa_url": issue["CAPA_URL"],
                "sumario_url": issue["SUMARIO_URL"],
                "artigos": [],
            }

            for arquivo in issue["ARQUIVOS"]:
                organized_article = {
                    "secao": arquivo["SECAO"],
                    "titulo": arquivo["TITULO"],
                    "autores": arquivo["AUTORES"],
                    "paginas": arquivo.get("PAGINAS"),
                    "palavras_chave": arquivo["PALAVRA_CHAVE"],
                    "resumo": arquivo["RESUMO"],
                    "citacoes": arquivo["CITACOES"],
                    "doi": arquivo.get("DOI"),
                    "doi_pdf": arquivo.get("DOI_PDF"),
                    "arquivo_url": arquivo["ARQUIVO_URL"],
                }
                organized_issue["artigos"].append(organized_article)

            organized_data["dados"][year].append(organized_issue)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Salvar como YAML
    yaml_filename = filename.replace(".json", ".yml")
    with open(os.path.join(save_dir, yaml_filename), "w", encoding="utf-8") as file:
        yaml.dump(
            organized_data,
            file,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            indent=2,
        )


def load_journal(file_dir, filename):
    # Tentar carregar YAML primeiro, senão JSON para compatibilidade
    yaml_filename = filename.replace(".json", ".yml")
    yaml_path = os.path.join(file_dir, yaml_filename)
    json_path = os.path.join(file_dir, filename)

    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as file:
            organized_data = yaml.safe_load(file)

        # Converter de volta para formato original para compatibilidade
        journal = {}
        for year, issues in organized_data["dados"].items():
            journal[year] = []
            for issue in issues:
                original_issue = {
                    "TITULO": issue["titulo"],
                    "ID": issue["id"],
                    "DOI": issue.get("doi"),
                    "CAPA_URL": issue["capa_url"],
                    "SUMARIO_URL": issue["sumario_url"],
                    "ARQUIVOS": [],
                }

                for article in issue["artigos"]:
                    original_article = {
                        "SECAO": article["secao"],
                        "TITULO": article["titulo"],
                        "AUTORES": article["autores"],
                        "PAGINAS": article.get("paginas"),
                        "PALAVRA_CHAVE": article["palavras_chave"],
                        "RESUMO": article["resumo"],
                        "CITACOES": article["citacoes"],
                        "DOI": article.get("doi"),
                        "DOI_PDF": article.get("doi_pdf"),
                        "ARQUIVO_URL": article["arquivo_url"],
                    }
                    original_issue["ARQUIVOS"].append(original_article)

                journal[year].append(original_issue)

        return journal

    elif os.path.exists(json_path):
        # Fallback para JSON antigo
        with open(json_path, "r", encoding="utf-8") as file:
            json_string = file.read()
            journal_dict = json.loads(json_string)
        return journal_dict

    else:
        raise FileNotFoundError(f"Arquivo não encontrado: {yaml_path} ou {json_path}")


def clear_name_dir(name):
    clean_name = name.encode("utf-8", "ignore").decode("utf-8")
    clean_name = clean_name.replace(" ", "_")
    # clean_name = clean_name.replace('@', '')
    clean_name = clean_name.replace(",", "")
    clean_name = clean_name.replace(":", "")
    clean_name = clean_name.replace("?", "")
    clean_name = clean_name.replace('"', "")
    clean_name = clean_name.replace("'", "")
    clean_name = clean_name.replace("/", "_")
    clean_name = clean_name.replace("\\", "_")

    return clean_name


def is_created(file_dir, file_name):
    # Verificar tanto YAML quanto JSON
    yaml_filename = file_name.replace(".json", ".yml")
    yaml_path = os.path.join(file_dir, yaml_filename)
    json_path = os.path.join(file_dir, file_name)

    return os.path.exists(yaml_path) or os.path.exists(json_path)
