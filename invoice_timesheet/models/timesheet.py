# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime, time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    invoiceable = fields.Boolean(string='Allow Timesheet Invoicing', default=False,
        help='Set true if want to create invoice of line')
    acs_invoice_id = fields.Many2one('account.move', string='Invoice', ondelete="set null")
    task_partner_id = fields.Many2one('res.partner', related='task_id.partner_id', string='Task Customer', store=True, readonly=True)

    @api.onchange('project_id')
    def _onchange_proj_id(self):
        if self.project_id and self.project_id.invoiceable:
            self.invoiceable = True
        else:
            self.invoiceable = False

    @api.model
    def create(self, vals):
        if vals.get('project_id'):
            project = self.env['project.project'].browse(vals.get('project_id'))
            vals['invoiceable'] = project.invoiceable
        return super(AccountAnalyticLine, self).create(vals)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    product_id = fields.Many2one('product.product', string='Product')
    invoiceable = fields.Boolean(string='Allow Timesheet Invoicing', default=False,
        help='Set true if want to create invoice of timesheetline')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
