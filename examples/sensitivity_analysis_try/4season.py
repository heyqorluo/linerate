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

start_tower = linerate.Tower(latitude=50 - 0.0045, longitude=0, altitude=500 - 88)
end_tower = linerate.Tower(latitude=50 + 0.0045, longitude=0, altitude=500 + 88)
span = linerate.Span(conductor=conductor, start_tower=start_tower, end_tower=end_tower, num_conductors=1)

# -----------------------------
# Four representative dates (use 14:00 for each)
# -----------------------------
season_datetimes = {
    "Winter": "2022-01-15T14:00",
    "Spring": "2022-04-15T14:00",
    "Summer": "2022-07-15T14:00",
    "Autumn": "2022-10-15T14:00",
}

# Keep clearness_ratio and ground_albedo consistent across seasons
COMMON_clearness_ratio = 0.5
COMMON_ground_albedo = 0.15

vars_info = {
    "air_temperature": {"label": "Air Temperature (°C)", "baseline": 20.0, "bounds": [-20.0, 40.0]},
    "wind_speed": {"label": "Wind Speed (m/s)", "baseline": 1.66, "bounds": [0.0, 12.0]},
    "wind_direction_deg": {"label": "Wind Angle (°)", "baseline": 80.0, "bounds": [0.0, 90.0]},
}

n_points = 60
Tmax_for_rating = 100.0


def eval_ampacities(span, t_measure, air_T, wind_spd, wind_deg, clearness, albedo):
    weather = linerate.Weather(
        air_temperature=air_T,
        wind_direction=np.radians(wind_deg),
        wind_speed=wind_spd,
        ground_albedo=albedo,
        clearness_ratio=clearness,
    )
    model_cigre = linerate.Cigre601(span, weather, t_measure)
    amp_cigre = model_cigre.compute_steady_state_ampacity(np.array([Tmax_for_rating]))[0]

    model_ieee = linerate.IEEE738(span, weather, t_measure)
    amp_ieee = model_ieee.compute_steady_state_ampacity(np.array([Tmax_for_rating]))[0]

    return amp_cigre, amp_ieee

# -----------------------------
# Plotting setup
# -----------------------------
season_colors = {"Winter": "tab:blue", "Spring": "tab:green", "Summer": "tab:orange", "Autumn": "tab:purple"}
style_cigre = "-"   # solid
style_ieee = "--"   # dashed

# -----------------------------
for var_key, info in vars_info.items():
    lo, hi = info["bounds"]
    xs = np.linspace(lo, hi, n_points)

    plt.figure(figsize=(9, 5))
    for season_idx, (season_name, dt_str) in enumerate(season_datetimes.items()):
        t_measure = np.datetime64(dt_str)

        amps_cigre = np.empty(n_points)
        amps_ieee = np.empty(n_points)

        for i, x in enumerate(xs):
            # baseline for non-swept variables (common across seasons)
            vals = {k: v["baseline"] for k, v in vars_info.items()}
            vals[var_key] = float(x)

            amp_cigre, amp_ieee = eval_ampacities(
                span=span,
                t_measure=t_measure,
                air_T=vals["air_temperature"],
                wind_spd=vals["wind_speed"],
                wind_deg=vals["wind_direction_deg"],
                clearness=COMMON_clearness_ratio,
                albedo=COMMON_ground_albedo,
            )
            amps_cigre[i] = amp_cigre
            amps_ieee[i] = amp_ieee

        color = season_colors.get(season_name, "k")
        markevery = max(1, n_points // 12)

        # plot CIGRE and IEEE curves for this season
        plt.plot(xs, amps_cigre, color=color, linestyle=style_cigre,
                 markevery=markevery, linewidth=1.8, 
                 label=f"{season_name} CIGRE ({dt_str})")
        plt.plot(xs, amps_ieee, color=color, linestyle=style_ieee,
                 markevery=markevery, linewidth=1.4, 
                 label=f"{season_name} IEEE ({dt_str})")

    plt.xlabel(info["label"])
    plt.ylabel("Ampacity (A)")
    plt.title(f"Ampacity vs {info['label']} — 4 seasons (CIGRE vs IEEE)\nclearness={COMMON_clearness_ratio}, albedo={COMMON_ground_albedo}")
    plt.grid(True)
    plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize="small")
    plt.tight_layout(rect=(0, 0, 0.78, 1.0))
    plt.show()

