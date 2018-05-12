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
	return columns, data
	
def get_columns():
	columns = [_("Campaign Name") + ":data:150", 
				_("Campaign Sub Category") + ":data:180",
				_("Lead Count") + ":Float:100",
				_("Quote Count") + ":Float:100", 
				_("Quote Amount") + ":Float:100",
				_("Order Count") + ":Float:100", 
				_("Order Amount") + ":Float:100"
			]
	return columns

def get_lead_data(filters):
	data_rows = []
	conditions=""
	if filters.from_date:
		conditions += " and date(creation) >= %(from_date)s"
	if filters.to_date:
		conditions += " and date(creation) <= %(to_date)s"
	if filters.campaign_name:
		conditions += " and campaign_name = %(campaign_name)s"
		

	if filters.get("campaign_sub_category"):
		show_campaign_sub_category = True
	else:
		show_campaign_sub_category = False


	data = frappe.db.sql("""select distinct campaign_name as "Campaign Name" from `tabLead` where ifnull(campaign_name, '') <> '' and 1 = 1 %s""" % (conditions,),filters, as_dict=1)
	dl=list(data)
	for row in dl:
		if show_campaign_sub_category:
			data_row = [row["Campaign Name"],"","","","","",""]
			data_rows.append(data_row)
			campaign_sub_category = frappe.db.sql("""select distinct ifnull(campaign_sub_category, 'blank') as "Campaign Sub Category" from `tabLead` where campaign_name = %s""",row["Campaign Name"], as_dict=1)
			cscl = list(campaign_sub_category)
			for csc_row in cscl:
				row["Lead Count"]= get_lead_count_by_sub_cat(row["Campaign Name"],csc_row["Campaign Sub Category"])
				row["Quote Count"]= get_lead_quotation_count_by_sub_cat(row["Campaign Name"],csc_row["Campaign Sub Category"])
				row["Quote Amount"] = get_lead_quote_amount_by_sub_cat(row["Campaign Name"],csc_row["Campaign Sub Category"])
				row["Order Count"] = get_quotation_ordered_count_by_sub_cat(row["Campaign Name"],csc_row["Campaign Sub Category"])
				row["Order Amount"] = get_order_amount_by_sub_cat(row["Campaign Name"],csc_row["Campaign Sub Category"])
				data_row = ["",csc_row["Campaign Sub Category"],row["Lead Count"],row["Quote Count"],row["Quote Amount"],row["Order Count"],row["Order Amount"]]
				data_rows.append(data_row)
		else:
			row["Lead Count"]= get_lead_count(row["Campaign Name"])
			row["Quote Count"]= get_lead_quotation_count(row["Campaign Name"])
			row["Quote Amount"] = get_lead_quote_amount(row["Campaign Name"])
			row["Order Count"] = get_quotation_ordered_count(row["Campaign Name"])
			row["Order Amount"] = get_order_amount(row["Campaign Name"])
			data_row = [row["Campaign Name"],"",row["Lead Count"],row["Quote Count"],row["Quote Amount"],row["Order Count"],row["Order Amount"]]
			data_rows.append(data_row)
	return data_rows

def get_lead_count(campaign):
	lead_count = frappe.db.sql("""select count(name) from `tabLead` 
										where campaign_name = %s""",campaign)
	return flt(lead_count[0][0]) if lead_count else 0

def get_lead_quotation_count(campaign):
	quotation_count = frappe.db.sql("""select count(name) from `tabQuotation` 
										where lead in (select name from `tabLead` where campaign_name = %s)""",campaign)
	return flt(quotation_count[0][0]) if quotation_count else 0

def get_lead_quote_amount(campaign):
	quotation_amount = frappe.db.sql("""select sum(base_total) from `tabQuotation` 
										where lead in (select name from `tabLead` where campaign_name = %s)""",campaign)
	return flt(quotation_amount[0][0]) if quotation_amount else 0

def get_quotation_ordered_count(campaign):
	quotation_ordered_count = frappe.db.sql("""select count(name) from `tabQuotation` 
												where status = 'Ordered' and lead in (select name from `tabLead` where campaign_name = %s)""",campaign)
	return flt(quotation_ordered_count[0][0]) if quotation_ordered_count else 0
	
def get_order_amount(campaign):
	ordered_count_amount = frappe.db.sql("""select sum(base_net_amount) from `tabSales Order Item` 
											where prevdoc_docname in (select name from `tabQuotation` 
											where status = 'Ordered' and lead in (select name from `tabLead` where campaign_name = %s))""",campaign)
	return flt(ordered_count_amount[0][0]) if ordered_count_amount else 0
#sub category
def get_lead_count_by_sub_cat(campaign, campaign_sub_category):
	if campaign_sub_category == "blank":
		lead_count = frappe.db.sql("""select count(name) from `tabLead` 
										where campaign_name = %s""",campaign)
	else:
		lead_count = frappe.db.sql("""select count(name) from `tabLead` 
										where campaign_name = %s and campaign_sub_category = %s""",(campaign, campaign_sub_category))
	return flt(lead_count[0][0]) if lead_count else 0

def get_lead_quotation_count_by_sub_cat(campaign, campaign_sub_category):
	if campaign_sub_category == "blank":
		quotation_count = frappe.db.sql("""select count(name) from `tabQuotation` 
										where lead in (select name from `tabLead` where campaign_name = %s and ifnull(campaign_sub_category, '') = '')""",campaign)
	else:
		quotation_count = frappe.db.sql("""select count(name) from `tabQuotation` 
										where lead in (select name from `tabLead` where campaign_name = %s and campaign_sub_category = %s)""",(campaign, campaign_sub_category))
	return flt(quotation_count[0][0]) if quotation_count else 0

def get_lead_quote_amount_by_sub_cat(campaign, campaign_sub_category):
	if campaign_sub_category == "blank":
		quotation_amount = frappe.db.sql("""select sum(base_total) from `tabQuotation` 
									where lead in (select name from `tabLead` where campaign_name = %s and ifnull(campaign_sub_category, '') = '')""",campaign)
	else:
		quotation_amount = frappe.db.sql("""select sum(base_total) from `tabQuotation` 
										where lead in (select name from `tabLead` where campaign_name = %s and campaign_sub_category = %s)""",(campaign, campaign_sub_category))
	return flt(quotation_amount[0][0]) if quotation_amount else 0

def get_quotation_ordered_count_by_sub_cat(campaign, campaign_sub_category):
	if campaign_sub_category == "blank":
		quotation_ordered_count = frappe.db.sql("""select count(name) from `tabQuotation` 
												where status = 'Ordered' and lead in (select name from `tabLead` where campaign_name = %s and ifnull(campaign_sub_category, '') = '')""",campaign)
	else:
		quotation_ordered_count = frappe.db.sql("""select count(name) from `tabQuotation` 
												where status = 'Ordered' and lead in (select name from `tabLead` where campaign_name = %s and campaign_sub_category = %s)""",(campaign, campaign_sub_category))
	return flt(quotation_ordered_count[0][0]) if quotation_ordered_count else 0
	
def get_order_amount_by_sub_cat(campaign, campaign_sub_category):
	if campaign_sub_category == "blank":
		ordered_count_amount = frappe.db.sql("""select sum(base_net_amount) from `tabSales Order Item` 
											where prevdoc_docname in (select name from `tabQuotation` 
											where status = 'Ordered' and lead in (select name from `tabLead` where campaign_name = %s and ifnull(campaign_sub_category, '') = ''))""",campaign)
	else:
		ordered_count_amount = frappe.db.sql("""select sum(base_net_amount) from `tabSales Order Item` 
											where prevdoc_docname in (select name from `tabQuotation` 
											where status = 'Ordered' and lead in (select name from `tabLead` where campaign_name = %s and campaign_sub_category = %s))""",(campaign, campaign_sub_category))
	return flt(ordered_count_amount[0][0]) if ordered_count_amount else 0