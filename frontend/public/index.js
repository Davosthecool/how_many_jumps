async function askPathToApi(start, end) {
    const request = new Request(`http://localhost:3000/api/get_distance/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            from: start,
            to: end
        })
    });
    return fetch(request)
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok " + response.statusText);
            }
            return response.json();
        })
        .catch(error => {
            throw new Error("There was a problem with the fetch operation: " + error.message);
        });
    
}


document.addEventListener("DOMContentLoaded", function () {
    const submitButton = document.getElementById("submit");

    submitButton.addEventListener("click", async function () {
        const start = document.getElementById("firstUrl").value;
        const end = document.getElementById("secondUrl").value;
        const guess = document.getElementById("numJumps").value;

        try {
            const result = await askPathToApi(start, end);
            console.log(result, guess);
        } catch (error) {
            console.error("Error:", error);
        }
    });

})