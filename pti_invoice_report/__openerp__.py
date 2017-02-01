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
    'name'          : 'Template Report Invoice',
    'version'       : '1.0',
    'summary'       : 'Change Template Invoice',
    'sequence'      : 10,
    "author"        : "Port Cities",
    'description'   : """
    
                        author : elsy S.T ,Akhmad kresna, Nisfari
                        
                        v.1.0 : \n
                        make Template Report for Invoice like a Request
                        
                        v.1.1 : \n
                        update access right for pti invoice group user. \n 
                        add dc reporting menu for kdc group user triger general ledger report view with filter account journal based on user dc id
                        
                        V.1.2 : \n
                        add more filter to general ledger report
                        
                      """,
    'category'      : 'reports',
    'depends'       : ['stock', 'account'],
    'data'          : [
                        'security/menuitem_for_groups.xml',
                        'wizard/go_live_daily_report.xml',
                        'wizard/report_generalledger_view.xml',
                        'views/template_invoice_view.xml',
                        'action_report.xml',    
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False,
}

