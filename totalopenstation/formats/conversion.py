#! /usr/bin/env python
# -*- coding: utf-8 -*-
# filename: tops_txt.py
# Copyright 2008 Luca Bianconi<lc.bianconi@googlemail.com>
# Copyright 2008,2011 Stefano Costa <steko@iosa.it>
# Copyright 2015-2016 Damien Gaignon <damien.gaignon@gmail.com>
#
# This file is part of Total Open Station.
#
# Total Open Station is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Total Open Station is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Total Open Station.  If not, see
# <http://www.gnu.org/licenses/>.

from math import sin, pi, cos


def deg_to_gon(angle):
    '''Convert degrees format to grade (gon) format.'''
    return angle * 400 / 360


def deg_to_rad(angle):
    '''Convert degrees format to radian format.'''
    return angle * (2 * pi) / 360


def deg_to_mil(angle):
    return angle * 6400 / 360


def deg_to_dms(angle):
    d, m = divmod(angle, 1)
    m, s = divmod(m * 100, 1)
    return d + m * 60 / 10000 + s * 100 * 3600 / 100000000


def dms_to_deg(angle):
    '''Convert degrees in DDD.MMSS format to degree format.'''
    d, m = divmod(angle, 1)
    m, s = divmod(m * 100, 1)
    return d + m / 60 + s * 100 / 3600


def dms_to_gon(angle):
    '''Convert degrees in DDD.MMSS format to grade (gon) format.'''
    angle = dms_to_deg(angle)
    return deg_to_gon(angle)


def dms_to_rad(angle):
    '''Convert degrees in DDD.MMSS format to radians format.'''
    angle = dms_to_deg(angle)
    return deg_to_rad(angle)


def dms_to_mil(angle):
    '''Convert degrees in DDD.MMSS format to radians format.'''
    angle = dms_to_deg(angle)
    return deg_to_mil(angle)


def rad_to_deg(angle):
    return angle * 360 / (2 * pi)


def rad_to_dms(angle):
    angle = rad_to_deg(angle)
    return deg_to_dms(angle)


def rad_to_gon(angle):
    return angle * 400 / (2 * pi)


def rad_to_mil(angle):
    return angle * 6400 / (2* pi)


def mil_to_gon(angle):
    '''Convert degrees in mil (NATO) format to grade (gon) format.'''
    return angle * 400 / 6400


def mil_to_rad(angle):
    '''Convert degrees in mil (NATO) format to radian format.'''
    return angle * (2 * pi) / 6400


def mil_to_deg(angle):
    return angle * 360 / 6400


def mil_to_dms(angle):
    angle = mil_to_deg(angle)
    return deg_to_dms(angle)


def gon_to_rad(angle):
    '''Convert grade (gon) format to radian format.'''
    return angle * (2 * pi) / 400


def gon_to_deg(angle):
    return angle * 360 / 400


def gon_to_dms(angle):
    angle = gon_to_deg(angle)
    return deg_to_dms(angle)


def gon_to_mil(angle):
    return angle * 6400 / 400


def to_rad(angle, angle_unit):
    '''Conversion function for angles to radian'''
    if angle_unit == "dms":
        return dms_to_rad(angle)
    elif angle_unit == "mil":
        return mil_to_rad(angle)
    elif angle_unit == "deg":
        return deg_to_rad(angle)
    else:
        return gon_to_rad(angle)


def to_deg(angle, angle_unit):
    '''Conversion function for angles to degree'''
    if angle_unit == "dms":
        return dms_to_deg(angle)
    elif angle_unit == "mil":
        return mil_to_deg(angle)
    elif angle_unit == "rad":
        return rad_to_deg(angle)
    else:
        return gon_to_deg(angle)


def to_gon(angle, angle_unit):
    '''Conversion function for angles to degree'''
    if angle_unit == "dms":
        return dms_to_gon(angle)
    elif angle_unit == "mil":
        return mil_to_gon(angle)
    elif angle_unit == "rad":
        return rad_to_gon(angle)
    else:
        return deg_to_gon(angle)


def to_dms(angle, angle_unit):
    '''Conversion function for angles to degree'''
    if angle_unit == "gon" or angle_unit == "grads":
        return gon_to_dms(angle)
    elif angle_unit == "mil":
        return mil_to_dms(angle)
    elif angle_unit == "rad":
        return rad_to_dms(angle)
    else:
        return deg_to_dms(angle)


def to_mil(angle, angle_unit):
    '''Conversion function for angles to degree'''
    if angle_unit == "dms":
        return dms_to_mil(angle)
    elif angle_unit == "gon" or angle_unit == "grads":
        return gon_to_mil(angle)
    elif angle_unit == "rad":
        return rad_to_mil(angle)
    else:
        return deg_to_mil(angle)

def horizontal_to_slope(dist, angle, angle_unit, angle_type="z"):
    '''Convert distance to slope from horizontal
    Angle is considered zenithal by default'''
    angle = to_rad(angle, angle_unit)
    if angle_type == "z":
        return dist / sin (angle)
    else:
        return dist / cos (angle)

def vertical_to_zenithal(angle, angle_unit):
    '''Convert angle from vertical (reference is horizontal) to
    zenithal (reference is north)'''
    if angle_unit == "deg":
        return 90 - angle
    elif angle_unit == "gon" or angle_unit == "grads":
        return 100 - angle
    elif angle_unit == "rad":
        return (pi / 2) - angle
    elif angle_unit == "mil":
        return 1600 - angle
    else:
        return deg_to_dms(360 - dms_to_deg(angle))

def bearing_to_azimuth(angle, angle_unit):
    quater = angle[0] + angle[-1]
    if quater == "NE":
        return angle
    if quater == "SE":
        if angle_unit == "deg":
            return 180 - angle
        elif angle_unit == "gon":
            return 200 - angle
        elif angle_unit == "rad":
            return pi - angle
        elif angle_unit == "mil":
            return 3200 - angle
        else:
            return deg_to_dms(180 - dms_to_deg(angle))
    if quater == "NW":
        if angle_unit == "deg":
            return 360 - angle
        elif angle_unit == "gon":
            return 400 - angle
        elif angle_unit == "rad":
            return 2 * pi - angle
        elif angle_unit == "mil":
            return 6400 - angle
        else:
            return deg_to_dms(360 - dms_to_deg(angle))
    if quater == "SW":
        if angle_unit == "deg":
            return 180 + angle
        elif angle_unit == "gon":
            return 200 + angle
        elif angle_unit == "rad":
            return pi + angle
        elif angle_unit == "mil":
            return 3200 + angle
        else:
            return deg_to_dms(180 + dms_to_deg(angle))
