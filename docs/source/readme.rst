Moldflow API
============

.. raw:: html

    <a href="https://badge.fury.io/py/moldflow"><img src="https://badge.fury.io/py/moldflow.svg" alt="PyPI version"/></a>
    <a href="https://pypi.org/project/moldflow/"><img src="https://img.shields.io/pypi/pyversions/moldflow.svg" alt="Python versions"/></a>
    <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"/></a>
    <a href="https://github.com/Autodesk/moldflow-api/actions"><img src="https://github.com/Autodesk/moldflow-api/workflows/CI/badge.svg" alt="CI Status"/></a>

Overview
========

Moldflow API is a Python wrapper library for the Synergy API, designed to simplify interactions with Autodesk Moldflow Synergy. This library provides a clean, pythonic interface to Moldflow's simulation capabilities, making it easier to integrate Moldflow functionality into your Python applications.

Requirements
============

- Windows 10/11
- Python 3.10.x - 3.13.x
- Autodesk Moldflow Synergy 2026.0.1 or later

Installation
============

From PyPI
----------

The easiest way to install Moldflow API is using pip:

.. code-block:: bash

   pip install moldflow

From Source
-----------

If you want to install from source or contribute to the project:

.. code-block:: bash

   git clone https://github.com/Autodesk/moldflow-api.git
   cd moldflow-api
   python -m pip install -r requirements.txt

Quick Start
===========

Here's a simple example to get you started:

.. code-block:: python

    from moldflow import Synergy

    # Initialize the API
    synergy = Synergy()

    # Example: Get version information
    version = synergy.version
    build = synergy.build
    print(f"Moldflow Synergy version: {version}")
    print(f"Build: {build}")

Usage Examples
=============================

Simulation Workflow
-----------------------------

This example shows a complete simulation setup from CAD import to analysis:

.. code-block:: python

    import os
    from moldflow import Synergy
    from moldflow.common import MeshType, MoldingProcess

    # Initialize Synergy
    synergy = Synergy()

    # Create new project and study
    synergy.new_project("test", "C:\\temp\\new_project")
    project = synergy.project
    project.new_study("injection_molding_analysis")

    # Get study document and set basic parameters
    study_doc = synergy.study_doc
    study_doc.molding_process = MoldingProcess.THERMOPLASTIC_INJECTION_MOLDING
    study_doc.mesh_type = MeshType.MESH_FUSION

    # Import CAD file (example)
    cad_file = "C:\\path\\to\\your\\part.stp"
    if os.path.exists(cad_file):
        import_opts = synergy.import_options
        study_doc.add_file(cad_file, import_opts, show_logs=True)

    # Set up mesh generation
    mesh_generator = synergy.mesh_generator
    mesh_editor = synergy.mesh_editor

    # Generate and validate mesh
    mesh_generator.generate()
    mesh_editor.auto_fix()
    mesh_editor.purge_nodes()

    # Get mesh diagnostics
    diagnosis_mgr = synergy.diagnosis_manager
    mesh_summary = diagnosis_mgr.get_mesh_summary(element_only=True)

    print(f"Mesh Quality Report:")
    print(f"  Elements: {mesh_summary.triangles_count}")
    print(f"  Nodes: {mesh_summary.nodes_count}")

    # Save the configured study
    project.save_all()
    print("Simulation setup complete!")

Material Management
----------------------------

Find and analyze materials with specific properties:

.. code-block:: python

    from moldflow import Synergy
    from moldflow.common import MaterialDatabase, MaterialDatabaseType

    synergy = Synergy()
    material_finder = synergy.material_finder

    # Search through different material databases
    databases = [
        (MaterialDatabase.THERMOPLASTIC, "Thermoplastics"),
        (MaterialDatabase.THERMOSET_MATERIAL, "Thermoset Materials"),
        (MaterialDatabase.UNDERFILL_ENCAPSULANT, "Underfill Encapsulants")
    ]

    material_catalog = {}

    for db_type, db_name in databases:
        print(f"\n=== {db_name} Materials ===")
        material_finder.set_data_domain(db_type, MaterialDatabaseType.SYSTEM)

        materials = []
        material = material_finder.get_first_material()
        count = 0

        while material and count < 10:  # Limit for example
            materials.append({
                'id': material.id,
                'name': material.name,
                'type': material.type
            })
            print(f"  {material.name} (ID: {material.id})")
            material = material_finder.get_next_material(material)
            count += 1

        material_catalog[db_name] = materials

    print(f"\nTotal material categories found: {len(material_catalog)}")

Mesh Analysis
---------------------------

Perform detailed mesh quality analysis and diagnostics:

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    diagnosis_mgr = synergy.diagnosis_manager
    mesh_editor = synergy.mesh_editor

    # Get comprehensive mesh summary
    mesh_summary = diagnosis_mgr.get_mesh_summary(
        element_only=False,
        inc_beams=True,
        inc_match=True,
        recalculate=True
    )

    # Detailed mesh quality report
    print("=== Comprehensive Mesh Analysis ===")
    print(f"Geometry:")
    print(f"  Triangles: {mesh_summary.triangles_count:,}")
    print(f"  Tetrahedra: {mesh_summary.tetras_count:,}")
    print(f"  Beams: {mesh_summary.beams_count:,}")
    print(f"  Nodes: {mesh_summary.nodes_count:,}")

    print(f"\nQuality Metrics:")
    print(f"  Aspect Ratio - Min: {mesh_summary.min_aspect_ratio:.3f}")
    print(f"  Aspect Ratio - Max: {mesh_summary.max_aspect_ratio:.3f}")
    print(f"  Aspect Ratio - Avg: {mesh_summary.ave_aspect_ratio:.3f}")
    print(f"  Max Dihedral Angle: {mesh_summary.max_dihedral_angle:.1f}°")
    print(f"  Max Volume Ratio: {mesh_summary.max_volume_ratio:.3f}")

    print(f"\nMesh Integrity:")
    print(f"  Free Edges: {mesh_summary.free_edges_count}")
    print(f"  Manifold Edges: {mesh_summary.manifold_edges_count}")
    print(f"  Non-Manifold Edges: {mesh_summary.non_manifold_edges_count}")
    print(f"  Connectivity Regions: {mesh_summary.connectivity_regions}")

    print(f"\nMesh Issues:")
    print(f"  Intersection Elements: {mesh_summary.intersection_elements}")
    print(f"  Overlap Elements: {mesh_summary.overlap_elements}")
    print(f"  Zero Triangles: {mesh_summary.zero_triangles}")
    print(f"  Zero Beams: {mesh_summary.zero_beams}")
    print(f"  Unoriented Elements: {mesh_summary.unoriented}")

    # Perform mesh diagnostics and repairs
    if mesh_summary.intersection_elements > 0:
        print(f"\n⚠️  Found {mesh_summary.intersection_elements} intersection elements")
        print("Running auto-fix...")
        fixed_elements = mesh_editor.auto_fix()
        print(f"Fixed {fixed_elements} elements")

    # Additional mesh operations
    entity_list = mesh_editor.create_entity_list()
    print(f"Created entity list for further operations")

    # Assess overall mesh quality
    if mesh_summary.ave_aspect_ratio > 10:
        print("⚠️  Average aspect ratio is high - consider mesh refinement")

    if mesh_summary.free_edges_count > mesh_summary.triangles_count * 0.1:
        print("⚠️  High number of free edges detected - check mesh integrity")

    print(f"\n✓ Mesh analysis complete")

Project and Study Management
----------------------------

Project management with multiple studies and configurations:

.. code-block:: python

    from moldflow import Synergy
    from moldflow.common import MoldingProcess, MeshType

    synergy = Synergy()
    project = synergy.project

    # Create multiple studies for different scenarios
    study_configs = [
        ("thermoplastic_study", MoldingProcess.THERMOPLASTIC_INJECTION_MOLDING, "Standard thermoplastic injection"),
        ("gas_assisted_study", MoldingProcess.GAS_ASSISTED_INJECTION_MOLDING, "Gas-assisted injection molding"),
        ("overmolding_study", MoldingProcess.THERMOPLASTICS_OVERMOLDING, "Thermoplastic overmolding"),
        ("compression_study", MoldingProcess.THERMOPLASTICS_INJECTION_COMPRESSION_MOLDING, "Injection-compression molding")
    ]

    created_studies = []

    for study_name, process, description in study_configs:
        print(f"Creating study: {study_name}")

        # Create new study
        success = project.new_study(study_name)
        if success:
            study_doc = synergy.study_doc
            study_doc.molding_process = process

            # Set mesh type based on study type
            if "compression" in study_name:
                study_doc.mesh_type = MeshType.MESH_3D
            else:
                study_doc.mesh_type = MeshType.MESH_MIDPLANE

            created_studies.append({
                'name': study_name,
                'process': process,
                'mesh_type': study_doc.mesh_type,
                'description': description
            })

            print(f"  ✓ {study_name} configured with {process.value}")
        else:
            print(f"  ✗ Failed to create {study_name}")

    # Save all studies
    project.save_all()

    print(f"\nProject Summary:")
    print(f"Successfully created {len(created_studies)} studies:")
    for study in created_studies:
        print(f"  - {study['name']}: {study['description']}")

Batch Processing Example
------------------------

Process multiple files or configurations automatically:

.. code-block:: python

    import os
    import glob
    from moldflow import Synergy

    def process_cad_files(file_pattern):
        """Process multiple CAD files through Moldflow analysis setup."""

        synergy = Synergy()
        cad_files = glob.glob(file_pattern)

        if not cad_files:
            print(f"No files found matching pattern: {file_pattern}")
            return

        print(f"Found {len(cad_files)} CAD files to process")

        results = []

        for i, cad_file in enumerate(cad_files, 1):
            filename = os.path.basename(cad_file)
            study_name = f"auto_{os.path.splitext(filename)[0]}"

            print(f"\n[{i}/{len(cad_files)}] Processing: {filename}")

            try:
                # Create new study
                project = synergy.project
                project.new_study(study_name)

                # Import CAD file
                import_opts = synergy.import_options
                study_doc = synergy.study_doc

                success = study_doc.add_file(cad_file, import_opts, show_logs=False)

                if success:
                    # Quick mesh setup
                    mesh_generator = synergy.mesh_generator
                    mesh_generator.generate()

                    mesh_editor = synergy.mesh_editor
                    mesh_editor.auto_fix()

                    # Get basic mesh info
                    diagnosis_mgr = synergy.diagnosis_manager
                    mesh_summary = diagnosis_mgr.get_mesh_summary(element_only=True)

                    result = {
                        'file': filename,
                        'study': study_name,
                        'elements': mesh_summary.triangles_count,
                        'nodes': mesh_summary.nodes_count,
                        'quality': mesh_summary.ave_aspect_ratio,
                        'status': 'Success'
                    }

                    print(f"  ✓ Mesh: {mesh_summary.triangles_count:,} elements")
                    print(f"  ✓ Quality: {mesh_summary.ave_aspect_ratio:.2f} avg aspect ratio")

                else:
                    result = {
                        'file': filename,
                        'study': study_name,
                        'status': 'Failed - Import Error'
                    }
                    print(f"  ✗ Failed to import CAD file")

                results.append(result)

            except Exception as e:
                print(f"  ✗ Error processing {filename}: {str(e)}")
                results.append({
                    'file': filename,
                    'status': f'Error: {str(e)}'
                })

        # Save all work
        synergy.project.save_all()

        # Summary report
        print(f"\n=== Batch Processing Summary ===")
        successful = len([r for r in results if r.get('status') == 'Success'])
        print(f"Successfully processed: {successful}/{len(results)} files")

        for result in results:
            if result.get('status') == 'Success':
                print(f"  ✓ {result['file']}: {result['elements']:,} elements")
            else:
                print(f"  ✗ {result['file']}: {result['status']}")

        return results

    # Example usage:
    results = process_cad_files("C:\\CAD_Files\\*.stp", "C:\\Moldflow_Results\\")

Advanced Utilities
==================

Unit Conversion
---------------

.. code-block:: python

    from moldflow import Synergy
    from moldflow.common import SystemUnits

    synergy = Synergy()
    uc = synergy.unit_conversion  # UnitConversion

    si = uc.convert_to_si("mm", 25.4)
    inch = uc.convert_to_unit("in", SystemUnits.ENGLISH, si)
    desc = uc.get_unit_description("mm", SystemUnits.METRIC)

    print(f"25.4 mm in SI: {si}")
    print(f"SI back to inches: {inch}")
    print(f"Unit description (Metric): {desc}")

Create Plot by Dataset and Export Results
-----------------------------------------

.. code-block:: python

    from moldflow import Synergy
    from moldflow.common import PlotType, SystemUnits

    synergy = Synergy()
    pm = synergy.plot_manager  # PlotManager

    # Derive a dataset id from the first available plot (avoids hard-coding)
    plot = pm.get_first_plot()
    if plot:
        ds_id = plot.data_id
        plot = pm.create_plot_by_ds_id(ds_id, PlotType.PLOT_DEFAULT_PLOT_FOR_DATA_ID)
    if plot:
        print(f"Plot created: {plot.name}")

        # Inspect data display format
        fmt = pm.get_data_display_format(plot.data_id)
        print(f"Display format: {fmt}")

        # Save result data as XML
        ok = pm.save_result_data_in_xml(plot.data_id, "results.xml", SystemUnits.STANDARD)
        print(f"Saved XML: {ok}")

Viewer Controls and Screenshot
------------------------------

.. code-block:: python

    from moldflow import Synergy
    from moldflow.common import ViewModes, StandardViews

    synergy = Synergy()
    viewer = synergy.viewer

    viewer.reset()
    viewer.set_view_mode(ViewModes.PERSPECTIVE_PROJECTION)
    viewer.fit()
    viewer.go_to_standard_view(StandardViews.ISOMETRIC)
    viewer.save_image("C:\\temp\\snapshot.png", x=1920, y=1080, result=True, legend=True, axis=True)

Iterate Plots and Export Overlays
---------------------------------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    pm = synergy.plot_manager
    viewer = synergy.viewer

    plot = pm.get_first_plot()
    while plot:
        print(f"Plot: {plot.name}")
        try:
            viewer.save_plot_scale_image(f"C:\\temp\\{plot.name}_scale.png")
            viewer.save_axis_image(f"C:\\temp\\{plot.name}_axis.png")
        except Exception as e:
            print(f"Overlay export not available: {e}")
        plot = pm.get_next_plot(plot)

More Advanced Examples
======================

Configure Import Options Before CAD Import
------------------------------------------

.. code-block:: python

    from moldflow import Synergy
    from moldflow.common import MeshType, ImportUnits, MDLKernel

    synergy = Synergy()
    io = synergy.import_options  # ImportOptions

    # Set import preferences
    io.mesh_type = MeshType.MESH_FUSION
    io.units = ImportUnits.MM
    io.use_mdl = True
    io.mdl_kernel = MDLKernel.PARASOLID
    io.mdl_mesh = True
    io.mdl_surfaces = True
    io.mdl_auto_edge_select = True

    # Use with study import
    study_doc = synergy.study_doc
    ok = study_doc.add_file("C:\\models\\part.stp", io, show_logs=True)
    print(f"Import success: {ok}")

Tune Plot Appearance and Export
-------------------------------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    pm = synergy.plot_manager

    # Create or fetch a plot without hard-coded ids
    plot = pm.get_first_plot()

    if plot:
        # Adjust plot attributes
        plot.name = "Analysis Plot"
        plot.number_of_frames = 30
        plot.number_of_contours = 12
        plot.mesh_fill = 0.35

        # Regenerate and export results data as XML
        plot.regenerate()
        pm.save_result_data_in_xml(plot.data_id, "results.xml", "Metric")

Viewer: Animation, Clipping Planes, and Bookmarks
-------------------------------------------------

.. code-block:: python

    from moldflow import Synergy
    from moldflow.common import AnimationSpeed, StandardViews, ViewModes

    synergy = Synergy()
    viewer = synergy.viewer

    # Camera setup
    viewer.reset()
    viewer.set_view_mode(ViewModes.PERSPECTIVE_PROJECTION)
    viewer.fit()
    viewer.go_to_standard_view(StandardViews.ISOMETRIC)

    # Save a quick animation
    viewer.save_animation("C:\\temp\\turntable.mp4", AnimationSpeed.MEDIUM, prompts=False)

    # Create a default clipping plane (avoids needing an id)
    viewer.create_default_clipping_plane()

    # Create a bookmark for the current view (vectors can be None to use current state)
    viewer.add_bookmark(
        name="IsoView",
        normal_view=None,
        up_view=None,
        focal_point=None,
        eye_position=None,
        clipping_range_min=0.0,
        clipping_range_max=1.0,
        view_angle=30.0,
        parallel_scale=1.0,
    )

Publish Shared View (LMV)
-------------------------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    url = synergy.export_lmv_shared_views("My Shared Analysis View")
    print(f"Shared view published at: {url}")

API Coverage Examples
=====================

Boundary Conditions
-------------------

.. code-block:: python

    from moldflow import Synergy
    from moldflow.common import AnalysisType

    synergy = Synergy()
    bc = synergy.boundary_conditions
    entity_list = synergy.study_doc.get_first_node()
    # Create pin constraints for WARP
    created = bc.create_pin_constraints(entity_list, AnalysisType.WARP)
    print(f"Pin constraints created: {created}")

Circuit Generator
-----------------

.. code-block:: python

   from moldflow import Synergy

    synergy = Synergy()
    cg = synergy.circuit_generator
    cg.diameter = 4.0
    cg.distance = 3.0
    cg.spacing = 12.0
    cg.num_channels = 4
    cg.delete_old = True
    cg.use_hoses = True
    ok = cg.generate()
    print(f"Circuit generated: {ok}")

Data Transform
--------------

.. code-block:: python

    from moldflow import Synergy
    from moldflow.common import TransformScalarOperations

    synergy = Synergy()
    dt = synergy.data_transform
    ia = synergy.create_integer_array(); ia.from_list([1, 2, 3])
    da = synergy.create_double_array(); da.from_list([0.5, 1.5, 2.5])
    ib = synergy.create_integer_array(); db = synergy.create_double_array()
    ok = dt.scalar(ia, da, TransformScalarOperations.MULTIPLY, 2.0, ib, db)
    print(f"Scalar transform ok: {ok}")

Folder Manager
--------------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    fm = synergy.folder_manager
    root = fm.create_entity_list()
    fm.create_child_folder(root)
    fm.create_child_layer(root)
    first = fm.get_first()
    while first:
        print("Folder/Layer found")
        first = fm.get_next(first)

Layer Manager
-------------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    lm = synergy.layer_manager
    lm.create_layer_by_name("MyLayer")
    lyr = lm.get_first()
    while lyr:
        print("Layer found")
        lyr = lm.get_next(lyr)

Material Selector
-----------------

.. code-block:: python

    from moldflow import Synergy
    from moldflow.common import MaterialIndex

    synergy = Synergy()
    ms = synergy.material_selector
    # Query current material file for first molding material
    print(ms.get_material_file(MaterialIndex.FIRST))

Mesh Generator
--------------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    mg = synergy.mesh_generator
    mg.edge_length = 2.0
    mg.merge_tolerance = 0.05
    mg.match = True
    ok = mg.generate()
    print(f"Mesh generated: {ok}")

Model Duplicator
----------------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    md = synergy.model_duplicator
    md.num_cavities = 2
    md.by_columns = True
    md.num_cols = 2
    md.num_rows = 1
    md.x_spacing = 50.0
    md.y_spacing = 40.0
    ok = md.generate()
    print(f"Model duplicated: {ok}")

Modeler
-------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    modeler = synergy.modeler
    v = synergy.create_vector(); v.set_xyz(0.0, 0.0, 0.0)
    node_list = modeler.create_node_by_xyz(v)
    print("Created node list")

Mold Surface Generator
----------------------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    msg = synergy.mold_surface_generator
    msg.centered = True
    dim = synergy.create_vector(); dim.set_xyz(100.0, 80.0, 60.0)
    msg.dimensions = dim
    ok = msg.generate()
    print(f"Mold surface generated: {ok}")

Predicate Manager
-----------------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    pmgr = synergy.predicate_manager
    pmgr.create_thickness_predicate(0.5, 3.0)
    print("Created thickness predicate")

Runner Generator
----------------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    rg = synergy.runner_generator
    rg.sprue_x = 0.0; rg.sprue_y = 0.0; rg.sprue_length = 30.0
    rg.sprue_diameter = 6.0; rg.sprue_taper_angle = 2.0
    ok = rg.generate()
    print(f"Runner generated: {ok}")

Study Document
--------------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    sd = synergy.study_doc
    print(f"Study name: {sd.study_name}")
    saved = sd.save()
    print(f"Saved: {saved}")

System Messages
---------------

.. code-block:: python

    from moldflow import Synergy
    from moldflow.common import SystemUnits

    synergy = Synergy()
    sm = synergy.system_message
    sa = synergy.create_string_array(); sa.from_list(["Diameter", "Length"])
    da = synergy.create_double_array(); da.from_list([6.0, 30.0])
    msg = sm.get_data_message(100, sa, da, SystemUnits.METRIC)
    print(msg)

Arrays and Geometry Helpers
---------------------------

.. code-block:: python

    from moldflow import Synergy

    synergy = Synergy()
    ia = synergy.create_integer_array(); ia.from_list([1, 2, 3]); print(ia.size)
    da = synergy.create_double_array(); da.from_list([0.1, 0.2])
    sa = synergy.create_string_array(); sa.from_list(["A", "B"])
    vec = synergy.create_vector(); vec.set_xyz(1.0, 2.0, 3.0)
    va = synergy.create_vector_array()

API Reference
=============

For detailed API documentation, see the :doc:`moldflow` section.

Development Setup
=================

If you're interested in contributing to the project:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/Autodesk/moldflow-api.git
   cd moldflow-api

   # Install development dependencies
   python -m pip install -r requirements.txt

   # Run tests
   python run.py test

   # Run linting
   python run.py lint

   # Format code
   python run.py format

Available Commands
------------------

The project includes a ``run.py`` script with several useful commands:

- ``python run.py build`` - Build the package
- ``python run.py test`` - Run tests
- ``python run.py lint`` - Run code linting
- ``python run.py format`` - Format code with black
- ``python run.py build-docs`` - Build documentation

Contributing
============

We welcome contributions! Please see our `Contributing Guide <https://github.com/Autodesk/moldflow-api/blob/main/CONTRIBUTING.md>`_ for details on how to contribute to this project.

Reporting Issues
================

If you encounter any problems or have feature requests, please file an issue on our `GitHub Issues page <https://github.com/Autodesk/moldflow-api/issues>`_.

For security vulnerabilities, please see our `Security Policy <https://github.com/Autodesk/moldflow-api/blob/main/SECURITY.md>`_.

License
=======

This project is licensed under the Apache License 2.0 - see the `LICENSE <https://github.com/Autodesk/moldflow-api/blob/main/LICENSE>`_ file for details.

Links
=====

- **GitHub Repository**: https://github.com/Autodesk/moldflow-api
- **PyPI Package**: https://pypi.org/project/moldflow
- **Issue Tracker**: https://github.com/Autodesk/moldflow-api/issues
