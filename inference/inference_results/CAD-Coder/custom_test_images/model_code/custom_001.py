import cadquery as cq
# Generating a workplane for sketch 0
wp_sketch0 = cq.Workplane(cq.Plane(cq.Vector(-0.5390625, -0.75, 0.0), cq.Vector(1.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0)))
loop0=wp_sketch0.moveTo(1.0736842105263158, 0.0).lineTo(1.0736842105263158, 1.5).lineTo(0.0, 1.5).lineTo(0.0, 0.0).close()
solid0=wp_sketch0.add(loop0).extrude(0.3984375)
solid=solid0
# Generating a workplane for sketch 1
wp_sketch1 = cq.Workplane(cq.Plane(cq.Vector(-0.5390625, -0.75, 0.0), cq.Vector(1.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0)))
loop1=wp_sketch1.moveTo(1.0736842105263158, 0.0).lineTo(1.0736842105263158, 1.5).lineTo(0.0, 1.5).lineTo(0.0, 0.0).close()
solid1=wp_sketch1.add(loop1).extrude(0.3984375)
solid=solid.union(solid1)
import cadquery as cq
cq.exporters.export(solid, "./inference/inference_results/CAD-Coder/custom_test_images/model_stl/custom_001.stl")

import cadquery as cq
cq.exporters.export(solid, "./inference/inference_results/CAD-Coder/custom_test_images/model_step/custom_001.step")
