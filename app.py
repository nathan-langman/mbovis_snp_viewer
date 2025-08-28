import streamlit as st
import pandas as pd
from pathlib import Path
import os


DATA_FILEPATH = Path(__file__).parent/'data/'

st.set_page_config(
    page_title='M. bovis SNP viewer',
    page_icon=':dna:',
)

def get_data(fname):
    data_path = os.path.join(DATA_FILEPATH, f'{fname}.csv')
    return pd.read_csv(data_path)


@st.cache_data
def get_genomes():
    df = get_data('main_df')
    df = df[~df['masked_snp']]
    df.sort_values(by='POS',inplace=True)
    df.reset_index(drop=True,inplace=True)
    return df[['genome','POS','REF','ALT','QUAL','snp__effect','snp__gene_name','snp__biotype','snp__hgvsp','classification','Host']]


@st.cache_data
def get_snps():
    df = get_data('snp_df')
    df = df[~df['masked_snp']]
    df.sort_values(by='POS',inplace=True)
    df.reset_index(drop=True,inplace=True)
    return df[['POS','REF','ALT','snp__gene_name','genome_count','classification_count','mode_class','characteristic_snp','snp__effect','snp__hgvsp']]


@st.cache_data
def get_mutpred():
    df = get_data('mutpred_results')
    df.sort_values(by='gene',inplace=True)
    df.reset_index(drop=True,inplace=True)
    return df.drop('comment',axis=1)


genome_df = get_genomes()
genomes = genome_df['genome'].unique()
genomes.sort()
snp_df = get_snps()
mutpred_df = get_mutpred()


st.title(":dna: M. Bovis SNP Viewer :dna:")
st.subheader("View information on SNPs from M. bovis wild strains")
view_options = st.selectbox(
    "Dashboard options",
    ("Select...", "Specific genome", "SNP list", "Characteristic SNPs", "Help"),
)

if view_options == 'Specific genome':
    genome_input = st.selectbox(
        "Choose a genome",
        genomes
    )
    spec_genome_df = genome_df[genome_df['genome']==genome_input]

    host = spec_genome_df['Host'].values[0]
    classification = spec_genome_df['classification'].values[0]

    st.write(f'Genome: {genome_input}')
    st.write(f'Host: {host}')
    st.write(f'Sublineage: {classification}')
    st.write(f"SNP count: {len(spec_genome_df)}")

    st.subheader("SNP List")
    st.dataframe(spec_genome_df.drop(['Host','classification','genome'],axis=1))

    st.subheader("Missense genes")
    st.dataframe(spec_genome_df[spec_genome_df['snp__effect']=='missense_variant']['snp__gene_name'].value_counts().rename('Missense SNP count').reset_index())

elif view_options == 'SNP list':
    st.subheader("SNP List")
    st.dataframe(snp_df)

elif view_options == 'Characteristic SNPs':
    st.subheader("Characteristic SNPs")
    st.dataframe(mutpred_df)

elif view_options == 'Help':
    st.subheader("Help")
    st.write("This tool allows a user to display data on SNPs from M. bovis wild strains.")
    st.write("The options are to:")
    st.write("  1) Select a specific genome and see all SNPs associated with it.")
    st.write("  2) View the full list of SNPs observed across the genomes analysed.")
    st.write("  3) View the MutPred2 predictions for 'characteristic SNPs'")

else:
    st.write('An option must be selected to display data.')