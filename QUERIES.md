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