import pandas as pd
import os
from datetime import datetime, timedelta

AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')
csv_file_store_path = AIRFLOW_HOME+'/dags/data/supermarket_sales - Sheet1.csv'

def dim_branch(df, hook) -> None:
    df.columns = [column_title.lower().replace(' ', '_') for column_title in df.columns]
    branch = pd.Series(df['branch'].unique(), name='branch')
    branch_df = pd.DataFrame(branch)
    branch_df.index += 1
    branch_df.to_sql(name='dim_branch', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace')

def dim_city(df, hook):
    city = pd.Series(df['city'].unique(), name='city')
    city_df = pd.DataFrame(city)
    city_df.index += 1
    city_df.to_sql(name='dim_city', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace')

def dim_customer_type(df, hook):
    customer_type = pd.Series(df['customer_type'].unique(), name='customer_type')
    customer_type_df = pd.DataFrame(customer_type)
    customer_type_df.index += 1
    customer_type_df.to_sql(name='dim_customer_type', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace')
   
def dim_gender(df, hook):
    gender = pd.Series(df['gender'].unique(), name='gender')
    gender_df = pd.DataFrame(gender)
    gender_df.index += 1
    gender_df.to_sql(name='dim_gender', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace')
   
def dim_product_line(df, hook):
    product_line = pd.Series(df['product_line'].unique(), name='product_line')
    product_line_df = pd.DataFrame(product_line)
    product_line_df.index += 1
    product_line_df.to_sql(name='dim_product_line', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace')
   
def dim_payment(df, hook):
    payment = pd.Series(df['payment'].unique(), name='payment')
    payment_df = pd.DataFrame(payment)
    payment_df.index += 1
    payment_df.to_sql(name='dim_payment', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace')

def fact_sales(df, hook):
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM nds.dim_branch;""")
    branch = dict(cursor.fetchall())
    cursor.execute("""SELECT * FROM nds.dim_city;""")
    city = dict(cursor.fetchall())
    cursor.execute("""SELECT * FROM nds.dim_customer_type;""")
    customer_type = dict(cursor.fetchall())
    cursor.execute("""SELECT * FROM nds.dim_gender;""")
    gender = dict(cursor.fetchall())
    cursor.execute("""SELECT * FROM nds.dim_product_line;""")
    product_line = dict(cursor.fetchall())
    cursor.execute("""SELECT * FROM nds.dim_payment;""")
    payment = dict(cursor.fetchall())
    cursor.close()
    conn.close()
    df['date'] = pd.to_datetime(df['date'], format="%m/%d/%Y")
    df['time'] = pd.to_datetime(df['time'], format="%H:%M").dt.time
    df['branch'] = df['branch'].map({v: k for k, v in branch.items()})
    df['city'] = df['city'].map({v: k for k, v in city.items()})
    df['customer_type'] = df['customer_type'].map({v: k for k, v in customer_type.items()})
    df['gender'] = df['gender'].map({v: k for k, v in gender.items()})
    df['product_line'] = df['product_line'].map({v: k for k, v in product_line.items()})
    df['payment'] = df['payment'].map({v: k for k, v in payment.items()})
    df.index += 1
    df.to_sql(name='fact_sales', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace', index=False)

def dim_nds(hook):
    df = pd.read_csv(csv_file_store_path)
    df.columns = [column_title.lower().replace(' ', '_') for column_title in df.columns]
    dim_branch(df, hook)
    dim_city(df, hook)
    dim_customer_type(df, hook)
    dim_gender(df, hook)
    dim_payment(df, hook)
    dim_product_line(df, hook)
    fact_sales(df, hook)
