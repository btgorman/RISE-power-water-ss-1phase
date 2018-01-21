# Copyright 2017 Brandon T. Gorman

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# BUILT USING PYTHON 3.6.0

import ctypes as ct
import pandas as pd
import numpy as np
import random, csv, sys, os
import math

import classes_water as ENC

def main(water_df):
	os_username = os.getlogin()

	# --------------
	# READ CSV FILES
	# --------------

	csv_curve = pd.read_csv('./data_water/network-water/2000curve.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_junction = pd.read_csv('./data_water/network-water/2100junction.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_reservoir = pd.read_csv('./data_water/network-water/2101reservoir.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_tank = pd.read_csv('./data_water/network-water/2102tank.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_pipe = pd.read_csv('./data_water/network-water/2200pipe.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_pump = pd.read_csv('./data_water/network-water/2201pump.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_valve = pd.read_csv('./data_water/network-water/2202valve.csv', sep=',', header=1, index_col=None, dtype=np.float64)

	# -----------------
	# CREATE COMPONENTS
	# -----------------

	object_curve = ENC.Curve(csv_curve)
	object_junction = ENC.Junction(csv_junction)
	object_reservoir = ENC.Reservoir(csv_reservoir)
	object_tank = ENC.Tank(csv_tank)
	object_pipe = ENC.Pipe(csv_pipe)
	object_pump = ENC.Pump(csv_pump)
	object_valve = ENC.Valve(csv_valve)

	# -----------------------
	# ADD COMPONENTS TO LISTS
	# -----------------------

	w_object_list = [object_junction, object_reservoir, object_tank, # Water NODES
	object_pipe, object_pump, object_valve, # Water LINKS
	object_curve] # Water SYSTEM OPS

	interconn_dict = {}

	# ---------
	# RUN EPANET and OPENDSS
	# ---------

	def run_EPANET():
		filedir = 'data_water/en-inputs/en-input.inp'
		with open(filedir, 'w', newline='\n') as csvfile:
			writer = csv.writer(csvfile, delimiter=' ')
			templist = ['[TITLE]']
			writer.writerow(templist)
			writer.writerow('')

			for water_object in w_object_list:
				water_object.createAllEN(writer, interconn_dict)

			templist = ['[ENERGY]']
			writer.writerow(templist)
			templist = ['Global', 'Efficiency', 75]
			writer.writerow(templist)
			templist = ['Global', 'Price', 0]
			writer.writerow(templist)
			templist = ['Demand', 'Charge', 0]
			writer.writerow(templist)
			writer.writerow('')

			templist = ['[REACTIONS]']
			writer.writerow(templist)
			templist = ['Order', 'Bulk', 1]
			writer.writerow(templist)
			templist = ['Order', 'Tank', 1]
			writer.writerow(templist)
			templist = ['Order', 'Wall', 1]
			writer.writerow(templist)
			templist = ['Global', 'Bulk', 0]
			writer.writerow(templist)
			templist = ['Global', 'Wall', 0]
			writer.writerow(templist)
			templist = ['Limiting', 'Potential', 0]
			writer.writerow(templist)
			templist = ['Roughness', 'Correlation', 0]
			writer.writerow(templist)
			writer.writerow('')

			templist = ['[TIMES]']
			writer.writerow(templist)
			templist = ['Duration', '00:00']
			writer.writerow(templist)
			templist = ['Hydraulic', 'Timestep', '0:01:00']
			writer.writerow(templist)
			templist = ['Quality', 'Timestep', '0:06']
			writer.writerow(templist)
			templist = ['Pattern', 'Timestep', '1:00']
			writer.writerow(templist)
			templist = ['Pattern', 'Start', '0:00']
			writer.writerow(templist)
			templist = ['Report', 'Timestep', '1:00']
			writer.writerow(templist)
			templist = ['Report', 'Start', '0:00']
			writer.writerow(templist)
			templist = ['Start', 'ClockTime', 12, 'am']
			writer.writerow(templist)
			templist = ['Statistic', 'NONE']
			writer.writerow(templist)
			writer.writerow('')

			templist = ['[REPORT]']
			writer.writerow(templist)
			templist = ['Status', 'No']
			writer.writerow(templist)
			templist = ['Summary', 'No']
			writer.writerow(templist)
			templist = ['Page', 0]
			writer.writerow(templist)
			writer.writerow('')

			templist = ['[OPTIONS]']
			writer.writerow(templist)
			templist = ['Units', 'GPM'] #GPM is US Customary units
			writer.writerow(templist)
			templist = ['Headloss', 'C-M']
			writer.writerow(templist)
			templist = ['Specific', 'Gravity', 1]
			writer.writerow(templist)
			templist = ['Viscosity', 1]
			writer.writerow(templist)
			templist = ['Trials', 40]
			writer.writerow(templist)
			templist = ['Accuracy', 0.001]
			writer.writerow(templist)
			templist = ['CHECKFREQ', 2]
			writer.writerow(templist)
			templist = ['MAXCHECK', 10]
			writer.writerow(templist)
			templist = ['DAMPLIMIT', 0]
			writer.writerow(templist)
			templist = ['Unbalanced', 'Continue', 10]
			writer.writerow(templist)
			templist = ['Pattern', 1]
			writer.writerow(templist)
			templist = ['Demand', 'Multiplier', 1.0]
			writer.writerow(templist)
			templist = ['Emitter', 'Exponent', 0.5]
			writer.writerow(templist)
			templist = ['Quality', 'None', 'mg/L']
			writer.writerow(templist)
			templist = ['Diffusivity', 1]
			writer.writerow(templist)
			templist = ['Tolerance', 0.01]
			writer.writerow(templist)
			writer.writerow('')

			templist=['[END]']
			writer.writerow(templist)

		epalib = ct.cdll.LoadLibrary('data_water/epanet2mingw64.dll')

		# Byte objects
		en_input_file = ct.c_char_p(filedir.encode('utf-8'))
		en_report_file = ct.c_char_p(str('data_water/en-outputs/out.rpt').encode('utf-8'))
		en_byte_file = ct.c_char_p(''.encode('utf-8'))

		# Send strings as char* to the epalib function
		errorcode = epalib.ENopen(en_input_file, en_report_file, en_byte_file)
		if errorcode != 0:
			print(1, 'ERRORCODE is', errorcode)

		errorcode = epalib.ENopenH()
		if errorcode != 0:
			print(2, 'ERRORCODE is', errorcode)

		init_flag = ct.c_int(0)
		errorcode = epalib.ENinitH(init_flag)
		if errorcode != 0:
			print(3, 'ERRORCODE is', errorcode)

		time = ct.pointer(ct.c_long(1))
		timestep = ct.pointer(ct.c_long(1))
		while True:
			errorcode = epalib.ENrunH(time)
			if errorcode != 0:
				pass
				# print(4, 'ERRORCODE is', errorcode)

			errorcode = epalib.ENnextH(timestep)
			if errorcode != 0:
				print(5, 'ERRORCODE is', errorcode)

			if timestep.contents.value == 0:
				break

		for water_object in w_object_list:
			water_object.readAllENoutputs(epalib)

		errorcode = epalib.ENcloseH()
		if errorcode != 0:
			print(6, 'ERRORCODE is', errorcode)

		errorcode = epalib.ENclose()
		if errorcode != 0:
			print(7, 'ERRORCODE is', errorcode)

		input_list_continuous = []
		input_list_categorical = []
		input_tensor_continuous = np.empty([0,0], dtype=np.float64).flatten()
		input_tensor_categorical = np.empty([0,0], dtype=np.float64).flatten()
		for object in w_object_list:
			list_continuous, list_categorical, tensor_continuous, tensor_categorical = object.convertToInputTensor()
			input_list_continuous = input_list_continuous + list_continuous
			input_list_categorical = input_list_categorical + list_categorical
			input_tensor_continuous = np.concatenate((input_tensor_continuous, tensor_continuous), axis=0)
			input_tensor_categorical = np.concatenate((input_tensor_categorical, tensor_categorical), axis=0)

		output_list = []
		output_tensor = np.empty([0,0], dtype=np.float64).flatten()
		for object in w_object_list:
			o_list, o_tensor = object.convertToOutputTensor()
			output_list = output_list + o_list
			output_tensor = np.concatenate((output_tensor, o_tensor), axis=0)

		return input_list_continuous, input_list_categorical, output_list, input_tensor_continuous, input_tensor_categorical, output_tensor

	# SIM STEP 1: SET LOAD AND DEMAND CURVES
	# ------------------------------

	# SIM STEP 2: SET LOAD INTERCONNECTIONS
	# ----------------------------------

	# SIM STEP 3: SET GENERATOR DISPATCH
	# ----------------------------------

	# SIM STEP 4: SET JUNCTION INTERCONNECTIONS
	# -----------------------------------------

	# SIM STEP 5:
	# Set water tank levels assuming that water tank levels start at 0
	# Set water valve flow control
	# ----------------------------

	# SIM STEP 6: RUN POWER-WATER SIMULATION
	# --------------------------------------

	base_curve_matrix  = np.array(object_curve.matrix, copy=True)
	base_junction_matrix = np.array(object_junction.matrix, copy=True)
	base_reservoir_matrix = np.array(object_reservoir.matrix, copy=True)
	base_tank_matrix = np.array(object_tank.matrix, copy=True)
	base_pipe_matrix = np.array(object_pipe.matrix, copy=True)
	base_pump_matrix = np.array(object_pump.matrix, copy=True)
	base_valve_matrix = np.array(object_valve.matrix, copy=True)

	# Begin failure analysis loop

	for pipe_fail_id in [pid for pid in object_pipe.matrix[:, ENC.Pipe.ID] if 0.0 <= pid < 1000.0]:

		# Reset objects
		object_curve.matrix = np.array(base_curve_matrix, copy=True)
		object_junction.matrix = np.array(base_junction_matrix, copy=True)
		object_reservoir.matrix = np.array(base_reservoir_matrix, copy=True)
		object_tank.matrix = np.array(base_tank_matrix, copy=True)
		object_pipe.matrix = np.array(base_pipe_matrix, copy=True)
		object_pump.matrix = np.array(base_pump_matrix, copy=True)
		object_valve.matrix = np.array(base_valve_matrix, copy=True)

		for pipe in object_pipe.matrix:
			if pipe[ENC.Pipe.ID] == pipe_fail_id:
				pipe[ENC.Pipe.OPERATIONAL_STATUS] = 0.0
				print('Failing Pipe ID {}'.format(int(pipe_fail_id)))

		water_demand_factor = water_df # %
		artificial_reservoir_id_shift = 1000.0
		max_groundwater_flow = 12399.0 # GPM
		groundwater_id_shift = 2000.0

		# Scale reservoir heads using water_demand_factor
		for reservoir in object_reservoir.matrix:
			if reservoir[ENC.Reservoir.ID] == 21.0:
				reservoir[ENC.Reservoir.TOTAL_HEAD] = max(reservoir[ENC.Reservoir.TOTAL_HEAD], 488.75 + 1043.2*water_demand_factor)
			elif reservoir[ENC.Reservoir.ID] == 22.0:
				reservoir[ENC.Reservoir.TOTAL_HEAD] = max(reservoir[ENC.Reservoir.TOTAL_HEAD], 538.21 + 1161.8*water_demand_factor)
			elif reservoir[ENC.Reservoir.ID] == 23.0:
				reservoir[ENC.Reservoir.TOTAL_HEAD] = max(reservoir[ENC.Reservoir.TOTAL_HEAD], 467.31 + 823.69*water_demand_factor)

		# Set valves to maximum amount of groundwater flow
		for junction in object_junction.matrix:
			for valve in object_valve.matrix:
				if valve[ENC.Valve.ID]-groundwater_id_shift == junction[ENC.Junction.ID]:
					# valve[ENC.Valve.SETTING] = min(junction[ENC.Junction.BASE_DEMAND], max_groundwater_flow)
					valve[ENC.Valve.SETTING] = max_groundwater_flow

		groundwater_list = []
		map_to_groundwater_reservoir = {}
		map_to_groundwater_pipe = {}

		# Track real reservoirs
		for reservoir in object_reservoir.matrix:
			if reservoir[ENC.Reservoir.ID] >= 3000.0:
				groundwater_list.append(reservoir[ENC.Reservoir.ID])
				map_to_groundwater_reservoir[reservoir[ENC.Reservoir.ID]] = reservoir
				for pipe in object_pipe.matrix:
					if reservoir[ENC.Reservoir.ID] == pipe[ENC.Pipe.ID]:
						map_to_groundwater_pipe[reservoir[ENC.Reservoir.ID]] = pipe
			# WARNING THIS IS HARDCODED
			elif reservoir[ENC.Reservoir.ID] == 23.0:
				groundwater_list.append(reservoir[ENC.Reservoir.ID])
				map_to_groundwater_reservoir[reservoir[ENC.Reservoir.ID]] = reservoir
				for pipe in object_pipe.matrix:
					# WARNING THIS IS HARDCODED
					if pipe[ENC.Pipe.ID] == 36.0:
						map_to_groundwater_pipe[reservoir[ENC.Reservoir.ID]] = pipe

		# Loop real reservoirs, turn off the ones with water inflow
		while len(groundwater_list) > 0:

			# initialize relevnt demand junctions
			demand_list = []
			map_to_junction = {}
			map_to_reservoir = {}
			map_to_pipe = {}

			# Track demand junctions
			for junction in object_junction.matrix:
				if junction[ENC.Junction.BASE_DEMAND_AVERAGE] > 0.0:
					demand_list.append(junction[ENC.Junction.ID])
			for junction in object_junction.matrix:
				if junction[ENC.Junction.ID] in demand_list:
					map_to_junction[junction[ENC.Junction.ID]] = junction

			# Track artificial reservoirs
			for reservoir in object_reservoir.matrix:
				if reservoir[ENC.Reservoir.ID]-artificial_reservoir_id_shift in demand_list:
					map_to_reservoir[reservoir[ENC.Reservoir.ID]-artificial_reservoir_id_shift] = reservoir

			# Track pipes for artifical reservoirs
			for pipe in object_pipe.matrix:
				if pipe[ENC.Pipe.ID]-artificial_reservoir_id_shift in demand_list:
					map_to_pipe[pipe[ENC.Pipe.ID]-artificial_reservoir_id_shift] = pipe

			# Reset demand junction demands to 0
			for junction_id in demand_list:
				map_to_junction[junction_id][ENC.Junction.BASE_DEMAND] = 0.0

			# Begin EPANET pressure-driven analysis for artificial reservoirs
			while len(demand_list) > 0:

				# Close artifical reservoirs pipes
				for junction_id in demand_list:
					map_to_pipe[junction_id][ENC.Pipe.OPERATIONAL_STATUS] = 0.0
				run_EPANET()

				# Open demand junctions with positive pressure ratio
				# Can take multiple iterations
				pos_pres_bool = True
				while pos_pres_bool:
					pos_pres_bool = False
					max_pres_id = demand_list[0]
					for junction_id in demand_list:
						if map_to_junction[junction_id][ENC.Junction.PRESSURE] > map_to_junction[max_pres_id][ENC.Junction.PRESSURE] and map_to_pipe[junction_id][ENC.Pipe.OPERATIONAL_STATUS] == 0.0:
							max_pres_id = junction_id
					# this uses the MINIMUM ALLOWABLE PRESSURE
					if map_to_junction[max_pres_id][ENC.Junction.PRESSURE] > (map_to_junction[max_pres_id][ENC.Junction.MIN_PRESSURE] -0.01) and map_to_pipe[max_pres_id][ENC.Pipe.OPERATIONAL_STATUS] == 0.0:
						map_to_pipe[max_pres_id][ENC.Pipe.OPERATIONAL_STATUS] = 1.0
						pos_pres_bool = True
					run_EPANET()
				run_EPANET()

				# Close artifical reservoirs with inflows
				# Can take multiple iterations
				neg_dem_bool = True
				while neg_dem_bool:
					neg_dem_bool = False
					for junction_id in demand_list:
						if map_to_reservoir[junction_id][ENC.Reservoir.DEMAND] < 0.0:
							map_to_pipe[junction_id][ENC.Pipe.OPERATIONAL_STATUS] = 0.0
							neg_dem_bool = True
					run_EPANET()
				run_EPANET()

				# Set base_demand to maximum if possible
				pda_count = 0
				demand_list_copy = demand_list.copy()
				for junction_id in demand_list_copy:
					if map_to_reservoir[junction_id][ENC.Reservoir.DEMAND] >= water_demand_factor * map_to_junction[junction_id][ENC.Junction.BASE_DEMAND_AVERAGE]:
						map_to_junction[junction_id][ENC.Junction.BASE_DEMAND] = water_demand_factor * map_to_junction[junction_id][ENC.Junction.BASE_DEMAND_AVERAGE]
						map_to_pipe[junction_id][ENC.Pipe.OPERATIONAL_STATUS] = 0.0
						demand_list.remove(junction_id)
						pda_count += 1

				# Set base_demand to greater than 0 and less than maximum if there are no maximums
				if pda_count == 0:
					for junction_id in demand_list_copy:
						if map_to_reservoir[junction_id][ENC.Reservoir.DEMAND] >= 0.0:
							map_to_junction[junction_id][ENC.Junction.BASE_DEMAND] = map_to_reservoir[junction_id][ENC.Reservoir.DEMAND]
							map_to_pipe[junction_id][ENC.Pipe.OPERATIONAL_STATUS] = 0.0
							demand_list.remove(junction_id)

				# End inner loop
			run_EPANET()

			# Close real reservoirs with inflows if possible
			pda_count = 0
			groundwater_list_copy = groundwater_list.copy()
			for groundwater_id in groundwater_list_copy:
				if map_to_groundwater_reservoir[groundwater_id][ENC.Reservoir.DEMAND] > 0.0:
					map_to_groundwater_pipe[groundwater_id][ENC.Pipe.OPERATIONAL_STATUS] = 0.0
					groundwater_list.remove(groundwater_id)
					pda_count += 1

			# Delete real reservoirs from being tracked if no real reservoirs have inflows
			if pda_count == 0:
				for groundwater_id in groundwater_list_copy:
					groundwater_list.remove(groundwater_id)

			# End middle loop

		input_list_continuous1, input_list_categorical1, output_list1, input_tensor_continuous1, input_tensor_categorical1, output_tensor1 = run_EPANET()

		# RESULTS STEP 0: Print
		# ---------------------
		# for row in object_reservoir.matrix:
		# 	if row[ENC.Reservoir.ID] == 1.0:
		# 		print('Reservoir 1 has head of {:.1f}'.format(row[ENC.Reservoir.HEAD]))

		# print('')
		# for row in object_pipe.matrix:
		# 	if row[ENC.Pipe.OPERATIONAL_STATUS] == 0.0:
		# 		print('Pipe {} is closed!'.format(int(row[ENC.Pipe.ID])))

		system_deficit = 0.0
		j_1_deficit = 0.0
		j_2_deficit = 0.0
		j_3_deficit = 0.0
		j_5_deficit = 0.0
		j_6_deficit = 0.0
		j_7_deficit = 0.0
		j_8_deficit = 0.0
		j_9_deficit = 0.0
		j_10_deficit = 0.0
		j_13_deficit = 0.0
		j_14_deficit = 0.0
		j_15_deficit = 0.0
		j_16_deficit = 0.0
		j_18_deficit = 0.0
		j_19_deficit = 0.0
		j_28_deficit = 0.0

		for row in object_junction.matrix:
			if row[ENC.Junction.BASE_DEMAND_AVERAGE] > 0.0:
				pass
				# print('Junction {} has pressure {:.2f} and outflow {:.2f} with deficit {:.2f} GPM and {:.2f} %'.format(int(row[ENC.Junction.ID]), row[ENC.Junction.PRESSURE], row[ENC.Junction.DEMAND], water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND], (1.0 - row[ENC.Junction.DEMAND] / (water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE]))*100.0 ))
			if row[ENC.Junction.ID] == 1.0:
				j_1_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 2.0:
				j_2_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 3.0:
				j_3_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 5.0:
				j_5_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 6.0:
				j_6_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 7.0:
				j_7_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 8.0:
				j_8_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 9.0:
				j_9_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 10.0:
				j_10_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 13.0:
				j_13_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 14.0:
				j_14_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 15.0:
				j_15_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 16.0:
				j_16_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 18.0:
				j_18_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 19.0:
				j_19_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])
			elif row[ENC.Junction.ID] == 28.0:
				j_28_deficit = max(0.0, water_demand_factor * row[ENC.Junction.BASE_DEMAND_AVERAGE] - row[ENC.Junction.DEMAND])		
		
		system_deficit = 0.0
		system_deficit += j_1_deficit
		system_deficit += j_2_deficit
		system_deficit += j_3_deficit
		system_deficit += j_5_deficit
		system_deficit += j_6_deficit
		system_deficit += j_7_deficit
		system_deficit += j_8_deficit
		system_deficit += j_9_deficit
		system_deficit += j_10_deficit
		system_deficit += j_13_deficit
		system_deficit += j_14_deficit
		system_deficit += j_15_deficit
		system_deficit += j_16_deficit
		system_deficit += j_18_deficit
		system_deficit += j_19_deficit
		system_deficit += j_28_deficit

		# print('')
		# for row in object_reservoir.matrix:
		# 	print('Reservoir {} has outflow {:.2f}'.format(int(row[ENC.Reservoir.ID]), row[ENC.Reservoir.DEMAND]))

		# for reservoir in object_reservoir.matrix:
		# 	if reservoir[ENC.Reservoir.DEMAND] > 0.0:
		# 		print('Reservoir {} has demand {}'.format(int(reservoir[ENC.Reservoir.ID]), reservoir[ENC.Reservoir.DEMAND]))

		# print('')
		# for pump in object_pump.matrix:
		# 	print('Pump {} has POWER_CONSUMPTION {:.2f} MW'.format(int(pump[ENC.Pump.ID]), pump[ENC.Pump.POWER_CONSUMPTION]*0.001))

		with open('model_outputs/analysis_water_failure/water_failure_analysis_pipe_{}.csv'.format(int(pipe_fail_id)), 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow([water_demand_factor, system_deficit, j_1_deficit, j_2_deficit, j_3_deficit, j_5_deficit, j_6_deficit, j_7_deficit, j_8_deficit, j_9_deficit, j_10_deficit, j_13_deficit, j_14_deficit, j_15_deficit, j_16_deficit, j_18_deficit, j_19_deficit, j_28_deficit])

	# End outer loop

	# RESULTS STEP 1: FORMAT INPUT/OUTPUT TENSORS
	# -------------------------------------------
	# input_list_continuous = input_list_continuous1
	# input_list_categorical = input_list_categorical1
	# output_list = output_list1

	# input_tensor_continuous = input_tensor_continuous1
	# input_tensor_categorical = input_tensor_categorical1
	# output_tensor = output_tensor1

	# RESULTS STEP 2: WRITE INPUT/OUTPUT TENSORS TO FILE
	# --------------------------------------------------
	# with open('tensor_outputs/input_list_continuous_columns.csv', 'w') as f:
	# 	writer = csv.writer(f, delimiter=',')
	# 	writer.writerow(input_list_continuous)
	# with open('tensor_outputs/input_list_categorical_columns.csv', 'w') as f:
	# 	writer = csv.writer(f, delimiter=',')
	# 	writer.writerow(input_list_categorical)
	# with open('tensor_outputs/output_list_columns.csv', 'w') as f:
	# 	writer = csv.writer(f, delimiter=',')
	# 	writer.writerow(output_list)

	# with open('tensor_outputs/input_tensor_continuous.csv', 'ab') as f:
	# 	np.savetxt(f, input_tensor_continuous[None, :], fmt='%0.6f', delimiter=' ', newline='\n')
	# with open('tensor_outputs/input_tensor_categorical.csv', 'ab') as f:
	# 	np.savetxt(f, input_tensor_categorical[None, :], fmt='%0.6f', delimiter=' ', newline='\n')
	# with open('tensor_outputs/output_tensor.csv', 'ab') as f:
	# 	np.savetxt(f, output_tensor[None, :], fmt='%0.6f', delimiter=' ', newline='\n')

	# END
	# ---

if __name__ == '__main__':

	water_df = float(sys.argv[1])
	
	main(water_df)