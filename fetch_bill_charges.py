import asyncio
from fetch_graphql import fetch_graphql
import streamlit as st

async def fetch_bill_charges(session, start_date, end_date, token):
    current_page = 1
    all_bill_charges = []

    # Create a placeholder for status updates
    status_placeholder = st.empty()

    while True:
        query = '''query ($filters: BillChargeFiltersInput, $pagination: PaginationInput) {
                fetchBillCharges(filters: $filters, pagination: $pagination) {
                    data {
                        quote {
                            id
                            customer {
                                id
                                name
                                taxvat
                                email
                            }
                            status
                            bill {
                                total
                                installmentsQuantity
                                items {
                                    amount
                                    description
                                    quantity
                                }
                            }
                        }
                        store {
                            name
                        }
                        amount
                        paidAt
                        dueAt
                        isPaid
                        paymentMethod {
                            name
                        }
                    }
                    meta {
                        currentPage
                        lastPage
                    }
                }
            }'''
        variables = {
            'filters': {
                'paidAtRange': {
                    'start': start_date,
                    'end': end_date
                }
            },
            'pagination': {
                'currentPage': current_page,
                'perPage': 200
            }
        }

        data = await fetch_graphql(session, 'https://open-api.eprocorpo.com.br/graphql', query, variables, token)

        if data is None:
            status_placeholder.error(f"❌ Falha ao baixar página {current_page}. Tentando novamente...")
            continue

        if 'errors' in data:
            status_placeholder.error(f"❌ Erro GraphQL: {data['errors']}")
            return None

        if 'data' not in data or 'fetchBillCharges' not in data['data']:
            status_placeholder.error(f"❌ Estrutura de resposta inesperada")
            return None

        bill_charges_data = data['data']['fetchBillCharges']['data']
        all_bill_charges.extend(bill_charges_data)

        meta = data['data']['fetchBillCharges']['meta']
        status_message = f"📥 Baixando relatório de Vendas - Página: {current_page} de {meta['lastPage']} - De: {start_date} - Até: {end_date}"
        status_placeholder.info(status_message)

        if current_page >= meta['lastPage']:
            break

        current_page += 1
        await asyncio.sleep(1)

    final_message = f"✅ Download concluído! Total de {len(all_bill_charges)} registros baixados."
    status_placeholder.success(final_message)
    return all_bill_charges
