document.addEventListener('DOMContentLoaded', function() {
    // Navbar Scroll Animation
    const navbar = document.querySelector('.navbar-custom');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Gallery Category Filtering
    const filterButtons = document.querySelectorAll('.gallery-filter-btn');
    const galleryItems = document.querySelectorAll('.gallery-item-container');

    if (filterButtons.length > 0 && galleryItems.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                // Add active class to clicked button
                this.classList.add('active');

                const filterValue = this.getAttribute('data-filter');

                galleryItems.forEach(item => {
                    if (filterValue === 'all' || item.getAttribute('data-category') === filterValue) {
                        item.style.display = 'block';
                        // Add fade-in animation
                        item.style.animation = 'fadeInUp 0.5s ease forwards';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }

    // Custom Lightbox Implementation
    const lightbox = document.getElementById('customLightbox');
    const lightboxImg = document.getElementById('lightboxImg');
    const lightboxCaption = document.getElementById('lightboxCaption');
    const closeBtn = document.querySelector('.lightbox-close');

    if (lightbox && lightboxImg && closeBtn) {
        const previewLinks = document.querySelectorAll('.lightbox-preview');

        previewLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const imgSrc = this.getAttribute('href');
                const title = this.getAttribute('data-title');
                
                lightboxImg.src = imgSrc;
                if (lightboxCaption && title) {
                    lightboxCaption.textContent = title;
                } else if (lightboxCaption) {
                    lightboxCaption.textContent = '';
                }

                lightbox.style.display = 'block';
                document.body.style.overflow = 'hidden'; // Stop background scrolling
            });
        });

        // Close lightbox when close button clicked
        closeBtn.addEventListener('click', function() {
            lightbox.style.display = 'none';
            document.body.style.overflow = 'auto'; // Enable scrolling
        });

        // Close lightbox when clicking outside image
        lightbox.addEventListener('click', function(e) {
            if (e.target === lightbox || e.target.classList.contains('container') || e.target.tagName === 'ROW') {
                lightbox.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    }
});
