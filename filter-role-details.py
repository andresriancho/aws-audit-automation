import json
import pprint

data = json.loads(file('role-details.json').read())

for role in data:
	role_data = data[role]

	if 'AssumeRolePolicyDocument' not in role_data:
		continue

	statements = role_data['AssumeRolePolicyDocument']['Statement']

	if len(statements) > 1:
		print role
		pprint.pprint(statements)
		continue

	# "Action": "sts:AssumeRoleWithSAML",
	first_statement = statements[0]

	if first_statement['Action'] == 'sts:AssumeRoleWithSAML':
		continue

	should_continue = True

	principals = first_statement['Principal']
	if 'Service' not in principals:
		print role
		pprint.pprint(statements)
		continue

	services = first_statement['Principal']['Service']
	if isinstance(services, basestring):
		services = [services]

	for service in services:
		if not service.endswith('.amazonaws.com'):
			should_continue = False
			break

	if should_continue:
		continue

	print role
	pprint.pprint(statements)