import logging, base64
from operator import itemgetter

from odoo import http
from odoo.http import request
from odoo.tools import groupby as groupbyelem
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.sale.controllers.portal import CustomerPortal as saleportal
from odoo.addons.account.controllers.portal import PortalAccount as invoiceportal
from odoo.addons.sale_subscription.controllers.portal import CustomerPortal as subscriptionportal
from odoo.addons.helpdesk.controllers.portal import CustomerPortal as helpdeskportal


#class MyCustomerPortal(CustomerPortal):
#    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
#    def home(self, **kw):
#        ret = super().home(**kw)
#        return ret
#
#    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
#    def my_helpdesk_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content', **kw):
#        res = super().my_helpdesk_tickets(page, date_begin, date_end, sortby, **kw)
#        return res




class CustomerPortalSale(saleportal):
    def _prepare_quotations_domain(self, partner):
        orig = super()._prepare_quotations_domain(partner)

        ret = [('partner_id', '=', -1), orig[1]]
        if request.env.user.portal_quotation_access == 'own':
            ret = [('partner_id', '=', partner.id), orig[1]]
        if request.env.user.portal_quotation_access == 'all':
            if partner.parent_id:
                ret = [
                    '|', ('partner_id', 'child_of', partner.id), ('partner_id', 'child_of', partner.parent_id.id), orig[1]
                ]
            else:
                ret = [('partner_id', 'child_of', partner.id), orig[1]]
        return ret

    def _prepare_orders_domain(self, partner):
        orig = super()._prepare_orders_domain(partner)

        ret = [('partner_id', '=', -1), orig[1]]
        if request.env.user.portal_order_access == 'own':
            ret = [('partner_id', '=', partner.id), orig[1]]
        if request.env.user.portal_order_access == 'all':
            if partner.parent_id:
                ret = [
                    '|', ('partner_id', 'child_of', partner.id), ('partner_id', 'child_of', partner.parent_id.id),
                    orig[1]
                ]
            else:
                ret = [('partner_id', 'child_of', partner.id), orig[1]]
        return ret

class CustomerPortalInvoice(invoiceportal):

    def _get_invoices_domain(self):
        res = super()._get_invoices_domain()
        partner = request.env.user.partner_id

        if not request.env.user.portal_invoice_access:
            ret = [('partner_id', '=', -1)]
        if request.env.user.portal_invoice_access == 'own':
            ret = [('partner_id', '=', partner.id)]
        if request.env.user.portal_invoice_access == 'all':
            if partner.parent_id:
                ret = [
                    '|', ('partner_id', 'child_of', partner.id), ('partner_id', 'child_of', partner.parent_id.id)
                ]
            else:
                ret = [('partner_id', 'child_of', partner.id)]
        return ret

class CustomerPortalHelpdesk(helpdeskportal):
    def _get_tickets_domain(self):
        #
        partner = request.env.user.partner_id
        domain =  [('partner_id', '=', -1)]
        if request.env.user.portal_ticket_access == 'all':
            if partner.parent_id:
                domain = [
                    '|', ('partner_id', 'child_of', partner.id), ('partner_id', 'child_of', partner.parent_id.id)
                ]
            else:
                domain = [('partner_id', 'child_of', partner.id)]
        elif request.env.user.portal_ticket_access == 'own':
            domain = [
                '|', ('partner_child_id', '=', partner.id), ('partner_email', '=', partner.email)
            ]
        return domain

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'ticket_count' in counters:
            values['ticket_count'] = (
                request.env['helpdesk.ticket'].search_count(self._get_tickets_domain())
                if request.env['helpdesk.ticket'].check_access_rights('read', raise_exception=False)
                else 0
            )
        return values

    @http.route()
    def my_helpdesk_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None, groupby='none', search_in='content', **kw):
        _items_per_page = self._items_per_page
        self._items_per_page = 100000000

        response = super().my_helpdesk_tickets(page=page, date_begin=date_begin, date_end=date_end, sortby=sortby, filterby=filterby, search=search, groupby=groupby, search_in=search_in, **kw)
        if not response.is_qweb:
            # should not happed
            return response
 
        self._items_per_page = _items_per_page
 

        domain = self._get_tickets_domain()
        tickets_ids = []
        for group in response.qcontext.get("grouped_tickets"):
            tickets_ids.extend(group.ids)
        domain += [("id", "in", tickets_ids)]
        #print(domain)

        # some code duplication here, unfortunately
        tickets_count = len(request.env['helpdesk.ticket'].search(domain))
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby, 'filterby': filterby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        searchbar_sortings = response.qcontext.get("searchbar_sortings")
        sortby = response.qcontext.get("sortby")
        order = searchbar_sortings[sortby]['order']

        tickets = request.env['helpdesk.ticket'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]

        if groupby == 'stage':
            grouped_tickets = [request.env['helpdesk.ticket'].concat(*g) for k, g in groupbyelem(tickets, itemgetter('stage_id'))]
        else:
            grouped_tickets = [tickets]

        response.qcontext.update({
            'grouped_tickets': grouped_tickets,
            'pager': pager,
        })

        return response


class CustomerPortalSubscription(subscriptionportal):

    def _get_subscription_domain(self, partner):
        ret = super()._get_subscription_domain(partner)
        if not request.env.user.portal_subscription_access:
            ret = [('partner_id', '=', -1)]
        if request.env.user.portal_subscription_access == 'own':
            ret = [('partner_id', '=', partner.id)]
        if request.env.user.portal_subscription_access == 'all':
            if partner.parent_id:
                ret = [
                    '|', ('partner_id', 'child_of', partner.id), ('partner_id', 'child_of', partner.parent_id.id)
                ]
            else:
                ret = [('partner_id', 'child_of', partner.id)]
        return ret


class CustomerPortalInh(http.Controller):

    @http.route(['/my/tickets/create_ticket'], type='http', auth="user", website=True)
    def crea_ticket(self, redirect=None, **post):
        """
        Creazione del ticket lato website da pulsante custom Crea Ticket
        """
        ticket = request.env['helpdesk.ticket'].sudo().create({
            'name': post['name'],
            'description': post['description'],
            'partner_id': request.env.user.partner_id.id,

        })

        for data in request.httprequest.files.getlist('attachments'):

            file = base64.b64encode(data.read())
            if (data.filename and data.filename != ''):
                request.env['ir.attachment'].sudo().create({
                    'name': data.filename,
                    'type': 'binary',
                    'datas': file,
                   # 'datas_fname': data.filename,
                    'store_fname': data.filename,
                    'res_model': 'helpdesk.ticket',
                    'res_id': ticket.id,
                })
        return request.redirect('/my/tickets')

