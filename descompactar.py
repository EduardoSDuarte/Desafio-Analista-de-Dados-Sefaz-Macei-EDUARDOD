from pathlib import Path
import zipfile

# Pasta onde estão os zips organizados por ano
pasta_origem = Path("dados_compactos")

# Pasta onde vamos extrair os CSVs
pasta_destino = Path("dados_extraidos")
pasta_destino.mkdir(exist_ok=True)

# Percorre cada subpasta de ano dentro de dados_compactos/
for pasta_ano in sorted(pasta_origem.iterdir()):
    if not pasta_ano.is_dir():
        continue  # ignora arquivos soltos, se houver

    ano = pasta_ano.name  # nome da subpasta = o ano (ex: "2020")

    # Encontra o(s) arquivo(s) .zip dentro dessa pasta de ano
    zips_do_ano = list(pasta_ano.glob("*.zip"))

    if not zips_do_ano:
        print(f"Aviso: nenhum .zip encontrado para o ano {ano}")
        continue

    for caminho_zip in zips_do_ano:
        destino_ano = pasta_destino / ano
        destino_ano.mkdir(exist_ok=True)

        with zipfile.ZipFile(caminho_zip, "r") as zip_ref:
            zip_ref.extractall(destino_ano)

        print(f"Extraído: {caminho_zip.name} -> {destino_ano}/")

print("Descompactação concluída.")