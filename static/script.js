// static/script.js

document.addEventListener('DOMContentLoaded', function() {

    // --- Button Ripple Effect ---
    function createRipple(event) {
        const button = event.currentTarget;

        const circle = document.createElement("span");
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;

        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
        circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
        circle.classList.add("ripple");

        // Clean up old ripples
        const ripple = button.getElementsByClassName("ripple")[0];
        if (ripple) {
            ripple.remove();
        }

        button.appendChild(circle);
    }

    const buttons = document.getElementsByClassName("btn");
    for (const button of buttons) {
        button.addEventListener("click", createRipple);
    }


    // --- Staggered List Animation using Intersection Observer ---
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Find all list items within the observed container
                const listItems = entry.target.querySelectorAll('.stagger-list-item');
                listItems.forEach((item, index) => {
                    // Apply a delay to each item to create the stagger effect
                    setTimeout(() => {
                        item.classList.add('is-visible');
                    }, index * 100); // 100ms delay between items
                });
                // Unobserve the container after animation to prevent re-triggering
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1 // Trigger when 10% of the element is visible
    });

    // Observe all elements with the .stagger-list class
    document.querySelectorAll('.stagger-list').forEach(list => {
        observer.observe(list);
    });

});