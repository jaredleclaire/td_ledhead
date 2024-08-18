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

	# checks which maps are toggled for output and saves them to the specified directory
	def SavePatterns(self):
		outputNative = op('null_pars')['Outputnative']
		outputDesign = op('null_pars')['Outputdesign']
		outputMatte = op('null_pars')['Outputmatte']
		
		version = str(parent.Ledhead.par.Version).zfill(2)

		screenName = (str(parent.Ledhead.par.Screenname).lower()).replace(' ','')
		screenLetter = (str(parent.Ledhead.par.Screenletter).lower()).replace(' ','')

		savePath = parent.Ledhead.par.Savepath

		print(version)
		print(screenName)
		
		if outputNative == True:
			op('out_native').save(savePath + '/' + screenLetter + '_' + screenName + '_native_v' + version + '.png')
		else:
			pass
			print('native save bypassed')

		if outputDesign == True:
			op('out_design').save(savePath + '/' + screenLetter + '_' + screenName + '_design_v' + version + '.png')
		else:
			pass
			print('design save bypassed')

		if outputMatte == True:
			op('out_matte').save(savePath + '/' + screenLetter + '_' + screenName + '_matte_v' + version + '.png')
		else:
			pass
			print('matte save bypassed')

		return
	
	# sets bi-color scheme for the screen
	def SetColor(self, r, g, b):

		parent.Ledhead.parGroup.Colora = (r,g,b)
		parent.Ledhead.parGroup.Colorb = (r * 0.5, g * 0.5, b * 0.5)

		return
	
