import googlemaps
import dist_matrix as tmo

from Bio import Cluster
import numpy as np
from numpy import array
import pandas as pd

def get_distance_matrix(df):
    inputs = [(df['lat'][i], df['long'][i]) for i in df.index]

    google_key = "****"

    maps = googlemaps.Client(key=google_key)

    # inputs = inputs[:5]  # for testing
    dist_matrix = tmo.get_dist_matrix(inputs, maps)

    return pd.DataFrame(columns=df['PINSITE_ID'].unique(), data=dist_matrix)

def get_kmedoids(df, dist_matrix, num_clusters):

    clusterid, error, nfound = Cluster.kmedoids(dist_matrix, nclusters=num_clusters)
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
    df_cluster = pd.read_csv('/home/usman/Downloads/Turf_Clusters/72GM/72GM_splits.csv')

    df_cluster['service-duration'] = df_cluster['service-duration'] * 24
    df_cluster = df_cluster[df_cluster['service-duration'] < 10. / 60]

    time_matrix = np.array(pd.read_csv('small_turfs_time_matrix.csv'))

    df = get_kmedoids(df_cluster, time_matrix, 50)

    print(df)