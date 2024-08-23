document.addEventListener("DOMContentLoaded", function() {
    const textarea = document.getElementById("postContent");
    const charCount = document.getElementById("charCount");

    if (textarea && charCount) {
        textarea.addEventListener("input", function() {
            const currentLength = textarea.value.length;
            charCount.textContent = `${currentLength}/350 characters`;
        });
    } else {
        console.error("Element(s) not found: ", { textarea, charCount });
    }
});
