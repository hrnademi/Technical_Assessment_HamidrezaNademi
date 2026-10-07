# Run the dashboard

## Locally
```
pip install -r requirements.txt
streamlit run dashboard_app.py
```
Open http://localhost:8501. The app reads `dashboard_data.db` from the same folder.

## Live link (Streamlit Community Cloud)
1. Push this repository to GitHub (the app, `dashboard_data.db` and `requirements.txt` are committed; the raw dataset is not).
2. On https://share.streamlit.io choose **New app**, pick the repository and branch.
3. Main file path: `app/dashboard_app.py`.
4. If the dependencies are not detected, copy `requirements.txt` to the repository root.
5. Deploy. No secrets are needed. The Pricing tab needs the pricing tables, which `part4_pricing.ipynb` adds to `dashboard_data.db` (commit the updated database).

## Rebuild the data / app
Run `notebooks/part3_dashboard.ipynb` top to bottom (needs the Part 1 and Part 2 outputs).
