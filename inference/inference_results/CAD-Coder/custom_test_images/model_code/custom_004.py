import cadquery as cq
# Generating a workplane for sketch 0
wp_sketch0 = cq.Workplane(cq.Plane(cq.Vector(-0.28125, 0.0, 0.0), cq.Vector(1.0, 6.123233995736766e-17, -6.123233995736766e-17), cq.Vector(6.123233995736766e-17, -1.0, 6.123233995736766e-17)))
loop0=wp_sketch0.moveTo(0.28421052631578947, 0.0).lineTo(0.5605263157894737, 0.0).lineTo(0.84375, 0.0).lineTo(0.84375, 0.28421052631578947).lineTo(0.5605263157894737, 0.28421052631578947).lineTo(0.28421052631578947, 0.28421052631578947).lineTo(0.0, 0.28421052631578947).lineTo(0.0, 0.0).close()
solid0=wp_sketch0.add(loop0).extrude(0.28125)
solid=solid0
import cadquery as cq
cq.exporters.export(solid, "./inference/inference_results/CAD-Coder/custom_test_images/model_stl/custom_004.stl")

import cadquery as cq
cq.exporters.export(solid, "./inference/inference_results/CAD-Coder/custom_test_images/model_step/custom_004.step")
