from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt,cstr
from collections import OrderedDict

@frappe.whitelist()
def get_crm_summary_data(from_date, to_date, campaign_name):
	def get_leads(from_date, to_date, campaign_name, based_on):
		based_on_field = frappe.scrub(based_on)
		conditions=""
		filters = {}
		if from_date:
			conditions += " and date(creation) >= %(from_date)s"
			filters = {"from_date":from_date}
		if to_date:
			conditions += " and date(creation) <= %(to_date)s"
			filters["to_date"] = to_date
		if campaign_name:
			conditions += " and campaign_name = %(campaign_name)s"
			filters["campaign_name"] = campaign_name
		lead_details = frappe.db.sql("""
			select {based_on_field} as fieldname,count(name) as count
			from `tabLead` 
			where {based_on_field} is not null and {based_on_field} != '' {conditions} group by {based_on_field}
		""".format(based_on_field=based_on_field, conditions=conditions), filters, as_dict=1)
		if lead_details:
			pass
		else:
			pass
			#frappe.msgprint(_("Disposition Data does not exist for the following filters."))
		data = []
		total = 0
		for lead in lead_details:
			total += lead.count

		total = float(total)

		for lead in lead_details:
			percent = round(lead["count"] / total,2) * 100
			row = {"status":lead.fieldname,"count":lead.count,"percent":percent}
			data.append(row)
		return data

	def get_quotation_order(from_date, to_date, campaign_name):
		conditions=""
		filters = {}
		if from_date:
			conditions += " date(creation) >= %(from_date)s"
			filters = {"from_date":from_date}
		if to_date:
			conditions += " and date(creation) <= %(to_date)s"
			filters["to_date"] = to_date
		if campaign_name:
			conditions += " and campaign_name = %(campaign_name)s"
			filters["campaign_name"] = campaign_name
		
		quotation = frappe.db.sql("""select "Quotations" as fieldname, count(name) as count, COALESCE(sum(base_total),0) as total
								from `tabQuotation`
								where lead in (select name from `tabLead` 
								where 1=1 and {conditions})""".format(conditions=conditions), filters, as_dict=1)

		orders = frappe.db.sql("""select "Orders" as fieldname, count(distinct parent) as count, COALESCE(sum(base_net_amount),0) as total 
							from `tabSales Order Item` 
							where prevdoc_docname in (select name from `tabQuotation` 
							where status = 'Ordered' and lead in (select name from `tabLead` 
							where 1 = 1 and {conditions}))""".format(conditions=conditions), filters, as_dict=1)
		if orders:
			pass
		else:
			pass
			#frappe.msgprint(_("Orders Data does not exist for the following filters."))
		data = []
		for quote in quotation:
			row = {"status":quote.fieldname,"count":quote.count,"$ amount":"{:,}".format(round(quote.total,2))}
			data.append(row)

		for order in orders:
			row = {"status":order.fieldname,"count":order.count,"$ amount":"{:,}".format(round(order.total,2))}
			data.append(row)
		return data

	def get_status(from_date, to_date, campaign_name):
		conditions=""
		filters = {}
		if from_date:
			conditions += " date(creation) >= %(from_date)s"
			filters = {"from_date":from_date}
		if to_date:
			conditions += " and date(creation) <= %(to_date)s"
			filters["to_date"] = to_date
		if campaign_name:
			conditions += " and campaign_name = %(campaign_name)s"
			filters["campaign_name"] = campaign_name
		
		opportunity = frappe.db.sql("""select "Opportunity" as fieldname, count(name) as count, 0 as percent
								from `tabOpportunity`
								where lead in (select name from `tabLead` 
								where 1=1 and {conditions})""".format(conditions=conditions), filters, as_dict=1)

		
		quotation = frappe.db.sql("""select "Quotations" as fieldname, count(name) as count, 0 as percent
								from `tabQuotation`
								where lead in (select name from `tabLead` 
								where 1=1 and {conditions})""".format(conditions=conditions), filters, as_dict=1)

		orders = frappe.db.sql("""select "Orders" as fieldname, count(distinct parent) as count, 0 as percent 
							from `tabSales Order Item` 
							where prevdoc_docname in (select name from `tabQuotation` 
							where status = 'Ordered' and lead in (select name from `tabLead` 
							where 1 = 1 and {conditions}))""".format(conditions=conditions), filters, as_dict=1)
		if orders:
			pass
		else:
			pass
			#frappe.msgprint(_("Orders Data does not exist for the following filters."))

		data = []

		for opp in opportunity:
			row = {"status":opp.fieldname,"count":opp.count,"percent":opp.percent}
			data.append(row)

		for quote in quotation:
			row = {"status":quote.fieldname,"count":quote.count,"percent":quote.percent}
			data.append(row)

		for order in orders:
			row = {"status":order.fieldname,"count":order.count,"percent":order.percent}
			data.append(row)

		total = 0
		for calc in data:
			total += calc["count"]
		total = float(total) 

		for row in data:
			if total > 0:
				if row["status"] == "Opportunity" :
					row["percent"] = round(row["count"] / total,2) * 100
				if row["status"] == "Quotations":
					row["percent"] = round(row["count"] / total,2) * 100
				if row["status"] == "Orders":
					row["percent"] = round(row["count"] / total,2) * 100
			else:
				row["percent"] = 0

		return data

	data = {
		"leads":get_leads(from_date, to_date, campaign_name, "disposition"),
		"orders":get_quotation_order(from_date, to_date, campaign_name),
		"status":get_status(from_date, to_date, campaign_name)
	}

	try:
		html = ""
		html = frappe.render_template("deckready/deckready/page/crm_summary/crm_summary.html", {"data": data})
	except Exception as e:
		html = ""
		#frappe.throw("Could not create data output. Reason: {0}".format(e))
		frappe.msgprint("Could not find data for the criteria entered")

	return html