#!/opt/stack/bin/python
import sys
from snack import *
import stack.wizard

def render_timezone(screen):

	#get list of timezones
	cities = []
	for line in open('/opt/stack/bin/timezones.txt'):
		line = line.replace('\n', '')
		line = filter(None, line.split('\t'))
		cities.append((line[0], line[0]))

	#render window to choose a timezone
	result = ListboxChoiceWindow(screen, "Stacki Installation", \
		"Cluster Timezone", cities, width=40, buttons=('Continue', 'Cancel'), \
		scroll=1, height=5)
	return result

def render_network(screen, data):

	#get list of ethernet devices from plugin
	devices = data.getDevices()

	#create form
	g = GridForm(screen, "Stacki Installation", 2, 10)

	#create labels
	title = Textbox(20, 2, "Network", scroll=0, wrap = 0)
	tb0 = Textbox(13, 1, "Hostname:", scroll=0, wrap=0)
	space = Textbox(13, 1, "", scroll=0, wrap=0)
	dev = Textbox(13, 2, "Devices:", scroll=0, wrap=0)
	space2 = Textbox(13, 1, "", scroll=0, wrap=0)
	tb1 = Textbox(13, 1, "IP:", scroll=0, wrap=0)
	tb2 = Textbox(13, 1, "Netmask:", scroll=0, wrap=0)
	tb3 = Textbox(13, 1, "Gateway:", scroll=0, wrap=0)
	tb4 = Textbox(13, 2, "DNS Servers:", scroll=0, wrap=0)

	#create list to choose device
	lb = Listbox(2, scroll=0, returnExit=0, width=21, showCursor=0)
	for d in devices:
		lb.append(d, d)

	#create input fields
	e0 = Entry(21, text=data.get('Kickstart_PrivateHostname'), scroll=1, \
		returnExit=0)
	e1 = Entry(21, text=data.get('Kickstart_PrivateAddress'), scroll=0, \
		returnExit=0)
	e2 = Entry(21, text=data.get('Kickstart_PrivateNetmask'), scroll=0, \
		returnExit=0)
	e3 = Entry(21, text=data.get('Kickstart_PrivateGateway'), scroll=0, \
		returnExit=0)
	e4 = Entry(21, text=data.get('Kickstart_PrivateDNSServers'), scroll=0, \
		returnExit=0)

	#add elements to form
	g.add(title, 0, 0)
	g.add(tb0, 0, 1)
	g.add(space, 0, 2)
	g.add(dev, 0, 3)
	g.add(space2, 0, 4)
	g.add(tb1, 0, 5)
	g.add(tb2, 0, 6)
	g.add(tb3, 0, 7)
	g.add(tb4, 0, 8)

	g.add(e0, 1, 1)
	g.add(lb, 1, 3)
	g.add(e1, 1, 5)
	g.add(e2, 1, 6)
	g.add(e3, 1, 7)
	g.add(e4, 1, 8)

	#create buttons
	back_button = Button("Back")
	continue_button = Button("Continue")

	#add buttons to form
	g.add(continue_button, 0, 9)
	g.add(back_button, 1, 9)

	#get the pressed button value
	form_result = g.runOnce()
	if form_result == back_button:
		btn_value = "back"
	else:
		btn_value = "continue"

	#return pressed button value and input values
	result = (btn_value, (e0.value(), lb.current(), e1.value(), e2.value(), \
		e3.value(), e4.value()))
	return result

def render_password(screen):

	g = GridForm(screen, "Stacki Installation", 2, 4)

	#create labels
	pass1 = Textbox(18, 1, "Password:", scroll=0, wrap=0)
	pass2 = Textbox(18, 1, "Confirm Password:", scroll=0, wrap=0)
	space = Textbox(18, 1, "", scroll=0, wrap=0)

	#create input fields
	e1 = Entry(21, text="", password=1, scroll=0, returnExit=0)
	e2 = Entry(21, text="", password=1, scroll=0, returnExit=0)

	#add elements to form
	g.add(pass1, 0, 0)
	g.add(pass2, 0, 1)
	g.add(e1, 1, 0)
	g.add(e2, 1, 1)
	g.add(space, 0, 2)

	#create buttons
	back_button = Button("Back")
	continue_button = Button("Continue")

	#add buttons to form
	g.add(continue_button, 0, 3)
	g.add(back_button, 1, 3)

	#get the pressed button value
	form_result = g.runOnce()
	if form_result == back_button:
		btn_value = "back"
	else:
		btn_value = "continue"

	#return pressed button value and input values
	result = (btn_value, (e1.value(), e2.value()))
	return result

def render_partition(screen):

	#partition choices
	choices = [('Automated', 'Automated'), ('Manual', 'Manual')]

	#render window to choose partition type
	result = ListboxChoiceWindow(screen, "Stacki Installation",
		"Partition Settings", choices, buttons=('Continue', 'Back'), \
		width=40, scroll = 0, height=2)
	return result

def render_pallets(screen, data):

	#get list of pallets
	packages = data.getDVDPallets()

	#if no pallets, display this screen
	if len(packages) == 0:
		result = ButtonChoiceWindow(screen, "Error", \
			"Please insert or mount a pallets DVD",
			buttons=['Ok', 'Cancel'])
		result = (result, "none")
	else:
		#create form
		g = GridForm(screen, "Stacki Installation", 1, 3)

		#create label
		tb = Textbox(40, 2, "Pallets to Install", scroll=0, wrap = 0)

		#create checkbox tree
		ct = CheckboxTree(height = 5, scroll = 1)
		ct.append("DVD Drive", item=None, selected=1)

		#insert pallet info into checkbox tree
		for p in packages:
			line = p[0] + ' ' + p[1] + ' ' + p[2] + ' ' + p[3]
			ct.addItem(line, (0, snackArgs['append']), selected=1)

		#create buttons
		bb = ButtonBar(screen, (("Continue", "continue"), ("Back", "back")))

		#add elements to form
		g.add(tb, 0, 0)
		g.add(ct, 0, 1)
		g.add(bb, 0, 2, growx = 1)

		#return pressed button value and selected pallets
		form_result = g.runOnce()
		result = (bb.buttonPressed(form_result), ct.getSelection())

	return result

def render_summary(screen, data):

	#get summary from the plugin
	summaryStr = data.generateSummary()

	#create form
	g = GridForm(screen, "Stacki Installation", 1, 4)

	#create elements
	tb = Textbox(52, 2, "Summary", scroll=0, wrap = 0)
	tb2 = Textbox(51, 16, summaryStr, scroll=1, wrap = 0)
	tb3 = Textbox(52, 1, "", scroll=0, wrap = 0)
	bb = ButtonBar(screen, (("Finish", "finish"), ("Back", "back")))

	#add elements to form
	g.add(tb, 0, 0)
	g.add(tb2, 0, 1)
	g.add(tb3, 0, 2)
	g.add(bb, 0, 3, growx = 1)

	#return the pressed button value
	form_result = g.runOnce()
	result = (bb.buttonPressed(form_result), "summary")
	return result

def process_data(page, btn_value, result):

	# Determine which button was pressed to move back or continue. If continue,
	# use boss config plugin to validate and/or calculate further attributes.
	# Update the page index accordingly.

	#check button pressed and process accordingly
	if btn_value == 'back':
		if page == 5 and no_partition:
			page = page - 2
		else:
			page = page - 1
	elif btn_value == 'cancel':
		page = 10
	elif btn_value == 'ok':
		page = page
	else:
		#timezone
		if page == 1:
			validated, message, title = \
				data.validateTimezone(str(result))
		#network
		elif page == 2:
			fqhn, eth, ip, subnet, gateway, dns = result

			#check the FQDN for appliance names
			validated, message, title = \
				data.validateDomain(fqhn)
			if validated:
				#check for valid network config
				validated, message, title = \
					data.validateNetwork((fqhn, eth, ip, subnet, \
						gateway, dns), config_net)
		#password
		elif page == 3:
			pw1, pw2 = result
			validated, message, title = data.validatePassword(pw1, pw2)
		#partition
		elif page == 4:
			validated, message, title = data.validatePartition(str(result))
		#pallets
		elif page == 5:
			#convert list of pallet strings to dict
			selected_pallets = []
			for p in result:
				a = p.split(" ")
				selected_pallets.append(
					{'name': a[0], 'version': a[1], 'release': a[2], 'id': a[3]})

			#takes two arguments of dvd-pallets and network-pallets
			validated, message, title = \
				data.validatePallets(selected_pallets, [])
		#summary
		elif page == 6:
			validated, message, title = data.writefiles()

		#check if error message needs display or proceed
		if not validated:
			ButtonChoiceWindow(screen, title, message,
				buttons=['Ok'])
		else:
			if page == 3 and no_partition:
				page += 2
			else:
				page += 1
	return page

def render(screen, page, data):

	# Determine page index and render the page.
	# Validate and process data after button pressed.

	if page == 1:
		btn_value, values = render_timezone(screen)
	elif page == 2:
		btn_value, values = render_network(screen, data)
	elif page == 3:
		btn_value, values = render_password(screen)
	elif page == 4:
		btn_value, values = render_partition(screen)
	elif page == 5:
		btn_value, values = render_pallets(screen, data)
	elif page == 6:
		btn_value, values = render_summary(screen, data)

	return process_data(page, btn_value, values)

#begin
config_net = True
no_partition = False
screen = SnackScreen()
page = 1
data = stack.wizard.Data()

#set network configuration flag
for s in sys.argv:
	if s == '--no-net-reconfig':
		config_net = False
	if s == '--no-partition':
		no_partition = True

#loop until the last page
while page < 7:
	page = render(screen, page, data)

#close screen
screen.finish()
