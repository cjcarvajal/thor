# spouse
spouse_query = """SELECT ?info 
WHERE
{{
  ?subject wdt:P26 ?object .
  ?object rdfs:label ?name .
  ?subject rdfs:label ?info .
  ?subject wdt:P27 wd:Q739
  FILTER (regex(?name, "{}","i"))
}} LIMIT 1"""

# political party filiations
political_party_query = """SELECT DISTINCT ?info
WHERE
{{
  ?subject rdfs:label ?name .
  ?subject wdt:P102 ?object .
  ?object rdfs:label ?info .
  ?subject wdt:P27 wd:Q739
  FILTER (regex(?name, "{}","i"))
  FILTER ( lang(?info) = "es" )
}}"""

# education
education_query = """SELECT DISTINCT ?info
WHERE
{{
  ?subject rdfs:label ?name .
  ?subject wdt:P69 ?object .
  ?object rdfs:label ?info .
  ?subject wdt:P27 wd:Q739 .
  FILTER (regex(?name, "{}","i"))
  FILTER ( lang(?info) = "es" )
}}"""

# place of birth
place_of_birth_query = """SELECT DISTINCT ?info
WHERE
{{
  ?subject rdfs:label ?name .
  ?subject wdt:P19 ?object .
  ?object rdfs:label ?info .
  ?subject wdt:P27 wd:Q739 .
  FILTER (regex(?name, "{}","i"))
  FILTER ( lang(?info) = "es" )
}} LIMIT 1"""

# positions held
positions_held_query = """SELECT DISTINCT ?info
WHERE
{{
  ?subject rdfs:label ?name .
  ?subject wdt:P39 ?object .
  ?object rdfs:label ?info .
  ?subject wdt:P27 wd:Q739 .
  FILTER (regex(?name, "{}","i"))
  FILTER ( lang(?info) = "es" )
}}"""
