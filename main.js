// JavaScript for Smart Attendance System

// Confirmation for deletion with enhanced alert
function confirmDeletion(event) {
    if (!confirm("Are you sure you want to delete this student?")) {
        event.preventDefault(); // Prevents the default link action if not confirmed
    }
}

// Form validation: Checks if all required fields are filled
function validateForm() {
    const nameField = document.getElementById('name');
    if (nameField && nameField.value.trim() === '') {
        alert("Please enter a name.");
        nameField.focus();
        return false; // Prevents form submission if validation fails
    }
    // Additional validations can be added here if there are more fields
    return true; // Allows form submission if validation passes
}

// Access the user's webcam for real-time recognition with error handling
function startWebcam(videoElementId) {
    const videoElement = document.getElementById(videoElementId);

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                videoElement.srcObject = stream;
            })
            .catch(function (error) {
                console.error("Webcam access error:", error);
                alert("Could not access the webcam. Please check your settings and allow access.");
            });
    } else {
        alert("Your browser does not support webcam access.");
    }
}

// Capture image from webcam, provide feedback, and prepare for submission
function captureImage(videoElementId, hiddenInputId) {
    const videoElement = document.getElementById(videoElementId);
    const hiddenInput = document.getElementById(hiddenInputId);
    const canvas = document.createElement('canvas');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;

    const context = canvas.getContext('2d');
    context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

    // Convert the canvas image to a data URL and store it in the hidden input
    hiddenInput.value = canvas.toDataURL('image/png');

    // Display feedback message after capturing the image
    alert("Image captured successfully and prepared for submission!");
}

// Submit the captured image to Flask for recognition
function submitImage(hiddenInputId, apiUrl) {
    const hiddenInput = document.getElementById(hiddenInputId);
    const imageData = hiddenInput.value;

    if (!imageData) {
        alert("No image captured. Please try again.");
        return;
    }

    // Send the image data to Flask using a POST request
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageData })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert(`Recognition successful: ${data.message}`);
            } else {
                alert(`Recognition failed: ${data.message}`);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while submitting the image.");
        });
}

// Responsive webcam adjustments for mobile
function adjustVideoForMobile(videoElementId) {
    const videoElement = document.getElementById(videoElementId);
    if (window.innerWidth <= 600) {
        videoElement.width = 320; // Resize for mobile screens
        videoElement.height = 240;
    }
}

// Event listeners
document.addEventListener("DOMContentLoaded", function () {
    // Apply confirm deletion to any delete buttons
    const deleteButtons = document.querySelectorAll(".delete-btn");
    deleteButtons.forEach(button => {
        button.addEventListener("click", confirmDeletion);
    });

    // Form validation for the registration/edit form
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (event) {
            if (!validateForm()) {
                event.preventDefault();
            }
        });
    }

    // Initialize webcam if the element with id="video" exists
    const videoElement = document.getElementById("video");
    if (videoElement) {
        startWebcam("video");
        adjustVideoForMobile("video");
    }

    // Capture button for real-time recognition page
    const captureButton = document.getElementById("capture");
    if (captureButton) {
        captureButton.addEventListener("click", function () {
            captureImage("video", "capturedImage");
        });
    }

    // Submit button for sending image to Flask
    const submitButton = document.getElementById("submit");
    if (submitButton) {
        submitButton.addEventListener("click", function () {
            submitImage("capturedImage", "/real_time_recognition");
        });
    }
});
