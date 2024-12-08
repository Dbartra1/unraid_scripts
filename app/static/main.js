document.addEventListener("DOMContentLoaded", () => {
    // Select all buttons with the class 'run-script-btn'
    const scriptButtons = document.querySelectorAll(".run-script-btn");

    // Add a click event listener to each button
    scriptButtons.forEach(button => {
        button.addEventListener("click", async (event) => {
            const scriptRoute = button.dataset.script; // Get API route from data attribute
            const section = button.closest(".script-section"); // Find the parent section
            const outputDiv = section.querySelector(".output"); // Find the associated output div
            const toggleOn = section.querySelector("input[id$='-on']").checked; // Check if script is enabled

            if (!toggleOn) {
                outputDiv.textContent = "Script is disabled. Enable it first to run.";
                outputDiv.style.color = "red";
                return;
            }

            outputDiv.textContent = "Running script...";
            outputDiv.style.color = "blue";

            try {
                // Make the POST request to the corresponding API route
                const response = await fetch(`/api/${scriptRoute}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                const data = await response.json();

                // Update the output div with the API response
                if (response.ok) {
                    outputDiv.textContent = `Success: ${data.message}`;
                    outputDiv.style.color = "green";
                } else {
                    outputDiv.textContent = `Error: ${data.error}`;
                    outputDiv.style.color = "red";
                }
            } catch (error) {
                console.error("Error calling API:", error);
                outputDiv.textContent = "An error occurred while running the script.";
                outputDiv.style.color = "red";
            }
        });
    });
});
