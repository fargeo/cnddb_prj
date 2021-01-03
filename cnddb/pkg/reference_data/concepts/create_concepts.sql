insert into concepts
select
uuid_generate_v4(),
id||'species',
'Concept'
from species;

insert into values
select
uuid_generate_v4(),
prefname,
b.conceptid,
'en',
'prefLabel'
from species a, concepts b
where a.id||'species' = b.legacyoid;

insert into values
select
uuid_generate_v4(),
cname,
b.conceptid,
'en',
'common_name'
from species a, concepts b
where a.id||'species' = b.legacyoid;

insert into values
select
uuid_generate_v4(),
sname,
b.conceptid,
'en',
'scientific_name'
from species a, concepts b
where a.id||'species' = b.legacyoid;

insert into relations
select 
uuid_generate_v4(),
'04b638af-ed98-4259-b05c-72d69f82f438',
conceptid,
'narrower'
from concepts where legacyoid like '%species';

---

insert into concepts
select
uuid_generate_v4(),
code||'threats',
'Concept'
from threats;

insert into values
select
uuid_generate_v4(),
threat_name,
b.conceptid,
'en',
'prefLabel'
from threats a, concepts b
where a.code||'threats' = b.legacyoid;

insert into values
select
uuid_generate_v4(),
"definition",
b.conceptid,
'en',
'scopeNote'
from threats a, concepts b
where a.code||'threats' = b.legacyoid;

insert into relations
select 
uuid_generate_v4(),
'1e86c786-6ef2-4cdb-a68e-dd5576ebdc8a',
conceptid,
'narrower'
from concepts where legacyoid like '%threats';

-----
insert into concepts
select
uuid_generate_v4(),
id||'counties',
'Concept'
from ca_counties;

insert into values
select
uuid_generate_v4(),
name,
b.conceptid,
'en',
'prefLabel'
from ca_counties a, concepts b
where a.id||'counties' = b.legacyoid;

insert into relations
select 
uuid_generate_v4(),
'03aeada3-b097-4047-a5ff-bdd7cd7f20fc',
conceptid,
'narrower'
from concepts where legacyoid like '%counties';

---

insert into concepts
select
uuid_generate_v4(),
id||'quads',
'Concept'
from quad24;

insert into values
select
uuid_generate_v4(),
quad24name,
b.conceptid,
'en',
'prefLabel'
from quad24 a, concepts b
where a.id||'quads' = b.legacyoid;

insert into values
select
uuid_generate_v4(),
q24code,
b.conceptid,
'en',
'altLabel'
from quad24 a, concepts b
where a.id||'quads' = b.legacyoid;

insert into relations
select 
uuid_generate_v4(),
'127b3f81-e856-4674-906f-dc882048845c',
conceptid,
'narrower'
from concepts where legacyoid like '%quads';

---

insert into concepts
select
uuid_generate_v4(),
id||'orgs',
'Concept'
from organizations;

insert into values
select
uuid_generate_v4(),
affiliationname,
b.conceptid,
'en',
'prefLabel'
from organizations a, concepts b
where a.id||'orgs' = b.legacyoid;


insert into relations
select 
uuid_generate_v4(),
'3dd5e7de-c6db-4935-8eba-295680ef2f1d',
conceptid,
'narrower'
from concepts where legacyoid like '%orgs';