# NPK model API

The NPK model API powers the **Soil Sensor vs. Deficiency** model in the
frontend. It is a research/simulation service; it does not read physical
sensors or actuate a fertilizer pump.

From the `NPK_Mix_Model` directory, create and activate a Python environment,
then install the dependencies and start the API:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8501
```

Alternatively, after installing the dependencies, start it from the repository
root with:

```powershell
.\NPK_Mix_Model\run_backend.bat
```

The launcher uses `NPK_Mix_Model\.venv` when present and checks that the API
dependencies are installed before starting on port 8501.

Keep the frontend running separately with `npm run dev` from `frontend`.
The frontend uses `http://127.0.0.1:8501` by default; set
`NEXT_PUBLIC_NPK_API_URL` before starting Next.js to override it.

The sensor demo endpoint is explicitly simulated. Experimental soil
calculations require user-supplied conversion coefficients and are marked
unverified. The DOA reference schedule is a solid-fertilizer baseline, not
a liquid-fertilizer recommendation.
