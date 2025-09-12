// Course card physics effects
const courseCards = document.querySelectorAll('.course-card');
const coursesShowcase = document.querySelector('.courses-showcase');

if (coursesShowcase && courseCards.length > 0) {
    let isMouseInside = false;

    coursesShowcase.addEventListener('mouseenter', () => {
        isMouseInside = true;
    });

    coursesShowcase.addEventListener('mouseleave', () => {
        isMouseInside = false;
        // Reset all cards to their original positions
        courseCards.forEach(card => {
            card.style.transform = '';
        });
    });

    coursesShowcase.addEventListener('mousemove', (e) => {
        if (!isMouseInside) return;

        const rect = coursesShowcase.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        courseCards.forEach(card => {
            const cardRect = card.getBoundingClientRect();
            const cardCenterX = cardRect.left + cardRect.width / 2 - rect.left;
            const cardCenterY = cardRect.top + cardRect.height / 2 - rect.top;

            const deltaX = mouseX - cardCenterX;
            const deltaY = mouseY - cardCenterY;
            const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

            // Magnetic effect when cursor is close
            if (distance < 100) {
                const force = (100 - distance) / 100;
                const moveX = deltaX * force * 0.3;
                const moveY = deltaY * force * 0.3;
                
                // Get original rotation from classes
                let originalRotation = 0;
                if (card.classList.contains('beginner-card')) originalRotation = -8;
                else if (card.classList.contains('intermediate-card')) originalRotation = 12;
                else if (card.classList.contains('advanced-card')) originalRotation = 5;
                else if (card.classList.contains('elite-card')) originalRotation = -15;

                // Apply magnetic movement with slight rotation
                const rotationModifier = (moveX / 50) * 5; // Slight tilt based on movement
                card.style.transform = `translate(${moveX}px, ${moveY}px) rotate(${originalRotation + rotationModifier}deg) scale(${1 + force * 0.1})`;
            } else {
                card.style.transform = '';
            }
        });
    });

    // Add click ripple effect and navigation
    courseCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('div');
            ripple.classList.add('ripple');
            
            const rect = card.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            card.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);

            // Smooth navigation to target section
            const href = card.getAttribute('href');
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    // Add a small delay for ripple effect to be visible
                    setTimeout(() => {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }, 200);
                }
            }
        });
    });
}
