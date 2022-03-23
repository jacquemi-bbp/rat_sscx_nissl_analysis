def entry = getProjectEntry()
def entryMetadata = entry.getMetadataMap()
 
def flag = entryMetadata['Analyze']
println "$flag"

if (entryMetadata['Analyze'] == 'True') {
	println ("ANALYSE == true")
}
