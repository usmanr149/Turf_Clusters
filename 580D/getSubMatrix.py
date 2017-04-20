import pandas as pd
import numpy as np

df = pd.read_csv('time_matrix_hold.csv')
df = df.set_index(df.columns)
matrix_t = np.array(df)

zig = 0
col_names = {}

for col in df.columns:
    col_names[zig] = col
    zig+=1

df_cluster = pd.read_csv('ODL_Inputs_580D.csv')

df_cluster['service-duration'] = df_cluster['service-duration']
df_cluster = df_cluster[df_cluster['service-duration'] < 10./60]

df_cluster['raw-id'] = df_cluster['Id'].apply(lambda x: str(int(float(x.split("_")[0]))))
df_cluster.drop_duplicates(subset=['raw-id'], inplace=True)

pk_site = df_cluster['raw-id'].unique()
pk_site = [pk for pk in df.columns if pk not in pk_site]

df = df.drop(pk_site, axis = 0)
df = df.drop(pk_site, axis = 1)

df.to_csv('small_turfs_time_matrix.csv', index=False)


'''
imp_col_row = list()
for key in col_names.keys():
    if col_names[key] not in pk_skite:
        imp_col_row.append(key)

matrix_t = np.delete(matrix_t, imp_col_row, axis=1)
matrix_t = np.delete(matrix_t, imp_col_row, axis=0)

matrix_t_hold =  matrix_t

for i in range(len(matrix_t)):
    for j in range(i + 1, len(matrix_t)):
        matrix_t[i][j] = matrix_t[j][i]

df_small_turfs = pd.DataFrame(columns=df_cluster['raw-id'].unique(), data=matrix_t)

df_small_turfs.to_csv('small_turfs_time_matrix.csv', index=False)
'''