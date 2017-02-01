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


class PickingSortOrder(models.Model):
    _name = "picking.sort.order"

    name = fields.Char('Name')
    dc_id = fields.Many2one('res.partner', 'Distribution Center')
    location_id = fields.Many2one('stock.location', 'Location')
    picking_sort_order_lines = fields.One2many('picking.sort.order.line', 'picking_sort_order_id', 'List sort order')


class PickingSortOrderLine(models.Model):
    _name = "picking.sort.order.line"
    _order = "index asc"

    picking_sort_order_id = fields.Many2one('picking.sort.order', 'Picking sort order')
    product_id = fields.Many2one('product.product', 'Product')
    index = fields.Integer('Index')

    _sql_constraints = [
            ('product_id_uniq', 'unique (product_id, picking_sort_order_id)', 'Product already exists !'),
            ('index_uniq', 'unique (index, picking_sort_order_id)', 'Index already exist !')
            ]
