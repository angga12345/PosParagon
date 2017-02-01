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

from openerp import api, fields, models, _
from openerp.exceptions import UserError

class SaleConfiguration(models.TransientModel):
    _inherit = 'account.config.settings'
    
    @api.one
    @api.depends('company_id')
    def _compute_account_id(self):
        """ this function using for set account id get from account id from company """
        self.account_id = self.company_id.account_id

    @api.one
    def _set_account_id(self):
        """ this function for set account id if account id is not same with account id on company """
        if self.account_id != self.company_id.account_id:
            self.company_id.account_id = self.account_id

    group_payments = fields.Boolean('Manage Sales And\n'
                                    ' Purchases Payments',
                                    implied_group='pti_bank_statement.group_payments')
    
    """ this field display on setting on the accounting menu for set account free product """
    account_id = fields.Many2one('account.account',oldname='Account Free Product' ,string='Account Free Product',compute='_compute_account_id', inverse='_set_account_id' )

class ResCompany(models.Model):
    _inherit = 'res.company'

    """ this field using for save account id for account setting, because account setting is transient model """
    account_id = fields.Many2one('account.account','Account Free Product')
