import linerate
import numpy as np
import matplotlib.pyplot as plt

# change in altitude of the towers simoultaneously

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
    aluminium_cross_section_area=float("nan"),  # No core magnetisation loss
    constant_magnetic_effect=1,
    current_density_proportional_magnetic_effect=0,
    max_magnetic_core_relative_resistance_increase=1,
)

weather = linerate.Weather(
    air_temperature=20,
    wind_direction=np.radians(80),  # Conductor azimuth is 0, so angle of attack is 80
    wind_speed=1.66,
    ground_albedo=0.15,
    clearness_ratio=0.5, #max sky
)

time_of_measurement = np.datetime64("2016-10-03 14:00") #summer for max sun rad
max_conductor_temperature = 100

ampacities_CIGRE = []
ampacities_IEEE = []
altitudes = np.linspace (100,1000, 21)

for alt in altitudes:
    start_tower = linerate.Tower(latitude=50 - 0.0045, longitude=0, altitude=alt - 0)
    end_tower = linerate.Tower(latitude=50 + 0.0045, longitude=0, altitude=alt + 0)
    span = linerate.Span(
        conductor=conductor,
        start_tower=start_tower,
        end_tower=end_tower,
        num_conductors=1,
    )
    model_CIGRE = linerate.Cigre601(span, weather, time_of_measurement)
    conductor_rating_CIGRE = model_CIGRE.compute_steady_state_ampacity(max_conductor_temperature)
    model_IEEE = linerate.IEEE738(span, weather, time_of_measurement)
    conductor_rating_IEEE = model_IEEE.compute_steady_state_ampacity(max_conductor_temperature)
    ampacities_CIGRE.append(conductor_rating_CIGRE)
    ampacities_IEEE.append(conductor_rating_IEEE)

plt.figure(figsize=(8,5))
plt.plot(altitudes, ampacities_CIGRE, marker="o", label = "CIGRE")
plt.plot(altitudes, ampacities_IEEE, marker="x", label="IEEE")

plt.xlabel("altitude")
plt.ylabel("Steady-State Ampacity (A)")
plt.title("Sensitivity of Ampacity to altitude")
plt.grid(True)
plt.legend()  
plt.show()