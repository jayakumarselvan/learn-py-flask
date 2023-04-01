# Query Reference

Below query used to retrieve the list with the average prices for each day on a route between port codes origin and destination
```sql
select
  to_char(gs_tbl.gs_day, 'YYYY-MM-DD') as "day",
  result_tbl.average_price
from
  (
    select generate_series.gs_day::date 
    from generate_series('2016-01-01'::date, '2016-01-10'::date, interval '1 day') as generate_series(gs_day)
  ) as gs_tbl

  left join (
    select 
      pr."day",
      (
        case 
          when COUNT(1) >=3 then CAST(ROUND(AVG(pr.price))AS INTEGER)
          else null
          end
      ) as average_price
    from 
      prices as pr
      left join ports as p_oc on p_oc.code = pr.orig_code
      left join ports as p_dc on p_dc.code = pr.dest_code
      left join regions as r_p_oc on r_p_oc.slug = p_oc.parent_slug
      left join regions as r_p_dc on r_p_dc.slug = p_dc.parent_slug
    where
      ( pr.day between '2016-01-01' and '2016-01-10' )
      and ( pr.orig_code ='CNSGH' or p_oc.parent_slug = 'CNSGH' or r_p_oc.parent_slug = 'CNSGH' )
      and ( pr.dest_code ='north_europe_main' or p_dc.parent_slug = 'north_europe_main' or r_p_dc.parent_slug = 'north_europe_main' )
    group by pr.day
  ) as result_tbl on result_tbl.day = gs_tbl.gs_day
order by gs_tbl.gs_day
-- limit 2 offset 4
```

We can create **View** if the query is required for multiple places or multiple module or multiple apps

Create a view
```sql
create view v_price_port_region as
select 
	pr.*,
	p_oc.code as p_oc_code, p_oc."name" as p_oc_name, p_oc.parent_slug as p_oc_parent_slug,
	p_dc.code as p_dc_code, p_dc."name" as p_dc_name, p_dc.parent_slug as p_dc_parent_slug,
	
	r_p_oc.slug as r_p_oc_slug, r_p_oc.name as r_p_oc_name, r_p_oc.parent_slug as r_p_oc_parent_slug, 
	r_p_dc.slug as r_p_dc_slug, r_p_dc.name as r_p_dc_name, r_p_dc.parent_slug as r_p_dc_parent_slug
from 
	prices as pr
	left join ports as p_oc on p_oc.code = pr.orig_code
	left join ports as p_dc on p_dc.code = pr.dest_code
	left join regions as r_p_oc on r_p_oc.slug = p_oc.parent_slug
	left join regions as r_p_dc on r_p_dc.slug = p_dc.parent_slug
```


Below query used to retrieve the list with the average prices for each day on a route between port codes origin and destination
```sql
select
  to_char(gs_tbl.gs_day, 'YYYY-MM-DD') as "day",
  result_tbl.average_price
from
  (
    select generate_series.gs_day::date 
    from generate_series('2016-01-01'::date, '2016-01-10'::date, interval '1 day') as generate_series(gs_day)
  ) as gs_tbl

  left join (
    select 
      vppr."day",
      (
        case 
          when COUNT(1) >=3 then CAST(ROUND(AVG(vppr.price))AS INTEGER)
          else null
          end
      ) as average_price
    from 
      v_price_port_region as vppr
    where
      ( vppr.day between '2016-01-01' and '2016-01-10' )
      and ( vppr.orig_code ='CNSGH' or p_oc_parent_slug = 'CNSGH' or r_p_oc_parent_slug = 'CNSGH' )
      and ( vppr.dest_code ='north_europe_main' or p_dc_parent_slug = 'north_europe_main' or r_p_dc_parent_slug = 'north_europe_main' )
    group by vppr.day
  ) as result_tbl on result_tbl.day = gs_tbl.gs_day
order by gs_tbl.gs_day
-- limit 2 offset 4
```

If periodically, price data is added or updated then we can create **Materialized Views** and refresh the data periodically. It will help to improve performance and to reduce the fetching time
```bash
We can refer the above the same queries

CREATE MATERIALIZED VIEW mv_price_port_region...
-- Above same Create a view query and list query
...

A common approach to automatically refresh materialized views is by using cron jobs. The below job will run every 15 min
15 * * * * psql -d name_of_your_database -c "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_price_port_region"

```