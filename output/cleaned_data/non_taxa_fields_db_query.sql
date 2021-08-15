select
name,
data_source_notes as csv,
raw_data ->> '% Planktic Foraminifera within whole sample' as "% Planktic Foraminifera within whole sample",
raw_data ->> 'Abundance' as "Abundance",
raw_data ->> 'Additional zone name' as "Additional zone name",
raw_data ->> 'Additional zone name (short)' as "Additional zone name (short)",
raw_data ->> 'Age' as "Age",
raw_data ->> 'Aspect comment (etching)' as "Aspect comment (etching)",
raw_data ->> 'Aspect comment (etching),Comment (general)' as "Aspect comment (etching),Comment (general)",
raw_data ->> 'BF Group abundance' as "BF Group abundance",
raw_data ->> 'BF Preservation' as "BF Preservation",
raw_data ->> 'BF comment' as "BF comment",
raw_data ->> 'BF preservation' as "BF preservation",
raw_data ->> 'COMMENTS' as "COMMENTS",
raw_data ->> 'Chrysophyte cyst group abundance' as "Chrysophyte cyst group abundance",
raw_data ->> 'Comment' as "Comment",
raw_data ->> 'Comment (general)' as "Comment (general)",
raw_data ->> 'Comments' as "Comments",
raw_data ->> 'Datum age average [Ma]' as "Datum age average [Ma]",
raw_data ->> 'Datum age maximum [Ma]' as "Datum age maximum [Ma]",
raw_data ->> 'Datum age minimum [Ma]' as "Datum age minimum [Ma]",
raw_data ->> 'Datum author year' as "Datum author year",
raw_data ->> 'Datum comment' as "Datum comment",
raw_data ->> 'Datum group' as "Datum group",
raw_data ->> 'Datum group code' as "Datum group code",
raw_data ->> 'Datum name' as "Datum name",
raw_data ->> 'Datum name generic' as "Datum name generic",
raw_data ->> 'Datum occurrence' as "Datum occurrence",
raw_data ->> 'Datum region' as "Datum region",
raw_data ->> 'Datum status' as "Datum status",
raw_data ->> 'Datum type' as "Datum type",
raw_data ->> 'Datum validation comment' as "Datum validation comment",
raw_data ->> 'Diatom abundance' as "Diatom abundance",
raw_data ->> 'Diatom preservation - pyritization2' as "Diatom preservation - pyritization2",
raw_data ->> 'Diatom preservation dissolution' as "Diatom preservation dissolution",
raw_data ->> 'Diatom preservation fragmentation' as "Diatom preservation fragmentation",
raw_data ->> 'Diatoms and siliceous plankton comment' as "Diatoms and siliceous plankton comment",
raw_data ->> 'Diatoms group abundance' as "Diatoms group abundance",
raw_data ->> 'Ebridian group abundance' as "Ebridian group abundance",
raw_data ->> 'File Data' as "File Data",
raw_data ->> 'Foram abundance' as "Foram abundance",
raw_data ->> 'Fragmentation' as "Fragmentation",
raw_data ->> 'Fragmentation rank [auto-pop]' as "Fragmentation rank [auto-pop]",
raw_data ->> 'General comment' as "General comment",
raw_data ->> 'Genus/species (upper zone)' as "Genus/species (upper zone)",
raw_data ->> 'Genus/species lower zone)' as "Genus/species lower zone)",
raw_data ->> 'Group Abundance' as "Group Abundance",
raw_data ->> 'Group abundance' as "Group abundance",
raw_data ->> 'Group abundance (%)' as "Group abundance (%)",
raw_data ->> 'Group preservation' as "Group preservation",
raw_data ->> 'Large Benthic Forams [%]' as "Large Benthic Forams [%]",
raw_data ->> 'Lower boundary age av. [Ma]' as "Lower boundary age av. [Ma]",
raw_data ->> 'Lower boundary age max [Ma]' as "Lower boundary age max [Ma]",
raw_data ->> 'Lower boundary age min [Ma]' as "Lower boundary age min [Ma]",
raw_data ->> 'Mixing' as "Mixing",
raw_data ->> 'Nannofossil abundance' as "Nannofossil abundance",
raw_data ->> 'Nannofossil comment' as "Nannofossil comment",
raw_data ->> 'No. specimens/tray' as "No. specimens/tray",
raw_data ->> 'PALEO WATER DEPTH (IS=inner shelf, MS=middle shelf, OS=outer shelf)' as "PALEO WATER DEPTH (IS=inner shelf, MS=middle shelf, OS=outer shelf)",
raw_data ->> 'PF Group Abundance' as "PF Group Abundance",
raw_data ->> 'PF Preservation' as "PF Preservation",
raw_data ->> 'PF Zone' as "PF Zone",
raw_data ->> 'PF group abundance' as "PF group abundance",
raw_data ->> 'PF preservation' as "PF preservation",
raw_data ->> 'Percentage of benthic forams in total foram assemblage [%]' as "Percentage of benthic forams in total foram assemblage [%]",
raw_data ->> 'Percentage of non-calcareous agglutinated forams in total foram assemblage [%]' as "Percentage of non-calcareous agglutinated forams in total foram assemblage [%]",
raw_data ->> 'Percentage of planktic forams in total foram assemblage [%]' as "Percentage of planktic forams in total foram assemblage [%]",
raw_data ->> 'Piece' as "Piece",
raw_data ->> 'Planktonic Benthic ratio (P:B)' as "Planktonic Benthic ratio (P:B)",
raw_data ->> 'Pleurostomellids comment' as "Pleurostomellids comment",
raw_data ->> 'Preservation' as "Preservation",
raw_data ->> 'Pteropod group abundance' as "Pteropod group abundance",
raw_data ->> 'Reworking comment (1= <1%, 2= light 1-10%, 3= >10%)' as "Reworking comment (1= <1%, 2= light 1-10%, 3= >10%)",
raw_data ->> 'Reworking comment (1= <1%, 2=light 1-10%, 3= >10%)' as "Reworking comment (1= <1%, 2=light 1-10%, 3= >10%)",
raw_data ->> 'Sample comment' as "Sample comment",
raw_data ->> 'Sample preparation comment' as "Sample preparation comment",
raw_data ->> 'Ship File Links' as "Ship File Links",
raw_data ->> 'Shore File Links' as "Shore File Links",
raw_data ->> 'Silicoflagellates group abundance' as "Silicoflagellates group abundance",
raw_data ->> 'Sillicoflagellate abundance' as "Sillicoflagellate abundance",
raw_data ->> 'Temperature Range' as "Temperature Range",
raw_data ->> 'Total in situ dinocysts' as "Total in situ dinocysts",
raw_data ->> 'Type (lower zone)' as "Type (lower zone)",
raw_data ->> 'Type (upper zone)' as "Type (upper zone)",
raw_data ->> 'Upper boundary age av. [Ma]' as "Upper boundary age av. [Ma]",
raw_data ->> 'Upper boundary age max [Ma]' as "Upper boundary age max [Ma]",
raw_data ->> 'Upper boundary age min [Ma]' as "Upper boundary age min [Ma]",
raw_data ->> 'XBroken' as "XBroken",
raw_data ->> 'XCorroded' as "XCorroded",
raw_data ->> 'XCrumpled' as "XCrumpled",
raw_data ->> 'Zone' as "Zone",
raw_data ->> 'Zone author (year)' as "Zone author (year)",
raw_data ->> 'Zone comment' as "Zone comment",
raw_data ->> 'Zone group' as "Zone group",
raw_data ->> 'Zone group,Type (upper zone)' as "Zone group,Type (upper zone)",
raw_data ->> 'Zone name' as "Zone name",
raw_data ->> 'Zone name (short)' as "Zone name (short)",
raw_data ->> 'Zone name [short]' as "Zone name [short]",
raw_data ->> 'Zone status' as "Zone status",
raw_data ->> 'comments' as "comments",
raw_data ->> 'constituent' as "constituent",
raw_data ->> 'count' as "count",
raw_data ->> 'count_type' as "count_type",
raw_data ->> 'dupes and comments' as "dupes and comments",
raw_data ->> 'pc_abundance_name_mode' as "pc_abundance_name_mode",
raw_data ->> 'pc_fossil_group' as "pc_fossil_group",
raw_data ->> 'pc_fossil_name' as "pc_fossil_name",
raw_data ->> 'pc_preservation_name_average' as "pc_preservation_name_average",
raw_data ->> 'physical_constituent_name' as "physical_constituent_name"
from samples
where data_source_type = 'micropal csv'
;