# Copyright 2021-2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    same_mobile_partner_id = fields.Many2one(
        "res.partner",
        compute="_compute_same_mobile_partner_id",
        string="Partner with same mobile",
        compute_sudo=True,
    )

    @api.depends("mobile", "company_id")
    def _compute_same_mobile_partner_id(self):
        for partner in self:
            partner.same_mobile_partner_id = partner._get_mobile_duplicates(limit=1)

    def action_view_mobile_duplicates(self):
        """Open every accessible contact matching this warning."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("View Duplicates"),
            "res_model": "res.partner",
            "view_mode": "tree,form",
            "domain": [("id", "in", self._get_mobile_duplicates().ids)],
            "context": {"active_test": False},
        }

    def _get_mobile_duplicates(self, limit=None):
        """Find contacts matching the mobile warning rules."""
        self.ensure_one()
        if not self.mobile:
            return self.env["res.partner"]
        # With phone_validation, the "mobile" field should be
        # clean in E.164 format, without any start/ending spaces
        # So we search on the 'mobile' field with '=' !
        domain = [("mobile", "=", self.mobile)]
        if self.company_id:
            domain += [
                "|",
                ("company_id", "=", False),
                ("company_id", "=", self.company_id.id),
            ]
        partner_id = self._origin.id
        if partner_id:
            domain.append(("id", "!=", partner_id))
        return self.with_context(active_test=False).search(domain, limit=limit)
