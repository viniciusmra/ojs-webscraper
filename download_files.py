import os
import utils
from urllib.request import urlretrieve

def download(journal, save_dir):

    if(not os.path.exists(save_dir)):
        os.makedirs(save_dir)
    for year in journal:
        print(year)
        year_dir = os.path.join(save_dir, year)
        
        if(not os.path.exists(year_dir)):
            os.makedirs(year_dir)
        
        for issue in journal[year]:
            print("\t" + issue['TITULO'])
            issue_dir = os.path.join(year_dir, utils.clear_name_dir(issue['TITULO']))
            
            if(not os.path.exists(issue_dir)):
                os.makedirs(issue_dir)
            
            urlretrieve(issue['CAPA_URL'], os.path.join(issue_dir, f"capa.{issue['CAPA_URL'][-3:]}"))

            for file in issue['ARQUIVOS']:
                if(file['ARQUIVO_URL']):
                    filename = utils.clear_name_dir(f"{file['SECAO']} - {file['TITULO'][:30]}.pdf")
                    filepath = os.path.join(issue_dir, filename)
                    try:
                        urlretrieve(file['ARQUIVO_URL'], filepath)
                    except Exception as e:
                        print(f"{issue['TITULO']} - {file['TITULO'][:20]}\n{e}")