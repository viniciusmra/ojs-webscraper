import xlwt
import utils


def create(journal, save_dir, filename):
    xls_file = xlwt.Workbook()
    sheet = xls_file.add_sheet("Artigos")

    # Criar estilo para células com quebras de linha
    wrap_style = xlwt.easyxf("alignment: wrap on, vert top;")

    headers = list(journal[next(iter(journal))][0]["ARQUIVOS"][0].keys())
    number_of_columns = len(headers)
    row = 0
    for index, header in enumerate(headers):
        sheet.write(row, index, header)
    row = row + 1
    for year in reversed(journal):
        for issue in reversed(journal[year]):
            # Título da edição
            sheet.write_merge(
                row,
                row,
                0,
                number_of_columns - 1,
                issue["TITULO"],
                xlwt.easyxf("align: horiz center;"),
            )
            row = row + 1

            # DOI da edição (se existir)
            if issue.get("DOI"):
                sheet.write_merge(
                    row,
                    row,
                    0,
                    number_of_columns - 1,
                    f"DOI: {issue['DOI']}",
                    xlwt.easyxf("align: horiz center; font: italic on;"),
                )
                row = row + 1

            for file in issue["ARQUIVOS"]:
                for index, header in enumerate(headers):
                    if header == "CITACOES":
                        # Juntar todas as citações em uma célula com quebras de linha
                        citations = file.get("CITACOES", [])
                        if citations:
                            citations_text = "\n".join(citations)
                            sheet.write(row, index, citations_text, wrap_style)
                        else:
                            sheet.write(row, index, "")
                    elif header == "RESUMO":
                        # Aplicar wrap também no resumo para melhor visualização
                        sheet.write(row, index, file[header], wrap_style)
                    else:
                        sheet.write(row, index, file[header])
                row = row + 1

    # Ajustar largura das colunas para melhor visualização
    for i, header in enumerate(headers):
        if header in ["RESUMO", "CITACOES"]:
            sheet.col(i).width = 15000  # Colunas mais largas para texto longo
        elif header == "TITULO":
            sheet.col(i).width = 8000
        elif header == "AUTORES":
            sheet.col(i).width = 6000
        elif header in ["DOI", "DOI_PDF"]:
            sheet.col(i).width = 8000  # Largura adequada para DOIs
        elif header == "PAGINAS":
            sheet.col(i).width = 3000  # Largura menor para páginas (ex: "1-15")
        else:
            sheet.col(i).width = 4000

    xls_file.save(save_dir + "/" + filename)
