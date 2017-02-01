from openerp import models, fields, api


class CurrentBussinessAllReportWizard(models.TransientModel):
    _name = "current.bussiness.all.report.wizard"
    _template = 'pti_ba_all_report.ba_view_all_report'
    
    date= fields.Date('Date')
    
    @api.multi
    def do_print(self):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(self._template)
        data = {
            'date_order':self.date,
        }
        datas = {
            'ids': [self.ids],
            'model': report.model,
            'form': data,
        }
        return report_obj.get_action(self, self._template, data=datas)
    

CurrentBussinessAllReportWizard()
