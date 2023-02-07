import datetime
import logging

from odoo import api, models, fields
from odoo.tools import float_is_zero, UserError


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    project_id = fields.Many2one('project.project')
    summary = fields.Text()
    is_ordine_quadro = fields.Boolean(help="Indica se l'ordine è di tipo 'Quadro'. Se flaggato, non mostra l'ordine lato portale cliente")
