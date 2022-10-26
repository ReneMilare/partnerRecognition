# import datetime as dt
import warnings

import dtw
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import talib
import yfinance as yf
from sklearn.neighbors import KNeighborsRegressor

warnings.filterwarnings("ignore")

def idtw(dfx, dfy, column_name):
  ix = []
  iy = []

  for i in range(0, len(dfx.index)):
    if i == 0:
      ix.append(1)
    else:
      ix.append(ix[i-1]*dfx[column_name][dfx.index[i]]/dfx[column_name][dfx.index[i-1]])

  for i in range(0, len(dfy.index)):
    if i == 0:
      iy.append(1)
    else:
      iy.append(iy[i-1]*dfy[column_name][dfy.index[i]]/dfy[column_name][dfy.index[i-1]])

  distance = dtw.dtw(iy, ix).distance
  return distance, ix, iy

stock = 'petr4'
window = 5
last_days = 20
param = 'Adj Close'

df = yf.download(stock+'.SA',period='max')

df['mma_20'] = talib.MA(df['Adj Close'], 20)
df['mme_9'] = talib.EMA(df['Adj Close'], 9)
df['retorno'] = df['Adj Close'].pct_change()
df['retorno5'] = df['Adj Close'].pct_change(window)
df.dropna(inplace=True)

df_index = df[[param, 'mma_20', 'mme_9', 'retorno5', 'retorno']][:-last_days]
df_query = df[[param, 'mma_20', 'mme_9', 'retorno5', 'retorno']][-last_days:]

distancies = {
  'distance': [],
  'data': [],
  'retorno5': []
}
ix = []
iy = []
for i in range(0, len(df_index.index)):

  df_index_ = df_index[i:i+last_days]
  if len(df_query.index) == len(df_index_.index):
    distance, ix_, iy_ = idtw(df_index_, df_query, param)
    distancies['distance'].append(distance)
    distancies['data'].append(df_index_.index[-1])
    distancies['retorno5'].append(df_index['retorno5'][df_index.index[i+window]])
    ix.append(ix_)
    iy.append(iy_)

df_to_analize = pd.DataFrame.from_dict(distancies)
df_to_analize.sort_values(by=['distance'], inplace=True, ignore_index=True )

sample = int(len(df_to_analize)*.01)
print('Window => ' + str(last_days))
print('Sample => ' + str(sample))
print(df_to_analize.head(sample))
print()
print('Retorno esperado para os prrximos 5 dias para a '+stock)
print('mínimo:')
print(df_to_analize['retorno5'].head(sample).min()*100)
print()
print('médio:')
print(df_to_analize['retorno5'].head(sample).mean()*100)
print()
print('máximo:')
print(df_to_analize['retorno5'].head(sample).max()*100)
print()
print('desvio padrão:')
print(df_to_analize['retorno5'].head(sample).std()*100)

x = df_to_analize.distance.head(sample).values
y = df_to_analize.retorno5.head(sample)

neigh = KNeighborsRegressor()
neigh.fit(x.reshape(-1,1), y)

print()
print('predito')
print(neigh.predict([[0]])*100)

for i in range(0, 9):
  get_index = np.argmax(df_index.index == df_to_analize['data'][i]._date_repr, axis=0)
  plt.figure(figsize=(9, 3))
  plt.title(str(df_to_analize['distance'][i]))
  plt.plot(df_index['Adj Close'][get_index-last_days:get_index+1])
  plt.plot(df_index['Adj Close'][get_index:get_index+window])
  # plt.show()

plt.figure(figsize=(9, 3))
plt.plot(df_query[param])
# plt.figure(figsize=(9, 3))
# plt.plot(df_index[df_to_analize['data'][0]][])
plt.show()