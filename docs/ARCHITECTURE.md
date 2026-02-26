# Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Web Browser │  │ Mobile App   │  │  API Client  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │               │
│         └─────────────────┴──────────────────┘               │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   Load Balancer │
                    │   (nginx/ALB)   │
                    └───────┬────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼────────┐                   ┌─────────▼──────────┐
│  Next.js       │                   │   FastAPI          │
│  Frontend      │◄─────────────────►│   Backend          │
│  (Port 3000)   │     REST API      │   (Port 8000)      │
└────────────────┘                   └─────────┬──────────┘
                                               │
                    ┌──────────────────────────┼────────────────┐
                    │                          │                │
            ┌───────▼────────┐        ┌───────▼────┐   ┌──────▼──────┐
            │  PostgreSQL    │        │  Model     │   │  File       │
            │  Database      │        │  Inference │   │  Storage    │
            └────────────────┘        └────────────┘   └─────────────┘
```

## Model Architecture

### CNN + Transformer

```
Input Image (3, 224, 224)
    │
    ▼
┌─────────────────────────────┐
│  ResNet50 Encoder           │
│  - Pretrained on ImageNet   │
│  - Remove FC layers         │
│  - Keep conv layers         │
└─────────────┬───────────────┘
              │
    Feature Maps (2048, 7, 7)
              │
              ▼
┌─────────────────────────────┐
│  Linear Projection          │
│  Conv2d(2048 → 512)         │
└─────────────┬───────────────┘
              │
    Embeddings (512, 49)
              │
              ▼
┌─────────────────────────────┐
│  Transformer Decoder        │
│  - 6 layers                 │
│  - 8 attention heads        │
│  - Masked self-attention    │
│  - Cross-attention to image │
└─────────────┬───────────────┘
              │
    Logits (vocab_size, seq_len)
              │
              ▼
┌─────────────────────────────┐
│  Beam Search / Greedy       │
│  - Beam width: 5            │
│  - Temperature: 1.0         │
└─────────────┬───────────────┘
              │
              ▼
    Generated Caption Text
```

### Baseline (LSTM + Attention)

```
Input Image
    │
    ▼
ResNet50 Encoder
    │
    ▼
Spatial Features (2048, 7, 7)
    │
    ▼
Flatten → (49, 2048)
    │
    ▼
┌─────────────────────────────┐
│  LSTM Decoder + Bahdanau    │
│  Attention                  │
│  - Hidden dim: 512          │
│  - Teacher forcing          │
└─────────────┬───────────────┘
              │
              ▼
    Generated Caption
```

## Database Schema

```sql
users
├── id (PK)
├── email (UNIQUE)
├── password_hash
└── created_at

api_keys
├── id (PK)
├── user_id (FK → users.id)
├── hashed_key (UNIQUE)
├── name
├── created_at
├── last_used
└── is_active

captions
├── id (PK)
├── user_id (FK → users.id)
├── image_path
├── generated_caption
├── model_version
├── confidence_score
├── inference_time_ms
└── timestamp

usage
├── id (PK)
├── user_id (FK → users.id, UNIQUE)
├── daily_request_count
├── total_requests
└── last_reset
```

## API Flow

### Authentication Flow

```
1. User Registration
   POST /auth/register
   ├── Validate email format
   ├── Hash password (bcrypt)
   ├── Create user record
   ├── Create usage record
   └── Return JWT token

2. User Login
   POST /auth/login
   ├── Verify credentials
   ├── Generate JWT token
   └── Return token

3. API Key Generation
   POST /api-keys/generate
   ├── Verify JWT token
   ├── Generate random key
   ├── Hash key (SHA-256)
   ├── Store hashed key
   └── Return original key (once)
```

### Caption Generation Flow

```
1. Image Upload
   POST /caption
   ├── Verify API key
   ├── Check rate limit
   ├── Validate file
   │   ├── Size ≤ 5MB
   │   ├── MIME type (jpeg/png)
   │   └── Valid image format
   ├── Save file temporarily
   └── Process

2. Inference
   ├── Load image
   ├── Preprocess
   │   ├── Resize (224x224)
   │   ├── Normalize
   │   └── Convert to tensor
   ├── Encode (ResNet50)
   ├── Decode (Transformer)
   │   ├── Beam search
   │   └── Top-k sampling
   ├── Decode tokens
   └── Return caption

3. Storage
   ├── Save to database
   ├── Update usage stats
   └── Clean up temp file
```

## Security Architecture

### Authentication & Authorization

```
JWT Token Flow:
1. User logs in → Server generates JWT
2. JWT contains: user_id, expiry
3. Signed with SECRET_KEY (HS256)
4. Client stores in HTTP-only cookie
5. Each request includes token
6. Server validates signature & expiry

API Key Flow:
1. User generates key → Random 32-byte string
2. Server hashes with SHA-256
3. Original key shown once
4. Future requests: hash incoming key
5. Compare hashed values
```

### Rate Limiting

```python
RateLimiter:
  - In-memory storage (user_id → [timestamps])
  - Window: 60 seconds
  - Max requests: 10
  - Algorithm: Sliding window
  - Cleanup: Remove old timestamps
```

### Input Validation

```
File Upload:
├── Server-side only
├── Max size: 5MB
├── Allowed types: JPEG, PNG
├── MIME type check
├── Image format verification (PIL)
└── Malicious file rejection

Text Input:
├── SQL injection prevention (ORM)
├── XSS prevention (sanitization)
└── Length limits
```

## Training Pipeline

```
1. Data Loading
   ├── Load images from disk
   ├── Load captions from JSON/CSV
   ├── Create vocabulary
   │   ├── Tokenize captions
   │   ├── Build word→index mapping
   │   └── Filter low-frequency words
   └── Create DataLoader

2. Training Loop
   for epoch in epochs:
     for batch in train_loader:
       ├── Load images & captions
       ├── Forward pass
       │   ├── Encode images
       │   ├── Decode with teacher forcing
       │   └── Compute loss
       ├── Backward pass
       │   ├── Compute gradients
       │   ├── Clip gradients
       │   └── Update weights
       └── Log metrics
     
     ├── Validation
     │   ├── Compute loss
     │   ├── Generate captions
     │   └── Compute metrics (BLEU, METEOR)
     └── Save checkpoint

3. Evaluation Metrics
   ├── BLEU-1, BLEU-4
   ├── METEOR
   ├── ROUGE-L
   └── CIDEr (optional)
```

## Inference Optimization

### TorchScript

```python
# JIT compilation
scripted_model = torch.jit.script(model)
torch.jit.save(scripted_model, 'model.pt')

# 15-30% speedup
# Portable across Python versions
```

### ONNX

```python
# Export to ONNX
torch.onnx.export(
    model, 
    dummy_input, 
    'model.onnx',
    opset_version=14
)

# Use ONNX Runtime
import onnxruntime
session = onnxruntime.InferenceSession('model.onnx')
```

### Quantization

```python
# Dynamic quantization
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {nn.Linear},
    dtype=torch.qint8
)

# 2-4x speedup on CPU
# 50-75% size reduction
```

## Deployment Patterns

### Single Server

```
Server (EC2 t2.medium)
├── Docker Compose
├── PostgreSQL (container)
├── Backend (container)
└── Frontend (container)

Pros: Simple, low cost
Cons: Single point of failure
```

### Microservices

```
├── Frontend (Vercel)
├── Backend (Render/EC2)
│   ├── API service
│   └── Worker service (async)
├── Database (RDS)
└── Storage (S3)

Pros: Scalable, resilient
Cons: Complex, higher cost
```

### Serverless

```
├── Frontend (Vercel/Netlify)
├── API (AWS Lambda + API Gateway)
├── Database (Aurora Serverless)
└── Model (SageMaker Endpoint)

Pros: Auto-scaling, pay-per-use
Cons: Cold starts, vendor lock-in
```

## Monitoring & Observability

```
Metrics Collection:
├── Request latency
├── Error rates
├── API key usage
├── Model inference time
└── Database query time

Logging:
├── Application logs (loguru)
├── Access logs (nginx)
├── Error tracking (Sentry)
└── Audit logs (database)

Alerting:
├── High error rate
├── Slow response time
├── Database connection issues
└── Disk space low
```

## Scalability Considerations

### Horizontal Scaling

```
Load Balancer
    │
    ├─► Backend Instance 1
    ├─► Backend Instance 2
    └─► Backend Instance 3
         │
         └─► Shared Database + Cache
```

### Caching Strategy

```
Level 1: Application cache (in-memory)
  - Vocabulary
  - Model weights
  
Level 2: Redis cache
  - API responses
  - User sessions
  
Level 3: CDN
  - Static assets
  - Images
```

### Database Optimization

```
Indexes:
  - users.email
  - api_keys.hashed_key
  - captions.user_id
  - captions.timestamp

Partitioning:
  - Partition captions by date

Connection Pooling:
  - Pool size: 10
  - Max overflow: 20
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14, TypeScript, TailwindCSS | Modern React framework |
| Backend | FastAPI, Python 3.11 | High-performance API |
| ML Framework | PyTorch 2.1 | Model training & inference |
| Database | PostgreSQL 15 | Relational data storage |
| Authentication | JWT, bcrypt | Secure auth |
| Containerization | Docker, Docker Compose | Consistent deployment |
| Monitoring | Loguru, Prometheus | Observability |
| Training Tools | Custom scripts (Bash/Python) | Automated training |
| Deployment | Render, Vercel, Supabase | Free tier hosting |
| Comparison | Custom benchmarking scripts | Model evaluation |

## New Automation Tools

### Training Automation
- **train_coco.sh**: Automated MS COCO training pipeline
- **train_flickr8k.sh**: Automated Flickr8k training pipeline  
- **train_coco.py**: Cross-platform Python training script
- Features: Dataset download, vocabulary building, model training

### Performance Analysis
- **compare_models.py**: Multi-model comparison tool
- **benchmark.py**: Single model benchmarking
- Metrics: Speed (greedy/beam), memory usage, BLEU scores
- Output: JSON results and formatted tables

### Deployment Automation
- **setup_free_tier.py**: Interactive deployment wizard
- **deploy_render.sh**: Backend deployment to Render
- **deploy_vercel.sh**: Frontend deployment to Vercel
- **deploy_supabase.sh**: Database setup guide
- Total cost: $0/month with free tiers

---

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Inference Time (GPU) | ~50-100ms |
| Inference Time (CPU) | ~200-500ms |
| API Response Time | ~150-600ms |
| Model Size | ~100MB |
| Memory Usage | ~2GB (GPU), ~1GB (CPU) |
| Throughput | ~20 req/s (single GPU) |
