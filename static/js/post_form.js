document.addEventListener("DOMContentLoaded", function() {
    const textarea = document.getElementById("postContent");
    const charCount = document.getElementById("charCount");

    textarea.addEventListener("input", function() {
        const currentLength = textarea.value.length;
        charCount.textContent = `${currentLength}/350 characters`;
    });
});
