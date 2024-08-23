// Wait for the entire DOM to load before executing the script
document.addEventListener("DOMContentLoaded", function() {
    // Select all elements with the class "reply-link"
    const replyLinks = document.querySelectorAll(".reply-link");

    // Iterate over each "reply-link" element
    replyLinks.forEach(link => {
        // Add a click event listener to each "reply-link"
        link.addEventListener("click", function(event) {
            // Prevent the default action of the link (which might be navigating to another page)
            event.preventDefault();

            // Get the ID of the comment associated with the clicked link from the "data-comment-id" attribute
            const commentId = this.getAttribute("data-comment-id");

            // Select the corresponding reply form using the comment ID
            const replyForm = document.getElementById(`reply-form-${commentId}`);

            // Toggle the display of the reply form between "block" and "none"
            if (replyForm.style.display === "none" || replyForm.style.display === "") {
                replyForm.style.display = "block"; // Show the reply form
            } else {
                replyForm.style.display = "none"; // Hide the reply form
            }
        });
    });
});
