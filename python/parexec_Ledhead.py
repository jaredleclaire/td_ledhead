# me - this DAT
# par - the Par object that has changed
# val - the current value
# prev - the previous value
# 
# Make sure the corresponding toggle is enabled in the Parameter Execute DAT.

def onValueChange(par, prev):
	# use par.eval() to get current value
	
	match par.name:
		case 'Scalingmode' | 'Screenresolutionw' | 'Screenresolutionh' | 'Densityunit' | 'Targetdensity':
			# Trigger scaling mode calculation when any scaling-related parameter changes
			scaling_mode = str(parent.Ledhead.par.Scalingmode).lower()
			parent.Ledhead.ApplyScalingMode(scaling_mode,verbose=False)
		case 'Tilesw' | 'Tilesh' | 'Tileresolutionw' | 'Tileresolutionh' | 'Tilesizemmw' | 'Tilesizemmh':
			parent.Ledhead.UpdateDerivedProperties()
			# Re-apply scaling mode when tile parameters change (which affects native resolution)
			scaling_mode = str(parent.Ledhead.par.Scalingmode).lower()
			parent.Ledhead.ApplyScalingMode(scaling_mode, verbose=False)
		case _:
			pass
	
	return

# Called at end of frame with complete list of individual parameter changes.
# The changes are a list of named tuples, where each tuple is (Par, previous value)
def onValuesChanged(changes):
	for c in changes:
		# use par.eval() to get current value
		par = c.par
		prev = c.prev
	return

def onPulse(par):

	match par.name:
		case 'Edittile':
			parent.Ledhead.EditTile()
		case 'Reinit':
			parent.Ledhead.Reinit()
		case 'Savepatterns':
			parent.Ledhead.SavePatterns()
		case _:
			pass

	return

def onExpressionChange(par, val, prev):
	return

def onExportChange(par, val, prev):
	return

def onEnableChange(par, val, prev):
	return

def onModeChange(par, val, prev):
	return
	