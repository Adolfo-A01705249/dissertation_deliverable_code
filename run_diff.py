import pandas as pd
from pybatfish.client.commands import *
from pybatfish.datamodel import *
from pybatfish.datamodel.answer import *
from pybatfish.datamodel.flow import *
from pybatfish.question import *
from pybatfish.question import bfq
from pathlib import Path
import sys

# Input configurations and outputs
curr_snapshot = "campion_workplace"

output_directory = "campion_workplace/outputs/"
router_regex = ".*"

# Initialize Snapshots
bf_session.host = 'localhost'
bf_set_network('network_name')

bf_init_snapshot(curr_snapshot, name="curr-snapshot", overwrite=True)

# Load Questions
load_questions()

# Run Batfish Questions
Path(output_directory).mkdir(parents=True, exist_ok=True)

result = bfq.aclDiff(nodes=router_regex).answer()
if not result.frame().empty:
    case_id = sys.argv[1]
    result.frame().to_csv(output_directory + f"acl_diff_{case_id}.csv")
    print("Diff file created")
else:
    print("NO diff file created")

# result = bfq.bgpedgediff(nodes=router_regex).answer()
# if not result.frame().empty:
#     result.frame().to_csv(output_directory + "bgp_edge_diff.csv")

# result = bfq.originatediff(nodes=router_regex).answer()
# if not result.frame().empty:
#     result.frame().to_csv(output_directory + "routes_diff.csv")

# result = bfq.admindistdiff(nodes=router_regex).answer()
# if not result.frame().empty:
#     result.frame().to_csv(output_directory + "admin_dist_diff.csv")

# result = bfq.ospfdiff(nodes=router_regex).answer()
# if not result.frame().empty:
#     result.frame().to_csv(output_directory + "ospf_diff.csv")

# result = bfq.staticroutediff(nodes=router_regex).answer()
# if not result.frame().empty:
#     result.frame().to_csv(output_directory + "static_route_diff.csv")

# result = bfq.routerdiff(nodes=router_regex).answer()
# if not result.frame().empty:
#     result.frame().to_csv(output_directory + "route_map_diff.csv")
