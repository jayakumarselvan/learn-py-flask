import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request
from psycopg2.extras import RealDictCursor
import json
import logging
# from decimal import Decimal
load_dotenv()

logging.basicConfig(filename='log.log', level=logging.INFO)

app = Flask(__name__)

url = os.getenv("DATABASE_URL")
min_price_count_per_day = int ( os.getenv("MIN_PRICE_COUNT_PER_DAY") )
pagination_per_page_default_limit = int ( os.getenv("PAGINATION_PER_PAGE_DEFAULT_LIMIT") )
orig_dest_code_length = int ( os.getenv("ORIG_DEST_CODE_LENGTH") )

connection = psycopg2.connect(url)

# class DecimalEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, Decimal):
#             return str(o)
#         return super().default(o)

@app.get("/api/v1/rates")
def get_rates():

  args = request.args

  date_from = args.get("date_from")
  date_to = args.get("date_to")
  origin = args.get("origin")
  destination = args.get("destination")
  current_page = args.get("page", default=None, type=int)
  per_page = args.get("limit", default=pagination_per_page_default_limit, type=int)

  if per_page <= 0:
    per_page = pagination_per_page_default_limit

  if not all([date_from, date_to, origin, destination]):
    message={
      "message":"date_from, date_to, origin, and destination fields are required",
      "code":400,
      "status": False
    }
    response = app.response_class(
      response=json.dumps(message), 
      status=400, 
      mimetype='application/json'
    )
    return response
  
  sql_limit_str = ""
  if( current_page is not None and current_page > 0 ):

    skip_val = per_page * (current_page - 1)

    sql_limit_str = " limit  {} offset {} ".format(per_page, skip_val)

  where_values = ( date_from, date_to, min_price_count_per_day, date_from, date_to, origin, origin, origin, destination, destination, destination )

  sql_get_rates = (
    """
    select
      to_char(gs_tbl.gs_day, 'YYYY-MM-DD') as "day",
      result_tbl.average_price
    from
      (
        select generate_series.gs_day::date 
        from generate_series(%s::date, %s::date, interval '1 day') as generate_series(gs_day)
      ) as gs_tbl
      left join (
        select 
          pr."day",
          (
            case 
              when COUNT(1) >=%s then CAST(ROUND(AVG(pr.price))AS INTEGER)
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
          ( pr.day between %s and %s )
          and ( pr.orig_code =%s or p_oc.parent_slug = %s or r_p_oc.parent_slug = %s )
          and ( pr.dest_code =%s or p_dc.parent_slug = %s or r_p_dc.parent_slug = %s )
        group by pr.day
      ) as result_tbl on result_tbl.day = gs_tbl.gs_day
      order by gs_tbl.gs_day
      {sql_limit_str}
    """.format(sql_limit_str=sql_limit_str)
  )

  app.logger.info("sql_get_rates")
  app.logger.info(sql_get_rates)
  app.logger.info("where_values")
  app.logger.info(where_values)
  with connection:
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
      cursor.execute(sql_get_rates, where_values)
      rates = cursor.fetchall()

  response = app.response_class(
    # cls=DecimalEncoder is not required for this api
    # response=json.dumps(rates, cls=DecimalEncoder), 
    response=json.dumps(rates), 
    status=200, 
    mimetype='application/json'
  )
  return response


@app.get("/api/v1/rates-list")
def get_rates_list():

  args = request.args

  date_from = args.get("date_from")
  date_to = args.get("date_to")
  origin = args.get("origin")
  destination = args.get("destination")
  current_page = args.get("page", default=None, type=int)
  per_page = args.get("limit", default=pagination_per_page_default_limit, type=int)

  if per_page <= 0:
    per_page = pagination_per_page_default_limit

  if not all([date_from, date_to, origin, destination]):
    message={
      "message":"date_from, date_to, origin, and destination fields are required",
      "code":400,
      "status": False
    }
    response = app.response_class(
      response=json.dumps(message), 
      status=400, 
      mimetype='application/json'
    )
    return response
  
  sql_limit_str = ""
  if( current_page is not None and current_page > 0 ):
    skip_val = per_page * (current_page - 1)
    sql_limit_str = " limit  {} offset {} ".format(per_page, skip_val)

  sql_join_str = ""
  sql_where_str = ""
  if( ( len(origin) == orig_dest_code_length and origin.isupper() ) and ( len(destination) == orig_dest_code_length and destination.isupper() ) ):
    sql_where_str = """
      and ( pr.orig_code = '{origin}' )
      and ( pr.dest_code = '{destination}' )
    """.format(origin=origin, destination=destination)
  else:
    sql_join_str = """
      left join ports as p_oc on p_oc.code = pr.orig_code
      left join ports as p_dc on p_dc.code = pr.dest_code
      left join regions as r_p_oc on r_p_oc.slug = p_oc.parent_slug
      left join regions as r_p_dc on r_p_dc.slug = p_dc.parent_slug
    """
    sql_where_str = """
      and ( pr.orig_code = '{origin}' or p_oc.parent_slug = '{origin}' or r_p_oc.parent_slug = '{origin}' )
      and ( pr.dest_code = '{destination}' or p_dc.parent_slug = '{destination}' or r_p_dc.parent_slug = '{destination}' )
    """.format(origin=origin, destination=destination)
    


  # where_values = ( date_from, date_to, min_price_count_per_day, date_from, date_to, origin, origin, origin, destination, destination, destination )

  sql_get_rates = (
    """
    select
      to_char(gs_tbl.gs_day, 'YYYY-MM-DD') as "day",
      result_tbl.average_price
    from
      (
        select generate_series.gs_day::date 
        from generate_series('{date_from}'::date, '{date_to}'::date, interval '1 day') as generate_series(gs_day)
      ) as gs_tbl
      left join (
        select 
          pr."day",
          (
            case 
              when COUNT(1) >={min_price_count_per_day} then CAST(ROUND(AVG(pr.price))AS INTEGER)
                    else null
              end
          ) as average_price
        from 
          prices as pr
          {sql_join_str}
        where
          ( pr.day between '{date_from}' and '{date_to}' )
          {sql_where_str}
        group by pr.day
      ) as result_tbl on result_tbl.day = gs_tbl.gs_day
      order by gs_tbl.gs_day
      {sql_limit_str}
    """.format(min_price_count_per_day=min_price_count_per_day, date_from=date_from, date_to=date_to, sql_join_str=sql_join_str, sql_where_str=sql_where_str, sql_limit_str=sql_limit_str)
  )

  app.logger.info("sql_get_rates")
  app.logger.info(sql_get_rates)

  with connection:
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
      cursor.execute(sql_get_rates)
      rates = cursor.fetchall()

  response = app.response_class(
    # cls=DecimalEncoder is not required for this api
    # response=json.dumps(rates, cls=DecimalEncoder), 
    response=json.dumps(rates), 
    status=200, 
    mimetype='application/json'
  )
  return response

@app.get("/")
def home():
  return "Hello world!"