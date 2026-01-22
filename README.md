Ledhead v2.0

-----------------

Ledhead is a TouchDesigner extension for configuring LED screen layouts, calculating screen properties, and managing resolution scaling with multiple modes.

Features

Scaling Modes
Ledhead supports multiple scaling modes to convert native screen resolution to optimized design resolution:
- **Density Mode**: Calculate resolution based on pixel density (pixels per unit) with support for multiple units (mm, cm, m, in, ft)
- **Manual Mode**: Specify custom design resolution values directly
- **Factor Mode**: Scale resolution by a multiplication factor
- **Bypass Mode**: Use native resolution without scaling

Optional post-processing adjustments:
- **Even Number Rounding**: Force resolution dimensions to even numbers for optimal codec compatibility
- **Aspect Ratio Preservation**: Automatically adjust height to maintain native screen aspect ratio

Automatic Property Calculation
Ledhead automatically calculates and updates derived screen properties:
- Screen resolution in pixels (native and scaled design)
- Physical screen dimensions in multiple units (meters and feet)
- Screen aspect ratio as formatted string
- Native pixel density in PPI (pixels per inch)
- Total tile count

All calculated values are stored as custom component parameters for easy access throughout your project.

Pattern Generation
- Generates LED test patterns with configurable tile parameters
- Replicator-friendly component for efficient tile rendering
- Tile appearance editing via floating network editor
- Pattern regeneration with single method call

Output Export
- Save generated patterns to PNG files
- Supported output types: native resolution, design resolution, and matte patterns
- Configurable save path with automatic versioning and naming

Color Control
- Set custom color schemes with automatic secondary color calculation (50% intensity)

API Reference

Main Methods:
- `ApplyScalingMode(mode, verbose=True, round_to_even=False, preserve_aspect=False)` - Apply scaling with optional post-processing
- `UpdateDerivedProperties()` - Manually recalculate all screen properties
- `SavePatterns()` - Export generated patterns to configured location
- `SetColor(r, g, b)` - Set primary and secondary colors
- `Reinit()` - Regenerate pattern tiles
- `EditTile()` - Open floating editor for tile customization

Suppress Console Output
By default, `ApplyScalingMode()` prints scaling results to the console. To suppress this:
```python
parent.Ledhead.ext.ApplyScalingMode('density', verbose=False)
```

Performance Note

This component is processor-intensive. It is not recommended for real-time projects where frame rate is critical.

-----------------
