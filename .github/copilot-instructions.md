# Copilot Instructions - Encuesta Satisfacción Clientes Chile

## Project Overview

This is a **Streamlit** application that visualizes and analyzes customer satisfaction survey results for Chilean educational institutions (schools and colleges). The app is deployed at: https://sitio-encuestas-alexia-cl.streamlit.app/

**Key Technologies:**
- Python 3.12+
- Streamlit for web interface version 1.48.1
- Pandas for data manipulation
- Plotly for interactive visualizations
- Data loaded from remote CSV (GitHub raw URL)

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app locally
streamlit run app.py
```

The app requires a password stored in `.streamlit/secrets.toml` (not committed to git):
```toml
password = "your-password-here"
```

## Architecture

### Data Flow
1. **Data Loading**: CSV file loaded from GitHub (`https://raw.githubusercontent.com/juliorod63/DATASETS/refs/heads/main/CL_Encuesta.csv`)
2. **Data Transformation**: Raw data passes through two transformation functions:
   - `transformacion_df()` - Normalizes role names (Cargo field) using extensive pattern matching
   - `transformar_centros()` - Normalizes school names (Centro field) using extensive pattern matching
3. **Metric Calculation**: Custom functions calculate NPS and CSAT scores
4. **Visualization**: Plotly charts display distributions, correlations, and comparisons

### File Structure
- `app.py` - Main Streamlit application with all visualizations and UI logic
- `utils.py` - Data loading, transformation, and metric calculation functions
- `flag_chile.png` - Chilean flag displayed in sidebar
- `encuesta.ipynb` - Jupyter notebook (likely for data exploration/prototyping)
- `survey/` - Python virtual environment (do not modify)

### Key Metrics

**NPS (Net Promoter Score):**
- Formula: `((Promoters - Detractors) / Total) × 100`
- Promoters: score >= 9
- Detractors: score <= 6
- Two variants: NPS_Alexia (based on NPS_Recomendar) and NPS_Modulo

**CSAT (Customer Satisfaction Score):**
- Formula: `(Positive responses / Total) × 100`
- Positive: ratings of 4 or 5 out of 5
- Two variants: CSAT (based on CS_Alexia) and CSAT_Capacitacion (based on Capacitacion)

## Data Conventions

### Column Names (after transformation)
The CSV columns are renamed on load:
- `email`, `Nombre`, `Centro`, `Cargo`, `Antiguedad`, `Modulo_Usado`
- `Satisf_Modulo`, `NPS_Modulo`, `Capacitacion`
- `CS_Alexia`, `Funcionalidad_Alexia`, `Amigable_Alexia`
- `NPS_Recomendar`, `Mejoras`

### Data Normalization Patterns

**Cargo (Role) normalization:**
- Uses extensive string matching with `.str.contains(pattern, case=False)`
- Multiple spelling variations mapped to standard roles
- Roles with <= 2 occurrences grouped as "Otros"
- Standard roles: Docente, Jefe/a, Coordinador/a, Secretaria, etc.

**Centro (School) normalization:**
- Similar pattern matching to handle spelling variations and abbreviations
- School names standardized across responses (e.g., "Saint Gabriel's School" variations)
- Case-insensitive matching crucial for data quality

### Analysis Categories
The app provides several analysis views:
- Overall metrics dashboard
- NPS/CSAT distributions by role, module, seniority
- Scatter matrix and correlation analysis
- Per-school detailed analysis (with center selector)
- Radar charts for multi-metric comparison
- Violin plots for distribution analysis

## Important Notes

- **Data transformations are critical**: The normalization functions in `utils.py` handle messy real-world survey data with spelling variations and inconsistencies
- **String matching is extensive**: When modifying normalization logic, test thoroughly as changes affect all downstream metrics
- **Password protection**: App uses Streamlit secrets for access control
- **Spanish language**: All UI text, column names, and data are in Spanish
- **Remote data source**: Data loaded from external GitHub repository, not stored locally

## Common Tasks

### Adding new school/role normalizations
Add pattern matching in `transformar_centros()` or `transformacion_df()` in `utils.py`:
```python
df.loc[df["Centro"].str.contains("pattern", case=False), "Centro"] = "Standard Name"
```

### Adding new visualizations
Add Plotly charts in `app.py` after the data transformations:
```python
fig = px.histogram(df, x="column", color="grouping_var", title="Title")
st.plotly_chart(fig)
```

### Modifying metrics calculations
Update functions in `utils.py`:
- `calcular_NPS_Alexia()` / `calcular_NPS_Modulo()`
- `calcular_CSAT()` / `calcular_CSAT_Capacitacion()`
