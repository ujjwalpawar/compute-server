#!/usr/bin/env python

kube_description= \
"""
Compute Cluster
"""
kube_instruction= \
"""
Not instructions yet
"""


import geni.portal as portal
import geni.rspec.pg as PG
import geni.rspec.igext as IG


pc = portal.Context()
rspec = PG.Request()


# Profile parameters.
pc.defineParameter("machineNum", "Number of Machines",
                   portal.ParameterType.INTEGER, 1)
pc.defineParameter("Hardware", "Machine Hardware",
                   portal.ParameterType.STRING,"d430",[("d430","d430"),("d710","d710"), ("d820", "d820"), ("pc3000", "pc3000")])
pc.defineParameter("OS", "Operating System",
                   portal.ParameterType.STRING,"ubuntu18",[("ubuntu18","ubuntu18"),("ubuntu20","ubuntu20"), ("ubuntu22", "ubuntu22")])

pc.defineParameter("isolcpus", "Isolated CPUs (True or False)",
                   portal.ParameterType.BOOLEAN, True,
                   advance=True)

pc.defineParameter("isolcpus_num", "Number of Isolated CPUs",
                   portal.ParameterType.INTEGER, 1,
                   advanced=True)

pc.defineParameter("isolcpus_numa", "Isolated CPUs in the same NUMA node (True or False)",
                   portal.ParameterType.BOOLEAN, True,
                   advance=True)

params = pc.bindParameters()

#
# Give the library a chance to return nice JSON-formatted exception(s) and/or
# warnings; this might sys.exit().
#
pc.verifyParameters()



tour = IG.Tour()
tour.Description(IG.Tour.TEXT,kube_description)
tour.Instructions(IG.Tour.MARKDOWN,kube_instruction)
rspec.addTour(tour)


# Network
netmask="255.255.255.0"
network = rspec.Link("Network")
network.link_multiplexing = True
network.vlan_tagging = True
network.best_effort = True

if params.OS == 'ubuntu20':
    os = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU20-64-STD'
elif params.OS == 'ubuntu22':
    os = 'urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-BETA'
else:
    os = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'

profileConfigs = ""
# Configuration parsing
if params.isolcpus == True:
    profileConfigs += 'PROFILE_CONF_COMMAND_ISOLCPU="/local/repository/scripts/isolcpus.sh" '
    if params.isolcpu_numa == True:
        numa = "yes"
    else:
        numa = "no"
    profileConfigs += 'PROFILE_CONF_COMMAND_ISOLCPU_ARGS="%d %s" ' % (params.isolcpus_num, numa)

# Machines
for i in range(0,params.machineNum):
    node = rspec.RawPC("node" + str(i))
    node.disk_image = os
    node.hardware_type = params.Hardware
    node.addService(PG.Execute(shell="bash", command=profileConfigs + "/local/repository/scripts/configure.sh"))
    iface = node.addInterface()
    iface.addAddress(PG.IPv4Address("192.168.1."+str(i+1), netmask))
    network.addInterface(iface)


#
# Print and go!
#
pc.printRequestRSpec(rspec)
