document.getElementById("reviewForm").addEventListener("submit", async (e) => {
e.preventDefault();


const formData = new FormData(e.target);


const response = await fetch("/api/generate-review/", {
method: "POST",
body: formData,
});


const result = await response.json();
const box = document.getElementById("resultBox");
box.style.display = "block";
box.innerText = result.review;
});