# -*- coding: utf-8 -*-
# Copyright 2015 Innoviu srl <http://www.innoviu.it>
# Copyright 2015 Agile Business Group <http://www.agilebg.com>
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
#                <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Fetchmail fetch missing",
    "summary": 'Fetchmail fetch missing messages',
    "version": "9.0.1.0.0",
    "category": "Discuss",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools/tree/9.0",
    "license": 'AGPL-3',
    "application": False,
    "installable": True,
    "depends": [
        'fetchmail',
        'mail',
    ],
    "data": [
        'views/fetchmail_views.xml',
        'views/mail_message_trash_views.xml',
        'security/ir.model.access.csv',
    ],
}
