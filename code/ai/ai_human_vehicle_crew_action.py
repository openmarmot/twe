"""
repo : https://github.com/openmarmot/twe

notes : vehicle crew action enum
"""

from enum import Enum


class VehicleCrewAction(Enum):
    NONE = "none"
    DRIVING = "driving"
    ROTATING = "rotating"
    ROTATING_TURRET = "rotating turret"
    IDLE = "idle"
    WAITING = "waiting"
    WAITING_FOR_ROTATE = "Waiting for driver to rotate the vehicle"
    WAITING_FOR_ROTATE_FIRE_MISSION = (
        "Waiting for driver to rotate the vehicle for fire mission"
    )
    WAITING_FOR_POSITION_FIRE_MISSION = (
        "Waiting for driver to get in position for fire mission"
    )
    WAITING_FOR_CLOSE_DISTANCE = "Waiting for driver to close distance"
    ENGAGING = "Engaging"
    RELOADING_PRIMARY = "reloading primary weapon"
    RELOADING_COAX = "reloading coax gun"
    OUT_OF_AMMO = "Out of Ammo"
    TURRET_JAMMED = "Turret Jammed"
    WEAPONS_DAMAGED = "Weapons Damaged"
    CLEARING_JAM = "Clearing weapon jam"
    SCANNING = "Scanning for targets"
    MONITORING = "Monitoring the situation"
    WAITING_FOR_PASSENGERS = "waiting for passengers"
    WAITING_AT_DESTINATION = "Waiting at destination"
    OPERATING_RADIO = "Beep boop. operating the radio"
