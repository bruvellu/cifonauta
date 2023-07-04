function showPassword() {
    passwordInput = document.querySelector("#id_password1")
    eyeIcons = document.querySelectorAll(".eye-icon")
    console.log(eyeIcons[0])
    if (isPasswordHidden) {
        eyeIcons[0].classList.remove("hidden-icon")
        eyeIcons[1].classList.add("hidden-icon")
        passwordInput.setAttribute("type", "text")
        isPasswordHidden = false
    }
    else {
        eyeIcons[0].classList.add("hidden-icon")
        eyeIcons[1].classList.remove("hidden-icon")
        passwordInput.setAttribute("type", "password")
        isPasswordHidden = true
    }
}

var isPasswordHidden = true