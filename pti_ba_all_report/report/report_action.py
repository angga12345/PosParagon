from openerp import models, api, fields, _


class CurrentBussinessAllReport(models.AbstractModel):
    _name = 'report.pti_ba_all_report.ba_view_all_report'
    _template = 'pti_ba_all_report.ba_view_all_report'

    @api.multi
    def _lines(self,date_wizard):
          lines=[]
          groups_id=self.env.ref('pti_pos_pricelist_discount.BA_group')
          domain = [('groups_id.id', '=', groups_id.id)]
          salesmen = self.env['res.users'].search(domain)
          for sales in salesmen:
              orders=self.env['pos.order'].search([('user_id','=',sales.id)]) 
              total=0
              for order in orders:
                do = fields.Date.to_string(fields.Date.from_string(order.date_order))
                if do == date_wizard:
                    total += order.amount_total
              vals = {
                'Salesman': sales.name,
                'Total': total
              }
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

CurrentBussinessAllReport()
