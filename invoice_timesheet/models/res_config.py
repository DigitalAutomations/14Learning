# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = "res.company"

    timesheet_product_id = fields.Many2one('product.product', string='Timesheet Product')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    timesheet_product_id = fields.Many2one('product.product', string='Timesheet Product')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            timesheet_product_id=self.env.user.company_id.timesheet_product_id and self.env.user.company_id.timesheet_product_id.id or False,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.ensure_one()
        if not self.env.user._is_admin():
            raise AccessError(_("Only administrators can change the settings"))

        self.env.user.company_id.timesheet_product_id = self.timesheet_product_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: