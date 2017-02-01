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
import logging
_log = logging.getLogger(__name__)
from openerp import SUPERUSER_ID

class accountJournal(models.Model):
    _inherit = "account.journal"
    
    can_view_ho = fields.Boolean(compute="_compute_access", search="_search_can_view")

    def _search_can_view(self, operator, value):
        if operator not in ('=','!=','<>'):
            raise UserError(_("operator invalid!"))
        if self._uid == SUPERUSER_ID:
            return [(1,'=',1)]
        dc_ids = False
        dc_id = False
        dc_id = self.env.user.partner_id.dc_id.id
        if not dc_id:
            return [(1,'=',1)]

        # if self.user_has_groups('account.group_account_manager'):
        #         lock_date = move.company_id.fiscalyear_lock_date
        
        if self.env.user.has_group('pti_branch.group_pti_branch_finance_admin'):
            return [(1,'=',1)]
        else:
            req = """
                select id from account_journal where
                    this_for_all = False and dc_id = %s
            """
            self.env.cr.execute(req % (dc_id,))

        ids = [i[0] for i in self.env.cr.fetchall()]
        op = operator == '=' and "in" or "not in"
        return [('id', op, ids)]

    @api.multi
    def _compute_access(self):
        dc_user = self.env.user.partner_id.dc_id.id
        for journal in self:
            if journal.location_id.dc_id.id == dc_user or journal.location_dest_id.dc_id.id == dc_user:
                journal.can_view_ho = True