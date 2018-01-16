
# ///////////////////////////////////////////////////////////////////////////////////
# OLD POWER-WATER N-1 FAILURE USING TANKS STUFF
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	# ANALYSIS STEP 5: Water N-1 and track base worst-case
	# ----------------------------------------------------

	# ANALYSIS STEP 6: Combined power-water N-1 and track worst-case
	# --------------------------------------------------------------

	# ANALYSIS STEP 7: Re-dispatch to reduce maximum water deficit
	# -----------------------------------------------------

	# object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = 0.0

	# for sdp_idx in range(0, len(subset_deficit_priority)):
	# 	sdp_id, sdp_val = subset_deficit_priority[sdp_idx]
	# 	node_list_constraint.append(sdp_id)
	
	# node_water_constraint = {1.0: 0.0,
	# 2.0: 0.0,
	# 7.0: 0.0,
	# 13.0: 0.0,
	# 15.0: 0.0,
	# 16.0: 0.0,
	# 18.0: 0.0,
	# 22.0: 0.0,
	# 33.0: 0.0}
	
	# def fun_set_power_dispatch(object_load, object_generator, losses, exports):
	# 	counter = 0
	# 	lost_min = 10000000.0
	# 	while True:
	# 		nres, ares = grb_solvers.unit_commitment_priority_list_water(object_load, object_generator, losses, exports, node_list_constraint, node_water_constraint) # unit commitment is variable
	# 		new_loss = run_OpenDSS(0, True)
	# 		counter += 1
	# 		# print(counter)

	# 		if math.fabs(losses - new_loss) > 1.0:
	# 			if counter > 199:
	# 				print('Dispatcher - Losses/Exports did not converge')
	# 				sys.exit()
	# 			elif counter > 150:
	# 				while True:
	# 					object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = dispatcher_max
	# 					nres, ares = grb_solvers.unit_commitment_priority_list_water_2(object_load, object_generator, losses, exports, node_list_constraint, node_water_constraint) # unit commitment is input
	# 					new_loss = run_OpenDSS(0, True)
	# 					counter +=1

	# 					if math.fabs(losses - new_loss) < 1.0:
	# 						return nres, ares
	# 					else:
	# 						losses += 0.8 * (new_loss - losses)
	# 			elif counter > 100:
	# 				while True:
	# 					object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = dispatcher_min
	# 					nres, ares = grb_solvers.unit_commitment_priority_list_water_2(object_load, object_generator, losses, exports, node_list_constraint, node_water_constraint) # unit commitment is input
	# 					new_loss = run_OpenDSS(0, True)
	# 					counter +=1

	# 					if math.fabs(losses - new_loss) < 1.0:
	# 						return nres, ares
	# 					else:
	# 						losses += 0.8 * (new_loss - losses)
	# 			elif counter > 50:
	# 				if math.fabs(new_loss) < math.fabs(lost_min):
	# 					lost_min = new_loss
	# 					dispatcher_min = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
	# 				else:
	# 					dispatcher_max = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
	# 			losses += 0.8*(new_loss - losses)
	# 		else:
	# 			return nres, ares

	# needed_reserves, avail_reserves = fun_set_power_dispatch(object_load, object_generator, losses, exports)
	# print('exports #1', 0.5 * (object_cable.matrix[33, ODC.Cable.REAL_POWER_2] - object_cable.matrix[33, ODC.Cable.REAL_POWER_1]))

	# ANALYSIS STEP 8: SET JUNCTION INTERCONNECTIONS
	# -----------------------------------------

	# ANALYSIS STEP 9:
	# Set water tank levels
	# Set water valve flow control
	# ----------------------------

	# ANALYSIS STEP 10:
	# -----------------

	# system_deficit = 0.0
	# subset_deficit = 0.0
	# subset_deficit_priority = []

	# temp_system_deficit = 0.0
	# temp_subset_deficit = 0.0
	# temp_subset_deficit_priority = []

	# base_pipe_status = np.array(object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS], copy=True)
	# base_tank_matrix = np.array(object_tank.matrix, copy=True)

	# base_gen_commitment = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
	# base_gen_dispatch = np.array(object_generator.matrix[:, ODC.Generator.REAL_GENERATION], copy=True)
	# base_branch_commitment = np.array(object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A], copy=True)

	# print('Generators')
	# for row in object_generator.matrix:
	# 	object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = np.array(base_gen_commitment, copy=True)
	# 	object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = np.array(base_gen_dispatch, copy=True)
	# 	run_OpenDSS(0, True)

	# 	if row[ODC.Generator.REAL_GENERATION] != 0.0:
	# 		print('GEN ID', row[ODC.Generator.ID])
	# 		row[ODC.Generator.REAL_GENERATION] = 0.0
	# 		row[ODC.Generator.OPERATIONAL_STATUS] = 0.0
	# 		run_OpenDSS(0, True)

	# 		# max_val = 0.0
	# 		# max_id = 0
	# 		# for cabidx in range(0, len(object_cable.matrix)):
	# 		# 	if object_cable.matrix[cabidx, ODC.Cable.A_PU_CAPACITY] > max_val:
	# 		# 		max_val = object_cable.matrix[cabidx, ODC.Cable.A_PU_CAPACITY]
	# 		# 		max_id = object_cable.matrix[cabidx, ODC.Cable.ID]

	# 		# print('max id', max_id)
	# 		# print('max pu', max_val)

	# 		minutes = grb_solvers.contingency_response(object_load, object_generator, object_cable)

	# 		if minutes > 10.01:
	# 			with open('minute_errors.csv', 'a', newline='') as file:
	# 				writer = csv.writer(file)
	# 				writer.writerow([power_load_factor, water_demand_factor, minutes])

	# 		object_junction.setInterconnectionDemand(interconn_dict)

	# 		for pipe in object_pipe.matrix:
	# 			if pipe[ENC.Pipe.ID] < 1000.0:
	# 				# print('SHUT DOWN PIPE:', pipe[ENC.Pipe.ID])

	# 				object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
	# 				object_tank.matrix = base_tank_matrix

	# 				pipe[ENC.Pipe.OPERATIONAL_STATUS] = 0.0

	# 				run_EPANET()

	# 				temp_subset_deficit = 0.0
	# 				temp_system_deficit = 0.0
	# 				temp_subset_deficit_priority = []

	# 				for tank in object_tank.matrix:
	# 					temp_system_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
	# 					if tank[ENC.Tank.ID]-1000.0 in subset_junction:
	# 						if math.fabs(tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL] - tank[ENC.Tank.HEAD]) > 1.0:
	# 							temp_subset_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
	# 							temp_subset_deficit_priority.append((tank[ENC.Tank.ID]-1000.0, math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])))

	# 				if row[ENC.Pipe.ID] == 9.0:
	# 					pipe_9_deficits = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
	# 					pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
	# 					pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
	# 					pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

	# 					if pipe_9_deficits > pipe_9_deficits_pw_n1:
	# 						pipe_9_deficits_pw_n1 = pipe_9_deficits
	# 						tank_15_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
	# 						tank_16_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
	# 						tank_18_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
	# 						tank_19_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

	# 				if temp_system_deficit > system_deficit and len(temp_subset_deficit_priority) > 0:
	# 					subset_deficit = temp_subset_deficit
	# 					subset_deficit_priority = sorted(temp_subset_deficit_priority, key=itemgetter(1), reverse=True)
						
	# 					system_deficit = temp_system_deficit
	# 		object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
	# 		object_tank.matrix = base_tank_matrix
	# object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = np.array(base_gen_commitment, copy=True)
	# object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = np.array(base_gen_dispatch, copy=True)

	# print('Cables')
	# for row in object_cable.matrix:
	# 	object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A] = np.array(base_branch_commitment, copy=True)
	# 	run_OpenDSS(0, True)
 
	# 	if row[ODC.Cable.ID] != 10.0 or row[ODC.Cable.ID] != 100.0:
	# 		if row[ODC.Cable.OPERATIONAL_STATUS_A] == 1.0:
	# 			print('CABLE ID', row[ODC.Cable.ID])
	# 			row[ODC.Cable.OPERATIONAL_STATUS_A] = 0.0
	# 			run_OpenDSS(0, True)

	# 			minutes = grb_solvers.contingency_response(object_load, object_generator, object_cable)

	# 			if minutes > 10.01:
	# 				with open('minute_errors.csv', 'a', newline='') as file:
	# 					writer = csv.writer(file)
	# 					writer.writerow([power_load_factor, water_demand_factor, minutes])

	# 			object_junction.setInterconnectionDemand(interconn_dict)

	# 		for pipe in object_pipe.matrix:
	# 			if pipe[ENC.Pipe.ID] < 1000.0:
	# 				# print('SHUT DOWN PIPE:', pipe[ENC.Pipe.ID])

	# 				object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
	# 				object_tank.matrix = base_tank_matrix

	# 				pipe[ENC.Pipe.OPERATIONAL_STATUS] = 0.0

	# 				run_EPANET()

	# 				temp_subset_deficit = 0.0
	# 				temp_system_deficit = 0.0
	# 				temp_subset_deficit_priority = []

	# 				for tank in object_tank.matrix:
	# 					temp_system_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
	# 					if tank[ENC.Tank.ID]-1000.0 in subset_junction:
	# 						if math.fabs(tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL] - tank[ENC.Tank.HEAD]) > 1.0:
	# 							temp_subset_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
	# 							temp_subset_deficit_priority.append((tank[ENC.Tank.ID]-1000.0, math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])))

	# 				if row[ENC.Pipe.ID] == 9.0:
	# 					pipe_9_deficits = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
	# 					pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
	# 					pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
	# 					pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

	# 					if pipe_9_deficits > pipe_9_deficits_pw_n1:
	# 						pipe_9_deficits_pw_n1 = pipe_9_deficits
	# 						tank_15_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
	# 						tank_16_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
	# 						tank_18_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
	# 						tank_19_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

	# 				if temp_system_deficit > system_deficit and len(temp_subset_deficit_priority) > 0:
	# 					subset_deficit = temp_subset_deficit
	# 					subset_deficit_priority = sorted(temp_subset_deficit_priority, key=itemgetter(1), reverse=True)
						
	# 					system_deficit = temp_system_deficit
	# 		object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
	# 		object_tank.matrix = base_tank_matrix
	# object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A] = np.array(base_branch_commitment, copy=True)
	# print('')

	# with open('main_analysis_power_water.csv', 'a', newline='') as file:
	# 	writer = csv.writer(file)
	# 	writer.writerow([power_load_factor, water_demand_factor, system_deficit, subset_deficit_priority, tank_15_p_w, tank_16_p_w, tank_18_p_w, tank_19_p_w])

# ///////////////////////////////////////////////////////////////////////////////////
# OLD STOCHASTIC FAILURE STUFF
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	# ------------------------
	# STOCHASTICITY PARAMETERS
	# ------------------------

	# water_num_switch = 0
	# water_num_stochastic = 0
	# power_num_switch = 0
	# power_num_stochastic = 0
	# for object in w_object_list:
	# 	water_num_switch += object.num_switches
	# 	water_num_stochastic += object.num_stochastic
	# for object in object_list:
	# 	power_num_switch += object.num_switches
	# 	power_num_stochastic += object.num_stochastic
	
	# def calc_probabilities():
		# temp = 0.0
		# switch_chanceval = 0.0
		# stochastic_chanceval = 0.0
		# for object in w_object_list:
		# 	if object.num_switches == 0:
		# 		object.switch_chance = (0.0, 0.0)
		# 	else:
		# 		try:
		# 			temp = switch_chanceval
		# 			switch_chanceval += object.num_switches / water_num_switch
		# 			object.switch_chance = (temp, switch_chanceval)
		# 		except:
		# 			object.switch_chance = (0.0, 0.0)
		# 	if object.num_stochastic == 0:
		# 		object.stochastic_chance = (0.0, 0.0)
		# 	else:
		# 		try:
		# 			temp = stochastic_chanceval
		# 			stochastic_chanceval += object.num_stochastic / water_num_stochastic
		# 			object.stochastic_chance = (temp, stochastic_chanceval)
		# 		except:
		# 			object.stochastic_chance = (0.0, 0.0)
		
		# temp = 0.0
		# switch_chanceval = 0.0
		# stochastic_chanceval = 0.0
		# for object in object_list:
		# 	if object.num_switches == 0:
		# 		object.switch_chance = (0.0, 0.0)
		# 	else:
		# 		try:
		# 			temp = switch_chanceval
		# 			switch_chanceval += object.num_switches / power_num_switch
		# 			object.switch_chance = (temp, switch_chanceval)
		# 		except:
		# 			object.switch_chance = (0.0, 0.0)
		# 	if object.num_stochastic == 0:
		# 		object.stochastic_chance = (0.0, 0.0)
		# 	else:
		# 		try:
		# 			temp = stochastic_chanceval
		# 			stochastic_chanceval += object.num_stochastic / power_num_stochastic
		# 			object.stochastic_chance = (temp, stochastic_chanceval)
		# 		except:
		# 			object.stochastic_chance = (0.0, 0.0)

	# def run_stochasticity(stoch_num):
	# 	# STOCHASTIC VALUES (e.g., demand)
	# 	for i in range(0, stoch_num):
	# 		if random.randrange(1, water_num_stochastic+power_num_stochastic+1) <= water_num_stochastic:
	# 			rval = random.random()
	# 			for object in w_object_list: # water list
	# 				lower, upper = object.stochastic_chance
	# 				if lower <= rval <= upper:
	# 					pass
	# 					# object.randomStochasticity()
	# 		else:
	# 			rval = random.random()
	# 			for object in object_list: # power list
	# 				lower, upper = object.stochastic_chance
	# 				if lower <= rval <= upper:
	# 					pass
	# 					# object.randomStochasticity()

	# 	# SWITCHING VALUES (e.g., on/off)
	# 	if random.random() <= 0.65: # 65% chance to shutoff
	# 		if random.randrange(1, water_num_switch+power_num_switch+1) <= water_num_switch:
	# 			rval = random.random()
	# 			for object in w_object_list: # water list
	# 				lower, upper = object.switch_chance
	# 				if lower <= rval <= upper:
	# 					pass
	# 					# object.randomSwitching()
	# 		else:
	# 			rval = random.random()
	# 			for object in object_list: # power list
	# 				lower, upper = object.switch_chance
	# 				if lower <= rval <= upper:
	# 					pass
	# 					# object.randomSwitching()

	# # SIM STEP 1: CALCULATE UNIFORM PROBABILITIES FOR COMPONENTS
	# calc_probabilities()

	# # SIM STEP 2: STOCHASTICITY OF OBJECT CONTROLS AND "FAILURE"
	# run_stochasticity(stoch_num)