#! /bin/sh
# Script to apply the two rendering setting files to the datasets of
# idr0052/experimentA


omero=/opt/omero/server/OMERO.server/bin/omero
project='idr0052-walther-condensinmap/experimentA'
experimentA_directory=/uod/idr/metadata/idr0052-walther-condensinmap/experimentA/

# Apply rendering settings to confocal datasets
$omero hql --ids-only --style csv -q "select d from ProjectDatasetLink l join l.parent as p join l.child as d where p.name='$project' and d.name like '%raw'" | cut -f2 -d "," | tail -n +2 > raw_datasets

cat raw_datasets | while read line
do
   $omero render set $line $experimentA_directory/confocal.yml
done


# Apply rendering settings to concentration datasets
$omero hql --ids-only --style csv -q "select d from ProjectDatasetLink l join l.parent as p join l.child as d where p.name='$project' and d.name like '%conc'" | cut -f2 -d "," | tail -n +2 > conc_datasets

cat conc_datasets | while read line
do
   $omero render set $line $experimentA_directory/concentration.yml
done

