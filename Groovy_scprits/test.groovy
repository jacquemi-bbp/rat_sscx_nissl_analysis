def entry = getProjectEntry()
def entryMetadata = entry.getMetadataMap()
 
def flag = entryMetadata['Analyze']
println " FLAG: $flag"

if (entryMetadata['Analyze'] == 'True') {
	println ("ANALYSE == true")
}
else {
        println ("ANALYSE == false")
}
