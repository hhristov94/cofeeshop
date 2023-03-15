from datetime import date
from typing import Type, List, Dict, Tuple

import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from loguru import logger
from sqlmodel import Session, SQLModel, create_engine, select

from sqlalchemy.sql import text
from sqlalchemy import func
from data_cleaning import clean_receipt_df, clean_customer_df, clean_product_df
from models import Customer, Product, Receipt, CustomerRead, ProductSales, CustomerLastOrder

sqlite_file_name = "data/coffeeshop.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


def insert_df(model: Type[SQLModel], df: pd.DataFrame) -> None:
    logger.info(f"Inserting rows into {model.__tablename__}...")
    with Session(engine) as session:
        for row in df.itertuples():
            session.add(model(**row._asdict()))
        session.commit()


def empty_table(model: Type[SQLModel]) -> Tuple | None:
    with Session(engine) as session:
        query = text(
            f'''SELECT 1 FROM {model.__tablename__} LIMIT 1; 
             ''')
        result = session.execute(query)
        return result.fetchone()


def insert_files() -> None:
    product_df = pd.read_csv('data/product.csv')
    product_df = clean_product_df(product_df)
    customer_df = pd.read_csv('data/customer.csv')
    customer_df = clean_customer_df(customer_df)
    receipt_df = pd.read_csv('data/sales_receipts.csv')
    receipt_df = clean_receipt_df(receipt_df)
    for df, model in zip((product_df, customer_df, receipt_df),
                         (Product, Customer, Receipt)):
        if empty_table(model) is None:
            insert_df(model, df)
        else:
            logger.info(f"{model.__tablename__} has rows. Skipping...")


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
    insert_files()


@app.get("/customers/birthday", response_model=Dict[str, List[CustomerRead]])
def birthdays(*, session: Session = Depends(get_session)):
    """
       Returns a list of all the customers that have a birthday today.
    """
    """
    SELECT customer_id, customer_first_name
    FROM customer
    WHERE birthdate = DATE.TODAY()
    """
    statement = select(Customer).where(Customer.birthdate == date.today())
    customers = session.exec(statement).all()
    return {'customers': customers}


@app.get("/products/top-selling-products/{year}", response_model=Dict[str, List[ProductSales]])
def products_sales_by_year(*, session: Session = Depends(get_session), year: int):
    """
       Returns a list of the top 10 selling products for a given year.
    """
    """
    SELECT product.product_name, count(*) as total_sales
    FROM product
    INNER JOIN receipt
    ON receipt.product_id = product.product_id
    WHERE year(receipt.timestamp) == "{year}"
    GROUP BY product.product_name
    ORDER BY total_sales DESC
    LIMIT 10
    """
    statement = select(Product.product,
                       func.count(Product.product).label('total_sales')) \
        .join(Receipt).where(Receipt.transaction_year == year) \
        .group_by(Product.product) \
        .order_by(text('total_sales DESC')) \
        .limit(10)
    products = session.exec(statement).all()

    if not products:
        raise HTTPException(status_code=404, detail="There are no sales for this year")
    return {'products': products}


@app.get("/customers/last-order-per-customer", response_model=Dict[str, List[CustomerLastOrder]])
def customers_last_orders(*, session: Session = Depends(get_session)):
    """
    Returns the list of all customers and their corresponding last order date.
    """
    query = text('''
        SELECT customer.customer_id, customer.customer_email, L.last_order_date
        FROM ( SELECT * FROM 
                ( SELECT receipt.customer_id, 
                         row_number() OVER (PARTITION BY receipt.customer_id
                                            ORDER BY receipt.timestamp DESC) AS nth_order_reversed,
                        receipt.transaction_date as last_order_date
                  FROM receipt )
               WHERE nth_order_reversed = 1) as L
        INNER JOIN customer
        ON customer.customer_id = L.customer_id     
        ''')
    customers = session.execute(query).all()
    return {'customers': customers}
