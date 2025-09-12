# WINORZ - Flask Web Application

A modern, responsive Flask web application for the WINORZ community platform. Convert scattered skills into focused income with anime-inspired energy and business reality.

## Features

- **Modern Design**: Clean, contemporary interface with glassmorphism effects
- **Dark Mode**: Toggle between light and dark themes with localStorage persistence
- **Responsive**: Fully responsive design with mobile-first approach
- **Interactive Elements**: Smooth animations, hover effects, and physics-based interactions
- **Course Navigation**: Dynamic course cards with magnetic cursor effects
- **Professional Layout**: Organized sections for community, pricing, courses, and more

## Project Structure

```
landing/
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # Jinja2 templates
│   ├── base.html         # Base template with common elements
│   ├── index.html        # Homepage template
│   └── courses.html      # Courses page template
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   │   ├── style.css    # Main stylesheet
│   │   └── courses.css  # Courses-specific styles
│   ├── js/              # JavaScript files
│   │   ├── main.js      # Main application JavaScript
│   │   └── courses.js   # Courses-specific JavaScript
│   └── images/          # Image assets
│       ├── logo.png     # Application logo
│       └── favicon.png  # Favicon
├── index_backup.html     # Original HTML backup
└── courses_backup.html  # Original HTML backup
```

## Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd winorz
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask application**
   ```bash
   python app.py
   ```

4. **Open your browser and navigate to**
   ```
   http://localhost:5000
   ```

## Routes

- `/` - Homepage with hero section, community benefits, pricing, and introduction
- `/courses` - Courses page with detailed skill categories organized by difficulty tiers

## Templates

### Base Template (`templates/base.html`)
- Common HTML structure, head tags, navigation, and footer
- Logo integration with `logo.png` from static/images
- Favicon support with `favicon.png`
- Theme toggle functionality
- Mobile-responsive hamburger menu

### Homepage (`templates/index.html`)
- Extends base template
- Hero section with call-to-action
- Community benefits grid
- About section with team visualization
- Statistics showcase with animated counters
- Pricing cards (Free Discord vs Elite Access)
- Intro video placeholder
- Affiliate vault showcase

### Courses Page (`templates/courses.html`)
- Extends base template with additional CSS/JS
- Interactive floating course cards in hero section
- Course tiers: Beginner, Intermediate, Advanced, Elite
- Detailed course categories with skill breakdowns
- Physics-based card interactions with cursor magnetism

## Styling

### Main Stylesheet (`static/css/style.css`)
- CSS custom properties for consistent theming
- Light and dark mode support
- Responsive grid layouts
- Smooth animations and transitions
- Glassmorphism effects for navigation
- Professional typography with Inter font

### Courses Stylesheet (`static/css/courses.css`)
- Course-specific components and animations
- Floating card animations with individual timing
- Magnetic cursor interaction effects
- Ripple click effects
- Tier-based color coding

## JavaScript Features

### Main Script (`static/js/main.js`)
- Theme switching with localStorage persistence
- Smooth scrolling navigation
- Mobile menu functionality
- Intersection Observer for scroll animations
- Parallax effects
- Enhanced button interactions
- Statistic counter animations

### Courses Script (`static/js/courses.js`)
- Physics-based course card interactions
- Magnetic cursor effects
- Click ripple animations
- Smooth section navigation
- Dynamic card positioning and rotation

## Key Features

1. **Logo Integration**: Uses `logo.png` for branding throughout the application
2. **Favicon Support**: Professional favicon implementation
3. **Theme Persistence**: Dark/light mode preferences saved locally
4. **Mobile Optimization**: Responsive design with hamburger menu
5. **Interactive Elements**: Hover effects, animations, and physics simulations
6. **Professional Navigation**: Fixed glassmorphism navbar with smooth scrolling
7. **Modular Architecture**: Separate templates and assets for maintainability

## Technology Stack

- **Backend**: Flask 3.0.0
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: CSS Grid, Flexbox, Custom Properties
- **Icons**: Font Awesome 6.4.0
- **Typography**: Google Fonts (Inter)
- **Build**: No build process required - vanilla HTML/CSS/JS

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

The application uses Flask's built-in development server. For production deployment, consider using:
- Gunicorn or uWSGI for WSGI serving
- Nginx for static file serving and reverse proxy
- SSL certificates for HTTPS

## License

All rights reserved. WINORZ 2025.


#
