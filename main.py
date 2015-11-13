import sys
import csv

inFilePath = '/data/in/tables/source.csv'
outFilePath = '/data/out/tables/destination.csv'
csvDelimiter = ','
csvQuoteChar = '"'

with open(inFilePath, "rt") as inFile, open(outFilePath, 'wt') as outFile:
	reader = csv.reader(inFile, delimiter = csvDelimiter, quotechar = csvQuoteChar)
	writer = csv.writer(outFile, delimiter = csvDelimiter, quotechar = csvQuoteChar, quoting = csv.QUOTE_MINIMAL)
	for row in reader:
		writer.writerow(['batman', row[0], row[1]])
