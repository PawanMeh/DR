# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt,cstr
from erpnext.accounts.report.financial_statements import get_period_list

def execute(filters=None):
	columns, data = [], []
	columns=get_columns()
	data=get_lead_data(filters)
	chart=get_chart_data(data)
	return columns, data, None, chart
	
def get_columns():
	columns = [_("Campaign Name") + ":data:130", _("Lead Count") + ":Int:80",
				_("Opp Count") + ":Int:80",
				_("Quot Count") + ":Int:80", _("Order Count") + ":Int:100",
				_("Order Value") + ":Float:100",
				_("Expenses") + ":Float:100",
				_("Opp/Lead %") + ":Float:100",
				_("Opp/Lead %") + ":Float:100",
				_("Quot/Lead %") + ":Float:100",_("Order/Quot %") + ":Float:100"
	]
	return columns

def get_lead_data(filters):
	conditions=""
	if filters.from_date:
		conditions += " and date(creation) >= %(from_date)s"
	if filters.to_date:
		conditions += " and date(creation) <= %(to_date)s"
	data = frappe.db.sql("""select campaign_name as "Campaign Name", count(name) as "Lead Count" from `tabLead` where 1 = 1 %s group by campaign_name""" % (conditions,),filters, as_dict=1)
	dl=list(data)
	for row in dl:
		is_quot_count_zero = False
		row["Quot Count"]= get_lead_quotation_count(row["Campaign Name"])
		row["Opp Count"] = get_lead_opp_count(row["Campaign Name"])
		row["Order Count"] = get_quotation_ordered_count(row["Campaign Name"])
		row["Order Value"] = get_order_amount(row["Campaign Name"])
		row["Expenses"] = get_campaign_expenses(row["Campaign Name"],filters)
		row["Opp/Lead %"] = row["Opp Count"] / row["Lead Count"] * 100
		row["Quot/Lead %"] = row["Quot Count"] / row["Lead Count"] * 100
		if row["Quot Count"] == 0:
			row["Quot Count"] = 1
			is_quot_count_zero = True
		row["Order/Quot %"] = row["Order Count"] / row["Quot Count"] * 100
		if is_quot_count_zero ==  True:
			row["Quot Count"] = 0
	return dl
	
def get_lead_quotation_count(campaign):
	quotation_count = frappe.db.sql("""select count(name) from `tabQuotation` 
										where lead in (select name from `tabLead` where campaign_name = %s)""",campaign)
	return flt(quotation_count[0][0]) if quotation_count else 0
	
def get_lead_opp_count(campaign):
	opportunity_count = frappe.db.sql("""select count(name) from `tabOpportunity` 
										where lead in (select name from `tabLead` where campaign_name = %s)""",campaign)
	return flt(opportunity_count[0][0]) if opportunity_count else 0
	
def get_quotation_ordered_count(campaign):
	quotation_ordered_count = frappe.db.sql("""select count(name) from `tabQuotation` 
												where status = 'Ordered' and lead in (select name from `tabLead` where campaign_name = %s)""",campaign)
	return flt(quotation_ordered_count[0][0]) if quotation_ordered_count else 0
	
def get_order_amount(campaign):
	ordered_count_amount = frappe.db.sql("""select sum(base_net_amount) from `tabSales Order Item` 
											where prevdoc_docname in (select name from `tabQuotation` 
											where status = 'Ordered' and lead in (select name from `tabLead` where campaign_name = %s))""",campaign)
	return flt(ordered_count_amount[0][0]) if ordered_count_amount else 0
	
def get_campaign_expenses(campaign,filters):
	conditions=""
	if filters.from_date:
		conditions += " date(a.creation) >= %(from_date)s"
	if filters.to_date:
		conditions += " and date(a.creation) <= %(to_date)s"
	if campaign:
		filters["campaign"] = campaign
		conditions += " and a.campaign_name = %(campaign)s"
	campaign_expenses = frappe.db.sql("""select a.campaign_name, sum(a.total_debit) from `tabJournal Entry` a, 
										`tabJournal Entry Account` b where a.name = b.parent and b.account = 'Advertising and Promotions - AH' and %s """% (conditions,),filters)
	return flt(campaign_expenses[0][1]) if campaign_expenses else 0

def get_chart_data(data):
	x_intervals = ['x'] + [row["Campaign Name"] for row in data]
	columns = [x_intervals]
	order_data = [row["Order Value"] for row in data]
	lead_data = [row["Expenses"] for row in data]
	if order_data:
		columns.append(["Order Amount"]+ order_data)
	if lead_data:
		columns.append(["Expenses"]+ lead_data)
	chart = {
		"data": {
			'x': 'x',
			'columns': columns,
			'colors': {
				'Order Amount': '#5E64FF',
				'Lead Count': '#ff5858'
			}
		}
	}
	chart["chart_type"] = "bar"
	return chart