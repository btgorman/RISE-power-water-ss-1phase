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

import classes_water as ENC
import classes_power as ODC
import classes_interconnection as ICC

from comtypes import automation
import win32com.client
# from win32com.client import makepy
# import sys
# sys.argv = ['makepy', 'OpenDSSEngine.DSS']
# makepy.main()

def main(dss_debug, write_cols):
	os_username = os.getlogin()

	# --------------
	# READ CSV FILES
	# --------------

	csv_curve = pd.read_csv('./data_water/network-water/2000curve.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_junction = pd.read_csv('./data_water/network-water/2100junction.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_reservoir = pd.read_csv('./data_water/network-water/2101reservoir.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_tank = pd.read_csv('./data_water/network-water/2102tank.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_pipe = pd.read_csv('./data_water/network-water/2200pipe.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_pump = pd.read_csv('./data_water/network-water/2201pump.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_valve = pd.read_csv('./data_water/network-water/2202valve.csv', sep=',', header=1, index_col=None, dtype=np.float32)

	csv_xycurve = pd.read_csv('./data_power/network-power/1000xycurve.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_regcontrol = pd.read_csv('./data_power/network-power/1100regcontrol.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_wiredata = pd.read_csv('./data_power/network-power/1200wiredata.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_linecode = pd.read_csv('./data_power/network-power/1201linecode.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_bus = pd.read_csv('./data_power/network-power/1300bus.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_vsource = pd.read_csv('./data_power/network-power/1301vsource.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_generator = pd.read_csv('./data_power/network-power/1302generator.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_load = pd.read_csv('./data_power/network-power/1303load.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_solarpv = pd.read_csv('./data_power/network-power/1304solarpv.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_windturbine = pd.read_csv('./data_power/network-power/1305windturbine.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_directconnection = pd.read_csv('./data_power/network-power/1400directconnection.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_cable = pd.read_csv('./data_power/network-power/1401cable.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_overheadline = pd.read_csv('./data_power/network-power/1402overheadline.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_twowindingtransformer = pd.read_csv('./data_power/network-power/1403twowindingtransformer.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_capacitor = pd.read_csv('./data_power/network-power/1404capacitor.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_reactor = pd.read_csv('./data_power/network-power/1405reactor.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	# csv_allcolumns= pd.read_csv('./data_power/network-power/allcolumns.csv', sep=',', header=1, index_col=None, dtype=np.float32)

	csv_pumpload = pd.read_csv('./data_interconnection/network-interconnection/9000pump-load.csv', sep=',', header=1, index_col=None, dtype=np.float32)
	csv_tankgenerator = pd.read_csv('./data_interconnection/network-interconnection/9001tank-generator.csv', sep=',', header=1, index_col=None, dtype=np.float32)

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

	object_pumpload = ICC.PumpLoad(csv_pumpload)
	object_tankgenerator = ICC.TankGenerator(csv_tankgenerator)

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

	interconn_dict = {'pumpload': object_pumpload, 'tankgenerator': object_tankgenerator,
	'pump': object_pump, 'load': object_load, 'tank': object_tank,
	'generator': object_generator, 'junction': object_junction}

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
			templist = ['Duration', '0:00:10']
			writer.writerow(templist)
			templist = ['Hydraulic', 'Timestep', '0:00:10']
			writer.writerow(templist)
			templist = ['Quality', 'Timestep', '0:05']
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
			templist = ['Headloss', 'H-W']
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
				print(4, 'ERRORCODE is', errorcode)

			for water_object in w_object_list:
				water_object.readAllENoutputs(epalib)

			errorcode = epalib.ENnextH(timestep)
			if errorcode != 0:
				print(5, 'ERRORCODE is', errorcode)

			if timestep.contents.value == 0:
				break

		errorcode = epalib.ENcloseH()
		if errorcode != 0:
			print(6, 'ERRORCODE is', errorcode)

		errorcode = epalib.ENclose()
		if errorcode != 0:
			print(7, 'ERRORCODE is', errorcode)

		input_list_continuous = []
		input_list_categorical = []
		input_tensor_continuous = np.empty([0,0], dtype=np.float32).flatten()
		input_tensor_categorical = np.empty([0,0], dtype=np.float32).flatten()
		for object in w_object_list:
			list_continuous, list_categorical, tensor_continuous, tensor_categorical = object.convertToInputTensor()
			input_list_continuous = input_list_continuous + list_continuous
			input_list_categorical = input_list_categorical + list_categorical
			input_tensor_continuous = np.concatenate((input_tensor_continuous, tensor_continuous), axis=0)
			input_tensor_categorical = np.concatenate((input_tensor_categorical, tensor_categorical), axis=0)

		output_list = []
		output_tensor = np.empty([0,0], dtype=np.float32).flatten()
		for object in w_object_list:
			o_list, o_tensor = object.convertToOutputTensor()
			output_list = output_list + o_list
			output_tensor = np.concatenate((output_tensor, o_tensor), axis=0)

		return input_list_continuous, input_list_categorical, output_list, input_tensor_continuous, input_tensor_categorical, output_tensor

	def run_OpenDSS(dss_debug, flag_solve_dispatch):
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

		# ALGORITHM to set power dispatch schedule
		# ----------------------------------------
		# CAISO contingency (spinning) reserve is max(5% of hydro-loads + 7% of other-loads, largest contingency) + 100% of interruptible imports
		# CAISO spinning reserves is 50% of operating reserves
		if flag_solve_dispatch == 1:
			# Calculate required contingency reserves (MW)
			max_cont_generator = max(object_generator.matrix[:, object_generator.REAL_GENERATION])
			total_load = sum(object_load.matrix[:, object_load.REAL_LOAD])
			print('Total Load: {} MW'.format(total_load*0.001))
			total_generation = sum(object_generator.matrix[:, object_generator.REAL_GENERATION])
			print('Total Gen: {} MW'.format(total_generation*0.001))
			for hydro_elem in object_generator.matrix:
				if (int(hydro_elem[object_generator.ID]) % 100) == 22:
					hydro_load = 0
					hydro_load += hydro_elem[object_generator.REAL_GENERATION]
			print('Total Hydro Load: {} MW'.format(hydro_load*0.001))
			sc_reserve_require = max(0.05*(hydro_load) + 0.07*(total_load-hydro_load), max_cont_generator)
			print('Required Contingency Reserve: {} MW'.format(sc_reserve_require*0.001))

			# Calculate available contingency reserves (MW)
			is_combustion_turbine = {101: True, 201: True, 102: True, 202: True}
			sc_reserve_avail = 0.0
			for gen_elem in object_generator.matrix:
				if is_combustion_turbine.get(int(gen_elem[object_generator.ID]), False):
					sc_reserve_avail += min(gen_elem[object_generator.REAL_GENERATION_MAX_RATING] - gen_elem[object_generator.REAL_GENERATION], gen_elem[object_generator.RAMP_RATE]*10)
				elif gen_elem[object_generator.REAL_GENERATION] > 0.0:
					sc_reserve_avail += min(gen_elem[object_generator.REAL_GENERATION_MAX_RATING] - gen_elem[object_generator.REAL_GENERATION], gen_elem[object_generator.RAMP_RATE]*10)
				# else:
				# 	print(min(gen_elem[object_generator.REAL_GENERATION_MAX_RATING] - gen_elem[object_generator.REAL_GENERATION], gen_elem[object_generator.RAMP_RATE]*10)*0.001)
			print('Available Contingecy Reserve: {} MW'.format(sc_reserve_avail*0.001))

			# # Identify sourcebus connector
			# for line_elem in object_directconnection.matrix:
			# 	if line_elem[object_directconnection.TERMINAL_1_ID] == 0.0:
			# 		dssCkt.Lines.Name = str(int(line_elem[object_directconnection.TYPE])) + '_' + str(int(line_elem[object_directconnection.ID]))
			# 	elif line_elem[object_directconnection.TERMINAL_2_ID] == 0.0:
			# 		dssCkt.Lines.Name = str(int(line_elem[object_directconnection.TYPE])) + '_' + str(int(line_elem[object_directconnection.ID]))

		dssText.Command = 'Set VoltageBases={}'.format(list(set_voltagebase))
		dssText.Command = 'CalcVoltageBases'
		dssText.Command = 'Solve BaseFrequency=60 MaxIter=300'

		if flag_solve_dispatch == 0:
			dssText.Command = 'Save Circuit'
			dssText.Command = 'Export Summary (summary.csv)'
			dssText.Command = 'Export Currents (currents.csv)'
			dssText.Command = 'Export Voltages (voltages.csv)'
			dssText.Command = 'Export Overloads (overloads.csv)'
			dssText.Command = 'Export Powers kVA (powers.csv)'

		variant_buses = automation.VARIANT()
		variant_voltages_mag = automation.VARIANT()
		variant_voltages_pu = automation.VARIANT()
		variant_currents = automation.VARIANT()
		variant_powers = automation.VARIANT()

		for object in object_list:
			object.readAllDSSOutputs(dssCkt, dssActvElem, dssActvBus, variant_buses, variant_voltages_mag, variant_voltages_pu, variant_currents, variant_powers)

		input_list_continuous = []
		input_list_categorical = []
		input_tensor_continuous = np.empty([0,0], dtype=np.float32).flatten()
		input_tensor_categorical = np.empty([0,0], dtype=np.float32).flatten()
		for object in object_list:
			list_continuous, list_categorical, tensor_continuous, tensor_categorical = object.convertToInputTensor()
			input_list_continuous = input_list_continuous + list_continuous
			input_list_categorical = input_list_categorical + list_categorical
			input_tensor_continuous = np.concatenate((input_tensor_continuous, tensor_continuous), axis=0)
			input_tensor_categorical = np.concatenate((input_tensor_categorical, tensor_categorical), axis=0)

		output_list = []
		output_tensor = np.empty([0,0], dtype=np.float32).flatten()
		for object in object_list:
			o_list, o_tensor = object.convertToOutputTensor()
			output_list = output_list + o_list
			output_tensor = np.concatenate((output_tensor, o_tensor), axis=0)

		return input_list_continuous, input_list_categorical, output_list, input_tensor_continuous, input_tensor_categorical, output_tensor

	# SIM STEP 1: SET LOAD CURVES
	# ------------------------------
	power_load_mu = -0.515408 # lognormal, AIC -9266.47
	power_load_sigma = 0.238325 # lognormal, AIC -9266.47
	power_load_factor = min(np.random.lognormal(power_load_mu, power_load_sigma, 1)[0], 1.0)
	power_load_factor = max(power_load_factor, 0.2)
	# TO DO: fix the water model and add water_load_factor function
	water_load_factor = min(0.5, 1.0)
	water_load_factor = max(water_load_factor, 0.1)
	print('power load factor is {}'.format(power_load_factor))
	object_load.multiplyLoadFactor(power_load_factor)

	# SIM STEP 2: SET GENERATOR DISPATCH
	# ----------------------------------
	flag_solve_dispatch = 1
	gen_prio_list_mul = {
	# priority: mult threshold turb1 turb2 turb3 ....
	0: (0.0, 0.0),
	1: (1.00000, 100.0000*1000.),
	2: (1.00000, 366.6667*1000.),
	3: (0.88574, 470.0033*1000.),
	4: (0.80545, 636.6700*1000.),
	5: (0.73671, 711.3233*1000.),
	6: (0.84772, 878.3233*1000.),
	7: (0.30010, 908.3333*1000.),
	8: (0.16750, 911.6833*1000.),
	9: (0.00000, 911.6833*1000.),
	10:(1.00000, 925.0133*1000.),
	11:(1.00000, 965.0133*1000.)
	}
	gen_prio_list_key = {
	# id: [priority_1, priority_2]
	122: [1],
	222: [1],
	322: [1],
	422: [1],
	522: [1],
	622: [1],
	118: [2],
	121: [2],
	323: [3, 10],
	615: [4, 11],
	116: [4, 11],
	123: [4, 11],
	223: [4, 11],
	301: [5],
	401: [5],
	302: [5],
	402: [5],
	113: [6],
	213: [6],
	313: [6],
	107: [7],
	207: [7],
	307: [7],
	115: [8],
	215: [8],
	315: [8],
	415: [8],
	515: [8],
	101: [9],
	201: [9],
	102: [9],
	202: [9]
	}
	total_load = sum(object_load.matrix[:, object_load.REAL_LOAD])
	print('Total Load: {} MW'.format(total_load*0.001))
	for row in object_generator.matrix:
		keys = gen_prio_list_key[int(row[object_generator.ID])]
		row[object_generator.REAL_GENERATION] = 0.0
		for elem in keys:
			_,  low_threshold = gen_prio_list_mul[elem-1]
			factor, high_threshold = gen_prio_list_mul[elem]
			if total_load >= high_threshold:
				row[object_generator.REAL_GENERATION] = factor * row[object_generator.REAL_GENERATION_MAX_RATING]
			elif total_load >= low_threshold and total_load < high_threshold:
				cur_factor = row[object_generator.REAL_GENERATION] / row[object_generator.REAL_GENERATION_MAX_RATING]
				factorfactor = (total_load - low_threshold) / (high_threshold - low_threshold)
				row[object_generator.REAL_GENERATION] = (factorfactor*(factor-cur_factor) + cur_factor) * row[object_generator.REAL_GENERATION_MAX_RATING]

	run_OpenDSS(0, flag_solve_dispatch)

	# SIM STEP 3: RUN POWER-WATER SIMULATION
	# --------------------------------------
	input_list_continuous, input_list_categorical, _, input_tensor_continuous, input_tensor_categorical, _ = run_OpenDSS(dss_debug, 0)
	input_list_continuous1, input_list_categorical1, _, input_tensor_continuous1, input_tensor_categorical1, _ = run_EPANET()
	_, _, output_list, _, _, output_tensor = run_OpenDSS(dss_debug, 0)
	_, _, output_list1, _, _, output_tensor1 = run_EPANET()

	# RESULTS STEP 1: FORMAT INPUT/OUTPUT TENSORS
	# -------------------------------------------
	input_list_continuous = input_list_continuous + input_list_continuous1
	input_list_categorical = input_list_categorical + input_list_categorical1
	output_list = output_list + output_list1

	input_tensor_continuous = np.concatenate((input_tensor_continuous, input_tensor_continuous1), axis=0)
	input_tensor_categorical = np.concatenate((input_tensor_categorical, input_tensor_categorical1), axis=0)
	output_tensor = np.concatenate((output_tensor, output_tensor1), axis=0)

	# RESULTS STEP 2: WRITE INPUT/OUTPUT TENSORS TO FILE
	# --------------------------------------------------
	if write_cols:
		with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/outputs/input_list_continuous_columns.csv', 'w') as f:
			writer = csv.writer(f, delimiter=',')
			writer.writerow(input_list_continuous)
		with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/outputs/input_list_categorical_columns.csv', 'w') as f:
			writer = csv.writer(f, delimiter=',')
			writer.writerow(input_list_categorical)
		with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/outputs/output_list_columns.csv', 'w') as f:
			writer = csv.writer(f, delimiter=',')
			writer.writerow(output_list)

	with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/outputs/input_tensor_continuous.csv', 'ab') as f:
		np.savetxt(f, input_tensor_continuous[None, :], fmt='%0.6f', delimiter=' ', newline='\n')
	with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/outputs/input_tensor_categorical.csv', 'ab') as f:
		np.savetxt(f, input_tensor_categorical[None, :], fmt='%0.6f', delimiter=' ', newline='\n')
	with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/outputs/output_tensor.csv', 'ab') as f:
		np.savetxt(f, output_tensor[None, :], fmt='%0.6f', delimiter=' ', newline='\n')

	# END
	# ---

if __name__ == '__main__':
	write_cols = False # Write column names to seperate file
	dss_debug = 0

	main(dss_debug, write_cols)





























# ///////////////////////////////////////////////////////////////////////////////////
# OLD STUFF
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