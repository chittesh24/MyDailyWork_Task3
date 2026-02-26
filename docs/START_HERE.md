# 🚀 START HERE - Image Captioning System

**Welcome!** This guide gets you up and running in 5 minutes.

---

## ⚡ Fastest Way to Deploy (3 Commands)

```bash
# 1. Quick setup (generates config)
python3 scripts/quick_setup.py

# 2. One-click deploy (starts everything)
bash scripts/one_click_deploy.sh

# 3. Open your browser
open http://localhost:3000
```

**That's it!** 🎉 You now have a fully functional image captioning system.

---

## 📋 What Just Happened?

The one-click deploy:
1. ✅ Validated your project structure
2. ✅ Generated secure environment variables
3. ✅ Built Docker containers
4. ✅ Started 3 services (Database, Backend, Frontend)
5. ✅ Initialized the database
6. ✅ Verified all services are healthy

---

## 🎯 Next Steps

### 1. Create an Account

1. Visit http://localhost:3000
2. Click "Register"
3. Enter email and password (min 8 chars)
4. Click "Create Account"

### 2. Generate API Key

1. Login with your credentials
2. Go to Dashboard
3. Click "Generate New Key"
4. **Copy and save the key** (shown only once!)

### 3. Generate Your First Caption

1. Go back to Home page
2. Drag and drop an image (or click to upload)
3. Wait ~500ms (CPU) or ~100ms (GPU)
4. See your AI-generated caption! ✨

### 4. Customize Your Experience

1. Visit http://localhost:3000/settings
2. Choose from 6 color themes
3. Adjust font size and animations
4. Save preferences

---

## 🤖 Train Your Own Model (Optional)

### Quick Training (Flickr8k - 2 hours on GPU)

```bash
bash scripts/train_flickr8k.sh
```

This will:
- Download Flickr8k dataset (~1GB)
- Build vocabulary
- Train model for 10 epochs
- Save best checkpoint to `checkpoints/flickr8k/`

### Full Training (MS COCO - 1-2 days on GPU)

```bash
bash scripts/train_coco.sh
```

This will:
- Download MS COCO dataset (~19GB)
- Build vocabulary (30K+ words)
- Train model for 20 epochs
- Save best checkpoint to `checkpoints/coco/`

### Use Pre-trained Model

```bash
# Download from HuggingFace or Google Drive
# Place in backend/checkpoints/
mkdir -p backend/checkpoints
# Add: best_model.pth and vocab.json
```

---

## ☁️ Deploy to Cloud (Free $0/month)

### Automated Cloud Deployment

```bash
python scripts/setup_free_tier.py
```

This interactive wizard will:
1. Guide you through Supabase setup (Database)
2. Deploy backend to Render.com
3. Deploy frontend to Vercel
4. Configure CORS automatically
5. Generate deployment summary

**Free Tier Stack:**
- ✅ Supabase (500MB database)
- ✅ Render (750 hrs/month backend)
- ✅ Vercel (unlimited frontend)
- ✅ **Total: $0/month**

---

## 🔧 Useful Commands

### Service Management

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build

# Check service health
bash scripts/health_check.sh
```

### Validation

```bash
# Validate entire project
python3 scripts/validate_project.py

# Test Python imports
python3 scripts/test_imports.py

# Check all services
bash scripts/health_check.sh
```

### Model Tools

```bash
# Compare multiple models
python scripts/compare_models.py \
  --models model1.pth model2.pth \
  --vocabs vocab1.json vocab2.json \
  --names "Model1" "Model2" \
  --test_images test/*.jpg

# Benchmark single model
python scripts/benchmark.py \
  --model best_model.pth \
  --vocab vocab.json \
  --image test.jpg
```

---

## 📚 Documentation

- **[INSTALL.md](INSTALL.md)** - Complete installation guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start tutorial
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Deployment instructions
- **[DEPLOYMENT_READY.md](DEPLOYMENT_READY.md)** - Pre-deployment checklist
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete features
- **[UPDATES.md](UPDATES.md)** - Latest changes
- **[TEST_RESULTS.md](TEST_RESULTS.md)** - Test validation report

---

## 🆘 Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker ps

# View error logs
docker-compose logs backend
docker-compose logs frontend

# Restart everything
docker-compose down
docker-compose up -d
```

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Kill the process
kill -9 <PID>
```

### Can't Access Frontend

```bash
# Check frontend is running
curl http://localhost:3000

# Check backend is accessible
curl http://localhost:8000

# Restart frontend
docker-compose restart frontend
```

### Database Connection Error

```bash
# Check database is running
docker-compose exec db pg_isready -U postgres

# Restart database
docker-compose restart db

# Reinitialize database
docker-compose down -v
docker-compose up -d
```

---

## ✅ Success Checklist

Your deployment is successful when:

- [ ] Frontend loads at http://localhost:3000
- [ ] Backend responds at http://localhost:8000
- [ ] Can register new user
- [ ] Can login successfully
- [ ] Can generate API key in dashboard
- [ ] Can upload image and get caption
- [ ] All services show "Healthy" in health check

---

## 🎯 What You Get

After this quick start, you have:

✅ **Full-Stack Application**
- Modern Next.js frontend
- FastAPI backend
- PostgreSQL database

✅ **AI Model**
- CNN + Transformer architecture
- Beam search decoding
- Production-ready inference

✅ **Security**
- JWT authentication
- API key management
- Rate limiting
- Input validation

✅ **Automation**
- One-click deployment
- Training scripts
- Model comparison tools
- Health monitoring

✅ **Documentation**
- 10 comprehensive guides
- API documentation
- Troubleshooting help

---

## 💡 Pro Tips

1. **Development Workflow:**
   ```bash
   # Make code changes
   # Rebuild specific service
   docker-compose up -d --build backend
   ```

2. **Monitor Logs:**
   ```bash
   # Follow all logs
   docker-compose logs -f
   
   # Follow specific service
   docker-compose logs -f backend
   ```

3. **Database Access:**
   ```bash
   # Connect to database
   docker-compose exec db psql -U postgres -d image_captions
   ```

4. **Performance:**
   - CPU inference: ~500ms per caption
   - GPU inference: ~100ms per caption
   - Use quantization for 2-4x CPU speedup

---

## 🚀 Ready to Go!

You're all set! Here's what to do:

1. ✅ **Visit** http://localhost:3000
2. ✅ **Register** a new account
3. ✅ **Upload** an image
4. ✅ **Get** AI-generated captions!

**Enjoy your image captioning system!** 🎉

---

## 📞 Need Help?

1. Check [INSTALL.md](INSTALL.md) for detailed installation
2. Read [DEPLOYMENT_READY.md](DEPLOYMENT_READY.md) for troubleshooting
3. Run `python scripts/validate_project.py` for diagnostics
4. Check `docker-compose logs -f` for error messages

**Happy captioning!** ✨
