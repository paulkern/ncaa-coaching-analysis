drop table if exists warehouse;
drop table if exists warehouse_schools;
drop table if exists wiki;

create table warehouse(name text, school text, position text, start_year int, end_year int,
									PRIMARY KEY (name, school, start_year) );

create table warehouse_schools(coach text, year int, school text, win int, loss int, tie int, pct real, points_for int, points_against int, delta int,
									PRIMARY KEY (coach, year) );

create table wiki(coach text, school text, position text, start_year int, end_year int,
							PRIMARY KEY (coach, school, start_year) );

.separator ","

.import ../finalData/warehouse_new.csv warehouse

.import ../finalData/warehouse_schools_new.csv warehouse_schools

.import ../finalData/wikipedia-refined.csv wiki