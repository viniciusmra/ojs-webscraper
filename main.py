import get_data
import utils
import create_sheet
import download_files
import os


journal_archive_URL = "https://revistas.ufpi.br/index.php/NOME-DA-REVISTA/issue/archive"
journal_name = "NOME-DA-REVISTA"
journal_save_dir = "DIRETORIO/DE/SALVAMENTO"

if __name__ == "__main__":
    if(utils.is_created(journal_save_dir, journal_name + ".json")):
        print("A revista já foi criado, carregando os dados...")
        journal = utils.load_journal(journal_save_dir, journal_name + ".json")
    else:
        print("Extraindo dados da revista...")
        journal = get_data.get_journal(journal_archive_URL)
        print("Criando arquivo JSON...")
        utils.save_journal(journal, journal_save_dir, journal_name + ".json")

    print("Criando arquivo XLS...")
    create_sheet.create(journal, journal_save_dir, journal_name + ".xls")

    print("Baixando PDFs...")
    download_files.download(journal, journal_save_dir)

    print("Concluído!")


