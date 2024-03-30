
import json
import os

def save_journal(journal, save_dir, filename):
    json_string = json.dumps(journal, ensure_ascii=False)

    if(not os.path.exists(save_dir)):
        os.makedirs(save_dir)

    with open(save_dir + "/" + filename, 'w', encoding='utf-8') as file:
        file.write(json_string)

def load_journal(file_dir, filename):
    with open(file_dir + "/"+ filename, 'r', encoding='utf-8') as file:
        json_string = file.read()
        journal_dict = json.loads(json_string)
    return journal_dict

def clear_name_dir(name):
    clean_name = name.encode('utf-8', 'ignore').decode('utf-8')
    clean_name = clean_name.replace(' ', '_')
    #clean_name = clean_name.replace('@', '')
    clean_name = clean_name.replace(',', '')
    clean_name = clean_name.replace(':', '')
    clean_name = clean_name.replace('?', '')
    clean_name = clean_name.replace('"', '')
    clean_name = clean_name.replace("'", '')
    clean_name = clean_name.replace("/", '_')
    clean_name = clean_name.replace("\\", '_')
    
    return clean_name

def is_created(file_dir, file_name):
    if os.path.exists(file_dir + "/" + file_name):
        return True
    else:
        return False