# Run the dashboard (v1.0)

## Locally
```
pip install -r requirements.txt
streamlit run dashboard_app_v1.0.py
```
Open http://localhost:8501. The app reads `dashboard_data_v1.0.db` from the same folder.

## Live link (Streamlit Community Cloud)
1. Push this repository to GitHub (the app, `dashboard_data_v1.0.db` and `requirements.txt` are committed; the raw dataset is not).
2. On https://share.streamlit.io choose **New app**, pick the repository and branch.
3. Main file path: `part3_dashboard_v1.0/dashboard_app_v1.0.py`.
4. If the dependencies are not detected, copy `requirements.txt` to the repository root.
5. Deploy. No secrets are needed.

## Rebuild the data / app
Run `part3_dashboard_v1.0.ipynb` top to bottom (needs the Part 1 and Part 2 outputs).
