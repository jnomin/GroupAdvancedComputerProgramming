document.addEventListener("DOMContentLoaded", function () {
  const input = document.querySelector("#movie-input");
  const resultsBox = document.querySelector("#autocomplete-results");

  // ✅ Prevent errors on pages without the input
  if (!input || !resultsBox) return;

  let timeout = null;

  input.addEventListener("input", function () {
    clearTimeout(timeout);
    const query = this.value.trim();
    if (query.length < 2) {
      resultsBox.innerHTML = "";
      resultsBox.style.display = "none";
      return;
    }

    timeout = setTimeout(() => {
      fetch(`/autocomplete?query=${encodeURIComponent(query)}`)
        .then((res) => res.json())
        .then((data) => {
          resultsBox.innerHTML = "";
          if (data.length === 0) {
            resultsBox.style.display = "none";
            return;
          }

          data.forEach((movie) => {
            const item = document.createElement("div");
            item.className = "autocomplete-item";

            const poster = document.createElement("img");
            poster.src = movie.poster || "/static/no-poster.jpg";
            poster.alt = movie.title;
            poster.className = "autocomplete-poster";

            const info = document.createElement("div");
            info.className = "autocomplete-text";
            info.textContent = `${movie.title} (${movie.year})`;

            item.appendChild(poster);
            item.appendChild(info);

            item.addEventListener("click", () => {
              window.location.href = `/movie/${encodeURIComponent(movie.title)}`;
            });

            resultsBox.appendChild(item);
          });

          resultsBox.style.display = "block";
        });
    }, 300);
  });

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      const title = input.value.trim();
      if (title.length > 0) {
        window.location.href = `/movie/${encodeURIComponent(title)}`;
      }
    }
  });

  document.addEventListener("click", (e) => {
    if (!resultsBox.contains(e.target) && e.target !== input) {
      resultsBox.innerHTML = "";
      resultsBox.style.display = "none";
    }
  });
});
