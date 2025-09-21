# SUARA - Unifi TV Customer Service Chatbot

A modern, iOS-style chatbot interface built with Next.js for Unifi TV customer service, integrated with AWS backend services.

## ✨ Features

- 💬 **Real-time Chat Interface** - Smooth, iOS-style messaging experience
- 📷 **Image Analysis** - Upload photos of error screens for automatic diagnosis
- 🎤 **Voice Support** - Record audio descriptions of issues
- 🤖 **AI-Powered Responses** - Integrated with AWS Bedrock and custom ML models
- 📱 **Responsive Design** - Works perfectly on desktop and mobile
- 🎨 **iOS-Style UI** - Vibrant colors, rounded corners, and smooth animations
- 🔧 **Full Backend Integration** - Connected to existing AWS Lambda functions

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- AWS backend deployed (see main project README)

### Installation

1. Navigate to the frontend directory:
```bash
cd nextjs-chatbot
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.local.example .env.local
# Edit .env.local with your API Gateway URL
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

```bash
npm run build
npm start
```

## 🏗️ Project Structure

```
src/
├── app/                 # Next.js app directory
│   ├── globals.css     # iOS-style global styles
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Home page
├── components/         # React components
│   ├── ChatContainer.tsx  # Main chat logic
│   ├── ChatInput.tsx      # Multi-modal input
│   └── ChatMessage.tsx    # Message display
├── lib/               # Utilities
│   └── api.ts         # Backend API client
└── types/             # TypeScript definitions
    └── index.ts
```

## 🎨 Design System

- **Colors**: iOS-inspired vibrant palette (SF Blue, SF Purple, SF Green)
- **Typography**: SF Pro Display font family
- **Spacing**: Consistent iOS-style spacing and padding
- **Animations**: Smooth transitions and micro-interactions
- **Shadows**: Subtle iOS-style shadows and depth

## 🔌 Backend Integration

The frontend integrates with these AWS services:

- **Upload Handler**: File upload to S3
- **Transcribe Handler**: Audio-to-text conversion
- **Image Analysis**: Rekognition + custom models
- **Bedrock Handler**: AI response generation
- **Action Executor**: Automated troubleshooting actions

## 🌐 Deployment

### Local Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm start
```

### Deploy to Vercel
```bash
npm i -g vercel
vercel
```

### Deploy to AWS Amplify
1. Connect your GitHub repository
2. Set environment variables in Amplify console
3. Deploy automatically on push

## 🔧 Configuration

### Environment Variables

```bash
NEXT_PUBLIC_API_URL=https://your-api-gateway-url.amazonaws.com/prod
```

### Customization

- **Colors**: Update `tailwind.config.js`
- **Fonts**: Modify font family in `globals.css`
- **API Endpoints**: Update `src/lib/api.ts`
- **Branding**: Change logo and colors in components

## 📱 Features in Detail

### Multi-Modal Input
- Text messages with rich formatting
- Image upload with preview
- Audio recording with waveform visualization
- File drag-and-drop support

### AI-Powered Responses
- Automatic image analysis for error detection
- Voice-to-text transcription
- Contextual troubleshooting suggestions
- Audio response playback

### iOS-Style UX
- Smooth animations and transitions
- Haptic-like feedback (visual)
- Rounded corners and shadows
- Vibrant, accessible color palette

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the Unifi TV Customer Service system developed for Telekom Malaysia.