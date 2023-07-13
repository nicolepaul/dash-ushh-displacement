import os
import zipfile
import pandas as pd


def parse_puf_files(data_folder, drop_bad=True):
    """This function loads all available PUF CSV zip files

    Args:
        data_folder (str): Location where PUF CSV zipfiles are stored

    Returns:
        puf (pd.DataFrame): DataFrame combining all available PUF CSVs
    """

    # Find all available PUF zip files
    file_suffix = "_PUF_CSV.zip"
    puf_zip_files = [
        file for file in os.listdir(data_folder) if file.endswith(file_suffix)
    ]
    puf_zip_paths = [os.path.join(data_folder, file) for file in puf_zip_files]
    n_puf = len(puf_zip_files)

    # Initialize data
    pufs = [pd.DataFrame() for _ in range(n_puf)]
    for i in range(n_puf):
        with zipfile.ZipFile(puf_zip_paths[i], "r") as f:
            puf_name = [
                name
                for name in f.namelist()
                if name.endswith(".csv") and "repwgt" not in name
            ][0]
            pufs[i] = pd.read_csv(f.open(puf_name))

    # Combine data
    puf = pd.concat(pufs, axis=0)

    # Print that 'bad' values are being dropped
    if drop_bad:
        bad_vals = [-88, -99]
        puf.replace(bad_vals, float('nan'), inplace=True)
        print(f"Setting bad_vals ({bad_vals}) = NaN")

    # Return result
    return puf


def custom_puf_handling(puf, data_dict):

    # Identify inital columns
    in_cols = puf.columns.tolist()

    # Bin continuous or discrete datasets
    puf, data_dict = convert_birth_year_to_age_bin(puf, data_dict)
    puf, data_dict = convert_hh_size_to_bin(puf, data_dict)
    puf, data_dict = convert_rent_to_bin(puf, data_dict)

    # Determine new columns
    out_cols = puf.columns.tolist()
    new_cols = [col for col in out_cols if col not in in_cols]
    print(f"Added new columns: {new_cols}")

    return puf, data_dict


def convert_birth_year_to_age_bin(df, data_dict):
    # Survey baseline year
    survey_year = 2022
    # Determine bins
    age_bins = [0, 24, 34, 44, 54, 64, 74, 1000]
    # Determine index of bins
    n_bins = len(age_bins) - 1
    age_idx = range(n_bins)
    # Create friendly strings for bins
    age_strs = [f'{age_bins[i]+1} - {age_bins[i+1]}' for i in range(n_bins)]
    age_strs[0] = f'{age_bins[1]} or less'
    age_strs[-1] = f'{age_bins[-2]+1}+'
    conversion = {age_idx[i]: age_strs[i] for i in range(n_bins)}
    # Add new column for age bins
    age_col = 'AGE_BIN'
    birthyear_col = 'TBIRTH_YEAR'
    df[age_col] = survey_year - df[birthyear_col].astype(int)
    for i in range(n_bins):
        idx = (df[age_col] > age_bins[i]) & (df[age_col] <= age_bins[i+1])
        df.loc[idx, age_col] = age_idx[i]
    # Adjust data dictionary
    if age_col not in data_dict.index:
        new_row = pd.DataFrame(index=[age_col], columns=data_dict.columns)
        new_row.loc[age_col]['Type'] = 'Ordinal'
        new_row.loc[age_col]['Name'] = 'Age'
        new_row.loc[age_col]['Conversion'] = conversion
        data_dict = pd.concat([data_dict, new_row], axis=0)
    else:
        data_dict.loc[age_col]['Conversion'] = conversion
    # Return result
    return df, data_dict


def convert_hh_size_to_bin(df, data_dict):
    # Determine bins
    hh_bins = [0, 1, 2, 4, 7, 1000]
    # Determine index of bins
    n_bins = len(hh_bins) - 1
    hh_idx = range(n_bins)
    # Create friendly strings for bins
    hh_strs = [f'{hh_bins[i]+1} - {hh_bins[i+1]}' for i in range(n_bins)]
    hh_strs[0] = '1'
    hh_strs[1] = '2'
    hh_strs[-1] = f'{hh_bins[-2]+1}+'
    conversion = {hh_idx[i]: hh_strs[i] for i in range(n_bins)}
    # Add new column for age bins
    hh_bin_col = 'HH_BIN'
    hh_col = 'THHLD_NUMPER'
    df[hh_bin_col] = float('nan')
    for i in range(n_bins):
        idx = (df[hh_col] > hh_bins[i]) & (df[hh_col] <= hh_bins[i+1])
        df.loc[idx, hh_bin_col] = hh_idx[i]
    # Adjust data dictionary
    if hh_bin_col not in data_dict.index:
        new_row = pd.DataFrame(index=[hh_bin_col], columns=data_dict.columns)
        new_row.loc[hh_bin_col]['Type'] = 'Ordinal'
        new_row.loc[hh_bin_col]['Name'] = 'Household size'
        new_row.loc[hh_bin_col]['Conversion'] = conversion
        data_dict = pd.concat([data_dict, new_row], axis=0)
    else:
        data_dict.loc[hh_bin_col]['Conversion'] = conversion
    # Return result
    return df, data_dict


def convert_rent_to_bin(df, data_dict):
    # Determine bins
    rent_bins = [0, 400, 800, 1200, 2000, 10000]
    # Determine index of bins
    n_bins = len(rent_bins) - 1
    rent_idx = range(n_bins)
    # Create friendly strings for bins
    rent_strs = [f'\${rent_bins[i]:,.0f} - \${rent_bins[i+1]:,.0f}' for i in range(n_bins)]
    rent_strs[0] = f'Less than \${rent_bins[2]:,.0f}'
    rent_strs[-1] = f'\${rent_bins[-2]:,.0f} or more'
    conversion = {rent_idx[i]: rent_strs[i] for i in range(n_bins)}
    # Add new column for age bins
    rent_bin_col = 'RENT_BIN'
    rent_col = 'TRENTAMT'
    df[rent_bin_col] = float('nan')
    for i in range(n_bins):
        idx = (df[rent_col] > rent_bins[i]) & (df[rent_col] <= rent_bins[i+1])
        df.loc[idx, rent_bin_col] = rent_idx[i]
    # Adjust data dictionary
    if rent_bin_col not in data_dict.index:
        new_row = pd.DataFrame(index=[rent_bin_col], columns=data_dict.columns)
        new_row.loc[rent_bin_col]['Type'] = 'Ordinal'
        new_row.loc[rent_bin_col]['Name'] = 'Rent (per month)'
        new_row.loc[rent_bin_col]['Conversion'] = conversion
        data_dict = pd.concat([data_dict, new_row], axis=0)
    else:
        data_dict.loc[rent_bin_col]['Conversion'] = conversion
    # Return result
    return df, data_dict