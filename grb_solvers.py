import classes_power as ODC
import numpy as np
import pandas as pd
import math

import gurobipy
from gurobipy import GRB

GEN_PRIORITY_KEY = {122: 1, 222: 1, 322: 1, 422: 1, 522: 1, 622: 1,
118: 2, 121: 2,
323: 3,
615: 4, 116: 4, 123: 4, 223: 4,
301: 5, 401: 5, 302: 5, 402: 5,
113: 6, 213: 6, 313: 6,
107: 7, 207: 7, 307: 7,
115: 8, 215: 8, 315: 8, 415: 8, 515: 8,
101: 9, 201: 9, 102: 9, 202: 9}

GEN_PRIORITY_COUNT = {1: 6, 2: 2, 3: 1, 4: 4, 5: 4, 6: 3, 7: 3, 8: 5, 9: 4}

NUMBER_OF_MINUTES = 10

# Unit commitment is a variable
def power_dispatch(object_load, object_generator, losses, exports):
	mx_dispatch = {1: 0., 2: 0., 3: 0., 4: 0., 5: 0., 6: 0., 7: 0., 8: 0., 9: 0.}
	mx_reserve = {1: 0., 2: 0., 3: 0., 4: 0., 5: 0., 6: 0., 7: 0., 8: 0., 9: 0.}
	dispatch_factor = {1: 0., 2: 0., 3: 0., 4: 0., 5: 0., 6: 0., 7: 0., 8: 0., 9: 0.}
	operational_status = {1: 0., 2: 0., 3: 0., 4: 0., 5: 0., 6: 0., 7: 0., 8: 0., 9: 0.}

	# Set "constants"
	for row in object_generator.matrix:
		mx_dispatch[GEN_PRIORITY_KEY[int(row[ODC.Generator.ID])]] += row[ODC.Generator.REAL_GENERATION_MAX_RATING]
		mx_reserve[GEN_PRIORITY_KEY[int(row[ODC.Generator.ID])]] += row[ODC.Generator.RAMP_RATE]
	SUM_LOAD = float(sum(object_load.matrix[:, ODC.Load.REAL_LOAD]))

	try:
		# Model
		m = gurobipy.Model('mip1')

		# Create variables
		gf_1 = m.addVar(lb=0.00, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_1') # TODO: fix these
		gf_2 = m.addVar(lb=0.25, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_2')
		gf_3 = m.addVar(lb=0.40, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_3')
		gf_4 = m.addVar(lb=0.35, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_4')
		gf_5 = m.addVar(lb=0.20, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_5')
		gf_6 = m.addVar(lb=0.35, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_6')
		gf_7 = m.addVar(lb=0.25, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_7')
		gf_8 = m.addVar(lb=0.20, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_8')
		gf_9 = m.addVar(lb=0.70, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_9')

		uc_1 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_1')
		uc_2 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_2')
		uc_3 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_3')
		uc_4 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_4')
		uc_5 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_5')
		uc_6 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_6')
		uc_7 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_7')
		uc_8 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_8')
		uc_9 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_9')

		ra_1 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_1')
		ra_2 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_2')
		ra_3 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_3')
		ra_4 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_4')
		ra_5 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_5')
		ra_6 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_6')
		ra_7 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_7')
		ra_8 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_8')
		ra_9 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_9')

		# Objective function that minimizes priority level of dispatch
		m.setObjective(1*uc_1*gf_1*mx_dispatch[1] + 2*uc_2*gf_1*mx_dispatch[2] + 3*uc_3*gf_1*mx_dispatch[3] + 4*uc_4*gf_1*mx_dispatch[4] + 5*uc_5*gf_1*mx_dispatch[5] + 6*uc_6*gf_1*mx_dispatch[6] + 7*uc_7*gf_1*mx_dispatch[7] + 8*uc_8*gf_1*mx_dispatch[8] + 9*uc_9*gf_1*mx_dispatch[9], GRB.MINIMIZE)

		# Constraint - Loads = Gen
		m.addConstr((SUM_LOAD+losses+exports) - 0.01 <= uc_1*gf_1*mx_dispatch[1] + uc_2*gf_2*mx_dispatch[2] + uc_3*gf_3*mx_dispatch[3] + uc_4*gf_4*mx_dispatch[4] + uc_5*gf_5*mx_dispatch[5] + uc_6*gf_6*mx_dispatch[6] + uc_7*gf_7*mx_dispatch[7] + uc_8*gf_8*mx_dispatch[8] + uc_9*gf_9*mx_dispatch[9], 'system_load_1')
		m.addConstr((SUM_LOAD+losses+exports) + 0.01 >= uc_1*gf_1*mx_dispatch[1] + uc_2*gf_2*mx_dispatch[2] + uc_3*gf_3*mx_dispatch[3] + uc_4*gf_4*mx_dispatch[4] + uc_5*gf_5*mx_dispatch[5] + uc_6*gf_6*mx_dispatch[6] + uc_7*gf_7*mx_dispatch[7] + uc_8*gf_8*mx_dispatch[8] + uc_9*gf_9*mx_dispatch[9], 'system_load_2')

		# Constraint - Minimum required reserve for CAISO
		m.addConstr(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9 >= uc_1*gf_1*mx_dispatch[1]*0.05 + (uc_2*gf_2*mx_dispatch[2] + uc_3*gf_3*mx_dispatch[3] + uc_4*gf_4*mx_dispatch[4] + uc_5*gf_5*mx_dispatch[5] + uc_6*gf_6*mx_dispatch[6] + uc_7*gf_7*mx_dispatch[7] + uc_8*gf_8*mx_dispatch[8] + uc_9*gf_9*mx_dispatch[9])*0.07, 'net_reserves')

		# Constraint - Minimum required reserve for largest unit
		m.addConstr(GEN_PRIORITY_COUNT[1]*(ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[1] - 1) * ra_1 >= uc_1*gf_1*mx_dispatch[1], 'reserve_req_1')
		m.addConstr(GEN_PRIORITY_COUNT[2]*(ra_1 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[2] - 1) * ra_2 >= uc_2*gf_2*mx_dispatch[2], 'reserve_req_2')
		m.addConstr(GEN_PRIORITY_COUNT[3]*(ra_1 + ra_2 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[3] - 1) * ra_3 >= uc_3*gf_3*mx_dispatch[3], 'reserve_req_3')
		m.addConstr(GEN_PRIORITY_COUNT[4]*(ra_1 + ra_2 + ra_3 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[4] - 1) * ra_4 >= uc_4*gf_4*mx_dispatch[4], 'reserve_req_4')
		m.addConstr(GEN_PRIORITY_COUNT[5]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_6 + ra_7 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[5] - 1) * ra_5 >= uc_5*gf_5*mx_dispatch[5], 'reserve_req_5')
		m.addConstr(GEN_PRIORITY_COUNT[6]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_7 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[6] - 1) * ra_6 >= uc_6*gf_6*mx_dispatch[6], 'reserve_req_6')
		m.addConstr(GEN_PRIORITY_COUNT[7]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[7] - 1) * ra_7 >= uc_7*gf_7*mx_dispatch[7], 'reserve_req_7')
		m.addConstr(GEN_PRIORITY_COUNT[8]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_9) + (GEN_PRIORITY_COUNT[8] - 1) * ra_8 >= uc_8*gf_8*mx_dispatch[8], 'reserve_req_8')
		m.addConstr(GEN_PRIORITY_COUNT[9]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8) + (GEN_PRIORITY_COUNT[9] - 1) * ra_9 >= uc_9*gf_9*mx_dispatch[9], 'reserve_req_9')

		# Constraint - Maximum available reserve
		m.addConstr(ra_1 <= uc_1 * (1.0 - gf_1) * mx_dispatch[1], 'reserve_avail_1_1')
		m.addConstr(ra_1 <= uc_1 * NUMBER_OF_MINUTES * mx_reserve[1], 'reserve_avail_1_2')
		m.addConstr(ra_2 <= uc_2 * (1.0 - gf_2) * mx_dispatch[2], 'reserve_avail_2_1')
		m.addConstr(ra_2 <= uc_2 * NUMBER_OF_MINUTES * mx_reserve[2], 'reserve_avail_2_2')
		m.addConstr(ra_3 <= uc_3 * (1.0 - gf_3) * mx_dispatch[3], 'reserve_avail_3_1')
		m.addConstr(ra_3 <= uc_3 * NUMBER_OF_MINUTES * mx_reserve[3], 'reserve_avail_3_2')
		m.addConstr(ra_4 <= uc_4 * (1.0 - gf_4) * mx_dispatch[4], 'reserve_avail_4_1')
		m.addConstr(ra_4 <= uc_4 * NUMBER_OF_MINUTES * mx_reserve[4], 'reserve_avail_4_2')
		m.addConstr(ra_5 <= uc_5 * (1.0 - gf_5) * mx_dispatch[5], 'reserve_avail_5_1')
		m.addConstr(ra_5 <= uc_5 * NUMBER_OF_MINUTES * mx_reserve[5], 'reserve_avail_5_2')
		m.addConstr(ra_6 <= uc_6 * (1.0 - gf_6) * mx_dispatch[6], 'reserve_avail_6_1')
		m.addConstr(ra_6 <= uc_6 * NUMBER_OF_MINUTES * mx_reserve[6], 'reserve_avail_6_2')
		m.addConstr(ra_7 <= uc_7 * (1.0 - gf_7) * mx_dispatch[7], 'reserve_avail_7_1')
		m.addConstr(ra_7 <= uc_7 * NUMBER_OF_MINUTES * mx_reserve[7], 'reserve_avail_7_2')
		m.addConstr(ra_8 <= uc_8 * (1.0 - gf_8) * mx_dispatch[8], 'reserve_avail_8_1')
		m.addConstr(ra_8 <= uc_8 * NUMBER_OF_MINUTES * mx_reserve[8], 'reserve_avail_8_2')
		m.addConstr(ra_9 <= (1.0 - gf_9) * mx_dispatch[9], 'reserve_avail_9_1')
		m.addConstr(ra_9 <= NUMBER_OF_MINUTES * mx_reserve[9], 'reserve_avail_9_2')

		# Solve
		m.params.outputFlag = 0
		m.optimize()

		for elem in m.getVars():
			if elem.varName == 'gf_1':
				dispatch_factor[1] = float(elem.x)
			elif elem.varName == 'gf_2':
				dispatch_factor[2] = float(elem.x)
			elif elem.varName == 'gf_3':
				dispatch_factor[3] = float(elem.x)
			elif elem.varName == 'gf_4':
				dispatch_factor[4] = float(elem.x)
			elif elem.varName == 'gf_5':
				dispatch_factor[5] = float(elem.x)
			elif elem.varName == 'gf_6':
				dispatch_factor[6] = float(elem.x)
			elif elem.varName == 'gf_7':
				dispatch_factor[7] = float(elem.x)
			elif elem.varName == 'gf_8':
				dispatch_factor[8] = float(elem.x)
			elif elem.varName == 'gf_9':
				dispatch_factor[9] = float(elem.x)
			elif elem.varName == 'uc_1':
				operational_status[1] = float(round(elem.x))
			elif elem.varName == 'uc_2':
				operational_status[2] = float(round(elem.x))
			elif elem.varName == 'uc_3':
				operational_status[3] = float(round(elem.x))
			elif elem.varName == 'uc_4':
				operational_status[4] = float(round(elem.x))
			elif elem.varName == 'uc_5':
				operational_status[5] = float(round(elem.x))
			elif elem.varName == 'uc_6':
				operational_status[6] = float(round(elem.x))
			elif elem.varName == 'uc_7':
				operational_status[7] = float(round(elem.x))
			elif elem.varName == 'uc_8':
				operational_status[8] = float(round(elem.x))
			elif elem.varName == 'uc_9':
				operational_status[9] = float(round(elem.x))

		for row in object_generator.matrix:
			row[ODC.Generator.REAL_GENERATION] = row[ODC.Generator.REAL_GENERATION_MAX_RATING] * dispatch_factor[GEN_PRIORITY_KEY[int(row[ODC.Generator.ID])]]
			row[ODC.Generator.OPERATIONAL_STATUS] = operational_status[GEN_PRIORITY_KEY[int(row[ODC.Generator.ID])]]
			row[ODC.Generator.REAL_GENERATION] = row[ODC.Generator.REAL_GENERATION] * row[ODC.Generator.OPERATIONAL_STATUS]
		
	except gurobipy.GurobiError:
		print('Gurobi error reported in power dispatch')

# Unit commitment is an input
def power_dispatch_2(object_load, object_generator, losses, exports):
	mx_dispatch = {1: 0., 2: 0., 3: 0., 4: 0., 5: 0., 6: 0., 7: 0., 8: 0., 9: 0.}
	mx_reserve = {1: 0., 2: 0., 3: 0., 4: 0., 5: 0., 6: 0., 7: 0., 8: 0., 9: 0.}
	dispatch_factor = {1: 0., 2: 0., 3: 0., 4: 0., 5: 0., 6: 0., 7: 0., 8: 0., 9: 0.}

	uc_1 = 0.0
	uc_2 = 0.0
	uc_3 = 0.0
	uc_4 = 0.0
	uc_5 = 0.0
	uc_6 = 0.0
	uc_7 = 0.0
	uc_8 = 0.0
	uc_9 = 0.0

	# Set "constants"
	for row in object_generator.matrix:
		mx_dispatch[GEN_PRIORITY_KEY[int(row[ODC.Generator.ID])]] += row[ODC.Generator.REAL_GENERATION_MAX_RATING]
		mx_reserve[GEN_PRIORITY_KEY[int(row[ODC.Generator.ID])]] += row[ODC.Generator.RAMP_RATE]
		if row[ODC.Generator.ID] == 122.0:
			uc_1 = row[ODC.Generator.OPERATIONAL_STATUS]
		elif row[ODC.Generator.ID] == 118.0:
			uc_2 = row[ODC.Generator.OPERATIONAL_STATUS]
		elif row[ODC.Generator.ID] == 323.0:
			uc_3 = row[ODC.Generator.OPERATIONAL_STATUS]
		elif row[ODC.Generator.ID] == 615.0:
			uc_4 = row[ODC.Generator.OPERATIONAL_STATUS]
		elif row[ODC.Generator.ID] == 301.0:
			uc_5 = row[ODC.Generator.OPERATIONAL_STATUS]
		elif row[ODC.Generator.ID] == 113.0:
			uc_6 = row[ODC.Generator.OPERATIONAL_STATUS]
		elif row[ODC.Generator.ID] == 107.0:
			uc_7 = row[ODC.Generator.OPERATIONAL_STATUS]
		elif row[ODC.Generator.ID] == 115.0:
			uc_8 = row[ODC.Generator.OPERATIONAL_STATUS]
		elif row[ODC.Generator.ID] == 101.0:
			uc_9 = row[ODC.Generator.OPERATIONAL_STATUS]
	SUM_LOAD = float(sum(object_load.matrix[:, ODC.Load.REAL_LOAD]))

	try:
		# Model
		m = gurobipy.Model('mip1')

		# Create variables
		gf_1 = m.addVar(lb=0.00, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_1') # TODO: fix these
		gf_2 = m.addVar(lb=0.25, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_2')
		gf_3 = m.addVar(lb=0.40, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_3')
		gf_4 = m.addVar(lb=0.35, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_4')
		gf_5 = m.addVar(lb=0.20, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_5')
		gf_6 = m.addVar(lb=0.35, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_6')
		gf_7 = m.addVar(lb=0.25, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_7')
		gf_8 = m.addVar(lb=0.20, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_8')
		gf_9 = m.addVar(lb=0.70, ub=1.0, vtype=GRB.CONTINUOUS, name='gf_9')

		ra_1 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_1')
		ra_2 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_2')
		ra_3 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_3')
		ra_4 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_4')
		ra_5 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_5')
		ra_6 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_6')
		ra_7 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_7')
		ra_8 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_8')
		ra_9 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='ra_9')

		# Objective function that minimizes priority level of dispatch
		m.setObjective(1*uc_1*gf_1*mx_dispatch[1] + 2*uc_2*gf_1*mx_dispatch[2] + 3*uc_3*gf_1*mx_dispatch[3] + 4*uc_4*gf_1*mx_dispatch[4] + 5*uc_5*gf_1*mx_dispatch[5] + 6*uc_6*gf_1*mx_dispatch[6] + 7*uc_7*gf_1*mx_dispatch[7] + 8*uc_8*gf_1*mx_dispatch[8] + 9*uc_9*gf_1*mx_dispatch[9], GRB.MINIMIZE)

		# Constraint - Loads = Gen
		m.addConstr((SUM_LOAD+losses+exports) - 0.01 <= uc_1*gf_1*mx_dispatch[1] + uc_2*gf_2*mx_dispatch[2] + uc_3*gf_3*mx_dispatch[3] + uc_4*gf_4*mx_dispatch[4] + uc_5*gf_5*mx_dispatch[5] + uc_6*gf_6*mx_dispatch[6] + uc_7*gf_7*mx_dispatch[7] + uc_8*gf_8*mx_dispatch[8] + uc_9*gf_9*mx_dispatch[9], 'system_load_1')
		m.addConstr((SUM_LOAD+losses+exports) + 0.01 >= uc_1*gf_1*mx_dispatch[1] + uc_2*gf_2*mx_dispatch[2] + uc_3*gf_3*mx_dispatch[3] + uc_4*gf_4*mx_dispatch[4] + uc_5*gf_5*mx_dispatch[5] + uc_6*gf_6*mx_dispatch[6] + uc_7*gf_7*mx_dispatch[7] + uc_8*gf_8*mx_dispatch[8] + uc_9*gf_9*mx_dispatch[9], 'system_load_2')

		# Constraint - Minimum required reserve for CAISO
		m.addConstr(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9 >= uc_1*gf_1*mx_dispatch[1]*0.05 + (uc_2*gf_2*mx_dispatch[2] + uc_3*gf_3*mx_dispatch[3] + uc_4*gf_4*mx_dispatch[4] + uc_5*gf_5*mx_dispatch[5] + uc_6*gf_6*mx_dispatch[6] + uc_7*gf_7*mx_dispatch[7] + uc_8*gf_8*mx_dispatch[8] + uc_9*gf_9*mx_dispatch[9])*0.07, 'net_reserves')

		# Constraint - Minimum required reserve for largest unit
		m.addConstr(GEN_PRIORITY_COUNT[1]*(ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[1] - 1) * ra_1 >= uc_1*gf_1*mx_dispatch[1], 'reserve_req_1')
		m.addConstr(GEN_PRIORITY_COUNT[2]*(ra_1 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[2] - 1) * ra_2 >= uc_2*gf_2*mx_dispatch[2], 'reserve_req_2')
		m.addConstr(GEN_PRIORITY_COUNT[3]*(ra_1 + ra_2 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[3] - 1) * ra_3 >= uc_3*gf_3*mx_dispatch[3], 'reserve_req_3')
		m.addConstr(GEN_PRIORITY_COUNT[4]*(ra_1 + ra_2 + ra_3 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[4] - 1) * ra_4 >= uc_4*gf_4*mx_dispatch[4], 'reserve_req_4')
		m.addConstr(GEN_PRIORITY_COUNT[5]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_6 + ra_7 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[5] - 1) * ra_5 >= uc_5*gf_5*mx_dispatch[5], 'reserve_req_5')
		m.addConstr(GEN_PRIORITY_COUNT[6]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_7 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[6] - 1) * ra_6 >= uc_6*gf_6*mx_dispatch[6], 'reserve_req_6')
		m.addConstr(GEN_PRIORITY_COUNT[7]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_8 + ra_9) + (GEN_PRIORITY_COUNT[7] - 1) * ra_7 >= uc_7*gf_7*mx_dispatch[7], 'reserve_req_7')
		m.addConstr(GEN_PRIORITY_COUNT[8]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_9) + (GEN_PRIORITY_COUNT[8] - 1) * ra_8 >= uc_8*gf_8*mx_dispatch[8], 'reserve_req_8')
		m.addConstr(GEN_PRIORITY_COUNT[9]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8) + (GEN_PRIORITY_COUNT[9] - 1) * ra_9 >= uc_9*gf_9*mx_dispatch[9], 'reserve_req_9')

		# Constraint - Maximum available reserve
		m.addConstr(ra_1 <= uc_1 * (1.0 - gf_1) * mx_dispatch[1], 'reserve_avail_1_1')
		m.addConstr(ra_1 <= uc_1 * NUMBER_OF_MINUTES * mx_reserve[1], 'reserve_avail_1_2')
		m.addConstr(ra_2 <= uc_2 * (1.0 - gf_2) * mx_dispatch[2], 'reserve_avail_2_1')
		m.addConstr(ra_2 <= uc_2 * NUMBER_OF_MINUTES * mx_reserve[2], 'reserve_avail_2_2')
		m.addConstr(ra_3 <= uc_3 * (1.0 - gf_3) * mx_dispatch[3], 'reserve_avail_3_1')
		m.addConstr(ra_3 <= uc_3 * NUMBER_OF_MINUTES * mx_reserve[3], 'reserve_avail_3_2')
		m.addConstr(ra_4 <= uc_4 * (1.0 - gf_4) * mx_dispatch[4], 'reserve_avail_4_1')
		m.addConstr(ra_4 <= uc_4 * NUMBER_OF_MINUTES * mx_reserve[4], 'reserve_avail_4_2')
		m.addConstr(ra_5 <= uc_5 * (1.0 - gf_5) * mx_dispatch[5], 'reserve_avail_5_1')
		m.addConstr(ra_5 <= uc_5 * NUMBER_OF_MINUTES * mx_reserve[5], 'reserve_avail_5_2')
		m.addConstr(ra_6 <= uc_6 * (1.0 - gf_6) * mx_dispatch[6], 'reserve_avail_6_1')
		m.addConstr(ra_6 <= uc_6 * NUMBER_OF_MINUTES * mx_reserve[6], 'reserve_avail_6_2')
		m.addConstr(ra_7 <= uc_7 * (1.0 - gf_7) * mx_dispatch[7], 'reserve_avail_7_1')
		m.addConstr(ra_7 <= uc_7 * NUMBER_OF_MINUTES * mx_reserve[7], 'reserve_avail_7_2')
		m.addConstr(ra_8 <= uc_8 * (1.0 - gf_8) * mx_dispatch[8], 'reserve_avail_8_1')
		m.addConstr(ra_8 <= uc_8 * NUMBER_OF_MINUTES * mx_reserve[8], 'reserve_avail_8_2')
		m.addConstr(ra_9 <= (1.0 - gf_9) * mx_dispatch[9], 'reserve_avail_9_1')
		m.addConstr(ra_9 <= NUMBER_OF_MINUTES * mx_reserve[9], 'reserve_avail_9_2')

		# Solve
		m.params.outputFlag = 0
		m.optimize()

		for elem in m.getVars():
			if elem.varName == 'gf_1':
				dispatch_factor[1] = float(elem.x)
			elif elem.varName == 'gf_2':
				dispatch_factor[2] = float(elem.x)
			elif elem.varName == 'gf_3':
				dispatch_factor[3] = float(elem.x)
			elif elem.varName == 'gf_4':
				dispatch_factor[4] = float(elem.x)
			elif elem.varName == 'gf_5':
				dispatch_factor[5] = float(elem.x)
			elif elem.varName == 'gf_6':
				dispatch_factor[6] = float(elem.x)
			elif elem.varName == 'gf_7':
				dispatch_factor[7] = float(elem.x)
			elif elem.varName == 'gf_8':
				dispatch_factor[8] = float(elem.x)
			elif elem.varName == 'gf_9':
				dispatch_factor[9] = float(elem.x)

		for row in object_generator.matrix:
			row[ODC.Generator.REAL_GENERATION] = row[ODC.Generator.REAL_GENERATION_MAX_RATING] * dispatch_factor[GEN_PRIORITY_KEY[int(row[ODC.Generator.ID])]]
			row[ODC.Generator.REAL_GENERATION] = row[ODC.Generator.REAL_GENERATION] * row[ODC.Generator.OPERATIONAL_STATUS]

	except gurobipy.GurobiError:
		print('Gurobi error reported in power dispatch')

def contingency_response(object_load, object_generator, object_cable, losses, exports):

	unit_recommit = {101: 0., 201: 0., 102: 0., 202: 0.}
	unit_response = {101: 0., 201: 0., 301: 0., 401: 0., 102: 0., 202: 0., 302: 0., 402: 0., 107: 0., 207: 0., 307: 0., 113: 0., 213: 0., 313: 0., 115: 0., 215: 0., 315: 0., 415: 0., 515: 0., 615: 0., 116: 0., 118: 0., 121: 0., 122: 0., 222: 0., 322: 0., 422: 0., 522: 0., 622: 0., 123: 0., 223: 0., 323: 0}

	ptdf_tab = pd.DataFrame.from_csv('C://Users//sk8er//Documents//git//RISE-power-water-ss-1phase//tables//ptdf.csv', header=0, index_col=0)
	lodf_tab = pd.DataFrame.from_csv('C://Users//sk8er//Documents//git//RISE-power-water-ss-1phase//tables//lodf.csv', header=0, index_col=0)

	uc_g = {}
	r_g = {}
	P_g = {}
	P_g_min = {}
	P_g_max = {}
	for row in object_generator.matrix:
		if row[ODC.Generator.OPERATIONAL_STATUS] == 0.0:
			row[ODC.Generator.REAL_GENERATION] = 0.0
		uc_g[int(row[ODC.Generator.ID])] = row[ODC.Generator.OPERATIONAL_STATUS] * row[ODC.Generator.FUNCTIONAL_STATUS]
		r_g[int(row[ODC.Generator.ID])] = row[ODC.Generator.RAMP_RATE]
		P_g[int(row[ODC.Generator.ID])] = row[ODC.Generator.REAL_GENERATION]
		P_g_min[int(row[ODC.Generator.ID])] = row[ODC.Generator.REAL_GENERATION_MIN_RATING]
		P_g_max[int(row[ODC.Generator.ID])] = row[ODC.Generator.REAL_GENERATION_MAX_RATING]

	outage_id = -1
	outage_count = 0
	outage_sign = 0

	P_b = {}
	P_b_min = {}
	P_b_max = {}
	for row in object_cable.matrix:
		P_b[int(row[ODC.Cable.ID])] = 0.5 * (row[ODC.Cable.REAL_POWER_2] - row[ODC.Cable.REAL_POWER_1])
		P_b_min[int(row[ODC.Cable.ID])] = - row[ODC.Cable.NORMAL_RATING] * row[ODC.Cable.MAX_PU_CAPACITY]
		P_b_max[int(row[ODC.Cable.ID])] = row[ODC.Cable.NORMAL_RATING] * row[ODC.Cable.MAX_PU_CAPACITY]
		if row[ODC.Cable.OPERATIONAL_STATUS_A] == 0.0:
			outage_id = int(row[ODC.Cable.ID])
			outage_sign = -lodf_tab.loc[outage_id][str(outage_id)]
			outage_count += 1
	if outage_id == -1:
		outage_id = 1
	if outage_count > 1:
		print('grb_solvers.py Error: More than one line outage!')


	SUM_LOAD = float(sum(object_load.matrix[:, ODC.Load.REAL_LOAD]))

	try:
		m = gurobipy.Model('mip1')
		
		slack = 0.1 # kW # slack = m.addVar(lb=0.0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='slack')

		mint = m.addVar(lb=0.0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='mint') #minutes

		uc_101 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_101') # combustion turbine with fast start capability
		uc_201 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_201') # combustion turbine with fast start capability
		uc_102 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_102') # combustion turbine with fast start capability
		uc_202 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_202') # combustion turbine with fast start capability

		r_101 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_101') # combustion turbine with fast start capability
		r_201 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_201') # combustion turbine with fast start capability
		r_301 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_301')
		r_401 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_401')
		r_102 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_102') # combustion turbine with fast start capability
		r_202 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_202') # combustion turbine with fast start capability
		r_302 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_302')
		r_402 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_402')
		r_107 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_107')
		r_207 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_207')
		r_307 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_307')
		r_113 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_113')
		r_213 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_213')
		r_313 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_313')
		r_115 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_115')
		r_215 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_215')
		r_315 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_315')
		r_415 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_415')
		r_515 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_515')
		r_615 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_615')
		r_116 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_116')
		r_118 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_118')
		r_121 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_121')
		r_122 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_122')
		r_222 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_222')
		r_322 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_322')
		r_422 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_422')
		r_522 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_522')
		r_622 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_622')
		r_123 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_123')
		r_223 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_223')
		r_323 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='r_323')

		# Objective function
		m.setObjective(mint, GRB.MINIMIZE)

		# Zero out imports/exports
		m.addConstr(-slack <= P_b[100] + uc_101*r_101*(ptdf_tab.loc[101]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[323][str(outage_id)]))

		m.addConstr(slack >= P_b[100] + uc_101*r_101*(ptdf_tab.loc[101]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[323][str(outage_id)]))


		# Re-dispatch must be greater than 10-minutes of ramping down *************************************************************
		m.addConstr(r_101 >= uc_101 * (mint * -r_g[101]))
		m.addConstr(r_201 >= uc_201 * (mint * -r_g[201]))
		m.addConstr(r_301 >= uc_g[301] * (mint * -r_g[301]))
		m.addConstr(r_401 >= uc_g[401] * (mint * -r_g[401]))
		m.addConstr(r_102 >= uc_102 * (mint * -r_g[102]))
		m.addConstr(r_202 >= uc_202 * (mint * -r_g[202]))
		m.addConstr(r_302 >= uc_g[302] * (mint * -r_g[302]))
		m.addConstr(r_402 >= uc_g[402] * (mint * -r_g[402]))
		m.addConstr(r_107 >= uc_g[107] * (mint * -r_g[107]))
		m.addConstr(r_207 >= uc_g[207] * (mint * -r_g[207]))
		m.addConstr(r_307 >= uc_g[307] * (mint * -r_g[307]))
		m.addConstr(r_113 >= uc_g[113] * (mint * -r_g[113]))
		m.addConstr(r_213 >= uc_g[213] * (mint * -r_g[213]))
		m.addConstr(r_313 >= uc_g[313] * (mint * -r_g[313]))
		m.addConstr(r_115 >= uc_g[115] * (mint * -r_g[115]))
		m.addConstr(r_215 >= uc_g[215] * (mint * -r_g[215]))
		m.addConstr(r_315 >= uc_g[315] * (mint * -r_g[315]))
		m.addConstr(r_415 >= uc_g[415] * (mint * -r_g[415]))
		m.addConstr(r_515 >= uc_g[515] * (mint * -r_g[515]))
		m.addConstr(r_615 >= uc_g[615] * (mint * -r_g[615]))
		m.addConstr(r_116 >= uc_g[116] * (mint * -r_g[116]))
		m.addConstr(r_118 >= uc_g[118] * (mint * -r_g[118]))
		m.addConstr(r_121 >= uc_g[121] * (mint * -r_g[121]))
		m.addConstr(r_122 >= uc_g[122] * (mint * -r_g[122]))
		m.addConstr(r_222 >= uc_g[222] * (mint * -r_g[222]))
		m.addConstr(r_322 >= uc_g[322] * (mint * -r_g[322]))
		m.addConstr(r_422 >= uc_g[422] * (mint * -r_g[422]))
		m.addConstr(r_522 >= uc_g[522] * (mint * -r_g[522]))
		m.addConstr(r_622 >= uc_g[622] * (mint * -r_g[622]))
		m.addConstr(r_123 >= uc_g[123] * (mint * -r_g[123]))
		m.addConstr(r_223 >= uc_g[223] * (mint * -r_g[223]))
		m.addConstr(r_323 >= uc_g[323] * (mint * -r_g[323]))

		# # Re-dispatch must be less than 10-minutes of ramping up ******************************************************************
		m.addConstr(r_101 <= uc_101 * (mint * r_g[101]))
		m.addConstr(r_201 <= uc_201 * (mint * r_g[201]))
		m.addConstr(r_301 <= uc_g[301] * (mint * r_g[301]))
		m.addConstr(r_401 <= uc_g[401] * (mint * r_g[401]))
		m.addConstr(r_102 <= uc_102 * (mint * r_g[102]))
		m.addConstr(r_202 <= uc_202 * (mint * r_g[202]))
		m.addConstr(r_302 <= uc_g[302] * (mint * r_g[302]))
		m.addConstr(r_402 <= uc_g[402] * (mint * r_g[402]))
		m.addConstr(r_107 <= uc_g[107] * (mint * r_g[107]))
		m.addConstr(r_207 <= uc_g[207] * (mint * r_g[207]))
		m.addConstr(r_307 <= uc_g[307] * (mint * r_g[307]))
		m.addConstr(r_113 <= uc_g[113] * (mint * r_g[113]))
		m.addConstr(r_213 <= uc_g[213] * (mint * r_g[213]))
		m.addConstr(r_313 <= uc_g[313] * (mint * r_g[313]))
		m.addConstr(r_115 <= uc_g[115] * (mint * r_g[115]))
		m.addConstr(r_215 <= uc_g[215] * (mint * r_g[215]))
		m.addConstr(r_315 <= uc_g[315] * (mint * r_g[315]))
		m.addConstr(r_415 <= uc_g[415] * (mint * r_g[415]))
		m.addConstr(r_515 <= uc_g[515] * (mint * r_g[515]))
		m.addConstr(r_615 <= uc_g[615] * (mint * r_g[615]))
		m.addConstr(r_116 <= uc_g[116] * (mint * r_g[116]))
		m.addConstr(r_118 <= uc_g[118] * (mint * r_g[118]))
		m.addConstr(r_121 <= uc_g[121] * (mint * r_g[121]))
		m.addConstr(r_122 <= uc_g[122] * (mint * r_g[122]))
		m.addConstr(r_222 <= uc_g[222] * (mint * r_g[222]))
		m.addConstr(r_322 <= uc_g[322] * (mint * r_g[322]))
		m.addConstr(r_422 <= uc_g[422] * (mint * r_g[422]))
		m.addConstr(r_522 <= uc_g[522] * (mint * r_g[522]))
		m.addConstr(r_622 <= uc_g[622] * (mint * r_g[622]))
		m.addConstr(r_123 <= uc_g[123] * (mint * r_g[123]))
		m.addConstr(r_223 <= uc_g[223] * (mint * r_g[223]))
		m.addConstr(r_323 <= uc_g[323] * (mint * r_g[323]))

		# # Re-dispatch must be greater than minimum generation *********************************************************************
		m.addConstr(P_g[101] + r_101 >= P_g_min[101])
		m.addConstr(P_g[201] + r_201 >= P_g_min[201])
		m.addConstr(uc_g[301]*P_g[301] + r_301 >= uc_g[301]*P_g_min[301])
		m.addConstr(uc_g[401]*P_g[401] + r_401 >= uc_g[401]*P_g_min[401])
		m.addConstr(P_g[102] + r_102 >= P_g_min[102])
		m.addConstr(P_g[202] + r_202 >= P_g_min[202])
		m.addConstr(uc_g[302]*P_g[302] + r_302 >= uc_g[302]*P_g_min[302])
		m.addConstr(uc_g[402]*P_g[402] + r_402 >= uc_g[402]*P_g_min[402])
		m.addConstr(uc_g[107]*P_g[107] + r_107 >= uc_g[107]*P_g_min[107])
		m.addConstr(uc_g[207]*P_g[207] + r_207 >= uc_g[207]*P_g_min[207])
		m.addConstr(uc_g[307]*P_g[307] + r_307 >= uc_g[307]*P_g_min[307])
		m.addConstr(uc_g[113]*P_g[113] + r_113 >= uc_g[113]*P_g_min[113])
		m.addConstr(uc_g[213]*P_g[213] + r_213 >= uc_g[213]*P_g_min[213])
		m.addConstr(uc_g[313]*P_g[313] + r_313 >= uc_g[313]*P_g_min[313])
		m.addConstr(uc_g[115]*P_g[115] + r_115 >= uc_g[115]*P_g_min[115])
		m.addConstr(uc_g[215]*P_g[215] + r_215 >= uc_g[215]*P_g_min[215])
		m.addConstr(uc_g[315]*P_g[315] + r_315 >= uc_g[315]*P_g_min[315])
		m.addConstr(uc_g[415]*P_g[415] + r_415 >= uc_g[415]*P_g_min[415])
		m.addConstr(uc_g[515]*P_g[515] + r_515 >= uc_g[515]*P_g_min[515])
		m.addConstr(uc_g[615]*P_g[615] + r_615 >= uc_g[615]*P_g_min[615])
		m.addConstr(uc_g[116]*P_g[116] + r_116 >= uc_g[116]*P_g_min[116])
		m.addConstr(uc_g[118]*P_g[118] + r_118 >= uc_g[118]*P_g_min[118])
		m.addConstr(uc_g[121]*P_g[121] + r_121 >= uc_g[121]*P_g_min[121])
		m.addConstr(uc_g[122]*P_g[122] + r_122 >= uc_g[122]*P_g_min[122])
		m.addConstr(uc_g[222]*P_g[222] + r_222 >= uc_g[222]*P_g_min[222])
		m.addConstr(uc_g[322]*P_g[322] + r_322 >= uc_g[322]*P_g_min[322])
		m.addConstr(uc_g[422]*P_g[422] + r_422 >= uc_g[422]*P_g_min[422])
		m.addConstr(uc_g[522]*P_g[522] + r_522 >= uc_g[522]*P_g_min[522])
		m.addConstr(uc_g[622]*P_g[622] + r_622 >= uc_g[622]*P_g_min[622])
		m.addConstr(uc_g[123]*P_g[123] + r_123 >= uc_g[123]*P_g_min[123])
		m.addConstr(uc_g[223]*P_g[223] + r_223 >= uc_g[223]*P_g_min[223])
		m.addConstr(uc_g[323]*P_g[323] + r_323 >= uc_g[323]*P_g_min[323])

		# # # Re-dispatch must be less than maximum generation ************************************************************************
		m.addConstr(P_g[101] + r_101 <= P_g_max[101])
		m.addConstr(P_g[201] + r_201 <= P_g_max[201])
		m.addConstr(uc_g[301]*P_g[301] + r_301 <= uc_g[301]*P_g_max[301])
		m.addConstr(uc_g[401]*P_g[401] + r_401 <= uc_g[401]*P_g_max[401])
		m.addConstr(P_g[102] + r_102 <= P_g_max[102])
		m.addConstr(P_g[202] + r_202 <= P_g_max[202])
		m.addConstr(uc_g[302]*P_g[302] + r_302 <= uc_g[302]*P_g_max[302])
		m.addConstr(uc_g[402]*P_g[402] + r_402 <= uc_g[402]*P_g_max[402])
		m.addConstr(uc_g[107]*P_g[107] + r_107 <= uc_g[107]*P_g_max[107])
		m.addConstr(uc_g[207]*P_g[207] + r_207 <= uc_g[207]*P_g_max[207])
		m.addConstr(uc_g[307]*P_g[307] + r_307 <= uc_g[307]*P_g_max[307])
		m.addConstr(uc_g[113]*P_g[113] + r_113 <= uc_g[113]*P_g_max[113])
		m.addConstr(uc_g[213]*P_g[213] + r_213 <= uc_g[213]*P_g_max[213])
		m.addConstr(uc_g[313]*P_g[313] + r_313 <= uc_g[313]*P_g_max[313])
		m.addConstr(uc_g[115]*P_g[115] + r_115 <= uc_g[115]*P_g_max[115])
		m.addConstr(uc_g[215]*P_g[215] + r_215 <= uc_g[215]*P_g_max[215])
		m.addConstr(uc_g[315]*P_g[315] + r_315 <= uc_g[315]*P_g_max[315])
		m.addConstr(uc_g[415]*P_g[415] + r_415 <= uc_g[415]*P_g_max[415])
		m.addConstr(uc_g[515]*P_g[515] + r_515 <= uc_g[515]*P_g_max[515])
		m.addConstr(uc_g[615]*P_g[615] + r_615 <= uc_g[615]*P_g_max[615])
		m.addConstr(uc_g[116]*P_g[116] + r_116 <= uc_g[116]*P_g_max[116])
		m.addConstr(uc_g[118]*P_g[118] + r_118 <= uc_g[118]*P_g_max[118])
		m.addConstr(uc_g[121]*P_g[121] + r_121 <= uc_g[121]*P_g_max[121])
		m.addConstr(uc_g[122]*P_g[122] + r_122 <= uc_g[122]*P_g_max[122])
		m.addConstr(uc_g[222]*P_g[222] + r_222 <= uc_g[222]*P_g_max[222])
		m.addConstr(uc_g[322]*P_g[322] + r_322 <= uc_g[322]*P_g_max[322])
		m.addConstr(uc_g[422]*P_g[422] + r_422 <= uc_g[422]*P_g_max[422])
		m.addConstr(uc_g[522]*P_g[522] + r_522 <= uc_g[522]*P_g_max[522])
		m.addConstr(uc_g[622]*P_g[622] + r_622 <= uc_g[622]*P_g_max[622])
		m.addConstr(uc_g[123]*P_g[123] + r_123 <= uc_g[123]*P_g_max[123])
		m.addConstr(uc_g[223]*P_g[223] + r_223 <= uc_g[223]*P_g_max[223])
		m.addConstr(uc_g[323]*P_g[323] + r_323 <= uc_g[323]*P_g_max[323])

		# Branches must be less than maximum thermal limit ************************************************************************
		m.addConstr(P_b[1] + uc_101*r_101*(ptdf_tab.loc[101]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[1])

		m.addConstr(P_b[2] + uc_101*r_101*(ptdf_tab.loc[101]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[2])

		m.addConstr(P_b[3] + uc_101*r_101*(ptdf_tab.loc[101]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[3])

		m.addConstr(P_b[4] + uc_101*r_101*(ptdf_tab.loc[101]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[4])

		m.addConstr(P_b[5] + uc_101*r_101*(ptdf_tab.loc[101]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[5])

		m.addConstr(P_b[6] + uc_101*r_101*(ptdf_tab.loc[101]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[6])

		m.addConstr(P_b[7] + uc_101*r_101*(ptdf_tab.loc[101]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[7])

		m.addConstr(P_b[8] + uc_101*r_101*(ptdf_tab.loc[101]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[8])

		m.addConstr(P_b[9] + uc_101*r_101*(ptdf_tab.loc[101]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[9])

		m.addConstr(P_b[10] + uc_101*r_101*(ptdf_tab.loc[101]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[10])

		m.addConstr(P_b[11] + uc_101*r_101*(ptdf_tab.loc[101]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[11])

		m.addConstr(P_b[12] + uc_101*r_101*(ptdf_tab.loc[101]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[12])

		m.addConstr(P_b[13] + uc_101*r_101*(ptdf_tab.loc[101]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[13])

		m.addConstr(P_b[14] + uc_101*r_101*(ptdf_tab.loc[101]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[14])
	
		m.addConstr(P_b[15] + uc_101*r_101*(ptdf_tab.loc[101]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[15])
	
		m.addConstr(P_b[16] + uc_101*r_101*(ptdf_tab.loc[101]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[16])
	
		m.addConstr(P_b[17] + uc_101*r_101*(ptdf_tab.loc[101]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[17])
	
		m.addConstr(P_b[18] + uc_101*r_101*(ptdf_tab.loc[101]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[18])
	
		m.addConstr(P_b[19] + uc_101*r_101*(ptdf_tab.loc[101]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[19])
	
		m.addConstr(P_b[20] + uc_101*r_101*(ptdf_tab.loc[101]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[20])
	
		m.addConstr(P_b[21] + uc_101*r_101*(ptdf_tab.loc[101]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[21])
	
		m.addConstr(P_b[22] + uc_101*r_101*(ptdf_tab.loc[101]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[22])
	
		m.addConstr(P_b[23] + uc_101*r_101*(ptdf_tab.loc[101]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[23])
	
		m.addConstr(P_b[24] + uc_101*r_101*(ptdf_tab.loc[101]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[24])
	
		m.addConstr(P_b[25] + uc_101*r_101*(ptdf_tab.loc[101]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[25])
	
		m.addConstr(P_b[26] + uc_101*r_101*(ptdf_tab.loc[101]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[26])
	
		m.addConstr(P_b[27] + uc_101*r_101*(ptdf_tab.loc[101]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[27])
	
		m.addConstr(P_b[28] + uc_101*r_101*(ptdf_tab.loc[101]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[28])
	
		m.addConstr(P_b[29] + uc_101*r_101*(ptdf_tab.loc[101]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[29])
	
		m.addConstr(P_b[30] + uc_101*r_101*(ptdf_tab.loc[101]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[30])
	
		m.addConstr(P_b[31] + uc_101*r_101*(ptdf_tab.loc[101]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[31])
	
		m.addConstr(P_b[32] + uc_101*r_101*(ptdf_tab.loc[101]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[32])
	
		m.addConstr(P_b[33] + uc_101*r_101*(ptdf_tab.loc[101]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[33])

		# # Branches must be greater than minimum thermal limit *********************************************************************
		m.addConstr(P_b[1] + uc_101*r_101*(ptdf_tab.loc[101]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[1])

		m.addConstr(P_b[2] + uc_101*r_101*(ptdf_tab.loc[101]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[2])

		m.addConstr(P_b[3] + uc_101*r_101*(ptdf_tab.loc[101]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[3])

		m.addConstr(P_b[4] + uc_101*r_101*(ptdf_tab.loc[101]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[4])

		m.addConstr(P_b[5] + uc_101*r_101*(ptdf_tab.loc[101]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[5])

		m.addConstr(P_b[6] + uc_101*r_101*(ptdf_tab.loc[101]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[6])

		m.addConstr(P_b[7] + uc_101*r_101*(ptdf_tab.loc[101]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[7])

		m.addConstr(P_b[8] + uc_101*r_101*(ptdf_tab.loc[101]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[8])

		m.addConstr(P_b[9] + uc_101*r_101*(ptdf_tab.loc[101]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[9])

		m.addConstr(P_b[10] + uc_101*r_101*(ptdf_tab.loc[101]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[10])

		m.addConstr(P_b[11] + uc_101*r_101*(ptdf_tab.loc[101]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[11])

		m.addConstr(P_b[12] + uc_101*r_101*(ptdf_tab.loc[101]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[12])

		m.addConstr(P_b[13] + uc_101*r_101*(ptdf_tab.loc[101]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[13])

		m.addConstr(P_b[14] + uc_101*r_101*(ptdf_tab.loc[101]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[14])
	
		m.addConstr(P_b[15] + uc_101*r_101*(ptdf_tab.loc[101]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[15])
	
		m.addConstr(P_b[16] + uc_101*r_101*(ptdf_tab.loc[101]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[16])
	
		m.addConstr(P_b[17] + uc_101*r_101*(ptdf_tab.loc[101]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[17])
	
		m.addConstr(P_b[18] + uc_101*r_101*(ptdf_tab.loc[101]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[18])
	
		m.addConstr(P_b[19] + uc_101*r_101*(ptdf_tab.loc[101]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[19])
	
		m.addConstr(P_b[20] + uc_101*r_101*(ptdf_tab.loc[101]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[20])
	
		m.addConstr(P_b[21] + uc_101*r_101*(ptdf_tab.loc[101]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[21])
	
		m.addConstr(P_b[22] + uc_101*r_101*(ptdf_tab.loc[101]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[22])
	
		m.addConstr(P_b[23] + uc_101*r_101*(ptdf_tab.loc[101]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[23])
	
		m.addConstr(P_b[24] + uc_101*r_101*(ptdf_tab.loc[101]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[24])
	
		m.addConstr(P_b[25] + uc_101*r_101*(ptdf_tab.loc[101]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[25])
	
		m.addConstr(P_b[26] + uc_101*r_101*(ptdf_tab.loc[101]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[26])
	
		m.addConstr(P_b[27] + uc_101*r_101*(ptdf_tab.loc[101]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[27])
	
		m.addConstr(P_b[28] + uc_101*r_101*(ptdf_tab.loc[101]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[28])
	
		m.addConstr(P_b[29] + uc_101*r_101*(ptdf_tab.loc[101]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[29])
	
		m.addConstr(P_b[30] + uc_101*r_101*(ptdf_tab.loc[101]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[30])
	
		m.addConstr(P_b[31] + uc_101*r_101*(ptdf_tab.loc[101]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[31])
	
		m.addConstr(P_b[32] + uc_101*r_101*(ptdf_tab.loc[101]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[32])
	
		m.addConstr(P_b[33] + uc_101*r_101*(ptdf_tab.loc[101]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*r_201*(ptdf_tab.loc[201]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*r_301*(ptdf_tab.loc[301]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*r_401*(ptdf_tab.loc[401]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*r_102*(ptdf_tab.loc[102]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*r_202*(ptdf_tab.loc[202]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*r_302*(ptdf_tab.loc[302]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*r_402*(ptdf_tab.loc[402]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*r_107*(ptdf_tab.loc[107]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*r_207*(ptdf_tab.loc[207]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*r_307*(ptdf_tab.loc[307]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*r_113*(ptdf_tab.loc[113]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*r_213*(ptdf_tab.loc[213]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*r_313*(ptdf_tab.loc[313]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*r_115*(ptdf_tab.loc[115]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*r_215*(ptdf_tab.loc[215]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*r_315*(ptdf_tab.loc[315]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*r_415*(ptdf_tab.loc[415]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*r_515*(ptdf_tab.loc[515]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*r_615*(ptdf_tab.loc[615]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*r_116*(ptdf_tab.loc[116]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*r_118*(ptdf_tab.loc[118]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*r_121*(ptdf_tab.loc[121]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*r_122*(ptdf_tab.loc[122]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*r_222*(ptdf_tab.loc[222]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*r_322*(ptdf_tab.loc[322]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*r_422*(ptdf_tab.loc[422]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*r_522*(ptdf_tab.loc[522]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*r_622*(ptdf_tab.loc[622]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*r_123*(ptdf_tab.loc[123]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*r_223*(ptdf_tab.loc[223]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*r_323*(ptdf_tab.loc[323]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[33])

		# Solve
		m.params.outputFlag = 0
		m.optimize()

		minute_results = 0.
		for elem in m.getVars():
			if elem.varName == 'uc_101':
				unit_recommit[101] = float(round(elem.x))
			elif elem.varName == 'uc_102':
				unit_recommit[102] = float(round(elem.x))
			elif elem.varName == 'uc_201':
				unit_recommit[201] = float(round(elem.x))
			elif elem.varName == 'uc_202':
				unit_recommit[202] = float(round(elem.x))
			elif elem.varName == 'r_101':
				unit_response[101] = float(elem.x)
			elif elem.varName == 'r_201':
				unit_response[201] = float(elem.x)
			elif elem.varName == 'r_301':
				unit_response[301] = float(elem.x)
			elif elem.varName == 'r_401':
				unit_response[401] = float(elem.x)
			elif elem.varName == 'r_102':
				unit_response[102] = float(elem.x)
			elif elem.varName == 'r_202':
				unit_response[202] = float(elem.x)
			elif elem.varName == 'r_302':
				unit_response[302] = float(elem.x)
			elif elem.varName == 'r_402':
				unit_response[402] = float(elem.x)
			elif elem.varName == 'r_107':
				unit_response[107] = float(elem.x)
			elif elem.varName == 'r_207':
				unit_response[207] = float(elem.x)
			elif elem.varName == 'r_307':
				unit_response[307] = float(elem.x)
			elif elem.varName == 'r_113':
				unit_response[113] = float(elem.x)
			elif elem.varName == 'r_213':
				unit_response[213] = float(elem.x)
			elif elem.varName == 'r_313':
				unit_response[313] = float(elem.x)
			elif elem.varName == 'r_115':
				unit_response[115] = float(elem.x)
			elif elem.varName == 'r_215':
				unit_response[215] = float(elem.x)
			elif elem.varName == 'r_315':
				unit_response[315] = float(elem.x)
			elif elem.varName == 'r_415':
				unit_response[415] = float(elem.x)
			elif elem.varName == 'r_515':
				unit_response[515] = float(elem.x)
			elif elem.varName == 'r_615':
				unit_response[615] = float(elem.x)
			elif elem.varName == 'r_116':
				unit_response[116] = float(elem.x)
			elif elem.varName == 'r_118':
				unit_response[118] = float(elem.x)
			elif elem.varName == 'r_121':
				unit_response[121] = float(elem.x)
			elif elem.varName == 'r_122':
				unit_response[122] = float(elem.x)
			elif elem.varName == 'r_222':
				unit_response[222] = float(elem.x)
			elif elem.varName == 'r_322':
				unit_response[322] = float(elem.x)
			elif elem.varName == 'r_422':
				unit_response[422] = float(elem.x)
			elif elem.varName == 'r_522':
				unit_response[522] = float(elem.x)
			elif elem.varName == 'r_622':
				unit_response[622] = float(elem.x)
			elif elem.varName == 'r_123':
				unit_response[123] = float(elem.x)
			elif elem.varName == 'r_223':
				unit_response[223] = float(elem.x)
			elif elem.varName == 'r_323':
				unit_response[323] = float(elem.x)
			elif elem.varName == 'mint':
				minute_results = float(elem.x)

		# unit_response[101] = 0.0
		# unit_response[201] = 0.0
		# unit_response[102] = 0.0
		# unit_response[202] = 0.0

		# unit_response[313] = 0.0

		# unit_response[615] = 0.0
		# unit_response[116] = 0.0
		# unit_response[118] = 0.0
		# unit_response[121] = 0.0

		# unit_response[123] = 0.0
		# unit_response[223] = 0.0

		for row in object_generator.matrix:
			if row[ODC.Generator.ID] == 101.0 or row[ODC.Generator.ID] == 201.0 or row[ODC.Generator.ID] == 102.0 or row[ODC.Generator.ID] == 202.0:
				uc_g[int(row[ODC.Generator.ID])] = unit_recommit[int(row[ODC.Generator.ID])]
			row[ODC.Generator.OPERATIONAL_STATUS] = uc_g[int(row[ODC.Generator.ID])]
			row[ODC.Generator.REAL_GENERATION] = uc_g[int(row[ODC.Generator.ID])]*row[ODC.Generator.REAL_GENERATION] + unit_response[int(row[ODC.Generator.ID])]

		# for elem in unit_response:
		# 	print(elem, unit_response[elem])

	except gurobipy.GurobiError:
		print('Gurobi error reported in contignency response')