from datetime import datetime
import time

import googlemaps
#import xmlrpc.client
import pandas as pd



google_key = "***"


def read_inputs(fpath, colnames):
    df = pd.read_csv(fpath)
    x = df[colnames[0]]
    y = df[colnames[1]]

    inputs=[]
    for row in range(len(df)):
        inputs.append((df[colnames[0]][row],df[colnames[1]][row]))

    return inputs


def get_tsp_data(points):
    distances = ''
    try:
        for i in range(0, len(points)):
            for j in range(0,i+1):
                if i == j:
                    distances += '0\n'
                else:
                    print(gmaps.distance_matrix(origins=points[i],destinations=points[j]))
                    result1 = gmaps.distance_matrix(origins=points[i],destinations=points[j])
                    print(result1)
                    d = result1['rows'][0]['elements'][0]['distance']['value']
                    distances += '%d ' % d
    except Exception as e:
        print ('Error in getting distance between %s and %s' % (points[i], points[j]))
    return distances

def get_dist_matrix(points, ggmaps):
    matrix_range = len(points)

    dist_matrix_arr = [[0 for x in range(matrix_range)] for x in range(matrix_range)]
    try:
        for i in range(0, matrix_range):
            for j in range(0,i+1):
                if i == j:
                    dist_matrix_arr[i][j] = 0
                else:
                    result1 = ggmaps.distance_matrix(origins=points[i],destinations=points[j])
                    d = result1['rows'][0]['elements'][0]['distance']['value']
                    dist_matrix_arr[i][j] = d
                    dist_matrix_arr[j][i] = d
    except Exception as e:
        print ('Error in getting distance between %s and %s' % (points[i], points[j]))
    return dist_matrix_arr



def solve_tsp(dist_matrix):
    tsp_template = """
    TYPE : TSP
    DIMENSION : %i
    EDGE_WEIGHT_TYPE : EXPLICIT
    EDGE_WEIGHT_FORMAT : LOWER_DIAG_ROW
    EDGE_WEIGHT_SECTION
    %s
    EOF
    """

    tsp_data = tsp_template % (19, distances)
    base_xml = """
    <document>
    <category>co</category>
    <solver>concorde</solver>
    <inputType>TSP</inputType>
    <priority>long</priority>
    <email>koosha.g@gmail.com</email>
    <dat2><![CDATA[]]></dat2>
    <dat1><![CDATA[]]></dat1>
    <tsp><![CDATA[%s]]></tsp>
    <ALGTYPE><![CDATA[con]]></ALGTYPE>
    <RDTYPE><![CDATA[fixed]]></RDTYPE>
    <PLTYPE><![CDATA[no]]></PLTYPE>
    <comment><![CDATA[]]></comment>
    </document>
    """
    tsp_xml = base_xml % tsp_data

    print(tsp_xml)



    NEOS_HOST="http://www.neos-server.org"
    NEOS_PORT=3332

    temp = ("https://neos-server.org/neos/", 3332)

    neos = xmlrpc.client.ServerProxy("%s:%d" % (NEOS_HOST, NEOS_PORT))
    #neos = xmlrpc.server(temp)

    (jobNumber,password) = neos.submitJob(tsp_xml)

    status="Waiting"
    while status == "Running" or status=="Waiting":
      time.sleep(1)
      status = neos.getJobStatus(jobNumber, password)

    msg = neos.getFinalResults(jobNumber, password).data
    print(msg)

    return msg

if __name__ == '__main__':
    input_points = read_inputs("turf_locations.csv", ['x', 'y'])
    gmaps = googlemaps.Client(key=google_key)

    sth = get_dist_matrix(input_points,gmaps)


    distances = get_tsp_data(input_points)
    solve_tsp(distances)



"""
TODO:
phase 1: optimal location of yards (calculate the distance of yards with centroids)
    - clustering using  ED
    - clustering using Net Dist
    - visulize on leaflet
phase 2: optimal turf assignment given yards
    - create a matrix with 11 rows (yards) and N columns (turfs)
    - the min on column identifies the yard that should serve the
    - visualize??
phase 3: optimal path given a yard and respective turfs
     - set origins to turfs starting from the yard get tsp solution
     - viz??
"""