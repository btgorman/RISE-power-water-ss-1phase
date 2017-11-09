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

NUMBER_OF_MINUTES = 10

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
		m.setObjective(1*uc_1 + 2*uc_2 + 3*uc_3 + 4*uc_4 + 5*uc_5 + 6*uc_6 + 7*uc_7 + 8*uc_8 + 9*uc_9, GRB.MINIMIZE)

		# Constraint - Loads = Gen
		m.addConstr((SUM_LOAD+losses+exports) - 0.01 <= uc_1*gf_1*mx_dispatch[1] + uc_2*gf_2*mx_dispatch[2] + uc_3*gf_3*mx_dispatch[3] + uc_4*gf_4*mx_dispatch[4] + uc_5*gf_5*mx_dispatch[5] + uc_6*gf_6*mx_dispatch[6] + uc_7*gf_7*mx_dispatch[7] + uc_8*gf_8*mx_dispatch[8] + uc_9*gf_9*mx_dispatch[9], 'system_load_1')
		m.addConstr((SUM_LOAD+losses+exports) + 0.01 >= uc_1*gf_1*mx_dispatch[1] + uc_2*gf_2*mx_dispatch[2] + uc_3*gf_3*mx_dispatch[3] + uc_4*gf_4*mx_dispatch[4] + uc_5*gf_5*mx_dispatch[5] + uc_6*gf_6*mx_dispatch[6] + uc_7*gf_7*mx_dispatch[7] + uc_8*gf_8*mx_dispatch[8] + uc_9*gf_9*mx_dispatch[9], 'system_load_2')

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
		print('Gurobi error reported in power dispatch')

def contingency_response(object_load, object_generator, losses, exports):

	uc_g = {}
	r_g = {}
	P_g = {}
	P_g_min = {}
	P_g_max = {}
	for row in object_generator.matrix:
		uc_g[int(row[ODC.Generator.ID])] = row[ODC.Generator.OPERATIONAL_STATUS] * row[ODC.Generator.FUNCTIONAL_STATUS]
		r_g[int(row[ODC.Generator.ID])] = row[ODC.Generator.RAMP_RATE]
		P_g[int(row[ODC.Generator.ID])] = row[ODC.Generator.REAL_GENERATION]
		P_g_min[int(row[ODC.Generator.ID])] = row[ODC.Generator.REAL_GENERATION_MIN_RATING]
		P_g_max[int(row[ODC.Generator.ID])] = row[ODC.Generator.REAL_GENERATION_MAX_RATING]
		if int(row[ODC.Generator.ID]) == 101 or int(row[ODC.Generator.ID]) == 201 or int(row[ODC.Generator.ID]) == 102 or int(row[ODC.Generator.ID]) == 202: # combustion turbines
			uc_g[int(row[ODC.Generator.ID])] = 1.0

	SUM_LOAD = float(sum(object_load.matrix[:, ODC.Load.REAL_LOAD]))

	try:
		m = gurobipy.Model('mip1')
		
		slack = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='power_slack')

		r_101 = m.addVar(vtype=GRB.CONTINUOUS, name='r_101')
		r_201 = m.addVar(vtype=GRB.CONTINUOUS, name='r_201')
		r_301 = m.addVar(vtype=GRB.CONTINUOUS, name='r_301')
		r_401 = m.addVar(vtype=GRB.CONTINUOUS, name='r_401')
		r_102 = m.addVar(vtype=GRB.CONTINUOUS, name='r_102')
		r_202 = m.addVar(vtype=GRB.CONTINUOUS, name='r_202')
		r_302 = m.addVar(vtype=GRB.CONTINUOUS, name='r_302')
		r_402 = m.addVar(vtype=GRB.CONTINUOUS, name='r_402')
		r_107 = m.addVar(vtype=GRB.CONTINUOUS, name='r_107')
		r_207 = m.addVar(vtype=GRB.CONTINUOUS, name='r_207')
		r_307 = m.addVar(vtype=GRB.CONTINUOUS, name='r_307')
		r_113 = m.addVar(vtype=GRB.CONTINUOUS, name='r_113')
		r_213 = m.addVar(vtype=GRB.CONTINUOUS, name='r_213')
		r_313 = m.addVar(vtype=GRB.CONTINUOUS, name='r_313')
		r_115 = m.addVar(vtype=GRB.CONTINUOUS, name='r_115')
		r_215 = m.addVar(vtype=GRB.CONTINUOUS, name='r_215')
		r_315 = m.addVar(vtype=GRB.CONTINUOUS, name='r_315')
		r_415 = m.addVar(vtype=GRB.CONTINUOUS, name='r_415')
		r_515 = m.addVar(vtype=GRB.CONTINUOUS, name='r_515')
		r_615 = m.addVar(vtype=GRB.CONTINUOUS, name='r_615')
		r_116 = m.addVar(vtype=GRB.CONTINUOUS, name='r_116')
		r_118 = m.addVar(vtype=GRB.CONTINUOUS, name='r_118')
		r_121 = m.addVar(vtype=GRB.CONTINUOUS, name='r_121')
		r_122 = m.addVar(vtype=GRB.CONTINUOUS, name='r_122')
		r_222 = m.addVar(vtype=GRB.CONTINUOUS, name='r_222')
		r_322 = m.addVar(vtype=GRB.CONTINUOUS, name='r_322')
		r_422 = m.addVar(vtype=GRB.CONTINUOUS, name='r_422')
		r_522 = m.addVar(vtype=GRB.CONTINUOUS, name='r_522')
		r_622 = m.addVar(vtype=GRB.CONTINUOUS, name='r_622')
		r_123 = m.addVar(vtype=GRB.CONTINUOUS, name='r_123')
		r_223 = m.addVar(vtype=GRB.CONTINUOUS, name='r_223')
		r_323 = m.addVar(vtype=GRB.CONTINUOUS, name='r_323')

		m.setObjective(slack, GRB.MINIMIZE)

		m.addConstr(SUM_LOAD+losses+exports - slack <= uc_g[101]*(P_g[101] + r_101) + uc_g[201]*(P_g[201] + r_201) + uc_g[301]*(P_g[301] + r_301) + uc_g[401]*(P_g[401] + r_401) + uc_g[102]*(P_g[102] + r_102) + uc_g[202]*(P_g[202] + r_202) + uc_g[302]*(P_g[302] + r_302) + uc_g[402]*(P_g[402] + r_402) + uc_g[107]*(P_g[107] + r_107) + uc_g[207]*(P_g[207] + r_207) + uc_g[307]*(P_g[307] + r_307) + uc_g[113]*(P_g[113] + r_113) + uc_g[213]*(P_g[213] + r_213) + uc_g[313]*(P_g[313] + r_313) + uc_g[115]*(P_g[115] + r_115) + uc_g[215]*(P_g[215] + r_215) + uc_g[315]*(P_g[315] + r_315) + uc_g[415]*(P_g[415] + r_415) + uc_g[515]*(P_g[515] + r_515) + uc_g[615]*(P_g[615] + r_615) + uc_g[116]*(P_g[116] + r_116) + uc_g[118]*(P_g[118] + r_118) + uc_g[121]*(P_g[121] + r_121) + uc_g[122]*(P_g[122] + r_122) + uc_g[222]*(P_g[222] + r_222) + uc_g[322]*(P_g[322] + r_322) + uc_g[422]*(P_g[422] + r_422) + uc_g[522]*(P_g[522] + r_522) + uc_g[622]*(P_g[622] + r_622) + uc_g[123]*(P_g[123] + r_123) + uc_g[223]*(P_g[223] + r_223) + uc_g[323]*(P_g[323] + r_323))
		m.addConstr(SUM_LOAD+losses+exports + slack >= uc_g[101]*(P_g[101] + r_101) + uc_g[201]*(P_g[201] + r_201) + uc_g[301]*(P_g[301] + r_301) + uc_g[401]*(P_g[401] + r_401) + uc_g[102]*(P_g[102] + r_102) + uc_g[202]*(P_g[202] + r_202) + uc_g[302]*(P_g[302] + r_302) + uc_g[402]*(P_g[402] + r_402) + uc_g[107]*(P_g[107] + r_107) + uc_g[207]*(P_g[207] + r_207) + uc_g[307]*(P_g[307] + r_307) + uc_g[113]*(P_g[113] + r_113) + uc_g[213]*(P_g[213] + r_213) + uc_g[313]*(P_g[313] + r_313) + uc_g[115]*(P_g[115] + r_115) + uc_g[215]*(P_g[215] + r_215) + uc_g[315]*(P_g[315] + r_315) + uc_g[415]*(P_g[415] + r_415) + uc_g[515]*(P_g[515] + r_515) + uc_g[615]*(P_g[615] + r_615) + uc_g[116]*(P_g[116] + r_116) + uc_g[118]*(P_g[118] + r_118) + uc_g[121]*(P_g[121] + r_121) + uc_g[122]*(P_g[122] + r_122) + uc_g[222]*(P_g[222] + r_222) + uc_g[322]*(P_g[322] + r_322) + uc_g[422]*(P_g[422] + r_422) + uc_g[522]*(P_g[522] + r_522) + uc_g[622]*(P_g[622] + r_622) + uc_g[123]*(P_g[123] + r_123) + uc_g[223]*(P_g[223] + r_223) + uc_g[323]*(P_g[323] + r_323))

		m.addConstr(r_101 >= uc_g[101] * (NUMBER_OF_MINUTES * -r_g[101]))
		m.addConstr(r_201 >= uc_g[201] * (NUMBER_OF_MINUTES * -r_g[201]))
		m.addConstr(r_301 >= uc_g[301] * (NUMBER_OF_MINUTES * -r_g[301]))
		m.addConstr(r_401 >= uc_g[401] * (NUMBER_OF_MINUTES * -r_g[401]))
		m.addConstr(r_102 >= uc_g[102] * (NUMBER_OF_MINUTES * -r_g[102]))
		m.addConstr(r_202 >= uc_g[202] * (NUMBER_OF_MINUTES * -r_g[202]))
		m.addConstr(r_302 >= uc_g[302] * (NUMBER_OF_MINUTES * -r_g[302]))
		m.addConstr(r_402 >= uc_g[402] * (NUMBER_OF_MINUTES * -r_g[402]))
		m.addConstr(r_107 >= uc_g[107] * (NUMBER_OF_MINUTES * -r_g[107]))
		m.addConstr(r_207 >= uc_g[207] * (NUMBER_OF_MINUTES * -r_g[207]))
		m.addConstr(r_307 >= uc_g[307] * (NUMBER_OF_MINUTES * -r_g[307]))
		m.addConstr(r_113 >= uc_g[113] * (NUMBER_OF_MINUTES * -r_g[113]))
		m.addConstr(r_213 >= uc_g[213] * (NUMBER_OF_MINUTES * -r_g[213]))
		m.addConstr(r_313 >= uc_g[313] * (NUMBER_OF_MINUTES * -r_g[313]))
		m.addConstr(r_115 >= uc_g[115] * (NUMBER_OF_MINUTES * -r_g[115]))
		m.addConstr(r_215 >= uc_g[215] * (NUMBER_OF_MINUTES * -r_g[215]))
		m.addConstr(r_315 >= uc_g[315] * (NUMBER_OF_MINUTES * -r_g[315]))
		m.addConstr(r_415 >= uc_g[415] * (NUMBER_OF_MINUTES * -r_g[415]))
		m.addConstr(r_515 >= uc_g[515] * (NUMBER_OF_MINUTES * -r_g[515]))
		m.addConstr(r_615 >= uc_g[615] * (NUMBER_OF_MINUTES * -r_g[615]))
		m.addConstr(r_116 >= uc_g[116] * (NUMBER_OF_MINUTES * -r_g[116]))
		m.addConstr(r_118 >= uc_g[118] * (NUMBER_OF_MINUTES * -r_g[118]))
		m.addConstr(r_121 >= uc_g[121] * (NUMBER_OF_MINUTES * -r_g[121]))
		m.addConstr(r_122 >= uc_g[122] * (NUMBER_OF_MINUTES * -r_g[122]))
		m.addConstr(r_222 >= uc_g[222] * (NUMBER_OF_MINUTES * -r_g[222]))
		m.addConstr(r_322 >= uc_g[322] * (NUMBER_OF_MINUTES * -r_g[322]))
		m.addConstr(r_422 >= uc_g[422] * (NUMBER_OF_MINUTES * -r_g[422]))
		m.addConstr(r_522 >= uc_g[522] * (NUMBER_OF_MINUTES * -r_g[522]))
		m.addConstr(r_622 >= uc_g[622] * (NUMBER_OF_MINUTES * -r_g[622]))
		m.addConstr(r_123 >= uc_g[123] * (NUMBER_OF_MINUTES * -r_g[123]))
		m.addConstr(r_223 >= uc_g[223] * (NUMBER_OF_MINUTES * -r_g[223]))
		m.addConstr(r_323 >= uc_g[323] * (NUMBER_OF_MINUTES * -r_g[323]))

		m.addConstr(r_101 <= uc_g[101] * (NUMBER_OF_MINUTES * r_g[101]))
		m.addConstr(r_201 <= uc_g[201] * (NUMBER_OF_MINUTES * r_g[201]))
		m.addConstr(r_301 <= uc_g[301] * (NUMBER_OF_MINUTES * r_g[301]))
		m.addConstr(r_401 <= uc_g[401] * (NUMBER_OF_MINUTES * r_g[401]))
		m.addConstr(r_102 <= uc_g[102] * (NUMBER_OF_MINUTES * r_g[102]))
		m.addConstr(r_202 <= uc_g[202] * (NUMBER_OF_MINUTES * r_g[202]))
		m.addConstr(r_302 <= uc_g[302] * (NUMBER_OF_MINUTES * r_g[302]))
		m.addConstr(r_402 <= uc_g[402] * (NUMBER_OF_MINUTES * r_g[402]))
		m.addConstr(r_107 <= uc_g[107] * (NUMBER_OF_MINUTES * r_g[107]))
		m.addConstr(r_207 <= uc_g[207] * (NUMBER_OF_MINUTES * r_g[207]))
		m.addConstr(r_307 <= uc_g[307] * (NUMBER_OF_MINUTES * r_g[307]))
		m.addConstr(r_113 <= uc_g[113] * (NUMBER_OF_MINUTES * r_g[113]))
		m.addConstr(r_213 <= uc_g[213] * (NUMBER_OF_MINUTES * r_g[213]))
		m.addConstr(r_313 <= uc_g[313] * (NUMBER_OF_MINUTES * r_g[313]))
		m.addConstr(r_115 <= uc_g[115] * (NUMBER_OF_MINUTES * r_g[115]))
		m.addConstr(r_215 <= uc_g[215] * (NUMBER_OF_MINUTES * r_g[215]))
		m.addConstr(r_315 <= uc_g[315] * (NUMBER_OF_MINUTES * r_g[315]))
		m.addConstr(r_415 <= uc_g[415] * (NUMBER_OF_MINUTES * r_g[415]))
		m.addConstr(r_515 <= uc_g[515] * (NUMBER_OF_MINUTES * r_g[515]))
		m.addConstr(r_615 <= uc_g[615] * (NUMBER_OF_MINUTES * r_g[615]))
		m.addConstr(r_116 <= uc_g[116] * (NUMBER_OF_MINUTES * r_g[116]))
		m.addConstr(r_118 <= uc_g[118] * (NUMBER_OF_MINUTES * r_g[118]))
		m.addConstr(r_121 <= uc_g[121] * (NUMBER_OF_MINUTES * r_g[121]))
		m.addConstr(r_122 <= uc_g[122] * (NUMBER_OF_MINUTES * r_g[122]))
		m.addConstr(r_222 <= uc_g[222] * (NUMBER_OF_MINUTES * r_g[222]))
		m.addConstr(r_322 <= uc_g[322] * (NUMBER_OF_MINUTES * r_g[322]))
		m.addConstr(r_422 <= uc_g[422] * (NUMBER_OF_MINUTES * r_g[422]))
		m.addConstr(r_522 <= uc_g[522] * (NUMBER_OF_MINUTES * r_g[522]))
		m.addConstr(r_622 <= uc_g[622] * (NUMBER_OF_MINUTES * r_g[622]))
		m.addConstr(r_123 <= uc_g[123] * (NUMBER_OF_MINUTES * r_g[123]))
		m.addConstr(r_223 <= uc_g[223] * (NUMBER_OF_MINUTES * r_g[223]))
		m.addConstr(r_323 <= uc_g[323] * (NUMBER_OF_MINUTES * r_g[323]))

		m.addConstr(P[101] + r_101 >= uc_g[101] * P_g_min[101])
		m.addConstr(P[201] + r_201 >= uc_g[201] * P_g_min[201])
		m.addConstr(P[301] + r_301 >= uc_g[301] * P_g_min[301])
		m.addConstr(P[401] + r_401 >= uc_g[401] * P_g_min[401])
		m.addConstr(P[102] + r_102 >= uc_g[102] * P_g_min[102])
		m.addConstr(P[202] + r_202 >= uc_g[202] * P_g_min[202])
		m.addConstr(P[302] + r_302 >= uc_g[302] * P_g_min[302])
		m.addConstr(P[402] + r_402 >= uc_g[402] * P_g_min[402])
		m.addConstr(P[107] + r_107 >= uc_g[107] * P_g_min[107])
		m.addConstr(P[207] + r_207 >= uc_g[207] * P_g_min[207])
		m.addConstr(P[307] + r_307 >= uc_g[307] * P_g_min[307])
		m.addConstr(P[113] + r_113 >= uc_g[113] * P_g_min[113])
		m.addConstr(P[213] + r_213 >= uc_g[213] * P_g_min[213])
		m.addConstr(P[313] + r_313 >= uc_g[313] * P_g_min[313])
		m.addConstr(P[115] + r_115 >= uc_g[115] * P_g_min[115])
		m.addConstr(P[215] + r_215 >= uc_g[215] * P_g_min[215])
		m.addConstr(P[315] + r_315 >= uc_g[315] * P_g_min[315])
		m.addConstr(P[415] + r_415 >= uc_g[415] * P_g_min[415])
		m.addConstr(P[515] + r_515 >= uc_g[515] * P_g_min[515])
		m.addConstr(P[615] + r_615 >= uc_g[615] * P_g_min[615])
		m.addConstr(P[116] + r_116 >= uc_g[116] * P_g_min[116])
		m.addConstr(P[118] + r_118 >= uc_g[118] * P_g_min[118])
		m.addConstr(P[121] + r_121 >= uc_g[121] * P_g_min[121])
		m.addConstr(P[122] + r_122 >= uc_g[122] * P_g_min[122])
		m.addConstr(P[222] + r_222 >= uc_g[222] * P_g_min[222])
		m.addConstr(P[322] + r_322 >= uc_g[322] * P_g_min[322])
		m.addConstr(P[422] + r_422 >= uc_g[422] * P_g_min[422])
		m.addConstr(P[522] + r_522 >= uc_g[522] * P_g_min[522])
		m.addConstr(P[622] + r_622 >= uc_g[622] * P_g_min[622])
		m.addConstr(P[123] + r_123 >= uc_g[123] * P_g_min[123])
		m.addConstr(P[223] + r_223 >= uc_g[223] * P_g_min[223])
		m.addConstr(P[323] + r_323 >= uc_g[323] * P_g_min[323])

		m.addConstr(P[101] + r_101 <= uc_g[101] * P_g_max[101])
		m.addConstr(P[201] + r_201 <= uc_g[201] * P_g_max[201])
		m.addConstr(P[301] + r_301 <= uc_g[301] * P_g_max[301])
		m.addConstr(P[401] + r_401 <= uc_g[401] * P_g_max[401])
		m.addConstr(P[102] + r_102 <= uc_g[102] * P_g_max[102])
		m.addConstr(P[202] + r_202 <= uc_g[202] * P_g_max[202])
		m.addConstr(P[302] + r_302 <= uc_g[302] * P_g_max[302])
		m.addConstr(P[402] + r_402 <= uc_g[402] * P_g_max[402])
		m.addConstr(P[107] + r_107 <= uc_g[107] * P_g_max[107])
		m.addConstr(P[207] + r_207 <= uc_g[207] * P_g_max[207])
		m.addConstr(P[307] + r_307 <= uc_g[307] * P_g_max[307])
		m.addConstr(P[113] + r_113 <= uc_g[113] * P_g_max[113])
		m.addConstr(P[213] + r_213 <= uc_g[213] * P_g_max[213])
		m.addConstr(P[313] + r_313 <= uc_g[313] * P_g_max[313])
		m.addConstr(P[115] + r_115 <= uc_g[115] * P_g_max[115])
		m.addConstr(P[215] + r_215 <= uc_g[215] * P_g_max[215])
		m.addConstr(P[315] + r_315 <= uc_g[315] * P_g_max[315])
		m.addConstr(P[415] + r_415 <= uc_g[415] * P_g_max[415])
		m.addConstr(P[515] + r_515 <= uc_g[515] * P_g_max[515])
		m.addConstr(P[615] + r_615 <= uc_g[615] * P_g_max[615])
		m.addConstr(P[116] + r_116 <= uc_g[116] * P_g_max[116])
		m.addConstr(P[118] + r_118 <= uc_g[118] * P_g_max[118])
		m.addConstr(P[121] + r_121 <= uc_g[121] * P_g_max[121])
		m.addConstr(P[122] + r_122 <= uc_g[122] * P_g_max[122])
		m.addConstr(P[222] + r_222 <= uc_g[222] * P_g_max[222])
		m.addConstr(P[322] + r_322 <= uc_g[322] * P_g_max[322])
		m.addConstr(P[422] + r_422 <= uc_g[422] * P_g_max[422])
		m.addConstr(P[522] + r_522 <= uc_g[522] * P_g_max[522])
		m.addConstr(P[622] + r_622 <= uc_g[622] * P_g_max[622])
		m.addConstr(P[123] + r_123 <= uc_g[123] * P_g_max[123])
		m.addConstr(P[223] + r_223 <= uc_g[223] * P_g_max[223])
		m.addConstr(P[323] + r_323 <= uc_g[323] * P_g_max[323])


	except gurobipy.GurobiError:
		print('Gurobi error reported in contignency response')