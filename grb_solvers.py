import classes_power as ODC
import numpy as np
import pandas as pd
import math

import gurobipy
from gurobipy import GRB, min_

import sys, os

os_username = os.getlogin()

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
EXTRA_RESERVE_MARGIN = 1.07 # %

def unit_commitment_priority_list(object_load, object_generator, losses, exports):

	out_u_c = {}
	out_u_d = {}
	out_u_r = {}
	unit_min_dispatch = {}

	obj_coeff_list = []
	hydro_coeff_list = []
	non_hydro_coeff_list = []
	combustion_ids = []

	combustion_id_counter = 0
	for unit_id in object_generator.matrix[:, ODC.Generator.ID]:
		obj_coeff_list.append(GEN_PRIORITY_KEY[int(unit_id)])

		if GEN_PRIORITY_KEY[int(unit_id)] == 9:
			combustion_ids.append(combustion_id_counter)
		if GEN_PRIORITY_KEY[int(unit_id)] == 1: # hydro units
			hydro_coeff_list.append(1.0)
			non_hydro_coeff_list.append(0.0)
		else: # non hydro units
			hydro_coeff_list.append(0.0)
			non_hydro_coeff_list.append(1.0)

		combustion_id_counter += 1

	unit_water_consumption = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], object_generator.matrix[:, ODC.Generator.WATER_CONSUMPTION])}
	obj_coeff = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], obj_coeff_list)}
	# coefficient with ones for hydro units only
	hydro_coeff = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], hydro_coeff_list)}
	# coefficients with ones for non-hydro units only
	non_hydro_coeff = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], non_hydro_coeff_list)}

	for row in object_generator.matrix:
		unit_min_dispatch[row[ODC.Generator.ID]] = row[ODC.Generator.REAL_GENERATION_MIN_RATING]

	SUM_LOAD = float(sum(object_load.matrix[:, ODC.Load.REAL_LOAD]) + sum(object_load.matrix[:, ODC.Load.INTERCONNECTION_LOAD]))
	losses = float(losses)
	exports = float(exports)

	try:
		m = gurobipy.Model('mip1')

		unit_dispatch = m.addVars(object_generator.matrix[:, ODC.Generator.ID], lb=0.0, ub=object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], vtype=GRB.CONTINUOUS, name='u_d')
		unit_commit = m.addVars(object_generator.matrix[:, ODC.Generator.ID], lb=0.0, ub=1.0, vtype=GRB.BINARY, name='u_c')
		unit_reserves = m.addVars(object_generator.matrix[:, ODC.Generator.ID], lb=0.0, ub=(NUMBER_OF_MINUTES * object_generator.matrix[:, ODC.Generator.RAMP_RATE]), vtype=GRB.CONTINUOUS, name='u_r')

		# Minimizes priority list
		m.setObjective(unit_commit[101.0]*unit_dispatch[101.0]*obj_coeff[101.0] + 
			unit_commit[201.0]*unit_dispatch[201.0]*obj_coeff[201.0] + 
			unit_commit[301.0]*unit_dispatch[301.0]*obj_coeff[301.0] + 
			unit_commit[401.0]*unit_dispatch[401.0]*obj_coeff[401.0] + 
			unit_commit[102.0]*unit_dispatch[102.0]*obj_coeff[102.0] + 
			unit_commit[202.0]*unit_dispatch[202.0]*obj_coeff[202.0] + 
			unit_commit[302.0]*unit_dispatch[302.0]*obj_coeff[302.0] + 
			unit_commit[402.0]*unit_dispatch[402.0]*obj_coeff[402.0] + 
			unit_commit[107.0]*unit_dispatch[107.0]*obj_coeff[107.0] + 
			unit_commit[207.0]*unit_dispatch[207.0]*obj_coeff[207.0] + 
			unit_commit[307.0]*unit_dispatch[307.0]*obj_coeff[307.0] + 
			unit_commit[113.0]*unit_dispatch[113.0]*obj_coeff[113.0] + 
			unit_commit[213.0]*unit_dispatch[213.0]*obj_coeff[213.0] + 
			unit_commit[313.0]*unit_dispatch[313.0]*obj_coeff[313.0] + 
			unit_commit[115.0]*unit_dispatch[115.0]*obj_coeff[115.0] + 
			unit_commit[215.0]*unit_dispatch[215.0]*obj_coeff[215.0] + 
			unit_commit[315.0]*unit_dispatch[315.0]*obj_coeff[315.0] + 
			unit_commit[415.0]*unit_dispatch[415.0]*obj_coeff[415.0] + 
			unit_commit[515.0]*unit_dispatch[515.0]*obj_coeff[515.0] + 
			unit_commit[615.0]*unit_dispatch[615.0]*obj_coeff[615.0] + 
			unit_commit[116.0]*unit_dispatch[116.0]*obj_coeff[116.0] + 
			unit_commit[118.0]*unit_dispatch[118.0]*obj_coeff[118.0] + 
			unit_commit[121.0]*unit_dispatch[121.0]*obj_coeff[121.0] + 
			unit_commit[122.0]*unit_dispatch[122.0]*obj_coeff[122.0] + 
			unit_commit[222.0]*unit_dispatch[222.0]*obj_coeff[222.0] + 
			unit_commit[322.0]*unit_dispatch[322.0]*obj_coeff[322.0] + 
			unit_commit[422.0]*unit_dispatch[422.0]*obj_coeff[422.0] + 
			unit_commit[522.0]*unit_dispatch[522.0]*obj_coeff[522.0] + 
			unit_commit[622.0]*unit_dispatch[622.0]*obj_coeff[622.0] + 
			unit_commit[123.0]*unit_dispatch[123.0]*obj_coeff[123.0] + 
			unit_commit[223.0]*unit_dispatch[223.0]*obj_coeff[223.0] + 
			unit_commit[323.0]*unit_dispatch[323.0]*obj_coeff[323.0], GRB.MINIMIZE)

		# Balances Gen~Load
		m.addConstr(SUM_LOAD+losses+exports - 0.01 <= unit_commit[101.0]*unit_dispatch[101.0] + 
			unit_commit[201.0]*unit_dispatch[201.0] + 
			unit_commit[301.0]*unit_dispatch[301.0] + 
			unit_commit[401.0]*unit_dispatch[401.0] + 
			unit_commit[102.0]*unit_dispatch[102.0] + 
			unit_commit[202.0]*unit_dispatch[202.0] + 
			unit_commit[302.0]*unit_dispatch[302.0] + 
			unit_commit[402.0]*unit_dispatch[402.0] + 
			unit_commit[107.0]*unit_dispatch[107.0] + 
			unit_commit[207.0]*unit_dispatch[207.0] + 
			unit_commit[307.0]*unit_dispatch[307.0] + 
			unit_commit[113.0]*unit_dispatch[113.0] + 
			unit_commit[213.0]*unit_dispatch[213.0] + 
			unit_commit[313.0]*unit_dispatch[313.0] + 
			unit_commit[115.0]*unit_dispatch[115.0] + 
			unit_commit[215.0]*unit_dispatch[215.0] + 
			unit_commit[315.0]*unit_dispatch[315.0] + 
			unit_commit[415.0]*unit_dispatch[415.0] + 
			unit_commit[515.0]*unit_dispatch[515.0] + 
			unit_commit[615.0]*unit_dispatch[615.0] + 
			unit_commit[116.0]*unit_dispatch[116.0] + 
			unit_commit[118.0]*unit_dispatch[118.0] + 
			unit_commit[121.0]*unit_dispatch[121.0] + 
			unit_commit[122.0]*unit_dispatch[122.0] + 
			unit_commit[222.0]*unit_dispatch[222.0] + 
			unit_commit[322.0]*unit_dispatch[322.0] + 
			unit_commit[422.0]*unit_dispatch[422.0] + 
			unit_commit[522.0]*unit_dispatch[522.0] + 
			unit_commit[622.0]*unit_dispatch[622.0] + 
			unit_commit[123.0]*unit_dispatch[123.0] + 
			unit_commit[223.0]*unit_dispatch[223.0] + 
			unit_commit[323.0]*unit_dispatch[323.0])
		m.addConstr(SUM_LOAD+losses+exports + 0.01 >= unit_commit[101.0]*unit_dispatch[101.0] + 
			unit_commit[201.0]*unit_dispatch[201.0] + 
			unit_commit[301.0]*unit_dispatch[301.0] + 
			unit_commit[401.0]*unit_dispatch[401.0] + 
			unit_commit[102.0]*unit_dispatch[102.0] + 
			unit_commit[202.0]*unit_dispatch[202.0] + 
			unit_commit[302.0]*unit_dispatch[302.0] + 
			unit_commit[402.0]*unit_dispatch[402.0] + 
			unit_commit[107.0]*unit_dispatch[107.0] + 
			unit_commit[207.0]*unit_dispatch[207.0] + 
			unit_commit[307.0]*unit_dispatch[307.0] + 
			unit_commit[113.0]*unit_dispatch[113.0] + 
			unit_commit[213.0]*unit_dispatch[213.0] + 
			unit_commit[313.0]*unit_dispatch[313.0] + 
			unit_commit[115.0]*unit_dispatch[115.0] + 
			unit_commit[215.0]*unit_dispatch[215.0] + 
			unit_commit[315.0]*unit_dispatch[315.0] + 
			unit_commit[415.0]*unit_dispatch[415.0] + 
			unit_commit[515.0]*unit_dispatch[515.0] + 
			unit_commit[615.0]*unit_dispatch[615.0] + 
			unit_commit[116.0]*unit_dispatch[116.0] + 
			unit_commit[118.0]*unit_dispatch[118.0] + 
			unit_commit[121.0]*unit_dispatch[121.0] + 
			unit_commit[122.0]*unit_dispatch[122.0] + 
			unit_commit[222.0]*unit_dispatch[222.0] + 
			unit_commit[322.0]*unit_dispatch[322.0] + 
			unit_commit[422.0]*unit_dispatch[422.0] + 
			unit_commit[522.0]*unit_dispatch[522.0] + 
			unit_commit[622.0]*unit_dispatch[622.0] + 
			unit_commit[123.0]*unit_dispatch[123.0] + 
			unit_commit[223.0]*unit_dispatch[223.0] + 
			unit_commit[323.0]*unit_dispatch[323.0])

		# Bounds unit dispatch with minimum dispatch
		m.addConstr(unit_commit[101.0]*unit_dispatch[101.0] >= unit_commit[101.0]*unit_min_dispatch[101.0])
		m.addConstr(unit_commit[201.0]*unit_dispatch[201.0] >= unit_commit[201.0]*unit_min_dispatch[201.0])
		m.addConstr(unit_commit[301.0]*unit_dispatch[301.0] >= unit_commit[301.0]*unit_min_dispatch[301.0])
		m.addConstr(unit_commit[401.0]*unit_dispatch[401.0] >= unit_commit[401.0]*unit_min_dispatch[401.0])
		m.addConstr(unit_commit[102.0]*unit_dispatch[102.0] >= unit_commit[102.0]*unit_min_dispatch[102.0])
		m.addConstr(unit_commit[202.0]*unit_dispatch[202.0] >= unit_commit[202.0]*unit_min_dispatch[202.0])
		m.addConstr(unit_commit[302.0]*unit_dispatch[302.0] >= unit_commit[302.0]*unit_min_dispatch[302.0])
		m.addConstr(unit_commit[402.0]*unit_dispatch[402.0] >= unit_commit[402.0]*unit_min_dispatch[402.0])
		m.addConstr(unit_commit[107.0]*unit_dispatch[107.0] >= unit_commit[107.0]*unit_min_dispatch[107.0])
		m.addConstr(unit_commit[207.0]*unit_dispatch[207.0] >= unit_commit[207.0]*unit_min_dispatch[207.0])
		m.addConstr(unit_commit[307.0]*unit_dispatch[307.0] >= unit_commit[307.0]*unit_min_dispatch[307.0])
		m.addConstr(unit_commit[113.0]*unit_dispatch[113.0] >= unit_commit[113.0]*unit_min_dispatch[113.0])
		m.addConstr(unit_commit[213.0]*unit_dispatch[213.0] >= unit_commit[213.0]*unit_min_dispatch[213.0])
		m.addConstr(unit_commit[313.0]*unit_dispatch[313.0] >= unit_commit[313.0]*unit_min_dispatch[313.0])
		m.addConstr(unit_commit[115.0]*unit_dispatch[115.0] >= unit_commit[115.0]*unit_min_dispatch[115.0])
		m.addConstr(unit_commit[215.0]*unit_dispatch[215.0] >= unit_commit[215.0]*unit_min_dispatch[215.0])
		m.addConstr(unit_commit[315.0]*unit_dispatch[315.0] >= unit_commit[315.0]*unit_min_dispatch[315.0])
		m.addConstr(unit_commit[415.0]*unit_dispatch[415.0] >= unit_commit[415.0]*unit_min_dispatch[415.0])
		m.addConstr(unit_commit[515.0]*unit_dispatch[515.0] >= unit_commit[515.0]*unit_min_dispatch[515.0])
		m.addConstr(unit_commit[615.0]*unit_dispatch[615.0] >= unit_commit[615.0]*unit_min_dispatch[615.0])
		m.addConstr(unit_commit[116.0]*unit_dispatch[116.0] >= unit_commit[116.0]*unit_min_dispatch[116.0])
		m.addConstr(unit_commit[118.0]*unit_dispatch[118.0] >= unit_commit[118.0]*unit_min_dispatch[118.0])
		m.addConstr(unit_commit[121.0]*unit_dispatch[121.0] >= unit_commit[121.0]*unit_min_dispatch[121.0])
		m.addConstr(unit_commit[122.0]*unit_dispatch[122.0] >= unit_commit[122.0]*unit_min_dispatch[122.0])
		m.addConstr(unit_commit[222.0]*unit_dispatch[222.0] >= unit_commit[222.0]*unit_min_dispatch[222.0])
		m.addConstr(unit_commit[322.0]*unit_dispatch[322.0] >= unit_commit[322.0]*unit_min_dispatch[322.0])
		m.addConstr(unit_commit[422.0]*unit_dispatch[422.0] >= unit_commit[422.0]*unit_min_dispatch[422.0])
		m.addConstr(unit_commit[522.0]*unit_dispatch[522.0] >= unit_commit[522.0]*unit_min_dispatch[522.0])
		m.addConstr(unit_commit[622.0]*unit_dispatch[622.0] >= unit_commit[622.0]*unit_min_dispatch[622.0])
		m.addConstr(unit_commit[123.0]*unit_dispatch[123.0] >= unit_commit[123.0]*unit_min_dispatch[123.0])
		m.addConstr(unit_commit[223.0]*unit_dispatch[223.0] >= unit_commit[223.0]*unit_min_dispatch[223.0])
		m.addConstr(unit_commit[323.0]*unit_dispatch[323.0] >= unit_commit[323.0]*unit_min_dispatch[323.0])

		# Minimum reserves for CAISO
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (0.05*unit_dispatch.prod(hydro_coeff)) + (0.07*unit_dispatch.prod(non_hydro_coeff)))

		# Minimum reserves for largest dispatch+reserve unit
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_dispatch[101.0] + unit_reserves[101.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_dispatch[201.0] + unit_reserves[201.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[301.0] * (unit_dispatch[301.0] + unit_reserves[301.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[401.0] * (unit_dispatch[401.0] + unit_reserves[401.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_dispatch[102.0] + unit_reserves[102.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_dispatch[202.0] + unit_reserves[202.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[302.0] * (unit_dispatch[302.0] + unit_reserves[302.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[402.0] * (unit_dispatch[402.0] + unit_reserves[402.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[107.0] * (unit_dispatch[107.0] + unit_reserves[107.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[207.0] * (unit_dispatch[207.0] + unit_reserves[207.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[307.0] * (unit_dispatch[307.0] + unit_reserves[307.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[113.0] * (unit_dispatch[113.0] + unit_reserves[113.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[213.0] * (unit_dispatch[213.0] + unit_reserves[213.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[313.0] * (unit_dispatch[313.0] + unit_reserves[313.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[115.0] * (unit_dispatch[115.0] + unit_reserves[115.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[215.0] * (unit_dispatch[215.0] + unit_reserves[215.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[315.0] * (unit_dispatch[315.0] + unit_reserves[315.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[415.0] * (unit_dispatch[415.0] + unit_reserves[415.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[515.0] * (unit_dispatch[515.0] + unit_reserves[515.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[615.0] * (unit_dispatch[615.0] + unit_reserves[615.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[116.0] * (unit_dispatch[116.0] + unit_reserves[116.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[118.0] * (unit_dispatch[118.0] + unit_reserves[118.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[121.0] * (unit_dispatch[121.0] + unit_reserves[121.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[122.0] * (unit_dispatch[122.0] + unit_reserves[122.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[222.0] * (unit_dispatch[222.0] + unit_reserves[222.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[322.0] * (unit_dispatch[322.0] + unit_reserves[322.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[422.0] * (unit_dispatch[422.0] + unit_reserves[422.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[522.0] * (unit_dispatch[522.0] + unit_reserves[522.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[622.0] * (unit_dispatch[622.0] + unit_reserves[622.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[123.0] * (unit_dispatch[123.0] + unit_reserves[123.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[223.0] * (unit_dispatch[223.0] + unit_reserves[223.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[323.0] * (unit_dispatch[323.0] + unit_reserves[323.0]))

		# Maximum reserves bounded by unit max dispatch for non-combustion units
		m.addConstrs(unit_reserves.select()[idx] <= [a*b for a,b in zip(unit_commit.select(), [i-j for i,j in zip(object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], unit_dispatch.select())]) ][idx] for idx in range(len(unit_reserves.select())) if idx not in combustion_ids)
		# Maximum reserves bounded by unit max reserve for non-combustion units
		m.addConstrs(unit_reserves.select()[idx] <= [a*b for a,b in zip(unit_commit.select(), [NUMBER_OF_MINUTES*i for i in object_generator.matrix[:, ODC.Generator.RAMP_RATE]])][idx] for idx in range(len(unit_reserves.select())) if idx not in combustion_ids)

		# Maximum reserves bounded by unit max dispatch for combustion units
		m.addConstrs(unit_reserves.select()[idx] <= [i-j for i,j in zip(object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], unit_dispatch.select())][idx] for idx in range(len(unit_reserves.select())) if idx in combustion_ids)
		# Maximum reserves boudned by unit max reserve for conbustion units
		m.addConstrs(unit_reserves.select()[idx] <= [NUMBER_OF_MINUTES*i for i in object_generator.matrix[:, ODC.Generator.RAMP_RATE]][idx] for idx in range(len(unit_reserves.select())) if idx in combustion_ids)

		m.params.outputFlag = 0
		m.optimize()

		for elem in m.getVars():
			if elem.varName[0:3] == 'u_c':
				out_u_c[float(elem.varName[4:9])] = float(elem.x)
			elif elem.varName[0:3] == 'u_d':
				out_u_d[float(elem.varName[4:9])] = float(elem.x)
			elif elem.varName[0:3] == 'u_r':
				out_u_r[float(elem.varName[4:9])] = float(elem.x)

		needed_reserves = 0.0
		for row in object_generator.matrix:
			row[ODC.Generator.OPERATIONAL_STATUS] = out_u_c[row[ODC.Generator.ID]]
			row[ODC.Generator.REAL_GENERATION] = row[ODC.Generator.OPERATIONAL_STATUS] * out_u_d[row[ODC.Generator.ID]]
			online = row[ODC.Generator.OPERATIONAL_STATUS]
			if GEN_PRIORITY_KEY[int(row[ODC.Generator.ID])] == 9:
				online = 1.0
			# actual_reserves = min(row[ODC.Generator.REAL_GENERATION_MAX_RATING] - row[ODC.Generator.REAL_GENERATION], online * NUMBER_OF_MINUTES * row[ODC.Generator.RAMP_RATE])
			if row[ODC.Generator.REAL_GENERATION] + min(row[ODC.Generator.REAL_GENERATION_MAX_RATING] - row[ODC.Generator.REAL_GENERATION], online * NUMBER_OF_MINUTES * row[ODC.Generator.RAMP_RATE]) > needed_reserves:
				needed_reserves = row[ODC.Generator.REAL_GENERATION] + min(row[ODC.Generator.REAL_GENERATION_MAX_RATING] - row[ODC.Generator.REAL_GENERATION], online * NUMBER_OF_MINUTES * row[ODC.Generator.RAMP_RATE])

		# if math.fabs(SUM_LOAD - sum(object_generator.matrix[:, ODC.Generator.REAL_GENERATION])) > 1.0:
		# 	print('total load', SUM_LOAD)
		# 	print('total gen', sum(object_generator.matrix[:,ODC.Generator.REAL_GENERATION]))

		# if actual_reserves < needed_reserves:
		# 	print('actual reserves', actual_reserves)
		# 	print('needed reserves', needed_reserves)

		return needed_reserves, sum(out_u_r.values()), out_u_r.copy()

	except gurobipy.GurobiError:
		print(gurobipy.GurobiError.message)
		print('GurobiError in Unit Dispatch')

def unit_commitment_priority_list_2(object_load, object_generator, losses, exports):

	out_u_c = {}
	out_u_d = {}
	out_u_r = {}
	unit_min_dispatch = {}
	unti_commit = {}

	obj_coeff_list = []
	hydro_coeff_list = []
	non_hydro_coeff_list = []
	combustion_ids = []

	combustion_id_counter = 0
	for unit_id in object_generator.matrix[:, ODC.Generator.ID]:
		obj_coeff_list.append(GEN_PRIORITY_KEY[int(unit_id)])

		if GEN_PRIORITY_KEY[int(unit_id)] == 9:
			combustion_ids.append(combustion_id_counter)
		if GEN_PRIORITY_KEY[int(unit_id)] == 1: # hydro units
			hydro_coeff_list.append(1.0)
			non_hydro_coeff_list.append(0.0)
		else: # non hydro units
			hydro_coeff_list.append(0.0)
			non_hydro_coeff_list.append(1.0)

		combustion_id_counter += 1

	unit_water_consumption = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], object_generator.matrix[:, ODC.Generator.WATER_CONSUMPTION])}
	obj_coeff = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], obj_coeff_list)}
	# coefficient with ones for hydro units only
	hydro_coeff = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], hydro_coeff_list)}
	# coefficients with ones for non-hydro units only
	non_hydro_coeff = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], non_hydro_coeff_list)}

	for row in object_generator.matrix:
		unit_min_dispatch[row[ODC.Generator.ID]] = row[ODC.Generator.REAL_GENERATION_MIN_RATING]
		unit_commit[row[ODC.Generator.ID]] == row[ODC.Generator.OPERATIONAL_STATUS]

	SUM_LOAD = float(sum(object_load.matrix[:, ODC.Load.REAL_LOAD]) + sum(object_load.matrix[:, ODC.Load.INTERCONNECTION_LOAD]))
	losses = float(losses)
	exports = float(exports)

	try:
		m = gurobipy.Model('mip1')

		unit_dispatch = m.addVars(object_generator.matrix[:, ODC.Generator.ID], lb=0.0, ub=object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], vtype=GRB.CONTINUOUS, name='u_d')
		unit_reserves = m.addVars(object_generator.matrix[:, ODC.Generator.ID], lb=0.0, ub=(NUMBER_OF_MINUTES * object_generator.matrix[:, ODC.Generator.RAMP_RATE]), vtype=GRB.CONTINUOUS, name='u_r')

		# Minimizes priority list
		m.setObjective(unit_commit[101.0]*unit_dispatch[101.0]*obj_coeff[101.0] + 
			unit_commit[201.0]*unit_dispatch[201.0]*obj_coeff[201.0] + 
			unit_commit[301.0]*unit_dispatch[301.0]*obj_coeff[301.0] + 
			unit_commit[401.0]*unit_dispatch[401.0]*obj_coeff[401.0] + 
			unit_commit[102.0]*unit_dispatch[102.0]*obj_coeff[102.0] + 
			unit_commit[202.0]*unit_dispatch[202.0]*obj_coeff[202.0] + 
			unit_commit[302.0]*unit_dispatch[302.0]*obj_coeff[302.0] + 
			unit_commit[402.0]*unit_dispatch[402.0]*obj_coeff[402.0] + 
			unit_commit[107.0]*unit_dispatch[107.0]*obj_coeff[107.0] + 
			unit_commit[207.0]*unit_dispatch[207.0]*obj_coeff[207.0] + 
			unit_commit[307.0]*unit_dispatch[307.0]*obj_coeff[307.0] + 
			unit_commit[113.0]*unit_dispatch[113.0]*obj_coeff[113.0] + 
			unit_commit[213.0]*unit_dispatch[213.0]*obj_coeff[213.0] + 
			unit_commit[313.0]*unit_dispatch[313.0]*obj_coeff[313.0] + 
			unit_commit[115.0]*unit_dispatch[115.0]*obj_coeff[115.0] + 
			unit_commit[215.0]*unit_dispatch[215.0]*obj_coeff[215.0] + 
			unit_commit[315.0]*unit_dispatch[315.0]*obj_coeff[315.0] + 
			unit_commit[415.0]*unit_dispatch[415.0]*obj_coeff[415.0] + 
			unit_commit[515.0]*unit_dispatch[515.0]*obj_coeff[515.0] + 
			unit_commit[615.0]*unit_dispatch[615.0]*obj_coeff[615.0] + 
			unit_commit[116.0]*unit_dispatch[116.0]*obj_coeff[116.0] + 
			unit_commit[118.0]*unit_dispatch[118.0]*obj_coeff[118.0] + 
			unit_commit[121.0]*unit_dispatch[121.0]*obj_coeff[121.0] + 
			unit_commit[122.0]*unit_dispatch[122.0]*obj_coeff[122.0] + 
			unit_commit[222.0]*unit_dispatch[222.0]*obj_coeff[222.0] + 
			unit_commit[322.0]*unit_dispatch[322.0]*obj_coeff[322.0] + 
			unit_commit[422.0]*unit_dispatch[422.0]*obj_coeff[422.0] + 
			unit_commit[522.0]*unit_dispatch[522.0]*obj_coeff[522.0] + 
			unit_commit[622.0]*unit_dispatch[622.0]*obj_coeff[622.0] + 
			unit_commit[123.0]*unit_dispatch[123.0]*obj_coeff[123.0] + 
			unit_commit[223.0]*unit_dispatch[223.0]*obj_coeff[223.0] + 
			unit_commit[323.0]*unit_dispatch[323.0]*obj_coeff[323.0], GRB.MINIMIZE)

		# Balances Gen~Load
		m.addConstr(SUM_LOAD+losses+exports - 0.01 <= unit_commit[101.0]*unit_dispatch[101.0] + 
			unit_commit[201.0]*unit_dispatch[201.0] + 
			unit_commit[301.0]*unit_dispatch[301.0] + 
			unit_commit[401.0]*unit_dispatch[401.0] + 
			unit_commit[102.0]*unit_dispatch[102.0] + 
			unit_commit[202.0]*unit_dispatch[202.0] + 
			unit_commit[302.0]*unit_dispatch[302.0] + 
			unit_commit[402.0]*unit_dispatch[402.0] + 
			unit_commit[107.0]*unit_dispatch[107.0] + 
			unit_commit[207.0]*unit_dispatch[207.0] + 
			unit_commit[307.0]*unit_dispatch[307.0] + 
			unit_commit[113.0]*unit_dispatch[113.0] + 
			unit_commit[213.0]*unit_dispatch[213.0] + 
			unit_commit[313.0]*unit_dispatch[313.0] + 
			unit_commit[115.0]*unit_dispatch[115.0] + 
			unit_commit[215.0]*unit_dispatch[215.0] + 
			unit_commit[315.0]*unit_dispatch[315.0] + 
			unit_commit[415.0]*unit_dispatch[415.0] + 
			unit_commit[515.0]*unit_dispatch[515.0] + 
			unit_commit[615.0]*unit_dispatch[615.0] + 
			unit_commit[116.0]*unit_dispatch[116.0] + 
			unit_commit[118.0]*unit_dispatch[118.0] + 
			unit_commit[121.0]*unit_dispatch[121.0] + 
			unit_commit[122.0]*unit_dispatch[122.0] + 
			unit_commit[222.0]*unit_dispatch[222.0] + 
			unit_commit[322.0]*unit_dispatch[322.0] + 
			unit_commit[422.0]*unit_dispatch[422.0] + 
			unit_commit[522.0]*unit_dispatch[522.0] + 
			unit_commit[622.0]*unit_dispatch[622.0] + 
			unit_commit[123.0]*unit_dispatch[123.0] + 
			unit_commit[223.0]*unit_dispatch[223.0] + 
			unit_commit[323.0]*unit_dispatch[323.0])
		m.addConstr(SUM_LOAD+losses+exports + 0.01 >= unit_commit[101.0]*unit_dispatch[101.0] + 
			unit_commit[201.0]*unit_dispatch[201.0] + 
			unit_commit[301.0]*unit_dispatch[301.0] + 
			unit_commit[401.0]*unit_dispatch[401.0] + 
			unit_commit[102.0]*unit_dispatch[102.0] + 
			unit_commit[202.0]*unit_dispatch[202.0] + 
			unit_commit[302.0]*unit_dispatch[302.0] + 
			unit_commit[402.0]*unit_dispatch[402.0] + 
			unit_commit[107.0]*unit_dispatch[107.0] + 
			unit_commit[207.0]*unit_dispatch[207.0] + 
			unit_commit[307.0]*unit_dispatch[307.0] + 
			unit_commit[113.0]*unit_dispatch[113.0] + 
			unit_commit[213.0]*unit_dispatch[213.0] + 
			unit_commit[313.0]*unit_dispatch[313.0] + 
			unit_commit[115.0]*unit_dispatch[115.0] + 
			unit_commit[215.0]*unit_dispatch[215.0] + 
			unit_commit[315.0]*unit_dispatch[315.0] + 
			unit_commit[415.0]*unit_dispatch[415.0] + 
			unit_commit[515.0]*unit_dispatch[515.0] + 
			unit_commit[615.0]*unit_dispatch[615.0] + 
			unit_commit[116.0]*unit_dispatch[116.0] + 
			unit_commit[118.0]*unit_dispatch[118.0] + 
			unit_commit[121.0]*unit_dispatch[121.0] + 
			unit_commit[122.0]*unit_dispatch[122.0] + 
			unit_commit[222.0]*unit_dispatch[222.0] + 
			unit_commit[322.0]*unit_dispatch[322.0] + 
			unit_commit[422.0]*unit_dispatch[422.0] + 
			unit_commit[522.0]*unit_dispatch[522.0] + 
			unit_commit[622.0]*unit_dispatch[622.0] + 
			unit_commit[123.0]*unit_dispatch[123.0] + 
			unit_commit[223.0]*unit_dispatch[223.0] + 
			unit_commit[323.0]*unit_dispatch[323.0])

		# Bounds unit dispatch with minimum dispatch
		m.addConstr(unit_commit[101.0]*unit_dispatch[101.0] >= unit_commit[101.0]*unit_min_dispatch[101.0])
		m.addConstr(unit_commit[201.0]*unit_dispatch[201.0] >= unit_commit[201.0]*unit_min_dispatch[201.0])
		m.addConstr(unit_commit[301.0]*unit_dispatch[301.0] >= unit_commit[301.0]*unit_min_dispatch[301.0])
		m.addConstr(unit_commit[401.0]*unit_dispatch[401.0] >= unit_commit[401.0]*unit_min_dispatch[401.0])
		m.addConstr(unit_commit[102.0]*unit_dispatch[102.0] >= unit_commit[102.0]*unit_min_dispatch[102.0])
		m.addConstr(unit_commit[202.0]*unit_dispatch[202.0] >= unit_commit[202.0]*unit_min_dispatch[202.0])
		m.addConstr(unit_commit[302.0]*unit_dispatch[302.0] >= unit_commit[302.0]*unit_min_dispatch[302.0])
		m.addConstr(unit_commit[402.0]*unit_dispatch[402.0] >= unit_commit[402.0]*unit_min_dispatch[402.0])
		m.addConstr(unit_commit[107.0]*unit_dispatch[107.0] >= unit_commit[107.0]*unit_min_dispatch[107.0])
		m.addConstr(unit_commit[207.0]*unit_dispatch[207.0] >= unit_commit[207.0]*unit_min_dispatch[207.0])
		m.addConstr(unit_commit[307.0]*unit_dispatch[307.0] >= unit_commit[307.0]*unit_min_dispatch[307.0])
		m.addConstr(unit_commit[113.0]*unit_dispatch[113.0] >= unit_commit[113.0]*unit_min_dispatch[113.0])
		m.addConstr(unit_commit[213.0]*unit_dispatch[213.0] >= unit_commit[213.0]*unit_min_dispatch[213.0])
		m.addConstr(unit_commit[313.0]*unit_dispatch[313.0] >= unit_commit[313.0]*unit_min_dispatch[313.0])
		m.addConstr(unit_commit[115.0]*unit_dispatch[115.0] >= unit_commit[115.0]*unit_min_dispatch[115.0])
		m.addConstr(unit_commit[215.0]*unit_dispatch[215.0] >= unit_commit[215.0]*unit_min_dispatch[215.0])
		m.addConstr(unit_commit[315.0]*unit_dispatch[315.0] >= unit_commit[315.0]*unit_min_dispatch[315.0])
		m.addConstr(unit_commit[415.0]*unit_dispatch[415.0] >= unit_commit[415.0]*unit_min_dispatch[415.0])
		m.addConstr(unit_commit[515.0]*unit_dispatch[515.0] >= unit_commit[515.0]*unit_min_dispatch[515.0])
		m.addConstr(unit_commit[615.0]*unit_dispatch[615.0] >= unit_commit[615.0]*unit_min_dispatch[615.0])
		m.addConstr(unit_commit[116.0]*unit_dispatch[116.0] >= unit_commit[116.0]*unit_min_dispatch[116.0])
		m.addConstr(unit_commit[118.0]*unit_dispatch[118.0] >= unit_commit[118.0]*unit_min_dispatch[118.0])
		m.addConstr(unit_commit[121.0]*unit_dispatch[121.0] >= unit_commit[121.0]*unit_min_dispatch[121.0])
		m.addConstr(unit_commit[122.0]*unit_dispatch[122.0] >= unit_commit[122.0]*unit_min_dispatch[122.0])
		m.addConstr(unit_commit[222.0]*unit_dispatch[222.0] >= unit_commit[222.0]*unit_min_dispatch[222.0])
		m.addConstr(unit_commit[322.0]*unit_dispatch[322.0] >= unit_commit[322.0]*unit_min_dispatch[322.0])
		m.addConstr(unit_commit[422.0]*unit_dispatch[422.0] >= unit_commit[422.0]*unit_min_dispatch[422.0])
		m.addConstr(unit_commit[522.0]*unit_dispatch[522.0] >= unit_commit[522.0]*unit_min_dispatch[522.0])
		m.addConstr(unit_commit[622.0]*unit_dispatch[622.0] >= unit_commit[622.0]*unit_min_dispatch[622.0])
		m.addConstr(unit_commit[123.0]*unit_dispatch[123.0] >= unit_commit[123.0]*unit_min_dispatch[123.0])
		m.addConstr(unit_commit[223.0]*unit_dispatch[223.0] >= unit_commit[223.0]*unit_min_dispatch[223.0])
		m.addConstr(unit_commit[323.0]*unit_dispatch[323.0] >= unit_commit[323.0]*unit_min_dispatch[323.0])

		# Minimum reserves for CAISO
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (0.05*unit_dispatch.prod(hydro_coeff)) + (0.07*unit_dispatch.prod(non_hydro_coeff)))

		# Minimum reserves for largest dispatch+reserve unit
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_dispatch[101.0] + unit_reserves[101.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_dispatch[201.0] + unit_reserves[201.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[301.0] * (unit_dispatch[301.0] + unit_reserves[301.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[401.0] * (unit_dispatch[401.0] + unit_reserves[401.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_dispatch[102.0] + unit_reserves[102.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_dispatch[202.0] + unit_reserves[202.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[302.0] * (unit_dispatch[302.0] + unit_reserves[302.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[402.0] * (unit_dispatch[402.0] + unit_reserves[402.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[107.0] * (unit_dispatch[107.0] + unit_reserves[107.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[207.0] * (unit_dispatch[207.0] + unit_reserves[207.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[307.0] * (unit_dispatch[307.0] + unit_reserves[307.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[113.0] * (unit_dispatch[113.0] + unit_reserves[113.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[213.0] * (unit_dispatch[213.0] + unit_reserves[213.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[313.0] * (unit_dispatch[313.0] + unit_reserves[313.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[115.0] * (unit_dispatch[115.0] + unit_reserves[115.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[215.0] * (unit_dispatch[215.0] + unit_reserves[215.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[315.0] * (unit_dispatch[315.0] + unit_reserves[315.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[415.0] * (unit_dispatch[415.0] + unit_reserves[415.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[515.0] * (unit_dispatch[515.0] + unit_reserves[515.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[615.0] * (unit_dispatch[615.0] + unit_reserves[615.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[116.0] * (unit_dispatch[116.0] + unit_reserves[116.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[118.0] * (unit_dispatch[118.0] + unit_reserves[118.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[121.0] * (unit_dispatch[121.0] + unit_reserves[121.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[122.0] * (unit_dispatch[122.0] + unit_reserves[122.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[222.0] * (unit_dispatch[222.0] + unit_reserves[222.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[322.0] * (unit_dispatch[322.0] + unit_reserves[322.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[422.0] * (unit_dispatch[422.0] + unit_reserves[422.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[522.0] * (unit_dispatch[522.0] + unit_reserves[522.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[622.0] * (unit_dispatch[622.0] + unit_reserves[622.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[123.0] * (unit_dispatch[123.0] + unit_reserves[123.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[223.0] * (unit_dispatch[223.0] + unit_reserves[223.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[323.0] * (unit_dispatch[323.0] + unit_reserves[323.0]))

		# Maximum reserves bounded by unit max dispatch for non-combustion units
		m.addConstrs(unit_reserves.select()[idx] <= [a*b for a,b in zip(unit_commit.select(), [i-j for i,j in zip(object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], unit_dispatch.select())]) ][idx] for idx in range(len(unit_reserves.select())) if idx not in combustion_ids)
		# Maximum reserves bounded by unit max reserve for non-combustion units
		m.addConstrs(unit_reserves.select()[idx] <= [a*b for a,b in zip(unit_commit.select(), [NUMBER_OF_MINUTES*i for i in object_generator.matrix[:, ODC.Generator.RAMP_RATE]])][idx] for idx in range(len(unit_reserves.select())) if idx not in combustion_ids)

		# Maximum reserves bounded by unit max dispatch for combustion units
		m.addConstrs(unit_reserves.select()[idx] <= [i-j for i,j in zip(object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], unit_dispatch.select())][idx] for idx in range(len(unit_reserves.select())) if idx in combustion_ids)
		# Maximum reserves boudned by unit max reserve for conbustion units
		m.addConstrs(unit_reserves.select()[idx] <= [NUMBER_OF_MINUTES*i for i in object_generator.matrix[:, ODC.Generator.RAMP_RATE]][idx] for idx in range(len(unit_reserves.select())) if idx in combustion_ids)

		m.params.outputFlag = 0
		m.optimize()

		for elem in m.getVars():
			if elem.varName[0:3] == 'u_d':
				out_u_d[float(elem.varName[4:9])] = float(elem.x)
			elif elem.varName[0:3] == 'u_r':
				out_u_r[float(elem.varName[4:9])] = float(elem.x)

		needed_reserves = 0.0
		for row in object_generator.matrix:
			row[ODC.Generator.OPERATIONAL_STATUS] = unit_commit[row[ODC.Generator.ID]]
			row[ODC.Generator.REAL_GENERATION] = row[ODC.Generator.OPERATIONAL_STATUS] * out_u_d[row[ODC.Generator.ID]]
			online = row[ODC.Generator.OPERATIONAL_STATUS]
			if GEN_PRIORITY_KEY[int(row[ODC.Generator.ID])] == 9:
				online = 1.0
			# actual_reserves += min(row[ODC.Generator.REAL_GENERATION_MAX_RATING] - row[ODC.Generator.REAL_GENERATION], online * NUMBER_OF_MINUTES * row[ODC.Generator.RAMP_RATE])
			if row[ODC.Generator.REAL_GENERATION] + min(row[ODC.Generator.REAL_GENERATION_MAX_RATING] - row[ODC.Generator.REAL_GENERATION], online * NUMBER_OF_MINUTES * row[ODC.Generator.RAMP_RATE]) > needed_reserves:
				needed_reserves = row[ODC.Generator.REAL_GENERATION] + min(row[ODC.Generator.REAL_GENERATION_MAX_RATING] - row[ODC.Generator.REAL_GENERATION], online * NUMBER_OF_MINUTES * row[ODC.Generator.RAMP_RATE])

		# if math.fabs(SUM_LOAD - sum(object_generator.matrix[:, ODC.Generator.REAL_GENERATION])) > 1.0:
		# 	print('total load', SUM_LOAD)
		# 	print('total gen', sum(object_generator.matrix[:,ODC.Generator.REAL_GENERATION]))

		# if actual_reserves < needed_reserves:
		# 	print('actual reserves', actual_reserves)
		# 	print('needed reserves', needed_reserves)

		return needed_reserves, sum(out_u_r.values()), out_u_r.copy()

	except gurobipy.GurobiError:
		print(gurobipy.GurobiError.message)
		print('GurobiError in Unit Dispatch')


def unit_commitment_priority_list_water(object_load, object_generator, losses, exports, node_list_constraint, node_water_constraint):

	out_u_c = {}
	out_u_d = {}
	out_u_r = {}
	unit_min_dispatch = {}
	unit_water_consumption = {}

	obj_coeff_list = []
	hydro_coeff_list = []
	non_hydro_coeff_list = []
	combustion_ids = []

	unit_to_junction_ids = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], object_generator.matrix[:, ODC.Generator.JUNCTION_ID])}
	GEN_PRIORITY_KEY_COPY = GEN_PRIORITY_KEY
	for elem in GEN_PRIORITY_KEY_COPY:
		if elem == 101 or elem == 102 or elem == 201 or elem == 202:
			pass
		elif unit_to_junction_ids[float(elem)] in node_list_constraint:
			GEN_PRIORITY_KEY_COPY[elem] = 10
		else:
			pass

	combustion_id_counter = 0
	for unit_id in object_generator.matrix[:, ODC.Generator.ID]:
		obj_coeff_list.append(GEN_PRIORITY_KEY_COPY[int(unit_id)])

		if GEN_PRIORITY_KEY_COPY[int(unit_id)] == 9:
			combustion_ids.append(combustion_id_counter)
		if GEN_PRIORITY_KEY_COPY[int(unit_id)] == 1: # hydro units
			hydro_coeff_list.append(1.0)
			non_hydro_coeff_list.append(0.0)
		else: # non hydro units
			hydro_coeff_list.append(0.0)
			non_hydro_coeff_list.append(1.0)

		combustion_id_counter += 1

	unit_water_consumption = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], object_generator.matrix[:, ODC.Generator.WATER_CONSUMPTION])}
	obj_coeff = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], obj_coeff_list)}
	# coefficient with ones for hydro units only
	hydro_coeff = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], hydro_coeff_list)}
	# coefficients with ones for non-hydro units only
	non_hydro_coeff = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], non_hydro_coeff_list)}

	for row in object_generator.matrix:
		unit_min_dispatch[row[ODC.Generator.ID]] = row[ODC.Generator.REAL_GENERATION_MIN_RATING]

	SUM_LOAD = float(sum(object_load.matrix[:, ODC.Load.REAL_LOAD]) + sum(object_load.matrix[:, ODC.Load.INTERCONNECTION_LOAD]))
	losses = float(losses)
	exports = float(exports)

	try:
		m = gurobipy.Model('mip1')

		unit_dispatch = m.addVars(object_generator.matrix[:, ODC.Generator.ID], lb=0.0, ub=object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], vtype=GRB.CONTINUOUS, name='u_d')
		unit_commit = m.addVars(object_generator.matrix[:, ODC.Generator.ID], lb=0.0, ub=1.0, vtype=GRB.BINARY, name='u_c')
		unit_reserves = m.addVars(object_generator.matrix[:, ODC.Generator.ID], lb=0.0, ub=(NUMBER_OF_MINUTES * object_generator.matrix[:, ODC.Generator.RAMP_RATE]), vtype=GRB.CONTINUOUS, name='u_r')

		# Minimizes priority list
		m.setObjective(unit_commit[101.0]*unit_dispatch[101.0]*obj_coeff[101.0] + 
			unit_commit[201.0]*unit_dispatch[201.0]*obj_coeff[201.0] + 
			unit_commit[301.0]*unit_dispatch[301.0]*obj_coeff[301.0] + 
			unit_commit[401.0]*unit_dispatch[401.0]*obj_coeff[401.0] + 
			unit_commit[102.0]*unit_dispatch[102.0]*obj_coeff[102.0] + 
			unit_commit[202.0]*unit_dispatch[202.0]*obj_coeff[202.0] + 
			unit_commit[302.0]*unit_dispatch[302.0]*obj_coeff[302.0] + 
			unit_commit[402.0]*unit_dispatch[402.0]*obj_coeff[402.0] + 
			unit_commit[107.0]*unit_dispatch[107.0]*obj_coeff[107.0] + 
			unit_commit[207.0]*unit_dispatch[207.0]*obj_coeff[207.0] + 
			unit_commit[307.0]*unit_dispatch[307.0]*obj_coeff[307.0] + 
			unit_commit[113.0]*unit_dispatch[113.0]*obj_coeff[113.0] + 
			unit_commit[213.0]*unit_dispatch[213.0]*obj_coeff[213.0] + 
			unit_commit[313.0]*unit_dispatch[313.0]*obj_coeff[313.0] + 
			unit_commit[115.0]*unit_dispatch[115.0]*obj_coeff[115.0] + 
			unit_commit[215.0]*unit_dispatch[215.0]*obj_coeff[215.0] + 
			unit_commit[315.0]*unit_dispatch[315.0]*obj_coeff[315.0] + 
			unit_commit[415.0]*unit_dispatch[415.0]*obj_coeff[415.0] + 
			unit_commit[515.0]*unit_dispatch[515.0]*obj_coeff[515.0] + 
			unit_commit[615.0]*unit_dispatch[615.0]*obj_coeff[615.0] + 
			unit_commit[116.0]*unit_dispatch[116.0]*obj_coeff[116.0] + 
			unit_commit[118.0]*unit_dispatch[118.0]*obj_coeff[118.0] + 
			unit_commit[121.0]*unit_dispatch[121.0]*obj_coeff[121.0] + 
			unit_commit[122.0]*unit_dispatch[122.0]*obj_coeff[122.0] + 
			unit_commit[222.0]*unit_dispatch[222.0]*obj_coeff[222.0] + 
			unit_commit[322.0]*unit_dispatch[322.0]*obj_coeff[322.0] + 
			unit_commit[422.0]*unit_dispatch[422.0]*obj_coeff[422.0] + 
			unit_commit[522.0]*unit_dispatch[522.0]*obj_coeff[522.0] + 
			unit_commit[622.0]*unit_dispatch[622.0]*obj_coeff[622.0] + 
			unit_commit[123.0]*unit_dispatch[123.0]*obj_coeff[123.0] + 
			unit_commit[223.0]*unit_dispatch[223.0]*obj_coeff[223.0] + 
			unit_commit[323.0]*unit_dispatch[323.0]*obj_coeff[323.0], GRB.MINIMIZE)

		# Balances Gen~Load
		m.addConstr(SUM_LOAD+losses+exports - 0.01 <= unit_commit[101.0]*unit_dispatch[101.0] + 
			unit_commit[201.0]*unit_dispatch[201.0] + 
			unit_commit[301.0]*unit_dispatch[301.0] + 
			unit_commit[401.0]*unit_dispatch[401.0] + 
			unit_commit[102.0]*unit_dispatch[102.0] + 
			unit_commit[202.0]*unit_dispatch[202.0] + 
			unit_commit[302.0]*unit_dispatch[302.0] + 
			unit_commit[402.0]*unit_dispatch[402.0] + 
			unit_commit[107.0]*unit_dispatch[107.0] + 
			unit_commit[207.0]*unit_dispatch[207.0] + 
			unit_commit[307.0]*unit_dispatch[307.0] + 
			unit_commit[113.0]*unit_dispatch[113.0] + 
			unit_commit[213.0]*unit_dispatch[213.0] + 
			unit_commit[313.0]*unit_dispatch[313.0] + 
			unit_commit[115.0]*unit_dispatch[115.0] + 
			unit_commit[215.0]*unit_dispatch[215.0] + 
			unit_commit[315.0]*unit_dispatch[315.0] + 
			unit_commit[415.0]*unit_dispatch[415.0] + 
			unit_commit[515.0]*unit_dispatch[515.0] + 
			unit_commit[615.0]*unit_dispatch[615.0] + 
			unit_commit[116.0]*unit_dispatch[116.0] + 
			unit_commit[118.0]*unit_dispatch[118.0] + 
			unit_commit[121.0]*unit_dispatch[121.0] + 
			unit_commit[122.0]*unit_dispatch[122.0] + 
			unit_commit[222.0]*unit_dispatch[222.0] + 
			unit_commit[322.0]*unit_dispatch[322.0] + 
			unit_commit[422.0]*unit_dispatch[422.0] + 
			unit_commit[522.0]*unit_dispatch[522.0] + 
			unit_commit[622.0]*unit_dispatch[622.0] + 
			unit_commit[123.0]*unit_dispatch[123.0] + 
			unit_commit[223.0]*unit_dispatch[223.0] + 
			unit_commit[323.0]*unit_dispatch[323.0])
		m.addConstr(SUM_LOAD+losses+exports + 0.01 >= unit_commit[101.0]*unit_dispatch[101.0] + 
			unit_commit[201.0]*unit_dispatch[201.0] + 
			unit_commit[301.0]*unit_dispatch[301.0] + 
			unit_commit[401.0]*unit_dispatch[401.0] + 
			unit_commit[102.0]*unit_dispatch[102.0] + 
			unit_commit[202.0]*unit_dispatch[202.0] + 
			unit_commit[302.0]*unit_dispatch[302.0] + 
			unit_commit[402.0]*unit_dispatch[402.0] + 
			unit_commit[107.0]*unit_dispatch[107.0] + 
			unit_commit[207.0]*unit_dispatch[207.0] + 
			unit_commit[307.0]*unit_dispatch[307.0] + 
			unit_commit[113.0]*unit_dispatch[113.0] + 
			unit_commit[213.0]*unit_dispatch[213.0] + 
			unit_commit[313.0]*unit_dispatch[313.0] + 
			unit_commit[115.0]*unit_dispatch[115.0] + 
			unit_commit[215.0]*unit_dispatch[215.0] + 
			unit_commit[315.0]*unit_dispatch[315.0] + 
			unit_commit[415.0]*unit_dispatch[415.0] + 
			unit_commit[515.0]*unit_dispatch[515.0] + 
			unit_commit[615.0]*unit_dispatch[615.0] + 
			unit_commit[116.0]*unit_dispatch[116.0] + 
			unit_commit[118.0]*unit_dispatch[118.0] + 
			unit_commit[121.0]*unit_dispatch[121.0] + 
			unit_commit[122.0]*unit_dispatch[122.0] + 
			unit_commit[222.0]*unit_dispatch[222.0] + 
			unit_commit[322.0]*unit_dispatch[322.0] + 
			unit_commit[422.0]*unit_dispatch[422.0] + 
			unit_commit[522.0]*unit_dispatch[522.0] + 
			unit_commit[622.0]*unit_dispatch[622.0] + 
			unit_commit[123.0]*unit_dispatch[123.0] + 
			unit_commit[223.0]*unit_dispatch[223.0] + 
			unit_commit[323.0]*unit_dispatch[323.0])

		# Bounds unit dispatch with minimum dispatch
		m.addConstr(unit_commit[101.0]*unit_dispatch[101.0] >= unit_commit[101.0]*unit_min_dispatch[101.0])
		m.addConstr(unit_commit[201.0]*unit_dispatch[201.0] >= unit_commit[201.0]*unit_min_dispatch[201.0])
		m.addConstr(unit_commit[301.0]*unit_dispatch[301.0] >= unit_commit[301.0]*unit_min_dispatch[301.0])
		m.addConstr(unit_commit[401.0]*unit_dispatch[401.0] >= unit_commit[401.0]*unit_min_dispatch[401.0])
		m.addConstr(unit_commit[102.0]*unit_dispatch[102.0] >= unit_commit[102.0]*unit_min_dispatch[102.0])
		m.addConstr(unit_commit[202.0]*unit_dispatch[202.0] >= unit_commit[202.0]*unit_min_dispatch[202.0])
		m.addConstr(unit_commit[302.0]*unit_dispatch[302.0] >= unit_commit[302.0]*unit_min_dispatch[302.0])
		m.addConstr(unit_commit[402.0]*unit_dispatch[402.0] >= unit_commit[402.0]*unit_min_dispatch[402.0])
		m.addConstr(unit_commit[107.0]*unit_dispatch[107.0] >= unit_commit[107.0]*unit_min_dispatch[107.0])
		m.addConstr(unit_commit[207.0]*unit_dispatch[207.0] >= unit_commit[207.0]*unit_min_dispatch[207.0])
		m.addConstr(unit_commit[307.0]*unit_dispatch[307.0] >= unit_commit[307.0]*unit_min_dispatch[307.0])
		m.addConstr(unit_commit[113.0]*unit_dispatch[113.0] >= unit_commit[113.0]*unit_min_dispatch[113.0])
		m.addConstr(unit_commit[213.0]*unit_dispatch[213.0] >= unit_commit[213.0]*unit_min_dispatch[213.0])
		m.addConstr(unit_commit[313.0]*unit_dispatch[313.0] >= unit_commit[313.0]*unit_min_dispatch[313.0])
		m.addConstr(unit_commit[115.0]*unit_dispatch[115.0] >= unit_commit[115.0]*unit_min_dispatch[115.0])
		m.addConstr(unit_commit[215.0]*unit_dispatch[215.0] >= unit_commit[215.0]*unit_min_dispatch[215.0])
		m.addConstr(unit_commit[315.0]*unit_dispatch[315.0] >= unit_commit[315.0]*unit_min_dispatch[315.0])
		m.addConstr(unit_commit[415.0]*unit_dispatch[415.0] >= unit_commit[415.0]*unit_min_dispatch[415.0])
		m.addConstr(unit_commit[515.0]*unit_dispatch[515.0] >= unit_commit[515.0]*unit_min_dispatch[515.0])
		m.addConstr(unit_commit[615.0]*unit_dispatch[615.0] >= unit_commit[615.0]*unit_min_dispatch[615.0])
		m.addConstr(unit_commit[116.0]*unit_dispatch[116.0] >= unit_commit[116.0]*unit_min_dispatch[116.0])
		m.addConstr(unit_commit[118.0]*unit_dispatch[118.0] >= unit_commit[118.0]*unit_min_dispatch[118.0])
		m.addConstr(unit_commit[121.0]*unit_dispatch[121.0] >= unit_commit[121.0]*unit_min_dispatch[121.0])
		m.addConstr(unit_commit[122.0]*unit_dispatch[122.0] >= unit_commit[122.0]*unit_min_dispatch[122.0])
		m.addConstr(unit_commit[222.0]*unit_dispatch[222.0] >= unit_commit[222.0]*unit_min_dispatch[222.0])
		m.addConstr(unit_commit[322.0]*unit_dispatch[322.0] >= unit_commit[322.0]*unit_min_dispatch[322.0])
		m.addConstr(unit_commit[422.0]*unit_dispatch[422.0] >= unit_commit[422.0]*unit_min_dispatch[422.0])
		m.addConstr(unit_commit[522.0]*unit_dispatch[522.0] >= unit_commit[522.0]*unit_min_dispatch[522.0])
		m.addConstr(unit_commit[622.0]*unit_dispatch[622.0] >= unit_commit[622.0]*unit_min_dispatch[622.0])
		m.addConstr(unit_commit[123.0]*unit_dispatch[123.0] >= unit_commit[123.0]*unit_min_dispatch[123.0])
		m.addConstr(unit_commit[223.0]*unit_dispatch[223.0] >= unit_commit[223.0]*unit_min_dispatch[223.0])
		m.addConstr(unit_commit[323.0]*unit_dispatch[323.0] >= unit_commit[323.0]*unit_min_dispatch[323.0])

		# Minimum reserves for CAISO
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (0.05*unit_dispatch.prod(hydro_coeff)) + (0.07*unit_dispatch.prod(non_hydro_coeff)))

		# Minimum reserves for largest dispatch+reserve unit
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_commit[101.0] * unit_dispatch[101.0] + unit_reserves[101.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_commit[201.0] * unit_dispatch[201.0] + unit_reserves[201.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[301.0] * (unit_dispatch[301.0] + unit_reserves[301.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[401.0] * (unit_dispatch[401.0] + unit_reserves[401.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_commit[102.0] * unit_dispatch[102.0] + unit_reserves[102.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_commit[202.0] * unit_dispatch[202.0] + unit_reserves[202.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[302.0] * (unit_dispatch[302.0] + unit_reserves[302.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[402.0] * (unit_dispatch[402.0] + unit_reserves[402.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[107.0] * (unit_dispatch[107.0] + unit_reserves[107.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[207.0] * (unit_dispatch[207.0] + unit_reserves[207.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[307.0] * (unit_dispatch[307.0] + unit_reserves[307.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[113.0] * (unit_dispatch[113.0] + unit_reserves[113.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[213.0] * (unit_dispatch[213.0] + unit_reserves[213.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[313.0] * (unit_dispatch[313.0] + unit_reserves[313.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[115.0] * (unit_dispatch[115.0] + unit_reserves[115.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[215.0] * (unit_dispatch[215.0] + unit_reserves[215.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[315.0] * (unit_dispatch[315.0] + unit_reserves[315.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[415.0] * (unit_dispatch[415.0] + unit_reserves[415.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[515.0] * (unit_dispatch[515.0] + unit_reserves[515.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[615.0] * (unit_dispatch[615.0] + unit_reserves[615.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[116.0] * (unit_dispatch[116.0] + unit_reserves[116.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[118.0] * (unit_dispatch[118.0] + unit_reserves[118.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[121.0] * (unit_dispatch[121.0] + unit_reserves[121.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[122.0] * (unit_dispatch[122.0] + unit_reserves[122.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[222.0] * (unit_dispatch[222.0] + unit_reserves[222.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[322.0] * (unit_dispatch[322.0] + unit_reserves[322.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[422.0] * (unit_dispatch[422.0] + unit_reserves[422.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[522.0] * (unit_dispatch[522.0] + unit_reserves[522.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[622.0] * (unit_dispatch[622.0] + unit_reserves[622.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[123.0] * (unit_dispatch[123.0] + unit_reserves[123.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[223.0] * (unit_dispatch[223.0] + unit_reserves[223.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[323.0] * (unit_dispatch[323.0] + unit_reserves[323.0]))
		
		# Minimum water consumption at the nodes
		m.addConstr(((unit_commit[101.0]*unit_dispatch[101.0]+unit_reserves[101.0])*unit_water_consumption[101.0] + (unit_commit[201.0]*unit_dispatch[201.0]+unit_reserves[201.0])*unit_water_consumption[201.0] + unit_commit[301.0]*(unit_dispatch[301.0]+unit_reserves[301.0])*unit_water_consumption[301.0] + unit_commit[401.0]*(unit_dispatch[401.0]+unit_reserves[401.0])*unit_water_consumption[401.0]) * 0.001 >= node_water_constraint[1.0])
		m.addConstr(((unit_commit[102.0]*unit_dispatch[102.0]+unit_reserves[102.0])*unit_water_consumption[102.0] + (unit_commit[202.0]*unit_dispatch[202.0]+unit_reserves[202.0])*unit_water_consumption[202.0] + unit_commit[302.0]*(unit_dispatch[302.0]+unit_reserves[302.0])*unit_water_consumption[302.0] + unit_commit[402.0]*(unit_dispatch[402.0]+unit_reserves[402.0])*unit_water_consumption[402.0]) * 0.001 >= node_water_constraint[2.0])
		m.addConstr((unit_commit[107.0]*(unit_dispatch[107.0]+unit_reserves[107.0])*unit_water_consumption[107.0] + unit_commit[207.0]*(unit_dispatch[207.0]+unit_reserves[207.0])*unit_water_consumption[207.0] + unit_commit[307.0]*(unit_dispatch[307.0]+unit_reserves[307.0])*unit_water_consumption[307.0]) * 0.001 >= node_water_constraint[7.0])
		m.addConstr((unit_commit[113.0]*(unit_dispatch[113.0]+unit_reserves[113.0])*unit_water_consumption[113.0] + unit_commit[213.0]*(unit_dispatch[213.0]+unit_reserves[213.0])*unit_water_consumption[213.0] + unit_commit[313.0]*(unit_dispatch[313.0]+unit_reserves[313.0])*unit_water_consumption[313.0]) * 0.001 >= node_water_constraint[13.0])
		m.addConstr((unit_commit[115.0]*(unit_dispatch[115.0]+unit_reserves[115.0])*unit_water_consumption[115.0] + unit_commit[215.0]*(unit_dispatch[215.0]+unit_reserves[215.0])*unit_water_consumption[215.0] + unit_commit[315.0]*(unit_dispatch[315.0]+unit_reserves[315.0])*unit_water_consumption[315.0] + unit_commit[415.0]*(unit_dispatch[415.0]+unit_reserves[415.0])*unit_water_consumption[415.0] + unit_commit[515.0]*(unit_dispatch[515.0]+unit_reserves[515.0])*unit_water_consumption[515.0] + unit_commit[615.0]*(unit_dispatch[615.0]+unit_reserves[615.0])*unit_water_consumption[615.0]) * 0.001 >= node_water_constraint[15.0])
		m.addConstr((unit_commit[116.0]*(unit_dispatch[116.0]+unit_reserves[116.0])*unit_water_consumption[116.0]) * 0.001 >= node_water_constraint[16.0])
		m.addConstr((unit_commit[118.0]*(unit_dispatch[118.0]+unit_reserves[118.0])*unit_water_consumption[118.0]+unit_commit[121.0]*(unit_dispatch[121.0]+unit_reserves[121.0])*unit_water_consumption[121.0]) * 0.001 >= node_water_constraint[18.0])
		m.addConstr((unit_commit[122.0]*(unit_dispatch[122.0]+unit_reserves[122.0])*unit_water_consumption[122.0] + unit_commit[222.0]*(unit_dispatch[222.0]+unit_reserves[222.0])*unit_water_consumption[222.0] + unit_commit[322.0]*(unit_dispatch[322.0]+unit_reserves[322.0])*unit_water_consumption[322.0] + unit_commit[422.0]*(unit_dispatch[422.0]+unit_reserves[422.0])*unit_water_consumption[422.0] + unit_commit[522.0]*(unit_dispatch[522.0]+unit_reserves[522.0])*unit_water_consumption[522.0] + unit_commit[622.0]*(unit_dispatch[622.0]+unit_reserves[622.0])*unit_water_consumption[622.0]) * 0.001 >= node_water_constraint[22.0])
		m.addConstr((unit_commit[123.0]*(unit_dispatch[123.0]+unit_reserves[123.0])*unit_water_consumption[123.0] + unit_commit[223.0]*(unit_dispatch[223.0]+unit_reserves[223.0])*unit_water_consumption[223.0] + unit_commit[323.0]*(unit_dispatch[323.0]+unit_reserves[323.0])*unit_water_consumption[323.0]) * 0.001 >= node_water_constraint[33.0])

		# Maximum reserves bounded by unit max dispatch for non-combustion units
		m.addConstrs(unit_reserves.select()[idx] <= [a*b for a,b in zip(unit_commit.select(), [i-j for i,j in zip(object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], unit_dispatch.select())]) ][idx] for idx in range(len(unit_reserves.select())) if idx not in combustion_ids)
		# Maximum reserves bounded by unit max reserve for non-combustion units
		m.addConstrs(unit_reserves.select()[idx] <= [a*b for a,b in zip(unit_commit.select(), [NUMBER_OF_MINUTES*i for i in object_generator.matrix[:, ODC.Generator.RAMP_RATE]])][idx] for idx in range(len(unit_reserves.select())) if idx not in combustion_ids)

		# Maximum reserves bounded by unit max dispatch for combustion units
		m.addConstrs(unit_reserves.select()[idx] <= [i-j for i,j in zip(object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], unit_dispatch.select())][idx] for idx in range(len(unit_reserves.select())) if idx in combustion_ids)
		# Maximum reserves boudned by unit max reserve for conbustion units
		m.addConstrs(unit_reserves.select()[idx] <= [NUMBER_OF_MINUTES*i for i in object_generator.matrix[:, ODC.Generator.RAMP_RATE]][idx] for idx in range(len(unit_reserves.select())) if idx in combustion_ids)

		m.params.outputFlag = 0
		m.optimize()

		expected_reserves = 0.0
		for elem in m.getVars():
			if elem.varName[0:3] == 'u_c':
				out_u_c[float(elem.varName[4:9])] = float(elem.x)
			elif elem.varName[0:3] == 'u_d':
				out_u_d[float(elem.varName[4:9])] = float(elem.x)
			elif elem.varName[0:3] == 'u_r':
				out_u_r[float(elem.varName[4:9])] = float(elem.x)
				expected_reserves += float(elem.x)
		# print('expected_reserves', expected_reserves)
		# print('323 dispatch', out_u_d[323.0])
		# print('323 reserves', out_u_r[323.0])

		actual_reserves = 0.0
		needed_reserves = 0.0
		for row in object_generator.matrix:
			row[ODC.Generator.OPERATIONAL_STATUS] = out_u_c[row[ODC.Generator.ID]]
			row[ODC.Generator.REAL_GENERATION] = row[ODC.Generator.OPERATIONAL_STATUS] * out_u_d[row[ODC.Generator.ID]]
			online = row[ODC.Generator.OPERATIONAL_STATUS]
			if GEN_PRIORITY_KEY_COPY[int(row[ODC.Generator.ID])] == 9:
				online = 1.0
			actual_reserves += min(row[ODC.Generator.REAL_GENERATION_MAX_RATING] - row[ODC.Generator.REAL_GENERATION], online * NUMBER_OF_MINUTES * row[ODC.Generator.RAMP_RATE])
			if row[ODC.Generator.REAL_GENERATION] + min(row[ODC.Generator.REAL_GENERATION_MAX_RATING] - row[ODC.Generator.REAL_GENERATION], online * NUMBER_OF_MINUTES * row[ODC.Generator.RAMP_RATE]) > needed_reserves:
				needed_reserves = row[ODC.Generator.REAL_GENERATION] + min(row[ODC.Generator.REAL_GENERATION_MAX_RATING] - row[ODC.Generator.REAL_GENERATION], online * NUMBER_OF_MINUTES * row[ODC.Generator.RAMP_RATE])
				# print('largest unit', row[ODC.Generator.ID],'needs', needed_reserves)

		# if math.fabs(SUM_LOAD - sum(object_generator.matrix[:, ODC.Generator.REAL_GENERATION])) > 1.0:
		# 	print('total load', SUM_LOAD)
		# 	print('total gen', sum(object_generator.matrix[:,ODC.Generator.REAL_GENERATION]))

		if actual_reserves < needed_reserves:
			print('actual reserves', actual_reserves)
			print('needed reserves', needed_reserves)

		return needed_reserves, actual_reserves

	except gurobipy.GurobiError:
		print(gurobipy.GurobiError.message)
		print('GurobiError in Unit Dispatch')

def unit_commitment_priority_list_water_2(object_load, object_generator, losses, exports, node_list_constraint, node_water_constraint):

	out_u_c = {}
	out_u_d = {}
	out_u_r = {}
	unit_min_dispatch = {}
	unti_commit = {}

	obj_coeff_list = []
	hydro_coeff_list = []
	non_hydro_coeff_list = []
	combustion_ids = []

	unit_to_junction_ids = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], object_generator.matrix[:, ODC.Generator.JUNCTION_ID])}
	GEN_PRIORITY_KEY_COPY = GEN_PRIORITY_KEY
	for elem in GEN_PRIORITY_KEY_COPY:
		if elem == 101 or elem == 102 or elem == 201 or elem == 202:
			pass
		elif unit_to_junction_ids[float(elem)] in node_list_constraint:
			GEN_PRIORITY_KEY_COPY[elem] = 10
		else:
			pass

	combustion_id_counter = 0
	for unit_id in object_generator.matrix[:, ODC.Generator.ID]:
		obj_coeff_list.append(GEN_PRIORITY_KEY_COPY[int(unit_id)])

		if GEN_PRIORITY_KEY_COPY[int(unit_id)] == 9:
			combustion_ids.append(combustion_id_counter)
		if GEN_PRIORITY_KEY_COPY[int(unit_id)] == 1: # hydro units
			hydro_coeff_list.append(1.0)
			non_hydro_coeff_list.append(0.0)
		else: # non hydro units
			hydro_coeff_list.append(0.0)
			non_hydro_coeff_list.append(1.0)

		combustion_id_counter += 1

	unit_water_consumption = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], object_generator.matrix[:, ODC.Generator.WATER_CONSUMPTION])}
	obj_coeff = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], obj_coeff_list)}
	# coefficient with ones for hydro units only
	hydro_coeff = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], hydro_coeff_list)}
	# coefficients with ones for non-hydro units only
	non_hydro_coeff = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], non_hydro_coeff_list)}

	unit_ramp_rate = {i: j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], object_generator.matrix[:, ODC.Generator.RAMP_RATE])}
	unit_max_gen = {i: j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING])}

	for row in object_generator.matrix:
		unit_min_dispatch[row[ODC.Generator.ID]] = row[ODC.Generator.REAL_GENERATION_MIN_RATING]
		unit_commit[row[ODC.Generator.ID]] == row[ODC.Generator.OPERATIONAL_STATUS]

	SUM_LOAD = float(sum(object_load.matrix[:, ODC.Load.REAL_LOAD]) + sum(object_load.matrix[:, ODC.Load.INTERCONNECTION_LOAD]))
	losses = float(losses)
	exports = float(exports)

	try:
		m = gurobipy.Model('mip1')

		unit_dispatch = m.addVars(object_generator.matrix[:, ODC.Generator.ID], lb=0.0, ub=object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], vtype=GRB.CONTINUOUS, name='u_d')
		unit_reserves = m.addVars(object_generator.matrix[:, ODC.Generator.ID], lb=0.0, ub=(NUMBER_OF_MINUTES * object_generator.matrix[:, ODC.Generator.RAMP_RATE]), vtype=GRB.CONTINUOUS, name='u_r')

		# Minimizes priority list
		m.setObjective(unit_commit[101.0]*unit_dispatch[101.0]*obj_coeff[101.0] + 
			unit_commit[201.0]*unit_dispatch[201.0]*obj_coeff[201.0] + 
			unit_commit[301.0]*unit_dispatch[301.0]*obj_coeff[301.0] + 
			unit_commit[401.0]*unit_dispatch[401.0]*obj_coeff[401.0] + 
			unit_commit[102.0]*unit_dispatch[102.0]*obj_coeff[102.0] + 
			unit_commit[202.0]*unit_dispatch[202.0]*obj_coeff[202.0] + 
			unit_commit[302.0]*unit_dispatch[302.0]*obj_coeff[302.0] + 
			unit_commit[402.0]*unit_dispatch[402.0]*obj_coeff[402.0] + 
			unit_commit[107.0]*unit_dispatch[107.0]*obj_coeff[107.0] + 
			unit_commit[207.0]*unit_dispatch[207.0]*obj_coeff[207.0] + 
			unit_commit[307.0]*unit_dispatch[307.0]*obj_coeff[307.0] + 
			unit_commit[113.0]*unit_dispatch[113.0]*obj_coeff[113.0] + 
			unit_commit[213.0]*unit_dispatch[213.0]*obj_coeff[213.0] + 
			unit_commit[313.0]*unit_dispatch[313.0]*obj_coeff[313.0] + 
			unit_commit[115.0]*unit_dispatch[115.0]*obj_coeff[115.0] + 
			unit_commit[215.0]*unit_dispatch[215.0]*obj_coeff[215.0] + 
			unit_commit[315.0]*unit_dispatch[315.0]*obj_coeff[315.0] + 
			unit_commit[415.0]*unit_dispatch[415.0]*obj_coeff[415.0] + 
			unit_commit[515.0]*unit_dispatch[515.0]*obj_coeff[515.0] + 
			unit_commit[615.0]*unit_dispatch[615.0]*obj_coeff[615.0] + 
			unit_commit[116.0]*unit_dispatch[116.0]*obj_coeff[116.0] + 
			unit_commit[118.0]*unit_dispatch[118.0]*obj_coeff[118.0] + 
			unit_commit[121.0]*unit_dispatch[121.0]*obj_coeff[121.0] + 
			unit_commit[122.0]*unit_dispatch[122.0]*obj_coeff[122.0] + 
			unit_commit[222.0]*unit_dispatch[222.0]*obj_coeff[222.0] + 
			unit_commit[322.0]*unit_dispatch[322.0]*obj_coeff[322.0] + 
			unit_commit[422.0]*unit_dispatch[422.0]*obj_coeff[422.0] + 
			unit_commit[522.0]*unit_dispatch[522.0]*obj_coeff[522.0] + 
			unit_commit[622.0]*unit_dispatch[622.0]*obj_coeff[622.0] + 
			unit_commit[123.0]*unit_dispatch[123.0]*obj_coeff[123.0] + 
			unit_commit[223.0]*unit_dispatch[223.0]*obj_coeff[223.0] + 
			unit_commit[323.0]*unit_dispatch[323.0]*obj_coeff[323.0], GRB.MINIMIZE)

		# Balances Gen~Load
		m.addConstr(SUM_LOAD+losses+exports - 0.01 <= unit_commit[101.0]*unit_dispatch[101.0] + 
			unit_commit[201.0]*unit_dispatch[201.0] + 
			unit_commit[301.0]*unit_dispatch[301.0] + 
			unit_commit[401.0]*unit_dispatch[401.0] + 
			unit_commit[102.0]*unit_dispatch[102.0] + 
			unit_commit[202.0]*unit_dispatch[202.0] + 
			unit_commit[302.0]*unit_dispatch[302.0] + 
			unit_commit[402.0]*unit_dispatch[402.0] + 
			unit_commit[107.0]*unit_dispatch[107.0] + 
			unit_commit[207.0]*unit_dispatch[207.0] + 
			unit_commit[307.0]*unit_dispatch[307.0] + 
			unit_commit[113.0]*unit_dispatch[113.0] + 
			unit_commit[213.0]*unit_dispatch[213.0] + 
			unit_commit[313.0]*unit_dispatch[313.0] + 
			unit_commit[115.0]*unit_dispatch[115.0] + 
			unit_commit[215.0]*unit_dispatch[215.0] + 
			unit_commit[315.0]*unit_dispatch[315.0] + 
			unit_commit[415.0]*unit_dispatch[415.0] + 
			unit_commit[515.0]*unit_dispatch[515.0] + 
			unit_commit[615.0]*unit_dispatch[615.0] + 
			unit_commit[116.0]*unit_dispatch[116.0] + 
			unit_commit[118.0]*unit_dispatch[118.0] + 
			unit_commit[121.0]*unit_dispatch[121.0] + 
			unit_commit[122.0]*unit_dispatch[122.0] + 
			unit_commit[222.0]*unit_dispatch[222.0] + 
			unit_commit[322.0]*unit_dispatch[322.0] + 
			unit_commit[422.0]*unit_dispatch[422.0] + 
			unit_commit[522.0]*unit_dispatch[522.0] + 
			unit_commit[622.0]*unit_dispatch[622.0] + 
			unit_commit[123.0]*unit_dispatch[123.0] + 
			unit_commit[223.0]*unit_dispatch[223.0] + 
			unit_commit[323.0]*unit_dispatch[323.0])
		m.addConstr(SUM_LOAD+losses+exports + 0.01 >= unit_commit[101.0]*unit_dispatch[101.0] + 
			unit_commit[201.0]*unit_dispatch[201.0] + 
			unit_commit[301.0]*unit_dispatch[301.0] + 
			unit_commit[401.0]*unit_dispatch[401.0] + 
			unit_commit[102.0]*unit_dispatch[102.0] + 
			unit_commit[202.0]*unit_dispatch[202.0] + 
			unit_commit[302.0]*unit_dispatch[302.0] + 
			unit_commit[402.0]*unit_dispatch[402.0] + 
			unit_commit[107.0]*unit_dispatch[107.0] + 
			unit_commit[207.0]*unit_dispatch[207.0] + 
			unit_commit[307.0]*unit_dispatch[307.0] + 
			unit_commit[113.0]*unit_dispatch[113.0] + 
			unit_commit[213.0]*unit_dispatch[213.0] + 
			unit_commit[313.0]*unit_dispatch[313.0] + 
			unit_commit[115.0]*unit_dispatch[115.0] + 
			unit_commit[215.0]*unit_dispatch[215.0] + 
			unit_commit[315.0]*unit_dispatch[315.0] + 
			unit_commit[415.0]*unit_dispatch[415.0] + 
			unit_commit[515.0]*unit_dispatch[515.0] + 
			unit_commit[615.0]*unit_dispatch[615.0] + 
			unit_commit[116.0]*unit_dispatch[116.0] + 
			unit_commit[118.0]*unit_dispatch[118.0] + 
			unit_commit[121.0]*unit_dispatch[121.0] + 
			unit_commit[122.0]*unit_dispatch[122.0] + 
			unit_commit[222.0]*unit_dispatch[222.0] + 
			unit_commit[322.0]*unit_dispatch[322.0] + 
			unit_commit[422.0]*unit_dispatch[422.0] + 
			unit_commit[522.0]*unit_dispatch[522.0] + 
			unit_commit[622.0]*unit_dispatch[622.0] + 
			unit_commit[123.0]*unit_dispatch[123.0] + 
			unit_commit[223.0]*unit_dispatch[223.0] + 
			unit_commit[323.0]*unit_dispatch[323.0])

		# Bounds unit dispatch with minimum dispatch
		m.addConstr(unit_commit[101.0]*unit_dispatch[101.0] >= unit_commit[101.0]*unit_min_dispatch[101.0])
		m.addConstr(unit_commit[201.0]*unit_dispatch[201.0] >= unit_commit[201.0]*unit_min_dispatch[201.0])
		m.addConstr(unit_commit[301.0]*unit_dispatch[301.0] >= unit_commit[301.0]*unit_min_dispatch[301.0])
		m.addConstr(unit_commit[401.0]*unit_dispatch[401.0] >= unit_commit[401.0]*unit_min_dispatch[401.0])
		m.addConstr(unit_commit[102.0]*unit_dispatch[102.0] >= unit_commit[102.0]*unit_min_dispatch[102.0])
		m.addConstr(unit_commit[202.0]*unit_dispatch[202.0] >= unit_commit[202.0]*unit_min_dispatch[202.0])
		m.addConstr(unit_commit[302.0]*unit_dispatch[302.0] >= unit_commit[302.0]*unit_min_dispatch[302.0])
		m.addConstr(unit_commit[402.0]*unit_dispatch[402.0] >= unit_commit[402.0]*unit_min_dispatch[402.0])
		m.addConstr(unit_commit[107.0]*unit_dispatch[107.0] >= unit_commit[107.0]*unit_min_dispatch[107.0])
		m.addConstr(unit_commit[207.0]*unit_dispatch[207.0] >= unit_commit[207.0]*unit_min_dispatch[207.0])
		m.addConstr(unit_commit[307.0]*unit_dispatch[307.0] >= unit_commit[307.0]*unit_min_dispatch[307.0])
		m.addConstr(unit_commit[113.0]*unit_dispatch[113.0] >= unit_commit[113.0]*unit_min_dispatch[113.0])
		m.addConstr(unit_commit[213.0]*unit_dispatch[213.0] >= unit_commit[213.0]*unit_min_dispatch[213.0])
		m.addConstr(unit_commit[313.0]*unit_dispatch[313.0] >= unit_commit[313.0]*unit_min_dispatch[313.0])
		m.addConstr(unit_commit[115.0]*unit_dispatch[115.0] >= unit_commit[115.0]*unit_min_dispatch[115.0])
		m.addConstr(unit_commit[215.0]*unit_dispatch[215.0] >= unit_commit[215.0]*unit_min_dispatch[215.0])
		m.addConstr(unit_commit[315.0]*unit_dispatch[315.0] >= unit_commit[315.0]*unit_min_dispatch[315.0])
		m.addConstr(unit_commit[415.0]*unit_dispatch[415.0] >= unit_commit[415.0]*unit_min_dispatch[415.0])
		m.addConstr(unit_commit[515.0]*unit_dispatch[515.0] >= unit_commit[515.0]*unit_min_dispatch[515.0])
		m.addConstr(unit_commit[615.0]*unit_dispatch[615.0] >= unit_commit[615.0]*unit_min_dispatch[615.0])
		m.addConstr(unit_commit[116.0]*unit_dispatch[116.0] >= unit_commit[116.0]*unit_min_dispatch[116.0])
		m.addConstr(unit_commit[118.0]*unit_dispatch[118.0] >= unit_commit[118.0]*unit_min_dispatch[118.0])
		m.addConstr(unit_commit[121.0]*unit_dispatch[121.0] >= unit_commit[121.0]*unit_min_dispatch[121.0])
		m.addConstr(unit_commit[122.0]*unit_dispatch[122.0] >= unit_commit[122.0]*unit_min_dispatch[122.0])
		m.addConstr(unit_commit[222.0]*unit_dispatch[222.0] >= unit_commit[222.0]*unit_min_dispatch[222.0])
		m.addConstr(unit_commit[322.0]*unit_dispatch[322.0] >= unit_commit[322.0]*unit_min_dispatch[322.0])
		m.addConstr(unit_commit[422.0]*unit_dispatch[422.0] >= unit_commit[422.0]*unit_min_dispatch[422.0])
		m.addConstr(unit_commit[522.0]*unit_dispatch[522.0] >= unit_commit[522.0]*unit_min_dispatch[522.0])
		m.addConstr(unit_commit[622.0]*unit_dispatch[622.0] >= unit_commit[622.0]*unit_min_dispatch[622.0])
		m.addConstr(unit_commit[123.0]*unit_dispatch[123.0] >= unit_commit[123.0]*unit_min_dispatch[123.0])
		m.addConstr(unit_commit[223.0]*unit_dispatch[223.0] >= unit_commit[223.0]*unit_min_dispatch[223.0])
		m.addConstr(unit_commit[323.0]*unit_dispatch[323.0] >= unit_commit[323.0]*unit_min_dispatch[323.0])

		# Minimum reserves for CAISO
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (0.05*unit_dispatch.prod(hydro_coeff)) + (0.07*unit_dispatch.prod(non_hydro_coeff)))

		# Minimum reserves for largest dispatch+reserve unit
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_commit[101.0] * unit_dispatch[101.0] + unit_reserves[101.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_commit[201.0] * unit_dispatch[201.0] + unit_reserves[201.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[301.0] * (unit_dispatch[301.0] + unit_reserves[301.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[401.0] * (unit_dispatch[401.0] + unit_reserves[401.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_commit[102.0] * unit_dispatch[102.0] + unit_reserves[102.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * (unit_commit[202.0] * unit_dispatch[202.0] + unit_reserves[202.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[302.0] * (unit_dispatch[302.0] + unit_reserves[302.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[402.0] * (unit_dispatch[402.0] + unit_reserves[402.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[107.0] * (unit_dispatch[107.0] + unit_reserves[107.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[207.0] * (unit_dispatch[207.0] + unit_reserves[207.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[307.0] * (unit_dispatch[307.0] + unit_reserves[307.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[113.0] * (unit_dispatch[113.0] + unit_reserves[113.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[213.0] * (unit_dispatch[213.0] + unit_reserves[213.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[313.0] * (unit_dispatch[313.0] + unit_reserves[313.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[115.0] * (unit_dispatch[115.0] + unit_reserves[115.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[215.0] * (unit_dispatch[215.0] + unit_reserves[215.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[315.0] * (unit_dispatch[315.0] + unit_reserves[315.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[415.0] * (unit_dispatch[415.0] + unit_reserves[415.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[515.0] * (unit_dispatch[515.0] + unit_reserves[515.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[615.0] * (unit_dispatch[615.0] + unit_reserves[615.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[116.0] * (unit_dispatch[116.0] + unit_reserves[116.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[118.0] * (unit_dispatch[118.0] + unit_reserves[118.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[121.0] * (unit_dispatch[121.0] + unit_reserves[121.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[122.0] * (unit_dispatch[122.0] + unit_reserves[122.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[222.0] * (unit_dispatch[222.0] + unit_reserves[222.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[322.0] * (unit_dispatch[322.0] + unit_reserves[322.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[422.0] * (unit_dispatch[422.0] + unit_reserves[422.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[522.0] * (unit_dispatch[522.0] + unit_reserves[522.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[622.0] * (unit_dispatch[622.0] + unit_reserves[622.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[123.0] * (unit_dispatch[123.0] + unit_reserves[123.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[223.0] * (unit_dispatch[223.0] + unit_reserves[223.0]))
		m.addConstr(unit_reserves.sum() >= EXTRA_RESERVE_MARGIN * unit_commit[323.0] * (unit_dispatch[323.0] + unit_reserves[323.0]))


		m.addConstr(unit_reserves[101.0] >= lb_reserves[101.0])
		m.addConstr(unit_reserves[201.0] >= lb_reserves[201.0])
		m.addConstr(unit_reserves[301.0] >= lb_reserves[301.0])
		m.addConstr(unit_reserves[401.0] >= lb_reserves[401.0])
		m.addConstr(unit_reserves[102.0] >= lb_reserves[102.0])
		m.addConstr(unit_reserves[202.0] >= lb_reserves[202.0])
		m.addConstr(unit_reserves[302.0] >= lb_reserves[302.0])
		m.addConstr(unit_reserves[402.0] >= lb_reserves[402.0])
		m.addConstr(unit_reserves[107.0] >= lb_reserves[107.0])
		m.addConstr(unit_reserves[207.0] >= lb_reserves[207.0])
		m.addConstr(unit_reserves[307.0] >= lb_reserves[307.0])
		m.addConstr(unit_reserves[113.0] >= lb_reserves[113.0])
		m.addConstr(unit_reserves[213.0] >= lb_reserves[213.0])
		m.addConstr(unit_reserves[313.0] >= lb_reserves[313.0])
		m.addConstr(unit_reserves[115.0] >= lb_reserves[115.0])
		m.addConstr(unit_reserves[215.0] >= lb_reserves[215.0])
		m.addConstr(unit_reserves[315.0] >= lb_reserves[315.0])
		m.addConstr(unit_reserves[415.0] >= lb_reserves[415.0])
		m.addConstr(unit_reserves[515.0] >= lb_reserves[515.0])
		m.addConstr(unit_reserves[615.0] >= lb_reserves[615.0])
		m.addConstr(unit_reserves[116.0] >= lb_reserves[116.0])
		m.addConstr(unit_reserves[118.0] >= lb_reserves[118.0])
		m.addConstr(unit_reserves[121.0] >= lb_reserves[121.0])
		m.addConstr(unit_reserves[122.0] >= lb_reserves[122.0])
		m.addConstr(unit_reserves[222.0] >= lb_reserves[222.0])
		m.addConstr(unit_reserves[322.0] >= lb_reserves[322.0])
		m.addConstr(unit_reserves[422.0] >= lb_reserves[422.0])
		m.addConstr(unit_reserves[522.0] >= lb_reserves[522.0])
		m.addConstr(unit_reserves[622.0] >= lb_reserves[622.0])
		m.addConstr(unit_reserves[123.0] >= lb_reserves[123.0])
		m.addConstr(unit_reserves[223.0] >= lb_reserves[223.0])
		m.addConstr(unit_reserves[323.0] >= lb_reserves[323.0])
		m.addConstr(lb_reserves[101.0] == min_(NUMBER_OF_MINUTES*unit_ramp_rate[101.0], (unit_max_gen[101.0]-unit_dispatch[101.0])))
		m.addConstr(lb_reserves[201.0] == min_(NUMBER_OF_MINUTES*unit_ramp_rate[201.0], (unit_max_gen[201.0]-unit_dispatch[201.0])))
		m.addConstr(lb_reserves[301.0] == min_(unit_commit[301.0]*NUMBER_OF_MINUTES*unit_ramp_rate[301.0], unit_commit[301.0]*(unit_max_gen[301.0]-unit_dispatch[301.0])))
		m.addConstr(lb_reserves[401.0] == min_(unit_commit[401.0]*NUMBER_OF_MINUTES*unit_ramp_rate[401.0], unit_commit[401.0]*(unit_max_gen[401.0]-unit_dispatch[401.0])))
		m.addConstr(lb_reserves[102.0] == min_(NUMBER_OF_MINUTES*unit_ramp_rate[102.0], (unit_max_gen[102.0]-unit_dispatch[102.0])))
		m.addConstr(lb_reserves[202.0] == min_(NUMBER_OF_MINUTES*unit_ramp_rate[202.0], (unit_max_gen[202.0]-unit_dispatch[202.0])))
		m.addConstr(lb_reserves[302.0] == min_(unit_commit[302.0]*NUMBER_OF_MINUTES*unit_ramp_rate[302.0], unit_commit[302.0]*(unit_max_gen[302.0]-unit_dispatch[302.0])))
		m.addConstr(lb_reserves[402.0] == min_(unit_commit[402.0]*NUMBER_OF_MINUTES*unit_ramp_rate[402.0], unit_commit[402.0]*(unit_max_gen[402.0]-unit_dispatch[402.0])))
		m.addConstr(lb_reserves[107.0] == min_(unit_commit[107.0]*NUMBER_OF_MINUTES*unit_ramp_rate[107.0], unit_commit[107.0]*(unit_max_gen[107.0]-unit_dispatch[107.0])))
		m.addConstr(lb_reserves[207.0] == min_(unit_commit[207.0]*NUMBER_OF_MINUTES*unit_ramp_rate[207.0], unit_commit[207.0]*(unit_max_gen[207.0]-unit_dispatch[207.0])))
		m.addConstr(lb_reserves[307.0] == min_(unit_commit[307.0]*NUMBER_OF_MINUTES*unit_ramp_rate[307.0], unit_commit[307.0]*(unit_max_gen[307.0]-unit_dispatch[307.0])))
		m.addConstr(lb_reserves[113.0] == min_(unit_commit[113.0]*NUMBER_OF_MINUTES*unit_ramp_rate[113.0], unit_commit[113.0]*(unit_max_gen[113.0]-unit_dispatch[113.0])))
		m.addConstr(lb_reserves[213.0] == min_(unit_commit[213.0]*NUMBER_OF_MINUTES*unit_ramp_rate[213.0], unit_commit[213.0]*(unit_max_gen[213.0]-unit_dispatch[213.0])))
		m.addConstr(lb_reserves[313.0] == min_(unit_commit[313.0]*NUMBER_OF_MINUTES*unit_ramp_rate[313.0], unit_commit[313.0]*(unit_max_gen[313.0]-unit_dispatch[313.0])))
		m.addConstr(lb_reserves[115.0] == min_(unit_commit[115.0]*NUMBER_OF_MINUTES*unit_ramp_rate[115.0], unit_commit[115.0]*(unit_max_gen[115.0]-unit_dispatch[115.0])))
		m.addConstr(lb_reserves[215.0] == min_(unit_commit[215.0]*NUMBER_OF_MINUTES*unit_ramp_rate[215.0], unit_commit[215.0]*(unit_max_gen[215.0]-unit_dispatch[215.0])))
		m.addConstr(lb_reserves[315.0] == min_(unit_commit[315.0]*NUMBER_OF_MINUTES*unit_ramp_rate[315.0], unit_commit[315.0]*(unit_max_gen[315.0]-unit_dispatch[315.0])))
		m.addConstr(lb_reserves[415.0] == min_(unit_commit[415.0]*NUMBER_OF_MINUTES*unit_ramp_rate[415.0], unit_commit[415.0]*(unit_max_gen[415.0]-unit_dispatch[415.0])))
		m.addConstr(lb_reserves[515.0] == min_(unit_commit[515.0]*NUMBER_OF_MINUTES*unit_ramp_rate[515.0], unit_commit[515.0]*(unit_max_gen[515.0]-unit_dispatch[515.0])))
		m.addConstr(lb_reserves[615.0] == min_(unit_commit[615.0]*NUMBER_OF_MINUTES*unit_ramp_rate[615.0], unit_commit[615.0]*(unit_max_gen[615.0]-unit_dispatch[615.0])))
		m.addConstr(lb_reserves[116.0] == min_(unit_commit[116.0]*NUMBER_OF_MINUTES*unit_ramp_rate[116.0], unit_commit[116.0]*(unit_max_gen[116.0]-unit_dispatch[116.0])))
		m.addConstr(lb_reserves[118.0] == min_(unit_commit[118.0]*NUMBER_OF_MINUTES*unit_ramp_rate[118.0], unit_commit[118.0]*(unit_max_gen[118.0]-unit_dispatch[118.0])))
		m.addConstr(lb_reserves[121.0] == min_(unit_commit[121.0]*NUMBER_OF_MINUTES*unit_ramp_rate[121.0], unit_commit[121.0]*(unit_max_gen[121.0]-unit_dispatch[121.0])))
		m.addConstr(lb_reserves[122.0] == min_(unit_commit[122.0]*NUMBER_OF_MINUTES*unit_ramp_rate[122.0], unit_commit[122.0]*(unit_max_gen[122.0]-unit_dispatch[122.0])))
		m.addConstr(lb_reserves[222.0] == min_(unit_commit[222.0]*NUMBER_OF_MINUTES*unit_ramp_rate[222.0], unit_commit[222.0]*(unit_max_gen[222.0]-unit_dispatch[222.0])))
		m.addConstr(lb_reserves[322.0] == min_(unit_commit[322.0]*NUMBER_OF_MINUTES*unit_ramp_rate[322.0], unit_commit[322.0]*(unit_max_gen[322.0]-unit_dispatch[322.0])))
		m.addConstr(lb_reserves[422.0] == min_(unit_commit[422.0]*NUMBER_OF_MINUTES*unit_ramp_rate[422.0], unit_commit[422.0]*(unit_max_gen[422.0]-unit_dispatch[422.0])))
		m.addConstr(lb_reserves[522.0] == min_(unit_commit[522.0]*NUMBER_OF_MINUTES*unit_ramp_rate[522.0], unit_commit[522.0]*(unit_max_gen[522.0]-unit_dispatch[522.0])))
		m.addConstr(lb_reserves[622.0] == min_(unit_commit[622.0]*NUMBER_OF_MINUTES*unit_ramp_rate[622.0], unit_commit[622.0]*(unit_max_gen[622.0]-unit_dispatch[622.0])))
		m.addConstr(lb_reserves[123.0] == min_(unit_commit[123.0]*NUMBER_OF_MINUTES*unit_ramp_rate[123.0], unit_commit[123.0]*(unit_max_gen[123.0]-unit_dispatch[123.0])))
		m.addConstr(lb_reserves[223.0] == min_(unit_commit[223.0]*NUMBER_OF_MINUTES*unit_ramp_rate[223.0], unit_commit[223.0]*(unit_max_gen[223.0]-unit_dispatch[223.0])))
		m.addConstr(lb_reserves[323.0] == min_(unit_commit[323.0]*NUMBER_OF_MINUTES*unit_ramp_rate[323.0], unit_commit[323.0]*(unit_max_gen[323.0]-unit_dispatch[323.0])))

		# Minimum water consumption at the nodes
		m.addConstr(((unit_commit[101.0]*unit_dispatch[101.0]+unit_reserves[101.0])*unit_water_consumption[101.0] + (unit_commit[201.0]*unit_dispatch[201.0]+unit_reserves[201.0])*unit_water_consumption[201.0] + unit_commit[301.0]*(unit_dispatch[301.0]+unit_reserves[301.0])*unit_water_consumption[301.0] + unit_commit[401.0]*(unit_dispatch[401.0]+unit_reserves[401.0])*unit_water_consumption[401.0]) * 0.001 >= node_water_constraint[1.0])
		m.addConstr(((unit_commit[102.0]*unit_dispatch[102.0]+unit_reserves[102.0])*unit_water_consumption[102.0] + (unit_commit[202.0]*unit_dispatch[202.0]+unit_reserves[202.0])*unit_water_consumption[202.0] + unit_commit[302.0]*(unit_dispatch[302.0]+unit_reserves[302.0])*unit_water_consumption[302.0] + unit_commit[402.0]*(unit_dispatch[402.0]+unit_reserves[402.0])*unit_water_consumption[402.0]) * 0.001 >= node_water_constraint[2.0])
		m.addConstr((unit_commit[107.0]*(unit_dispatch[107.0]+unit_reserves[107.0])*unit_water_consumption[107.0] + unit_commit[207.0]*(unit_dispatch[207.0]+unit_reserves[207.0])*unit_water_consumption[207.0] + unit_commit[307.0]*(unit_dispatch[307.0]+unit_reserves[307.0])*unit_water_consumption[307.0]) * 0.001 >= node_water_constraint[7.0])
		m.addConstr((unit_commit[113.0]*(unit_dispatch[113.0]+unit_reserves[113.0])*unit_water_consumption[113.0] + unit_commit[213.0]*(unit_dispatch[213.0]+unit_reserves[213.0])*unit_water_consumption[213.0] + unit_commit[313.0]*(unit_dispatch[313.0]+unit_reserves[313.0])*unit_water_consumption[313.0]) * 0.001 >= node_water_constraint[13.0])
		m.addConstr((unit_commit[115.0]*(unit_dispatch[115.0]+unit_reserves[115.0])*unit_water_consumption[115.0] + unit_commit[215.0]*(unit_dispatch[215.0]+unit_reserves[215.0])*unit_water_consumption[215.0] + unit_commit[315.0]*(unit_dispatch[315.0]+unit_reserves[315.0])*unit_water_consumption[315.0] + unit_commit[415.0]*(unit_dispatch[415.0]+unit_reserves[415.0])*unit_water_consumption[415.0] + unit_commit[515.0]*(unit_dispatch[515.0]+unit_reserves[515.0])*unit_water_consumption[515.0] + unit_commit[615.0]*(unit_dispatch[615.0]+unit_reserves[615.0])*unit_water_consumption[615.0]) * 0.001 >= node_water_constraint[15.0])
		m.addConstr((unit_commit[116.0]*(unit_dispatch[116.0]+unit_reserves[116.0])*unit_water_consumption[116.0]) * 0.001 >= node_water_constraint[16.0])
		m.addConstr((unit_commit[118.0]*(unit_dispatch[118.0]+unit_reserves[118.0])*unit_water_consumption[118.0]+unit_commit[121.0]*(unit_dispatch[121.0]+unit_reserves[121.0])*unit_water_consumption[121.0]) * 0.001 >= node_water_constraint[18.0])
		m.addConstr((unit_commit[122.0]*(unit_dispatch[122.0]+unit_reserves[122.0])*unit_water_consumption[122.0] + unit_commit[222.0]*(unit_dispatch[222.0]+unit_reserves[222.0])*unit_water_consumption[222.0] + unit_commit[322.0]*(unit_dispatch[322.0]+unit_reserves[322.0])*unit_water_consumption[322.0] + unit_commit[422.0]*(unit_dispatch[422.0]+unit_reserves[422.0])*unit_water_consumption[422.0] + unit_commit[522.0]*(unit_dispatch[522.0]+unit_reserves[522.0])*unit_water_consumption[522.0] + unit_commit[622.0]*(unit_dispatch[622.0]+unit_reserves[622.0])*unit_water_consumption[622.0]) * 0.001 >= node_water_constraint[22.0])
		m.addConstr((unit_commit[123.0]*(unit_dispatch[123.0]+unit_reserves[123.0])*unit_water_consumption[123.0] + unit_commit[223.0]*(unit_dispatch[223.0]+unit_reserves[223.0])*unit_water_consumption[223.0] + unit_commit[323.0]*(unit_dispatch[323.0]+unit_reserves[323.0])*unit_water_consumption[323.0]) * 0.001 >= node_water_constraint[33.0])

		# Maximum reserves bounded by unit max dispatch for non-combustion units
		m.addConstrs(unit_reserves.select()[idx] <= [a*b for a,b in zip(unit_commit.select(), [i-j for i,j in zip(object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], unit_dispatch.select())]) ][idx] for idx in range(len(unit_reserves.select())) if idx not in combustion_ids)
		# Maximum reserves bounded by unit max reserve for non-combustion units
		m.addConstrs(unit_reserves.select()[idx] <= [a*b for a,b in zip(unit_commit.select(), [NUMBER_OF_MINUTES*i for i in object_generator.matrix[:, ODC.Generator.RAMP_RATE]])][idx] for idx in range(len(unit_reserves.select())) if idx not in combustion_ids)

		# Maximum reserves bounded by unit max dispatch for combustion units
		m.addConstrs(unit_reserves.select()[idx] <= [i-j for i,j in zip(object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], unit_dispatch.select())][idx] for idx in range(len(unit_reserves.select())) if idx in combustion_ids)
		# Maximum reserves boudned by unit max reserve for conbustion units
		m.addConstrs(unit_reserves.select()[idx] <= [NUMBER_OF_MINUTES*i for i in object_generator.matrix[:, ODC.Generator.RAMP_RATE]][idx] for idx in range(len(unit_reserves.select())) if idx in combustion_ids)

		m.params.outputFlag = 0
		m.optimize()

		for elem in m.getVars():
			if elem.varName[0:3] == 'u_d':
				out_u_d[float(elem.varName[4:9])] = float(elem.x)
			elif elem.varName[0:3] == 'u_r':
				out_u_r[float(elem.varName[4:9])] = float(elem.x)

		actual_reserves = 0.0
		needed_reserves = 0.0
		for row in object_generator.matrix:
			row[ODC.Generator.OPERATIONAL_STATUS] = unit_commit[row[ODC.Generator.ID]]
			row[ODC.Generator.REAL_GENERATION] = row[ODC.Generator.OPERATIONAL_STATUS] * out_u_d[row[ODC.Generator.ID]]
			online = row[ODC.Generator.OPERATIONAL_STATUS]
			if GEN_PRIORITY_KEY_COPY[int(row[ODC.Generator.ID])] == 9:
				online = 1.0
			actual_reserves += min(row[ODC.Generator.REAL_GENERATION_MAX_RATING] - row[ODC.Generator.REAL_GENERATION], online * NUMBER_OF_MINUTES * row[ODC.Generator.RAMP_RATE])
			if row[ODC.Generator.REAL_GENERATION] + min(row[ODC.Generator.REAL_GENERATION_MAX_RATING] - row[ODC.Generator.REAL_GENERATION], online * NUMBER_OF_MINUTES * row[ODC.Generator.RAMP_RATE]) > needed_reserves:
				needed_reserves = row[ODC.Generator.REAL_GENERATION] + min(row[ODC.Generator.REAL_GENERATION_MAX_RATING] - row[ODC.Generator.REAL_GENERATION], online * NUMBER_OF_MINUTES * row[ODC.Generator.RAMP_RATE])

		# if math.fabs(SUM_LOAD - sum(object_generator.matrix[:, ODC.Generator.REAL_GENERATION])) > 1.0:
		# 	print('total load', SUM_LOAD)
		# 	print('total gen', sum(object_generator.matrix[:,ODC.Generator.REAL_GENERATION]))

		# if actual_reserves < needed_reserves:
		# 	print('actual reserves', actual_reserves)
		# 	print('needed reserves', needed_reserves)

		return needed_reserves, actual_reserves

	except gurobipy.GurobiError:
		print(gurobipy.GurobiError.message)
		print('GurobiError in Unit Dispatch')

def contingency_response(object_load, object_generator, object_cable):

	unit_recommit = {101: 0., 201: 0., 102: 0., 202: 0.}
	unit_response = {101: 0., 201: 0., 301: 0., 401: 0., 102: 0., 202: 0., 302: 0., 402: 0., 107: 0., 207: 0., 307: 0., 113: 0., 213: 0., 313: 0., 115: 0., 215: 0., 315: 0., 415: 0., 515: 0., 615: 0., 116: 0., 118: 0., 121: 0., 122: 0., 222: 0., 322: 0., 422: 0., 522: 0., 622: 0., 123: 0., 223: 0., 323: 0}

	ptdf_tab = pd.DataFrame.from_csv('C://Users//' + os_username + '//Documents//git//RISE-power-water-ss-1phase//model_methods//dcopf_tables//ptdf.csv', header=0, index_col=0)
	lodf_tab = pd.DataFrame.from_csv('C://Users//' + os_username + '//Documents//git//RISE-power-water-ss-1phase//model_methods//dcopf_tables//lodf.csv', header=0, index_col=0)

	uc_g = {}
	r_g = {}
	P_g = {}
	P_g_min = {}
	P_g_max = {}
	MAX_RESPONSE = max(object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING])
	for row in object_generator.matrix:
		if row[ODC.Generator.OPERATIONAL_STATUS] == 0.0:
			row[ODC.Generator.REAL_GENERATION] = 0.0
		uc_g[int(row[ODC.Generator.ID])] = row[ODC.Generator.OPERATIONAL_STATUS]
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


	SUM_LOAD = float(sum(object_load.matrix[:, ODC.Load.REAL_LOAD]) + sum(object_load.matrix[:, ODC.Load.INTERCONNECTION_LOAD]))

	try:
		m = gurobipy.Model('mip1')
		
		slack = 0.1 # kW
		# slack = m.addVar(lb=0.0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='slack')

		mint = m.addVar(lb=0.0, ub=100.0, vtype=GRB.CONTINUOUS, name='mint') #minutes

		uc_101 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_101') # combustion turbine with fast start capability
		uc_201 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_201') # combustion turbine with fast start capability
		uc_102 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_102') # combustion turbine with fast start capability
		uc_202 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_202') # combustion turbine with fast start capability

		r_101 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_101') # combustion turbine with fast start capability
		r_201 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_201') # combustion turbine with fast start capability
		r_301 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_301')
		r_401 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_401')
		r_102 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_102') # combustion turbine with fast start capability
		r_202 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_202') # combustion turbine with fast start capability
		r_302 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_302')
		r_402 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_402')
		r_107 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_107')
		r_207 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_207')
		r_307 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_307')
		r_113 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_113')
		r_213 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_213')
		r_313 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_313')
		r_115 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_115')
		r_215 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_215')
		r_315 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_315')
		r_415 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_415')
		r_515 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_515')
		r_615 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_615')
		r_116 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_116')
		r_118 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_118')
		r_121 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_121')
		r_122 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_122')
		r_222 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_222')
		r_322 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_322')
		r_422 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_422')
		r_522 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_522')
		r_622 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_622')
		r_123 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_123')
		r_223 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_223')
		r_323 = m.addVar(lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='r_323')

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
		m.addConstr(uc_101*P_g[101] + r_101 >= P_g_min[101])
		m.addConstr(uc_201*P_g[201] + r_201 >= P_g_min[201])
		m.addConstr(uc_g[301]*P_g[301] + r_301 >= uc_g[301]*P_g_min[301])
		m.addConstr(uc_g[401]*P_g[401] + r_401 >= uc_g[401]*P_g_min[401])
		m.addConstr(uc_102*P_g[102] + r_102 >= P_g_min[102])
		m.addConstr(uc_202*P_g[202] + r_202 >= P_g_min[202])
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
		m.addConstr(uc_101*P_g[101] + r_101 <= P_g_max[101])
		m.addConstr(uc_201*P_g[201] + r_201 <= P_g_max[201])
		m.addConstr(uc_g[301]*P_g[301] + r_301 <= uc_g[301]*P_g_max[301])
		m.addConstr(uc_g[401]*P_g[401] + r_401 <= uc_g[401]*P_g_max[401])
		m.addConstr(uc_102*P_g[102] + r_102 <= P_g_max[102])
		m.addConstr(uc_202*P_g[202] + r_202 <= P_g_max[202])
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

		opt_results = 0.
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
				opt_results = float(elem.x)

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
			row[ODC.Generator.REAL_GENERATION] = uc_g[int(row[ODC.Generator.ID])]*row[ODC.Generator.REAL_GENERATION]
			if row[ODC.Generator.ID] == 101.0 or row[ODC.Generator.ID] == 201.0 or row[ODC.Generator.ID] == 102.0 or row[ODC.Generator.ID] == 202.0:
				uc_g[int(row[ODC.Generator.ID])] = unit_recommit[int(row[ODC.Generator.ID])]
			row[ODC.Generator.OPERATIONAL_STATUS] = uc_g[int(row[ODC.Generator.ID])]
			row[ODC.Generator.REAL_GENERATION] += row[ODC.Generator.OPERATIONAL_STATUS]*unit_response[int(row[ODC.Generator.ID])]

		# for elem in unit_response:
		# 	print(elem, unit_response[elem])

		return opt_results

	except gurobipy.GurobiError:
		print('Gurobi error reported in contignency response')

def contingency_response_water(object_load, object_generator, object_cable, node_list_constraint):

	unit_recommit = {101: 0., 201: 0., 102: 0., 202: 0.}
	unit_response = {101: 0., 201: 0., 301: 0., 401: 0., 102: 0., 202: 0., 302: 0., 402: 0., 107: 0., 207: 0., 307: 0., 113: 0., 213: 0., 313: 0., 115: 0., 215: 0., 315: 0., 415: 0., 515: 0., 615: 0., 116: 0., 118: 0., 121: 0., 122: 0., 222: 0., 322: 0., 422: 0., 522: 0., 622: 0., 123: 0., 223: 0., 323: 0}

	ptdf_tab = pd.DataFrame.from_csv('C://Users//' + os_username + '//Documents//git//RISE-power-water-ss-1phase//model_methods//dcopf_tables//ptdf.csv', header=0, index_col=0)
	lodf_tab = pd.DataFrame.from_csv('C://Users//' + os_username + '//Documents//git//RISE-power-water-ss-1phase//model_methods//dcopf_tables//lodf.csv', header=0, index_col=0)

	uc_g = {}
	r_g = {}
	P_g = {}
	P_g_min = {}
	P_g_max = {}
	MAX_RESPONSE = max(object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING])
	for row in object_generator.matrix:
		if row[ODC.Generator.OPERATIONAL_STATUS] == 0.0:
			row[ODC.Generator.REAL_GENERATION] = 0.0
		uc_g[int(row[ODC.Generator.ID])] = row[ODC.Generator.OPERATIONAL_STATUS]
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

	unit_to_junction_ids = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], object_generator.matrix[:, ODC.Generator.JUNCTION_ID])}
	u_w_cons = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], object_generator.matrix[:, ODC.Generator.WATER_CONSUMPTION])}
	u_w_fact = {i:j for i,j in zip(object_generator.matrix[:, ODC.Generator.ID], 0.0*object_generator.matrix[:, ODC.Generator.ID])}
	for elem in u_w_fact:
		if unit_to_junction_ids[elem] in node_list_constraint:
			u_w_fact[elem] = 1.0

	SUM_LOAD = float(sum(object_load.matrix[:, ODC.Load.REAL_LOAD]) + sum(object_load.matrix[:, ODC.Load.INTERCONNECTION_LOAD]))

	try:
		m = gurobipy.Model('mip1')
		
		# slack = 0.1 # kW
		slack = m.addVar(lb=0.0, ub=100.0, vtype=GRB.CONTINUOUS, name='slack')

		# mint = m.addVar(lb=0.0, ub=100.0, vtype=GRB.CONTINUOUS, name='mint') #minutes

		uc_101 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_101') # combustion turbine with fast start capability
		uc_201 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_201') # combustion turbine with fast start capability
		uc_102 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_102') # combustion turbine with fast start capability
		uc_202 = m.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name='uc_202') # combustion turbine with fast start capability

		unit_dispatch = m.addVars(object_generator.matrix[:, ODC.Generator.ID], lb=0.0, ub=object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING], vtype=GRB.CONTINUOUS, name='u_d')
		u_r = m.addVars(object_generator.matrix[:, ODC.Generator.ID], lb=-MAX_RESPONSE, ub=MAX_RESPONSE, vtype=GRB.CONTINUOUS, name='u_r')

		# Objective function
		m.setObjective(slack + uc_101*u_r[101.0]*u_w_cons[101.0]*u_w_fact[101.0] +
		uc_201*u_r[201.0]*u_w_cons[201.0]*u_w_fact[201.0] +
		uc_g[301]*u_r[301.0]*u_w_cons[301.0]*u_w_fact[301.0] +
		uc_g[401]*u_r[401.0]*u_w_cons[401.0]*u_w_fact[401.0] +
		uc_102*u_r[102.0]*u_w_cons[102.0]*u_w_fact[102.0] +
		uc_202*u_r[202.0]*u_w_cons[202.0]*u_w_fact[202.0] +
		uc_g[302]*u_r[302.0]*u_w_cons[302.0]*u_w_fact[302.0] +
		uc_g[402]*u_r[402.0]*u_w_cons[402.0]*u_w_fact[402.0] +
		uc_g[107]*u_r[107.0]*u_w_cons[107.0]*u_w_fact[107.0] +
		uc_g[207]*u_r[207.0]*u_w_cons[207.0]*u_w_fact[207.0] +
		uc_g[307]*u_r[307.0]*u_w_cons[307.0]*u_w_fact[307.0] +
		uc_g[113]*u_r[113.0]*u_w_cons[113.0]*u_w_fact[113.0] +
		uc_g[213]*u_r[213.0]*u_w_cons[213.0]*u_w_fact[213.0] +
		uc_g[313]*u_r[313.0]*u_w_cons[313.0]*u_w_fact[313.0] +
		uc_g[115]*u_r[115.0]*u_w_cons[115.0]*u_w_fact[115.0] +
		uc_g[215]*u_r[215.0]*u_w_cons[215.0]*u_w_fact[215.0] +
		uc_g[315]*u_r[315.0]*u_w_cons[315.0]*u_w_fact[315.0] +
		uc_g[415]*u_r[415.0]*u_w_cons[415.0]*u_w_fact[415.0] +
		uc_g[515]*u_r[515.0]*u_w_cons[515.0]*u_w_fact[515.0] +
		uc_g[615]*u_r[615.0]*u_w_cons[615.0]*u_w_fact[615.0] +
		uc_g[116]*u_r[116.0]*u_w_cons[116.0]*u_w_fact[116.0] +
		uc_g[118]*u_r[118.0]*u_w_cons[118.0]*u_w_fact[118.0] +
		uc_g[121]*u_r[121.0]*u_w_cons[121.0]*u_w_fact[121.0] +
		uc_g[122]*u_r[122.0]*u_w_cons[122.0]*u_w_fact[122.0] +
		uc_g[222]*u_r[222.0]*u_w_cons[222.0]*u_w_fact[222.0] +
		uc_g[322]*u_r[322.0]*u_w_cons[322.0]*u_w_fact[322.0] +
		uc_g[422]*u_r[422.0]*u_w_cons[422.0]*u_w_fact[422.0] +
		uc_g[522]*u_r[522.0]*u_w_cons[522.0]*u_w_fact[522.0] +
		uc_g[622]*u_r[622.0]*u_w_cons[622.0]*u_w_fact[622.0] +
		uc_g[123]*u_r[123.0]*u_w_cons[123.0]*u_w_fact[123.0] +
		uc_g[223]*u_r[223.0]*u_w_cons[223.0]*u_w_fact[223.0] +
		uc_g[323]*u_r[323.0]*u_w_cons[323.0]*u_w_fact[323.0], GRB.MINIMIZE)

		# Zero out imports/exports
		m.addConstr(-slack <= P_b[100] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[323][str(outage_id)]))

		m.addConstr(slack >= P_b[100] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['100'] + outage_sign * lodf_tab.loc[outage_id]['100'] * ptdf_tab.loc[323][str(outage_id)]))


		# Re-dispatch must be greater than 10-minutes of ramping down *************************************************************
		m.addConstr(u_r[101.0] >= uc_101 * (NUMBER_OF_MINUTES * -r_g[101]))
		m.addConstr(u_r[201.0] >= uc_201 * (NUMBER_OF_MINUTES * -r_g[201]))
		m.addConstr(u_r[301.0] >= uc_g[301] * (NUMBER_OF_MINUTES * -r_g[301]))
		m.addConstr(u_r[401.0] >= uc_g[401] * (NUMBER_OF_MINUTES * -r_g[401]))
		m.addConstr(u_r[102.0] >= uc_102 * (NUMBER_OF_MINUTES * -r_g[102]))
		m.addConstr(u_r[202.0] >= uc_202 * (NUMBER_OF_MINUTES * -r_g[202]))
		m.addConstr(u_r[302.0] >= uc_g[302] * (NUMBER_OF_MINUTES * -r_g[302]))
		m.addConstr(u_r[402.0] >= uc_g[402] * (NUMBER_OF_MINUTES * -r_g[402]))
		m.addConstr(u_r[107.0] >= uc_g[107] * (NUMBER_OF_MINUTES * -r_g[107]))
		m.addConstr(u_r[207.0] >= uc_g[207] * (NUMBER_OF_MINUTES * -r_g[207]))
		m.addConstr(u_r[307.0] >= uc_g[307] * (NUMBER_OF_MINUTES * -r_g[307]))
		m.addConstr(u_r[113.0] >= uc_g[113] * (NUMBER_OF_MINUTES * -r_g[113]))
		m.addConstr(u_r[213.0] >= uc_g[213] * (NUMBER_OF_MINUTES * -r_g[213]))
		m.addConstr(u_r[313.0] >= uc_g[313] * (NUMBER_OF_MINUTES * -r_g[313]))
		m.addConstr(u_r[115.0] >= uc_g[115] * (NUMBER_OF_MINUTES * -r_g[115]))
		m.addConstr(u_r[215.0] >= uc_g[215] * (NUMBER_OF_MINUTES * -r_g[215]))
		m.addConstr(u_r[315.0] >= uc_g[315] * (NUMBER_OF_MINUTES * -r_g[315]))
		m.addConstr(u_r[415.0] >= uc_g[415] * (NUMBER_OF_MINUTES * -r_g[415]))
		m.addConstr(u_r[515.0] >= uc_g[515] * (NUMBER_OF_MINUTES * -r_g[515]))
		m.addConstr(u_r[615.0] >= uc_g[615] * (NUMBER_OF_MINUTES * -r_g[615]))
		m.addConstr(u_r[116.0] >= uc_g[116] * (NUMBER_OF_MINUTES * -r_g[116]))
		m.addConstr(u_r[118.0] >= uc_g[118] * (NUMBER_OF_MINUTES * -r_g[118]))
		m.addConstr(u_r[121.0] >= uc_g[121] * (NUMBER_OF_MINUTES * -r_g[121]))
		m.addConstr(u_r[122.0] >= uc_g[122] * (NUMBER_OF_MINUTES * -r_g[122]))
		m.addConstr(u_r[222.0] >= uc_g[222] * (NUMBER_OF_MINUTES * -r_g[222]))
		m.addConstr(u_r[322.0] >= uc_g[322] * (NUMBER_OF_MINUTES * -r_g[322]))
		m.addConstr(u_r[422.0] >= uc_g[422] * (NUMBER_OF_MINUTES * -r_g[422]))
		m.addConstr(u_r[522.0] >= uc_g[522] * (NUMBER_OF_MINUTES * -r_g[522]))
		m.addConstr(u_r[622.0] >= uc_g[622] * (NUMBER_OF_MINUTES * -r_g[622]))
		m.addConstr(u_r[123.0] >= uc_g[123] * (NUMBER_OF_MINUTES * -r_g[123]))
		m.addConstr(u_r[223.0] >= uc_g[223] * (NUMBER_OF_MINUTES * -r_g[223]))
		m.addConstr(u_r[323.0] >= uc_g[323] * (NUMBER_OF_MINUTES * -r_g[323]))

		# # Re-dispatch must be less than 10-minutes of ramping up ******************************************************************
		m.addConstr(u_r[101.0] <= uc_101 * (NUMBER_OF_MINUTES * r_g[101]))
		m.addConstr(u_r[201.0] <= uc_201 * (NUMBER_OF_MINUTES * r_g[201]))
		m.addConstr(u_r[301.0] <= uc_g[301] * (NUMBER_OF_MINUTES * r_g[301]))
		m.addConstr(u_r[401.0] <= uc_g[401] * (NUMBER_OF_MINUTES * r_g[401]))
		m.addConstr(u_r[102.0] <= uc_102 * (NUMBER_OF_MINUTES * r_g[102]))
		m.addConstr(u_r[202.0] <= uc_202 * (NUMBER_OF_MINUTES * r_g[202]))
		m.addConstr(u_r[302.0] <= uc_g[302] * (NUMBER_OF_MINUTES * r_g[302]))
		m.addConstr(u_r[402.0] <= uc_g[402] * (NUMBER_OF_MINUTES * r_g[402]))
		m.addConstr(u_r[107.0] <= uc_g[107] * (NUMBER_OF_MINUTES * r_g[107]))
		m.addConstr(u_r[207.0] <= uc_g[207] * (NUMBER_OF_MINUTES * r_g[207]))
		m.addConstr(u_r[307.0] <= uc_g[307] * (NUMBER_OF_MINUTES * r_g[307]))
		m.addConstr(u_r[113.0] <= uc_g[113] * (NUMBER_OF_MINUTES * r_g[113]))
		m.addConstr(u_r[213.0] <= uc_g[213] * (NUMBER_OF_MINUTES * r_g[213]))
		m.addConstr(u_r[313.0] <= uc_g[313] * (NUMBER_OF_MINUTES * r_g[313]))
		m.addConstr(u_r[115.0] <= uc_g[115] * (NUMBER_OF_MINUTES * r_g[115]))
		m.addConstr(u_r[215.0] <= uc_g[215] * (NUMBER_OF_MINUTES * r_g[215]))
		m.addConstr(u_r[315.0] <= uc_g[315] * (NUMBER_OF_MINUTES * r_g[315]))
		m.addConstr(u_r[415.0] <= uc_g[415] * (NUMBER_OF_MINUTES * r_g[415]))
		m.addConstr(u_r[515.0] <= uc_g[515] * (NUMBER_OF_MINUTES * r_g[515]))
		m.addConstr(u_r[615.0] <= uc_g[615] * (NUMBER_OF_MINUTES * r_g[615]))
		m.addConstr(u_r[116.0] <= uc_g[116] * (NUMBER_OF_MINUTES * r_g[116]))
		m.addConstr(u_r[118.0] <= uc_g[118] * (NUMBER_OF_MINUTES * r_g[118]))
		m.addConstr(u_r[121.0] <= uc_g[121] * (NUMBER_OF_MINUTES * r_g[121]))
		m.addConstr(u_r[122.0] <= uc_g[122] * (NUMBER_OF_MINUTES * r_g[122]))
		m.addConstr(u_r[222.0] <= uc_g[222] * (NUMBER_OF_MINUTES * r_g[222]))
		m.addConstr(u_r[322.0] <= uc_g[322] * (NUMBER_OF_MINUTES * r_g[322]))
		m.addConstr(u_r[422.0] <= uc_g[422] * (NUMBER_OF_MINUTES * r_g[422]))
		m.addConstr(u_r[522.0] <= uc_g[522] * (NUMBER_OF_MINUTES * r_g[522]))
		m.addConstr(u_r[622.0] <= uc_g[622] * (NUMBER_OF_MINUTES * r_g[622]))
		m.addConstr(u_r[123.0] <= uc_g[123] * (NUMBER_OF_MINUTES * r_g[123]))
		m.addConstr(u_r[223.0] <= uc_g[223] * (NUMBER_OF_MINUTES * r_g[223]))
		m.addConstr(u_r[323.0] <= uc_g[323] * (NUMBER_OF_MINUTES * r_g[323]))

		# # Re-dispatch must be greater than minimum generation *********************************************************************
		m.addConstr(uc_101*P_g[101] + u_r[101.0] >= P_g_min[101])
		m.addConstr(uc_201*P_g[201] + u_r[201.0] >= P_g_min[201])
		m.addConstr(uc_g[301]*P_g[301] + u_r[301.0] >= uc_g[301]*P_g_min[301])
		m.addConstr(uc_g[401]*P_g[401] + u_r[401.0] >= uc_g[401]*P_g_min[401])
		m.addConstr(uc_102*P_g[102] + u_r[102.0] >= P_g_min[102])
		m.addConstr(uc_202*P_g[202] + u_r[202.0] >= P_g_min[202])
		m.addConstr(uc_g[302]*P_g[302] + u_r[302.0] >= uc_g[302]*P_g_min[302])
		m.addConstr(uc_g[402]*P_g[402] + u_r[402.0] >= uc_g[402]*P_g_min[402])
		m.addConstr(uc_g[107]*P_g[107] + u_r[107.0] >= uc_g[107]*P_g_min[107])
		m.addConstr(uc_g[207]*P_g[207] + u_r[207.0] >= uc_g[207]*P_g_min[207])
		m.addConstr(uc_g[307]*P_g[307] + u_r[307.0] >= uc_g[307]*P_g_min[307])
		m.addConstr(uc_g[113]*P_g[113] + u_r[113.0] >= uc_g[113]*P_g_min[113])
		m.addConstr(uc_g[213]*P_g[213] + u_r[213.0] >= uc_g[213]*P_g_min[213])
		m.addConstr(uc_g[313]*P_g[313] + u_r[313.0] >= uc_g[313]*P_g_min[313])
		m.addConstr(uc_g[115]*P_g[115] + u_r[115.0] >= uc_g[115]*P_g_min[115])
		m.addConstr(uc_g[215]*P_g[215] + u_r[215.0] >= uc_g[215]*P_g_min[215])
		m.addConstr(uc_g[315]*P_g[315] + u_r[315.0] >= uc_g[315]*P_g_min[315])
		m.addConstr(uc_g[415]*P_g[415] + u_r[415.0] >= uc_g[415]*P_g_min[415])
		m.addConstr(uc_g[515]*P_g[515] + u_r[515.0] >= uc_g[515]*P_g_min[515])
		m.addConstr(uc_g[615]*P_g[615] + u_r[615.0] >= uc_g[615]*P_g_min[615])
		m.addConstr(uc_g[116]*P_g[116] + u_r[116.0] >= uc_g[116]*P_g_min[116])
		m.addConstr(uc_g[118]*P_g[118] + u_r[118.0] >= uc_g[118]*P_g_min[118])
		m.addConstr(uc_g[121]*P_g[121] + u_r[121.0] >= uc_g[121]*P_g_min[121])
		m.addConstr(uc_g[122]*P_g[122] + u_r[122.0] >= uc_g[122]*P_g_min[122])
		m.addConstr(uc_g[222]*P_g[222] + u_r[222.0] >= uc_g[222]*P_g_min[222])
		m.addConstr(uc_g[322]*P_g[322] + u_r[322.0] >= uc_g[322]*P_g_min[322])
		m.addConstr(uc_g[422]*P_g[422] + u_r[422.0] >= uc_g[422]*P_g_min[422])
		m.addConstr(uc_g[522]*P_g[522] + u_r[522.0] >= uc_g[522]*P_g_min[522])
		m.addConstr(uc_g[622]*P_g[622] + u_r[622.0] >= uc_g[622]*P_g_min[622])
		m.addConstr(uc_g[123]*P_g[123] + u_r[123.0] >= uc_g[123]*P_g_min[123])
		m.addConstr(uc_g[223]*P_g[223] + u_r[223.0] >= uc_g[223]*P_g_min[223])
		m.addConstr(uc_g[323]*P_g[323] + u_r[323.0] >= uc_g[323]*P_g_min[323])

		# # # Re-dispatch must be less than maximum generation ************************************************************************
		m.addConstr(uc_101*P_g[101] + u_r[101.0] <= P_g_max[101])
		m.addConstr(uc_201*P_g[201] + u_r[201.0] <= P_g_max[201])
		m.addConstr(uc_g[301]*P_g[301] + u_r[301.0] <= uc_g[301]*P_g_max[301])
		m.addConstr(uc_g[401]*P_g[401] + u_r[401.0] <= uc_g[401]*P_g_max[401])
		m.addConstr(uc_102*P_g[102] + u_r[102.0] <= P_g_max[102])
		m.addConstr(uc_202*P_g[202] + u_r[202.0] <= P_g_max[202])
		m.addConstr(uc_g[302]*P_g[302] + u_r[302.0] <= uc_g[302]*P_g_max[302])
		m.addConstr(uc_g[402]*P_g[402] + u_r[402.0] <= uc_g[402]*P_g_max[402])
		m.addConstr(uc_g[107]*P_g[107] + u_r[107.0] <= uc_g[107]*P_g_max[107])
		m.addConstr(uc_g[207]*P_g[207] + u_r[207.0] <= uc_g[207]*P_g_max[207])
		m.addConstr(uc_g[307]*P_g[307] + u_r[307.0] <= uc_g[307]*P_g_max[307])
		m.addConstr(uc_g[113]*P_g[113] + u_r[113.0] <= uc_g[113]*P_g_max[113])
		m.addConstr(uc_g[213]*P_g[213] + u_r[213.0] <= uc_g[213]*P_g_max[213])
		m.addConstr(uc_g[313]*P_g[313] + u_r[313.0] <= uc_g[313]*P_g_max[313])
		m.addConstr(uc_g[115]*P_g[115] + u_r[115.0] <= uc_g[115]*P_g_max[115])
		m.addConstr(uc_g[215]*P_g[215] + u_r[215.0] <= uc_g[215]*P_g_max[215])
		m.addConstr(uc_g[315]*P_g[315] + u_r[315.0] <= uc_g[315]*P_g_max[315])
		m.addConstr(uc_g[415]*P_g[415] + u_r[415.0] <= uc_g[415]*P_g_max[415])
		m.addConstr(uc_g[515]*P_g[515] + u_r[515.0] <= uc_g[515]*P_g_max[515])
		m.addConstr(uc_g[615]*P_g[615] + u_r[615.0] <= uc_g[615]*P_g_max[615])
		m.addConstr(uc_g[116]*P_g[116] + u_r[116.0] <= uc_g[116]*P_g_max[116])
		m.addConstr(uc_g[118]*P_g[118] + u_r[118.0] <= uc_g[118]*P_g_max[118])
		m.addConstr(uc_g[121]*P_g[121] + u_r[121.0] <= uc_g[121]*P_g_max[121])
		m.addConstr(uc_g[122]*P_g[122] + u_r[122.0] <= uc_g[122]*P_g_max[122])
		m.addConstr(uc_g[222]*P_g[222] + u_r[222.0] <= uc_g[222]*P_g_max[222])
		m.addConstr(uc_g[322]*P_g[322] + u_r[322.0] <= uc_g[322]*P_g_max[322])
		m.addConstr(uc_g[422]*P_g[422] + u_r[422.0] <= uc_g[422]*P_g_max[422])
		m.addConstr(uc_g[522]*P_g[522] + u_r[522.0] <= uc_g[522]*P_g_max[522])
		m.addConstr(uc_g[622]*P_g[622] + u_r[622.0] <= uc_g[622]*P_g_max[622])
		m.addConstr(uc_g[123]*P_g[123] + u_r[123.0] <= uc_g[123]*P_g_max[123])
		m.addConstr(uc_g[223]*P_g[223] + u_r[223.0] <= uc_g[223]*P_g_max[223])
		m.addConstr(uc_g[323]*P_g[323] + u_r[323.0] <= uc_g[323]*P_g_max[323])

		# Branches must be less than maximum thermal limit ************************************************************************
		m.addConstr(P_b[1] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[1])

		m.addConstr(P_b[2] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[2])

		m.addConstr(P_b[3] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[3])

		m.addConstr(P_b[4] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[4])

		m.addConstr(P_b[5] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[5])

		m.addConstr(P_b[6] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[6])

		m.addConstr(P_b[7] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[7])

		m.addConstr(P_b[8] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[8])

		m.addConstr(P_b[9] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[9])

		m.addConstr(P_b[10] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[10])

		m.addConstr(P_b[11] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[11])

		m.addConstr(P_b[12] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[12])

		m.addConstr(P_b[13] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[13])

		m.addConstr(P_b[14] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[14])
	
		m.addConstr(P_b[15] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[15])
	
		m.addConstr(P_b[16] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[16])
	
		m.addConstr(P_b[17] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[17])
	
		m.addConstr(P_b[18] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[18])
	
		m.addConstr(P_b[19] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[19])
	
		m.addConstr(P_b[20] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[20])
	
		m.addConstr(P_b[21] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[21])
	
		m.addConstr(P_b[22] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[22])
	
		m.addConstr(P_b[23] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[23])
	
		m.addConstr(P_b[24] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[24])
	
		m.addConstr(P_b[25] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[25])
	
		m.addConstr(P_b[26] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[26])
	
		m.addConstr(P_b[27] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[27])
	
		m.addConstr(P_b[28] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[28])
	
		m.addConstr(P_b[29] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[29])
	
		m.addConstr(P_b[30] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[30])
	
		m.addConstr(P_b[31] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[31])
	
		m.addConstr(P_b[32] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[32])
	
		m.addConstr(P_b[33] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[323][str(outage_id)]) <= P_b_max[33])

		# # Branches must be greater than minimum thermal limit *********************************************************************
		m.addConstr(P_b[1] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['1'] + outage_sign * lodf_tab.loc[outage_id]['1'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[1])

		m.addConstr(P_b[2] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['2'] + outage_sign * lodf_tab.loc[outage_id]['2'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[2])

		m.addConstr(P_b[3] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['3'] + outage_sign * lodf_tab.loc[outage_id]['3'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[3])

		m.addConstr(P_b[4] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['4'] + outage_sign * lodf_tab.loc[outage_id]['4'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[4])

		m.addConstr(P_b[5] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['5'] + outage_sign * lodf_tab.loc[outage_id]['5'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[5])

		m.addConstr(P_b[6] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['6'] + outage_sign * lodf_tab.loc[outage_id]['6'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[6])

		m.addConstr(P_b[7] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['7'] + outage_sign * lodf_tab.loc[outage_id]['7'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[7])

		m.addConstr(P_b[8] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['8'] + outage_sign * lodf_tab.loc[outage_id]['8'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[8])

		m.addConstr(P_b[9] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['9'] + outage_sign * lodf_tab.loc[outage_id]['9'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[9])

		m.addConstr(P_b[10] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['10'] + outage_sign * lodf_tab.loc[outage_id]['10'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[10])

		m.addConstr(P_b[11] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['11'] + outage_sign * lodf_tab.loc[outage_id]['11'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[11])

		m.addConstr(P_b[12] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['12'] + outage_sign * lodf_tab.loc[outage_id]['12'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[12])

		m.addConstr(P_b[13] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['13'] + outage_sign * lodf_tab.loc[outage_id]['13'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[13])

		m.addConstr(P_b[14] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['14'] + outage_sign * lodf_tab.loc[outage_id]['14'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[14])
	
		m.addConstr(P_b[15] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['15'] + outage_sign * lodf_tab.loc[outage_id]['15'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[15])
	
		m.addConstr(P_b[16] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['16'] + outage_sign * lodf_tab.loc[outage_id]['16'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[16])
	
		m.addConstr(P_b[17] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['17'] + outage_sign * lodf_tab.loc[outage_id]['17'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[17])
	
		m.addConstr(P_b[18] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['18'] + outage_sign * lodf_tab.loc[outage_id]['18'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[18])
	
		m.addConstr(P_b[19] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['19'] + outage_sign * lodf_tab.loc[outage_id]['19'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[19])
	
		m.addConstr(P_b[20] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['20'] + outage_sign * lodf_tab.loc[outage_id]['20'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[20])
	
		m.addConstr(P_b[21] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['21'] + outage_sign * lodf_tab.loc[outage_id]['21'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[21])
	
		m.addConstr(P_b[22] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['22'] + outage_sign * lodf_tab.loc[outage_id]['22'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[22])
	
		m.addConstr(P_b[23] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['23'] + outage_sign * lodf_tab.loc[outage_id]['23'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[23])
	
		m.addConstr(P_b[24] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['24'] + outage_sign * lodf_tab.loc[outage_id]['24'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[24])
	
		m.addConstr(P_b[25] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['25'] + outage_sign * lodf_tab.loc[outage_id]['25'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[25])
	
		m.addConstr(P_b[26] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['26'] + outage_sign * lodf_tab.loc[outage_id]['26'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[26])
	
		m.addConstr(P_b[27] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['27'] + outage_sign * lodf_tab.loc[outage_id]['27'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[27])
	
		m.addConstr(P_b[28] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['28'] + outage_sign * lodf_tab.loc[outage_id]['28'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[28])
	
		m.addConstr(P_b[29] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['29'] + outage_sign * lodf_tab.loc[outage_id]['29'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[29])
	
		m.addConstr(P_b[30] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['30'] + outage_sign * lodf_tab.loc[outage_id]['30'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[30])
	
		m.addConstr(P_b[31] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['31'] + outage_sign * lodf_tab.loc[outage_id]['31'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[31])
	
		m.addConstr(P_b[32] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['32'] + outage_sign * lodf_tab.loc[outage_id]['32'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[32])
	
		m.addConstr(P_b[33] + uc_101*u_r[101.0]*(ptdf_tab.loc[101]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[101][str(outage_id)]) +
			uc_201*u_r[201.0]*(ptdf_tab.loc[201]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[201][str(outage_id)]) +
			uc_g[301]*u_r[301.0]*(ptdf_tab.loc[301]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[301][str(outage_id)]) +
			uc_g[401]*u_r[401.0]*(ptdf_tab.loc[401]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[401][str(outage_id)]) +
			uc_102*u_r[102.0]*(ptdf_tab.loc[102]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[102][str(outage_id)]) +
			uc_202*u_r[202.0]*(ptdf_tab.loc[202]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[202][str(outage_id)]) +
			uc_g[302]*u_r[302.0]*(ptdf_tab.loc[302]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[302][str(outage_id)]) +
			uc_g[402]*u_r[402.0]*(ptdf_tab.loc[402]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[402][str(outage_id)]) +
			uc_g[107]*u_r[107.0]*(ptdf_tab.loc[107]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[107][str(outage_id)]) +
			uc_g[207]*u_r[207.0]*(ptdf_tab.loc[207]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[207][str(outage_id)]) +
			uc_g[307]*u_r[307.0]*(ptdf_tab.loc[307]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[307][str(outage_id)]) +
			uc_g[113]*u_r[113.0]*(ptdf_tab.loc[113]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[113][str(outage_id)]) +
			uc_g[213]*u_r[213.0]*(ptdf_tab.loc[213]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[213][str(outage_id)]) +
			uc_g[313]*u_r[313.0]*(ptdf_tab.loc[313]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[313][str(outage_id)]) +
			uc_g[115]*u_r[115.0]*(ptdf_tab.loc[115]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[115][str(outage_id)]) +
			uc_g[215]*u_r[215.0]*(ptdf_tab.loc[215]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[215][str(outage_id)]) +
			uc_g[315]*u_r[315.0]*(ptdf_tab.loc[315]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[315][str(outage_id)]) +
			uc_g[415]*u_r[415.0]*(ptdf_tab.loc[415]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[415][str(outage_id)]) +
			uc_g[515]*u_r[515.0]*(ptdf_tab.loc[515]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[515][str(outage_id)]) +
			uc_g[615]*u_r[615.0]*(ptdf_tab.loc[615]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[615][str(outage_id)]) +
			uc_g[116]*u_r[116.0]*(ptdf_tab.loc[116]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[116][str(outage_id)]) +
			uc_g[118]*u_r[118.0]*(ptdf_tab.loc[118]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[118][str(outage_id)]) +
			uc_g[121]*u_r[121.0]*(ptdf_tab.loc[121]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[121][str(outage_id)]) +
			uc_g[122]*u_r[122.0]*(ptdf_tab.loc[122]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[122][str(outage_id)]) +
			uc_g[222]*u_r[222.0]*(ptdf_tab.loc[222]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[222][str(outage_id)]) +
			uc_g[322]*u_r[322.0]*(ptdf_tab.loc[322]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[322][str(outage_id)]) +
			uc_g[422]*u_r[422.0]*(ptdf_tab.loc[422]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[422][str(outage_id)]) +
			uc_g[522]*u_r[522.0]*(ptdf_tab.loc[522]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[522][str(outage_id)]) +
			uc_g[622]*u_r[622.0]*(ptdf_tab.loc[622]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[622][str(outage_id)]) +
			uc_g[123]*u_r[123.0]*(ptdf_tab.loc[123]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[123][str(outage_id)]) +
			uc_g[223]*u_r[223.0]*(ptdf_tab.loc[223]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[223][str(outage_id)]) +
			uc_g[323]*u_r[323.0]*(ptdf_tab.loc[323]['33'] + outage_sign * lodf_tab.loc[outage_id]['33'] * ptdf_tab.loc[323][str(outage_id)]) >= P_b_min[33])

		# Solve
		m.params.outputFlag = 0
		m.optimize()

		opt_results = 0.
		for elem in m.getVars():
			if elem.varName == 'uc_101':
				unit_recommit[101] = float(round(elem.x))
			elif elem.varName == 'uc_102':
				unit_recommit[102] = float(round(elem.x))
			elif elem.varName == 'uc_201':
				unit_recommit[201] = float(round(elem.x))
			elif elem.varName == 'uc_202':
				unit_recommit[202] = float(round(elem.x))
			elif elem.varName[0:3] == 'u_r':
				unit_response[float(elem.varName[4:9])] = float(elem.x)
			elif elem.varName == 'slack':
				print('slack =',elem.x)
			# elif elem.varName == 'mint':
			# 	opt_results = float(elem.x)

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
			row[ODC.Generator.REAL_GENERATION] = uc_g[int(row[ODC.Generator.ID])]*row[ODC.Generator.REAL_GENERATION]
			if row[ODC.Generator.ID] == 101.0 or row[ODC.Generator.ID] == 201.0 or row[ODC.Generator.ID] == 102.0 or row[ODC.Generator.ID] == 202.0:
				uc_g[int(row[ODC.Generator.ID])] = unit_recommit[int(row[ODC.Generator.ID])]
			row[ODC.Generator.OPERATIONAL_STATUS] = uc_g[int(row[ODC.Generator.ID])]
			row[ODC.Generator.REAL_GENERATION] += row[ODC.Generator.OPERATIONAL_STATUS]*unit_response[row[ODC.Generator.ID]]

		# for elem in unit_response:
		# 	print(elem, unit_response[elem])

		return opt_results

	except gurobipy.GurobiError:
		print('Gurobi error reported in contignency response')