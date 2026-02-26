"""
Vercel entry point for the optimized image captioning API.
This file is used as the serverless function handler.
"""
from api.optimized_main import app

# Vercel uses this for serverless functions
handler = app
