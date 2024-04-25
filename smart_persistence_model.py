# -*- coding: utf-8 -*-
"""
Created on Thur. Apr  25 09:01:50 2024

@author: Felix S.

Description: This module contains various function definitions for the Data preprozessing part.

"""


# coding: utf-8

# Imports 

import numpy as np
import pandas as pd
import pvlib



def smart_persistence_pv_forecast(labels: np.ndarray, datetime_labels: list, parameters: dict = None) -> list:
    """
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
        parameters = {
            'latitude': 37.42808,
            'longitude': -122.17023,
            'altitude': 23,
            'panel_elevation': 22.5,
            'panel_azimuth': 195,
            'max_solar_irradiance': 1000,
            'time_delta': 15
        }

    smart_predictions = _calculate_predictions(labels, datetime_labels, parameters)
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
