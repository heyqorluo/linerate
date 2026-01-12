import numpy as np
import matplotlib.pyplot as plt
import linerate

start_tower = linerate.Tower(latitude=50 - 0.0045, longitude=0, altitude=500 - 88)
end_tower = linerate.Tower(latitude=50 + 0.0045, longitude=0, altitude=500 + 88)

time_of_measurement = np.datetime64("2016-10-03T14:00")

# Sensitivity targets: emissivity and solar_absorptivity
vars_info = {
    "emissivity": {"label": "Emissivity (ε)", "baseline": 0.8, "bounds": [0.7, 0.9]},
    "solar_absorptivity": {"label": "Solar absorptivity (α_s)", "baseline": 0.8, "bounds": [0.7, 0.9]},
}

n_points = 60
Tmax_for_rating = 50.0   # maximum conductor temperature for ampacity calculation?

# Define baseline weather conditions
BASE_GROUND_ALBEDO = 0.15
BASE_CLEARNESS = 0.5
BASE_AIR_T = 20.0
BASE_WIND_DIR_DEG = 80.0

def eval_ampacities_simultaneous_change_with_wind(epsilon, wind_spd):

    conductor = linerate.Conductor(
        core_diameter=10.4e-3,
        conductor_diameter=28.1e-3,
        outer_layer_strand_diameter=2.2e-3,
        emissivity=epsilon,
        solar_absorptivity=epsilon,
        temperature1=25,
        temperature2=75,
        resistance_at_temperature1=7.283e-5,
        resistance_at_temperature2=8.688e-5,
        aluminium_cross_section_area=float("nan"),
        constant_magnetic_effect=1,
        current_density_proportional_magnetic_effect=0,
        max_magnetic_core_relative_resistance_increase=1,
    )
    span = linerate.Span(conductor=conductor, start_tower=start_tower, end_tower=end_tower, num_conductors=1)

    weather = linerate.Weather(
        air_temperature=BASE_AIR_T,
        wind_direction=np.radians(BASE_WIND_DIR_DEG),
        wind_speed=wind_spd,
        ground_albedo=BASE_GROUND_ALBEDO,
        clearness_ratio=BASE_CLEARNESS,
    )

    amp_cigre_arr = linerate.Cigre601(span, weather, time_of_measurement).compute_steady_state_ampacity(np.array([Tmax_for_rating]))
    amp_ieee_arr = linerate.IEEE738(span, weather, time_of_measurement).compute_steady_state_ampacity(np.array([Tmax_for_rating]))
    return float(amp_cigre_arr[0]), float(amp_ieee_arr[0])

# For different wind speeds, conduct sensitivity analysis for simultaneous change of emissivity and absorptivity
wind_speeds = [0.5, 1.0, 1.5, 2.0]
lo, hi = vars_info["emissivity"]["bounds"]
xs = np.linspace(lo, hi, n_points)

colors = ["tab:blue", "tab:green", "tab:orange", "tab:purple"]

plt.figure(figsize=(9, 5))
for idx, ws in enumerate(wind_speeds):
    amps_cigre = np.empty(n_points)
    amps_ieee = np.empty(n_points)
    for i, eps in enumerate(xs):
        ac, ai = eval_ampacities_simultaneous_change_with_wind(epsilon=float(eps), wind_spd=ws)
        amps_cigre[i] = ac
        amps_ieee[i] = ai

    # plot CIGRE and IEEE for this wind speed
    plt.plot(xs, amps_cigre, color=colors[idx], linestyle="-", label=f"CIGRE, wind={ws} m/s")
    plt.plot(xs, amps_ieee, color=colors[idx], linestyle="--", label=f"IEEE, wind={ws} m/s")

    # Print uncertainty around midpoint
    midpoint = 0.8
    mid_ac, mid_ai = eval_ampacities_simultaneous_change_with_wind(epsilon=midpoint, wind_spd=ws)
    plus_ac = amps_cigre.max() - mid_ac
    minus_ac = mid_ac - amps_cigre.min()
    plus_ai = amps_ieee.max() - mid_ai
    minus_ai = mid_ai - amps_ieee.min()
    
    pct_plus_ac = (plus_ac / mid_ac * 100.0) if mid_ac != 0 else float("nan")
    pct_minus_ac = (minus_ac / mid_ac * 100.0) if mid_ac != 0 else float("nan")
    pct_plus_ai = (plus_ai / mid_ai * 100.0) if mid_ai != 0 else float("nan")
    pct_minus_ai = (minus_ai / mid_ai * 100.0) if mid_ai != 0 else float("nan")

    print(
        f"Wind Speed={ws} m/s | CIGRE Ampacity={mid_ac:.1f} A, +{pct_plus_ac:.2f}% / -{pct_minus_ac:.2f}% | "
        f"IEEE Ampacity={mid_ai:.1f} A, +{pct_plus_ai:.2f}% / -{pct_minus_ai:.2f}%"
    )

plt.xlabel("Emissivity = Solar absorptivity (ε = α_s)")
plt.ylabel("Conductor Ampacity (A)")
plt.title("Ampacity vs emissivity/absorptivity for different wind speeds (ε = α_s)")
plt.ylim(500, 1200)  
plt.grid(True)
plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize="small")
plt.tight_layout(rect=(0, 0, 0.78, 1.0))
plt.show()
