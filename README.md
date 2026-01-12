# BriteCo Ad Generator

AI-powered advertisement image generator for BriteCo jewelry insurance campaigns. Creates platform-specific ad creatives with brand guideline enforcement.

## 🎯 Features

### AI-Powered Prompt Generation
- **Claude Sonnet 4.5**: Generates detailed image prompts based on campaign concepts
- **GPT-4**: Alternative prompt generation option
- Enforces BriteCo brand guidelines automatically
- Optimized for wedding/engagement audience (Millennial/Gen Z)

### Multi-Platform Support
Generates ads for different social media platforms:

**Meta (Facebook/Instagram)**:
- Feed Post (1200x1200, 1:1)
- Feed Portrait (1080x1350, 4:5)
- Stories/Reels (1080x1920, 9:16)

**Reddit**:
- Feed Landscape (1200x628, 1.91:1)
- Feed Square (960x960, 1:1)

**Pinterest**:
- Standard Pin (1000x1500, 2:3)
- Square Pin (1000x1000, 1:1)

### Brand Guidelines
Automatically enforces:
- **Colors**: Turquoise (#31D7CA), Navy (#272D3F), Orange (#FC883A)
- **Photography**: Warm lighting, optimistic, authentic
- **Style**: Modern, trustworthy, Millennial/Gen Z focused
- **Visual Elements**: Turquoise accents, outlined products, checkmark overlays

## 🚀 Quick Start

### Prerequisites
- Node.js 14+ (or just use native Node.js modules - no dependencies except dotenv)
- API Keys:
  - Anthropic Claude API key OR OpenAI API key
  - Google AI API key (for image generation - TODO)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd briteco-ad-generator-simple
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   # Windows
   copy .env.example .env

   # Mac/Linux
   cp .env.example .env
   ```

   Then edit `.env` and add your API keys:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-...
   OPENAI_API_KEY=sk-proj-...
   GOOGLE_AI_API_KEY=AIzaSy...
   ```

4. **Start the server**
   ```bash
   npm start
   ```

5. **Open in browser**
   ```
   http://localhost:3000
   ```

## 📖 Usage

### Generate Ads

1. **Enter Campaign Concept**: Describe your ad campaign idea
   - Example: "New Year engagement season campaign highlighting peace of mind"
   - Example: "Summer wedding planning with focus on protection during travel"

2. **Select Platforms**: Choose which platforms you want ads for
   - Meta (Facebook/Instagram)
   - Reddit
   - Pinterest

3. **Choose AI Provider**: Select Claude or ChatGPT for prompt generation

4. **Generate Prompt**: Click "Generate Image Prompt" to create AI-optimized prompt

5. **Review & Edit**: Edit the prompt if needed

6. **Generate Images**: Click "Generate Images" (currently shows placeholders - Gemini integration pending)

7. **Download**: Save generated images for each platform

## 🏗️ Project Structure

```
briteco-ad-generator-simple/
├── server.js                # Node.js backend server
├── index.html              # Frontend interface
├── package.json            # Dependencies
├── .env                    # Environment variables (DO NOT COMMIT)
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 Configuration

### Brand Guidelines
Edit brand colors and style in `server.js`:
- Lines 68-80 (Claude prompt)
- Lines 114-124 (OpenAI prompt)

### Platform Specifications
Modify sizes in `server.js` (lines 18-32):
```javascript
const platformSpecs = {
    meta: [
        { name: 'Feed Post', width: 1200, height: 1200, aspectRatio: '1:1' },
        // ...
    ]
}
```

## 🚧 TODO: Gemini Image Generation

Current status: Placeholder images are returned

**To implement** (refer to venue-newsletter-tool for working example):

1. Add Gemini API call in `server.js`
2. Pass generated prompt to Gemini 2.5 Flash Image (Imagen 3)
3. Specify aspect ratio based on platform
4. Return base64 encoded images
5. Reference implementation: `venue-newsletter-tool/backend/integrations/gemini_client.py`

## 🔒 Security

### API Keys
- **NEVER** commit `.env` file to Git
- Use `.env.example` as a template
- Regenerate keys immediately if exposed
- Store production keys separately

### Rate Limiting
API cost considerations:
- Claude Sonnet 4.5: ~$0.003 per prompt generation
- GPT-4: ~$0.01-0.03 per prompt generation
- Gemini Image: Free tier available (when implemented)

## 🐛 Troubleshooting

### Server won't start
- Check if port 3000 is in use
- Verify Node.js version: `node --version`
- Run `npm install` to install dependencies

### API Errors
- Verify API keys in `.env` file
- Check API key permissions
- Review server console for errors

### Missing Dependencies
```bash
npm install dotenv
```

## 📝 Development Roadmap

- [x] Claude prompt generation
- [x] OpenAI prompt generation
- [x] Multi-platform support
- [x] Brand guidelines enforcement
- [ ] Gemini image generation integration
- [ ] Image editing/customization
- [ ] Batch generation
- [ ] Template library
- [ ] A/B testing support

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test
4. Commit: `git commit -m "Description"`
5. Push: `git push origin feature-name`
6. Create pull request

## 📄 License

ISC License

## 🙋 Support

For issues or questions:
1. Check GitHub issues
2. Review troubleshooting section
3. Create new issue with details

## 🎉 Credits

Built with:
- [Anthropic Claude](https://www.anthropic.com/)
- [OpenAI GPT-4](https://platform.openai.com/)
- [Google Gemini](https://ai.google.dev/) (integration pending)
- Native Node.js (http, https, fs)

---

**Making jewelry insurance marketing easier, one ad at a time** 💍✨
