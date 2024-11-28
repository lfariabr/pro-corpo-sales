import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import numpy as np

# Custom color palette
COLORS = ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6', '#1abc9c', '#e67e22', '#34495e']

def generate_color_gradient(n_colors):
    """Generate a gradient of purple colors."""
    color_scale = []
    for i in range(n_colors):
        # Generate colors from light purple to dark purple
        r = int(232 - (i * (232-128)/n_colors))  # From 232 to 128
        g = int(232 - (i * (232-0)/n_colors))    # From 232 to 0
        b = int(250 - (i * (250-128)/n_colors))  # From 250 to 128
        color_scale.append(f'rgb({r},{g},{b})')
    return color_scale

# Page config
st.set_page_config(
    page_title="COC - Análise de Vendas",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("COC - Análise de Vendas 📊")

# File uploader
uploaded_file = st.file_uploader("Escolha o arquivo Excel", type=['xlsx'])

if uploaded_file is not None:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)
    
    # Convert 'Data venda' to datetime and extract date only
    df['Data venda'] = pd.to_datetime(df['Data venda']).dt.date
    
    # Date selector
    today = date.today()
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Data Inicial", value=today)
    with col2:
        end_date = st.date_input("Data Final", value=today)
    
    # Date validation
    if start_date > end_date:
        st.error("Data inicial deve ser anterior ou igual à data final")
        st.stop()
    
    # Apply filters
    df = df[df['Status'] == 'Finalizado']
    df = df[df['Consultor'] != 'BKO VENDAS']
    df = df[
        (df['Data venda'] >= start_date) & 
        (df['Data venda'] <= end_date)
    ]
    
    if len(df) == 0:
        st.warning("Nenhum dado encontrado para o período selecionado")
        st.stop()
    
    # Add some statistics
    st.header("Estatísticas Gerais 💎")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_valor = df['Valor líquido'].sum()
        st.metric("Valor Total", f"R$ {total_valor:,.2f}")
    
    with col2:
        media_valor = df['Valor líquido'].mean()
        st.metric("Ticket Médio", f"R$ {media_valor:,.2f}")
    
    with col3:
        total_vendas = len(df)
        st.metric("Total de Vendas", f"{total_vendas:,}")

    st.write("---")

    # Division 1
    st.header("Visão por Unidade 💜")
    col1, col2 = st.columns(2)
    
    with col1:
        # DataFrame grouped by Unidade
        unidade_df = df.groupby('Unidade')['Valor líquido'].sum().sort_values(ascending=False).reset_index()
        unidade_df['Valor líquido'] = unidade_df['Valor líquido'].apply(lambda x: f'R$ {x:,.2f}')
        st.dataframe(unidade_df, hide_index=True)
    
    with col2:
        # Bar chart for "Valor líquido por Unidade"
        unidade_sales = df.groupby('Unidade')['Valor líquido'].sum().sort_values(ascending=True)
        
        # Generate enough colors for all units
        colors = generate_color_gradient(len(unidade_sales))
        
        fig = go.Figure(data=[
            go.Bar(
                x=unidade_sales.index,
                y=unidade_sales.values,
                text=[f'R$ {x:,.2f}' for x in unidade_sales.values],
                textposition='auto',
                marker_color=colors
            )
        ])
        
        fig.update_layout(
            xaxis_title='Unidade',
            yaxis_title='Valor líquido (R$)',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Division 2
    st.header("Vendas por Consultor 💎")
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart for "Análise por Consultor"
        consultor_sales = df.groupby('Consultor')['Valor líquido'].sum().sort_values(ascending=True)
        
        # Generate enough colors for all consultants
        colors = generate_color_gradient(len(consultor_sales))
        
        fig = go.Figure(data=[
            go.Bar(
                x=consultor_sales.index,
                y=consultor_sales.values,
                text=[f'R$ {x:,.2f}' for x in consultor_sales.values],
                textposition='auto',
                marker_color=colors
            )
        ])
        
        fig.update_layout(
            xaxis_title='Consultor',
            yaxis_title='Valor líquido (R$)',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # DataFrame grouped by Consultor with additional metrics
        consultor_stats = df.groupby('Consultor').agg({
            'Valor líquido': ['sum', 'mean'],
            'ID orçamento': 'nunique'  # Count unique budget IDs
        }).round(2)
        
        # Rename columns
        consultor_stats.columns = ['Total Vendas', 'Média por Venda', 'Quantidade']
        
        # Reorder columns
        consultor_stats = consultor_stats[['Total Vendas', 'Quantidade', 'Média por Venda']]
        consultor_stats = consultor_stats.sort_values('Total Vendas', ascending=False)
        
        # Format currency values
        consultor_stats['Total Vendas'] = consultor_stats['Total Vendas'].apply(lambda x: f'R$ {x:,.2f}')
        consultor_stats['Média por Venda'] = consultor_stats['Média por Venda'].apply(lambda x: f'R$ {x:,.2f}')
        
        # Reset index to show Consultor as a column
        consultor_stats = consultor_stats.reset_index()
        
        st.dataframe(consultor_stats, hide_index=True)
    
    # Division 3
    st.header("Visão por Procedimento 💜")
    col1, col2 = st.columns(2)
    
    with col1:
        # DataFrame grouped by Procedimento (top 10)
        procedimento_df = df.groupby('Procedimento')['Valor líquido'].sum().sort_values(ascending=False).head(10).reset_index()
        procedimento_df['Valor líquido'] = procedimento_df['Valor líquido'].apply(lambda x: f'R$ {x:,.2f}')
        st.dataframe(procedimento_df, hide_index=True)
    
    with col2:
        # Pie chart for top 5 procedures using Plotly
        top_5_proc = df.groupby('Procedimento')['Valor líquido'].sum().sort_values(ascending=False).head(5)
        
        fig = go.Figure(data=[go.Pie(
            labels=top_5_proc.index,
            values=top_5_proc.values,
            hole=.4,
            textinfo='label+percent',
            marker=dict(colors=COLORS)
        )])
        
        fig.update_layout(
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    
else:
    st.info("Por favor, faça upload do arquivo Excel para visualizar a análise.")

# Footer
st.markdown("<div style='position: fixed; bottom: 10px; right: 10px; font-size: 12px;'>Pró-Corpo Lab 💜</div>", unsafe_allow_html=True)