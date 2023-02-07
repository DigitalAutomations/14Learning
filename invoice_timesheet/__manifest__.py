#╔══════════════════════════════════════════════════════════════════════╗
#║                                                                      ║
#║                  ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                   ║
#║                  ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                   ║
#║                  ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                   ║
#║                  ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                   ║
#║                  ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                   ║
#║                  ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                   ║
#║                            ╔═╝║     ╔═╝║                             ║
#║                            ╚══╝     ╚══╝                             ║
#║                  SOFTWARE DEVELOPED AND SUPPORTED BY                 ║
#║                ALMIGHTY CONSULTING SOLUTIONS PVT. LTD.               ║
#║                      COPYRIGHT (C) 2016 - TODAY                      ║
#║                      https://www.almightycs.com                      ║
#║                                                                      ║
#╚══════════════════════════════════════════════════════════════════════╝
{
    "name": "Invoice Timesheet", 
    "version": "1.0.1",
    "category": "Accounting",
    "summary": "Invoice Timesheet Entry Customized for  ALIQUID S.R.L.",
    "description": """Invoice Timesheet Entry invoice timesheet entry
    invoice from timesheet timesheet invoicing invoice task task invoicing work invoicing invoice from worklog timesheet Invoicing
    """,
    "author": "Almighty Consulting Solutions Pvt. Ltd.",
    'support': 'info@almightycs.com',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    "depends": ["project","hr_timesheet","account"], 
    "data": [
        "security/ir.model.access.csv",
        "views/timesheet_view.xml",
        "views/res_config_view.xml",
        "wizard/timesheet_make_invoice_views.xml",
    ],
    'images': [
        'static/description/timesheet_cover.jpg',
    ],
    "application": True,
    "sequence": 1,
    "installable": True,
    'price': 70,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: