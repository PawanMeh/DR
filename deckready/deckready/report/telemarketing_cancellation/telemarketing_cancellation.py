# Copyright (c) 2013, hello@openetech.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt,cstr

def execute(filters=None):
	columns, data = [], []
	columns=get_columns()
	data=get_lead_data(filters)
	return columns, data, None
	
def get_columns():
	columns = [_("Lead Name") + ":data:130",_("Tele Agent") + ":data:80", _("Creation Date") + ":Date:100",
				_("Appt Date") + ":Date:100",
				_("Days to Appt") + ":Int:80",
				_("Subject") + ":Data:200",
				_("Description") + ":Data:300"
	]
	return columns

def get_lead_data(filters):
	conditions=""
	if filters.from_date:
		conditions += " and date(a.creation) >= %(from_date)s"
	if filters.to_date:
		conditions += " and date(a.creation) <= %(to_date)s"
	data = frappe.db.sql("""select a.lead_name as "Lead Name", a.telemarketing_agent as "Tele Agent", date(a.creation) as "Creation Date", date(b.starts_on) as "Appt Date",datediff(b.starts_on,b.creation) as "Days to Appt", b.subject as "Subject", b.description as "Description" from `tabLead` a, `tabEvent` b where a.name = b.ref_name and b.ref_type = "Lead" and a.telemarketing_agent IS NOT NULL %s""" % (conditions,),filters, as_dict=1)
	dl=list(data)
	return dl
	