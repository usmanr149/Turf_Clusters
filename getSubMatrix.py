import pandas as pd
import numpy as np

df = pd.read_csv('time_matrix_hold.csv')

matrix_t = np.array(df)

zig = 0
col_names = {}

for col in df.columns:
    col_names[zig] = col
    zig+=1

df_cluster = pd.read_csv('/home/usman/Downloads/Turf_Clusters/72GM/72GM_splits.csv')

df_cluster['service-duration'] = df_cluster['service-duration']*24
df_cluster = df_cluster[df_cluster['service-duration'] < 10./60]

df_cluster['raw-id'] = df_cluster['raw-id'].apply(lambda x: str(int(float(x.split("_")[0]))))

pk_skite = df_cluster['raw-id'].unique()

imp_col_row = list()

for key in col_names.keys():
    if col_names[key] not in pk_skite:
        imp_col_row.append(key)

matrix_t = np.delete(matrix_t, imp_col_row, axis=1)
matrix_t = np.delete(matrix_t, imp_col_row, axis=0)


df_small_turfs = pd.DataFrame(columns=df_cluster['raw-id'].unique(), data=matrix_t)

df_small_turfs.to_csv('small_turfs_time_matrix.csv', index=False)