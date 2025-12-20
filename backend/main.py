from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scraper.brainyquote_scraper import scrape_quotes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/scrape")
def scrape(topic: str):
    data = scrape_quotes(topic)
    return {
        "count": len(data),
        "data": data
    }
