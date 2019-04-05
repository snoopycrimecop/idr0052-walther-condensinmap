#!/usr/bin/env bash
# Script to apply the two rendering setting files to the experimentA and
# experimentB of the idr0052 study


omero=/opt/omero/server/OMERO.server/bin/omero
experimentA=idr0052-walther-condensinmap/experimentA
experimentB=idr0052-walther-condensinmap/experimentB
experimentA_directory="$(dirname "$0")/../experimentA/rendering_settings"
experimentB_directory="$(dirname "$0")/../experimentB/rendering_settings"

# Apply rendering settings to confocal datasets
$omero hql --ids-only --style csv -q "select d from ProjectDatasetLink l join l.parent as p join l.child as d where p.name='$experimentA' and d.name like '%raw'" | cut -f2 -d "," | tail -n +2 > raw_datasets

cat raw_datasets | while read dataset
do
    echo "Setting rendering for $dataset"
    $omero render set $dataset $experimentA_directory/raw.yml
done


# Apply rendering settings to concentration datasets
$omero hql --ids-only --style csv -q "select d from ProjectDatasetLink l join l.parent as p join l.child as d where p.name='$experimentA' and d.name like '%conc'" | cut -f2 -d "," | tail -n +2 > conc_datasets

cat conc_datasets | while read dataset
do
    echo "Setting rendering for $dataset"
    $omero render set $dataset $experimentA_directory/conc.yml
done


# Apply rendering settings to experimentB
$omero hql --ids-only --style csv -q "select d, d.name from ProjectDatasetLink l join l.parent as p join l.child as d where p.name='$experimentB'" | cut -f2,3 -d "," | tail -n +2 > experimentB_datasets

cat experimentB_datasets | while IFS=',' read dataset name
do
    echo "Setting rendering for $dataset"
    $omero render set $dataset "$experimentB_directory/$name.yml"
done
