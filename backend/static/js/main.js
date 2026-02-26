// ===== NAVIGATION MOBILE & DESKTOP COLLAPSE =====
const navToggle = document.querySelector('.nav-toggle');
const sidebar = document.querySelector('.sidebar');
const mainWrapper = document.querySelector('.main-wrapper');
const navLinks = document.querySelectorAll('.nav-link');

if (navToggle) {
    navToggle.addEventListener('click', () => {
        if (window.innerWidth > 768) {
            // Desktop: Collapse/Expand
            sidebar.classList.toggle('collapsed');
            mainWrapper.classList.toggle('sidebar-collapsed');
        } else {
            // Mobile: Show/Hide
            sidebar.classList.toggle('active');
        }

        // Handle hamburger icon animation
        const spans = navToggle.querySelectorAll('span');
        const isActive = (window.innerWidth > 768) ? !sidebar.classList.contains('collapsed') : sidebar.classList.contains('active');

        if (isActive) {
            spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
        } else {
            spans[0].style.transform = 'none';
            spans[1].style.opacity = '1';
            spans[2].style.transform = 'none';
        }
    });
}

navLinks.forEach(link => {
    link.addEventListener('click', () => {
        if (sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            const spans = navToggle.querySelectorAll('span');
            if (spans.length > 0) {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        }
    });
});

// ===== ACTIVE NAV LINK =====
const currentPath = window.location.pathname;
navLinks.forEach(link => {
    if (link.getAttribute('href') === currentPath ||
        (currentPath === '/' && link.getAttribute('href') === '/')) {
        link.classList.add('active');
    }
});

console.log('ASL Recognition App Loaded!');

