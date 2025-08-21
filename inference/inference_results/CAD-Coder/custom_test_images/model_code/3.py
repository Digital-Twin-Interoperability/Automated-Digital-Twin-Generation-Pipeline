import cadquery as cq
# Generating a workplane for sketch 0
wp_sketch0 = cq.Workplane(cq.Plane(cq.Vector(-0.5390625, 0.0, 0.0), cq.Vector(1.0, 6.123233995736766e-17, -6.123233995736766e-17), cq.Vector(6.123233995736766e-17, -1.0, 6.123233995736766e-17)))
loop0=wp_sketch0.moveTo(0.5407894736842105, 0.0).circle(0.5407894736842105)
solid0=wp_sketch0.add(loop0).extrude(0.3984375)
solid=solid0
import cadquery as cq
cq.exporters.export(solid, "./inference/inference_results/CAD-Coder/custom_test_images/model_stl/3.stl")

import cadquery as cq
cq.exporters.export(solid, "./inference/inference_results/CAD-Coder/custom_test_images/model_step/3.step")
