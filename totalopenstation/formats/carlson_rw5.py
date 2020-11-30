# -*- coding: utf-8 -*-
# filename: formats/carlson_rw5.py
# Copyright 2014 Stefano Costa <steko@iosa.it>
# Copyright 2016 Damien Gaignon <damien.gaignon@gmail.com>

# This file is part of Total Open Station.

# Total Open Station is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# Total Open Station is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Total Open Station.  If not, see
# <http://www.gnu.org/licenses/>.

import logging

import re

from totalopenstation.formats.conversion import horizontal_to_slope, \
                                                vertical_to_zenithal, \
                                                bearing_to_azimuth
from . import Feature, Point, UNKNOWN_STATION, UNKNOWN_POINT
from .polar import BasePoint, PolarPoint

# ussfeet = US Survey Feet
UNITS = {"angle": {"0": "dms", "1": "gon"},
         "distance": {"0": "feet", "1": "meter", "2": "ussfeet"}}

REG = { "type": r"^(?:-{2}?)?(?P<type>\D{2}),",
        "MO": r",AD(?P<AD>[\d. ]*),UN(?P<UN>[\d. ]*),SF(?P<SF>[\d. ]*),EC(?P<EC>[\d. ]*),EO(?P<EO>[\d. ]*),AU(?P<AU>[\d. ]*)",
        "OC": r",OP(?P<OP>[\d. ]*),N (?P<N>[\d. ]*),E (?P<E>[\d. ]*),EL(?P<EL>[\d. ]*)[,-]*(?P<note>.*)",
        "LS": r",HI(?P<HI>[\d. ]*),HR(?P<HR>[\d. ]*)",
        "BK": r",OP(?P<OP>[\d. ]*),BP(?P<BP>[\d. ]*),BS(?P<BS>[\d. ]*),BC(?P<BC>[\d. ]*)",
        "SP": r",PN(?P<PN>[\d. ]*),N (?P<N>[\d. ]*),E (?P<E>[\d. ]*),EL(?P<EL>[\d. ]*)[,-]*(?P<note>.*)",
        "TR": r",OP(?P<OP>[\d. ]*),FP(?P<FP>[\d. ]*|[\w. ]*),(?:(?:AR|AL|DL|DR)(?P<HA>[\d. ]*)|BR(?P<BR>[(N|S)\d. (W|E)]*)|AZ(?P<AZ>[\d.]*)),(?:ZE(?P<ZE>[\d. -]*)|VA(?P<VA>[\d. -]*)|CE(?P<CE>[\d. -]*)),(?:SD(?P<SD>[\d. ]*)|HD(?P<HD>[\d. ]*))[,-]*(?P<note>.*)"
}
# These followings value are the same as REG["TR"] but could not be added on the
# first initilization of the dictionary.
REG.update({ "SS": REG["TR"],
             "BD": REG["TR"],
             "BR": REG["TR"],
             "FD": REG["TR"],
             "FR": REG["TR"]
})

logger = logging.getLogger(__name__)

def _record(recstr):
    type = None
    rec = None
    try:
        type = re.search(REG['type'], recstr).group('type')
    except AttributeError:
        pass
    if type in REG:
        rec = {key: value for key, value in re.search(REG[type], recstr).groupdict().iteritems() if value is not None}
    elif type != None:
        print('Type "%s" is not used for now' % type)
    return type, rec

#   fields = recstr.split(',')
#   record_fields = {f[0:2] : f[2:] for f in fields[1:]}

#   # Record type, including comment records
#   if len(fields[0]) > 2:
#       record_fields['type'] = fields[0].strip('-')
#       record_fields['comment'] = True
#   else:
#       record_fields['type'] = fields[0]

#   # Note field
#   try:
#       record_fields['--']
#   except KeyError:
#       record_fields['note'] = ''
#   else:
#       record_fields['note'] = record_fields['--']
#   return record_fields

class FormatParser:
    '''The FormatParser for Carlson RW5 data format.

    Args:
        data (str): A string representing the file to be parsed.

    Attributes:
        rows (list): A list of each lines of the file being parsed
                    which do not begin with '-- '.
    '''

    def __init__(self, data):
        self.rows = (r for r in data.splitlines() if not r.startswith('-- '))
        # Text comments, but not comment records ------------------------^

    @property
    def points(self):
        '''Extract all RW5 data.

        This parser is based on the information in :ref:`if_carlson_rw5`

        Returns:
            A list of GeoJSON-like Feature object representing points coordinates.

        Raises:

        Notes:
            Sometimes needed records are commented so it is needed to parse
            also comments
        '''
        points_coord = {}
        base_points = {}
        points = []
        pid = 0

        for row in self.rows:
            type, rec = _record(row)
            if type == None and rec == None:
                continue
            # Get angle and distance units
            if type == 'MO':
                angle_unit = UNITS["angle"][rec['AU']]
                dist_unit = UNITS["distance"][rec['UN']]
            # Look for point coordinates
            if type == 'SP':
                point_name = rec['PN']
                northing = float(rec['N'])  # extra whitespace
                easting = float(rec['E'])  # extra whitespace
                elevation = float(rec['EL'])
                point = Point(easting, northing, elevation)
                attrib = [rec['note']]
                f = Feature(point,
                            desc='PT',
                            id=pid,
                            point_name=point_name,
                            dist_unit=dist_unit,
                            attrib=attrib)
                points.append(f)
                pid += 1
                points_coord[point_name] = point
            # Look for station coordinates
            if type == 'OC':
                station_name = rec['OP']
                northing = float(rec['N'])  # extra whitespace
                easting = float(rec['E'])  # extra whitespace
                elevation = float(rec['EL'])
                station_point = Point(easting, northing, elevation)
                points_coord[station_name] = station_point
                bp = BasePoint(x=easting, y=northing, z=elevation, ih=0,
                                b_zero_st=0.0)
                base_points[station_name] = bp
            # Look for line of sight values
            # Finalize station computing
            if type == 'LS':
                ih = float(rec['HI'])
                th = float(rec['HR'])
                try:
                    station_point
                except NameError:
                    logger.info('There is no known station')
                    station_point = UNKNOWN_STATION
                stf = Feature(station_point,
                              desc='ST',
                              id=pid,
                              point_name=station_name,
                              dist_unit=dist_unit,
                              attrib=[])
                bp = base_points[station_name]
                bp.ih = ih
                # Do not add station if previous station record is the same
                try:
                    last_stf
                except NameError:
                    last_stf = stf
                    points.append(stf)
                    pid += 1
                else:
                    if stf.point_name != last_stf.point_name or \
                                    stf.geometry.x != last_stf.geometry.x or \
                                    stf.geometry.y != last_stf.geometry.y or \
                                    stf.geometry.z != last_stf.geometry.z:
                        points.append(stf)
                        pid += 1
                        last_stf = stf
            # Look for polar data
            if type in ('SS', 'TR', 'BD', 'BR', 'FD', 'FR'):
                point_name = rec['FP']
                attrib = [rec['note']]
                # Angle is recorded as azimuth or horizontal angle
                # Horizontal angle is either Bearing, Angle Right or Left,
                # Deflection Right or Left
                if 'AZ' in rec:
                    angle = float(rec['AZ'])
                elif 'HA' in rec:
                    angle = float(rec['HA'])
                elif 'BR' in rec:
                    angle = float(bearing_to_azimuth(rec['BR'], angle_unit))
                else:
                    logger.info('There is no horizontal angle value')
               # Vertical angle is either Zenith, Vertical angle
                # or Change elevation
                if 'ZE' in rec:
                    z_angle = float(rec['ZE'])
                    z_angle_type = 'z'
                elif 'CE' in rec:
                    z_angle = float(rec['CE'])
                    z_angle_type = 'dh'
                elif 'VA' in rec:
                    z_angle = float(rec['VA'])
                    z_angle_type = 'v'
                else:
                    logger.info('There is no vertical angle value')
                if 'SD' in rec:
                    dist = float(rec['SD'])
                    dist_type = 's'
                elif 'HD' in rec:
                    dist = float(rec['HD'])
                    dist_type = 'h'
                else:
                    logger.info('There is no distance value')
                attrib = [rec['note']]
                p = PolarPoint(angle_unit=angle_unit,
                               z_angle_type=z_angle_type,
                               dist_type=dist_type,
                               dist=dist,
                               angle=angle,
                               z_angle=z_angle,
                               th=th,
                               base_point=bp,
                               pid=pid,
                               text=point_name,
                               coordorder='ENZ')
                point = p.to_point()
                f = Feature(point,
                            desc='PT',
                            id=pid,
                            point_name=point_name,
                            dist_unit=dist_unit,
                            attrib=attrib)
                points.append(f)
                pid += 1
        logger.debug(points)
        return points


    @property
    def raw_line(self):
        '''Extract all Carlson RW5 data.

        This parser is based on the information in :ref:`if_carlson_rw5`

        Returns:
            A list of GeoJSON-like Feature object representing points coordinates.

        Raises:

        Notes:
            Information needed are:
                - station : Occupy Point and Line of Sight
                - backsight : Backsight
                - direct point : Store Point
                - computed point : Foresight Direct/Reverse, Traverse/Sideshot, Backsight Direct/Reverse

            Sometimes needed records are commented so it is needed to parse also comments
        '''

        points_coord = {}
        points = []
        pid = 0
        station_id = 1

        for row in self.rows:
            type, rec = _record(row)
            if type == None and rec == None:
                continue
#           type = None
#           try:
#               type = re.search(REG['type'], row).group('type')
#           except AttributeError:
#               continue
#           if type in REG:
#               rec = {key: value for key, value in re.search(REG[type], row).groupdict().iteritems() if value is not None}
#           else:
#               print('Type "%s" is not used for now' % type)
#               continue
            # Get angle and distance units
            if type == 'MO':
                angle_unit = UNITS["angle"][rec['AU']]
                dist_unit = UNITS["distance"][rec['UN']]
                continue
            # Look for point coordinates
            if type == 'SP':
                point = Point(float(rec['E']),
                              float(rec['N']),
                              float(rec['EL']))
                points.append(
                    Feature(point,
                            desc='PT',
                            id=pid,
                            point_name=rec['PN'],
                            dist_unit=dist_unit,
                            attrib=[rec['note']])
                )
                pid += 1
                points_coord[rec['PN']] = point
                continue
            # Look for station coordinates
            # Initialize station record
            if type == 'OC':
                station_name = rec['OP']
                points_coord[rec['OP']] = Point(float(rec['E']),
                                                float(rec['N']),
                                                float(rec['EL']))
                points.append(
                    Feature(
                            Point(float(rec['E']),
                                  float(rec['N']),
                                  float(rec['EL'])),
                            desc='ST',
                            id=pid,
                            point_name=station_name,
                            angle_unit=angle_unit,
                            dist_unit=dist_unit,
                            ih=0.0,
                            attrib=[rec['note'],
                                    "Default IH"]
                    )
                )
                pid += 1
                continue
            # Look for line of sight values
            # Finalize station record
            if type == 'LS':
                th = float(rec['HR'])
                # For ih, LS record should have a station recorded before
                # cause in our system, ih is directly associated with a station
                try:
                    station_name
                #  otherwise use a fake one and add a Fake flag to the station
                except NameError:
                    logger.info('There is no known station')
                    station_point = UNKNOWN_STATION
                    station_name = 'station_' + str(station_id)
                    station_id += 1
                    points_coord[station_name] = station_point
                    points.append(
                        Feature(
                                station_point,
                                desc='ST',
                                id=pid,
                                point_name=station_name,
                                angle_unit=angle_unit,
                                dist_unit=dist_unit,
                                ih=float(rec['HI']),
                                attrib=["FAKE"]
                        )
                    )
                    pid += 1
                else:
                    # Search for the last station with that name
                    for f in points[::-1]:
                        if f.point_name == station_name and f.desc == "ST":
                            # If this station has a default ih, replace it
                            if "Default IH" in f.properties['attrib']:
                                f.properties['ih'] = float(rec['HI'])
                                f.properties['attrib'].remove("Default IH")
                            # Otherwise, if the station has a different ih
                            # copy the station with the new ih
                            elif f.properties['ih'] != float(rec['HI']):
                                points.append(
                                    Feature(
                                            f.geometry,
                                            desc='ST',
                                            id=pid,
                                            point_name=station_name,
                                            angle_unit=angle_unit,
                                            dist_unit=dist_unit,
                                            ih=float(rec['HI']),
                                            attrib=[]
                                    )
                                )
                                pid += 1
                            break
                continue
            # Look for back sight values
            if type == 'BK':
                try:
                    point = points_coord[rec['BP']]
                except KeyError:
                    logger.info('There is no known point')
                    point = UNKNOWN_POINT
                points.append(
                    Feature(
                            point,
                            desc='BS',
                            id=pid,
                            point_name=rec['BP'],
                            angle_unit=angle_unit,
                            circle=rec['BC'],
                            azimuth=rec['BS'],
                            station_name=rec['OP']
                    )
                )
                pid += 1
                continue
            # Look for polar data
            if type in ('SS', 'TR', 'BD', 'BR', 'FD', 'FR'):
                point_name = rec['FP']
                # Angle is recorded as azimuth or horizontal angle
                if 'AZ' in rec:
                    azimuth = float(rec['AZ'])
                else:
                    azimuth = 0.0
                # Horizontal angle is either Bearing, Angle Right or Left,
                # Deflection Right or Left
                if 'HA' in rec:
                    angle = float(rec['HA'])
                elif 'BR' in rec:
                    angle = float(bearing_to_azimuth(rec['BR'], angle_unit))
                else:
                    angle = 0.0
               # Vertical angle is either Zenith, Vertical angle
                # or Change elevation
                if 'ZE' in rec:
                    z_angle = float(rec['ZE'])
                    z_angle_type = 'z'
                if 'CE' in rec:
                    z_angle = float(rec['CE'])
                    z_angle_type = 'dh'
                if 'VA' in rec:
                    z_angle = float(rec['VA'])
                    z_angle_type = 'v'
                if 'SD' in rec:
                    dist = float(rec['SD'])
                    dist_type = 's'
                if 'HD' in rec:
                    dist = float(rec['HD'])
                    dist_type = 'h'
                attrib = [rec['note']]
                try:
                    point = points_coord[rec['FP']]
                except KeyError:
                    logger.info('There is no known point')
                    point = UNKNOWN_POINT
                if rec['OP']:
                    station_name = rec['OP']
                else:
                    logger.info('There is no known station')
                    station_name = 'station_' + str(station_id)
                    station_id += 1
                points.append(
                    Feature(point,
                            desc='PO',
                            id=pid,
                            point_name=rec['FP'],
                            angle_unit=angle_unit,
                            z_angle_type=z_angle_type,
                            dist_unit=dist_unit,
                            dist_type=dist_type,
                            azimuth=azimuth,
                            angle=angle,
                            z_angle=z_angle,
                            dist=dist,
                            th=th,
                            station_name=station_name,
                            attrib=[rec['note']]
                    )
                )
                pid += 1

        logger.debug(points)
        return points, {"dist_unit": dist_unit, "angle_unit": angle_unit}
