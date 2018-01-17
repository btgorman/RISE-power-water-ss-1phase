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
import time

from statistics import median

import classes_water as ENC
import classes_power as ODC
import classes_interconnection as ICC
import grb_solvers

from comtypes import automation
import win32com.client
# from win32com.client import makepy
# sys.argv = ['makepy', 'OpenDSSEngine.DSS']
# makepy.main()

from operator import itemgetter

def main(dss_debug, write_cols, power_df, water_df, pipe_fail_id):

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

	csv_xycurve = pd.read_csv('./data_power/network-power/1000xycurve.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_regcontrol = pd.read_csv('./data_power/network-power/1100regcontrol.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_wiredata = pd.read_csv('./data_power/network-power/1200wiredata.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_linecode = pd.read_csv('./data_power/network-power/1201linecode.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_bus = pd.read_csv('./data_power/network-power/1300bus.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_vsource = pd.read_csv('./data_power/network-power/1301vsource.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_generator = pd.read_csv('./data_power/network-power/1302generator.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_load = pd.read_csv('./data_power/network-power/1303load.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_solarpv = pd.read_csv('./data_power/network-power/1304solarpv.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_windturbine = pd.read_csv('./data_power/network-power/1305windturbine.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_directconnection = pd.read_csv('./data_power/network-power/1400directconnection.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_cable = pd.read_csv('./data_power/network-power/1401cable.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_overheadline = pd.read_csv('./data_power/network-power/1402overheadline.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_twowindingtransformer = pd.read_csv('./data_power/network-power/1403twowindingtransformer.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_capacitor = pd.read_csv('./data_power/network-power/1404capacitor.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_reactor = pd.read_csv('./data_power/network-power/1405reactor.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	# csv_allcolumns= pd.read_csv('./data_power/network-power/allcolumns.csv', sep=',', header=1, index_col=None, dtype=np.float64)

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

	object_xycurve = ODC.XYCurve(csv_xycurve)
	object_regcontrol = ODC.RegControl(csv_regcontrol)
	object_wiredata = ODC.WireData(csv_wiredata)
	object_linecode = ODC.LineCode(csv_linecode)
	object_bus = ODC.Bus(csv_bus)
	object_vsource = ODC.VSource(csv_vsource)
	object_generator = ODC.Generator(csv_generator)
	object_load = ODC.Load(csv_load)
	object_solarpv = ODC.SolarPV(csv_solarpv)
	object_windturbine = ODC.WindTurbine(csv_windturbine, object_xycurve)
	object_directconnection = ODC.DirectConnection(csv_directconnection)
	object_cable = ODC.Cable(csv_cable)
	object_overheadline = ODC.OverheadLine(csv_overheadline)
	object_twowindingtransformer = ODC.TwoWindingTransformer(csv_twowindingtransformer)
	object_capacitor = ODC.Capacitor(csv_capacitor)
	object_reactor = ODC.Reactor(csv_reactor)

	# -----------------------
	# ADD COMPONENTS TO LISTS
	# -----------------------

	w_object_list = [object_junction, object_reservoir, object_tank, # Water NODES
	object_pipe, object_pump, object_valve, # Water LINKS
	object_curve] # Water SYSTEM OPS

	object_list = [object_vsource, object_bus, object_generator, object_load, object_solarpv, object_windturbine, #NODES
	object_xycurve, object_wiredata, object_linecode, #OTHERS
	object_directconnection, object_cable, object_overheadline, object_twowindingtransformer, object_capacitor, object_reactor, # CONNECTIONS
	object_regcontrol] # CONTROLS

	interconn_dict = {'generator': object_generator, 'load': object_load, 'pump': object_pump, 'junction': object_junction}

	# ---------
	# RUN EPANET and OPENDSS
	# ---------

	def run_EPANET():
		filedir = 'C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/data_water/en-inputs/en-input.inp'
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
			templist = ['Duration', '0:00']
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

		epalib = ct.cdll.LoadLibrary('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/data_water/epanet2mingw64.dll')

		# Byte objects
		en_input_file = ct.c_char_p(filedir.encode('utf-8'))
		en_report_file = ct.c_char_p(str('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/data_water/en-outputs/out.rpt').encode('utf-8'))
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

	def run_OpenDSS(dss_debug, solverFlag):
		# SET SOURCEBUS
		# VsourceClass.sourcebus = vsourceobj.id[1]
		dssObj = win32com.client.Dispatch('OpenDSSEngine.DSS') # OPENDSS COMPORT

		dssObj.AllowForms = False
		dssText = dssObj.Text
		dssCkt = dssObj.ActiveCircuit
		dssSolution = dssCkt.Solution
		dssActvElem = dssCkt.ActiveCktElement
		dssActvBus = dssCkt.ActiveBus

		dssText.Command = 'Clear'

		dssText.Command = 'Set DataPath=\'C:\\Users\\'+os_username+'\\Documents\\OpenDSS'
		dssText.Command = 'Set DefaultBaseFrequency=60'

		for object in object_list:
			object.createAllDSS(dssText, interconn_dict, dss_debug)

		set_voltagebase = set()
		for object in object_list:
			set_voltagebase = set_voltagebase | object.voltagesToSets()

		dssText.Command = 'Set VoltageBases={}'.format(list(set_voltagebase))
		dssText.Command = 'CalcVoltageBases'
		dssText.Command = 'Solve BaseFrequency=60 MaxIter=300'

		variant_buses = automation.VARIANT()
		variant_voltages_mag = automation.VARIANT()
		variant_voltages_pu = automation.VARIANT()
		variant_currents = automation.VARIANT()
		variant_powers = automation.VARIANT()

		for object in object_list:
			object.readAllDSSOutputs(dssCkt, dssActvElem, dssActvBus, variant_buses, variant_voltages_mag, variant_voltages_pu, variant_currents, variant_powers)

		if solverFlag == False:
			# dssText.Command = 'Save Circuit'
			# dssText.Command = 'Export Summary (summary.csv)'
			# dssText.Command = 'Export Currents (currents.csv)'
			# dssText.Command = 'Export Voltages (voltages.csv)'
			# dssText.Command = 'Export Overloads (overloads.csv)'
			# dssText.Command = 'Export Powers kVA (powers.csv)'

			input_list_continuous = []
			input_list_categorical = []
			input_tensor_continuous = np.empty([0,0], dtype=np.float64).flatten()
			input_tensor_categorical = np.empty([0,0], dtype=np.float64).flatten()
			for object in object_list:
				list_continuous, list_categorical, tensor_continuous, tensor_categorical = object.convertToInputTensor()
				input_list_continuous = input_list_continuous + list_continuous
				input_list_categorical = input_list_categorical + list_categorical
				input_tensor_continuous = np.concatenate((input_tensor_continuous, tensor_continuous), axis=0)
				input_tensor_categorical = np.concatenate((input_tensor_categorical, tensor_categorical), axis=0)

			output_list = []
			output_tensor = np.empty([0,0], dtype=np.float64).flatten()
			for object in object_list:
				o_list, o_tensor = object.convertToOutputTensor()
				output_list = output_list + o_list
				output_tensor = np.concatenate((output_tensor, o_tensor), axis=0)

			return input_list_continuous, input_list_categorical, output_list, input_tensor_continuous, input_tensor_categorical, output_tensor
		else:
			losses = dssCkt.Losses
			return float(losses[0])*0.001 # kW

	# SIM STEP 0: SOLVE PUMP POWER CONSUMPTION
	# ----------------------------------------

	for pipe in object_pipe.matrix:
		if pipe[ENC.Pipe.ID] == pipe_fail_id:
			pipe[ENC.Pipe.OPERATIONAL_STATUS] = 0.0

	base_curve_matrix = np.array(object_curve.matrix, copy=True)
	base_junction_matrix = np.array(object_junction.matrix, copy=True)
	base_reservoir_matrix = np.array(object_reservoir.matrix, copy=True)
	base_tank_matrix = np.array(object_tank.matrix, copy=True)
	base_pipe_matrix = np.array(object_pipe.matrix, copy=True)
	base_pump_matrix = np.array(object_pump.matrix, copy=True)
	base_valve_matrix = np.array(object_valve.matrix, copy=True)

	artificial_reservoir_id_shift = 1000.0
	max_groundwater_flow = 12399.0 # GPM
	groundwater_id_shift = 2000.0

	# Scale reservoir heads using water_df
	for reservoir in object_reservoir.matrix:
		if reservoir[ENC.Reservoir.ID] < 1000.0:
			reservoir[ENC.Reservoir.TOTAL_HEAD] = max(1.0, water_df) * reservoir[ENC.Reservoir.TOTAL_HEAD]

	# Set valves to maximum amount of groundwater flow
	for junction in object_junction.matrix:
		for valve in object_valve.matrix:
			if valve[ENC.Valve.ID]-groundwater_id_shift == junction[ENC.Junction.ID]:
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
				if map_to_junction[max_pres_id][ENC.Junction.PRESSURE] > (map_to_junction[max_pres_id][ENC.Junction.MIN_PRESSURE]-0.01) and map_to_pipe[max_pres_id][ENC.Pipe.OPERATIONAL_STATUS] == 0.0:
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
				if map_to_reservoir[junction_id][ENC.Reservoir.DEMAND] >= water_df * map_to_junction[junction_id][ENC.Junction.BASE_DEMAND_AVERAGE]:
					map_to_junction[junction_id][ENC.Junction.BASE_DEMAND] = water_df * map_to_junction[junction_id][ENC.Junction.BASE_DEMAND_AVERAGE]
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
	run_EPANET()

	# SIM STEP 1: SET LOAD AND DEMAND CURVES
	# ------------------------------

	power_factor = 0.0
	power_load_factor = power_df
	object_load.multiplyLoadFactor(power_load_factor, power_factor)
	print('power load factor', power_load_factor)
	# object_junction.multiplyLoadFactor(water_df)
	print('water demand factor', water_df)

	# SIM STEP 2: SET LOAD INTERCONNECTIONS
	# ----------------------------------
	
	object_load.setInterconnectionLoad(interconn_dict)

	# SIM STEP 3: SET GENERATOR DISPATCH
	# ----------------------------------
	
	exports = 0.0 # kW
	losses = 0.0 # kW

	def fun_set_power_dispatch(object_load, object_generator, losses, exports):
		counter = 0
		lost_min = 10000000.0
		while True:
			need_reserves, actual_reserves, nominal_reserves_dict = grb_solvers.unit_commitment_priority_list(object_load, object_generator, losses, exports) # unit commitment is variable
			new_loss = run_OpenDSS(0, True)
			counter += 1

			if math.fabs(losses - new_loss) > 1.0:
				if counter > 199:
					print('Dispatcher - Losses/Exports did not converge')
					sys.exit()
				elif counter > 150:
					while True:
						object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = dispatcher_max
						need_reserves, actual_reserves, nominal_reserves_dict = grb_solvers.unit_commitment_priority_list_2(object_load, object_generator, losses, exports) # unit commitment is input
						new_loss = run_OpenDSS(0, True)
						counter +=1

						if math.fabs(losses - new_loss) < 1.0:
							return need_reserves, actual_reserves, nominal_reserves_dict
						else:
							losses += 0.8 * (new_loss - losses)
				elif counter > 100:
					while True:
						object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = dispatcher_min
						need_reserves, actual_reserves, nominal_reserves_dict = grb_solvers.unit_commitment_priority_list_2(object_load, object_generator, losses, exports) # unit commitment is input
						new_loss = run_OpenDSS(0, True)
						counter +=1

						if math.fabs(losses - new_loss) < 1.0:
							return need_reserves, actual_reserves, nominal_reserves_dict
						else:
							losses += 0.8 * (new_loss - losses)
				elif counter > 50:
					if math.fabs(new_loss) < math.fabs(lost_min):
						lost_min = new_loss
						dispatcher_min = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
					else:
						dispatcher_max = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
				losses += 0.8*(new_loss - losses)
			else:
				return need_reserves, actual_reserves, nominal_reserves_dict

	# node_list_constraint = []
	# node_water_constraint = {1.0: 0.0,
	# 2.0: 0.0,
	# 7.0: 0.0,
	# 13.0: 0.0,
	# 15.0: 0.0,
	# 16.0: 0.0,
	# 18.0: 0.0,
	# 22.0: 0.0,
	# 33.0: 0.0}
	
	need_reserves, actual_reserves, nominal_reserves_dict = fun_set_power_dispatch(object_load, object_generator, losses, exports)
	for generator in object_generator.matrix:
		if generator[ODC.Generator.ID] in [101.0, 102.0, 201.0, 202.0]:
			pass
		else:
			if nominal_reserves_dict[generator[ODC.Generator.ID]] > 0.0 and generator[ODC.Generator.OPERATIONAL_STATUS] == 0.0:
				print('*********************** YOU GOOFED *******************************')
	print('exports #1', 0.5 * (object_cable.matrix[33, ODC.Cable.REAL_POWER_2] - object_cable.matrix[33, ODC.Cable.REAL_POWER_1]))
	print('')

	# SIM STEP 4: SET JUNCTION INTERCONNECTIONS
	# -----------------------------------------

	# SIM STEP 5:
	# Set water tank levels
	# Set water valve flow control
	# ----------------------------
	
	object_curve.matrix = np.array(base_curve_matrix, copy=True)
	object_junction.matrix = np.array(base_junction_matrix, copy=True)
	object_reservoir.matrix = np.array(base_reservoir_matrix, copy=True)
	object_tank.matrix = np.array(base_tank_matrix, copy=True)
	object_pipe.matrix = np.array(base_pipe_matrix, copy=True)
	object_pump.matrix = np.array(base_pump_matrix, copy=True)
	object_valve.matrix = np.array(base_valve_matrix, copy=True)

	object_junction.setInterconnectionDemand(interconn_dict, nominal_reserves_dict)

	artificial_reservoir_id_shift = 1000.0
	max_groundwater_flow = 12399.0 # GPM
	groundwater_id_shift = 2000.0

	# Scale reservoir heads using water_df
	for reservoir in object_reservoir.matrix:
		if reservoir[ENC.Reservoir.ID] < 1000.0:
			reservoir[ENC.Reservoir.TOTAL_HEAD] = max(1.0, water_df) * reservoir[ENC.Reservoir.TOTAL_HEAD]

	# Set valves to maximum amount of groundwater flow
	for junction in object_junction.matrix:
		for valve in object_valve.matrix:
			if valve[ENC.Valve.ID]-groundwater_id_shift == junction[ENC.Junction.ID]:
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
				if map_to_junction[max_pres_id][ENC.Junction.PRESSURE] > (map_to_junction[max_pres_id][ENC.Junction.MIN_PRESSURE]-0.01) and map_to_pipe[max_pres_id][ENC.Pipe.OPERATIONAL_STATUS] == 0.0:
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
				if map_to_reservoir[junction_id][ENC.Reservoir.DEMAND] >= water_df * map_to_junction[junction_id][ENC.Junction.BASE_DEMAND_AVERAGE] + map_to_junction[junction_id][ENC.Junction.INTERCONNECTION_DISPATCH_DEMAND] + map_to_junction[junction_id][ENC.Junction.INTERCONNECTION_RESPONSE_DEMAND]:
					map_to_junction[junction_id][ENC.Junction.BASE_DEMAND] = water_df * map_to_junction[junction_id][ENC.Junction.BASE_DEMAND_AVERAGE] + map_to_junction[junction_id][ENC.Junction.INTERCONNECTION_DISPATCH_DEMAND] + map_to_junction[junction_id][ENC.Junction.INTERCONNECTION_RESPONSE_DEMAND]
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
	run_EPANET()

	# SIM STEP 6: RUN POWER-WATER SIMULATION
	# --------------------------------------

	genid_to_genobject = {}
	juncid_to_genid_water = {}
	reduced_reserves_dict = {}

	for generator in object_generator.matrix:
		genid_to_genobject[generator[ODC.Generator.ID]] = generator

	for junction in object_junction.matrix:
		juncid_to_genid_water[junction[ENC.Junction.ID]] = []
		for generator in object_generator.matrix:
			if junction[ENC.Junction.ID] == generator[ODC.Generator.JUNCTION_ID]:
				juncid_to_genid_water[junction[ENC.Junction.ID]].append((generator[ODC.Generator.ID], generator[ODC.Generator.WATER_CONSUMPTION]))

	for junction in object_junction.matrix:
		if junction[ENC.Junction.BASE_DEMAND_AVERAGE] > 0.0:
			# Water demand is met for nominal reserves
			if junction[ENC.Junction.BASE_DEMAND] >= junction[ENC.Junction.INTERCONNECTION_DISPATCH_DEMAND] + junction[ENC.Junction.INTERCONNECTION_RESPONSE_DEMAND]:
				for genid, _ in juncid_to_genid_water[junction[ENC.Junction.ID]]:
					reduced_reserves_dict[genid] = nominal_reserves_dict[genid]
			elif junction[ENC.Junction.BASE_DEMAND] <= junction[ENC.Junction.INTERCONNECTION_DISPATCH_DEMAND]:
				for genid, _ in juncid_to_genid_water[junction[ENC.Junction.ID]]:
					reduced_reserves_dict[genid] = 0.0
			elif junction[ENC.Junction.INTERCONNECTION_DISPATCH_DEMAND] < junction[ENC.Junction.BASE_DEMAND] < junction[ENC.Junction.INTERCONNECTION_DISPATCH_DEMAND] + junction[ENC.Junction.INTERCONNECTION_RESPONSE_DEMAND]:
				def getWaterConsumption(genid_genwater):
					return genid_genwater[1]

				demand_for_reserves = junction[ENC.Junction.INTERCONNECTION_DISPATCH_DEMAND] + junction[ENC.Junction.INTERCONNECTION_RESPONSE_DEMAND] - junction[ENC.Junction.BASE_DEMAND]
				for genid, genwater in sorted(juncid_to_genid_water[junction[ENC.Junction.ID]], key=getWaterConsumption, reverse=True):
					if demand_for_reserves > 0.0:
						if nominal_reserves_dict[genid] * genid_to_genobject[genid][ODC.Generator.WATER_CONSUMPTION] * 0.001 <= demand_for_reserves:
							reduced_reserves_dict[genid] = 0.0
							demand_for_reserves -= nominal_reserves_dict[genid] * genid_to_genobject[genid][ODC.Generator.WATER_CONSUMPTION] * 0.001
						else:
							fraction = 1.0 - (demand_for_reserves/(nominal_reserves_dict[genid]*0.001*genid_to_genobject[genid][ODC.Generator.WATER_CONSUMPTION]))
							reduced_reserves_dict[genid] = fraction * nominal_reserves_dict[genid]
							demand_for_reserves -= (nominal_reserves_dict[genid] - reduced_reserves_dict[genid]) * genid_to_genobject[genid][ODC.Generator.WATER_CONSUMPTION] * 0.001
					else:
						reduced_reserves_dict[genid] = nominal_reserves_dict[genid]

			else:
				print("ERROR IN CALCULATING REDUCED RESERVES!")

	nominal_reserves_list = []
	reduced_reserves_list = []
	for generator in object_generator.matrix:
		nominal_reserves_list.append(nominal_reserves_dict.get(generator[ODC.Generator.ID], 0.0))
		reduced_reserves_list.append(nominal_reserves_dict.get(generator[ODC.Generator.ID], 0.0) - reduced_reserves_dict.get(generator[ODC.Generator.ID], 0.0))

	with open('C:\\Users\\' + os_username + '\\Documents\\git\\RISE-power-water-ss-1phase\\model_outputs\\analysis_power_water\\power_water_pipe_{}.csv'.format(int(pipe_fail_id)), 'a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow([water_df, power_df, need_reserves, actual_reserves, sum(reduced_reserves_dict.values())] + nominal_reserves_list + reduced_reserves_list)

	# Interconnections have no effect
	# input_list_continuous, input_list_categorical, output_list, input_tensor_continuous, input_tensor_categorical, output_tensor = run_OpenDSS(dss_debug, False)
	# input_list_continuous1, input_list_categorical1, output_list1, input_tensor_continuous1, input_tensor_categorical1, output_tensor1 = run_EPANET()
	# Interconnections have an effect
	# _, _, output_list, _, _, output_tensor = run_OpenDSS(dss_debug, False)
	# _, _, output_list1, _, _, output_tensor1 = run_EPANET()

	# RESULTS STEP 1: FORMAT INPUT/OUTPUT TENSORS
	# -------------------------------------------
	
	# input_list_continuous = input_list_continuous + input_list_continuous1
	# input_list_categorical = input_list_categorical + input_list_categorical1
	# output_list = output_list + output_list1

	# input_tensor_continuous = np.concatenate((input_tensor_continuous, input_tensor_continuous1), axis=0)
	# input_tensor_categorical = np.concatenate((input_tensor_categorical, input_tensor_categorical1), axis=0)
	# output_tensor = np.concatenate((output_tensor, output_tensor1), axis=0)

	# RESULTS STEP 2: WRITE INPUT/OUTPUT TENSORS TO FILE
	# --------------------------------------------------
	
	# if write_cols:
	# 	with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/tensor_outputs/input_list_continuous_columns.csv', 'w') as f:
	# 		writer = csv.writer(f, delimiter=',')
	# 		writer.writerow(input_list_continuous)
	# 	with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/tensor_outputs/input_list_categorical_columns.csv', 'w') as f:
	# 		writer = csv.writer(f, delimiter=',')
	# 		writer.writerow(input_list_categorical)
	# 	with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/tensor_outputs/output_list_columns.csv', 'w') as f:
	# 		writer = csv.writer(f, delimiter=',')
	# 		writer.writerow(output_list)

	# with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/tensor_outputs/input_tensor_continuous.csv', 'ab') as f:
	# 	np.savetxt(f, input_tensor_continuous[None, :], fmt='%0.6f', delimiter=' ', newline='\n')
	# with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/tensor_outputs/input_tensor_categorical.csv', 'ab') as f:
	# 	np.savetxt(f, input_tensor_categorical[None, :], fmt='%0.6f', delimiter=' ', newline='\n')
	# with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/tensor_outputs/output_tensor.csv', 'ab') as f:
	# 	np.savetxt(f, output_tensor[None, :], fmt='%0.6f', delimiter=' ', newline='\n')

	# END SIMULATION
	# --------------

if __name__ == '__main__':
	write_cols = False # Write column names to seperate file
	dss_debug = 0

	power_df = float(sys.argv[1])
	water_df = float(sys.argv[2])
	pipe_fid = float(sys.argv[3])

	main(dss_debug, write_cols, power_df, water_df, pipe_fid)