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
        
        // Set values
        consumeTimeInput.value = formattedTime;
        
        // Set attribute for datepicker
        if (typeof flatpickr === 'undefined') {
            // Fallback if flatpickr is not available
            consumeDateInput.value = formattedDate;
        }
    }
    
    // Initialize Flatpickr datepicker
    if (consumeDateInput && typeof flatpickr !== 'undefined') {
        try {
            const datepicker = flatpickr(consumeDateInput, {
                dateFormat: 'Y-m-d',
                defaultDate: new Date(),
                enableTime: false,
                allowInput: true,
                clickOpens: true,
                static: true,
                onChange: function(selectedDates, dateStr) {
                    // Custom behavior can be added here if needed
                }
            });
        } catch (e) {
            // Fallback to basic input if Flatpickr fails
            setCurrentDateTime();
        }
    } else if (consumeDateInput) {
        // Fallback to basic input if Flatpickr is not available
        setCurrentDateTime();
    }
    
    // Direct manipulation function - simplified to ensure reliability
    function updateFormForCategory(category) {
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
                        option.dataset.ingredients = favorite.ingredients ? JSON.stringify(favorite.ingredients) : '';
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
                const option = document.createElement('option');
                option.value = "";
                option.textContent = "Error loading favorites";
                option.disabled = true;
                favoriteSelect.appendChild(option);
            });
    }
    
    // Directly set up category change handler
    if (categorySelect) {
        // When category changes, update the form
        categorySelect.addEventListener('change', function() {
            const category = this.value;
            updateFormForCategory(category);
        });
        
        // If there's already a value, trigger the change
        if (categorySelect.value) {
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
                    } else if (categorySelect) {
                        // If no category is selected, default to 'consume'
                        categorySelect.value = 'consume';
                        updateFormForCategory('consume');
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
                const ingredients = selectedOption.dataset.ingredients;
                
                const descriptionInput = document.getElementById('description');
                const ingredientsInput = document.getElementById('ingredients');
                
                if (descriptionInput && description) {
                    descriptionInput.value = description;
                }
                
                if (ingredientsInput && ingredients) {
                    try {
                        // Parse the ingredients JSON string and join with newlines
                        const ingredientsList = JSON.parse(ingredients);
                        ingredientsInput.value = ingredientsList.join('\n');
                    } catch (e) {
                        ingredientsInput.value = '';
                    }
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
            const ingredientsInput = document.getElementById('ingredients');
            if (descriptionInput) {
                descriptionInput.value = '';
            }
            if (ingredientsInput) {
                ingredientsInput.value = '';
            }
        });
    }
    
    // Form submission handler
    if (activityForm) {
        activityForm.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Get the submit button and show loading state
            const submitBtn = document.querySelector('#save-activity-btn');
            const submitText = submitBtn.querySelector('#submit-text');
            const loadingSpinner = submitBtn.querySelector('#loading-spinner');
            
            // Disable submit button and show loading state
            submitBtn.disabled = true;
            submitText.textContent = 'Saving...';
            loadingSpinner.classList.remove('hidden');
            
            // Validate required fields
            const category = categorySelect.value;
            const activityName = activityNameInput.value;
            
            if (!category || !activityName) {
                alert('Please fill in all required fields.');
                // Reset submit button
                submitBtn.disabled = false;
                submitText.textContent = 'Save Activity';
                loadingSpinner.classList.add('hidden');
                return;
            }
            
            // Create activity data object
            const activityData = {
                category: category,
                name: activityName,
                favorite: saveFavoriteToggle.checked
            };
            
            // Add category-specific data
            if (category === 'consume') {
                // Get all consume-specific fields
                const description = document.getElementById('description').value;
                const ingredients = document.getElementById('ingredients').value;
                const consumeDate = document.getElementById('consume-date').value;
                const consumeTime = document.getElementById('consume-time').value;
                
                // Validate required consume fields
                if (!consumeDate || !consumeTime) {
                    alert('Please fill in the date and time fields.');
                    // Reset submit button
                    submitBtn.disabled = false;
                    submitText.textContent = 'Save Activity';
                    loadingSpinner.classList.add('hidden');
                    return;
                }
                
                // Get timezone offset in minutes
                const timezoneOffset = new Date().getTimezoneOffset();
                
                // Add consume-specific data
                activityData.description = description;
                activityData.ingredients = ingredients ? ingredients.split('\n').filter(i => i.trim()) : [];
                activityData.date = consumeDate;
                activityData.time = consumeTime;
                activityData.timezone_offset = -timezoneOffset; // Negate the offset to match server expectation
            }
            
            // Get CSRF token
            const csrftoken = getCookie('csrftoken');
            
            // Send the data to the server
            fetch('/activities/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(activityData)
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.message || 'Failed to save activity');
                    });
                }
                return response.json();
            })
            .then(data => {
                // Show success message
                showStatusMessage('success', data.message || 'Activity saved successfully!');
                
                // Hide modal
                closeModal();
                
                // Reset form
                activityForm.reset();
                
                // Reload the page
                window.location.reload();
            })
            .catch(error => {
                showStatusMessage('error', error.message || 'An error occurred while saving the activity');
            })
            .finally(() => {
                // Reset submit button state
                submitBtn.disabled = false;
                submitText.textContent = 'Save Activity';
                loadingSpinner.classList.add('hidden');
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
    
    // Helper function to show status messages
    function showStatusMessage(type, message) {
        const alertClass = type === 'success' 
            ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
            : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100';
            
        const alertHTML = `
            <div class="p-4 mb-4 text-sm rounded-lg ${alertClass}" role="alert">
                ${message}
            </div>
        `;
        
        // Insert alert before the form
        const form = document.getElementById('activityForm');
        if (form) {
            const alertDiv = document.createElement('div');
            alertDiv.innerHTML = alertHTML;
            form.parentNode.insertBefore(alertDiv, form);
            
            // Remove alert after 5 seconds
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }
    
    // Helper function to close the modal
    function closeModal() {
        const modal = document.getElementById('activityModal');
        if (typeof flowbite !== 'undefined' && modal) {
            const modalInstance = flowbite.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
    }
}); 