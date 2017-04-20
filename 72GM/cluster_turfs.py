import numpy as np
import pandas as pd
from Bio import Cluster
from k_medoids import *


def get_kmedoids(df, dist_matrix, num_clusters):

    clusterid, error, nfound = Cluster.kmedoids(dist_matrix, nclusters=2)
    df = df.reset_index()
    #df['cluster_id'] = pd.DataFrame(data=clusterid)

    return df

def duration_to_sec(x):
    try:
        x = x.split(':')
        return float(x[0]) + float(x[1]) / 60 + float(x[2]) / 3600
    except IndexError:
        return 0


def readData(file_name):
    df = pd.read_csv(file_name)

    df = df.dropna(subset=['PKSITE_NO'])

    df["Service-Duration for 580D"] = df["Service-Duration for 580D"].apply(lambda x: duration_to_sec(x))
    df["Service-Duration for 72GM"] = df["Service-Duration for 72GM"].apply(lambda x: duration_to_sec(x))

    return df

if __name__ == '__main__':
    df_cluster = pd.read_csv('72GM_splits.csv')
    df_cluster['service-duration'] = df_cluster['service-duration'] * 24
    df_cluster = df_cluster[df_cluster['service-duration'] < 10. / 60]
    df_cluster['raw-id'] = df_cluster['raw-id'].apply(lambda x: str(int(float(x.split("_")[0]))))
    df_cluster.drop_duplicates(subset=['raw-id'], inplace=True)

    D = np.array(pd.read_csv('small_turfs_time_matrix.csv'))

    for i in range(len(D)):
        for j in range(i + 1, len(D)):
            D[i][j] = D[j][i]


    #df = get_kmedoids(df_cluster, array([[0.0, 1.1, 2.3],[1.1, 0.0, 4.5],[2.3, 4.5, 0.0]]), 1)

    M, C = kMedoids(D, 100)
    print(M)
    print(C)

    df_cluster = df_cluster.reset_index()
    df_cluster['cluster'] = pd.Series(M)

    #df_cluster.to_csv('Cluster_72GM_review.csv', index=False)
    df_cluster.drop_duplicates(subset=['cluster'], inplace=True)

    df_cluster['service-duration'] = pd.Series(np.array(df_cluster.groupby('cluster').sum()['service-duration']*1.3))

    df_72GM = pd.read_csv('72GM_splits.csv')

    df_72GM['service-duration'] = df_72GM['service-duration'] * 24
    df_72GM = df_72GM[df_72GM['service-duration'] >= 10. / 60]
    df_72GM['cluster'] = ''
    df_cluster.drop(['Unnamed: 0'], inplace=True, axis = 1)
    df_72GM.drop(['Unnamed: 0'], inplace=True, axis=1)
    df_72GM = df_72GM.append(df_cluster)

    df_72GM.to_csv('ODL_Input_72.csv')
