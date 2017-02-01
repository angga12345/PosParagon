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
    'name'          : 'PTI Font Report ',
    'version'       : '1.0',
    'summary'       : 'Create font PTI',
    'sequence'      : 1,
    'description'   : """
    
                        author : elsy S.T 
                        
                        v.1.0 : \n
                        create css font-family: ubuntu, font-size: 14px
            
                      """,
    'category'      : 'report',
    'depends'       : ['stock'],
    'data'          : [
                       'views/font_report_pti_view.xml',
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}

