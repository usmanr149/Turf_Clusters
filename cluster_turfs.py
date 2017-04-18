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

    df = readData('../southside_service_inventory.csv')

    df_small_turfs_580D = df[(df['Service-Duration for 580D'] < 5/60) & (df['Service-Duration for 580D'] > 0)]
    df_small_turfs_72GM = df[(df['Service-Duration for 72GM'] < 5/60) & (df['Service-Duration for 72GM'] > 0)]

    dist_matrix_580D = get_distance_matrix(df_small_turfs_580D)

    dist_matrix_580D.to_csv("Dist_matrix_580D.csv", index=False)

    #df_cluters = get_kmedoids(df_small_turfs_580D, dist_matrix_580D, 30)

    #df_cluters.to_csv('Cluster_review.csv', index = False)
