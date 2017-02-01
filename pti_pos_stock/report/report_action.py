from openerp import models, api


class CurrentStockReport(models.AbstractModel):
    _name = 'report.pti_pos_stock.current_stock_report_view'
    _template = 'pti_pos_stock.current_stock_report_view'

    @api.multi
    def _lines(self, warehouse_id):
        vals, lines = {'product': '', 'qty': 0}, []
        self.env.cr.execute("SELECT p.name, sum(sq.qty) as "'current_stock'" "
                            "FROM stock_quant sq join product_template p "
                            "ON sq.product_id = p.id "
                            "WHERE sq.location_id = %s "
                            "GROUP BY p.id, sq.location_id", ([(warehouse_id)]))
        result = self.env.cr.dictfetchall()
        for quant in result:
            vals = {'product': quant['name'], 'qty': quant['current_stock']}
            lines.append(vals)
        return lines

    @api.multi
    def render_html(self, data):
        report_obj = self.env['report']
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'data': data['form'],
            'get_lines': self._lines,
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
        }
        return report_obj.render(self._template, docargs)

CurrentStockReport()
