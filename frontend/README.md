# News Chatbot Frontend

## Overview
The frontend of the News Chatbot is a modern, responsive web application built with React and TypeScript. It provides an intuitive interface for users to interact with the news chatbot, featuring real-time chat capabilities, news article display, and a sleek user experience.

## Architecture

### 1. Technology Stack
- **Core Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS for utility-first styling
- **UI Components**: 
  - Headless UI for accessible components
  - Heroicons for beautiful icons
- **State Management**: React's built-in state management
- **HTTP Client**: Axios for API communication
- **Development Tools**:
  - TypeScript for type safety
  - ESLint for code quality
  - PostCSS for CSS processing

### 2. Project Structure
```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   ├── services/         # API and business logic
│   ├── styles/           # Global styles and Tailwind config
│   ├── types/            # TypeScript type definitions
│   ├── App.tsx           # Main application component
│   └── index.tsx         # Application entry point
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
└── tailwind.config.js    # Tailwind CSS configuration
```

### 3. Key Features

#### Real-time Chat Interface
- WebSocket-based real-time communication
- Message history management
- Typing indicators
- Message status tracking

#### News Article Display
- Responsive article cards
- Rich text formatting
- Image handling
- Article metadata display

#### User Experience
- Responsive design for all devices
- Dark/Light mode support
- Smooth animations
- Loading states and error handling

### 4. Component Architecture

#### Core Components
1. **Chat Components**
   - ChatWindow: Main chat interface
   - MessageList: Message history display
   - MessageInput: User input handling
   - TypingIndicator: Real-time typing status

2. **News Components**
   - ArticleCard: Individual article display
   - ArticleList: Article collection view
   - ArticleDetail: Detailed article view
   - NewsFilter: Article filtering and search

3. **Layout Components**
   - Header: Navigation and branding
   - Sidebar: Navigation and filters
   - Footer: Additional information
   - Modal: Popup dialogs

### 5. State Management
- Local component state for UI elements
- Context API for global state
- Custom hooks for reusable logic
- WebSocket state management

### 6. API Integration
- RESTful API communication via Axios
- WebSocket connection management
- Error handling and retry logic
- Request/Response interceptors

### 7. Styling Architecture
- Tailwind CSS for utility-first styling
- Custom CSS variables for theming
- Responsive design breakpoints
- Component-specific styles

## Development Setup

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn package manager

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/kumarsantosh3914/news-chatbot.git
   cd news-chatbot/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start development server:
   ```bash
   npm start
   # or
   yarn start
   ```

### Available Scripts
- `npm start`: Run development server
- `npm build`: Build for production
- `npm test`: Run tests
- `npm eject`: Eject from create-react-app

## Production Build
1. Build the application:
   ```bash
   npm run build
   ```

2. The build artifacts will be stored in the `build/` directory

## Best Practices
1. **Code Style**
   - Follow TypeScript best practices
   - Use functional components with hooks
   - Implement proper error boundaries
   - Write meaningful component documentation

2. **Performance**
   - Implement code splitting
   - Optimize bundle size
   - Use proper caching strategies
   - Implement lazy loading

3. **Testing**
   - Write unit tests for components
   - Implement integration tests
   - Use proper mocking strategies
   - Maintain good test coverage