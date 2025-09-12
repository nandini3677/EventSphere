// static/js/signup.js
document.querySelectorAll("form[data-role]").forEach(form => {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const role = form.getAttribute("data-role");
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => data[key] = value);
    data.role = role;

    if (data.password !== data.confirm_password) {
      alert("Passwords do not match!");
      return;
    }

    const response = await fetch("/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    alert(result.message);
  });
});
