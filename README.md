Ledhead v2.0

-----------------

Ledhead is a TouchDesigner tool for generating LED test patterns and managing LED screen configuration and scaling.

Features

Design Resolution Scaling
Ledhead supports multiple scaling modes to convert native screen resolution to optimized design resolution:
- Density Mode: Calculate resolution based on pixel density (pixels per unit) with support for multiple units (mm, cm, m, in, ft)
- Manual Mode: Specify custom design resolution values directly
- Factor Mode: Scale resolution by a multiplication factor
- Bypass Mode: Use native resolution without scaling

The density mode automatically converts physical screen dimensions (stored in meters) to your selected unit and performs normalized calculations.

Pattern Generation
- Generates LED test patterns with configurable grid parameters
- Replicator-friendly component for efficient processing
- Provides screen size and resolution information

Output Export
- Save generated patterns to multiple output formats simultaneously
- Supported output types: native resolution, design resolution, and matte patterns
- Configurable save path and versioning

Color Control
- Set custom color schemes with automatic secondary color calculation

Additional Functionality
- Floating tile editor for appearance customization
- Pattern regeneration/reinitialization
- Parameter-driven backend logic with real-time updates

Performance Note

This component is processor-intensive. It is not recommended for real-time projects where frame rate is critical.

-----------------
