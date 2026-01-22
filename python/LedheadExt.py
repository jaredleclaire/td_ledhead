"""
Ledhead Extension Module

Provides LED screen configuration, scaling, and pattern management for TouchDesigner.
Handles multiple resolution scaling modes, calculates screen properties (aspect ratio,
physical dimensions, pixel density), and manages pattern export and visualization.

Access via: parent.Ledhead.ext (if promoted) or op('ledhead_component').ext

API OVERVIEW:
=============

Scaling Modes:
  - density: Calculate design resolution from pixel density and physical screen size
  - manual: Use manually specified design resolution values
  - factor: Scale native resolution by a multiplication factor
  - bypass: Use native resolution without scaling

Custom Component Parameters (automatically calculated and updated):
  - Screenresolution: Native screen resolution in pixels
  - Screendesignresolution: Scaled design resolution in pixels
  - Screenaspectratio: Screen aspect ratio as formatted string (e.g., "1.78:1")
  - Screensizem: Physical screen dimensions in meters
  - Screensizeft: Physical screen dimensions in feet
  - Nativepixeldensity: Screen pixel density in PPI (pixels per inch)
  - Tilecount: Total number of tiles

Main Methods:
  - ApplyScalingMode(mode, verbose=True, round_to_even=False, preserve_aspect=False)
  - UpdateDerivedProperties()
  - SavePatterns()
  - SetColor(r, g, b)
  - Reinit()
  - EditTile()

Example Usage:
  # Apply scaling with aspect ratio preservation
  parent.Ledhead.ext.ApplyScalingMode('density', preserve_aspect=True, round_to_even=True)
  
  # Set color scheme
  parent.Ledhead.ext.SetColor(1.0, 0.5, 0.2)
  
  # Regenerate tiles
  parent.Ledhead.ext.Reinit()
"""

class LedheadExt:
	"""
	Ledhead LED Screen Extension.
	
	Manages LED screen configuration with support for:
	- Multiple resolution scaling modes (density-based, manual, factor-based, bypass)
	- Automatic derived property calculation (aspect ratio, physical dimensions, pixel density)
	- Post-processing adjustments (even number rounding, aspect ratio preservation)
	- Pattern export and visualization
	- Tile configuration and replication
	- Color scheme management
	"""
	
	# ============================================================================
	# CLASS CONSTANTS
	# ============================================================================
	
	# Operator path constants for pattern output
	OP_NULL_PARS = 'null_pars'
	OP_OUT_NATIVE = 'out_native'
	OP_OUT_DESIGN = 'out_design'
	OP_OUT_MATTE = 'out_matte'
	OP_CONTAINER_REPLICATOR = 'container1/replicator1'
	OP_REPLICATOR = 'replicator1'
	
	# Conversion factors
	METER_TO_MM = 1000.0
	METER_TO_CM = 100.0
	METER_TO_IN = 39.3701
	METER_TO_FT = 3.28084
	COLOR_SECONDARY_SCALE = 0.5
	
	# ============================================================================
	# INITIALIZATION
	# ============================================================================
	
	def __init__(self, ownerComp):
		"""
		Initialize LedheadExt extension.
		
		Args:
			ownerComp: The component to which this extension is attached.
		"""
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		
		# Initialize derived properties on component load
		self.UpdateDerivedProperties()

		# Initialize scaling mode on component load
		scaling_mode = str(parent.Ledhead.par.Scalingmode).lower()
		self.ApplyScalingMode(scaling_mode, verbose=False)

	# ============================================================================
	# INTERNAL METHODS - PROPERTY MANAGEMENT
	# ============================================================================
	
	def UpdateDerivedProperties(self):
		"""
		Recalculate and update all derived read-only properties.
		
		Called automatically during initialization and after scaling changes.
		Calculates: resolution, aspect ratio, physical sizes, pixel density, tile count.
		Writes results directly to custom component parameters.
		
		Raises:
			Exception: Caught and logged if parameter access fails.
		"""
		try:
			# Calculate screen resolution from tile configuration
			tiles_w = int(parent.Ledhead.par.Tilesw)
			tiles_h = int(parent.Ledhead.par.Tilesh)
			tile_res_w = int(parent.Ledhead.par.Tileresolutionw)
			tile_res_h = int(parent.Ledhead.par.Tileresolutionh)
			
			screen_res_w = tiles_w * tile_res_w
			screen_res_h = tiles_h * tile_res_h
			parent.Ledhead.parGroup.Screenresolution = (screen_res_w, screen_res_h)
			
			# Calculate aspect ratio
			aspect_ratio = screen_res_w / screen_res_h if screen_res_h > 0 else 0.0
			aspect_str = f'{aspect_ratio:.2f}:1'
			parent.Ledhead.par.Screenaspectratio = aspect_str
			
			# Get and store physical screen size in meters
			screen_size_w = (parent.Ledhead.par.Tilesw * parent.Ledhead.par.Tilesizemmw) / self.METER_TO_MM
			screen_size_h = (parent.Ledhead.par.Tilesh * parent.Ledhead.par.Tilesizemmh) / self.METER_TO_MM
			parent.Ledhead.parGroup.Screensizem = (screen_size_w, screen_size_h)
			
			# Convert physical size to feet
			screen_size_ft = (screen_size_w * self.METER_TO_FT, 
							  screen_size_h * self.METER_TO_FT)
			parent.Ledhead.parGroup.Screensizeft = screen_size_ft
			
			# Calculate native pixel density in PPI
			screen_width_inches = screen_size_w * self.METER_TO_IN
			screen_height_inches = screen_size_h * self.METER_TO_IN
			
			if screen_width_inches > 0 and screen_height_inches > 0:
				ppi_width = screen_res_w / screen_width_inches
				ppi_height = screen_res_h / screen_height_inches
				native_ppi = round((ppi_width + ppi_height) / 2.0, 2)
			else:
				native_ppi = 0.0
			
			parent.Ledhead.par.Nativepixeldensity = native_ppi
			
			# Calculate total tile count
			tile_count = tiles_w * tiles_h
			parent.Ledhead.par.Tilecount = tile_count
			
		except Exception as e:
			print(f'Error updating derived properties: {e}')

	# ============================================================================
	# PUBLIC METHODS - SCALING MODES
	# ============================================================================
	
	def ApplyScalingMode(self, mode, verbose=True, round_to_even=False, preserve_aspect=False):
		"""
		Calculate and apply design resolution based on selected scaling mode.
		
		Supports four scaling modes:
		- 'density': Calculate from pixel density and physical screen size
		- 'manual': Use manually specified design resolution values
		- 'factor': Scale native resolution by a multiplication factor
		- 'bypass': Use native resolution without scaling
		
		For density mode, the calculation is:
		design_res = physical_dimension_in_unit * pixels_per_unit
		
		Physical dimensions are converted from meters to the selected unit (mm, cm, m, in, ft).
		
		Args:
			mode (str): Scaling mode name (case-insensitive)
			verbose (bool): If True, print scaling results to console. Default is True.
			round_to_even (bool): If True, round dimensions to even numbers. Default is False.
			preserve_aspect (bool): If True, adjust height to preserve native aspect ratio. Default is False.
			
		Returns:
			tuple: (design_width_pixels, design_height_pixels)
		"""
		native_res_w = int(parent.Ledhead.par.Screenresolutionw)
		native_res_h = int(parent.Ledhead.par.Screenresolutionh)
		
		if mode == 'density':
			design_res_w, design_res_h = self._calculate_density_scaling(
				native_res_w, native_res_h)
			
		elif mode == 'manual':
			design_res_w, design_res_h = self._calculate_manual_scaling()
			
		elif mode == 'factor':
			design_res_w, design_res_h = self._calculate_factor_scaling(
				native_res_w, native_res_h)
			
		elif mode == 'bypass':
			design_res_w = native_res_w
			design_res_h = native_res_h
			
		else:
			# Default to bypass for unknown modes
			design_res_w = native_res_w
			design_res_h = native_res_h
		
		# Apply post-processing adjustments
		if round_to_even:
			design_res_w = self._round_to_even(design_res_w)
			design_res_h = self._round_to_even(design_res_h)
		
		if preserve_aspect:
			design_res_w, design_res_h = self._preserve_aspect_ratio(
				design_res_w, design_res_h, native_res_w, native_res_h)
		
		# Apply calculated design resolution and update properties
		parent.Ledhead.parGroup.Screendesignresolution = (design_res_w, design_res_h)
		self.UpdateDerivedProperties()
		
		if verbose:
			print(f'Scaling Mode: {mode} | Native: {native_res_w}x{native_res_h} | Design: {design_res_w}x{design_res_h}')
		
		return (design_res_w, design_res_h)

	# ============================================================================
	# PRIVATE METHODS - SCALING CALCULATIONS
	# ============================================================================
	
	def _round_to_even(self, value):
		"""
		Round a value to the nearest even number.
		
		Args:
			value (float): Value to round
			
		Returns:
			int: Nearest even integer
		"""
		rounded = int(round(value))
		return rounded if rounded % 2 == 0 else rounded + 1
	
	def _preserve_aspect_ratio(self, design_w, design_h, native_w, native_h):
		"""
		Adjust design resolution to preserve native aspect ratio.
		
		If aspect ratios don't match exactly, adjusts height to preserve width
		and match the native aspect ratio.
		
		Args:
			design_w (int): Calculated design width
			design_h (int): Calculated design height
			native_w (int): Native screen width
			native_h (int): Native screen height
			
		Returns:
			tuple: (adjusted_width, adjusted_height) with preserved aspect ratio
		"""
		native_aspect = native_w / native_h if native_h > 0 else 1.0
		design_aspect = design_w / design_h if design_h > 0 else 1.0
		
		if abs(native_aspect - design_aspect) > 0.001:  # Allow small floating point tolerance
			# Adjust height to match native aspect ratio
			adjusted_h = max(int(round(design_w / native_aspect)), 1)
			return design_w, adjusted_h
		
		return design_w, design_h
	
	def _calculate_density_scaling(self, native_res_w, native_res_h):
		"""
		Calculate design resolution using pixel density mode.
		
		Args:
			native_res_w (int): Native screen width in pixels
			native_res_h (int): Native screen height in pixels
			
		Returns:
			tuple: (design_width, design_height) in pixels
		"""
		target_density = float(parent.Ledhead.par.Targetdensity)
		density_unit = str(parent.Ledhead.par.Densityunit).lower()
		
		# Get physical screen dimensions in meters
		screen_width_m = parent.Ledhead.parGroup.Screensizem[0]
		screen_height_m = parent.Ledhead.parGroup.Screensizem[1]
		
		# Convert from meters to selected unit
		meter_to_unit = {
			'mm': self.METER_TO_MM,
			'cm': self.METER_TO_CM,
			'm': 1.0,
			'in': self.METER_TO_IN,
			'ft': self.METER_TO_FT,
		}
		
		if density_unit in meter_to_unit:
			conversion_factor = meter_to_unit[density_unit]
			screen_width_unit = screen_width_m * conversion_factor
			screen_height_unit = screen_height_m * conversion_factor
		else:
			# Default to meters if unknown unit
			screen_width_unit = screen_width_m
			screen_height_unit = screen_height_m
		
		# design_res = physical_dimension * pixels_per_unit
		design_res_w = max(int(screen_width_unit * target_density), 1)
		design_res_h = max(int(screen_height_unit * target_density), 1)
		
		return design_res_w, design_res_h
	
	def _calculate_manual_scaling(self):
		"""
		Calculate design resolution using manually specified values.
		
		Returns:
			tuple: (design_width, design_height) in pixels
		"""
		manual_res = parent.Ledhead.parGroup.Manualresolution
		design_res_w = int(manual_res[0])
		design_res_h = int(manual_res[1])
		
		return design_res_w, design_res_h
	
	def _calculate_factor_scaling(self, native_res_w, native_res_h):
		"""
		Calculate design resolution using multiplication factor mode.
		
		Args:
			native_res_w (int): Native screen width in pixels
			native_res_h (int): Native screen height in pixels
			
		Returns:
			tuple: (design_width, design_height) in pixels
		"""
		scale_factor = float(parent.Ledhead.par.Scalefactor)
		design_res_w = max(int(native_res_w * scale_factor), 1)
		design_res_h = max(int(native_res_h * scale_factor), 1)
		
		return design_res_w, design_res_h

	# ============================================================================
	# PUBLIC METHODS - PATTERN EXPORT
	# ============================================================================
	
	def SavePatterns(self):
		"""
		Export generated patterns to PNG files.
		
		Saves enabled output types (native, design, matte) to the configured save path.
		File naming format: {letter}_{name}_{type}_v{version}.png
		
		Requires:
		- Save path to be configured and writable
		- Output toggles to enable desired export types
		
		Raises:
			AttributeError: If required parameters are missing
			IOError: If file I/O operations fail
		"""
		try:
			# Get output toggles
			outputNative = op(self.OP_NULL_PARS)['Outputnative']
			outputDesign = op(self.OP_NULL_PARS)['Outputdesign']
			outputMatte = op(self.OP_NULL_PARS)['Outputmatte']
			
			# Get naming parameters
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
			
			# Save enabled outputs
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

	# ============================================================================
	# PUBLIC METHODS - COLOR CONTROL
	# ============================================================================
	
	def SetColor(self, r, g, b):
		"""
		Set primary and secondary color scheme for the screen.
		
		Sets two colors:
		- Primary (Colora): (r, g, b)
		- Secondary (Colorb): (r * 0.5, g * 0.5, b * 0.5)
		
		Args:
			r (float): Red channel value
			g (float): Green channel value
			b (float): Blue channel value
		"""
		parent.Ledhead.parGroup.Colora = (r, g, b)
		parent.Ledhead.parGroup.Colorb = (r * self.COLOR_SECONDARY_SCALE, 
										  g * self.COLOR_SECONDARY_SCALE, 
										  b * self.COLOR_SECONDARY_SCALE)

	# ============================================================================
	# PUBLIC METHODS - PATTERN GENERATION
	# ============================================================================
	
	def Reinit(self):
		"""
		Regenerate the screen pattern.
		
		Triggers the replicators to recreate all pattern tiles.
		Useful after changing tile configuration or appearance parameters.
		
		Raises:
			Exception: Caught and logged if replicator access fails.
		"""
		try:
			op(self.OP_CONTAINER_REPLICATOR).par.recreateall.pulse()
			op(self.OP_REPLICATOR).par.recreateall.pulse()
		except Exception as e:
			print(f'Error reinitializing pattern: {e}')

	def EditTile(self):
		"""
		Open a floating network editor for tile appearance editing.
		
		Creates a floating pane displaying the tile container for visual editing.
		"""
		p = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name="Output")
		p.owner = op('container1/button1')