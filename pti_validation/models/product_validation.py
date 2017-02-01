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

from openerp import models, fields, api, _


class productvalidation(models.Model):
    _inherit='product.template'
    
    @api.model
    def default_get(self, vals):
        rec = super(productvalidation, self).default_get(vals)
        
        rec.update({
            'sale_ok': False,
        })
        return rec
    
    @api.model
    def create(self, vals):
        ir_model_data = self.env['ir.model.data']
        try:
            group_id = ir_model_data.get_object_reference('pti_validation', 'pti_prodev')[1]
        except ValueError:
            group_id = False
        group_prodev = self.env['res.groups'].search([('id', '=', group_id)])
        for prodev in group_prodev :
            for user in prodev.users :
                if self.env.user.id == user.id:
                    vals.update({
                        'state':'draft',
                        })
                    
        result = super(productvalidation, self).create(vals)
        return result 
    
    @api.multi
    def validate(self):
        return self.write({'state': 'sellable','sale_ok':True})

