# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
from frappe.utils.jinja import get_jenv
import frappe


def resolve_class(classes):
	if classes is None:
		return ""

	if isinstance(classes, frappe.string_types):
		return classes

	if isinstance(classes, (list, tuple)):
		return " ".join([resolve_class(c) for c in classes]).strip()

	if isinstance(classes, dict):
		return " ".join([classname for classname in classes if classes[classname]]).strip()

	return classes


def inspect(var, render=True):
	context = {"var": var}
	if render:
		html = "<pre>{{ var | pprint | e }}</pre>"
	else:
		return ""
	return get_jenv().from_string(html).render(context)


def web_block(template, values=None, **kwargs):
	options = {"template": template, "values": values}
	options.update(kwargs)
	return web_blocks([options])


def web_blocks(blocks):
	from frappe import throw, _dict
	from frappe.website.doctype.web_page.web_page import get_web_blocks_html

	web_blocks = []
	for block in blocks:
		if not block.get("template"):
			throw("Web Template is not specified")

		doc = _dict(
			{
				"doctype": "Web Page Block",
				"web_template": block["template"],
				"web_template_values": block.get("values", {}),
				"add_top_padding": 1,
				"add_bottom_padding": 1,
				"add_container": 1,
				"hide_block": 0,
				"css_class": "",
			}
		)
		doc.update(block)
		web_blocks.append(doc)

	out = get_web_blocks_html(web_blocks)

	html = out.html
	for script in out.scripts:
		html += "<script>{}</script>".format(script)

	return html

def script(path):
	path = assets_url(path)
	if '/public/' in path:
		path = path.replace('/public/', '/dist/')
	return f'<script type="text/javascript" src="{path}"></script>'

def style(path):
	path = assets_url(path)
	if '/public/' in path:
		path = path.replace('/public/', '/dist/')
	if path.endswith(('.scss', '.sass', '.less', '.styl')):
		path = path.rsplit('.', 1)[0] + '.css'
	return f'<link type="text/css" rel="stylesheet" href="{path}">'

def assets_url(path):
	if not path.startswith('/'):
		path = '/' + path
	if not path.startswith('/assets'):
		path = '/assets' + path
	return path
