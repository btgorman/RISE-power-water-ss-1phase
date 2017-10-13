import classes_power as ODC
import numpy as np

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

def power_dispatch(object_load, object_generator, losses, export):
	mx_dispatch = {1: 0., 2: 0., 3: 0., 4: 0., 5: 0., 6: 0., 7: 0., 8: 0., 9: 0.}
	mx_reserve = {1: 0., 2: 0., 3: 0., 4: 0., 5: 0., 6: 0., 7: 0., 8: 0., 9: 0.}
	dispatch_factor = {1: 0., 2: 0., 3: 0., 4: 0., 5: 0., 6: 0., 7: 0., 8: 0., 9: 0.}
	operational_status = {1: 0., 2: 0., 3: 0., 4: 0., 5: 0., 6: 0., 7: 0., 8: 0., 9: 0.}

	# Set "constants"
	for row in object_generator.matrix:
		mx_dispatch[GEN_PRIORITY_KEY[int(row[ODC.Generator.ID])]] += row[ODC.Generator.REAL_GENERATION_MAX_RATING]
		mx_reserve[GEN_PRIORITY_KEY[int(row[ODC.Generator.ID])]] += row[ODC.Generator.RAMP_RATE]
	SUM_LOAD = float(sum(object_load.matrix[:, ODC.Load.REAL_LOAD]))
	NUMBER_OF_MINUTES = 10

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
		m.setObjective(1*uc_1 + 2*uc_2 + 3*uc_3 + 4*uc_4 + 5*uc_5 + 6*uc_6 + 7*uc_7 + 8*uc_8 + 9*uc_9, GRB.MINIMIZE)

		# Constraint - Loads = Gen
		m.addConstr((SUM_LOAD+losses+export) - 0.01 <= uc_1*gf_1*mx_dispatch[1] + uc_2*gf_2*mx_dispatch[2] + uc_3*gf_3*mx_dispatch[3] + uc_4*gf_4*mx_dispatch[4] + uc_5*gf_5*mx_dispatch[5] + uc_6*gf_6*mx_dispatch[6] + uc_7*gf_7*mx_dispatch[7] + uc_8*gf_8*mx_dispatch[8] + uc_9*gf_9*mx_dispatch[9], 'system_load_1')
		m.addConstr((SUM_LOAD+losses+export) + 0.01 >= uc_1*gf_1*mx_dispatch[1] + uc_2*gf_2*mx_dispatch[2] + uc_3*gf_3*mx_dispatch[3] + uc_4*gf_4*mx_dispatch[4] + uc_5*gf_5*mx_dispatch[5] + uc_6*gf_6*mx_dispatch[6] + uc_7*gf_7*mx_dispatch[7] + uc_8*gf_8*mx_dispatch[8] + uc_9*gf_9*mx_dispatch[9], 'system_load_2')

		# Constraint - Minimum required reserve for CAISO
		m.addConstr(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9 >= uc_1*gf_1*mx_dispatch[1]*0.05 + (uc_2*gf_2*mx_dispatch[2] + uc_3*gf_3*mx_dispatch[3] + uc_4*gf_4*mx_dispatch[4] + uc_5*gf_5*mx_dispatch[5] + uc_6*gf_6*mx_dispatch[6] + uc_7*gf_7*mx_dispatch[7] + uc_8*gf_8*mx_dispatch[8] + uc_9*gf_9*mx_dispatch[9])*0.07, 'net_reserves')

		# Constraint - Minimum required reserve for largest unit
		m.addConstr(GEN_PRIORITY_COUNT[1]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) >= uc_1*gf_1*mx_dispatch[1], 'reserve_req_1')
		m.addConstr(GEN_PRIORITY_COUNT[2]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) >= uc_2*gf_2*mx_dispatch[2], 'reserve_req_2')
		m.addConstr(GEN_PRIORITY_COUNT[3]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) >= uc_3*gf_3*mx_dispatch[3], 'reserve_req_3')
		m.addConstr(GEN_PRIORITY_COUNT[4]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) >= uc_4*gf_4*mx_dispatch[4], 'reserve_req_4')
		m.addConstr(GEN_PRIORITY_COUNT[5]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) >= uc_5*gf_5*mx_dispatch[5], 'reserve_req_5')
		m.addConstr(GEN_PRIORITY_COUNT[6]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) >= uc_6*gf_6*mx_dispatch[6], 'reserve_req_6')
		m.addConstr(GEN_PRIORITY_COUNT[7]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) >= uc_7*gf_7*mx_dispatch[7], 'reserve_req_7')
		m.addConstr(GEN_PRIORITY_COUNT[8]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) >= uc_8*gf_8*mx_dispatch[8], 'reserve_req_8')
		m.addConstr(GEN_PRIORITY_COUNT[9]*(ra_1 + ra_2 + ra_3 + ra_4 + ra_5 + ra_6 + ra_7 + ra_8 + ra_9) >= uc_9*gf_9*mx_dispatch[9], 'reserve_req_9')

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

	except gurobipy.GurobiError:
		print('Gurobi error reported')