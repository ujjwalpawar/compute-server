#!/usr/bin/env python

kube_description= \
"""
Development Cluster
"""
kube_instruction= \
"""
Author: Jon Larrea
"""


import geni.portal as portal
import geni.rspec.pg as PG
import geni.rspec.igext as IG
import geni.rspec.emulab.spectrum as spectrum
import geni.rspec.emulab.pnext as pn

pc = portal.Context()
rspec = PG.Request()


# Profile parameters.
pc.defineParameter("machineNum", "Number of Machines",
                   portal.ParameterType.INTEGER, 1)
pc.defineParameter("Hardware", "Machine Hardware",
                   portal.ParameterType.STRING,"d430",[("d430","d430"),("d710","d710"), ("d820", "d820"), ("pc3000", "pc3000"), ("d740", "d740"), ("d840", "d840")])
pc.defineParameter("OS", "Operating System",
                   portal.ParameterType.STRING,"ubuntu18",[("ubuntu18","ubuntu18"),("ubuntu20","ubuntu20"), ("ubuntu22", "ubuntu22")])

# Isolated CPU parameters
pc.defineParameter("isolcpusNumber", "Number of Isolated CPUs",
                   portal.ParameterType.INTEGER, 0,
                   advanced=True)

# Kubernetes parameters
pc.defineParameter("k8s", "Install Kubernetes",
                   portal.ParameterType.BOOLEAN, False,
                   advanced=True)

dense_radios = [
    ("cnode-mario", "Mario"),
    ("cnode-moran", "Moran"),
    ("cnode-guesthouse", "Guesthouse"),
    ("cnode-ebc", "EBC"),
    ("cnode-ustar", "USTAR"),
]

pc.defineStructParameter(
    "dense_radios", "Dense Site Radios", [],
    multiValue=True,
    min=0,
    multiValueTitle="Dense Site NUC+B210 radios to allocate.",
    members=[
        portal.Parameter(
            "device",
            "SFF Compute + NI B210 device",
            portal.ParameterType.STRING,
            dense_radios[0], dense_radios,
            longDescription="A small form factor compute with attached NI B210 device at the given " \
                            "Dense Deployment site will be allocated."
        ),
    ]
)

fixed_radios = [
    ("web", "WEB, nuc1"),
    ("bookstore", "Bookstore, nuc2"),
    ("humanities", "Humanities, nuc1"),
    ("law73", "Law 73, nuc1"),
    ("ebc", "EBC, nuc1"),
    ("madsen", "Madsen, nuc1"),
    ("sagepoint", "Sage Point, nuc1"),
    ("moran", "Moran, nuc1"),
    ("cpg", "Central Parking Garage, nuc1"),
    ("guesthouse", "Guest House, nuc1"),
]

pc.defineStructParameter(
    "fixed_radios", "Fixed Endpoint Radios", [],
    multiValue=True,
    min=0,
    multiValueTitle="Fixed endpoint NUC+B210/COTSUE radios to allocate.",
    members=[
        portal.Parameter(
            "fe_id",
            "SFF Compute + NI B210 device + COTS UE",
            portal.ParameterType.STRING,
            fixed_radios[0], fixed_radios,
            longDescription="A small form factor compute with attached NI B210 and COTS UE the " \
                            "given Fixed Endpoint site will be allocated."
        ),
    ]
)

portal.context.defineStructParameter(
    "freq_ranges", "Frequency Ranges To Transmit In",
    defaultValue=[{"freq_min": 3410.0, "freq_max": 3450.0}],
    multiValue=True,
    min=0,
    multiValueTitle="Frequency ranges to be used for transmission.",
    members=[
        portal.Parameter(
            "freq_min",
            "Frequency Range Min",
            portal.ParameterType.BANDWIDTH,
            3410.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Frequency Range Max",
            portal.ParameterType.BANDWIDTH,
            3450.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ]
)

pc.defineParameter(
    name="start_vnc_dense",
    description="enable noVNC on dense nodes",
    typ=portal.ParameterType.BOOLEAN,
    defaultValue=True,
    advanced=True
)

pc.defineParameter(
    name="start_vnc_fixed",
    description="enable noVNC on fixed endpoint nodes",
    typ=portal.ParameterType.BOOLEAN,
    defaultValue=True,
    advanced=True
)



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

# Variable that stores configuration scripts and arguments
profileConfigs = ""

# Kubernetes configuration
k8s_ip = 0 # This is to calculate the IPs when K8s is installed
if params.k8s == True:
    # Declare the master node
    master = rspec.RawPC("master")
    master.hardware_type = params.Hardware
    master.routable_control_ip = True
    master.disk_image = os
    iface = master.addInterface()
    iface.addAddress(PG.IPv4Address("192.168.1.1", netmask))
    network.addInterface(iface)
    master.addService(PG.Execute(shell="bash", command="/local/repository/scripts/master.sh"))
    k8s_ip = 1
    # Configure script for the slave nodes
    profileConfigs += "PROFILE_CONF_COMMAND_K8S='/local/repository/scripts/slave.sh' "

# IsolCPU configuration
if params.isolcpusNumber > 0:
    profileConfigs += "PROFILE_CONF_COMMAND_ISOLCPU='/local/repository/scripts/isolcpus.sh' "
    profileConfigs += "PROFILE_CONF_COMMAND_ISOLCPU_ARGS='%d' " % (params.isolcpusNumber)
else:
    profileConfigs += "PROFILE_CONF_COMMAND_NOREBOOT='touch' "
    profileConfigs += "PROFILE_CONF_COMMAND_NOREBOOT_ARGS='/local/.noreboot' "

# Machines
count = 0
for i in range(0,params.machineNum):
    count += 1
    node = rspec.RawPC("node" + str(i))
    node.disk_image = os
    node.addService(PG.Execute(shell="bash", command=profileConfigs + "/local/repository/scripts/configure.sh"))
    node.hardware_type = params.Hardware
    iface = node.addInterface()
    iface.addAddress(PG.IPv4Address("192.168.1."+str(i+1+k8s_ip), netmask))
    network.addInterface(iface)

for idx, dense_radio in enumerate(params.dense_radios):
    node = rspec.RawPC("dense-{}".format(dense_radio.device.split("-")[-1]))
    node.disk_image = os
    node.addService(PG.Execute(shell="bash", command=profileConfigs + "/local/repository/scripts/configure.sh"))
    node.component_id = dense_radio.device
    # node.hardware_type = params.Hardware
    iface = node.addInterface()
    iface.addAddress(PG.IPv4Address("192.168.1."+str(1+k8s_ip+count), netmask))
    network.addInterface(iface)
    count += 1


for idx, fixed_radio in enumerate(params.fixed_radios):
    node = rspec.RawPC("{}-{}".format(fixed_radio.fe_id, "nuc2"))
    node.component_manager_id = "urn:publicid:IDN+emulab.net+authority+cm"
    # node.component_manager_id = agg_full_name
    node.disk_image = os
    node.addService(PG.Execute(shell="bash", command=profileConfigs +"/local/repository/scripts/configure.sh"))
    node.component_id = "nuc2"
    iface = node.addInterface()
    iface.addAddress(PG.IPv4Address("192.168.1."+str(1+k8s_ip+count), netmask))
    network.addInterface(iface)
    count += 1

#
# Print and go!
#
pc.printRequestRSpec(rspec)
