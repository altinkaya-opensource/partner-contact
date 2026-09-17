# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    same_email_partner_id = fields.Many2one(
        "res.partner",
        compute="_compute_same_email_partner_id",
        string="Partner with same e-mail",
        compute_sudo=True,
    )

    @api.depends("email", "company_id")
    def _compute_same_email_partner_id(self):
        for partner in self:
            partner.same_email_partner_id = partner._get_email_duplicates()[:1]

    def action_view_email_duplicates(self):
        """Open every accessible contact matching this warning."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("View Duplicates"),
            "res_model": "res.partner",
            "view_mode": "tree,form",
            "domain": [("id", "in", self._get_email_duplicates().ids)],
            "context": {"active_test": False},
        }

    def _get_email_duplicates(self):
        """Find all contacts matching the email warning rules."""
        self.ensure_one()
        partner_email = (self.email or "").strip().lower()
        if not partner_email:
            return self.env["res.partner"]
        domain = [("email", "=ilike", f"%{partner_email}%")]
        if self.company_id:
            domain += [
                "|",
                ("company_id", "=", False),
                ("company_id", "=", self.company_id.id),
            ]
        partner_id = self._origin.id
        if partner_id:
            domain += [
                ("id", "!=", partner_id),
                "!",
                ("id", "child_of", partner_id),
                "!",
                ("id", "parent_of", partner_id),
            ]
        return (
            self.with_context(active_test=False)
            .search(domain)
            .filtered(
                lambda partner: (partner.email or "").strip().lower() == partner_email
            )
        )
