import cadquery as cq
# Generating a workplane for sketch 0
wp_sketch0 = cq.Workplane(cq.Plane(cq.Vector(-0.75, 0.0, 0.0), cq.Vector(1.0, 6.123233995736766e-17, -6.123233995736766e-17), cq.Vector(6.123233995736766e-17, -1.0, 6.123233995736766e-17)))
loop0=wp_sketch0.moveTo(0.25263157894736843, 0.0).lineTo(0.25263157894736843, 0.12631578947368421).lineTo(0.49736842105263157, 0.12631578947368421).lineTo(0.49736842105263157, 0.0).lineTo(0.75, 0.0).lineTo(0.75, 0.25263157894736843).lineTo(0.0, 0.25263157894736843).lineTo(0.0, 0.0).close()
solid0=wp_sketch0.add(loop0).extrude(0.5)
solid=solid0
# Generating a workplane for sketch 1
wp_sketch1 = cq.Workplane(cq.Plane(cq.Vector(-0.25, 0.0, 0.125), cq.Vector(1.0, 6.123233995736766e-17, -6.123233995736766e-17), cq.Vector(6.123233995736766e-17, -1.0, 6.123233995736766e-17)))
loop1=wp_sketch1.moveTo(0.25, 0.0).lineTo(0.25, 0.12631578947368421).lineTo(0.0, 0.12631578947368421).lineTo(0.0, 0.0).close()
solid1=wp_sketch1.add(loop1).extrude(0.5)
solid=solid.union(solid1)
import cadquery as cq
cq.exporters.export(solid, "./inference/inference_results/CAD-Coder/custom_test_images/model_stl/1.stl")

import cadquery as cq
cq.exporters.export(solid, "./inference/inference_results/CAD-Coder/custom_test_images/model_step/1.step")
