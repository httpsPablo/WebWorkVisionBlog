
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import {
  getFirestore,
  collection,
  getDocs,
  query,
  orderBy
} from "https://www.gstatic.com/firebasejs/9.6.1/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyDuI1i-VauC9rp-YOWe2GGpHXhOiX9eR3o",
  authDomain: "webworkvisionblog.firebaseapp.com",
  projectId: "webworkvisionblog",
  storageBucket: "webworkvisionblog.appspot.com",
  messagingSenderId: "1031451530206",
  appId: "1:1031451530206:web:8fa548813cc1d8ba49034f",
  measurementId: "G-0BDZXG0P7C"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

const container = document.getElementById("article-container");
const asideList = document.querySelector(".popular-posts ul");

function slugify(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

async function loadArticles() {
  container.innerHTML = "<p>loading articles...</p>";
  try {
    const q = query(collection(db, "technology_articles"), orderBy("date", "desc"));
    const querySnapshot = await getDocs(q);

    container.innerHTML = "";
    asideList.innerHTML = "";

    querySnapshot.forEach((doc) => {
      const data = doc.data();
      const title = data.title || "Sin título";
      const description = data.description || "Sin descripción";
      const id = slugify(title);

      let date = "";
      if (data.date) {
        if (typeof data.date.toDate === "function") {
          date = data.date.toDate().toLocaleDateString("es-AR");
        } else {
          date = new Date(data.date).toLocaleDateString("es-AR");
        }
      }

      // Artículo principal
      const articleHTML = `
        <div class="article" id="${id}">
          <h2>${title}</h2>
          <small>${date}</small>
          <p>${description}</p>
        </div>
      `;
      container.innerHTML += articleHTML;

      // Enlace popular en el aside
      const asideItem = document.createElement("li");
      asideItem.innerHTML = `<a href="#${id}">${title}</a>`;
      asideList.appendChild(asideItem);
    });
  } catch (error) {
    console.error("Error, no cargaron los articulos", error);
    container.innerHTML = "<p>Error not loading articles.</p>";
  }
}

window.addEventListener("load", loadArticles);

// Scroll suave y centrado al hacer clic en los links del aside
asideList.addEventListener("click", (e) => {
  if (e.target.tagName === "A") {
    e.preventDefault();
    const targetId = e.target.getAttribute("href").substring(1);
    const targetElement = document.getElementById(targetId);
    if (targetElement) {
      targetElement.scrollIntoView({
        behavior: "smooth",
        block: "center"
      });
      history.pushState(null, "", `#${targetId}`);
    }
  }
});


    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href.startsWith('#')) {
          e.preventDefault();
          const target = document.querySelector(href);
          if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            history.pushState(null, '', href);
          }
        }
      });
    });
  document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('nav-toggle');
    const menu = document.getElementById('nav-menu');

    if (toggle && menu) {
      toggle.addEventListener('click', () => {
        menu.classList.toggle('active');
      });
    }
  });

