document.addEventListener("DOMContentLoaded", () => {
    const runButton = document.getElementById("run-script1-btn");
    const outputDiv = document.getElementById("output-script1");

    // Event listener for "Run Script" button
    runButton.addEventListener("click", async () => {
        const isEnabled = document.getElementById("script1-on").checked; // Check if the script is enabled
        if (!isEnabled) {
            outputDiv.textContent = "Script is disabled. Enable it first to run.";
            outputDiv.style.color = "red";
            return;
        }

        // Show loading state
        outputDiv.textContent = "Running script...";
        outputDiv.style.color = "blue";

        try {
            // Make a POST request to trigger the API route
            const response = await fetch("/api/start-transfer", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            const data = await response.json();

            // Display output based on success or error
            if (response.ok) {
                outputDiv.textContent = `Success: ${data.message}`;
                outputDiv.style.color = "green";
            } else {
                outputDiv.textContent = `Error: ${data.error}`;
                outputDiv.style.color = "red";
            }
        } catch (error) {
            console.error("Error calling the API:", error);
            outputDiv.textContent = "An error occurred while running the script.";
            outputDiv.style.color = "red";
        }
    });

    // Example: Monitor the cron job toggle and input
    const cronToggle = document.getElementById("cron-toggle-script1");
    const cronInput = document.getElementById("cron-time-script1");

    cronToggle.addEventListener("change", () => {
        if (cronToggle.checked) {
            const cronTime = cronInput.value.trim();
            if (!cronTime) {
                alert("Please enter a valid cron schedule before enabling the cron job.");
                cronToggle.checked = false;
                return;
            }
            console.log(`Cron enabled with schedule: ${cronTime}`);
        } else {
            console.log("Cron job disabled.");
        }
    });
});
