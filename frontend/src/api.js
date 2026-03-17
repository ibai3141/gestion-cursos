const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      ...(options.headers ?? {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await response.json() : null;

  if (!response.ok) {
    throw new Error(data?.detail ?? "Ha ocurrido un error en la peticion");
  }

  return data;
}

export async function login(email, contrasenia) {
  const query = new URLSearchParams({ email, contrasenia }).toString();
  return request(`/auth/login?${query}`, { method: "POST" });
}

export async function registroProfesor(payload) {
  return request("/auth/registro/profesor", { method: "POST", body: payload });
}

export async function registroEstudiante(payload) {
  return request("/auth/registro/estudiante", { method: "POST", body: payload });
}

export async function getMisCursos(token) {
  return request("/cursos/", { token });
}

export async function getTodosLosCursos(token) {
  return request("/cursos/todosCursos", { token });
}

export async function crearCurso(token, payload) {
  return request("/cursos/", { method: "POST", token, body: payload });
}

export async function getProfesores(token) {
  return request("/profesores/", { token });
}

export async function inscribirseEnCurso(token, curso_id) {
  return request("/inscripciones/", {
    method: "POST",
    token,
    body: { curso_id },
  });
}

export function getMicrosoftLoginUrl() {
  return `${API_BASE_URL}/auth/microsoft/login`;
}

export function getMicrosoftRegisterUrl(rol) {
  return `${API_BASE_URL}/auth/microsoft/registro/${rol}`;
}
