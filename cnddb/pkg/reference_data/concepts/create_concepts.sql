
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