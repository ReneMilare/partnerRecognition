import dtw

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