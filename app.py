import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import asyncio
import aiohttp
from supabase import create_client, Client
from fetch_bill_charges import fetch_bill_charges
import json
from postgrest.exceptions import APIError

# Initialize Supabase client
supabase: Client = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# Try to access the table, if it doesn't exist, we'll catch the error
try:
    supabase.table('bill_charges').select("*").limit(1).execute()
except APIError as e:
    if 'relation "public.bill_charges" does not exist' in str(e):
        st.error("The bill_charges table doesn't exist in your Supabase database. Please create it using the following SQL in the Supabase SQL editor:")
        st.code("""
CREATE TABLE IF NOT EXISTS bill_charges (
    id SERIAL PRIMARY KEY,
    quote_id TEXT,
    customer_id TEXT,
    customer_name TEXT,
    customer_taxvat TEXT,
    customer_email TEXT,
    store_name TEXT,
    total_amount NUMERIC,
    installments INTEGER,
    paid_at TIMESTAMPTZ,
    due_at TIMESTAMPTZ,
    is_paid BOOLEAN,
    payment_method TEXT,
    status TEXT,
    quote_items TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
        """, language="sql")
        st.stop()

# Page config
st.set_page_config(
    page_title="COC - Relatório de Vendas",
    page_icon="",
    layout="wide"
)

# Title
st.title("COC - Relatório de Vendas")

# Password protection
password = st.text_input("Enter password:", type="password")
correct_password = st.secrets["APP_PASSWORD"]

if password == correct_password:
    # Date inputs with today as default
    today = date.today()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=today, max_value=today)
    with col2:
        end_date = st.date_input("End Date", value=today, max_value=today)
    
    # Date validation
    if start_date > end_date:
        st.error("Start date must be before or equal to end date")
        st.stop()
    
    if end_date > today:
        st.error("End date cannot be in the future")
        st.stop()
    
    date_range = (end_date - start_date).days
    if date_range > 90:
        st.warning("")
    
    if st.button("Baixar Relatório "):
        try:
            with st.spinner("Por favor aguarde, estamos baixando os dados"):
                # Clear existing data
                clear_result = supabase.table('bill_charges').delete().neq('id', 0).execute()
                st.write("")
                
                # Fetch new data
                async def fetch_data():
                    async with aiohttp.ClientSession() as session:
                        token = st.secrets["TOKEN"]
                        bill_charges = await fetch_bill_charges(session, start_date.isoformat(), end_date.isoformat(), token)
                        return bill_charges

                # Run the async function
                bill_charges = asyncio.run(fetch_data())
                
                if bill_charges is None:
                    st.error("Failed to fetch data from the API. Please check the logs for details.")
                elif not bill_charges:
                    st.warning(f"No records found between {start_date} and {end_date}")
                else:
                    total_records = len(bill_charges)
                    st.write(f"Processing {total_records} records...")
                    
                    # Create progress bar
                    progress_bar = st.progress(0)
                    
                    # Transform data in batches
                    BATCH_SIZE = 100
                    transformed_data = []
                    
                    for i, charge in enumerate(bill_charges):
                        quote = charge['quote']
                        customer = quote['customer']
                        store = charge['store']
                        
                        record = {
                            'quote_id': quote['id'],
                            'customer_id': customer['id'],
                            'customer_name': customer['name'],
                            'customer_taxvat': customer.get('taxvat'),
                            'customer_email': customer.get('email'),
                            'store_name': store['name'],
                            'total_amount': charge['amount'],
                            'installments': quote['bill'].get('installmentsQuantity'),
                            'paid_at': charge.get('paidAt'),
                            'due_at': charge.get('dueAt'),
                            'is_paid': charge['isPaid'],
                            'payment_method': charge['paymentMethod']['name'],
                            'status': quote['status'],
                            'quote_items': json.dumps(quote['bill']['items'])
                        }
                        transformed_data.append(record)
                        
                        # Update progress
                        progress = (i + 1) / total_records
                        progress_bar.progress(progress)
                        
                        # Batch insert when we reach BATCH_SIZE
                        if len(transformed_data) >= BATCH_SIZE:
                            supabase.table('bill_charges').insert(transformed_data).execute()
                            transformed_data = []
                    
                    # Insert any remaining records
                    if transformed_data:
                        supabase.table('bill_charges').insert(transformed_data).execute()
                    
                    # Create DataFrame for display
                    df = pd.DataFrame(bill_charges)
                    df = pd.json_normalize(bill_charges, sep='_')
                    
                    # Convert amount to proper format
                    # df['amount'] = df['amount'].astype(str).str.replace('.0', '', regex=False)
                    df['amount'] = df['amount'].astype(float) / 100
                    
                    # Group by store and calculate total amount
                    store_totals = df.groupby('store_name')['amount'].sum().reset_index()
                    store_totals.columns = ['Loja', 'Total Vendas']
                    store_totals['Total Vendas'] = store_totals['Total Vendas'].apply(lambda x: f'R$ {x:,.2f}')
                    store_totals = store_totals.sort_values('Total Vendas', ascending=False)
                    
                    # Display success and statistics
                    st.success(f"Successfully processed {total_records} records!")
                    
                    # Show statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Records", total_records)
                    with col2:
                        total_amount = df['amount'].sum()
                        st.metric("Total Amount", f"R$ {total_amount:,.2f}")
                    with col3:
                        paid_count = sum(1 for charge in bill_charges if charge['isPaid'])
                        st.metric("Paid Records", f"{paid_count} ({(paid_count/total_records*100):.1f}%)")
                    
                    # Display the store totals
                    st.subheader("Vendas por Loja")
                    st.dataframe(store_totals, hide_index=True)
                    # Display the dataframe
                    st.dataframe(df)
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)

else:
    st.error("Please enter the correct password to access the application.")