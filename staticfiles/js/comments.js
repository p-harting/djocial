document.addEventListener("DOMContentLoaded", function() {
    const replyLinks = document.querySelectorAll(".reply-link");

    replyLinks.forEach(link => {
        link.addEventListener("click", function(event) {
            event.preventDefault();
            const commentId = this.getAttribute("data-comment-id");
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            if (replyForm.style.display === "none" || replyForm.style.display === "") {
                replyForm.style.display = "block";
            } else {
                replyForm.style.display = "none";
            }
        });
    });
});