#!/usr/bin/env python3
"""
Stock Photo Marketplace - 自动赚钱项目
出售高质量照片、插图、视频素材
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Stock Photo Marketplace", version="1.0.0")

DB_PATH = Path.home() / "桌面" / "stock-photo-marketplace" / "photos.db"
DB_PATH.parent.mkdir(exist_ok=True)

class Photo(BaseModel):
    title: str
    category: str
    price: float
    tags: List[str] = []

class Purchase(BaseModel):
    photo_id: int
    email: str
    license_type: str = "standard"

@app.get("/")
async def root():
    return {
        "message": "Stock Photo Marketplace - 自动赚钱",
        "version": "1.0.0",
        "categories": ["Business", "Nature", "Technology", "People", "Abstract"]
    }

@app.post("/upload")
async def upload_photo(photo: Photo):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO photos (title, category, price, tags) VALUES (?, ?, ?, ?)",
        (photo.title, photo.category, photo.price, ",".join(photo.tags))
    )
    conn.commit()
    conn.close()
    return {"message": "Photo uploaded", "photo_id": 1}

@app.post("/purchase")
async def purchase_photo(purchase: Purchase):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM photos WHERE id = ?", (purchase.photo_id,))
    photo = cursor.fetchone()
    if not photo:
        conn.close()
        return {"error": "Photo not found"}
    
    # 应用折扣
    if purchase.license_type == "exclusive":
        price = photo[0] * 3
    else:
        price = photo[0]
    
    cursor.execute(
        "INSERT INTO purchases (photo_id, email, amount) VALUES (?, ?, ?)",
        (purchase.photo_id, purchase.email, price)
    )
    conn.commit()
    conn.close()
    
    return {"message": "Purchase successful", "amount": price}

@app.get("/stats")
async def stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM photos")
    total_photos = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(amount) FROM purchases")
    total_revenue = cursor.fetchone()[0] or 0
    conn.close()
    return {
        "total_photos": total_photos,
        "total_revenue": total_revenue,
        "monthly_revenue": total_revenue * 12
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
