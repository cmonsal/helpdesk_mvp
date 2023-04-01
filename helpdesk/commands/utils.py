import click

import frappe
from frappe.commands import get_site, pass_context
from frappe.database.sequence import create_sequence
from frappe.installer import update_site_config


doctype_map = {
	"Agent Group Item": "HD Team Item",
	"Agent Group": "HD Team",
	"Agent": "HD Agent",
	"Article Item": "HD Article Item",
	"Article": "HD Article",
	"Canned Response": "HD Canned Response",
	"Category": "HD Article Category",
	"Desk Account Request": "HD Desk Account Request",
	"FD Customer": "HD Customer",
	"FD Preset Filter Item": "HD Preset Filter Item",
	"FD Preset Filter": "HD Preset Filter",
	"Frappe Desk Comment": "HD Ticket Comment",
	"Frappe Desk Notification": "HD Notification",
	"Holiday": "HD Holiday",
	"Organization Contact Item": "HD Organization Contact Item",
	"Organization": "HD Organization",
	"Pause SLA On Status": "HD Pause Service Level Agreement On Status",
	"Portal Signup Request": "HD Portal Signup Request",
	"SLA Fulfilled On Status": "HD Service Level Agreement Fulfilled On Status",
	"SLA": "HD Service Level Agreement",
	"Service Day": "HD Service Day",
	"Service Holiday List": "HD Service Holiday List",
	"Service Level Priority": "HD Service Level Priority",
	"Sub Category Item": "HD Article Sub Category Item",
	"Support Search Source": "HD Support Search Source",
	"Teams User": "HD Team Member",
	"Ticket Activity": "HD Ticket Activity",
	"Ticket Custom Field Item": "HD Ticket Custom Field Item",
	"Ticket Custom Field": "HD Ticket Custom Field",
	"Ticket Custom Fields Config": "HD Ticket Custom Field Config",
	"Ticket Priority": "HD Ticket Priority",
	"Ticket Template DocField": "HD Ticket Template DocField",
	"Ticket Template": "HD Ticket Template",
	"Ticket Type": "HD Ticket Type",
	"Ticket": "HD Ticket",
	"User Article Feedback": "HD Article Feedback",
}
doctypes_with_sequence = [
	"HD Preset Filter Item",
	"HD Team Item",
	"HD Team Member",
	"HD Ticket Custom Field Item",
]
old_settings, new_settings = "Frappe Desk Settings", "HD Settings"
single_table = "Singles"


@click.command("frappedesk-doctypes-str")
def frappedesk_doctypes_str():
	doctypes = doctype_map.keys()
	doctypes_str = ",".join(doctypes)
	print(doctypes_str)


@click.command("migrate-from-frappedesk")
@click.option(
	"--settings", help="Migrate settings. This will remove old settings", is_flag=True
)
@click.option(
	"--attachments",
	help="Migrate attachments. This will remove old attachments data",
	is_flag=True,
)
@click.option(
	"--remove-old-tables",
	help="Remove old tables. This will remove all old tables from database",
	is_flag=True,
)
@pass_context
def migrate_from_frappedesk(
	context,
	settings: bool = False,
	attachments: bool = False,
	remove_old_tables: bool = False,
):
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect(site=site)

	# Turn on maintenance mode. This will prevent any write to existing data
	update_site_config("maintenance_mode", 1)

	migrate_doctypes()
	generate_sequences()

	if settings:
		migrate_settings()

	if attachments:
		migrate_attachments()

	if remove_old_tables:
		remove_frappedesk_data()

	# Confirm database changes
	frappe.db.commit()

	# Turn off maintenance mode
	update_site_config("maintenance_mode", 0)


def migrate_doctypes():
	for doctype in doctype_map:
		old = doctype
		new = doctype_map[doctype]

		# skip if old table does not exist
		if not frappe.db.table_exists(old):
			continue

		# skip if new table does not exist
		if not frappe.db.table_exists(new):
			continue

		QBNewTable = frappe.qb.DocType(new)
		QBOldTable = frappe.qb.DocType(old)

		frappe.qb.into(QBNewTable).ignore().from_(QBOldTable).select(
			QBOldTable.star
		).run()

		print("Migrated", old, "to", new)


def migrate_settings():
	QBSingles = frappe.qb.DocType(single_table)

	frappe.qb.from_(QBSingles).delete().where(QBSingles.doctype == new_settings).run()
	frappe.qb.update(QBSingles).set(QBSingles.doctype, new_settings).where(
		QBSingles.doctype == old_settings
	).run()

	print("Migrated", old_settings, "to", new_settings)


def migrate_attachments():
	QBFile = frappe.qb.DocType("File")

	for doctype in doctype_map:
		old = doctype
		new = doctype_map[doctype]

		q = (
			frappe.qb.update(QBFile)
			.set(QBFile.attached_to_doctype, new)
			.where(QBFile.attached_to_doctype == old)
		)

		q.run()

		print("Migrated attachments of", old, "to", new, q)


def generate_sequences():
	for doctype in doctypes_with_sequence:
		sequence_name = frappe.scrub(doctype + "_id_seq")
		frappe.db.sql_ddl(f"DROP SEQUENCE IF EXISTS {sequence_name}")
		create_sequence(doctype)
		print("Created", sequence_name)


def remove_frappedesk_data():
	for doctype in doctype_map:
		QBTable = frappe.qb.DocType(doctype)
		frappe.qb.drop_table(QBTable).run()
		print("Dropped table for", doctype)

	QBSingles = frappe.qb.DocType(single_table)
	frappe.qb.from_(QBSingles).delete().where(QBSingles.doctype == old_settings).run()
	print("Dropped", old_settings)


commands = [frappedesk_doctypes_str, migrate_from_frappedesk]