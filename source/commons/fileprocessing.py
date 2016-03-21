
import csv
import sys

from account.models import Address

def readingfile():
    with open(sys.argv[1], 'locations') as f:
    try:
        reader = csv.DictReader(f)
        for row in reader:
            Address.objects.create(zipcode=row['zipcode'])
    except ValueError as e:
        raise "Something's wrong. Cannot read the file %s " % e