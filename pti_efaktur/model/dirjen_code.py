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
from openerp.exceptions import UserError
from datetime import datetime, timedelta
import pytz
from openerp import SUPERUSER_ID

class DirjenTaxCode(models.Model):
    _name = "dirjen.tax.code"

    name = fields.Char('VAT Number')
    validated = fields.Boolean('Validated', help="if already updloaded to e-pajak check this", default=False)
    invoice_id = fields.Many2one('account.invoice', 'Invoice', help="If you can't find invoice mean already have serial number")
    date_validated = fields.Date('Date validate')
    dc_id = fields.Many2one('res.partner',related='invoice_id.dc_id',string='Distribution Center',  help='Distribution center' )
    npwp_o = fields.Boolean('NPWP000', default=False)
    date_assign = fields.Date('Date Assign')
    
    @api.one
    def _groups_access(self):
        allow = True
        no_access = [
                     {'module' : 'pti_branch', 'group_id' : 'group_pti_branch_sales_admin_invoice'}
                    ]
        ir_model_data = self.env['ir.model.data']
        res = []
        for data in no_access:
            temp = ir_model_data.get_object_reference(data['module'], data['group_id'])[1]
            if temp:
                res.append(temp)
        user = self.env.user
        not_allowed_group_ids = tuple(res)

        for group in user.groups_id:
            if group.id in not_allowed_group_ids:
                allow = False
                break
            
        self.access_group = allow
    
    @api.multi
    def write(self, values):
        if values.get('invoice_id') == False:
            inv_ids = self.env['account.invoice'].search([('dirjen_tax_id','=',self.id)])
            if inv_ids:
                inv_ids.write({'dirjen_tax_id':False})
        elif values.get('invoice_id'):
            # invoice which have dirjen serial number imposible choosen.
            # blocked using domain in xml view
            inv = self.env['account.invoice'].browse([values.get('invoice_id')])
            if not inv.dirjen_tax_id.id:
                inv.write({'dirjen_tax_id':self.id})
                # removing dirjen serial number in previous invoice
                self.invoice_id.write({'dirjen_tax_id' : False})
            else:
                raise UserError(_("%s have serial number %s!" % (inv.number, inv.dirjen_tax_id.name)))
        if not values.get('date_validated',False):
            values['date_validated'] = datetime.now()
        result = super(DirjenTaxCode, self).write(values)
        return result
        
    access_group = fields.Boolean(compute='_groups_access', string='Access groups', default=True)

class AccountInvoiceToDirgenTaxCode(models.Model):
    _inherit="account.invoice"

    dirjen_tax_id = fields.Many2one('dirjen.tax.code', string="VAT Number", copy=False)

    @api.multi
    def invoice_validate(self):
        '''
        THIS CODE EXTENDS IN HERE BECAUSE THIS FUNCTION ALREADY OVERIDE IN pti_invoice_account
        '''
        for invoice in self:
            if not invoice.dirjen_tax_id and invoice.type == 'out_invoice':
                dirjen_tax_id = False
                dirjen_tax_src = self.env['dirjen.tax.code'].search([('invoice_id','=',False)], limit=1)
                dirjen_tax_src.write({'invoice_id': invoice.id, 'date_assign' : fields.date.today()})
                dirjen_tax_id = dirjen_tax_src.id
                invoice.write({'dirjen_tax_id': dirjen_tax_id})
        return super(AccountInvoiceToDirgenTaxCode, self).invoice_validate()