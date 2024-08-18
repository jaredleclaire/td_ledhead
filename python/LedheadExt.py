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
		outputNative = op('null_pars')['Outputnative']
		outputDesign = op('null_pars')['Outputdesign']
		outputMatte = op('null_pars')['Outputmatte']
		
		version = str(parent.Ledhead.par.Version).zfill(2)

		screenName = (str(parent.Ledhead.par.Screenname).lower()).replace(' ','')
		screenLetter = (str(parent.Ledhead.par.Screenletter).lower()).replace(' ','')

		savePath = parent.Ledhead.par.Savepath

		print(f'{savePath}/{screenLetter}_{screenName}_native_v{version}.png')
		
		if outputNative == True:
			op('out_native').save(f'{savePath}/{screenLetter}_{screenName}_native_v{version}.png')
		else:
			pass
			print('native save bypassed')

		if outputDesign == True:
			op('out_design').save(f'{savePath}/{screenLetter}_{screenName}_design_v{version}.png')
		else:
			pass
			print('design save bypassed')

		if outputMatte == True:
			op('out_matte').save(f'{savePath}/{screenLetter}_{screenName}_matte_v{version}.png')
		else:
			pass
			print('matte save bypassed')

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

	# sets mode for setting design scale resolution
	def SetScalingMode(self, mode):

		if mode == 'density':
			# set parameter enable state
			parent.Ledhead.par.Densityunit.enable = True
			parent.Ledhead.par.Targetdensity.enable = True
			parent.Ledhead.parGroup.Manualresolution.enable = False
			parent.Ledhead.par.Scalefactor.enable = False
		
		elif mode == 'manual':
			# set parameter enable state
			parent.Ledhead.par.Densityunit.enable = False
			parent.Ledhead.par.Targetdensity.enable = False
			parent.Ledhead.parGroup.Manualresolution.enable = True
			parent.Ledhead.par.Scalefactor.enable = False

			'''
			# initialize resolution to same as native resolution
			screen_res_w = int(parent.Ledhead.par.Screenresolutionw)
			screen_res_h = int(parent.Ledhead.par.Screenresolutionh)

			parent.Ledhead.parGroup.Manualdesignresolution = (screen_res_w, screen_res_h)
			'''
		
		elif mode == 'factor':
			# set parameter enable state
			parent.Ledhead.par.Densityunit.enable = False
			parent.Ledhead.par.Targetdensity.enable = False
			parent.Ledhead.parGroup.Manualresolution.enable = False
			parent.Ledhead.par.Scalefactor.enable = True
		
		elif mode == 'bypass':
			# set parameter enable state
			parent.Ledhead.par.Densityunit.enable = False
			parent.Ledhead.par.Targetdensity.enable = False
			parent.Ledhead.parGroup.Manualresolution.enable = False
			parent.Ledhead.par.Scalefactor.enable = False
		
		else:
			pass

	# re-generates screen pattern
	def Reinit(self):

		op('container1/replicator1').par.recreateall.pulse()
		op('replicator1').par.recreateall.pulse()