document.querySelector('form').addEventListener('submit', function(event) {
    let progElem = document.querySelector('[name="feed_program"]');
    let program = progElem ? progElem.value : '';
    let maleGpBird = parseFloat(document.querySelector('[name="feed_male_gp_bird"]')?.value || 0);
    let femaleGpBird = parseFloat(document.querySelector('[name="feed_female_gp_bird"]')?.value || 0);

    // If submit button is delete, we can skip validation, but usually formaction overrides normal submit flow or we can check submitter
    if (event.submitter && event.submitter.classList.contains('btn-danger')) {
        return;
    }

    if (program === 'Full Feed') {
        if (maleGpBird <= 0 || femaleGpBird <= 0) {
            alert("Invalid Entry: Grams per bird for male and female cannot be 0 for Full Feed program.");
            event.preventDefault();
            return false;
        }
    }
});
