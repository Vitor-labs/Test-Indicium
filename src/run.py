from presentation.cli.main import SARSCoVAnalysisSystem

if __name__ == "__main__":
    system = SARSCoVAnalysisSystem()

    print("Sistema de Análise SARS-CoV")
    print("=" * 50)

    while True:
        print("\nOpções:")
        print("1. Configurar pipeline de dados")
        print("2. Configurar pipeline de notícias")
        print("3. Modo consulta interativa")
        print("4. Sair")

        choice = input("\nEscolha uma opção (1-4): ").strip()

        if choice == "1":
            system.setup_data_pipeline()
        elif choice == "2":
            system.setup_news_pipeline()
        elif choice == "3":
            system.interactive_query_mode()
        elif choice == "4":
            print("Encerrando sistema...")
            break
        else:
            print("Opção inválida!")
