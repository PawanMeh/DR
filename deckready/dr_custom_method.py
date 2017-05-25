from __future__ import unicode_literals
import frappe, json
import frappe.utils


from frappe import _

def validate_campaign(self,method):
	if not self.campaign_name:
		for je in self.accounts:
			if je.account == "Advertising and Promotions - AH":
				frappe.throw(_("Campaign Name is required for Advertising & Promotions Expense. If you do not know the Campaign Name, enter 'None' in the Campaign Name field."))
			else:
				self.campaign_name = "None"