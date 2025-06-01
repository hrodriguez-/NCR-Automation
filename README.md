# Area Boundary to Surface Converter

A Speckle Automate function that converts Revit AreaBoundary objects into surfaces while preserving all associated metadata.

## Overview

This function addresses the common need to convert area boundary curves exported from Revit into usable surface geometry that can be consumed by other applications in the AEC workflow. The function intelligently processes boundary curves and creates planar surfaces while maintaining all the rich metadata associated with the original area boundaries.

## Getting Started

### Using this Speckle Function

1. [Create](https://automate.speckle.dev/) a new Speckle Automation.
2. Select your Speckle Project and Speckle Model containing Revit area boundaries.
3. Select the "Area Boundary to Surface Converter" Function.
4. Configure the conversion parameters (tolerance, options, etc.).
5. Click `Create Automation`.

### Getting Started with Creating Your Own Version

1. [Register](https://automate.speckle.dev/) your Function with [Speckle Automate](https://automate.speckle.dev/) and select the Python template.
2. A new repository will be created in your GitHub account.
3. Replace the template code with this area boundary converter implementation.
4. Make changes to your Function in `main.py`. See below for the Developer Requirements and instructions on how to test.
5. To create a new version of your Function, create a new [GitHub release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository) in your repository.

## Features

- **Automatic Detection**: Finds all AreaBoundary objects in your Speckle model using the flatten utility
- **Intelligent Processing**: Checks for coplanar curves and validates geometry
- **Metadata Preservation**: Transfers all area properties (name, number, area value, etc.)
- **Flexible Options**: Configure tolerance, minimum area thresholds, and processing behavior
- **Error Handling**: Comprehensive reporting of successful conversions and failures
- **Hole Support**: Handles interior boundaries as holes in surfaces (configurable)

## Input Parameters

### Surface Creation Tolerance
- **Type**: Number
- **Default**: 0.01
- **Description**: Tolerance for determining if curves are coplanar and for surface creation

### Preserve Original Boundaries
- **Type**: Boolean
- **Default**: True
- **Description**: Keep original area boundary curves alongside generated surfaces

### Handle Interior Holes
- **Type**: Boolean
- **Default**: True
- **Description**: Process interior boundaries as holes in the main surface

### Minimum Area Threshold
- **Type**: Number
- **Default**: 0.1
- **Description**: Minimum area size to process (in square units)

## Developer Requirements

1. Install the following:
    - [Python 3.11+](https://www.python.org/downloads/)
    - [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
2. Run `poetry shell && poetry install` to install the required Python packages.

## Building and Testing

The code can be tested locally by running `poetry run pytest`.

### Local Development

```bash
# Clone your repository
git clone <your-repo-url>
cd area-boundary-converter

# Install dependencies
poetry shell && poetry install

# Run tests
poetry run pytest

# Run linting
poetry run black .
poetry run ruff check .
```

### Testing with Real Data

1. Copy `.env.example` to `.env` and fill in your Speckle server details
2. Update `example.function_inputs.json` with your test parameters
3. Run the function locally for testing

### Building and Running the Docker Container Image

Running and testing your code on your machine is a great way to develop your Function; the following instructions are more in-depth and only required if you are having issues with your Function in GitHub Actions or on Speckle Automate.

#### Building the Docker Container Image

To build the Docker Container Image, you must have [Docker](https://docs.docker.com/get-docker/) installed.

Once you have Docker running on your local machine:

1. Open a terminal
2. Navigate to the directory in which you cloned this repository
3. Run the following command:

    ```bash
    docker build -f ./Dockerfile -t area_boundary_converter .
    ```

#### Running the Docker Container Image

Once you've built the image, you can test it locally:

```bash
docker run --rm area_boundary_converter \
python -u main.py run \
'{"projectId": "1234", "modelId": "1234", "branchName": "myBranch", "versionId": "1234", "speckleServerUrl": "https://speckle.xyz", "automationId": "1234", "automationRevisionId": "1234", "automationRunId": "1234", "functionId": "1234", "functionName": "Area Boundary Converter", "functionLogo": "base64EncodedPng"}' \
'{"surface_tolerance": 0.01, "preserve_original": true, "merge_holes": true, "min_area_threshold": 0.1}' \
yourSpeckleServerAuthenticationToken
```
## How It Works

1. **Discovery Phase**: Uses the flatten utility to find all AreaBoundary and Area objects in the model
2. **Curve Extraction**: Extracts boundary curves from various possible locations in the object structure
3. **Validation**: Checks if curves are coplanar and form valid closed loops
4. **Surface Creation**: Generates mesh surfaces from the boundary curves using triangulation
5. **Metadata Transfer**: Copies all relevant properties from the original area boundary
6. **Output Generation**: Creates a new model version with converted surfaces

## Supported Revit Objects

- **AreaBoundary**: Direct area boundary curve objects
- **Area**: Area objects that contain outline/boundary information
- **Custom Objects**: Any object with recognizable curve geometry

## Output

The function creates a new model version containing:
- **Original Boundaries** (if preserve option is enabled)
- **Generated Surfaces**: Mesh surfaces created from area boundaries
- **Conversion Statistics**: Summary of processing results via automation context
- **Error Reports**: Details about any failed conversions

## Technical Implementation

### Curve-to-Surface Algorithm

1. **Boundary Analysis**: Groups curves into closed loops
2. **Planarity Check**: Verifies curves lie in the same plane within tolerance
3. **Triangulation**: Creates mesh surfaces using simple triangulation
4. **Optimization**: Future versions will support NURBS surfaces and complex hole handling

### Metadata Preservation

The function preserves these standard Revit area properties:
- Area value
- Perimeter
- Name and Number
- Level information
- Room associations
- Department and Occupancy
- All custom parameters

### Integration with Speckle Template

This function is built on the official Speckle Automate Python template and includes:
- Proper error handling using automation context
- Standardized function inputs with Pydantic validation
- Comprehensive testing framework
- Docker containerization for deployment
- GitHub Actions workflow for CI/CD

## Deployment

1. **Register Function**: Use Speckle Automate's "New Function" wizard and select Python template
2. **Replace Code**: Replace the template `main.py` with this implementation
3. **Set Secrets**: Add `SPECKLE_AUTOMATE_FUNCTION_ID` and `SPECKLE_AUTOMATE_FUNCTION_PUBLISH_TOKEN` to GitHub repository secrets
4. **Release**: Create a GitHub release to trigger automatic deployment via GitHub Actions

## Error Handling

Common issues and solutions:

### "No area boundaries found"
- Ensure your Revit model contains Area objects
- Check that areas have been properly exported to Speckle
- Verify the model contains the expected object structure

### "Curves not coplanar"
- Increase the surface tolerance parameter
- Check if area boundaries have 3D curves (unusual but possible)
- Manually review the geometry in the source model

### "No curves found"
- Verify area boundaries have associated geometry
- Check if the curve data is nested in unexpected object properties
- Review the object structure in Speckle Web

## File Structure

```
├── main.py                          # Main function implementation
├── flatten.py                       # Utility for flattening Speckle objects
├── pyproject.toml                   # Poetry dependencies and configuration
├── Dockerfile                       # Container configuration
├── example.function_inputs.json     # Example function inputs for testing
├── .env.example                     # Environment variables template
├── tests/
│   └── test_area_converter.py       # Unit tests
├── .github/
│   └── workflows/
│       └── main.yml                 # GitHub Actions CI/CD
└── README.md                        # This file
```

## Testing

The function includes comprehensive unit tests:

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=main

# Run specific test
poetry run pytest tests/test_area_converter.py::TestAreaBoundaryProcessor::test_curve_detection
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests and linting (`poetry run pytest && poetry run black . && poetry run ruff check .`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Future Enhancements

- **NURBS Surface Support**: Create true surface objects instead of meshes
- **Advanced Hole Handling**: Better processing of complex interior boundaries
- **Curve Connectivity**: Improved algorithm for grouping disconnected curves
- **Performance Optimization**: Parallel processing for large models
- **Quality Metrics**: Surface quality assessment and reporting
- **Adaptive Tolerance**: Automatic tolerance adjustment based on model scale

## Resources

- [Learn more about SpecklePy](https://speckle.guide/dev/python.html) and interacting with Speckle from Python
- [Speckle Automate Documentation](https://speckle.guide/automate/)
- [Speckle Community Forum](https://speckle.community/)

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Visit the [Speckle Community Forum](https://speckle.community/)
- Check the [Speckle documentation](https://speckle.guide/)

## Changelog

### v0.1.0
- Initial release based on Speckle Automate Python template
- Basic area boundary to surface conversion
- Metadata preservation
- Configurable processing options
- Comprehensive error handling and testing
- Docker containerization and CI/CD pipeline