from sqlmodel import Field, SQLModel
from datetime import datetime, date
from typing import Optional


class Customer(SQLModel, table=True):
    customer_id: Optional[int] = Field(primary_key=True)
    customer_first_name: str
    home_store: int
    customer_email: str
    customer_since: date
    loyalty_card_number: int
    birthdate: date
    gender: str


class CustomerRead(SQLModel):
    customer_id: int
    customer_first_name: str


class CustomerLastOrder(SQLModel):
    customer_id: int
    customer_email: str
    last_order_date: date


class Receipt(SQLModel, table=True):
    row_id: Optional[int] = Field(primary_key=True)
    transaction_id: int
    timestamp: datetime
    transaction_date: date
    transaction_year: int
    sales_outlet_id: int
    staff_id: int
    customer_id: int = Field(foreign_key="customer.customer_id")
    instore_yn: bool
    order: int
    line_item_id: int
    product_id: int = Field(foreign_key="product.product_id")
    quantity: int
    line_item_amount: float
    unit_price: float
    promo_item_yn: bool


class Product(SQLModel, table=True):
    product_id: Optional[int] = Field(default=None, primary_key=True)
    product_group: str
    product_category: str
    product_type: str
    product: str
    product_description: str
    unit_of_measure: str
    current_wholesale_price: float
    current_retail_price: float
    tax_exempt_yn: bool
    promo_yn: bool
    new_product_yn: bool


class ProductSales(SQLModel):
    product: str
    total_sales: int
