# Neuroloopy - Real-time fMRI Neurofeedback Package

A modular Python package for real-time fMRI neurofeedback processing, refactored from the original `instabrain_dicoms_remtrain_v3.py` script.

## Features

- **Real-time file watching** for DICOM files
- **Modular architecture** with separate modules for different functions
- **Command-line interface** for easy usage
- **Dashboard integration** for real-time monitoring
- **Configurable parameters** via YAML files
- **Logging support** for debugging and analysis
- **Multi-processing** for efficient volume processing

## Installation

### Prerequisites

- Python 3.8 or higher
- FSL (for motion correction)
- ANTs (for MNI transformation)
- dcm2niix (for DICOM to NIfTI conversion)

### Install the package

```bash
# Clone the repository
git clone https://github.com/yourusername/neuroloopy.git
cd neuroloopy

# Install in development mode
pip install -e .
```

## Usage

### Basic Usage

```bash
# Using configuration file
neuroloopy --config config.yaml

# Using command line arguments
neuroloopy --subject-id sub-01 --session 1 --run 1

# With debug mode
neuroloopy --config config.yaml --debug

# With logging and dashboard
neuroloopy --config config.yaml --logging --dashboard
```

### Configuration File

Create a configuration file (e.g., `config.yaml`) based on the example:

```yaml
# Subject and session information
subject-id: sub-01
session-number: 1
start-run: 1

# Timing parameters
baseline-trs: 10
feedback-trs: 100
moving-avg-trs: 5

# Processing parameters
mc-mode: fsl
watch-dir: ./data
post-url: http://localhost:8080

# Dashboard settings
dashboard_bool: true
dashboard-base-url: http://localhost:8080
```

## Package Structure

```
src/neuroloopy/
├── __init__.py          # Package entry point
├── watcher.py           # Real-time file watching
├── preproc.py           # Preprocessing functions
├── anal.py              # Analysis functions
├── utils.py             # Utility functions
├── cli.py               # Command line interface
├── dashboard.py         # Dashboard integration
└── dashboard/           # Dashboard web interface
    ├── server.js
    ├── dashboard.html
    └── package.json
```

## Modules

### watcher.py
- `InstaWatcher`: Main file watcher class
- `start_watcher()`: Function to start the watcher

### preproc.py
- `convert_dicom_to_nii()`: Convert DICOM to NIfTI
- `process_volume()`: Process individual volumes
- `map_voxels_to_roi()`: Extract ROI data

### anal.py
- `apply_classifier()`: Apply trained classifier
- `calculate_feedback()`: Calculate feedback from data
- `calculate_voxel_sigmas()`: Calculate voxel statistics

### utils.py
- `load_config()`: Load YAML configuration
- `validate_config()`: Validate configuration
- `setup_logging()`: Setup logging
- `create_directories()`: Create necessary directories

### cli.py
- `main()`: Main CLI entry point
- `create_parser()`: Create argument parser

### dashboard.py
- Dashboard integration functions
- Health check functions

## API Usage

```python
from neuroloopy import start_watcher, load_config

# Load configuration
config = load_config('config.yaml')

# Start watcher
observer = start_watcher(
    config=config,
    subject_id='sub-01',
    session=1,
    config_name='my_config',
    debug_bool=False,
    logging_bool=True,
    dashboard_bool=True,
    start_run=1
)

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    observer.join()
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

### Code Formatting

```bash
# Format code
black src/neuroloopy/

# Lint code
flake8 src/neuroloopy/
```

## Configuration Parameters

### Required Parameters
- `subject-id`: Subject identifier
- `session-number`: Session number
- `start-run`: Starting run number
- `baseline-trs`: Number of baseline TRs
- `watch-dir`: Directory to watch for DICOM files
- `post-url`: URL for posting feedback data

### Optional Parameters
- `feedback-mode`: 'continuous' or 'intermittent'
- `mc-mode`: Motion correction mode ('fsl', 'afni', 'none')
- `dashboard_bool`: Enable dashboard integration
- `logging_bool`: Enable event logging
- `debug_bool`: Enable debug mode

## Dashboard Integration

The package includes a web-based dashboard for real-time monitoring:

1. Start the dashboard server:
   ```bash
   cd src/neuroloopy/dashboard
   npm install
   npm start
   ```

2. Access the dashboard at `http://localhost:8080`

3. Enable dashboard integration in your configuration:
   ```yaml
   dashboard_bool: true
   dashboard-base-url: http://localhost:8080
   ```

## Troubleshooting

### Common Issues

1. **DICOM files not detected**: Check the `watch-dir` path and file permissions
2. **Motion correction fails**: Ensure FSL is installed and in PATH
3. **Dashboard not connecting**: Check if dashboard server is running
4. **Classifier errors**: Verify classifier file exists and is compatible

### Debug Mode

Enable debug mode for detailed logging:

```bash
neuroloopy --config config.yaml --debug
```

### Logging

Enable event logging for debugging:

```bash
neuroloopy --config config.yaml --logging
```

Log files are saved in the `log/` directory.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Citation

If you use this package in your research, please cite:

```
Neuroloopy: Real-time fMRI neurofeedback package
Version 0.1.0
https://github.com/yourusername/neuroloopy
``` 