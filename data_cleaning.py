import re
import pandas as pd


def clean_column_name(column_name: str) -> str:
    """
    Sanitize column names by converting them to lowercase, removing whitespace,
    replacing spaces and special characters with underscores, and removing any
    duplicate underscores.
    """
    # Convert to lowercase and remove whitespace
    column_name = column_name.lower().strip()
    # Replace spaces and special characters with underscores
    column_name = re.sub(r'[\s\W]+', '_', column_name)
    # Remove any duplicate underscores
    column_name = re.sub(r'_+', '_', column_name)
    return column_name


def clean_numeric(input_str: str) -> str:
    """
    Removes all non-numeric characters from a string,
    except for decimal points.
    """
    return re.sub(r'[^\d\.]+', '', input_str)


def clean_email(email: str) -> str:
    """
    Clean the email address by removing leading and trailing whitespace, converting
    to lowercase, and removing any invalid characters. Returns the cleaned email
    address or an empty string if the email is invalid.
    """
    # Remove leading and trailing whitespace
    email = email.strip()

    # Convert to lowercase
    email = email.lower()

    # Remove invalid characters
    email = re.sub(r'[^a-z0-9\.\-\_@]', '', email)

    return email


def convert_yn_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts all the columns which names end with _yn to boolean type.
    """
    for column in df.columns:
        if column.endswith("_yn"):
            df[column] = df[column].map({'Y': True, "N": False}, na_action='ignore').fillna(False)
    return df


def clean_customer_df(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [clean_column_name(column) for column in df.columns]
    df['loyalty_card_number'] = pd.to_numeric(df['loyalty_card_number'].apply(clean_numeric))
    df['customer_email'] = df['customer_email'].apply(clean_email).dropna()
    df['customer_since'] = pd.to_datetime(df['customer_since']).dt.date
    df['birthdate'] = pd.to_datetime(df['birthdate']).dt.date
    df = df.drop(['birth_year'], axis=1)
    return df


def clean_product_df(df: pd.DataFrame) -> pd.DataFrame:
    df['current_retail_price'] = pd.to_numeric(df['current_retail_price'].apply(clean_numeric))
    df = convert_yn_columns(df)
    return df


def clean_receipt_df(df: pd.DataFrame) -> pd.DataFrame:
    df['timestamp'] = pd.to_datetime(df['transaction_date'] + ' ' + df['transaction_time'])
    df['transaction_year'] = df['timestamp'].dt.year
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df = df.apply(lambda x: x.replace({'Y': True, 'N': False}) if x.name.endswith('_yn') else x)
    df = convert_yn_columns(df)
    df = df.drop('transaction_time', axis=1)
    return df
