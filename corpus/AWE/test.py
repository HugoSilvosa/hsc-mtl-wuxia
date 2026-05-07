import pandas as pd

df = pd.read_csv('resultados_similitud.txt', sep=';', header=None)
filtro_yes = df[df[4] == 'yes']
filtro_no = df[df[4] == 'no']
resultado = filtro_yes.groupby(0)[4].count()
resultado2 = filtro_no.groupby(0)[4].count()

print(resultado)
print(resultado2)


res = df.groupby(0)[3].mean()

print(res)

filter = df[df[3]>0.1]
res = filter.groupby(0)[3].mean()
print(res)
