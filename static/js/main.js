// Modern Theme Toggle functionality
const themeToggle = document.getElementById('themeToggle');
const mobileThemeToggle = document.getElementById('mobileThemeToggle');
const body = document.body;
const mobileThemeLabel = document.querySelector('.mobile-theme-label');

// Check for saved theme preference or default to light mode
const currentTheme = localStorage.getItem('theme') || 'light';
body.setAttribute('data-theme', currentTheme);
updateThemeToggle(currentTheme);

// Desktop theme toggle
if (themeToggle) {
    themeToggle.addEventListener('change', () => {
        toggleTheme();
    });
}

// Mobile theme toggle
if (mobileThemeToggle) {
    mobileThemeToggle.addEventListener('change', () => {
        toggleTheme();
    });
}

function toggleTheme() {
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeToggle(newTheme);
}

function updateThemeToggle(theme) {
    const isDark = theme === 'dark';
    
    // Update checkboxes
    if (themeToggle) {
        themeToggle.checked = isDark;
    }
    if (mobileThemeToggle) {
        mobileThemeToggle.checked = isDark;
    }
    
    // Update mobile label text
    if (mobileThemeLabel) {
        mobileThemeLabel.textContent = isDark ? 'Light Mode' : 'Dark Mode';
    }
}

// Smooth scrolling for navigation links with navbar offset
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const navbarHeight = 120; // Fixed navbar height + top position + padding
            const targetPosition = target.offsetTop - navbarHeight;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animationPlayState = 'running';
        }
    });
}, observerOptions);

// Observe loading elements
document.querySelectorAll('.loading').forEach(el => {
    observer.observe(el);
});

// Mobile menu functionality
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const mobileMenu = document.getElementById('mobileMenu');

if (mobileMenuToggle && mobileMenu) {
    const mobileMenuIcon = mobileMenuToggle.querySelector('i');

    mobileMenuToggle.addEventListener('click', () => {
        const isExpanded = mobileMenu.classList.contains('active');
        mobileMenu.classList.toggle('active');
        
        // Update ARIA attributes
        mobileMenuToggle.setAttribute('aria-expanded', !isExpanded);
        mobileMenuToggle.setAttribute('aria-label', !isExpanded ? 'Close mobile menu' : 'Open mobile menu');
        
        // Toggle hamburger icon
        if (!isExpanded) {
            mobileMenuIcon.className = 'fas fa-times';
        } else {
            mobileMenuIcon.className = 'fas fa-bars';
        }
    });

    // Close mobile menu when clicking on a link
    document.querySelectorAll('.mobile-nav-links a, .mobile-cta a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
            mobileMenuToggle.setAttribute('aria-expanded', 'false');
            mobileMenuToggle.setAttribute('aria-label', 'Open mobile menu');
            mobileMenuIcon.className = 'fas fa-bars';
        });
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!mobileMenuToggle.contains(e.target) && !mobileMenu.contains(e.target)) {
            mobileMenu.classList.remove('active');
            mobileMenuToggle.setAttribute('aria-expanded', 'false');
            mobileMenuToggle.setAttribute('aria-label', 'Open mobile menu');
            mobileMenuIcon.className = 'fas fa-bars';
        }
    });
}

// Navbar glass effect enhancement on scroll
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Enhance glass effect based on scroll position
    if (scrollTop > 50) {
        navbar.style.background = document.body.getAttribute('data-theme') === 'dark' 
            ? 'rgba(15, 23, 42, 0.15)' 
            : 'rgba(255, 255, 255, 0.15)';
        navbar.style.backdropFilter = 'blur(25px) saturate(200%)';
    } else {
        navbar.style.background = document.body.getAttribute('data-theme') === 'dark' 
            ? 'rgba(15, 23, 42, 0.08)' 
            : 'rgba(255, 255, 255, 0.08)';
        navbar.style.backdropFilter = 'blur(20px) saturate(180%)';
    }
});

// Add hover effects to cards
document.querySelectorAll('.benefit-card, .stat-item').forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-10px) scale(1.02)';
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0) scale(1)';
    });
});

// Counter animation for stats
const animateCounter = (element, target) => {
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target + (element.dataset.suffix || '');
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current) + (element.dataset.suffix || '');
        }
    }, 30);
};

// Initialize counter animations when stats section is visible
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const numbers = entry.target.querySelectorAll('.stat-number');
            numbers.forEach(number => {
                const text = number.textContent;
                
                // Special handling for non-numeric values
                if (text === '24/7' || text.includes('$')) {
                    // Don't animate text/currency values, just keep them as is
                    return;
                }
                
                const value = parseInt(text.replace(/\D/g, ''));
                const suffix = text.replace(/\d/g, '');
                number.dataset.suffix = suffix;
                animateCounter(number, value);
            });
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

const statsSection = document.querySelector('.stats');
if (statsSection) {
    statsObserver.observe(statsSection);
}

// Add parallax effect to hero section
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    const heroContent = document.querySelector('.hero-content');
    const heroVisual = document.querySelector('.hero-visual');
    
    if (hero && scrolled < hero.offsetHeight) {
        if (heroContent) {
            heroContent.style.transform = `translateY(${scrolled * 0.3}px)`;
        }
        if (heroVisual) {
            heroVisual.style.transform = `translateY(${scrolled * 0.2}px) rotate(${3 + scrolled * 0.01}deg)`;
        }
    }
});

// Add loading animation on page load
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
    
    // Set current year in footer
    const currentYearElement = document.getElementById('currentYear');
    if (currentYearElement) {
        currentYearElement.textContent = new Date().getFullYear();
    }
    
    // Trigger loading animations (skip hero content for LCP optimization)
    document.querySelectorAll('.loading').forEach((el, index) => {
        // Skip hero content elements for faster LCP
        if (el.closest('.hero-content')) {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
            return;
        }
        
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// Add interactive button effects
document.querySelectorAll('.cta-button').forEach(button => {
    button.addEventListener('mouseenter', () => {
        button.style.transform = 'translateY(-3px) scale(1.05)';
        button.style.boxShadow = 'var(--shadow-xl)';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'translateY(0) scale(1)';
        button.style.boxShadow = 'var(--shadow-md)';
    });
});
