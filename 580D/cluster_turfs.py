import numpy as np
import pandas as pd
from Bio import Cluster
from k_medoids import *


def get_kmedoids(df, dist_matrix, num_clusters):

    clusterid, error, nfound = Cluster.kmedoids(dist_matrix, num_clusters)
    df = df.reset_index()
    df['cluster_id'] = pd.DataFrame(data=clusterid)

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
    df_cluster = pd.read_csv('ODL_Inputs_580D.csv')
    df_cluster['service-duration'] = df_cluster['service-duration']
    df_cluster = df_cluster[df_cluster['service-duration'] < 10. / 60]
    df_cluster['raw-id'] = df_cluster['Id'].apply(lambda x: str(int(float(x.split("_")[0]))))
    df_cluster.drop_duplicates(subset=['raw-id'], inplace=True)

    D = np.array(pd.read_csv('small_turfs_time_matrix.csv'))


    for i in range(len(D)):
        for j in range(i + 1, len(D)):
            D[i][j] = D[j][i]

    #df = get_kmedoids(df_cluster, array([[0.0, 1.1, 2.3],[1.1, 0.0, 4.5],[2.3, 4.5, 0.0]]), 1)

    clus_dict, M, C = kMedoids(D, 15)
    print(M)
    print(C)


    df_cluster = df_cluster.reset_index()
    #df_cluster['cluster'] = pd.Series(M)

    df_ = pd.read_csv('small_turfs_time_matrix.csv')
    df_['cluster'] = pd.Series(M)
    df_['raw-id'] = pd.Series(df_.columns)
    df_cluster = df_cluster.merge(df_[['cluster', 'raw-id']], on='raw-id', how='left')
    names = df_.columns
    new_clus_dict = {}

    for key, values in clus_dict.items():
        new_clus_dict[names[values[0]]] = [names[v] for v in values]

    print(new_clus_dict)

    #df_cluster = get_kmedoids(df_cluster, D, 25)

    df_cluster.to_csv('580D_cluster_review.csv')
    df_cluster = df_cluster.drop('service-duration', axis = 1).merge((df_cluster.groupby('cluster')['service-duration'].sum()*1.3).reset_index(), on='cluster', how='left')
    df_cluster.drop_duplicates(subset=['cluster'], inplace=True)
    df_580D = pd.read_csv('ODL_Inputs_580D.csv')

    df_580D = df_580D[df_580D['service-duration'] >= 10. / 60]
    df_580D['cluster'] = ''
    df_cluster.drop(['index', 'raw-id'], inplace=True, axis = 1)
    #df_580D.drop(['Unnamed: 0'], inplace=True, axis=1)
    df_580D = df_580D.append(df_cluster)

    df_580D.to_csv('ODL_Input_clustered_580D.csv', index=False)
