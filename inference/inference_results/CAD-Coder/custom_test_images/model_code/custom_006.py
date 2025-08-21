import cadquery as cq
# Generating a workplane for sketch 0
wp_sketch0 = cq.Workplane(cq.Plane(cq.Vector(-0.28125, 0.0, 0.0), cq.Vector(1.0, 6.123233995736766e-17, -6.123233995736766e-17), cq.Vector(6.123233995736766e-17, -1.0, 6.123233995736766e-17)))
loop0=wp_sketch0.moveTo(0.28421052631578947, 0.0).circle(0.27828947368421053)
solid0=wp_sketch0.add(loop0).extrude(0.75)
solid=solid0
# Generating a workplane for sketch 1
wp_sketch1 = cq.Workplane(cq.Plane(cq.Vector(-0.2421875, 0.0, 0.0), cq.Vector(1.0, 6.123233995736766e-17, -6.123233995736766e-17), cq.Vector(6.123233995736766e-17, -1.0, 6.123233995736766e-17)))
loop1=wp_sketch1.moveTo(0.24078947368421053, 0.0).circle(0.24078947368421053)
solid1=wp_sketch1.add(loop1).extrude(0.75)
solid=solid.union(solid1)
import cadquery as cq
cq.exporters.export(solid, "./inference/inference_results/CAD-Coder/custom_test_images/model_stl/custom_006.stl")

import cadquery as cq
cq.exporters.export(solid, "./inference/inference_results/CAD-Coder/custom_test_images/model_step/custom_006.step")
