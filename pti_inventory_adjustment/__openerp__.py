# Copyright (C) 2016 by PT Paragon Technology And Innovation
#
# This file is part of PTI Odoo Addons.
#
# PTI Odoo Addons is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PTI Odoo Addons is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PTI Odoo Addons.  If not, see <http://www.gnu.org/licenses/>.

{
    "name": "PCI: Fast Inventory Adjustment",
    "version": "1.0",
    "author": "portcities .ltd",
    "website": "http://www.portcities.net",
    "category": "Generic Modules",
    "depends": ["stock"],
    "description": """
        Stock Adjustment 
    Current status & target:
Current status :  
For start inventory button needs 2 minutes to generate 1998 line adjustments
Validate inventory needs 1 hour to make done
The inventory adjustment will create new quants to make the quantity on hand updated but it is remove quant history
Target
For 1000 lines possible to execute in 0,0009999996


Analysis : \n
Prepare_inventory : the process to get the inventory line from available quantity on quants\n
Get all location and children location that have available quantity\n
Write into inventory line to be proceed to the stock move\n
action _done : process to update the inventory by create new picking from balance location to physical location and transfer it in the same time\n
Action_check : check quants available and not reserve then decide which quant need to reserve by the move for inventory adjustment\n
Check if there are quants available for it’s product if yes continue to resolve inventory line\n
Resolve_inventory_line : reserve the quents and prepare the operations to create quants for adjustment\n
Post_inventory : the process to post the inventory as new quants and update quantity on hand (using action done of stock move)\n
In action_done stock move : the process to makes the status of stock move in done and process the reserved quants\n
\n
Proposed :\n
Update the function and calculation to get the current quantity on hand in order to fill it on inventory adjustment line\n
Update function to query on creation of inventory adjustment line\n
Update the function create stock move in resolve_inventory_valuation\n
Using the improvement function for action done that is used for sale order DO\n

""",
    "demo_xml":[],
    "data":[],
    "active": False,
    "installable": True
}

