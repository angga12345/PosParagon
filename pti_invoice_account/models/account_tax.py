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
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
import logging
_log = logging.getLogger(__name__)

class AccountTax(models.Model):
    _inherit = 'account.tax'
    _description = "change amount compute result"

    @api.v8
    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):
        """ Returns all information required to apply taxes (in self + their children in case of a tax goup).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }]
        } """
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        taxes = []
        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        prec = currency.decimal_places
        if company_id.tax_calculation_rounding_method == 'round_globally':
            prec += 5
        total_excluded = total_included = base = round(price_unit * quantity, prec)

        for tax in self:
            if tax.amount_type == 'group':
                ret = tax.children_tax_ids.compute_all(price_unit, currency, quantity, product, partner)
                total_excluded = ret['total_excluded']
                base = ret['total_excluded']
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                taxes += ret['taxes']
                continue

            tax_amount = tax._compute_amount(base, price_unit, quantity, product, partner)
            if company_id.tax_calculation_rounding_method == 'round_globally':
                tax_amount = round(tax_amount, prec)
            else:
                tax_amount = currency.round(tax_amount)
            
            if tax_amount:
                if tax.price_include:
                    total_excluded -= tax_amount
                    base -= tax_amount
                else:
                    total_included += tax_amount

                if tax.include_base_amount:
                    base += tax_amount

                taxes.append({
                    'id': tax.id,
                    'name': tax.name,
                    'amount': int(tax_amount),
                    'sequence': tax.sequence,
                    'account_id': tax.account_id.id,
                    'refund_account_id': tax.refund_account_id.id,
                    'analytic': tax.analytic,
                })
        _log.info ("taxxxxxxxxxxxxx %s" % taxes)
        _log.info ("taxxxxxxxxxxxxx %s" % total_excluded)
        _log.info ("taxxxxxxxxxxxxx %s" % total_included)
        return {
            'taxes': sorted(taxes, key=lambda k: k['sequence']),
            'total_excluded': currency.round(total_excluded),
            'total_included': currency.round(total_included),
        }

