import datetime

import numpy as np
from numpy import nan
import pandas as pd
import pytz

import pytest
from pytz.exceptions import UnknownTimeZoneError
from pandas.util.testing import assert_series_equal, assert_frame_equal

from pvlib.location import Location

from test_solarposition import expected_solpos
from conftest import requires_scipy

aztz = pytz.timezone('US/Arizona')

def test_location_required():
    Location(32.2, -111)

def test_location_all():
    Location(32.2, -111, 'US/Arizona', 700, 'Tucson')


@pytest.mark.parametrize('tz', [
    aztz, 'America/Phoenix',  -7, -7.0,
])
def test_location_tz(tz):
    Location(32.2, -111, tz)


def test_location_invalid_tz():
    with pytest.raises(UnknownTimeZoneError):
        Location(32.2, -111, 'invalid')


def test_location_invalid_tz_type():
    with pytest.raises(TypeError):
        Location(32.2, -111, [5])


def test_location_print_all():
    tus = Location(32.2, -111, 'US/Arizona', 700, 'Tucson')
    expected_str = 'Tucson: latitude=32.2, longitude=-111, tz=US/Arizona, altitude=700'
    assert tus.__str__() == expected_str

def test_location_print_pytz():
    tus = Location(32.2, -111, aztz, 700, 'Tucson')
    expected_str = 'Tucson: latitude=32.2, longitude=-111, tz=US/Arizona, altitude=700'
    assert tus.__str__() == expected_str


@requires_scipy
def test_get_clearsky():
    tus = Location(32.2, -111, 'US/Arizona', 700, 'Tucson')
    times = pd.DatetimeIndex(start='20160101T0600-0700',
                             end='20160101T1800-0700',
                             freq='3H')
    clearsky = tus.get_clearsky(times)
    expected = pd.DataFrame(data=np.
        array([[   0.        ,    0.        ,    0.        ],
               [ 258.60422702,  761.57329257,   50.1235982 ],
               [ 611.96347869,  956.95353414,   70.8232806 ],
               [ 415.10904044,  878.52649603,   59.07820922],
               [   0.        ,    0.        ,    0.        ]]),
                            columns=['ghi', 'dni', 'dhi'],
                            index=times)
    assert_frame_equal(expected, clearsky, check_less_precise=2)


def test_get_clearsky_ineichen_supply_linke():
    tus = Location(32.2, -111, 'US/Arizona', 700)
    times = pd.date_range(start='2014-06-24', end='2014-06-25', freq='3h')
    times_localized = times.tz_localize(tus.tz)
    expected = pd.DataFrame(np.
        array([[    0.        ,     0.        ,     0.        ],
               [    0.        ,     0.        ,     0.        ],
               [   79.73090244,   316.16436502,    40.45759009],
               [  703.43653498,   876.41452667,    95.15798252],
               [ 1042.37962396,   939.86391062,   118.44687715],
               [  851.32411813,   909.11186737,   105.36662462],
               [  257.18266827,   646.16644264,    62.02777094],
               [    0.        ,     0.        ,     0.        ],
               [    0.        ,     0.        ,     0.        ]]),
                            columns=['ghi', 'dni', 'dhi'],
                            index=times_localized)
    out = tus.get_clearsky(times_localized, linke_turbidity=3)
    assert_frame_equal(expected, out, check_less_precise=2)


def test_get_clearsky_haurwitz():
    tus = Location(32.2, -111, 'US/Arizona', 700, 'Tucson')
    times = pd.DatetimeIndex(start='20160101T0600-0700',
                             end='20160101T1800-0700',
                             freq='3H')
    clearsky = tus.get_clearsky(times, model='haurwitz')
    expected = pd.DataFrame(data=np.array(
                            [[   0.        ],
                             [ 242.30085588],
                             [ 559.38247117],
                             [ 384.6873791 ],
                             [   0.        ]]),
                            columns=['ghi'],
                            index=times)
    assert_frame_equal(expected, clearsky)


def test_get_clearsky_simplified_solis():
    tus = Location(32.2, -111, 'US/Arizona', 700, 'Tucson')
    times = pd.DatetimeIndex(start='20160101T0600-0700',
                             end='20160101T1800-0700',
                             freq='3H')
    clearsky = tus.get_clearsky(times, model='simplified_solis')
    expected = pd.DataFrame(data=np.
        array([[   0.        ,    0.        ,    0.        ],
               [  70.00146271,  638.01145669,  236.71136245],
               [ 101.69729217,  852.51950946,  577.1117803 ],
               [  86.1679965 ,  755.98048017,  385.59586091],
               [   0.        ,    0.        ,    0.        ]]),
                            columns=['dhi', 'dni', 'ghi'],
                            index=times)
    expected = expected[['ghi', 'dni', 'dhi']]
    assert_frame_equal(expected, clearsky, check_less_precise=2)


def test_get_clearsky_simplified_solis_apparent_elevation():
    tus = Location(32.2, -111, 'US/Arizona', 700, 'Tucson')
    times = pd.DatetimeIndex(start='20160101T0600-0700',
                             end='20160101T1800-0700',
                             freq='3H')
    solar_position = {'apparent_elevation': pd.Series(80, index=times),
                      'apparent_zenith': pd.Series(10, index=times)}
    clearsky = tus.get_clearsky(times, model='simplified_solis',
                                solar_position=solar_position)
    expected = pd.DataFrame(data=np.
        array([[  131.3124497 ,  1001.14754036,  1108.14147919],
               [  131.3124497 ,  1001.14754036,  1108.14147919],
               [  131.3124497 ,  1001.14754036,  1108.14147919],
               [  131.3124497 ,  1001.14754036,  1108.14147919],
               [  131.3124497 ,  1001.14754036,  1108.14147919]]),
                            columns=['dhi', 'dni', 'ghi'],
                            index=times)
    expected = expected[['ghi', 'dni', 'dhi']]
    assert_frame_equal(expected, clearsky, check_less_precise=2)


def test_get_clearsky_simplified_solis_dni_extra():
    tus = Location(32.2, -111, 'US/Arizona', 700, 'Tucson')
    times = pd.DatetimeIndex(start='20160101T0600-0700',
                             end='20160101T1800-0700',
                             freq='3H')
    clearsky = tus.get_clearsky(times, model='simplified_solis',
                                dni_extra=1370)
    expected = pd.DataFrame(data=np.
        array([[   0.        ,    0.        ,    0.        ],
               [  67.82281485,  618.15469596,  229.34422063],
               [  98.53217848,  825.98663808,  559.15039353],
               [  83.48619937,  732.45218243,  373.59500313],
               [   0.        ,    0.        ,    0.        ]]),
                            columns=['dhi', 'dni', 'ghi'],
                            index=times)
    expected = expected[['ghi', 'dni', 'dhi']]
    assert_frame_equal(expected, clearsky)


def test_get_clearsky_simplified_solis_pressure():
    tus = Location(32.2, -111, 'US/Arizona', 700, 'Tucson')
    times = pd.DatetimeIndex(start='20160101T0600-0700',
                             end='20160101T1800-0700',
                             freq='3H')
    clearsky = tus.get_clearsky(times, model='simplified_solis',
                                pressure=95000)
    expected = pd.DataFrame(data=np.
        array([[   0.        ,    0.        ,    0.        ],
               [  70.20556637,  635.53091983,  236.17716435],
               [ 102.08954904,  850.49502085,  576.28465815],
               [  86.46561686,  753.70744638,  384.90537859],
               [   0.        ,    0.        ,    0.        ]]),
                            columns=['dhi', 'dni', 'ghi'],
                            index=times)
    expected = expected[['ghi', 'dni', 'dhi']]
    assert_frame_equal(expected, clearsky, check_less_precise=2)


def test_get_clearsky_simplified_solis_aod_pw():
    tus = Location(32.2, -111, 'US/Arizona', 700, 'Tucson')
    times = pd.DatetimeIndex(start='20160101T0600-0700',
                             end='20160101T1800-0700',
                             freq='3H')
    clearsky = tus.get_clearsky(times, model='simplified_solis',
                                aod700=0.25, precipitable_water=2.)
    expected = pd.DataFrame(data=np.
        array([[   0.        ,    0.        ,    0.        ],
               [  85.77821205,  374.58084365,  179.48483117],
               [ 143.52743364,  625.91745295,  490.06254157],
               [ 114.63275842,  506.52275195,  312.24711495],
               [   0.        ,    0.        ,    0.        ]]),
                            columns=['dhi', 'dni', 'ghi'],
                            index=times)
    expected = expected[['ghi', 'dni', 'dhi']]
    assert_frame_equal(expected, clearsky, check_less_precise=2)


def test_get_clearsky_valueerror():
    tus = Location(32.2, -111, 'US/Arizona', 700, 'Tucson')
    times = pd.DatetimeIndex(start='20160101T0600-0700',
                             end='20160101T1800-0700',
                             freq='3H')
    with pytest.raises(ValueError):
        clearsky = tus.get_clearsky(times, model='invalid_model')


def test_from_tmy_3():
    from test_tmy import tmy3_testfile
    from pvlib.tmy import readtmy3
    data, meta = readtmy3(tmy3_testfile)
    loc = Location.from_tmy(meta, data)
    assert loc.name is not None
    assert loc.altitude != 0
    assert loc.tz != 'UTC'
    assert_frame_equal(loc.tmy_data, data)


def test_from_tmy_2():
    from test_tmy import tmy2_testfile
    from pvlib.tmy import readtmy2
    data, meta = readtmy2(tmy2_testfile)
    loc = Location.from_tmy(meta, data)
    assert loc.name is not None
    assert loc.altitude != 0
    assert loc.tz != 'UTC'
    assert_frame_equal(loc.tmy_data, data)


def test_get_solarposition(expected_solpos):
    from test_solarposition import golden_mst
    times = pd.date_range(datetime.datetime(2003,10,17,12,30,30),
                          periods=1, freq='D', tz=golden_mst.tz)
    ephem_data = golden_mst.get_solarposition(times, temperature=11)
    ephem_data = np.round(ephem_data, 3)
    expected_solpos.index = times
    expected_solpos = np.round(expected_solpos, 3)
    assert_frame_equal(expected_solpos, ephem_data[expected_solpos.columns])


def test_get_airmass():
    tus = Location(32.2, -111, 'US/Arizona', 700, 'Tucson')
    times = pd.DatetimeIndex(start='20160101T0600-0700',
                             end='20160101T1800-0700',
                             freq='3H')
    airmass = tus.get_airmass(times)
    expected = pd.DataFrame(data=np.array(
                            [[        nan,         nan],
                             [ 3.61046506,  3.32072602],
                             [ 1.76470864,  1.62309115],
                             [ 2.45582153,  2.25874238],
                             [        nan,         nan]]),
                            columns=['airmass_relative', 'airmass_absolute'],
                            index=times)
    assert_frame_equal(expected, airmass)

    airmass = tus.get_airmass(times, model='young1994')
    expected = pd.DataFrame(data=np.array(
                            [[        nan,         nan],
                             [ 3.6075018 ,  3.31800056],
                             [ 1.7641033 ,  1.62253439],
                             [ 2.45413091,  2.25718744],
                             [        nan,         nan]]),
                            columns=['airmass_relative', 'airmass_absolute'],
                            index=times)
    assert_frame_equal(expected, airmass)


def test_get_airmass_valueerror():
    tus = Location(32.2, -111, 'US/Arizona', 700, 'Tucson')
    times = pd.DatetimeIndex(start='20160101T0600-0700',
                             end='20160101T1800-0700',
                             freq='3H')
    with pytest.raises(ValueError):
        clearsky = tus.get_airmass(times, model='invalid_model')


def test_Location___repr__():
    tus = Location(32.2, -111, 'US/Arizona', 700, 'Tucson')
    assert tus.__repr__()==('Tucson: latitude=32.2, longitude=-111, '+
    'tz=US/Arizona, altitude=700')
