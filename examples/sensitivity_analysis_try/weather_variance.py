import numpy as np
import matplotlib.pyplot as plt
import linerate

# Define conductor type
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

# Create towers for a span that faces east-west
start_tower = linerate.Tower(latitude=50 - 0.0045, longitude=0, altitude=500 - 88)
end_tower = linerate.Tower(latitude=50 + 0.0045, longitude=0, altitude=500 + 88)
span = linerate.Span(conductor=conductor, start_tower=start_tower, end_tower=end_tower, num_conductors=1)
time_of_measurement = np.datetime64("2016-10-03 14:00")

# Create the weather data class
# variables, baseline and bounds for sensitivity analysis
vars_info = {
    "air_temperature": {"label": "Air Temperature (°C)", "baseline": 20.0, "bounds": [-10.0, 40.0]},
    "wind_speed": {"label": "Wind Speed (m/s)", "baseline": 1.66, "bounds": [0.0, 10.0]},
    "wind_direction_deg": {"label": "Wind Angle (°)", "baseline": 80.0, "bounds": [0.0, 90.0]},
    "clearness_ratio": {"label": "Clearness Ratio (0-1)", "baseline": 0.5, "bounds": [0.0, 1.2]}, # value selection detailed in cigre601
    "ground_albedo": {"label": "Ground albedo (0-1)", "baseline": 0.15, "bounds": [0.05, 0.8]}, # value selection detailed in cigre601
}

n_points = 60
Tmax_for_rating = 50.0   # (°C) used to compute ampacity

def eval_case(air_T, wind_spd, wind_deg, clearness, albedo):
    weather = linerate.Weather(
        air_temperature=air_T,
        wind_direction=np.radians(wind_deg),
        wind_speed=wind_spd,
        ground_albedo=albedo,
        clearness_ratio=clearness,
    )
    model_cigre = linerate.Cigre601(span, weather, time_of_measurement)
    amp_cigre = model_cigre.compute_steady_state_ampacity(np.array([Tmax_for_rating]))[0]
    
    model_ieee = linerate.IEEE738(span, weather, time_of_measurement)
    amp_ieee = model_ieee.compute_steady_state_ampacity(np.array([Tmax_for_rating]))[0]
    return amp_cigre, amp_ieee



for var, info in vars_info.items():
    lo, hi = info["bounds"]
    xs = np.linspace(lo, hi, n_points) 
    amps_ieee = np.empty(n_points)
    amps_cigre = np.empty(n_points)

    for i, x in enumerate(xs): # i is the index, x is the variable value
        vals = {k: v["baseline"] for k, v in vars_info.items()} # set all variables to baseline
        vals[var] = x
        amps = eval_case(
            air_T=vals["air_temperature"],
            wind_spd=vals["wind_speed"],
            wind_deg=vals["wind_direction_deg"],
            clearness=vals["clearness_ratio"],
            albedo=vals["ground_albedo"],
        )
        amps_cigre[i] = amps[0]
        amps_ieee[i] = amps[1]


    plt.figure(figsize=(6, 4))
    plt.plot(xs, amps_cigre, "-k", label="CIGRE 601")
    plt.plot(xs, amps_ieee, "--r", label="IEEE 738")
    plt.xlabel(info["label"])
    plt.ylabel("Conductor Ampacity (A)")
    plt.title(f"Ampacity vs. {info["label"]} Sensitivity Analysis")
    plt.legend()
    plt.grid()
    plt.show()
