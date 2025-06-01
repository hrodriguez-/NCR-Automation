"""Area Boundary to Surface Converter for Speckle Automate.

This module contains the business logic for converting Revit AreaBoundary curves 
to surfaces while preserving metadata.
"""

from pydantic import Field
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)
from specklepy.objects import Base
from specklepy.objects.geometry import Point, Line, Polyline, Curve, Mesh, Surface
from specklepy.objects.other import Collection
from typing import List, Dict, Any, Optional, Tuple
import math

from flatten import flatten_base


class FunctionInputs(AutomateBase):
    """These are function author-defined values.

    Automate will make sure to supply them matching the types specified here.
    Please use the pydantic model schema to define your inputs:
    https://docs.pydantic.dev/latest/usage/models/
    """

    surface_tolerance: float = Field(
        default=0.01,
        title="Surface Creation Tolerance",
        description="Tolerance for determining if curves are coplanar and creating surfaces",
    )

    preserve_original: bool = Field(
        default=True,
        title="Preserve Original Boundaries",
        description="Keep original area boundary curves alongside generated surfaces",
    )

    merge_holes: bool = Field(
        default=True,
        title="Handle Interior Holes",
        description="Process interior boundaries as holes in the main surface",
    )

    min_area_threshold: float = Field(
        default=0.1,
        title="Minimum Area Threshold",
        description="Minimum area size to process (in square units)",
    )


class AreaBoundaryProcessor:
    """Core logic for processing area boundaries"""

    def __init__(self, tolerance: float = 0.01):
        self.tolerance = tolerance

    def extract_curves_from_boundary(self, boundary: Base) -> List[Curve]:
        """Extract curve geometry from area boundary object"""
        curves = []

        # Try different possible locations for boundary curves
        possible_curve_attrs = [
            "curves",
            "outline",
            "boundary",
            "geometry",
            "displayValue",
        ]

        for attr_name in possible_curve_attrs:
            if hasattr(boundary, attr_name):
                attr_value = getattr(boundary, attr_name)
                if isinstance(attr_value, list):
                    curves.extend([c for c in attr_value if self.is_curve(c)])
                elif self.is_curve(attr_value):
                    curves.append(attr_value)

        return curves

    def is_curve(self, obj: Any) -> bool:
        """Check if object is a curve-like geometry"""
        if not isinstance(obj, Base):
            return False

        curve_types = ["Line", "Polyline", "Curve", "Arc", "Circle", "Ellipse"]
        return any(
            curve_type in str(getattr(obj, "speckle_type", ""))
            for curve_type in curve_types
        )

    def group_curves_into_loops(self, curves: List[Curve]) -> List[List[Curve]]:
        """Group curves into closed loops (outer boundary + holes)"""
        if not curves:
            return []

        # For simple case, assume all curves form one loop
        # In production, implement proper curve connectivity analysis
        return [curves]

    def curves_are_coplanar(self, curves: List[Curve]) -> bool:
        """Check if curves lie in the same plane"""
        if len(curves) < 2:
            return True

        # Extract points from curves and check planarity
        points = []
        for curve in curves:
            points.extend(self.get_curve_points(curve))

        if len(points) < 3:
            return True

        # Use first three non-collinear points to define plane
        return self.points_are_coplanar(points)

    def get_curve_points(self, curve: Curve) -> List[Point]:
        """Extract points from a curve object"""
        points = []

        if hasattr(curve, "start") and hasattr(curve, "end"):
            # Line-like objects
            points.extend([curve.start, curve.end])
        elif hasattr(curve, "points"):
            # Polyline-like objects
            points.extend(curve.points)
        elif hasattr(curve, "controlPoints"):
            # NURBS curves
            points.extend(curve.controlPoints)

        return points

    def points_are_coplanar(self, points: List[Point]) -> bool:
        """Check if points lie in the same plane within tolerance"""
        if len(points) < 4:
            return True

        # Use cross product to find normal vector of plane
        # defined by first three points
        p1, p2, p3 = points[0], points[1], points[2]

        v1 = [p2.x - p1.x, p2.y - p1.y, p2.z - p1.z]
        v2 = [p3.x - p1.x, p3.y - p1.y, p3.z - p1.z]

        # Cross product for normal
        normal = [
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0],
        ]

        # Normalize
        normal_length = math.sqrt(sum(n * n for n in normal))
        if normal_length < self.tolerance:
            return True  # Degenerate case

        normal = [n / normal_length for n in normal]

        # Check if all other points are within tolerance of plane
        for point in points[3:]:
            # Vector from p1 to point
            to_point = [point.x - p1.x, point.y - p1.y, point.z - p1.z]
            # Distance to plane (dot product with normal)
            distance = abs(sum(to_point[i] * normal[i] for i in range(3)))
            if distance > self.tolerance:
                return False

        return True

    def create_surface_from_curves(
        self, curves: List[Curve], metadata: Dict[str, Any]
    ) -> Base:
        """Create a surface from boundary curves"""
        # For demonstration, create a simple mesh surface
        # In production, use proper surface creation methods

        # Extract all points from curves
        all_points = []
        for curve in curves:
            all_points.extend(self.get_curve_points(curve))

        if len(all_points) < 3:
            return None

        # Create a simple triangulated mesh from boundary points
        mesh = self.create_mesh_from_points(all_points)

        # Transfer metadata to the mesh
        for key, value in metadata.items():
            setattr(mesh, key, value)

        # Mark as converted surface
        mesh.speckle_type = "Objects.Geometry.Mesh"
        mesh.converted_from = "AreaBoundary"

        return mesh

    def create_mesh_from_points(self, points: List[Point]) -> Mesh:
        """Create a mesh from boundary points using simple triangulation"""
        # Convert points to vertices list
        vertices = []
        for point in points:
            vertices.extend([point.x, point.y, point.z])

        # Simple triangulation (for demonstration)
        # In production, use proper triangulation algorithm
        faces = []
        if len(points) >= 3:
            # Create triangular faces
            for i in range(1, len(points) - 1):
                faces.extend([0, i, i + 1])

        mesh = Mesh(vertices=vertices, faces=faces)
        return mesh

    def extract_metadata(self, boundary: Base) -> Dict[str, Any]:
        """Extract all metadata from area boundary object"""
        metadata = {}

        # Standard properties to preserve
        preserve_attrs = [
            "area",
            "perimeter",
            "name",
            "number",
            "level",
            "roomNumber",
            "roomName",
            "department",
            "occupancy",
            "parameters",
            "properties",
            "units",
        ]

        for attr in preserve_attrs:
            if hasattr(boundary, attr):
                metadata[attr] = getattr(boundary, attr)

        # Also preserve any custom parameters
        if hasattr(boundary, "parameters") and isinstance(boundary.parameters, dict):
            metadata.update(boundary.parameters)

        return metadata


def automate_function(
    automate_context: AutomationContext,
    function_inputs: FunctionInputs,
) -> None:
    """Convert Revit Area boundaries to surfaces while preserving metadata.

    Args:
        automate_context: A context-helper object that carries relevant information
            about the runtime context of this function.
            It gives access to the Speckle project data that triggered this run.
            It also has convenient methods for attaching result data to the Speckle model.
        function_inputs: An instance object matching the defined schema.
    """

    # The context provides a convenient way to receive the triggering version.
    version_root_object = automate_context.receive_version()

    # Initialize processor
    processor = AreaBoundaryProcessor(tolerance=function_inputs.surface_tolerance)

    # Find all area boundaries using the flatten utility
    all_objects = list(flatten_base(version_root_object))
    boundaries = [
        obj
        for obj in all_objects
        if hasattr(obj, "speckle_type")
        and ("AreaBoundary" in str(obj.speckle_type) or "Area" in str(obj.speckle_type))
    ]

    if not boundaries:
        automate_context.mark_run_failed("No area boundaries found in the model")
        return

    converted_surfaces = []
    failed_conversions = []

    for i, boundary in enumerate(boundaries):
        try:
            # Extract curves from boundary
            curves = processor.extract_curves_from_boundary(boundary)

            if not curves:
                failed_conversions.append(f"Boundary {i}: No curves found")
                continue

            # Check if curves are coplanar
            if not processor.curves_are_coplanar(curves):
                failed_conversions.append(f"Boundary {i}: Curves not coplanar")
                continue

            # Extract metadata
            metadata = processor.extract_metadata(boundary)

            # Check area threshold if area is available
            if (
                "area" in metadata
                and metadata["area"] < function_inputs.min_area_threshold
            ):
                continue

            # Group curves into loops
            curve_loops = processor.group_curves_into_loops(curves)

            for loop in curve_loops:
                # Create surface from curve loop
                surface = processor.create_surface_from_curves(loop, metadata)

                if surface:
                    converted_surfaces.append(surface)

        except Exception as e:
            failed_conversions.append(f"Boundary {i}: {str(e)}")

    # Create result collection with converted surfaces
    converted_objects = []

    if function_inputs.preserve_original:
        converted_objects.extend(boundaries)

    converted_objects.extend(converted_surfaces)

    # Create new version in the project with results
    if converted_surfaces:
        model_id = automate_context.create_version_in_project(
            converted_objects,
            f"Area boundaries converted to surfaces - {len(converted_surfaces)} surfaces created",
        )

        # Attach success info to the converted surfaces
        automate_context.attach_info_to_objects(
            category="Surface Conversion",
            object_ids=[
                surface.id for surface in converted_surfaces if hasattr(surface, "id")
            ],
            message=f"Successfully converted {len(converted_surfaces)} area boundaries to surfaces",
        )

        # Mark run as successful
        automate_context.mark_run_success(
            f"Converted {len(converted_surfaces)} area boundaries to surfaces. "
            f"Created new version: {model_id}"
        )
    else:
        automate_context.mark_run_failed(
            "No area boundaries could be converted to surfaces"
        )

    # Report any failures
    if failed_conversions:
        automate_context.attach_error_to_objects(
            category="Conversion Failures",
            object_ids=[],
            message=f"Failed to convert {len(failed_conversions)} boundaries: {'; '.join(failed_conversions[:3])}",
        )

    # Set the automation context view to show results
    automate_context.set_context_view()


# Entry point for Speckle Automate
# NOTE: always pass in the automate function by its reference; do not invoke it!
if __name__ == "__main__":
    # Pass in the function reference with the inputs schema to the executor.
    execute_automate_function(automate_function, FunctionInputs)
