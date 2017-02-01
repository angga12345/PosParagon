from openerp import fields, models


DAYS = [('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday')]


class LoyaltyRule(models.Model):
    _inherit = 'loyalty.rule'

    rule_time_ids = fields.One2many("loyalty.rule.time", "loyalty_rule_id", string="Rule Times")
    use_hour_rules = fields.Boolean(string="Hour Rules", default=False)


class LoyaltyRuleTime(models.Model):
    _name = 'loyalty.rule.time'

    loyalty_rule_id = fields.Many2one("loyalty.rule", string="Loyalty Rule")
    day = fields.Selection(DAYS, string="Days", required=1)
    start_hour = fields.Float(string="Start Hour", required=1)
    end_hour = fields.Float(string="End Hour", required=1)
