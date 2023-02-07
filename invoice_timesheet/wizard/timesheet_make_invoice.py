# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _

from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class TimesheetInvoice(models.TransientModel):
    _name = "timesheet.invoice"
    _description = "Timesheet Invoice"

    groupby_project = fields.Boolean(string='Groupby Project', default=False,
        help='Set true if want to create single invoice for project')
    groupby_partner  = fields.Boolean(string='Groupby Project Partner', default=False,
        help='Set true if want to create single invoice for project')
    groupby_task_partner = fields.Boolean(string='Groupby Task Partner', default=False,
        help='Set true if want to create single invoice for Task Customer')
    print_time = fields.Boolean(string='Add timesheet Date in Invoice line Description', default=False,
        help='Set true if want to append timesheet date in invoice line')
    print_description = fields.Boolean(string='Add timesheet Description in Invoice line Description', default=False,
        help='Set true if want to append timesheet date in invoice line')

    def create_invoice(self, line, partner_id=False):
        inv_obj = self.env['account.move']
        if not partner_id:
            partner_id = line.partner_id
        if not partner_id and line.project_id.partner_id:
            partner_id = line.project_id.partner_id
        if not partner_id:
            raise UserError(_('Please set Customer on project or analytic account first.'))
        invoice = inv_obj.create({
            'move_type': 'out_invoice',
            'ref': False,
            'partner_id': partner_id.id,
            'partner_shipping_id': partner_id.id,
        })
        return invoice

    def create_invoice_line(self, line, invoice, product_id, print_detail=False, print_description=False, price=0):
        inv_line_obj = self.env['account.move.line']
        lang = self.env['res.lang'].sudo().search([('code','=',self.env.user.lang)])
        account_id = product_id.property_account_income_id or product_id.categ_id.property_account_income_categ_id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (product_id.name,))
        name = product_id.name

        if print_description:
            name = name + ': ' + line.name

        if print_detail:
            date_data = line.date.strftime(DEFAULT_SERVER_DATE_FORMAT)
            name = name + ' on ' + date_data

        inv_line_obj.with_context(check_move_validity=False).create({
            'move_id': invoice.id,
            'name': name,
            'account_id': account_id.id,
            'price_unit': price or product_id.lst_price,
            'quantity': line.unit_amount,
            'discount': 0.0,
            'product_uom_id': product_id.uom_id.id,
            'product_id': product_id.id,
            'tax_ids': [(6, 0, product_id.taxes_id and product_id.taxes_id.ids or [])],
        })
        

    def create_invoices(self):
        Line = self.env['account.analytic.line']
        groupby = False
        invoices = []

        if self.groupby_project:
            groupby = 'project_id'
        if self.groupby_partner:
            groupby = 'partner_id'
        if self.groupby_task_partner:
            groupby = 'task_partner_id'

        if groupby:
            timesheet_group = Line.read_group([('id', 'in', self._context.get('active_ids', [])),
                ('acs_invoice_id', '=', False)] , fields=[groupby], groupby=[groupby])
            for group in timesheet_group:
                domain = [('id', 'in', self._context.get('active_ids', [])),
                    ('acs_invoice_id', '=', False)]
                if group[groupby]:
                    domain += [(groupby, '=', int(group[groupby][0]))]
                timesheet_lines = Line.search(domain)
                if timesheet_lines:
                    if self.groupby_task_partner:
                        invoice = self.create_invoice(timesheet_lines[0],timesheet_lines[0].task_partner_id)
                    else:
                        invoice = self.create_invoice(timesheet_lines[0])
                    invoices.append(invoice.id)
                    for line in timesheet_lines:
                        product_id = False
                        price = 0
                        if line.task_id.sale_line_id:
                            product_id = line.task_id.sale_line_id.product_id
                            price = line.task_id.sale_line_id.price_unit

                        if not product_id:
                            product_id = line.product_id or (line.project_id and line.project_id.product_id) or self.env.user.company_id.timesheet_product_id
                        if not product_id:
                            raise UserError(_('Please set Timesheet Product in General Settings or configure Proper product in line or related project first.'))
                        
                        self.create_invoice_line(line, invoice, product_id, self.print_time, self.print_description, price)
                        line.acs_invoice_id = invoice.id

        else:
            timesheet_lines = Line.browse(self._context.get('active_ids', []))
            for line in timesheet_lines:
                if not line.acs_invoice_id:
                    product_id = False
                    price = 0
                    if line.task_id.sale_line_id:
                        product_id = line.task_id.sale_line_id.product_id
                        price = line.task_id.sale_line_id.price_unit
                    if not product_id:
                        product_id = line.product_id or (line.project_id and line.project_id.product_id) or self.env.user.company_id.timesheet_product_id
                    if not product_id:
                        raise UserError(_('Please set Timesheet Product in General Settings or configure Proper product in line or related project first.'))
                    invoice = self.create_invoice(line)
                    invoices.append(invoice.id)
                    self.create_invoice_line(line, invoice, product_id, self.print_time, self.print_description, price)
                    line.acs_invoice_id = invoice.id

        if not invoices:
            raise UserError(_('Please check there is nothing to invoice in selected lines may be you are missing partner or trying to invoice already invoiced lines.'))

        acs_invoices = self.env['account.move'].search([('id','in',invoices)])
        for invoice in acs_invoices:
            invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_tax_base_amount=True)

        if self._context.get('open_invoices', False):
            action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
            if len(invoices) > 1:
                action['domain'] = [('id', 'in', invoices)]
            elif len(invoices) == 1: 
                action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
                action['res_id'] = invoices[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action
        return {'type': 'ir.actions.act_window_close'}
