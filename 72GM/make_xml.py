import pandas as pd
import datetime as dt
import sys

import numpy as np

df_ = pd.read_csv('Equipment_Inventory - Sheet3.csv')

def create_xml_for_vehicle(start, end):
    df_eq = pd.read_csv('Equipment_Inventory - Sheet3.csv')
    replace_DOW = {'Monday - Friday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                   'Monday - Sunday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                   'Monday - Thursday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday'],
                   'Friday - Monday': ['Friday', 'Saturday', 'Sunday', 'Monday'],
                   'Tuesday - Friday': ['Tuesday', 'Wednesday', 'Thursday', 'Friday']}

    df_eq['Days_of_Week'] = df_eq['Days_of_Week'].map(replace_DOW)

    new_df_eq = pd.DataFrame(columns=df_eq.columns)

    for i in range(len(df_eq)):
        for day in df_eq['Days_of_Week'][i]:
            new_df_eq = new_df_eq.append(df_eq.ix[i])
            new_df_eq.iloc[-1, new_df_eq.columns.get_loc('Days_of_Week')] = day

    df_vehicle_580D = pd.DataFrame(
        columns=["vehicle-name", "vehicle-id", "start-latitude", "start-longitude", "end-latitude",
                 "end-longitude", "start-time", "end-time", "capacity", "speed-multiplier", "cost-per-km",
                 "cost-per-hour", "waiting-cost-per-hour", "fixed-cost", "skills", "number-of-vehicles", 'day'])

    day_Conversion = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 0}
    # day_Conversion = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}

    for cycle in range(1, 4):
        zig = 0
        for i in new_df_eq.index:
            if new_df_eq.iloc[i]['equipment_type(5910 or 72inch)'] == "Toro 5910 192\"":
                if day_Conversion[new_df_eq.iloc[i]["Days_of_Week"]] == 6 or day_Conversion[new_df_eq.iloc[i]["Days_of_Week"]] == 0:
                    skill = "roadway"
                elif day_Conversion[new_df_eq.iloc[i]["Days_of_Week"]] == 1 or day_Conversion[new_df_eq.iloc[i]["Days_of_Week"]] == 5:
                    if zig > 0:
                        skill = "neighbourhood"
                    else:
                        skill = 'roadway'
                    zig += 1
                else:
                    skill = "neighbourhood"
                df_vehicle_580D = df_vehicle_580D.append(
                    pd.DataFrame(columns=df_vehicle_580D.columns, data=[[new_df_eq.iloc[i]["vehicle_name"],
                                                                         new_df_eq.iloc[i]["vehicle_id"] + "_" + str(
                                                                             cycle) + "_" + str(
                                                                             day_Conversion[new_df_eq.iloc[i]["Days_of_Week"]]),
                                                                         new_df_eq.iloc[i]["depot_latitude"],
                                                                         new_df_eq.iloc[i]["depot_latitude.1"],
                                                                         new_df_eq.iloc[i]["depot_latitude"],
                                                                         new_df_eq.iloc[i]["depot_latitude.1"],
                                                                         str(day_Conversion[
                                                                                 new_df_eq.iloc[i]["Days_of_Week"]] + 7 * (
                                                                             cycle - 1)) + "d 06:00:00",
                                                                         str(day_Conversion[
                                                                                 new_df_eq.iloc[i]["Days_of_Week"]] + 7 * (
                                                                             cycle - 1)) + "d 14:45:00",
                                                                         10000, 1, 0.001, 1, 0.5, 100,
                                                                         skill, 1, day_Conversion[
                                                                             new_df_eq.iloc[i]["Days_of_Week"]] + 7 * (
                                                                         cycle - 1)]]))

    new_df_vehicle_580D = df_vehicle_580D.copy()
    new_df_vehicle_580D['start-time'] = new_df_vehicle_580D['start-time'].apply(lambda x: fix_time(x))
    new_df_vehicle_580D['end-time'] = new_df_vehicle_580D['end-time'].apply(lambda x: fix_time(x))

    new_df_vehicle_580D = new_df_vehicle_580D[(new_df_vehicle_580D['end-time'] < end) & (new_df_vehicle_580D['end-time'] > start)]

    xml = ['<vehicles>']
    xml.append(new_df_vehicle_580D.to_xml_vehicle())
    xml.append('</vehicles>')

    return '\n'.join(xml)


def create_xml_for_turf():
    df_580D = pd.read_csv('ODL_Inputs.csv')

    df_580D['start-time'] = df_580D['start-time'].apply(lambda x: fix_time(x))
    df_580D['end-time'] = df_580D['end-time'].apply(lambda x: fix_time(x))

    df_580D['service-duration'] = df_580D['service-duration'].apply(lambda x: 24*x)
    xml = ['<services>']
    xml.append(df_580D.to_xml_turfs())
    xml.append('</services>')

    return '\n'.join(xml)

def fix_time(x):
    def time_to_hour(x):
        x = x.split(':')
        return float(x[0])+float(x[1])/60 + float(x[2])/3600
    x = str(x).split('d')
    time = x[1]
    return float(x[0])*24 + time_to_hour(time)

def to_xml_vehicle(df, filename=None, mode='w'):
    veh_depot = {}

    for index, row in df_.iterrows():
        veh_depot[row['vehicle_id']] = row['depot_name']

    def row_to_xml(row):
        xml = ["<vehicle>"]
        xml.append('<id>{0}</id>'.format(row['vehicle-id']))
        xml.append('<typeId>solomonType</typeId>'.format(row['vehicle-name']))
        xml.append('<startLocation>')
        xml.append('<id>{0}</id>'.format(veh_depot[row['vehicle-id'].split("_")[0]]))
        xml.append('<coord x="{0}" y="{1}"/>'.format(row['start-longitude'], row['start-latitude']))
        xml.append('</startLocation>')
        xml.append('<endLocation>')
        xml.append('<id>{0}</id>'.format(veh_depot[row['vehicle-id'].split("_")[0]]))
        xml.append('<coord x="{0}" y="{1}"/>'.format(row['start-longitude'], row['start-latitude']))
        xml.append('</endLocation>')
        xml.append('<timeWindows>')
        xml.append('<start>{0}</start>'.format(row['start-time']))
        xml.append('<end>{0}</end>'.format(row['end-time']))
        xml.append('</timeWindows>')
        xml.append('<skills>{0}</skills>'.format(row['skills']))
        xml.append('</vehicle>')

        return '\n'.join(xml)
    res = '\n'.join(df.apply(row_to_xml, axis=1))

    if filename is None:
        return res
    with open(filename, mode) as f:
        f.write(res)

def to_xml_turfs(df, filename=None, mode='w'):
    def row_to_xml(row):
        xml = ["<service id='{0}' type='delivery'>".format(row['Id'])]
        xml.append('<locationId>{0}</locationId>'.format(str(row['Id']).split("_")[0]))
        xml.append('<coord x="{0}" y="{1}"/>'.format(row['longitude'], row['latitude']))
        xml.append('<capacity-demand>1</capacity-demand>')
        xml.append('<duration>{0}</duration>'.format(row['service-duration']))
        xml.append('<timeWindows>')
        xml.append('<timeWindow>')
        xml.append('<start>{0}</start>'.format(row['start-time']))
        xml.append('<end>{0}</end>'.format(row['end-time']))
        xml.append('</timeWindow>')
        xml.append('</timeWindows>')
        xml.append('</service>')

        return '\n'.join(xml)

    res = '\n'.join(df.apply(row_to_xml, axis=1))

    if filename is None:
        return res
    with open(filename, mode) as f:
        f.write(res)


if __name__ == '__main__':
    if len(sys.argv[:]) < 3:
        exit()
    pd.DataFrame.to_xml_turfs = to_xml_turfs
    pd.DataFrame.to_xml_vehicle = to_xml_vehicle
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<problem      xmlns = "http://www.w3schools.com"   xmlns:xsi = "http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation = "http://www.w3schools.com vrp_xml_schema.xsd" >')
    xml.append('<problemType>\n<fleetSize>FINITE</fleetSize>\n<fleetComposition>HOMOGENEOUS</fleetComposition>\n</problemType>')
    xml.append(create_xml_for_vehicle(int(sys.argv[1]), int(sys.argv[2])))
    xml.append(create_xml_for_turf())
    xml.append('</problem>')
    #print("\n".join(xml))

    with open('problem_setup.xml', 'w') as f:
        f.write("\n".join(xml))

