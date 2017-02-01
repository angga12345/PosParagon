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
    'name'          : 'Template Report E-faktur',
    'version'       : '1.2',
    'summary'       : 'Create Template Report E-faktur',
    'sequence'      : 5,
    'description'   : """
    
                        author : Helmy A.P 
                        
                        v.1.0 : \n
                        make Template Report for E-faktur\n
                        v.1.1 : \n
                        serial number code\n
                        v.1.2 : \n
                        Set dirjen tax code when validate invoice\n
                        author : PAA
            
                      """,
    'category'      : 'reports',
    'depends'       : ['pti_branch','pti_invoice_account'],
    'data'          : [
                        'security/ir.model.access.csv',
                        'security/ir_rule.xml',
                        'wizard/reexport_efaktur.xml',
                        'wizard/e_faktur_view.xml',
                        'wizard/efaktur_report.xml',
                        'views/dirjen_code.xml',
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}

