# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 19:57:33 2022

@author: cariefrantz
@project: GSLMO

Converts salinity to density of Great Salt Lake water at different temperatures
using the equation of state developed by Naftz et al (2011).

The equation of state is officially valid from 0-180 g/L salinity.
However, recent work by A. Rupke et al. at the Utah Geological Survey announced
at the 2022 Great Salt Lake Issues Forum was reported that extends the validity
of the equation of state to higher salinity values.

Reference:
    
    Naftz, D. L., Millero, F. J., Jones, B. F., & Green, W. R. (2011). An
    Equation of State for Hypersaline Water in Great Salt Lake, Utah, USA.
    Aquatic Geochemistry, 17(6), 809–820.
    https://doi.org/10.1007/s10498-011-9138-z


Copyright (C) 2022  Carie M. Frantz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
    
"""

###############
# IMPORTS
###############
import math


###############
# GLOBAL CONSTANTS
###############

# Constants from the Naftz et al. (2011) equation of state
A = 184.01062
B = 1.04708
C = -1.21061
D = 0.000314721
E = 0.00199
F = -0.00112

# Warning text for values outside the valid range
warn_start = 'Warning: The '
warn_mid = ' is outside the range of 0–180 g/L used to develop the GSL equation of state in Naftz (2011). Take this calculated '
warn_end = ' value with a grain of salt. Pun fully intended.'


###############
# FUNCTIONS
###############

def C_to_K(temp_C):
    '''Converts temperature in degrees C to absolute temperature in Kelvin'''
    T_K = temp_C + 273.15
    return T_K


def water_density(temp_C):
    '''
    Calculates the density of pure water at a given temperature

    Parameters
    ----------
    temp_C : float
        Temperature in degrees C for which water density should be calculated.
        Should be the same temperature at which the sample water density was
        measured, i.e., the field temperature.

    Returns
    -------
    density : float
        Calculated density of pure water in g/cm3.

    '''
    density = (999.83952 +16.952577 * temp_C -7.9905127e-3 * temp_C**2
               -4.6241757e-5 * temp_C**3 +1.0584601e-7 * temp_C**4
               -2.8103006e-10 * temp_C**5) / (1 +0.016887236 * temp_C) / 1000
    return density


def salinity_to_density(salinity, temp_C):
    '''
    Determines water density from measured salinity

    Parameters
    ----------
    salinity : float
        Measured conductivity salinity (in g/L) of a GSL sample.
    temp_C : float
        Temperature at which salinity was measured in degrees C.

    Returns
    -------
    density_gcm3 : TYPE
        Calculated water density in g/cm3.

    '''
    T_K = C_to_K(temp_C)
    p0 = water_density(temp_C)
    density_kgm3 = p0*1000 + A + B*salinity + C*T_K + D*salinity**2 + E*T_K**2 + F*salinity*T_K
    density_gcm3 = density_kgm3/1000
    if salinity < 0 or salinity > 180:
        print(warn_start + 'salinity input' + warn_mid + 'density' + warn_end)
    return density_gcm3


def density_to_salinity(density, temp_C):
    '''
    Determine salinitys from measured water density

    Parameters
    ----------
    density : float
        Density of the water measured in g/cm3.
    temp_C : float
        Temperature at which density was measured in degrees C.

    Returns
    -------
    salinity : float
        Calculated salinity result in g/L

    '''
    
    # Convert temperature
    T_K = C_to_K(temp_C)
    
    # Calculate density of pure water
    p0 = water_density(temp_C)
    
    # Calculate variables
    G = B + F*T_K
    H = A + C*T_K + E*T_K**2 - (density-p0)*1000
    
    salinity = (-G + math.sqrt(G**2 - 4*D*H)) /(2*D)
    
    if salinity < 0 or salinity > 180:
        print(warn_start + 'calculated salinity value' + warn_mid + 'salinity'
              + warn_end)
    
    return salinity

    