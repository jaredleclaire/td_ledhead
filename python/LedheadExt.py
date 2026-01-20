"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from TDStoreTools import StorageManager
import TDFunctions as TDF

class LedheadExt:
	"""
	LedheadExt description
	"""
	# Operator path constants
	OP_NULL_PARS = 'null_pars'
	OP_OUT_NATIVE = 'out_native'
	OP_OUT_DESIGN = 'out_design'
	OP_OUT_MATTE = 'out_matte'
	OP_CONTAINER_REPLICATOR = 'container1/replicator1'
	OP_REPLICATOR = 'replicator1'
	
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

		# properties
		TDF.createProperty(self, 'MyProperty', value=0, dependable=True,
						   readOnly=False)

		# attributes:
		self.a = 0 # attribute
		self.B = 1 # promoted attribute

		# stored items (persistent across saves and re-initialization):
		storedItems = [
			# Only 'name' is required...
			{'name': 'StoredProperty', 'default': None, 'readOnly': False,
			 						'property': True, 'dependable': True},
		]
		# Uncomment the line below to store StoredProperty. To clear stored
		# 	items, use the Storage section of the Component Editor
		
		# self.stored = StorageManager(self, ownerComp, storedItems)

	# adjusts design resolution based on scale factor without augmenting aspect ratio
	def setDesignRes(self, tile_res_x, tile_res_y):
		return
	
	# PROMOTED EXTENSIONS
	# checks which maps are toggled for output and saves them to the specified directory
	def SavePatterns(self):
		try:
			outputNative = op(self.OP_NULL_PARS)['Outputnative']
			outputDesign = op(self.OP_NULL_PARS)['Outputdesign']
			outputMatte = op(self.OP_NULL_PARS)['Outputmatte']
			
			version = str(parent.Ledhead.par.Version).zfill(2)
			screenName = str(parent.Ledhead.par.Screenname).lower().replace(' ', '-')
			screenLetter = str(parent.Ledhead.par.Screenletter).lower().replace(' ', '')
			savePath = parent.Ledhead.par.Savepath
			
			if not savePath:
				print('Error: Save path is empty')
				return
			
			# Define output configurations
			outputs = [
				(outputNative, self.OP_OUT_NATIVE, 'native'),
				(outputDesign, self.OP_OUT_DESIGN, 'design'),
				(outputMatte, self.OP_OUT_MATTE, 'matte'),
			]
			
			for should_save, op_name, output_type in outputs:
				if should_save:
					file_path = f'{savePath}/{screenLetter}_{screenName}_{output_type}_v{version}.png'
					print(f'Saving {output_type}: {file_path}')
					op(op_name).save(file_path)
				else:
					print(f'{output_type} save bypassed')
			
			print('All patterns saved successfully')
			
		except AttributeError as e:
			print(f'Error: Missing parameter - {e}')
		except IOError as e:
			print(f'Error: File I/O error - {e}')
		except Exception as e:
			print(f'Error saving patterns: {e}')
		
		return
	
	# sets color scheme for the screen
	def SetColor(self, r, g, b):

		parent.Ledhead.parGroup.Colora = (r,g,b)
		parent.Ledhead.parGroup.Colorb = (r * 0.5, g * 0.5, b * 0.5)

		return
	
	# opens a floating editor for editing tile appearance
	def EditTile(self):

		p = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name="Output")
		p.owner = op('container1/button1')

	# applies scaling mode logic and calculates design resolution
	def ApplyScalingMode(self, mode):
		"""
		Calculates design resolution based on the selected scaling mode.
		Scaling modes:
		- 'density': Scale based on target pixel density (pixels per unit)
		- 'manual': Use manually specified design resolution
		- 'factor': Scale using a multiplication factor
		- 'bypass': Use native resolution without scaling
		
		Density units: mm, cm, m, in, ft
		Density value represents: pixels per [selected unit]
		"""
		
		native_res_w = int(parent.Ledhead.par.Screenresolutionw)
		native_res_h = int(parent.Ledhead.par.Screenresolutionh)
		
		if mode == 'density':
			# Calculate design resolution based on pixel density (pixels per unit)
			target_density = float(parent.Ledhead.par.Targetdensity)
			density_unit = str(parent.Ledhead.par.Densityunit).lower()
			
			# Get physical screen dimensions in meters
			screen_width_m = parent.Ledhead.parGroup.Screensizem[0]
			screen_height_m = parent.Ledhead.parGroup.Screensizem[1]
			
			# Convert from meters to selected unit
			meter_to_unit = {
				'mm': 1000.0,    # 1 meter = 1000 mm
				'cm': 100.0,     # 1 meter = 100 cm
				'm': 1.0,        # 1 meter = 1 m
				'in': 39.3701,   # 1 meter = 39.3701 inches
				'ft': 3.28084,   # 1 meter = 3.28084 feet
			}
			
			if density_unit in meter_to_unit:
				conversion_factor = meter_to_unit[density_unit]
				screen_width_unit = screen_width_m * conversion_factor
				screen_height_unit = screen_height_m * conversion_factor
			else:
				# Default to meters if unknown unit
				screen_width_unit = screen_width_m
				screen_height_unit = screen_height_m
			
			# Calculate design resolution from physical dimensions and density
			# design_res = physical_dimension * pixels_per_unit
			design_res_w = max(int(screen_width_unit * target_density), 1)
			design_res_h = max(int(screen_height_unit * target_density), 1)
			
		elif mode == 'manual':
			# Use manually specified resolution
			manual_res = parent.Ledhead.parGroup.Manualresolution
			design_res_w = int(manual_res[0])
			design_res_h = int(manual_res[1])
			
		elif mode == 'factor':
			# Scale using a multiplication factor
			scale_factor = float(parent.Ledhead.par.Scalefactor)
			design_res_w = max(int(native_res_w * scale_factor), 1)
			design_res_h = max(int(native_res_h * scale_factor), 1)
			
		elif mode == 'bypass':
			# Use native resolution without scaling
			design_res_w = native_res_w
			design_res_h = native_res_h
			
		else:
			# Default to bypass if unknown mode
			design_res_w = native_res_w
			design_res_h = native_res_h
		
		# Apply calculated design resolution
		parent.Ledhead.parGroup.Screendesignresolution = (design_res_w, design_res_h)
		
		print(f'Scaling Mode: {mode} | Native: {native_res_w}x{native_res_h} | Design: {design_res_w}x{design_res_h}')
		
		return (design_res_w, design_res_h)
	
	# re-generates screen pattern
	def Reinit(self):
		try:
			op(self.OP_CONTAINER_REPLICATOR).par.recreateall.pulse()
			op(self.OP_REPLICATOR).par.recreateall.pulse()
		except Exception as e:
			print(f'Error reinitializing pattern: {e}')
		return