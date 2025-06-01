"""Tests for the area boundary converter function."""

import pytest
from specklepy.objects import Base
from specklepy.objects.geometry import Point, Line, Mesh
from main import FunctionInputs, AreaBoundaryProcessor


class TestAreaBoundaryProcessor:
    """Test cases for the AreaBoundaryProcessor class."""

    def test_processor_initialization(self):
        """Test that processor initializes with correct tolerance."""
        processor = AreaBoundaryProcessor(tolerance=0.05)
        assert processor.tolerance == 0.05

    def test_curve_detection(self):
        """Test curve detection logic."""
        processor = AreaBoundaryProcessor()

        # Create mock curve object
        line = Line()
        line.speckle_type = "Objects.Geometry.Line"

        assert processor.is_curve(line) is True

        # Test non-curve object
        point = Point()
        point.speckle_type = "Objects.Geometry.Point"

        assert processor.is_curve(point) is False

    def test_metadata_extraction(self):
        """Test metadata extraction from boundary objects."""
        processor = AreaBoundaryProcessor()

        # Create mock boundary with metadata
        boundary = Base()
        boundary.area = 100.5
        boundary.name = "Test Area"
        boundary.number = "001"
        boundary.level = "Level 1"

        metadata = processor.extract_metadata(boundary)

        assert metadata["area"] == 100.5
        assert metadata["name"] == "Test Area"
        assert metadata["number"] == "001"
        assert metadata["level"] == "Level 1"

    def test_points_are_coplanar(self):
        """Test planarity checking for points."""
        processor = AreaBoundaryProcessor()

        # Create coplanar points (all in XY plane)
        points = [
            Point(x=0, y=0, z=0),
            Point(x=1, y=0, z=0),
            Point(x=1, y=1, z=0),
            Point(x=0, y=1, z=0),
        ]

        assert processor.points_are_coplanar(points) is True

        # Create non-coplanar points
        non_coplanar_points = [
            Point(x=0, y=0, z=0),
            Point(x=1, y=0, z=0),
            Point(x=1, y=1, z=0),
            Point(x=0, y=1, z=1),  # This point breaks planarity
        ]

        assert processor.points_are_coplanar(non_coplanar_points) is False


class TestFunctionInputs:
    """Test cases for function inputs validation."""

    def test_default_values(self):
        """Test that default input values are correct."""
        inputs = FunctionInputs(
            surface_tolerance=0.01,
            preserve_original=True,
            merge_holes=True,
            min_area_threshold=0.1,
        )

        assert inputs.surface_tolerance == 0.01
        assert inputs.preserve_original is True
        assert inputs.merge_holes is True
        assert inputs.min_area_threshold == 0.1

    def test_custom_values(self):
        """Test custom input values."""
        inputs = FunctionInputs(
            surface_tolerance=0.05,
            preserve_original=False,
            merge_holes=False,
            min_area_threshold=1.0,
        )

        assert inputs.surface_tolerance == 0.05
        assert inputs.preserve_original is False
        assert inputs.merge_holes is False
        assert inputs.min_area_threshold == 1.0


if __name__ == "__main__":
    pytest.main([__file__])
