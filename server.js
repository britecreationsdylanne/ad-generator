const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

// Load environment variables from .env file
require('dotenv').config();

// API Keys from environment variables
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const GOOGLE_AI_API_KEY = process.env.GOOGLE_AI_API_KEY;

// Validate API keys are present
if (!ANTHROPIC_API_KEY && !OPENAI_API_KEY) {
    console.error('ERROR: Missing API keys! Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env file');
    process.exit(1);
}

// Helper to make HTTPS requests
function makeHTTPSRequest(requestUrl, options) {
    return new Promise((resolve, reject) => {
        const req = https.request(requestUrl, options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    resolve(data);
                }
            });
        });
        req.on('error', reject);
        if (options.body) {
            req.write(options.body);
        }
        req.end();
    });
}

// Generate prompt using Claude
async function generatePromptClaude(campaignText, platforms) {
    console.log('[Claude] Generating prompt...');

    const promptContext = `You are an expert at creating image generation prompts for AI models.

Create an image generation prompt for BriteCo jewelry insurance ads for ${platforms.join(', ')}.

Campaign context: ${campaignText}

BriteCo Brand Guidelines:
- Colors: Turquoise (#31D7CA), Navy (#272D3F), Orange (#FC883A)
- Style: Modern, clean, optimistic, trustworthy
- Target: Millennials and Gen Z engaged couples
- Photography: Warm lighting, diverse couples, genuine moments
- No gradients - solid colors only
- Gilroy font family

Requirements for the prompt:
- Show happy couple with engagement ring or jewelry
- Warm, natural lighting
- Modern, clean aesthetic
- Include turquoise color accent somewhere
- Professional photography quality
- Authentic, candid moment
- Diverse representation

Generate ONE detailed, creative prompt (200 words max) for Nano Banana (Google Gemini) image generator. Make it specific, visual, and actionable.`;

    const requestBody = JSON.stringify({
        model: 'claude-sonnet-4-5-20250929',
        max_tokens: 500,
        messages: [{
            role: 'user',
            content: promptContext
        }]
    });

    const response = await makeHTTPSRequest('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-api-key': ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01'
        },
        body: requestBody
    });

    if (response.content && response.content[0] && response.content[0].text) {
        console.log('[Claude] SUCCESS');
        return response.content[0].text;
    }
    throw new Error('Invalid Claude response');
}

// Generate prompt using OpenAI
async function generatePromptOpenAI(campaignText, platforms) {
    console.log('[OpenAI] Generating prompt...');

    const requestBody = JSON.stringify({
        model: 'gpt-4o',
        messages: [{
            role: 'system',
            content: 'You are an expert at creating image generation prompts for AI models.'
        }, {
            role: 'user',
            content: `Create an image generation prompt for BriteCo jewelry insurance ads for ${platforms.join(', ')}.

Campaign context: ${campaignText}

BriteCo Brand Guidelines:
- Colors: Turquoise (#31D7CA), Navy (#272D3F), Orange (#FC883A)
- Style: Modern, clean, optimistic, trustworthy
- Target: Millennials and Gen Z engaged couples
- Photography: Warm lighting, diverse couples, genuine moments

Requirements:
- Show happy couple with engagement ring or jewelry
- Warm, natural lighting
- Modern, clean aesthetic
- Include turquoise color accent
- Professional photography quality
- Authentic, candid moment
- Diverse representation

Generate ONE detailed, creative prompt (200 words max) for Nano Banana (Google Gemini). Make it specific, visual, and actionable.`
        }],
        temperature: 0.7,
        max_tokens: 500
    });

    const response = await makeHTTPSRequest('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${OPENAI_API_KEY}`
        },
        body: requestBody
    });

    if (response.choices && response.choices[0] && response.choices[0].message) {
        console.log('[OpenAI] SUCCESS');
        return response.choices[0].message.content;
    }
    throw new Error('Invalid OpenAI response');
}

// Generate images using Google Gemini (Nano Banana)
async function generateImagesGemini(prompt, platforms) {
    console.log('[Gemini] Generating images...');

    const platformSizes = {
        'Meta': [
            { name: 'Square Feed', width: 1080, height: 1080 },
            { name: 'Portrait Story', width: 1080, height: 1920 },
            { name: 'Landscape', width: 1200, height: 1200 }
        ],
        'Reddit': [
            { name: 'Feed', width: 1200, height: 628 },
            { name: 'Square', width: 960, height: 960 }
        ],
        'Pinterest': [
            { name: 'Standard Pin', width: 1000, height: 1500 },
            { name: 'Square', width: 1000, height: 1000 }
        ]
    };

    const images = [];

    for (const platform of platforms) {
        const sizes = platformSizes[platform] || platformSizes['Meta'];

        for (const size of sizes) {
            try {
                console.log(`[Gemini] ${platform} - ${size.name}...`);

                const requestUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${GOOGLE_AI_API_KEY}`;

                const requestBody = JSON.stringify({
                    contents: [{
                        parts: [{
                            text: prompt
                        }]
                    }]
                });

                const response = await makeHTTPSRequest(requestUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: requestBody
                });

                console.log(`[Gemini] Response received:`, JSON.stringify(response).substring(0, 500));

                if (response.candidates && response.candidates[0]) {
                    const candidate = response.candidates[0];
                    if (candidate.content && candidate.content.parts) {
                        console.log(`[Gemini] Parts count: ${candidate.content.parts.length}`);

                        const imagePart = candidate.content.parts.find(part => part.inline_data);

                        if (imagePart && imagePart.inline_data && imagePart.inline_data.data) {
                            const imageData = imagePart.inline_data.data;
                            const mimeType = imagePart.inline_data.mime_type || 'image/png';

                            images.push({
                                platform,
                                size: size.name,
                                width: size.width,
                                height: size.height,
                                url: `data:${mimeType};base64,${imageData}`
                            });

                            console.log(`[Gemini] SUCCESS - ${platform} ${size.name}`);
                        } else {
                            console.log(`[Gemini] No inline_data found in parts`);
                        }
                    } else {
                        console.log(`[Gemini] No content or parts in candidate`);
                    }
                } else {
                    console.log(`[Gemini] No candidates in response`);
                    console.log(`[Gemini] Response keys:`, Object.keys(response));
                }
            } catch (error) {
                console.error(`[Gemini] Error ${platform} ${size.name}:`, error.message);
            }
        }
    }

    return images;
}

// Create HTTP server
const server = http.createServer(async (req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;

    // CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // Serve index.html
    if (pathname === '/' || pathname === '/index.html') {
        const filePath = path.join(__dirname, 'index.html');
        fs.readFile(filePath, (err, data) => {
            if (err) {
                res.writeHead(404);
                res.end('File not found');
            } else {
                res.writeHead(200, { 'Content-Type': 'text/html' });
                res.end(data);
            }
        });
        return;
    }

    // API: Generate prompt
    if (pathname === '/api/generate-prompt' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                const data = JSON.parse(body);
                const { campaignText, platforms, provider } = data;

                console.log('\n=== Generate Prompt ===');
                console.log('Provider:', provider);

                let prompt;
                if (provider === 'claude') {
                    prompt = await generatePromptClaude(campaignText, platforms);
                } else {
                    prompt = await generatePromptOpenAI(campaignText, platforms);
                }

                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: true,
                    prompt: prompt
                }));
            } catch (error) {
                console.error('[API Error]:', error);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: false,
                    error: error.message
                }));
            }
        });
        return;
    }

    // API: Generate images
    if (pathname === '/api/generate-images' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                const data = JSON.parse(body);
                const { prompt, platforms } = data;

                console.log('\n=== Generate Images ===');
                console.log('Platforms:', platforms);

                const images = await generateImagesGemini(prompt, platforms);

                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: true,
                    images: images
                }));
            } catch (error) {
                console.error('[API Error]:', error);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: false,
                    error: error.message
                }));
            }
        });
        return;
    }

    // 404
    res.writeHead(404);
    res.end('Not found');
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log('='.repeat(80));
    console.log('BriteCo Ad Generator - FIXED SERVER');
    console.log('='.repeat(80));
    console.log(`\nURL: http://localhost:${PORT}`);
    console.log('\nAPIs:');
    console.log('  [OK] Claude (claude-sonnet-4-5-20250929)');
    console.log('  [OK] OpenAI (gpt-4o)');
    console.log('  [OK] Google Gemini (gemini-2.5-flash-image / Nano Banana)');
    console.log('\nPress Ctrl+C to stop');
    console.log('='.repeat(80));
});
