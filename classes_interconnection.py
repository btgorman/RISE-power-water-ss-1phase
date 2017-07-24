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

# LAST EDITED: JUNE 16, 2017
# BUILT USING PYTHON 3.6.0

import numpy as np
import pandas as pd

class PumpLoad:
	CLID = 9000
	
	ID = 0
	TYPE = 1
	LOAD_ID = 2
	PUMP_ID = 3
	CHECK_LOAD_DEMAND = 4
	CHECK_PUMP_STATUS = 5

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 0
		self.num_stochastic = self.num_components * 0
		self.switch_chance = (0.0, 0.0)
		self.stochastic_chance = (0.0, 0.0)

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('INTERCONN ERROR in PumpLoad0')

	def PumpRow(self, ID):
		for row in self.matrix:
			if row[PumpLoad.PUMP_ID] == ID:
				return row
		return 0

	def LoadRow(self, ID):
		for row in self.matrix:
			if row[PumpLoad.LOAD_ID] == ID:
				return row
		return 0

class TankGenerator:
	CLID = 9001
	
	ID = 0
	TYPE = 1
	GENERATOR_ID = 2
	JUNCTION_ID = 3
	TANK_ID = 4
	CHECK_GENERATOR_PRODUCTION = 5
	CHECK_TANK_LEVEL = 6

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 0
		self.num_stochastic = self.num_components * 0
		self.switch_chance = (0.0, 0.0)
		self.stochastic_chance = (0.0, 0.0)

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('INTERCONN ERROR in TankGenerator0')

	def GeneratorRow(self, ID):
		for row in self.matrix:
			if row[TankGenerator.GENERATOR_ID] == ID:
				return row
		return 0

	def JunctionRow(self, ID):
		for row in self.matrix:
			if row[TankGenerator.JUNCTION_ID] == ID:
				return row
		return 0

	def TankRow(self, ID):
		for row in self.matrix:
			if row[TankGenerator.TANK_ID] == ID:
				return row
		return 0
