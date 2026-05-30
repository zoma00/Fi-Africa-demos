


git@github.com:AutoHubPlatform/Products_similarity.git



🔍 Advanced Similarity Search: Find similar products from your database using configurable parameters
📤 Smart Product Upload: Upload new products with automatic duplicate detection
🧠 AI-Powered Recognition: Uses OpenAI CLIP model for accurate image embeddings
📊 Database Analytics: Real-time dashboard with product statistics and health monitoring
🎯 Multiple Distance Metrics: Cosine, Euclidean, and Inner Product similarity calculations
🆕 Latest Enhancements
Search Before Upload: Find similar products without uploading new images
Top 3 Similar Products: Always shows up to 3 most similar items (configurable 1-10)
Dynamic Similarity Thresholds: Adjustable similarity confidence levels (0.0-1.0)
Improved UI Navigation: Clean tabbed interface with dedicated sections
Smart Duplicate Prevention: Warns about existing similar products before adding
Enhanced Database Viewer: Fixed vector compatibility issues with pgvector
## Architecture

<img src="./docs/architecture.svg" alt="Product similarity architecture diagram" width="100%">

The application runs as a Streamlit interface backed by PostgreSQL with pgvector. Product images are processed into OpenAI CLIP embeddings, stored in the vector database, and queried through configurable similarity search.
🛠️ Technology Stack
Frontend: Streamlit (Python web framework)
Database: PostgreSQL 15 with pgvector extension
AI Model: OpenAI CLIP for image embeddings
Vector Search: pgvector for efficient similarity search
Containerization: Docker & Docker Compose
Image Processing: PIL (Python Imaging Library)
📋 Prerequisites
Docker and Docker Compose
OpenAI API key
Minimum 4GB RAM
10GB free disk space
🚀 Quick Start
1. Clone the Repository
git clone <repository-url>
cd image-matcher
2. Environment Setup
# Copy environment template
cp .env.example .env

# Edit with your OpenAI API key
nano .env
Add your OpenAI API key:

OPENAI_API_KEY=your_openai_api_key_here
3. Deploy with Docker Compose
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
4. Access the Application
Streamlit App: http://127.0.0.1:8501/
PgAdmin4: http://localhost:5050 (if configured)
🎯 How to Use
🔍 Search Similar Products (New Feature)
Navigate to the "Search Similar Products from Database" section
Select any existing product from the dropdown
Adjust similarity parameters:
Similarity Threshold: 0.0 (most lenient) to 1.0 (most strict)
Number of Results: 1-10 similar products to display
Click "🔎 Find Similar Products"
View results with confidence scores and product details
📤 Upload New Products
Go to the "Upload New Product" section
Choose an image file (PNG, JPG, JPEG, WebP)
Click "🔄 Process Image"
System automatically checks for similar existing products
If duplicates found, decide whether to proceed
Enter barcode and product name=
📊 Database Analytics
View real-time statistics
Monitor database health
Browse all products with embeddings
Track daily additions
⚙️ Configuration
Similarity Search Parameters
Parameter	Range	Description
Similarity Threshold	0.0 - 1.0	Minimum confidence level for matches
Top K Results	1 - 10	Number of similar products to return
Distance Metric	cosine/euclidean/inner_product	Algorithm for similarity calculation
Distance Metrics Explained
Cosine: Best for general visual similarity
Euclidean: Best for exact feature matching
Inner Product: Best for semantic similarity
🗄️ Database Schema
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(255) UNIQUE NOT NULL,
    product_name VARCHAR(255),
    image_path VARCHAR(255),
    embedding vector(512),  -- OpenAI CLIP embeddings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optimized indexes for vector search
CREATE INDEX ON products USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON products USING ivfflat (embedding vector_l2_ops);
🐳 Docker Services
Service	Port	Description
app	8501	Streamlit application
db	5433	PostgreSQL with pgvector
pgadmin	5050	Database administration (optional)
🔧 Development
Local Development Setup
# Install Python dependencies
pip install -r app/requirements.txt

# Set environment variables
export OPENAI_API_KEY="your_key_here"
export DATABASE_URL="postgresql://user:pass@localhost:5433/products_db"

# Run Streamlit locally
cd app
streamlit run streamlit_app.py
Container Management
# Restart specific service
docker-compose restart app

# View logs
docker-compose logs -f app

# Rebuild after code changes
docker-compose up --build -d

# Clean reset
docker-compose down
docker-compose up -d
🚨 Troubleshooting
Common Issues
1. "function array_length(vector, integer) does not exist"

✅ Fixed: Updated to use proper pgvector functions
2. "'str' object has no attribute 'tolist'"

✅ Fixed: Enhanced embedding format handling for database retrieval
3. "Only 1 match found instead of Top 3"

✅ Fixed: Improved similarity search to always return top K results
4. Port conflicts (5050 already in use)

# Check what's using the port
sudo lsof -i :5050

# Use different port in docker-compose.yml
ports:
  - "5051:80"  # Change 5050 to 5051
Performance Tips
Database: Ensure proper vector indexes are created
Memory: Allocate sufficient RAM for CLIP model
Storage: Monitor disk space for uploaded images
API Limits: Monitor OpenAI API usage and rate limits
📊 Performance Metrics
Search Speed: < 100ms for similarity queries
Upload Processing: 2-5 seconds per image
Database Capacity: Millions of products with proper indexing
Concurrent Users: 10+ simultaneous users supported
🔐 Security
API keys stored in environment variables
Database credentials in Docker secrets
Image uploads validated and sanitized
SQL injection protection with parameterized queries
📈 Roadmap
 Batch image processing
 Advanced filtering (category, price range)
 REST API endpoints
 Multi-language support
 Mobile app integration
 Advanced analytics dashboard
🤝 Contributing
Fork the repository
Create a feature branch
Make your changes
Add tests if applicable
Submit a pull request
📄 License
View the full license here: MIT LICENSE

📞 Support
For issues and questions:

Check the troubleshooting section
Review container logs: docker-compose logs
Create an issue in the repository
Phone: +20 1096401022
Email: zoma0097@gmail.com
🔬 Powered by OpenAI CLIP for advanced image similarity search

Last Updated: July 2025 - Enhanced with advanced similarity search and improved UI

Monica
Monica
Repo Summary
Supports the most advanced models to help you quickly understand the contents of the repo
About
An advanced AI-powered product recognition and similarity search system using OpenAI CLIP embeddings and PostgreSQL with pgvector for efficient vector similarity search.

Resources
 Readme
License
 MIT license
 Activity
 Custom properties
Stars
 0 stars
Watchers
 0 watching
Forks
 0 forks
 Audit log
Report repository
Releases
No releases published
Create a new release
Packages
No packages published
Publish your first package
Contributors
2
@zoma00
zoma00 Hazem Adel Elbatawy
@AmirI-146
AmirI-146
Languages
Python
75.1%
 
Shell
23.7%
 
Dockerfile
1.2%
Suggested workflows
Based on your tech stack
SLSA Generic generator logo
SLSA Generic generator
Generate SLSA3 provenance for your existing release workflows
Python Package using Anaconda logo
Python Package using Anaconda
Create and test a Python package on multiple Python versions using Anaconda for package management.
Python package logo
Python package
Create and test a Python package on multiple Python versions.
More workflows
Footer
© 2026 GitHub, Inc.
Footer navigation
Terms
