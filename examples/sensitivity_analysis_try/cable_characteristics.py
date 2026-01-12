import numpy as np
import matplotlib.pyplot as plt
import linerate

# Define distinct conductor types
lines = [
    {
        "id": 18,
        "name": "100m_50S_ACSR_6+7_4.72+1.57m_",   
        "core_diameter": 0.00471,
        "conductor_diameter": 0.01415,
        "outer_layer_strand_diameter": 0.00472,
        "emissivity": 0.8, # assumed value
        "solar_absorptivity": 0.8, # assumed value
        "temperature1": 25,
        "temperature2": 75,
        "resistance_at_temperature1": 0.000291986,
        "resistance_at_temperature2": 0.000291986, # keep constant for now..
        "aluminium_cross_section_area": None, # should be calculated??
        "constant_magnetic_effect": 1,
        "current_density_proportional_magnetic_effect": 0,
        "max_magnetic_core_relative_resistance_increase": 1,
    },
    # {
    #     "id": 10,
    #     "name": "0.1i_50S_HDCU_7_0.136i_",
    #     "core_diameter": 0, # this value cannot be 0!!
    #     "conductor_diameter": 0.0103632,
    #     "outer_layer_strand_diameter": 0.0034544,
    #     "emissivity": 0.8,
    #     "solar_absorptivity": 0.8,
    #     "temperature1": 25,
    #     "temperature2": 75,
    #     "resistance_at_temperature1": 0.000305,
    #     "resistance_at_temperature2": 0.000305,
    #     "aluminium_cross_section_area": None,
    #     "constant_magnetic_effect": 0,
    #     "current_density_proportional_magnetic_effect": 0,
    #     "max_magnetic_core_relative_resistance_increase": 1,
    # },
    {
        "id": 19,
        "name": "0.15i_50S_ACSR_30+7_0.102x2i_WOL",
        "core_diameter": 0.0077724,
        "conductor_diameter": 0.0181356,
        "outer_layer_strand_diameter": 0.0025908,
        "emissivity": 0.8,
        "solar_absorptivity": 0.8,
        "temperature1": 25,
        "temperature2": 75,
        "resistance_at_temperature1": 0.000300978,
        "resistance_at_temperature2": 0.000300978,
        "aluminium_cross_section_area": None,
        "constant_magnetic_effect": 1,
        "current_density_proportional_magnetic_effect": 0,
        "max_magnetic_core_relative_resistance_increase": 1,
    },
    {
        "id": 21,
        "name": "0.1i_50_ACSR_6+7_0.186+0.062i_DO",
        "core_diameter": 0.0047244,
        "conductor_diameter": 0.0141732,
        "outer_layer_strand_diameter": 0.0047244,
        "emissivity": 0.8,
        "solar_absorptivity": 0.8,
        "temperature1": 25,
        "temperature2": 75,
        "resistance_at_temperature1": 0.000437945,
        "resistance_at_temperature2": 0.000437945,
        "aluminium_cross_section_area": None,
        "constant_magnetic_effect": 1,
        "current_density_proportional_magnetic_effect": 0,
        "max_magnetic_core_relative_resistance_increase": 1,
    },
]


# Create towers for a span that faces east-west
start_tower = linerate.Tower(latitude=50 - 0.0045, longitude=0, altitude=500 - 88)
end_tower = linerate.Tower(latitude=50 + 0.0045, longitude=0, altitude=500 + 88)

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
Tmax_for_rating = 50.0  

for var_key, info in vars_info.items():
    lo, hi = info["bounds"]
    xs = np.linspace(lo, hi, n_points)
    
    plt.figure(figsize=(8, 5))
    for line in lines:
        conductor = linerate.Conductor(
            core_diameter=line["core_diameter"],
            conductor_diameter=line["conductor_diameter"],
            outer_layer_strand_diameter=line["outer_layer_strand_diameter"],
            emissivity=line["emissivity"],
            solar_absorptivity=line["solar_absorptivity"],
            temperature1=line["temperature1"],
            temperature2=line["temperature2"],
            resistance_at_temperature1=line["resistance_at_temperature1"],
            resistance_at_temperature2=line["resistance_at_temperature2"],
            aluminium_cross_section_area=line["aluminium_cross_section_area"] if line["aluminium_cross_section_area"] is not None else float("nan"),
            constant_magnetic_effect=line["constant_magnetic_effect"],
            current_density_proportional_magnetic_effect=line["current_density_proportional_magnetic_effect"],
            max_magnetic_core_relative_resistance_increase=line["max_magnetic_core_relative_resistance_increase"],
        )
        span = linerate.Span(conductor=conductor, start_tower=start_tower, end_tower=end_tower, num_conductors=1)
        amps_cigre = np.empty(n_points)
        for i, x in enumerate(xs): # i is the index, x is the variable value
            vals ={"air_temperature": vars_info["air_temperature"]["baseline"],
                   "wind_speed": vars_info["wind_speed"]["baseline"],
                   "wind_direction_deg": vars_info["wind_direction_deg"]["baseline"],
                   "clearness_ratio": vars_info["clearness_ratio"]["baseline"],
                   "ground_albedo": vars_info["ground_albedo"]["baseline"]
                   }
            vals[var_key] = x
            
            weather = linerate.Weather(
                air_temperature=vals["air_temperature"],
                wind_direction=np.radians(vals["wind_direction_deg"]),
                wind_speed=vals["wind_speed"],
                ground_albedo=vals["ground_albedo"],
                clearness_ratio=vals["clearness_ratio"], 
            )
            model_cigre = linerate.Cigre601(span, weather, time_of_measurement)
            try:
                amp_cigre = model_cigre.compute_steady_state_ampacity(np.array([Tmax_for_rating]))[0]
            except Exception as e:
                # solver failed for this point; record NaN and continue
                amp_cigre = np.nan
            amps_cigre[i] = amp_cigre
        # name the label using bothname and id
        label = f"{line['name']} (row: {line['id']})"
        plt.plot(xs, amps_cigre, label=label)

    plt.xlabel(info["label"])
    plt.ylabel("Ampacity (A)")
    plt.title(f"Ampacity vs {info['label']} — comparison of conductor types (CIGRE)")
    plt.grid(True)
    plt.legend(fontsize="small", loc="best")
    plt.tight_layout()
    plt.show()
