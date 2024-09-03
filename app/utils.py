import pandas as pd

def sort_dataframe(df, sort_option, price_column='Discounted Price', rating_column='Product Rating'):
    if sort_option == 'reset':
        if "Unnamed: 0" in df.columns:
            ascending_order = True  # Default sort order for reset
            df = df.sort_values(by="Unnamed: 0", ascending=ascending_order)
            print("reset")

    elif sort_option in ['price_low_to_high', 'price_high_to_low']:
        if price_column in df.columns:
            # Extract numeric price values and handle conversion
            if df[price_column].dtype == 'object':
                df['Currency'] = df[price_column].str.extract(r'([INR$Rs.])')
                df[price_column] = df[price_column].replace({'INR': '', '\$': '', 'Rs.': '', '\xa0': '', ',': ''}, regex=True).astype(float)
            
            # Determine sorting order and apply it
            ascending_order = sort_option == 'price_low_to_high'
            df = df.sort_values(by=price_column, ascending=ascending_order)

            # Format price with currency symbols and proper formatting
            df[price_column] = df['Currency'].fillna('') + ' ' + df[price_column].apply(lambda x: '{:,.2f}'.format(x))
            df = df.drop(columns=['Currency'])
        else:
            print(f"Column '{price_column}' not found.")

    elif sort_option in ['rating_high_to_low', 'rating_low_to_high']:
        if rating_column in df.columns:
            # Clean and convert rating values
            df[rating_column] = pd.to_numeric(df[rating_column].replace({'Stars': ''}, regex=True), errors='coerce')
            
            # Determine sorting order and apply it
            ascending_order = sort_option == 'rating_low_to_high'
            df = df.sort_values(by=rating_column, ascending=ascending_order)
        else:
            print(f"Column '{rating_column}' not found.")

    return df
