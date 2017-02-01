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

class ConfirmValidation(models.TransientModel):
    _name = 'confirm.validation'
    
    bank_statement = fields.Many2one('account.bank.statement', 'Bank Statement')
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(ConfirmValidation, self).default_get(cr, uid, fields, context=context)
        res.update({'bank_statement' : context.get('active_id') or False})
        return res
    
    def do_validation(self, cr, uid, ids, context=None):
        if context is None: context = {}
        res = self.pool.get('account.bank.statement').browse(cr, uid, context.get('active_id') or False, context)
        res.check_confirm_bank()
        return True

