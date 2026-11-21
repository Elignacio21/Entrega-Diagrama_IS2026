const formulario = document.getElementById("form-registro");
const estado = document.getElementById("estado");
const respuesta = document.getElementById("respuesta");
const listaUsuarios = document.getElementById("lista-usuarios");

function limpiarErrores() {
  for (const parrafo of document.querySelectorAll(".error")) {
    parrafo.textContent = "";
  }
  for (const campo of document.querySelectorAll("input")) {
    campo.removeAttribute("aria-invalid");
  }
}

function mostrarErrores(errores) {
  for (const [campo, mensaje] of Object.entries(errores)) {
    const parrafo = document.getElementById(`error-${campo}`);
    const entrada = document.getElementById(campo);
    if (parrafo) parrafo.textContent = mensaje;
    if (entrada) entrada.setAttribute("aria-invalid", "true");
  }
}

async function refrescarUsuarios() {
  const res = await fetch("/api/usuarios");
  if (res.ok) {
    const data = await res.json();
    listaUsuarios.textContent = JSON.stringify(data.usuarios, null, 2);
  }
}

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  limpiarErrores();

  const datos = {
    correo: document.getElementById("correo").value,
    password: document.getElementById("password").value,
  };

  try {
    const res = await fetch("/api/usuarios", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });
    const cuerpo = await res.json();

    estado.textContent = `HTTP ${res.status}`;
    estado.className = res.ok ? "estado ok" : "estado fallo";
    respuesta.textContent = JSON.stringify(cuerpo, null, 2);

    if (res.ok) {
      formulario.reset();
      await refrescarUsuarios();
    } else if (cuerpo.errores) {
      mostrarErrores(cuerpo.errores);
    }
  } catch (error) {
    estado.textContent = "No se pudo conectar con el servidor";
    estado.className = "estado fallo";
    respuesta.textContent = String(error);
  }
});

refrescarUsuarios();