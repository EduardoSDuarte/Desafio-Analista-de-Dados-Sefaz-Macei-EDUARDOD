import pandas as pd
from pathlib import Path

pasta_dados = Path("dados_extraidos")

lista_dataframes = []

for pasta_ano in sorted(pasta_dados.iterdir()):
    if not pasta_ano.is_dir():
        continue

    ano = pasta_ano.name
    caminho_csv = pasta_ano / "finbra.csv"

    if not caminho_csv.exists():
        print(f"Aviso: finbra.csv não encontrado para o ano {ano}")
        continue

    df_ano = pd.read_csv(
        caminho_csv,
        sep=";",
        skiprows=3,
        encoding="latin-1",
        decimal=",",
        thousands=".",
    )

    df_ano["ano"] = int(ano)
    lista_dataframes.append(df_ano)

    print(f"Ano {ano}: {len(df_ano)} linhas lidas")

# Junta tudo num único DataFrame
df_consolidado = pd.concat(lista_dataframes, ignore_index=True)


def classificar_conta(texto_conta):
    codigo = texto_conta.split(" - ")[0].strip()

    if codigo.startswith("FU"):
        return "agregado_subfuncoes_restantes"
    if "Intraorçamentárias" in texto_conta or "Exceto Intraorçamentárias" in texto_conta:
        return "total_agregado"
    if "." in codigo:
        return "subfuncao"
    if codigo.isdigit() and len(codigo) == 2:
        return "funcao"
    return "outro"


df_consolidado["tipo_conta"] = df_consolidado["Conta"].apply(classificar_conta)

df_consolidado["codigo_conta"] = df_consolidado["Conta"].apply(
    lambda x: x.split(" - ")[0].strip() if " - " in x else None
)

print(f"\nTotal consolidado: {len(df_consolidado)} linhas")
print(df_consolidado.head())

print("\nQuantidade de capitais (instituições distintas) por ano:")
print(df_consolidado.groupby("ano")["Instituição"].nunique())

print("\nTipo da coluna Valor:", df_consolidado["Valor"].dtype)

print("\nDistribuição por tipo de conta:")
print(df_consolidado["tipo_conta"].value_counts())