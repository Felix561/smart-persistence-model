# -*- coding: utf-8 -*-
"""
Created on Thur. Apr  25 09:01:50 2024

@author: Felix S.

Description: This module contains various function definitions for the Data preprozessing part.

"""


# coding: utf-8

# imports 

import subprocess
import sys

# Function to install a package using pip
def install_package(package_name: str):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Try to import pvlib and install it if not already installed
try:
    import pvlib
except ImportError:
    install_package('pvlib')
    import pvlib

# Other imports
import numpy as np
import pandas as pd
from math import *
import calendar
import datetime
import time




# My own SPM implementation:

def spm_pv_forecast_v1(labels: np.ndarray, datetime_labels: list, parameters: dict = None) -> np.array:
    """
    Implementation of Version 1.
    Calculates the Smart Persistence Predictions for given labels and timestamps.

    Parameters:
    labels (numpy.ndarray): The labels for the data.
    datetime_labels (list): The timestamps for the data.
    parameters (dict, optional): A dictionary containing the parameters required for calculation.
        If None, default parameters will be used.

        The `parameters` dictionary should contain the following keys:

        - 'latitude' (float): Latitude of the location in decimal degrees.
        - 'longitude' (float): Longitude of the location in decimal degrees.
        - 'altitude' (int): Altitude of the location in meters.
        - 'panel_elevation' (float): Elevation angle of the solar PV arrays in degrees.
        - 'panel_azimuth' (float): Azimuth angle of the solar PV arrays in degrees.
        - 'max_solar_irradiance' (int): Maximum solar irradiance in W/m^2.
        - 'time_delta' (int): Forecast horizon in minutes.

        If no parameters are provided, default parameters from the SKIPP'D Benchmark Dataset will be used,
        corresponding to the PV installation at Stanford University.

    Returns:
    list: A list consisting of Smart Persistence Predictions.
    """

    # Default parameters if none provided
    if parameters is None:
        # Standart parameters for the SKIPPD Dataset (Source: https://doi.org/10.1016/j.solener.2023.03.043)
        parameters = {
            'latitude': 37.42808,
            'longitude': -122.17023,
            'altitude': 23,
            'panel_elevation': 22.5,
            'panel_azimuth': 195,
            'max_solar_irradiance': 1000,
            'time_delta': 15,
            'effective_panel_area': 24.9842,
        }

    smart_predictions = _calculate_predictions(labels, datetime_labels, parameters)
    smart_predictions = np.array(smart_predictions)
    return smart_predictions



def _calculate_predictions(labels: np.ndarray, datetime_labels: list, parameters: dict) -> list:
    times = []
    smart_predictions = []
    for i, time in enumerate(datetime_labels):
        actual_pv_output = labels[i]
        smart_pred, _, _ = _the_future_pv_output(time, actual_pv_output, parameters)
        times.append(time)
        smart_predictions.append(np.float32(smart_pred))
    return smart_predictions


def _the_future_pv_output(time: pd.Timestamp, actual_pv_output: float, parameters: dict) -> tuple:
    try:
        actual_clr_pv_output = _calculate_clr_pv_output(time, parameters)
        future_clr_pv_output = _calculate_clr_pv_output(time + pd.Timedelta(value=parameters['time_delta'], unit='minutes'), parameters)
        k_clr = actual_pv_output / actual_clr_pv_output
        future_pv_output = k_clr * future_clr_pv_output
        return future_pv_output, future_clr_pv_output, k_clr
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None, None

def _calculate_clr_pv_output(date: pd.Timestamp, parameters: dict) -> float:
    try:
        sun_zenith_deg, sun_azimuth_deg = _calc_sun_position(date, parameters)
        sun_zenith_rad = np.radians(sun_zenith_deg)
        sun_azimuth_rad = np.radians(sun_azimuth_deg)
        panel_elevation_rad = np.radians(parameters['panel_elevation'])
        panel_azimuth_rad = np.radians(parameters['panel_azimuth'])
        pclr_t = parameters['max_solar_irradiance'] * parameters['effective_panel_area'] * (np.cos(panel_elevation_rad)* np.cos(sun_zenith_rad) + np.sin(panel_elevation_rad)* np.sin(sun_zenith_rad)* np.cos((sun_azimuth_rad-panel_azimuth_rad)))
        return pclr_t
    except Exception as e:
        print(f"An error occurred while calculating clear sky PV output: {str(e)}")
        return None

def _calc_sun_position(date: pd.Timestamp, parameters: dict) -> tuple:
    try:
        solar_position = pvlib.solarposition.get_solarposition(
                                                                date,
                                                                parameters['latitude'],
                                                                parameters['longitude'],
                                                                parameters['altitude'],
                                                                pressure=None,
                                                                method='nrel_numpy'
                                                                )
        sun_azimuth = solar_position['azimuth'].values[0]
        sun_zenith = solar_position['elevation'].values[0]
        return sun_zenith, sun_azimuth
    except Exception as e:
        print(f"An error occurred while calculating solar position: {str(e)}")
        return None, None




# implementation by Yuchao Nie (used in the SUNSET model paper):

def spm_pv_forecast_v2(labels: np.ndarray, datetime_labels: list, parameters: dict = None) -> np.ndarray:
    """
    Implementaion Version 2.
    Calculates the per_prediction using the Relative_output function for each timestamp in datetime_labels.

    Parameters:
    labels (numpy.ndarray): Array of labels representing PV outputs.
    datetime_labels (list): List of datetime objects representing timestamps.
    parameters (dict, optional): Dictionary of parameters. Defaults to None.
        If None, default parameters will be used.

        The `parameters` dictionary should contain the following keys:

        - 'latitude' (float): Latitude of the location in decimal degrees.
        - 'longitude' (float): Longitude of the location in decimal degrees.
        - 'altitude' (int): Altitude of the location in meters.
        - 'panel_elevation' (float): Elevation angle of the solar PV arrays in degrees.
        - 'panel_azimuth' (float): Azimuth angle of the solar PV arrays in degrees.
        - 'max_solar_irradiance' (int): Maximum solar irradiance in W/m^2.
        - 'time_delta' (int): Forecast horizon in minutes.
        - 'time_zone_center_longitude': time zone correction, for your time zone, behind or before UTC (Coordinated Universal Time) in deggrees.

        If no parameters are provided, default parameters from the SKIPP'D Benchmark Dataset will be used,
        corresponding to the PV installation at Stanford University.


    Returns:
    numpy.ndarray: Array of per_predictions.
    """
    # Default parameters if none provided
    if parameters is None:
        # Standart parameters for the SKIPPD Dataset (Source: https://doi.org/10.1016/j.solener.2023.03.043)
        parameters = {
            'latitude': 37.42808,                   # Latitude of the location in decimal degrees
            'longitude': -122.17023,                # Longitude of the location in decimal degrees
            'altitude': 23,                         # Altitude of the location in meters
            'panel_elevation': 22.5 ,               # Elevation angle of the solar PV arrays in degrees
            'panel_azimuth': 195,                   # Azimuth angle of the solar PV arrays in degrees
            'max_solar_irradiance': 1000,           # Maximum solar irradiance in W/m^2
            'effective_panel_area': 24.98,          # Effective PV panel area in square meters
            'time_delta': 15,                       # forecast horizon in minutes
            'time_zone_center_longitude': -120      # time zone correction, for your time zone, behind or before UTC (Coordinated Universal Time) in deggrees.
        }

    ntimes = len(datetime_labels)
    per_prediction = np.zeros(ntimes)
    for i in range(ntimes):
        CSI_cur, P_theo_cur = Relative_output(datetime_labels[i], labels[i],parameters)
        CSI, P_theo_pred = Relative_output(datetime_labels[i] + datetime.timedelta(minutes=parameters["time_delta"]), labels[i],parameters)
        per_prediction[i] = CSI_cur * P_theo_pred
    return per_prediction


def Relative_output(times: datetime.datetime, PV_ops: float, parameters: dict) -> tuple[float, float]:
    """
    Calculates the theoretical and relative PV output.

    Parameters:
    times (datetime.datetime): A single datetime object.
    PV_ops (float): Single PV output at the given datetime.
    parameters (dict): Dictionary of parameters.

    Returns:
    tuple: Relative PV output and theoretical PV output.
    """

    # Constants
    P0=parameters["max_solar_irradiance"]/1000  # Solar energy incident on Earth's surface in kW/m2
    A_eff=parameters["effective_panel_area"]    # Effective area covered by panels in m2
    epsilon=radians(parameters["panel_elevation"]) # Elevation angle of solar panel
    zeta=radians(parameters["panel_azimuth"]) # Azimuth angle of solar panel
    latitude=radians(parameters["latitude"]) # Latitudinal co-ordinate of Stanford

    day_of_year, time_of_day=inputs_for_rel_op(times,parameters)
    # Calculating parameters dependent on time, day and location
    alpha=2*pi*(time_of_day-43200)/86400 # Hour angle in radians
    delta=radians(23.44*sin(radians((360/365.25)*(day_of_year-80)))); # Solar declination angle
    chi=acos(sin(delta)*sin(latitude)+cos(delta)*cos(latitude)*cos(alpha))# Zenith angle of sun
    tan_xi=sin(alpha)/(sin(latitude)*cos(alpha)-cos(latitude)*tan(delta)) # tan(Azimuth angle of sun,xi)
    if alpha>0 and tan_xi>0:
        xi=pi+atan(tan_xi)
    elif alpha>0 and tan_xi<0:
        xi=2*pi+atan(tan_xi)
    elif alpha<0 and tan_xi>0:
        xi=atan(tan_xi)
    else:
        xi=pi+atan(tan_xi)
    # Calculating theoretical output
    P_theo=P0*A_eff*(cos(epsilon)*cos(chi)+sin(epsilon)*sin(chi)*cos(xi-zeta))
    # To deal with troublesome cases
    if P_theo<0.05:
        P_theo=0.05
    if PV_ops<0.05:
        PV_ops=0.05
    Rel_PV_op=PV_ops/P_theo
    if Rel_PV_op>1.5:
        Rel_PV_op=1.5

    return Rel_PV_op, P_theo

def inputs_for_rel_op(date_and_time: datetime.datetime, parameters: dict) -> tuple[int, int]:
    """
    Converts a datetime object to day of year and time of day in seconds.

    Parameters:
    date_and_time (datetime.datetime): A datetime object.
    parameters (dict): Dictionary of parameters.

    Returns:
    tuple: Day of year and time of day in seconds.
    """
    # Time correction. The center of PST is -120 W, while the logitude of the PV array is about 2 degree west of PST center

    time_zone_center_longitude = parameters["time_zone_center_longitude"]
    panel_longitude = parameters["longitude"] # minus sign indicate west longitude
    correction = np.abs(60/15*(panel_longitude - time_zone_center_longitude))
    min_correction = int(correction) # Local time delay in minutes from the PST
    sec_correction = int((correction - min_correction)*60)  # Local time delay in seconds from the PST
    if date_and_time.minute<=min_correction:
        date_and_time= date_and_time.replace(hour = date_and_time.hour-1, minute=60+date_and_time.minute-min_correction-1, second=60-sec_correction)
    else:
        date_and_time = date_and_time.replace(minute=date_and_time.minute-min_correction-1, second=60-sec_correction)

    time_of_day=date_and_time.hour * 3600 + date_and_time.minute * 60 + date_and_time.second

    # Following piece of code calculates day of year
    months=[31,28,31,30,31,30,31,31,30,31,30,31] # days in each month
    if (date_and_time.year % 4 == 0) and (date_and_time.year % 100 != 0 or date_and_time.year % 400 ==0 ) == True:
        months[1]=29 # Modification for leap year
    day_of_year=sum(months[:date_and_time.month-1])+date_and_time.day

    # Fix for daylight savings (NOTE: This doesn't work for 1st hour of each day in DST period.)

    # which day of year is the 2nd Sunday of March in that year
    dst_start_day = sum(months[:2]) + calendar.monthcalendar(date_and_time.year,date_and_time.month)[1][6]
    # which day of year is the 1st Sunday of Nov in that year
    dst_end_day = sum(months[:10]) + calendar.monthcalendar(date_and_time.year,date_and_time.month)[0][6]
    if day_of_year >= dst_start_day and day_of_year < dst_end_day:
        time_of_day=time_of_day-3600

    return day_of_year, time_of_day
    






