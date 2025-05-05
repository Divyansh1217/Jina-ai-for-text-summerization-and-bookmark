const API_URL = "http://localhost:8000";

function register() {
  const email = document.getElementById("regEmail").value;
  const password = document.getElementById("regPassword").value;

  fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  })
    .then(res => res.json())
    .then(data => {
      alert("Registered successfully");
      window.location.href = "login.html";
    });
}

function login() {
  const username = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        alert("Login successful");
        window.location.href = "dashboard.html";
      } else {
        alert("Login failed");
      }
    });
}

function addBookmark() {
  const url = document.getElementById("bookmarkUrl").value;
  const tag = prompt("Enter tag (e.g., work, personal):");

  fetch(`${API_URL}/bookmarks`, {
    method: "POST",
    headers: {
      "Authorization": "Bearer " + localStorage.getItem("token"),
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ url, tag })
  })
    .then(res => res.json())
    .then(() => {
      alert("Bookmark added!");
      loadBookmarks();
    });
}

function loadBookmarks() {
  const filterTag = document.getElementById("tagFilter")?.value || "";
  fetch(`${API_URL}/bookmarks`, {
    headers: { "Authorization": "Bearer " + localStorage.getItem("token") }
  })
  .then(res => res.json())
  .then(bookmarks => {
    const list = document.getElementById("bookmarksList");
    const tagSelect = document.getElementById("tagFilter");
    list.innerHTML = "";

    const tags = new Set();
    bookmarks.forEach(b => tags.add(b.tag));

    // Populate filter dropdown
    if (tagSelect) {
      tagSelect.innerHTML = `<option value="">All</option>`;
      [...tags].forEach(tag => {
        const opt = document.createElement("option");
        opt.value = tag;
        opt.innerText = tag;
        tagSelect.appendChild(opt);
      });
      tagSelect.value = filterTag;
    }

    // Filter and display bookmarks
    const filtered = filterTag ? bookmarks.filter(b => b.tag === filterTag) : bookmarks;
    filtered.forEach(b => {
      const li = document.createElement("li");
      li.setAttribute("data-id", b.id);
      li.innerHTML = `
        <a href="${b.url}" target="_blank" class="text-blue-600 hover:underline">${b.title}</a>
        <span class="text-sm text-gray-500">[${b.tag}]</span>
        
        <!-- Summary Section -->
        <div class="mt-2">
          <p id="summary-${b.id}" class="text-gray-600 text-sm line-clamp-3">${b.summary}</p>
          <button onclick="toggleSummary(${b.id})" class="text-blue-500 text-sm mt-1">Show more</button>
        </div>
        
        <!-- Delete Button -->
        <button onclick="deleteBookmark(${b.id})" class="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600 mt-2">❌</button>
      `;
      list.appendChild(li);
    });

    // Call the makeListDraggable function after the bookmarks are loaded
    makeListDraggable();
  });
}


function toggleSummary(bookmarkId) {
  const summaryElement = document.getElementById(`summary-${bookmarkId}`);
  const button = summaryElement.nextElementSibling;

  // Toggle the line-clamp for truncating and the button text
  if (summaryElement.classList.contains("line-clamp-3")) {
    summaryElement.classList.remove("line-clamp-3");
    button.innerText = "Show less";
  } else {
    summaryElement.classList.add("line-clamp-3");
    button.innerText = "Show more";
  }
}


function makeListDraggable() {
  const list = document.getElementById("bookmarksList");
  let draggedItem = null;

  list.querySelectorAll("li").forEach(item => {
    item.setAttribute("draggable", true); // Make the item draggable

    // When the drag starts, store the dragged item
    item.addEventListener("dragstart", (e) => {
      draggedItem = item;
      setTimeout(() => {
        item.style.display = "none"; // Hide the item while dragging
      }, 0);
    });

    // When dragging is over, show the item again
    item.addEventListener("dragend", () => {
      setTimeout(() => {
        draggedItem.style.display = "block"; // Show the item after dragging
        draggedItem = null;
      }, 0);
    });

    // Allow the item to be dropped by preventing the default behavior
    item.addEventListener("dragover", (e) => {
      e.preventDefault();
    });

    // Handle the drop and reorder the items
    item.addEventListener("drop", (e) => {
      e.preventDefault();
      if (draggedItem !== item) {
        const draggedIndex = [...list.children].indexOf(draggedItem);
        const targetIndex = [...list.children].indexOf(item);

        // Move the dragged item to its new position
        if (draggedIndex < targetIndex) {
          item.after(draggedItem);
        } else {
          item.before(draggedItem);
        }
        // Optionally send the updated order to the backend
      }
    });
  });
}


function deleteBookmark(id) {
  fetch(`${API_URL}/bookmarks/${id}`, {
    method: "DELETE",
    headers: { "Authorization": "Bearer " + localStorage.getItem("token") }
  })
    .then(res => res.json())
    .then(() => loadBookmarks());
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "login.html";
}
