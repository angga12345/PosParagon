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

# -*- coding: utf-8 -*-
{
    'name'          : 'Template Report Delivery and Proforma Invoice',
    'version'       : '2.0',
    'summary'       : 'Create Template Report Delivery Note and Proforma Invoice',
    'sequence'      : 5,
    'description'   : """
   
                        author : elsy S.T 
                        
                        v.1.0 : \n
                        make Template Report for Delivery Note and Proforma Invoice like a Request \n
                        
                        v.2.0 : \n
                        new report version
            
                      """,
    'category'      : 'reports',
    'depends'       : ['pti_customers'],
    'data'          : [
                        'action_report.xml',
                        'wizard/picking_consolidate.xml',
                        'views/proforma_invoice_view.xml',
                        'views/template_delivery_note.xml',
                        'views/template_delivery_note_sorted.xml',
                        'views/picking_list_printed.xml',
                        'views/do.xml',
                        'views/template_internal_transfer.xml',
                        'views/template_consolidate_product.xml',
                        'views/template_tracking_shipment.xml',
                        'security/ir.actions.report.xml.csv',
                        'security/report.paperformat.csv',
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}

