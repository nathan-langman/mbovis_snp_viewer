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
genes = snp_df['snp__gene_name'].unique()
genes.sort()


def sample_view():
    st.subheader("Sample viewer")
    genome_input = st.selectbox(
        "Choose a sample",
        genomes
    )
    spec_genome_df = genome_df[genome_df['genome']==genome_input]

    host = spec_genome_df['Host'].values[0]
    classification = spec_genome_df['classification'].values[0]

    st.write(f'Sample: {genome_input}')
    st.write(f'Host: {host}')
    st.write(f'Sublineage: {classification}')
    st.write(f"SNP count: {len(spec_genome_df)}")

    st.subheader("SNP List")
    st.dataframe(spec_genome_df.drop(['Host','classification','genome'],axis=1))

    st.subheader("Missense genes")
    st.dataframe(spec_genome_df[spec_genome_df['snp__effect']=='missense variant']['snp__gene_name'].value_counts().rename('Missense SNP count').reset_index())


def gene_view():
    st.subheader("Gene viewer")
    gene_input = st.selectbox(
        "Choose a gene",
        genes
    )
    spec_gene_df = genome_df[genome_df['snp__gene_name']==gene_input]
    gene_df = snp_df[snp_df['snp__gene_name']==gene_input]

    st.write(f"Total SNP count: {len(spec_gene_df)}")
    st.write(f"Unique SNP count: {len(gene_df)}")
    st.write(f"Unique non-synonymous SNP count: {len(gene_df[gene_df['snp__effect']!='synonymous_variant'])}")
    st.write(f"Samples with SNP: {spec_gene_df['genome'].nunique()}")

    st.subheader("SNPs")
    st.dataframe(gene_df)

    st.subheader("Full SNP List")
    st.dataframe(spec_gene_df)


def snp_view():
    st.subheader("SNP List")
    st.dataframe(snp_df)


def characteristic_view():
    st.subheader("Characteristic SNPs")
    st.dataframe(mutpred_df)


def help_view():
    st.subheader("Help")
    st.write("This tool allows a user to display data on SNPs from M. bovis wild strains.")
    st.write("The options are to:")
    st.write("  1) Select a specific sample and see all SNPs associated with it.")
    st.write("  1) Select a specific gene and see all SNPs associated with it.")
    st.write("  2) View the full list of SNPs observed across the genomes analysed.")
    st.write("  3) View the MutPred2 predictions for 'characteristic SNPs'")


def unknown_view():
    st.subheader('Welcome to M. bovis SNP Viewer!')
    st.write('Please select an option from the above drop-down to continue.')

view_dict = {
    'Specific genome':sample_view,
    'Specific gene':gene_view,
    'SNP list':snp_view,
    'Characteristic SNPs':characteristic_view,
    'Help':help_view
}

st.title(":dna: M. Bovis SNP Viewer :dna:")
st.subheader("View information on SNPs from M. bovis wild strains")
view_options = st.selectbox(
    "Dashboard menu:",
    ("Select...", "Specific genome", "Specific gene", "SNP list", "Characteristic SNPs", "Help"),
)

display_func = view_dict.get(view_options, unknown_view)
display_func()
