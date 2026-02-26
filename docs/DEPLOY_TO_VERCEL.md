# Quick Deploy to Vercel - Optimized Setup

## 🚀 One-Command Deployment

### Step 1: Prepare Your Project

```bash
# Navigate to project directory
cd image_captioning_system

# Use optimized configuration
cp vercel_optimized.json vercel.json
cp backend/requirements_optimized.txt backend/requirements.txt
```

### Step 2: Install Vercel CLI (if not already installed)

```bash
npm install -g vercel
```

### Step 3: Deploy

```bash
# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

## ⚙️ Environment Variables Setup

Set these in your Vercel Dashboard (Settings → Environment Variables):

### Required Variables
```env
SECRET_KEY=your_random_secret_key_here_min_32_chars
DATABASE_URL=sqlite:///./local.db
```

### Optional Variables (with defaults)
```env
DEVICE=cpu
MODEL_NAME=Salesforce/blip-image-captioning-base
PRELOAD_MODEL=false
ALLOWED_ORIGINS=*
TRANSFORMERS_CACHE=/tmp/transformers_cache
```

## 🧪 Test Your Deployment

### 1. Health Check
```bash
curl https://your-app.vercel.app/health
```

### 2. Test Caption Generation
```bash
curl -X POST https://your-app.vercel.app/demo/caption \
  -F "file=@test_images/sample.jpg" \
  -F "method=beam_search" \
  -F "beam_width=3"
```

Expected Response:
```json
{
  "caption": "a dog sitting on a beach",
  "inference_time_ms": 450.23,
  "model_version": "Salesforce/blip-image-captioning-base-optimized",
  "method": "beam_search"
}
```

## 📊 Performance Benchmarks

Run these tests to verify optimization:

### Fast Mode (Recommended)
```bash
time curl -X POST https://your-app.vercel.app/demo/caption \
  -F "file=@test.jpg" \
  -F "beam_width=3" \
  -F "method=beam_search"
```
**Expected**: 200-500ms

### Greedy Mode (Fastest)
```bash
time curl -X POST https://your-app.vercel.app/demo/caption \
  -F "file=@test.jpg" \
  -F "method=greedy"
```
**Expected**: 150-300ms

## 🔧 Troubleshooting

### Issue: Deployment Failed
```bash
# Check logs
vercel logs your-deployment-url --follow

# Common fixes:
1. Verify requirements_optimized.txt is used
2. Check vercel.json syntax
3. Ensure Python 3.11 is specified
```

### Issue: Function Timeout
```bash
# Reduce complexity in vercel.json:
{
  "functions": {
    "backend/api/optimized_main.py": {
      "memory": 3008,
      "maxDuration": 30  // Increase if needed
    }
  }
}
```

### Issue: Out of Memory
```bash
# Use smaller beam width
curl -F "beam_width=2"  # Instead of 3

# Or use greedy
curl -F "method=greedy"
```

## ✅ Post-Deployment Checklist

- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Demo endpoint generates captions
- [ ] Inference time < 1000ms on average
- [ ] No timeout errors
- [ ] Memory usage < 2GB
- [ ] CORS configured correctly for your frontend

## 🎯 Next Steps

1. **Update Frontend**: Point your frontend to the new Vercel URL
2. **Monitor Performance**: Use Vercel Analytics
3. **Set Up Alerts**: Configure error notifications
4. **Scale**: Upgrade to Vercel Pro if needed for better performance

---

For detailed optimization info, see [OPTIMIZATION_GUIDE.md](./OPTIMIZATION_GUIDE.md)
