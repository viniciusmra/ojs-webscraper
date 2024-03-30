import xlwt
import utils


def create(journal, save_dir, filename):
    xls_file = xlwt.Workbook()
    sheet = xls_file.add_sheet('Artigos')
    headers = list(journal[next(iter(journal))][0]['ARQUIVOS'][0].keys())
    number_of_columns = len(headers)
    row = 0
    for index, header in enumerate(headers):
        sheet.write(row, index, header)
    row = row + 1
    for year in reversed(journal):
        for issue in reversed(journal[year]):
            sheet.write_merge(row, row, 0, number_of_columns-1, issue['TITULO'], xlwt.easyxf('align: horiz center;'))
            row = row + 1
            for file in issue['ARQUIVOS']:
                for index, header in enumerate(headers):
                    sheet.write(row, index, file[header])
                row = row + 1
    xls_file.save(save_dir + "/" + filename)