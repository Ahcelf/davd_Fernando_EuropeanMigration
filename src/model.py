import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize


class StatsModel:
    def __init__(self):
        self.model = LinearRegression()

    def predict_next_years(self, df, years_ahead=3):
        if df is None or df.empty or len(df) < 5:
            return df if df is not None else pd.DataFrame()

        X = df['year'].values.reshape(-1, 1)
        y = df['value'].values
        self.model.fit(X, y)
        last_year = int(pd.to_numeric(df['year']).max())
        future_years = np.array([last_year + i for i in range(1, years_ahead + 1)]).reshape(-1, 1)
        predictions = self.model.predict(future_years)
        df_pred = pd.DataFrame({'year': future_years.flatten(), 'value': predictions, 'type': 'Predicción'})
        df_hist = df.copy()
        df_hist['type'] = 'Histórico'
        return pd.concat([df_hist, df_pred], ignore_index=True)


class SyntheticFutureModel:
    """
    Modelo de Futuros Sintéticos usando la estrategia del "Espejo".
    
    Crea escenarios contrafactuales respondiendo: "¿Qué habría pasado si X evento no hubiera ocurrido?"
    Ejemplo: Impacto del Brexit en Reino Unido, políticas específicas, crisis, etc.
    """
    
    def __init__(self):
        self.weights = None
        self.treated_country = None
        self.donor_countries = None
        self.event_year = None
        self.validation_metrics = {}
        
    def transform_data(self, raw_data):
        """
        Transforma datos brutos a ratios comparables.
        
        Args:
            raw_data: Dict con {'population': df, 'gdp': df, 'unemployment': df, 'immigration': df}
                     Cada df tiene columnas [geo_col, 'year', 'value']
        
        Returns:
            Dict con datos transformados: {'gdp_per_capita': df, 'unemployment_rate': df, 'immigration_rate': df}
        """
        transformed = {}
        
        # 1. PIB per Cápita = PIB / Población
        if 'gdp' in raw_data and 'population' in raw_data:
            gdp_df = raw_data['gdp'].copy()
            pop_df = raw_data['population'].copy()
            
            # Identificar columna geo
            geo_col = [col for col in gdp_df.columns if 'geo' in col.lower()][0]
            
            # Merge GDP y Population
            merged = gdp_df.merge(pop_df, on=[geo_col, 'year'], suffixes=('_gdp', '_pop'))
            merged['gdp_per_capita'] = (merged['value_gdp'] * 1_000_000) / merged['value_pop']  # GDP en millones €
            
            transformed['gdp_per_capita'] = merged[[geo_col, 'year', 'gdp_per_capita']].rename(columns={'gdp_per_capita': 'value'})
        
        # 2. Tasa de Desempleo (ya está en %, solo copiar)
        if 'unemployment' in raw_data:
            transformed['unemployment_rate'] = raw_data['unemployment'].copy()
        
        # 3. Tasa de Inmigración = (Inmigración / Población) * 100
        if 'immigration' in raw_data and 'population' in raw_data:
            imm_df = raw_data['immigration'].copy()
            pop_df = raw_data['population'].copy()
            
            geo_col = [col for col in imm_df.columns if 'geo' in col.lower()][0]
            
            merged = imm_df.merge(pop_df, on=[geo_col, 'year'], suffixes=('_imm', '_pop'))
            merged['immigration_rate'] = (merged['value_imm'] / merged['value_pop']) * 100
            
            transformed['immigration_rate'] = merged[[geo_col, 'year', 'immigration_rate']].rename(columns={'immigration_rate': 'value'})
        
        return transformed
    
    def fit(self, target_country_data, donor_countries_data, event_year, metric='gdp_per_capita'):
        """
        Entrena el modelo usando la estrategia del "Espejo".
        
        Args:
            target_country_data: DataFrame con ['year', 'value'] del país objetivo (pre-transformado)
            donor_countries_data: Dict {country_code: DataFrame} de países donantes
            event_year: Año del evento a analizar
            metric: Métrica a usar ('gdp_per_capita', 'unemployment_rate', 'immigration_rate')
        
        Returns:
            weights: Dict con pesos óptimos {country_code: peso}
        """
        self.event_year = event_year
        
        # Filtrar datos pre-evento
        target_pre = target_country_data[target_country_data['year'] < event_year].copy()
        
        if len(target_pre) < 5:  # Necesitamos al menos 5 años históricos
            return None
        
        # Preparar matriz de donantes
        donor_matrix = []
        donor_codes = []
        
        for country_code, df in donor_countries_data.items():
            df_pre = df[df['year'] < event_year].copy()
            
            # Alinear años
            merged = target_pre[['year']].merge(df_pre[['year', 'value']], on='year', how='left')
            
            # Requiere al menos 70% de datos disponibles
            if merged['value'].notna().sum() >= len(target_pre) * 0.7:
                # Rellenar valores faltantes (forward/backward fill)
                values = merged['value'].fillna(method='ffill').fillna(method='bfill').values
                donor_matrix.append(values)
                donor_codes.append(country_code)
        
        if len(donor_codes) == 0:
            return None
        
        # Matriz X: países donantes (filas=años, columnas=países)
        X = np.array(donor_matrix).T
        y = target_pre['value'].values
        
        # Optimización: Minimizar ||y - X*w||² con restricciones
        def objective(w):
            return np.sum((y - X @ w) ** 2)
        
        # Restricción: suma de pesos = 1
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        
        # Límites: pesos entre 0 y 1
        bounds = [(0, 1) for _ in range(len(donor_codes))]
        
        # Inicialización: pesos uniformes
        w0 = np.ones(len(donor_codes)) / len(donor_codes)
        
        # Resolver optimización
        result = minimize(objective, w0, method='SLSQP', bounds=bounds, constraints=constraints, options={'maxiter': 1000})
        
        if result.success:
            # Filtrar pesos significativos (> 1%)
            self.weights = {code: weight for code, weight in zip(donor_codes, result.x) if weight > 0.01}
            self.donor_countries = donor_codes
            return self.weights
        else:
            return None
    
    def predict(self, donor_countries_data, years):
        """
        Genera la serie sintética para los años especificados.
        
        Args:
            donor_countries_data: Dict {country_code: DataFrame} con datos completos
            years: Array de años para predecir
        
        Returns:
            DataFrame con ['year', 'value'] del país sintético
        """
        if self.weights is None:
            return None
        
        synthetic_values = []
        
        for year in years:
            year_value = 0
            weight_sum = 0
            
            for country_code, weight in self.weights.items():
                if country_code in donor_countries_data:
                    df = donor_countries_data[country_code]
                    year_data = df[df['year'] == year]
                    
                    if not year_data.empty:
                        year_value += weight * year_data['value'].values[0]
                        weight_sum += weight
            
            # Normalizar si no todos los países tienen datos
            if weight_sum > 0:
                synthetic_values.append(year_value / weight_sum)
            else:
                synthetic_values.append(np.nan)
        
        return pd.DataFrame({'year': years, 'value': synthetic_values})
    
    def calculate_impact(self, real_data, synthetic_data):
        """
        Calcula el impacto del evento (diferencia entre real y sintético).
        
        Args:
            real_data: DataFrame del país real
            synthetic_data: DataFrame del país sintético
        
        Returns:
            DataFrame con ['year', 'real', 'synthetic', 'impact', 'phase']
        """
        merged = real_data.merge(synthetic_data, on='year', suffixes=('_real', '_synthetic'))
        merged['impact'] = merged['value_real'] - merged['value_synthetic']
        merged['phase'] = merged['year'].apply(lambda y: 'Pre-Evento' if y < self.event_year else 'Post-Evento')
        
        return merged[['year', 'value_real', 'value_synthetic', 'impact', 'phase']].rename(
            columns={'value_real': 'real', 'value_synthetic': 'synthetic'}
        )
    
    def get_weights_summary(self, etl):
        """
        Resumen legible de los pesos del modelo.
        
        Args:
            etl: Instancia de EurostatETL para nombres de países
        
        Returns:
            Lista de tuplas (nombre_país, peso) ordenada por peso descendente
        """
        if self.weights is None:
            return []
        
        summary = [(etl.get_country_name(code), weight) for code, weight in self.weights.items()]
        return sorted(summary, key=lambda x: x[1], reverse=True)
