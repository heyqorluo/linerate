import numpy as np
import matplotlib.pyplot as plt
import linerate

conductor = linerate.Conductor(
    core_diameter=10.4e-3,
    conductor_diameter=28.1e-3,
    outer_layer_strand_diameter=2.2e-3,
    emissivity=0.9,
    solar_absorptivity=0.9,
    temperature1=25,
    temperature2=75,
    resistance_at_temperature1=7.283e-5,
    resistance_at_temperature2=8.688e-5,
    aluminium_cross_section_area=float("nan"),
    constant_magnetic_effect=1,
    current_density_proportional_magnetic_effect=0,
    max_magnetic_core_relative_resistance_increase=1,
)

# baseline tower parameters
BASE_LAT = 50.0
BASE_LON = 0.0
BASE_ALT = 500.0

# time and common weather
time_of_measurement = np.datetime64("2016-10-03T14:00")
weather = linerate.Weather(
        air_temperature=20.0,
        wind_direction=np.radians(80),
        wind_speed=1.66,
        ground_albedo=0.15,
        clearness_ratio=0.5,
    )

Tmax_for_rating = 50
n_points = 60

# create span from tower parameters
def make_span_from_towers(start_lat, start_lon, start_alt, end_lat, end_lon, end_alt):
    start_tower = linerate.Tower(latitude=start_lat, longitude=start_lon, altitude=start_alt)
    end_tower = linerate.Tower(latitude=end_lat, longitude=end_lon, altitude=end_alt)
    span = linerate.Span(conductor=conductor, start_tower=start_tower, end_tower=end_tower, num_conductors=1)
    return span

# compute ampacities for a given span
def compute_ampacities_for_span(span, t_measure):
    amp_cigre_arr = linerate.Cigre601(span, weather, t_measure).compute_steady_state_ampacity(np.array([Tmax_for_rating]))
    amp_ieee_arr = linerate.IEEE738(span, weather, t_measure).compute_steady_state_ampacity(np.array([Tmax_for_rating]))
    return float(amp_cigre_arr[0]), float(amp_ieee_arr[0])

# -----------------------------
# Sweep 1: vary tower separation (latitude offset)
# start_lat = BASE_LAT - offset, end_lat = BASE_LAT + offset
# -----------------------------
# lat_offsets = np.linspace(0.0005, 0.01, n_points)  # degrees
# amps_cigre_sep = np.empty(n_points)
# amps_ieee_sep = np.empty(n_points)

# for i, off in enumerate(lat_offsets):
#     start_lat = BASE_LAT - off
#     end_lat = BASE_LAT + off
#     span = make_span_from_towers(start_lat, BASE_LON, BASE_ALT, end_lat, BASE_LON, BASE_ALT)
#     ac, ai = compute_ampacities_for_span(span, time_of_measurement)
#     amps_cigre_sep[i] = ac
#     amps_ieee_sep[i] = ai

# plt.figure(figsize=(7, 4))
# plt.plot(lat_offsets, amps_cigre_sep, "-k", label="CIGRE 601")
# plt.plot(lat_offsets, amps_ieee_sep, "--r", label="IEEE 738")
# plt.xlabel("Latitude offset (deg)")
# plt.ylabel("Ampacity (A)")
# plt.title("Sensitivity: tower separation (latitude) effect on ampacity")
# plt.ylim(1000, 1600)
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# -----------------------------
# Sweep 2: vary end tower altitude
# -----------------------------
end_alt_deltas = np.linspace(-200.0, 200.0, n_points)  # meters
amps_cigre_alt = np.empty(n_points)
amps_ieee_alt = np.empty(n_points)

for i, delta in enumerate(end_alt_deltas):
    start_alt = BASE_ALT
    end_alt = BASE_ALT + delta
    start_lat = BASE_LAT - 0.0045
    end_lat = BASE_LAT + 0.0045
    span = make_span_from_towers(start_lat, BASE_LON, start_alt, end_lat, BASE_LON, end_alt)
    ac, ai = compute_ampacities_for_span(span, time_of_measurement)
    amps_cigre_alt[i] = ac
    amps_ieee_alt[i] = ai

plt.figure(figsize=(7, 4))
plt.plot(end_alt_deltas, amps_cigre_alt, "-k", label="CIGRE 601")
plt.plot(end_alt_deltas, amps_ieee_alt, "--r", label="IEEE 738")
plt.xlabel("Altitude offset (m)")
plt.ylabel("Ampacity (A)")
plt.title("Sensitivity: tower altitude effect on ampacity")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
