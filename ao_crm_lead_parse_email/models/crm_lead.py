# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools import html2plaintext
import re


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def _prepare_message_new_custom_values(self, msg, custom_values=None):
        def parse_description(description):
            fields = ['email', 'first & last name']
            _dict = {}
            description = description.lower()
            for line in description.split('\n'):
                for field in fields:
                    if field in line:
                        split_line = line.split(':')
                        if len(split_line) > 1:
                            _dict[field] = line.split(':')[1].strip()
            return _dict
        subject = msg.get('subject', '')
        subject = subject.lower()
        keyphrase = self.env['ir.config_parameter'].sudo().get_param(
            'crm.lead.parse.email.keyphrase', default=False)
        if keyphrase and keyphrase in subject:
            if custom_values is None:
                custom_values = {}
            desc = html2plaintext(msg.get('body')) if msg.get('body') \
                else ''
            _dict = parse_description(desc)
            contact_name = False
            email_from = False
            if _dict.get('email'):
                email_from = re.sub(r'\s\[\d\]', '',
                                    _dict.get('email')).strip()
            if _dict.get('first & last name'):
                contact_name = _dict.get('first & last name').title()
            # Search for an existing partner:
            if email_from:
                partner_id = self.env['res.partner'].search([
                    ('email', '=', email_from)], limit=1)
            elif contact_name:
                partner_id = self.env['res.partner'].search([
                    ('name', '=', contact_name)], limit=1)
            else:
                partner_id = False
            vals = {
                'email_from': email_from,
                'contact_name': contact_name,
                'partner_name': contact_name,
                'partner_id': partner_id.id if partner_id else False,
            }
            msg['from'] = _dict.get('email')
            custom_values.update(vals)
        return custom_values, msg

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        rec_id = super(CrmLead, self).message_new(
            msg, custom_values=custom_values)
        model = self._name
        if model == 'crm.lead':
            custom_values = {}
            custom_values, msg = self._prepare_message_new_custom_values(
                msg, custom_values)
            if custom_values:
                rec_id.write(custom_values)
        return rec_id
