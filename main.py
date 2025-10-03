from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn


import shutil
import os

from ingestion_agent import ingestion_agent
from imaging_agent import imaging_agent
from therapy_agent import TherapyAgent
from pharmacy_match_agent import PharmacyMatchAgent
from orchestrator import CoordinatorAgent

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


therapy_agent = TherapyAgent()
pharmacy_agent = PharmacyMatchAgent()
coordinator = CoordinatorAgent()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
async def upload_files(
    request: Request,
    xray_file: UploadFile = File(...),
    pdf_file: UploadFile = File(None)
):
    # Save uploaded X-ray
    xray_path = os.path.join(UPLOAD_FOLDER, xray_file.filename)
    with open(xray_path, "wb") as buffer:
        shutil.copyfileobj(xray_file.file, buffer)

    # Save uploaded PDF if exists
    pdf_path = None
    if pdf_file:
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(pdf_file.file, buffer)

    # Run all agents
    ingestion_output = ingestion_agent(xray_path, pdf_path)
    imaging_output = imaging_agent(ingestion_output["xray_path"])
    therapy_output = therapy_agent.recommend(imaging_output["condition_probs"], ingestion_output["patient"])

    # Pharmacy match for first OTC option
    pharmacy_output = None
    if therapy_output["otc_options"]:
        pharmacies = pharmacy_agent.load_pharmacies("./data/pharmacies.json")
        inventory = pharmacy_agent.load_inventory("./data/inventory.csv")
        sku = therapy_output["otc_options"][0]["sku"]
        pharmacy_output = pharmacy_agent.find_pharmacy_with_stock(sku, pharmacies, inventory)

    # Consolidate final plan
    final_plan = coordinator.consolidate(imaging_output, therapy_output, ingestion_output["notes"])

    # Render result page with checkout option
    return templates.TemplateResponse("result.html", {
        "request": request,
        "ingestion": ingestion_output,
        "imaging": imaging_output,
        "therapy": therapy_output,
        "pharmacy": pharmacy_output,
        "final": final_plan
    })


@app.post("/checkout")
def checkout():
    # Mock order placement
    return {"message": "Mock order placed successfully!"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render sets PORT dynamically
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
