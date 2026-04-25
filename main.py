import get_data
import utils
import create_sheet
import download_files
import os
from revistas_config import REVISTAS_UFPI


def processar_revista(revista_info, base_save_dir):
    """Processa uma única revista"""
    journal_name = revista_info["pasta"]
    journal_archive_URL = revista_info["url_archive"]
    journal_save_dir = os.path.join(base_save_dir, journal_name)

    print(f"\n{'='*60}")
    print(f"Processando: {revista_info['nome']}")
    print(f"URL: {journal_archive_URL}")
    print(f"Pasta: {journal_save_dir}")
    print(f"{'='*60}")

    try:
        if utils.is_created(journal_save_dir, journal_name + ".json"):
            print("A revista já foi criada, carregando os dados...")
            journal = utils.load_journal(journal_save_dir, journal_name + ".json")
        else:
            print("Extraindo dados da revista...")
            journal = get_data.get_journal(journal_archive_URL)

            if not journal:
                print("❌ Nenhum dado encontrado para esta revista")
                return False

            print("Criando arquivo YAML...")
            utils.save_journal(journal, journal_save_dir, journal_name + ".json")

        print("Criando arquivo XLS...")
        create_sheet.create(journal, journal_save_dir, journal_name + ".xls")

        print("Baixando PDFs...")
        download_files.download(journal, journal_save_dir)

        print("✅ Concluído!")
        return True

    except Exception as e:
        print(f"❌ Erro ao processar revista: {e}")
        return False


def main():
    """Função principal"""
    print("🚀 EXTRATOR DE REVISTAS UFPI")
    print("=" * 50)

    # Configurações
    base_save_dir = "./revistas_ufpi"

    # Mostrar lista de revistas
    print(f"Total de revistas disponíveis: {len(REVISTAS_UFPI)}")
    print("\nOpções:")
    print("1. Processar todas as revistas")
    print("2. Processar revista específica")
    print("3. Processar múltiplas revistas (lista de números)")

    opcao = input("\nEscolha uma opção (1-3): ").strip()

    revistas_para_processar = []

    if opcao == "1":
        revistas_para_processar = REVISTAS_UFPI
        print("📋 Processando todas as revistas...")

    elif opcao == "2":
        print("\n📋 Revistas disponíveis:")
        for i, revista in enumerate(REVISTAS_UFPI, 1):
            print(f"{i:2d}. {revista['nome']}")

        try:
            escolha = int(input("\nEscolha o número da revista: ")) - 1
            if 0 <= escolha < len(REVISTAS_UFPI):
                revistas_para_processar = [REVISTAS_UFPI[escolha]]
            else:
                print("❌ Número inválido")
                return
        except ValueError:
            print("❌ Por favor, digite um número válido")
            return

    elif opcao == "3":
        print("\n📋 Revistas disponíveis:")
        for i, revista in enumerate(REVISTAS_UFPI, 1):
            print(f"{i:2d}. {revista['nome']}")

        try:
            numeros = input("\nDigite os números separados por vírgula (ex: 1,3,5): ")
            indices = [int(n.strip()) - 1 for n in numeros.split(",")]

            for idx in indices:
                if 0 <= idx < len(REVISTAS_UFPI):
                    revistas_para_processar.append(REVISTAS_UFPI[idx])
                else:
                    print(f"⚠️  Número {idx + 1} inválido, ignorando...")

            if not revistas_para_processar:
                print("❌ Nenhuma revista válida selecionada")
                return

        except ValueError:
            print("❌ Formato inválido. Use números separados por vírgula")
            return
    else:
        print("❌ Opção inválida")
        return

    # Processar revistas selecionadas
    print(f"\n🎯 Processando {len(revistas_para_processar)} revista(s)...")

    sucessos = 0
    falhas = 0

    for i, revista_info in enumerate(revistas_para_processar, 1):
        print(f"\n[{i}/{len(revistas_para_processar)}]")

        if processar_revista(revista_info, base_save_dir):
            sucessos += 1
        else:
            falhas += 1

    # Relatório final
    print(f"\n{'='*60}")
    print("📊 RELATÓRIO FINAL")
    print(f"{'='*60}")
    print(f"Total processadas: {len(revistas_para_processar)}")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {falhas}")
    print(f"💾 Dados salvos em: {base_save_dir}")
    print("🎉 Processo concluído!")


if __name__ == "__main__":
    main()
