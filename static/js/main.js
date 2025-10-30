// Electronic Medication Administration Record - Main JavaScript

document.addEventListener("DOMContentLoaded", function () {
  console.log("eMAR System Loaded");

  // Check API health
  checkAPIHealth();
});

async function checkAPIHealth() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    console.log("API Status:", data);
  } catch (error) {
    console.error("Error checking API health:", error);
  }
}
