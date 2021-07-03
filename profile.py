#!/usr/bin/env python

kube_description= \
"""
Compute Server
"""
kube_instruction= \
"""
Not instructions yet
"""

#
# Standard geni-lib/portal libraries
#
import geni.portal as portal
import geni.rspec.pg as PG
import geni.rspec.emulab as elab
import geni.rspec.igext as IG
import geni.urn as URN



#
# PhantomNet extensions.
#
import geni.rspec.emulab.pnext as PN 

#
# This geni-lib script is designed to run in the PhantomNet Portal.
#
pc = portal.Context()


params = pc.bindParameters()

#
# Give the library a chance to return nice JSON-formatted exception(s) and/or
# warnings; this might sys.exit().
#
pc.verifyParameters()

rspec = PG.Request()
compute = rspec.RawPC("epc")
compute.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
compute.hardware_type = 'd430'
compute.routable_control_ip = True

tour = IG.Tour()
tour.Description(IG.Tour.TEXT,kube_description)
tour.Instructions(IG.Tour.MARKDOWN,kube_instruction)
rspec.addTour(tour)

#
# Print and go!
#
pc.printRequestRSpec(rspec)
