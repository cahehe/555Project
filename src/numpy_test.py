
import numpy.matlib

# Actual location
ru = numpy.array([1.0, 0.6])

sat_0_location = numpy.array([0, 0]);
sat_1_location = numpy.array([1, 0]);
sat_2_location = numpy.array([1, 1]);

rho_0 = numpy.linalg.norm(sat_0_location - ru);
rho_1 = numpy.linalg.norm(sat_1_location - ru);
rho_2 = numpy.linalg.norm(sat_2_location - ru);

# Estimated location
ru_hat = numpy.array([0.1, 0.1])

for i in range(10):
    # Calculate distances from current estimate to satellite locations
    rho_0_hat = numpy.linalg.norm(sat_0_location - ru_hat);
    rho_1_hat = numpy.linalg.norm(sat_1_location - ru_hat);
    rho_2_hat = numpy.linalg.norm(sat_2_location - ru_hat);

    # Calculate unit vector in direction of satellite
    unit_0 = (sat_0_location - ru_hat)/rho_0_hat;
    unit_1 = (sat_1_location - ru_hat)/rho_1_hat;
    unit_2 = (sat_2_location - ru_hat)/rho_2_hat;

    # Set up linear equation for approximate adjustment
    delta_rho_vector = numpy.matrix([rho_0_hat - rho_0, rho_1_hat - rho_1, rho_2_hat - rho_2]).T;
    unit_vector_matrix = numpy.matrix([[unit_0[0], unit_0[1]], [unit_1[0], unit_1[1]], [unit_2[0], unit_2[1]]]);

    # Solve linear equation
    delta_ru_hat = numpy.linalg.inv(unit_vector_matrix.T*unit_vector_matrix)*unit_vector_matrix.T*delta_rho_vector

    # Apply adjustment
    ru_hat[0] += delta_ru_hat[0]
    ru_hat[1] += delta_ru_hat[1]

print(ru_hat - ru)

