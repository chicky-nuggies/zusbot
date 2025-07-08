# Zus Coffee Frontend

A modern React application for the Zus Coffee AI Assistant, providing an intuitive interface for chatting with the AI, searching products, and finding outlets.

## Features

- **Chat Interface**: Interactive chatbot with conversation history and session management
- **Product Search**: AI-powered product search with intelligent summaries
- **Outlet Finder**: Natural language outlet search with detailed results
- **Tool Metadata**: Transparent display of AI tool usage and data sources
- **Responsive Design**: Mobile-friendly interface that works on all devices
- **Modern UI**: Clean, coffee-themed design with smooth animations

## Tech Stack

- **React 18** - Modern React with hooks
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **CSS3** - Modern styling with grid, flexbox, and animations
- **ES6+** - Modern JavaScript features

## Getting Started

### Prerequisites

- Node.js 16 or higher
- npm or yarn package manager

### Installation

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Build for Production

```bash
npm run build
```

This builds the app for production to the `build` folder.

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/
│   │   ├── Common/
│   │   │   ├── LoadingSpinner.js
│   │   │   └── ToolMetadata.js
│   │   └── Layout/
│   │       ├── Header.js
│   │       └── Navigation.js
│   ├── pages/
│   │   ├── Chat.js
│   │   ├── Products.js
│   │   └── Outlets.js
│   ├── services/
│   │   └── api.js
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
└── package.json
```

## API Integration

The frontend communicates with the backend API through the following endpoints:

- `POST /api/chat` - Chat with the AI assistant
- `GET /api/products` - Search products with AI
- `GET /api/outlets` - Query outlets with natural language
- `GET /api/health` - Health check

## Components

### Pages

- **Chat**: Full-featured chat interface with message history
- **Products**: Product search with AI-generated summaries
- **Outlets**: Outlet finder with natural language queries

### Common Components

- **LoadingSpinner**: Reusable loading indicator
- **ToolMetadata**: Displays AI tool usage information
- **Header**: App header with branding
- **Navigation**: Main navigation menu

## Styling

The app uses a modern CSS approach with:

- CSS Grid and Flexbox for layouts
- CSS Variables for consistent theming
- Responsive design with mobile-first approach
- Smooth animations and transitions
- Coffee-themed color palette

## Features in Detail

### Chat Interface

- Real-time messaging with the AI
- Session management and conversation history
- Message timestamps and status indicators
- Suggested conversation starters
- Tool usage metadata display

### Product Search

- AI-powered product recommendations
- Similarity scoring for retrieved products
- Quick suggestion buttons
- Detailed product information display

### Outlet Finder

- Natural language outlet queries
- Location-based search
- Facility and amenity filtering
- Comprehensive outlet information

### Tool Metadata

- Transparent AI operation display
- Tool arguments and results
- Execution timestamps
- Collapsible detailed view

## Browser Support

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Contributing

1. Follow React best practices
2. Use functional components with hooks
3. Maintain consistent code style
4. Add proper error handling
5. Ensure responsive design
6. Test on multiple devices

## License

This project is part of the Zus Coffee AI Assistant system.
