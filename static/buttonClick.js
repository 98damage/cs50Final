document.addEventListener('DOMContentLoaded', function () {
    const selectedRecipes = new Set();
    const maxSelections = 7;

    const submitButton = document.getElementById('submit-recipes-btn');
    const addRecipeButtons = document.querySelectorAll('.add-recipe-btn');
    const hiddenInput = document.getElementById('selected-recipes-input');  // Reference to the hidden input field

    // Ensure the submit button is visible and initially disabled
    submitButton.style.display = 'block';
    submitButton.disabled = true;
    submitButton.classList.add('btn-secondary');  // Assume 'btn-secondary' is a greyed-out style

    addRecipeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const recipeid = this.getAttribute('recipeid');

            // Toggle selection
            if (selectedRecipes.has(recipeid)) {
                selectedRecipes.delete(recipeid);
                this.classList.remove('btn-danger');
                this.classList.add('btn-primary');
                this.textContent = 'Add';
            } else if (selectedRecipes.size < maxSelections) {
                selectedRecipes.add(recipeid);
                this.classList.remove('btn-primary');
                this.classList.add('btn-danger');
                this.textContent = 'Remove';
            }

            // Update the hidden input with the serialized array
            hiddenInput.value = JSON.stringify(Array.from(selectedRecipes));

            // Enable or disable the submit button based on the number of selections
            if (selectedRecipes.size === maxSelections) {
                submitButton.disabled = false;
                submitButton.classList.remove('btn-secondary');
                submitButton.classList.add('btn-primary');  // Change to the primary style when enabled
            } else {
                submitButton.disabled = true;
                submitButton.classList.remove('btn-primary');
                submitButton.classList.add('btn-secondary');  // Greyed out when not enough selections
            }

            // Disable other buttons if 7 recipes are selected
            if (selectedRecipes.size >= maxSelections) {
                addRecipeButtons.forEach(btn => {
                    if (!selectedRecipes.has(btn.getAttribute('recipeid'))) {
                        btn.disabled = true;
                        btn.classList.add('btn-secondary');
                    }
                });
            } else {
                addRecipeButtons.forEach(btn => {
                    btn.disabled = false;
                    btn.classList.remove('btn-secondary');
                });
            }
        });
    });
});