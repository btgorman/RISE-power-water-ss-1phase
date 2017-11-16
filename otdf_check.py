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
import classes_power as ODC
import classes_interconnection as ICC
import grb_solvers

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

	csv_xycurve = pd.read_csv('./data_power/network-power/1000xycurve.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_regcontrol = pd.read_csv('./data_power/network-power/1100regcontrol.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_wiredata = pd.read_csv('./data_power/network-power/1200wiredata.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_linecode = pd.read_csv('./data_power/network-power/1201linecode.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_bus = pd.read_csv('./data_power/network-power/1300bus.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_vsource = pd.read_csv('./data_power/network-power/1301vsource.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	# this uses a custom generator data file
	csv_generator = pd.read_csv('./data_power/network-power/1302generator_ptdf.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_load = pd.read_csv('./data_power/network-power/1303load.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_solarpv = pd.read_csv('./data_power/network-power/1304solarpv.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_windturbine = pd.read_csv('./data_power/network-power/1305windturbine.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_directconnection = pd.read_csv('./data_power/network-power/1400directconnection.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_cable = pd.read_csv('./data_power/network-power/1401cable.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_overheadline = pd.read_csv('./data_power/network-power/1402overheadline.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_twowindingtransformer = pd.read_csv('./data_power/network-power/1403twowindingtransformer.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_capacitor = pd.read_csv('./data_power/network-power/1404capacitor.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_reactor = pd.read_csv('./data_power/network-power/1405reactor.csv', sep=',', header=1, index_col=None, dtype=np.float64)

	csv_pumpload = pd.read_csv('./data_interconnection/network-interconnection/9000pump-load.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_tankgenerator = pd.read_csv('./data_interconnection/network-interconnection/9001tank-generator.csv', sep=',', header=1, index_col=None, dtype=np.float64)

	# -----------------
	# CREATE COMPONENTS
	# -----------------

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

	object_list = [object_vsource, object_bus, object_generator, object_load, object_solarpv, object_windturbine, #NODES
	object_xycurve, object_wiredata, object_linecode, #OTHERS
	object_directconnection, object_cable, object_overheadline, object_twowindingtransformer, object_capacitor, object_reactor, # CONNECTIONS
	object_regcontrol] # CONTROLS

	interconn_dict = {'pumpload': object_pumpload, 'tankgenerator': object_tankgenerator,
	'load': object_load,
	'generator': object_generator}

	# ---------
	# RUN OPENDSS
	# ---------

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


	# SIM STEP 1: SET LOAD CURVES
	# ------------------------------
	# ensures power factor of 0.95
	power_factor_factor = (math.sqrt(1.0**2 - 0.95**2) / 0.95)
	real_load_factor = 0.5
	reactive_load_factor = 0.0
	object_load.multiplyLoadFactor(real_load_factor, power_factor_factor)

	# SIM STEP 2: SET GENERATOR DISPATCH
	# ----------------------------------
	object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = real_load_factor * object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING]
	# almost zeros out reactive power in the network
	object_generator.matrix[:, ODC.Generator.REACTIVE_GENERATION] = object_generator.matrix[:, ODC.Generator.REAL_GENERATION] * power_factor_factor * 0.8467

	# SIM STEP 3: RUN POWER-WATER SIMULATION
	# --------------------------------------
	lodf_tab = pd.DataFrame.from_csv('tables\lodf.csv', header=0, index_col=0)
	ptdf_tab = pd.DataFrame.from_csv('tables\ptdf.csv', header=0, index_col=0)

	run_OpenDSS(dss_debug, False)
	branch_id_base = object_cable.matrix[:, ODC.Cable.ID]
	branch_real_power_base = np.array(0.5*(object_cable.matrix[:, ODC.Cable.REAL_POWER_2] - object_cable.matrix[:, ODC.Cable.REAL_POWER_1]), copy=True)

	# countcount = 0
	# ptdf_estimator = np.array(object_cable.matrix[:, ODC.Cable.ID], copy=True)*0
	# for gen in object_generator.matrix:
	# 	delta = 0.3 * gen[ODC.Generator.REAL_GENERATION_MAX_RATING]
	# 	object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = real_load_factor * object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING]
	# 	gen[ODC.Generator.REAL_GENERATION] += delta
	# 	run_OpenDSS(dss_debug, False)
	# 	branch_real_power = np.array(0.5*(object_cable.matrix[:, ODC.Cable.REAL_POWER_2] - object_cable.matrix[:, ODC.Cable.REAL_POWER_1]), copy=True)
	# 	branch_delta = branch_real_power - branch_real_power_base

	# 	ptdf_estimator = np.array(ptdf_tab.loc[int(gen[ODC.Generator.ID])])
	# 	if countcount >= 0:
	# 		print(max(np.absolute(branch_delta - delta*ptdf_estimator)))
	# 		print(max((branch_delta - delta*lodf_estimator)/(0.5* branch_real_power+branch_real_power_base)))
	# 		print(min((branch_delta - delta*lodf_estimator)/(0.5* branch_real_power+branch_real_power_base)))
	# 		print('')
	# 		countcount += 1

	# countcount = 0
	# lodf_estimator = np.array(object_cable.matrix[:, ODC.Cable.ID], copy=True)*0
	# for cable in object_cable.matrix:
	# 	if cable[ODC.Cable.ID] != 100.0:
	# 		object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A] = 1.0
	# 		cable[ODC.Cable.OPERATIONAL_STATUS_A] = 0.0
	# 		for iditer in range(0, len(branch_id_base)):
	# 			if cable[ODC.Cable.ID] == branch_id_base[iditer]:
	# 				delta = math.fabs(branch_real_power_base[iditer])
	# 		run_OpenDSS(dss_debug, False)
	# 		branch_real_power = np.array(0.5*(object_cable.matrix[:, ODC.Cable.REAL_POWER_2] - object_cable.matrix[:, ODC.Cable.REAL_POWER_1]), copy=True)
	# 		branch_delta = branch_real_power - branch_real_power_base

	# 		lodf_estimator = np.array(lodf_tab.loc[int(cable[ODC.Cable.ID])])
	# 		if countcount >= 0:
	# 			print(max(np.absolute(branch_delta - delta*lodf_estimator)))
	# 			print(max((branch_delta - delta*lodf_estimator)/(0.5* branch_real_power+branch_real_power_base)))
	# 			print(min((branch_delta - delta*lodf_estimator)/(0.5* branch_real_power+branch_real_power_base)))
	# 			print('')
	# 			countcount +=1
	
	countcount = 0
	delta_percent = 0.5
	lodf_estimator = np.array(object_cable.matrix[:, ODC.Cable.ID], copy=True)*0
	ptdf_estimator = np.array(object_cable.matrix[:, ODC.Cable.ID], copy=True)*0
	for cable in object_cable.matrix:
		if cable[ODC.Cable.ID] != 100.0:
			object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = real_load_factor * object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING]
			object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A] = 1.0
			cable[ODC.Cable.OPERATIONAL_STATUS_A] = 0.0
			run_OpenDSS(dss_debug, False)
			branch_real_power_line_base = np.array(0.5*(object_cable.matrix[:, ODC.Cable.REAL_POWER_2] - object_cable.matrix[:, ODC.Cable.REAL_POWER_1]), copy=True)
			print(cable[ODC.Cable.ID])

			maxerror = 0.0
			for gen in object_generator.matrix:
				delta_kw = delta_percent * gen[ODC.Generator.REAL_GENERATION_MAX_RATING]
				object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = real_load_factor * object_generator.matrix[:, ODC.Generator.REAL_GENERATION_MAX_RATING]
				gen[ODC.Generator.REAL_GENERATION] += delta_kw
				run_OpenDSS(dss_debug, False)
				branch_real_power = np.array(0.5*(object_cable.matrix[:, ODC.Cable.REAL_POWER_2] - object_cable.matrix[:, ODC.Cable.REAL_POWER_1]), copy=True)
				branch_delta = branch_real_power - branch_real_power_line_base

				ptdf_estimator = np.array(ptdf_tab.loc[int(gen[ODC.Generator.ID])])
				lodf_estimator = np.array(lodf_tab.loc[int(cable[ODC.Cable.ID])])
				lodf_val = - lodf_tab.loc[int(cable[ODC.Cable.ID])][str(int(cable[ODC.Cable.ID]))]
				otdf_val = ptdf_tab.loc[int(gen[ODC.Generator.ID])][str(int(cable[ODC.Cable.ID]))]

				if countcount >= 0:
					maxerror = max(maxerror, max(np.absolute(branch_delta - delta_kw*(ptdf_estimator + lodf_val*lodf_estimator*otdf_val))))
				countcount += 1
			print(maxerror)
			print('')


	# for b in range(0, branches):
	# 	for g in range(0, generators):
	# 		otdf[g, b] = ptdf_tab.loc[float(g)][str(b)] + lodf_tab.loc[float(o)][str(b)] * ptdf_tab[float(g)][str(o)]

	###############################
	
	
	

	# END
	# ---

if __name__ == '__main__':
	write_cols = False # Write column names to seperate file
	dss_debug = 0

	main(dss_debug, write_cols)