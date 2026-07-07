import pandas as pd

# Lê o Parquet já consolidado (rápido, sem reprocessar os CSVs)
df = pd.read_parquet("finbra_consolidado.parquet")

# Filtra só linhas de FUNÇÃO (ignora subfunção e totais agregados,
# pra não somar valor em dobro)
df_funcao = df[df["tipo_conta"] == "funcao"].copy()

# Separa o que foi empenhado e o que foi pago
empenhado = df_funcao[df_funcao["Coluna"] == "Despesas Empenhadas"]
pago = df_funcao[df_funcao["Coluna"] == "Despesas Pagas"]

# Chaves para juntar empenhado e pago corretamente:
# mesma instituição, mesmo ano, mesma função (Conta)
chaves = ["Instituição", "UF", "ano", "Conta", "codigo_conta"]

empenhado_agg = empenhado.groupby(chaves, as_index=False)["Valor"].sum()
empenhado_agg = empenhado_agg.rename(columns={"Valor": "valor_empenhado"})

pago_agg = pago.groupby(chaves, as_index=False)["Valor"].sum()
pago_agg = pago_agg.rename(columns={"Valor": "valor_pago"})

# Junta empenhado e pago lado a lado
df_execucao = pd.merge(empenhado_agg, pago_agg, on=chaves, how="inner")

# Calcula a Taxa de Execução Financeira
df_execucao["taxa_execucao"] = (
    df_execucao["valor_pago"] / df_execucao["valor_empenhado"] * 100
)

print(f"Total de linhas na análise de execução: {len(df_execucao)}")
print(df_execucao.head(10))

# Exemplo: taxa média de execução por capital (todas as funções, todos os anos)
print("\nTaxa de execução média por capital:")
print(
    df_execucao.groupby("Instituição")["taxa_execucao"]
    .mean()
    .sort_values(ascending=False)
)

# Salva o resultado para consultas futuras
df_execucao.to_parquet("execucao_financeira.parquet", index=False)
print("\nArquivo salvo: execucao_financeira.parquet")

# ==========================================================================
# Evolução temporal: Maceió vs média das capitais
# ==========================================================================

# Taxa de execução média por ano, só para Maceió
maceio_por_ano = (
    df_execucao[df_execucao["Instituição"].str.contains("Maceió")]
    .groupby("ano")["taxa_execucao"]
    .mean()
)

# Taxa de execução média por ano, considerando TODAS as capitais
media_capitais_por_ano = df_execucao.groupby("ano")["taxa_execucao"].mean()

comparativo = pd.DataFrame({
    "Maceió": maceio_por_ano,
    "Média das capitais": media_capitais_por_ano,
})
comparativo["diferenca"] = comparativo["Maceió"] - comparativo["Média das capitais"]

print("\nEvolução da taxa de execução: Maceió vs média das capitais")
print(comparativo)

