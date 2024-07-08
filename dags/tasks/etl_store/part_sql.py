generate_schema = '''
    -- Создание схем, если таковых нет
    create schema if not exists nds;
    create schema if not exists dds;
    create schema if not exists stg;
'''

generate_tables_dds = '''

    -- Создание таблиц dds
    create table if not exists dds.dim_branch(
        id serial primary key,
        branch varchar(3) not null
    );

    create table if not exists dds.dim_city(
        id serial primary key,
        city varchar(150) not null
    );

    create table if not exists dds.dim_customer_type(
        id serial primary key,
        customer_type varchar(10) not null
    );

    create table if not exists dds.dim_gender(
        id serial primary key,
        gender varchar(10) not null
    );

    create table if not exists dds.dim_product_line(
        id serial primary key,
        product_line varchar(150) not null
    );

    create table if not exists dds.dim_payment(
        id serial primary key,
        payment varchar(150) not null
    );

    create table if not exists dds.dim_date as
        with array_date as (
            select dd::date as dt
            from generate_series('2000-01-01'::timestamp,'2050-01-01'::timestamp,'1 day'::interval) dd
        )
        select
            dt as date,
            date_part('week', dt)::int as week_of_year,
            date_trunc('week', dt)::date as week_start,
            date_part('isodow', dt)::int as day_of_week,
            date_part('month', dt)::int as month_number,
            to_char(dt::timestamp, 'Month') as month_name,
            extract(quarter from dt) as quarter,
            date_part('isoyear', dt)::int as year
        from array_date;
        alter table dds.dim_date drop constraint if exists dim_date_pkey cascade;
        alter table dds.dim_date add constraint dim_date_pkey primary key (date);
            
    create table if not exists dds.dim_time as
        with array_time as (
            select 
                tt::time as t
            from generate_series(current_date, current_date + '1 day - 1 second'::interval,'1 minute') tt
        ),
        array_part as (
            select
                t as time
            from array_time order by t
        )
        select time,
                case
                    when (time >= '00:00:00'::time AND time < '06:00:00'::time) then 'night'
                    when (time >= '06:00:00'::time AND time < '11:00:00'::time) then 'morning'
                    when (time >= '11:00:00'::time AND time < '17:00:00'::time) then 'noon'
                    when (time >= '17:00:00'::time AND time < '22:00:00'::time) then 'evening'
                    when (time >= '22:00:00'::time AND time < '24:00:00'::time) then 'night'
                end as date_part 
        from array_part;
        alter table dds.dim_time drop constraint if exists dim_time_pkey cascade;
        alter table dds.dim_time add constraint dim_time_pkey primary key (time);

    create table if not exists dds.fact_sales(
        invoice_id varchar(15) PRIMARY KEY,
        branch int not null references dds.dim_branch(id),
        city int not null references dds.dim_city(id),
        customer_type int not null references dds.dim_customer_type(id),
        gender int not null references dds.dim_gender(id),
        product_line int not null references dds.dim_product_line(id),
        unit_price double precision,
        quantity double precision,
        "tax_5%" double precision,
        total double precision,
        date date not null,
        time time not null,
        payment int not null references dds.dim_payment(id),
        cogs double precision,
        gross_margin_percentage double precision,
        gross_income double precision,
        rating double precision
    );
    alter table dds.fact_sales add constraint fact_sales_date_fkey foreign key (date) references dds.dim_date(date);
    alter table dds.fact_sales add constraint fact_sales_time_fkey foreign key (time) references dds.dim_time(time);   
'''

update_dds_tables = '''
    insert into dds.dim_branch (branch)
        (select branch from nds.dim_branch where branch not in (select branch from dds.dim_branch));

    insert into dds.dim_city (city)
        (select city from nds.dim_city where city not in (select city from dds.dim_city));

    insert into dds.dim_customer_type (customer_type)
        (select customer_type from nds.dim_customer_type where customer_type not in (select customer_type from dds.dim_customer_type));

    insert into dds.dim_gender (gender)
        (select gender from nds.dim_gender where gender not in (select gender from dds.dim_gender));

    insert into dds.dim_product_line (product_line)
        (select product_line from nds.dim_product_line where product_line not in (select product_line from dds.dim_product_line));
    
    insert into dds.dim_payment (payment)
        (select payment from nds.dim_payment where payment not in (select payment from dds.dim_payment));
'''

update_dds_fact= '''
    insert into dds.fact_sales (invoice_id, branch, city, customer_type, gender, product_line, unit_price, quantity, "tax_5%",
        total, date, time, payment, cogs, gross_margin_percentage, gross_income, rating)
        (select distinct 
            invoice_id, branch, city, customer_type, gender, 
            product_line, unit_price, quantity, "tax_5%", total, date::date,
            time, payment, cogs, gross_margin_percentage, gross_income, rating 
        from nds.fact_sales where invoice_id not in (select distinct invoice_id FROM dds.fact_sales));
'''