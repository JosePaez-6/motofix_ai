// ======================================================
// CONFIGURACIÓN AUTOMÁTICA DEL BACKEND
// Detecta si estás en local o en producción (Railway)
// ======================================================
const API_URL = window.location.hostname.includes("localhost") || window.location.hostname.includes("127.0.0.1")
  ? "http://127.0.0.1:8000"
  : "https://motofix-production.up.railway.app";

// ======================================================
// Cargar dinámicamente los modelos disponibles
// ======================================================
window.addEventListener("DOMContentLoaded", async () => {
  const select = document.getElementById("modelo");
  try {
    const res = await fetch(`${API_URL}/modelos`);
    const data = await res.json();
    if (data.modelos && data.modelos.length > 0) {
      select.innerHTML = data.modelos
        .map((m) => `<option value="${m}">${m}</option>`)
        .join("");
    } else {
      select.innerHTML = `<option value="">No hay modelos disponibles</option>`;
    }
  } catch (error) {
    console.error("Error al cargar modelos:", error);
    select.innerHTML = `<option value="">Error al conectar con el servidor</option>`;
  }
});

// ======================================================
// Enviar pregunta al backend
// ======================================================
document.getElementById("chat-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const modelo = document.getElementById("modelo").value;
  const pregunta = document.getElementById("pregunta").value.trim();
  const respuestaDiv = document.getElementById("respuesta");

  if (!pregunta) {
    alert("Por favor, escribe tu pregunta");
    return;
  }

  // Mostrar indicador de carga
  document.getElementById("response").style.display = "block";
  respuestaDiv.innerHTML = `
    <div class="d-flex align-items-center">
      <div class="spinner-border text-primary me-3" role="status"></div>
      <div>Analizando tu pregunta con nuestros expertos...</div>
    </div>
  `;

  // Enviar la solicitud a la API
  try {
    const response = await fetch(`${API_URL}/preguntar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ modelo, pregunta }),
    });

    if (!response.ok) {
      throw new Error("Error al procesar la solicitud.");
    }

    const data = await response.json();
    respuestaDiv.innerHTML = `
      <div class="mb-2"><strong>Modelo consultado:</strong> ${data.modelo}</div>
      <div><strong>Tu pregunta:</strong> ${data.pregunta}</div>
      <div class="mt-3 alert alert-info bg-primary bg-opacity-10 border-primary">
        <i class="fas fa-info-circle me-2"></i> 
        ${data.respuesta || "No se encontró una respuesta específica. Intenta reformular tu pregunta."}
      </div>
      <div class="mt-3 text-center">
        <button class="btn btn-sm btn-outline-primary" 
                onclick="document.getElementById('pregunta').value=''; document.getElementById('pregunta').focus();">
          <i class="fas fa-plus me-1"></i> Hacer otra pregunta
        </button>
      </div>
    `;
  } catch (error) {
    console.error("Error:", error);
    respuestaDiv.innerHTML = `
      <div class="alert alert-danger">
        <i class="fas fa-exclamation-triangle me-2"></i> 
        No se pudo conectar con el servidor. Verifica tu conexión o intenta más tarde.
      </div>
    `;
  }
});

// ====================================================== 
// Preguntas frecuentes (rellena el input automáticamente)
// ======================================================
document.querySelectorAll(".question-tag").forEach((tag) => {
  tag.addEventListener("click", function () {
    document.getElementById("pregunta").value = this.getAttribute("data-question");
    document.getElementById("pregunta").focus();
  });
});
