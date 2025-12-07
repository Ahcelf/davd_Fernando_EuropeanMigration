import eurostat
import pandas as pd


class EurostatETL:
    def __init__(self):
        self.datasets = {
            'population': 'demo_pjan',
            'unemployment': 'une_rt_a',
            'immigration': 'migr_imm8',
            'gdp': 'nama_10_gdp'
        }
        self.countries = {
            'AT': 'Austria', 'BE': 'Bélgica', 'BG': 'Bulgaria', 
            'HR': 'Croacia', 'CY': 'Chipre', 'CZ': 'República Checa',
            'DK': 'Dinamarca', 'EE': 'Estonia', 'FI': 'Finlandia', 
            'FR': 'Francia', 'DE': 'Alemania', 'EL': 'Grecia', 'GR': 'Grecia',
            'HU': 'Hungría', 'IE': 'Irlanda', 'IT': 'Italia', 
            'LV': 'Letonia', 'LT': 'Lituania', 'LU': 'Luxemburgo',
            'MT': 'Malta', 'NL': 'Países Bajos', 'PL': 'Polonia', 
            'PT': 'Portugal', 'RO': 'Rumania', 'SK': 'Eslovaquia',
            'SI': 'Eslovenia', 'ES': 'España', 'SE': 'Suecia',
            'UK': 'Reino Unido', 'NO': 'Noruega', 'CH': 'Suiza',
            'IS': 'Islandia', 'LI': 'Liechtenstein', 'RS': 'Serbia',
            'TR': 'Turquía', 'AL': 'Albania', 'BA': 'Bosnia y Herzegovina',
            'ME': 'Montenegro', 'MK': 'Macedonia del Norte', 'XK': 'Kosovo'
        }
        self.iso3_map = {
            'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 
            'CY': 'CYP', 'CZ': 'CZE', 'DK': 'DNK', 'EE': 'EST', 
            'FI': 'FIN', 'FR': 'FRA', 'DE': 'DEU', 'EL': 'GRC', 
            'GR': 'GRC', 'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA', 
            'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX', 'MT': 'MLT', 
            'NL': 'NLD', 'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 
            'SK': 'SVK', 'SI': 'SVN', 'ES': 'ESP', 'SE': 'SWE',
            'UK': 'GBR', 'NO': 'NOR', 'CH': 'CHE', 'IS': 'ISL',
            'LI': 'LIE', 'RS': 'SRB', 'TR': 'TUR', 'AL': 'ALB',
            'BA': 'BIH', 'ME': 'MNE', 'MK': 'MKD', 'XK': 'XKX'
        }

    def get_country_list(self):
        unique_countries = {}
        for k, v in self.countries.items():
            if v not in unique_countries.values():
                unique_countries[k] = v
        return [{'label': name, 'value': code} for code, name in unique_countries.items()]
    
    def get_country_name(self, code):
        return self.countries.get(code, code)

    def _clean_data(self, df):
        df.columns = [x.lower() for x in df.columns]
        id_vars = [col for col in df.columns if not str(col).strip().isdigit()]
        df_melted = df.melt(id_vars=id_vars, var_name='year', value_name='value')
        df_melted['year'] = pd.to_numeric(df_melted['year'], errors='coerce')
        df_melted['value'] = pd.to_numeric(df_melted['value'], errors='coerce')
        return df_melted.dropna(subset=['year', 'value'])

    def _fetch_data_raw(self, dataset_code):
        try:
            return eurostat.get_data_df(dataset_code)
        except:
            return pd.DataFrame()

    def get_country_profile(self, country_code):
        if not country_code: return None
        
        def fetch_one(key, filters, use_sum=True):
            df = self._fetch_data_raw(self.datasets[key])
            if df.empty: return pd.DataFrame(columns=['year', 'value'])
            
            df.columns = [x.lower() for x in df.columns]
            geo_col = [col for col in df.columns if 'geo' in col][0]
            df = df[df[geo_col] == country_code]
            
            for col, val in filters.items():
                if col in df.columns: df = df[df[col] == val]
            
            df_clean = self._clean_data(df)
            if use_sum:
                return df_clean.groupby('year')['value'].sum().reset_index().sort_values('year')
            else:
                return df_clean.groupby('year')['value'].first().reset_index().sort_values('year')

        return {
            'population': fetch_one('population', {'sex': 'T', 'age': 'TOTAL'}, use_sum=False),
            'unemployment': fetch_one('unemployment', {'age': 'Y15-74', 'sex': 'T'}, use_sum=False),
            'immigration': fetch_one('immigration', {'age': 'TOTAL', 'sex': 'T'}, use_sum=False),
            'gdp': fetch_one('gdp', {'unit': 'CP_MEUR', 'na_item': 'B1GQ'}, use_sum=False)
        }

    def get_comparison_data(self, country_codes):
        results = {'population': [], 'unemployment': [], 'gdp': [], 'immigration': []}
        
        filters_map = {
            'population': {'sex': 'T', 'age': 'TOTAL'},
            'unemployment': {'age': 'Y15-74', 'sex': 'T'},
            'immigration': {'age': 'TOTAL', 'sex': 'T'},
            'gdp': {'unit': 'CP_MEUR', 'na_item': 'B1GQ'}
        }

        for key, filters in filters_map.items():
            df_raw = self._fetch_data_raw(self.datasets[key])
            if df_raw.empty: 
                results[key] = pd.DataFrame()
                continue
            
            df_raw.columns = [x.lower() for x in df_raw.columns]
            geo_col = [col for col in df_raw.columns if 'geo' in col][0]
            df_filtered = df_raw[df_raw[geo_col].isin(country_codes)]
            
            for col, val in filters.items():
                if col in df_filtered.columns: df_filtered = df_filtered[df_filtered[col] == val]

            df_clean = self._clean_data(df_filtered)
            if not df_clean.empty:
                # Use first() to get single value per country/year, avoiding duplicates
                df_final = df_clean.groupby([geo_col, 'year'])['value'].first().reset_index()
                df_final['country_name'] = df_final[geo_col].map(self.countries)
                results[key] = df_final
            else:
                results[key] = pd.DataFrame()
            
        return results

    def get_full_data_for_metric(self, dataset_key, filters=None):
        """Obtiene TODOS los datos (todos los años) para el mapa general"""
        df = self._fetch_data_raw(self.datasets[dataset_key])
        if df.empty: return pd.DataFrame()
        
        df.columns = [x.lower() for x in df.columns]
        
        if filters:
            for col, val in filters.items():
                if col in df.columns: df = df[df[col] == val]

        df_clean = self._clean_data(df)
        geo_col = [col for col in df.columns if 'geo' in col][0]
        
        # Filtrar solo países de interés
        df_clean = df_clean[df_clean[geo_col].isin(self.countries.keys())]
        
        # Agrupar por país y año usando first() para evitar duplicados
        df_final = df_clean.groupby([geo_col, 'year'])['value'].first().reset_index()
        
        # Añadir metadatos
        df_final['country_name'] = df_final[geo_col].map(self.countries)
        df_final['iso_alpha'] = df_final[geo_col].map(self.iso3_map)
        
        return df_final
    
    def get_data_for_synthetic_future(self):
        """
        Obtiene datos completos (todos los países, todos los años) para análisis de futuros sintéticos.
        
        Returns:
            Dict con {'population': df, 'gdp': df, 'unemployment': df, 'immigration': df}
            Cada DataFrame tiene columnas [geo_col, 'year', 'value']
        """
        filters_map = {
            'population': {'sex': 'T', 'age': 'TOTAL'},
            'unemployment': {'sex': 'T', 'age': 'Y_GE15'},
            'immigration': {'sex': 'T', 'age': 'TOTAL'},
            'gdp': {'na_item': 'B1GQ', 'unit': 'CP_MEUR'}
        }
        
        results = {}
        
        for metric, filters in filters_map.items():
            df_raw = self._fetch_data_raw(self.datasets[metric])
            
            if df_raw.empty:
                results[metric] = pd.DataFrame()
                continue
            
            df_raw.columns = [x.lower() for x in df_raw.columns]
            geo_col = [col for col in df_raw.columns if 'geo' in col][0]
            
            # Aplicar filtros
            for col, val in filters.items():
                if col in df_raw.columns:
                    df_raw = df_raw[df_raw[col] == val]
            
            # Limpiar
            df_clean = self._clean_data(df_raw)
            
            # Filtrar solo países válidos
            df_clean = df_clean[df_clean[geo_col].isin(self.countries.keys())]
            
            # Agrupar para evitar duplicados
            df_final = df_clean.groupby([geo_col, 'year'])['value'].first().reset_index()
            
            results[metric] = df_final
        
        return results
