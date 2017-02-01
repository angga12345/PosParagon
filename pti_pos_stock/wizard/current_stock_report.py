from openerp import models, fields, api


class CurrentStockReportWizard(models.TransientModel):
    _name = "current.stock.report.wizard"
    _template = 'pti_pos_stock.current_stock_report_view'

    location_id = fields.Many2one('stock.location', 'Warehouse',
                                  required=True,
                                  domain=[('usage', '=', 'internal'),('shop_id','!=',False)])

    @api.multi
    def do_print(self):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(self._template)
        data = {
            'warehouse': self.location_id.id,
            'warehouse_name': str(self.location_id.partner_id.name) + ':' + str(self.location_id.name),
        }
        datas = {
            'ids': [self.ids],
            'model': report.model,
            'form': data,
        }
        return report_obj.get_action(self, self._template, data=datas)

CurrentStockReportWizard()
