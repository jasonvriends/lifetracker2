document.addEventListener('DOMContentLoaded', function() {
    // Get relevant elements
    const categorySelect = document.getElementById('category');
    const favoriteSelect = document.getElementById('favorite-activities');
    const clearFavoriteBtn = document.getElementById('clear-favorite');
    const dynamicFields = document.getElementById('dynamic-fields');
    const basicFields = document.getElementById('basic-fields');
    const consumeFields = document.getElementById('consume-fields');
    const activityNameLabel = document.getElementById('activity-name-label');
    const activityNameInput = document.getElementById('activity-name');
    const saveFavoriteToggle = document.getElementById('save-favorite');
    const activityForm = document.getElementById('activityForm');
    
    // Date and time inputs
    const consumeDateInput = document.getElementById('consume-date');
    const consumeTimeInput = document.getElementById('consume-time');
    
    console.log('Activity Modal JS loaded');
    console.log('Category select found:', !!categorySelect);
    
    // Function to set current date and time from user's timezone
    function setCurrentDateTime() {
        if (!consumeDateInput || !consumeTimeInput) return;
        
        // Get current date and time in user's timezone
        const now = new Date();
        
        // Format date (YYYY-MM-DD)
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const formattedDate = `${year}-${month}-${day}`;
        
        // Format time (HH:MM)
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const formattedTime = `${hours}:${minutes}`;
        
        console.log('Setting date/time to:', formattedDate, formattedTime);
        
        // Set values
        consumeDateInput.value = formattedDate;
        consumeTimeInput.value = formattedTime;
        
        // Set attribute for datepicker
        consumeDateInput.setAttribute('data-date', formattedDate);
    }
    
    // Initialize datepicker if using Flowbite
    if (consumeDateInput && typeof Datepicker !== 'undefined') {
        try {
            const datepicker = new Datepicker(consumeDateInput, {
                format: 'yyyy-mm-dd',
                autohide: true,
                todayBtn: true,
                clearBtn: false,
                todayHighlight: true
            });
            console.log('Datepicker initialized');
        } catch (e) {
            console.error('Error initializing datepicker:', e);
        }
    }
    
    // Direct manipulation function - simplified to ensure reliability
    function updateFormForCategory(category) {
        console.log('Direct update for category:', category);
        
        // Show/hide dynamic fields
        if (category) {
            if (dynamicFields) dynamicFields.classList.remove('hidden');
            
            // Update category-specific fields
            if (category === 'consume') {
                if (activityNameLabel) activityNameLabel.textContent = 'Consume Name';
                if (activityNameInput) activityNameInput.placeholder = 'What did you consume?';
                if (consumeFields) consumeFields.classList.remove('hidden');
                
                // Set current date and time for consume
                setCurrentDateTime();
            } else {
                if (activityNameLabel) activityNameLabel.textContent = 'Name';
                if (activityNameInput) activityNameInput.placeholder = 'Activity name';
                if (consumeFields) consumeFields.classList.add('hidden');
            }
            
            // Enable favorites
            if (favoriteSelect) favoriteSelect.disabled = false;
            if (clearFavoriteBtn) clearFavoriteBtn.disabled = false;
            
            // Load favorites
            loadFavorites(category);
        } else {
            if (dynamicFields) dynamicFields.classList.add('hidden');
            if (favoriteSelect) favoriteSelect.disabled = true;
            if (clearFavoriteBtn) clearFavoriteBtn.disabled = true;
        }
    }
    
    // Function to load favorites for a specific category
    function loadFavorites(category) {
        // Clear current options
        if (!favoriteSelect) return;
        
        favoriteSelect.innerHTML = '<option value="" selected>Select a favorite</option>';
        
        // Fetch favorites
        fetch(`/activities/favorites/${category}/`)
            .then(response => response.json())
            .then(data => {
                if (data && data.length > 0) {
                    data.forEach(favorite => {
                        const option = document.createElement('option');
                        option.value = favorite.id;
                        option.textContent = favorite.name;
                        option.dataset.description = favorite.description || '';
                        favoriteSelect.appendChild(option);
                    });
                } else {
                    const option = document.createElement('option');
                    option.value = "";
                    option.textContent = "No favorites found";
                    option.disabled = true;
                    favoriteSelect.appendChild(option);
                }
            })
            .catch(error => {
                console.error('Error loading favorites:', error);
                const option = document.createElement('option');
                option.value = "";
                option.textContent = "Error loading favorites";
                option.disabled = true;
                favoriteSelect.appendChild(option);
            });
    }
    
    // Directly set up category change handler
    if (categorySelect) {
        console.log('Setting up category change handler');
        
        // When category changes, update the form
        categorySelect.addEventListener('change', function() {
            const category = this.value;
            console.log('Category changed to:', category);
            updateFormForCategory(category);
        });
        
        // If there's already a value, trigger the change
        if (categorySelect.value) {
            console.log('Initial category:', categorySelect.value);
            updateFormForCategory(categorySelect.value);
        }
    }
    
    // Modal visibility handler
    const activityModal = document.getElementById('activityModal');
    if (activityModal) {
        // Set up a MutationObserver to detect modal visibility changes
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && 
                    mutation.attributeName === 'class' && 
                    !activityModal.classList.contains('hidden')) {
                    console.log('Modal visible, checking category');
                    if (categorySelect && categorySelect.value) {
                        updateFormForCategory(categorySelect.value);
                    }
                }
            });
        });
        
        observer.observe(activityModal, { attributes: true });
        
        // Also handle direct clicks on modal toggle buttons
        document.addEventListener('click', function(event) {
            if (event.target.hasAttribute('data-modal-toggle') && 
                event.target.getAttribute('data-modal-toggle') === 'activityModal') {
                
                // Slight delay to ensure modal is open
                setTimeout(() => {
                    if (categorySelect && categorySelect.value) {
                        updateFormForCategory(categorySelect.value);
                    }
                }, 100);
            }
        });
    }
    
    // Event handler for favorite selection
    if (favoriteSelect) {
        favoriteSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (selectedOption && selectedOption.value) {
                // Fill in the form with the selected favorite's details
                activityNameInput.value = selectedOption.textContent;
                
                const description = selectedOption.dataset.description;
                const descriptionInput = document.getElementById('description');
                if (descriptionInput && description) {
                    descriptionInput.value = description;
                }
            }
        });
    }
    
    // Event handler for clear favorite button
    if (clearFavoriteBtn) {
        clearFavoriteBtn.addEventListener('click', function() {
            favoriteSelect.value = '';
            activityNameInput.value = '';
            const descriptionInput = document.getElementById('description');
            if (descriptionInput) {
                descriptionInput.value = '';
            }
            const ingredientsInput = document.getElementById('ingredients');
            if (ingredientsInput) {
                ingredientsInput.value = '';
            }
        });
    }
    
    // Form submission handler
    if (activityForm) {
        activityForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate required fields
            const category = categorySelect.value;
            const activityName = activityNameInput.value;
            
            if (!category || !activityName) {
                alert('Please fill in all required fields.');
                return;
            }
            
            // Create data object
            const formData = {
                'category': category,
                'activity-name': activityName,
                'save-favorite': saveFavoriteToggle.checked
            };
            
            // Add category-specific data
            if (category === 'consume') {
                formData['description'] = document.getElementById('description').value;
                formData['ingredients'] = document.getElementById('ingredients').value;
                formData['consume-date'] = document.getElementById('consume-date').value;
                formData['consume-time'] = document.getElementById('consume-time').value;
            }
            
            // Send the data via AJAX
            fetch('/activities/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Show success message
                    const successAlert = document.getElementById('success-alert');
                    const successMessage = document.getElementById('success-message');
                    if (successAlert && successMessage) {
                        successMessage.textContent = data.message;
                        successAlert.classList.remove('hidden');
                        
                        // Hide modal
                        const modal = document.getElementById('activityModal');
                        if (typeof flowbite !== 'undefined' && modal) {
                            const modalInstance = flowbite.Modal.getInstance(modal);
                            if (modalInstance) {
                                modalInstance.hide();
                            }
                        }
                        
                        // Reset form
                        activityForm.reset();
                        
                        // Redirect or reload if needed
                        if (data.redirect) {
                            setTimeout(() => {
                                window.location.href = data.redirect;
                            }, 1000);
                        } else {
                            setTimeout(() => {
                                window.location.reload();
                            }, 1000);
                        }
                    }
                } else {
                    // Show error
                    alert(data.message || 'An error occurred. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    }
    
    // Helper function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}); 