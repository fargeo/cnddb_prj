update observations a
set arches_species_id = '[{''resourceId'': '''|| b.ResourceID::text||''', ''ontologyProperty'': '''', ''resourceXresourceId'': '''', ''inverseOntologyProperty'': ''''}]'
from species b
where 1=1
and a.comname = b.cname;