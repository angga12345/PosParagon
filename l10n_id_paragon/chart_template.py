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

from openerp.exceptions import AccessError, UserError, ValidationError
from openerp import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class WizardMultiChartsAccounts(models.TransientModel):
    _inherit = 'wizard.multi.charts.accounts'
    
    @api.multi
    def execute(self):
        '''
        This function is called at the confirmation of the wizard to generate the COA from the templates. It will read
        all the provided information to create the accounts, the banks, the journals, the taxes, the
        accounting properties... accordingly for the chosen company.
        '''
        if len(self.env['account.account'].search([('company_id', '=', self.company_id.id)])) > 0:
            # We are in a case where we already have some accounts existing, meaning that user has probably
            # created its own accounts and does not need a coa, so skip installation of coa.
            _logger.info('Could not install chart of account since some accounts already exists for the company (%s)', (self.company_id.id,))
            return {}
        if not self.env.user._is_admin():
            raise AccessError(_("Only administrators can change the settings"))
        ir_values_obj = self.env['ir.values']
        company = self.company_id
        self.company_id.write({'currency_id': self.currency_id.id,
                               'accounts_code_digits': self.code_digits,
                               'anglo_saxon_accounting': self.use_anglo_saxon,
                               'bank_account_code_prefix': self.bank_account_code_prefix,
                               'cash_account_code_prefix': self.cash_account_code_prefix,
                               'chart_template_id': self.chart_template_id.id})

        #set the coa currency to active
        self.currency_id.write({'active': True})

        # When we install the CoA of first company, set the currency to price types and pricelists
        if company.id == 1:
            for reference in ['product.list_price', 'product.standard_price', 'product.list0']:
                try:
                    tmp2 = self.env.ref(reference).write({'currency_id': self.currency_id.id})
                except ValueError:
                    pass

        # If the floats for sale/purchase rates have been filled, create templates from them
        self._create_tax_templates_from_rates(company.id)

        # Install all the templates objects and generate the real objects
        acc_template_ref, taxes_ref = self.chart_template_id._install_template(company, code_digits=self.code_digits, transfer_account_id=self.transfer_account_id)

        # write values of default taxes for product as super user
        if self.sale_tax_id and taxes_ref:
            ir_values_obj.sudo().set_default('product.template', "taxes_id", [taxes_ref[self.sale_tax_id.id]], for_all_users=True, company_id=company.id)
        if self.purchase_tax_id and taxes_ref:
            ir_values_obj.sudo().set_default('product.template', "supplier_taxes_id", [taxes_ref[self.purchase_tax_id.id]], for_all_users=True, company_id=company.id)

        # Create Bank journals
#         self._create_bank_journals_from_o2m(company, acc_template_ref)

        # Create the current year earning account (outside of the CoA)
        #self.env['account.account'].create({
        #    'code': '9999',
        #    'name': _('Undistributed Profits/Losses'),
        #    'user_type_id': self.env.ref("account.data_unaffected_earnings").id,
        #    'company_id': company.id,})
        return {}
        #return super(WizardMultiChartsAccounts, self).execute()

