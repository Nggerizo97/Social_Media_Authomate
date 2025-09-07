# Social Media Automation System

🚀 **COMPLETE 4-PHASE SOCIAL MEDIA AUTOMATION ARCHITECTURE** 🚀

A comprehensive, production-ready system for automated content posting across Facebook, Instagram, TikTok, and YouTube platforms with built-in content policy validation and intelligent file management.

## ✅ Implementation Status

**ALL 4 PHASES COMPLETED SUCCESSFULLY**

- ✅ **Phase 1**: Architecture & Configuration
- ✅ **Phase 2**: Content Policy Checker Module  
- ✅ **Phase 3**: Social Media Connectors
- ✅ **Phase 4**: Main Orchestration System

## 🏗️ System Architecture

```
Social_Media_Authomate/
├── src/
│   ├── connectors/              # Platform-specific modules
│   │   ├── facebook_poster.py   # Facebook Graph API integration
│   │   ├── youtube_uploader.py  # YouTube Data API integration
│   │   ├── instagram_poster.py  # Instagram Selenium automation
│   │   └── tiktok_poster.py     # TikTok Selenium automation
│   │
│   ├── utils/                   # Core utilities
│   │   ├── policy_checker.py    # Content compliance validation
│   │   └── logger.py           # Comprehensive logging system
│   │
│   ├── main.py                 # Main orchestration workflow
│   └── prompt_social.py        # AI image generation (existing)
│
├── media/
│   ├── input/                  # Files ready for processing
│   ├── processed/              # Successfully posted content
│   └── quarantine/             # Policy-violating content
│
├── logs/
│   └── app.log                 # Application logs
│
├── config.ini                  # System configuration
├── .env.template              # Environment variables template
└── requirements.txt           # Python dependencies
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone repository
git clone https://github.com/Nggerizo97/Social_Media_Authomate.git
cd Social_Media_Authomate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.template .env
```

### 2. Configure Credentials

Edit `.env` file with your API credentials:

```bash
# Facebook Graph API
FB_APP_ID=your_facebook_app_id
FB_APP_SECRET=your_facebook_app_secret
FB_ACCESS_TOKEN=your_facebook_access_token
FB_PAGE_ID=your_facebook_page_id

# YouTube Data API
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret

# Instagram (Selenium)
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

# TikTok (Selenium)
TIKTOK_USERNAME=your_tiktok_username
TIKTOK_PASSWORD=your_tiktok_password
```

### 3. Prepare Content

```bash
# Add media files to input directory
cp your_video.mp4 media/input/
echo "Amazing content! #hashtag" > media/input/your_video.txt
```

### 4. Run Automation

```bash
python src/main.py
```

## 🔧 Core Features

### 📋 Content Policy Validation
- **Banned Keywords Detection**: Configurable keyword filtering
- **File Format Validation**: Support for videos (mp4, mov, avi, mkv) and images (jpg, png, gif)
- **File Size Limits**: Configurable size restrictions per platform
- **Automatic Quarantine**: Non-compliant content moved to quarantine with detailed logs

### 🌐 Multi-Platform Publishing

#### Facebook (Graph API)
- Photo and video posting via Graph API v18.0
- Automatic content type detection
- Full metadata support

#### YouTube (YouTube Data API)
- Video uploads with metadata
- OAuth 2.0 authentication
- Resumable uploads for large files
- Privacy settings configuration

#### Instagram (Selenium)
- Automated browser-based posting
- Photo and video support
- Login automation
- Headless mode for servers

#### TikTok (Selenium)
- Video upload automation
- Advanced anti-detection measures
- Caption and metadata support
- Upload progress monitoring

### 📊 Intelligent File Management
- **Input Processing**: Automatic scanning of input directory
- **Success Handling**: Successful posts moved to processed directory
- **Failure Handling**: Policy violations moved to quarantine
- **Audit Trail**: Complete logging of all operations

### 🔍 Comprehensive Logging
- File-based logging with configurable levels
- Real-time console output
- Detailed operation tracking
- Policy violation reporting

## 🎯 Usage Examples

### Basic Workflow
```bash
# 1. Add content
echo "Check out this sunset! 🌅" > media/input/sunset.txt
cp sunset.mp4 media/input/

# 2. Run automation
python src/main.py

# 3. Check results
ls media/processed/  # Successfully posted content
ls media/quarantine/ # Policy violations
cat logs/app.log     # Detailed logs
```

### Policy Testing
```bash
# Create content with banned keyword
echo "This contains violencia content" > media/input/bad_content.txt
cp video.mp4 media/input/bad_content.mp4

# Run system - content will be quarantined
python src/main.py
```

## ⚙️ Configuration

### Policy Settings (config.ini)
```ini
[POLICIES]
banned_keywords = violencia,odio,discurso de odio,contenido sexual,drogas
max_file_size_mb = 100
allowed_video_formats = mp4,mov,avi,mkv
allowed_image_formats = jpg,jpeg,png,gif
```

### Platform Settings
```ini
[SELENIUM]
headless_mode = true
implicit_wait = 10

[LOGGING]
log_level = INFO
```

## 📈 System Status

The system provides real-time status reporting:

```
✓ Facebook: Ready (credentials configured)
⚠ YouTube: Available (credentials needed)
⚠ Instagram: Available (requires selenium package)
⚠ TikTok: Available (requires selenium package)
```

## 🛡️ Security Features

- **Credential Management**: Environment variables and secure config files
- **Policy Enforcement**: Automatic content screening
- **Error Handling**: Comprehensive exception management
- **Audit Logging**: Complete operation tracking

## 📦 Dependencies

### Core Requirements
- `python-dotenv` - Environment management
- `configparser` - Configuration handling
- `requests` - HTTP client for APIs
- `pathlib` - File path management

### Platform-Specific
- `google-api-python-client` - YouTube integration
- `selenium` - Instagram/TikTok automation
- `webdriver-manager` - Browser driver management
- `facebook-sdk` - Facebook API client

### AI Integration (Existing)
- `google-generativeai` - AI image generation
- `Pillow` - Image processing

## 🚨 Production Deployment

### Environment Setup
```bash
# Install Chrome for Selenium
apt-get update && apt-get install -y chromium-browser

# Set environment variables
export HEADLESS_MODE=true
export LOG_LEVEL=INFO
```

### Monitoring
- Monitor `logs/app.log` for operations
- Check `media/quarantine/` for policy violations
- Review success rates in processing summaries

## 🤝 Contributing

This system is designed with modularity in mind:

1. **Add New Platforms**: Create new connector modules following existing patterns
2. **Extend Policies**: Add validation rules in `policy_checker.py`
3. **Customize Workflows**: Modify orchestration in `main.py`

## 📄 License

MIT License - See LICENSE file for details.

---

**🎉 SYSTEM READY FOR PRODUCTION DEPLOYMENT 🎉**

*Complete social media automation with enterprise-grade features and robust error handling.*