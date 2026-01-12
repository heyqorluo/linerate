import numpy as np
import linerate


conductor = linerate.Conductor(
    core_diameter=10.4e-3,
    conductor_diameter=31.2e-3,
    outer_layer_strand_diameter=10.4e-3,
    emissivity=0.9,
    solar_absorptivity=0.9,
    temperature1=25,
    temperature2=75,
    resistance_at_temperature1=5.167e-4,
    resistance_at_temperature2=8.688e-5,
    aluminium_cross_section_area=float("nan"),  # No core magnetisation loss
    constant_magnetic_effect=1,
    current_density_proportional_magnetic_effect=0,
    max_magnetic_core_relative_resistance_increase=1,
)


start_tower = linerate.Tower(latitude=50 - 0.0045, longitude=0, altitude=500 - 88)
end_tower = linerate.Tower(latitude=50 + 0.0045, longitude=0, altitude=500 + 88)
span = linerate.Span(
    conductor=conductor,
    start_tower=start_tower,
    end_tower=end_tower,
    num_conductors=1,
)


weather = linerate.Weather(
    air_temperature=9,
    wind_direction=np.radians(80),  # Conductor azimuth is 0, so angle of attack is 80
    wind_speed=0.5,
    ground_albedo=0,
    clearness_ratio=0.5,
)


time_of_measurement = np.datetime64("2016-10-03 14:00")
max_conductor_temperature = 50


model = linerate.Cigre601(span, weather, time_of_measurement)
conductor_rating = model.compute_steady_state_ampacity(max_conductor_temperature)
print(f"The span has a steady-state ampacity rating of {conductor_rating:.0f} A if the maximum temperature is {max_conductor_temperature} °C")
