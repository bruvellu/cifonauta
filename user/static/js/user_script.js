function showPassword() {
    passwordInput = document.querySelector(".get-password")
    visibleIcon = document.querySelector(".visible-icon")
    notVisibleIcon = document.querySelector(".not-visible-icon")
    if (isPasswordHidden) {
        visibleIcon.classList.remove("hidden-icon")
        notVisibleIcon.classList.add("hidden-icon")
        passwordInput.setAttribute("type", "text")
        isPasswordHidden = false
    }
    else {
        visibleIcon.classList.add("hidden-icon")
        notVisibleIcon.classList.remove("hidden-icon")
        passwordInput.setAttribute("type", "password")
        isPasswordHidden = true
    }
}

var isPasswordHidden = true