// firebase-load.js

// Configuración de Firebase (usa tus valores reales del proyecto Firebase aquí)
const firebaseConfig = {
  apiKey: "AIzaSyDuI1i-VauC9rp-YOWe2GGpHXhOiX9eR3o",
  authDomain: "webworkvisionblog.firebaseapp.com",
  projectId: "webworkvisionblog",
  storageBucket: "webworkvisionblog.appspot.com",
  messagingSenderId: "1031451530206",
  appId: "1:1031451530206:web:8fa548813cc1d8ba49034f",
  measurementId: "G-0BDZXG0P7C"
};

// Inicializar Firebase
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// Función para cargar artículos ordenados por fecha descendente
function loadArticles() {
  const container = document.getElementById("articles-container");
  container.innerHTML = "<p>Cargando artículos...</p>";

  db.collection("article")
    .orderBy("date", "desc")
    .get()
    .then((querySnapshot) => {
      container.innerHTML = ""; // limpiar contenedor
      querySnapshot.forEach((doc) => {
        const data = doc.data();
        const title = data.title || "Sin título";
        const description = data.description || "";
        const date = data.date
          ? new Date(data.date).toLocaleDateString()
          : "";

        const articleHTML = `
          <div class="article">
            <h2>${title}</h2>
            <small>${date}</small>
            <p>${description}</p>
          </div>
        `;
        container.innerHTML += articleHTML;
      });
    })
    .catch((error) => {
      container.innerHTML = "<p>Error cargando artículos.</p>";
      console.error("Error getting documents: ", error);
    });
}

// Cargar artículos cuando la página termine de cargar
window.onload = loadArticles;
