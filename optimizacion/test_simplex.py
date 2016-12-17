from simplex import Simplex

objective = ('maximize', '40x_1 + 30x_2 + 38x_3 + 45x_4')
constraints = [
    '1x_1 <= 4',
    '1x_2 <= 3',
    '1x_3 <= 3',
    '1x_4 <= 4',
    '1x_1 + 1x_2 + 1x_3 + 1x_4 = 8'
]

# objective = ('minimize', '4x_1 + 1x_2')
# constraints = ['3x_1 + 1x_2 = 3', '4x_1 + 3x_2 >= 6', '1x_1 + 2x_2 <= 4']
# lp_system = Simplex(num_vars=2, constraints=constraints, objective_function=objective)

lp_system = Simplex(num_vars=4, constraints=constraints, objective_function=objective)

sol = lp_system.solution
print("Solution")
print(sol)

opt_val = lp_system.optimize_val

print("Optimize value")
print(opt_val)

