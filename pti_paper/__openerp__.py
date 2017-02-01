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
    'name'          : 'PTI Paper Format ',
    'version'       : '1.0',
    'summary'       : 'Create paper format',
    'sequence'      : 1,
    'depends'       : ['pti_do_report','pti_invoice_report'],
    'description'   : """
                        author : elsy S.T 
                        
                        v.1.0 : \n
                        create paper format (landscape)
            
                      """,
    'category'      : 'report',
    'data'          : [
                       'views/paper_format_pti_view.xml',
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}

