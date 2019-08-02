import json

rds_snapshots = json.loads(file('rds-snapshots.json').read())

for region in rds_snapshots:
    
    for snapshot in rds_snapshots[region]:
        
        db_attrs = rds_snapshots[region][snapshot]['attributes']['DBSnapshotAttributes']
        
        if len(db_attrs) > 1:
            print snapshot
            continue

        if db_attrs[0]['AttributeName'] != 'restore':
            print snapshot
            continue

        if db_attrs[0]['AttributeValues'] != []:
            print snapshot
            continue
